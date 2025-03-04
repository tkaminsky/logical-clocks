import unittest
import os
import shutil
import socket
import json
import time
import threading

# Import the ClientProcess class and Events enum.
# Make sure your ClientProcess class is saved in client_process.py
from client import ClientProcess, Events

class TestClientProcess(unittest.TestCase):
    def setUp(self):
        # Use a temporary experiment directory to isolate log output.
        self.experiment_dir = "test_experiment"
        self.client_name = "test_client"
        self.clock_speed = 10
        # Use a fixed port for these tests.
        self.port = 50000
        self.client = ClientProcess(self.clock_speed, self.port, self.client_name, self.experiment_dir)

    def tearDown(self):
        # Close the client and remove any created log directories.
        try:
            self.client.close()
        except Exception:
            pass
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_initialization(self):
        """Test that initialization creates the required log directories and files."""
        md_path = f"logs/{self.experiment_dir}/{self.client_name}_log/md.txt"
        log_path = f"logs/{self.experiment_dir}/{self.client_name}_log/events.csv"
        self.assertTrue(os.path.exists(md_path), "Metadata file not created")
        self.assertTrue(os.path.exists(log_path), "Events log file not created")
        # Check that metadata file contains the expected strings.
        with open(md_path, 'r') as f:
            content = f.read()
        self.assertIn(f"Name: {self.client_name}", content)
        self.assertIn(f"Port: {self.port}", content)

    def test_update_availability(self):
        """Test that update_availability properly makes the client available and increments ticks."""
        self.client.is_available = False
        # Set last_available in the past so that (current time - last_available) > 1/clock_speed.
        self.client.last_available = time.time() - 0.2
        current_ticks = self.client.ticks
        self.client.time = self.client.last_available + 0.2
        self.client.update_availability()
        self.assertTrue(self.client.is_available, "Client should be available after time has passed")
        self.assertEqual(self.client.ticks, current_ticks + 1, "Ticks should have incremented by 1")

    def test_set_unavailable(self):
        """Test that set_unavailable marks the client as unavailable and sets last_available."""
        self.client.is_available = True
        self.client.time = time.time()
        self.client.set_unavailable()
        self.assertFalse(self.client.is_available, "Client should be unavailable after set_unavailable")
        self.assertAlmostEqual(self.client.last_available, self.client.time, msg="last_available should equal current time")

    def test_internal_event(self):
        """Test that internal_event logs an event containing the INTERNAL_EVENT enum."""
        self.client.internal_event()
        # Flush the log so the write is committed.
        self.client.log.flush()
        with open(self.client.log_path, 'r') as f:
            log_contents = f.read()
        self.assertIn("Events.INTERNAL_EVENT", log_contents, "Internal event not logged correctly")

    def test_send_and_await_message(self):
        """Test that a message sent from one client is received by another using sockets."""
        # Create a second client (the receiver) on a different port.
        port_receiver = 50001
        receiver = ClientProcess(self.clock_speed, port_receiver, "receiver", self.experiment_dir)

        # Define a function to run await_message in a separate thread.
        result = {}
        def server_thread():
            result['msg'] = receiver.await_message()
        
        t = threading.Thread(target=server_thread)
        t.start()
        # Give the receiver a moment to start listening.
        time.sleep(0.1)
        message = {"tick": 1, "port": self.port, "content": "hello"}
        # Use the sender (self.client) to send a message to the receiver.
        self.client.send_message(message, port_receiver)
        t.join(timeout=2)
        self.assertIn('msg', result, "Receiver did not get any message")
        self.assertEqual(result['msg'], message, "The received message does not match the sent message")
        receiver.close()

    def test_queue_operations(self):
        """
        Test that append_message and read_message work as expected.
        Note: read_message pops two messages – the first to log the event and the second as the return value.
        """
        msg1 = {"tick": 5, "port": 12345, "content": "first"}
        msg2 = {"tick": 10, "port": 54321, "content": "second"}
        self.client.append_message(msg1)
        self.client.append_message(msg2)
        # Initially, ticks should be 0.
        self.assertEqual(self.client.ticks, 0, "Initial ticks should be 0")
        # read_message should update ticks to msg2's tick and return msg2.
        returned_msg = self.client.read_message()
        self.assertEqual(returned_msg, msg1, "read_message did not return the expected message")
        self.assertEqual(self.client.ticks, 5, "Client ticks were not updated correctly")

        # There should be one message left in the queue.
        self.assertEqual(len(self.client.network_queue), 1, "Queue should have 1 message left")
        # read_message should return the next message in the queue.
        returned_msg = self.client.read_message()
        self.assertEqual(returned_msg, msg2, "read_message did not return the expected message")
        # The queue should be empty after reading the last message.
        self.assertEqual(len(self.client.network_queue), 0, "Queue should be empty after reading all messages")

    def test_close(self):
        """Test that closing the client properly closes the server socket and log file."""
        self.client.close()
        # Once closed, the server socket's file descriptor should be -1.
        self.assertEqual(self.client.server_socket.fileno(), -1, "Server socket should be closed")
        # Attempting to write to the closed log file should raise a ValueError.
        with self.assertRaises(ValueError):
            self.client.log.write("test")

if __name__ == '__main__':
    unittest.main()
