import numpy as np
import os
import socket
import json
import time
from collections import deque
from enum import Enum

# Create an enum
class Events(Enum):
    RECEIVED_MSG = 1
    SENT_MSG = 2
    INTERNAL_EVENT = 3
    BROADCAST_MSG = 4

"""
    clock_speed: the speed of the client's clock, in tics/sec
    port: The port on which the client will listen for incoming messages.
"""
class ClientProcess:
    def __init__(self, clock_speed, port, name, experiment_dir):
        self.port = port
        self.host = '127.0.0.1'

        # Create a socket for receiving messages.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[INFO] Process listening on {self.host}:{self.port}")

        # Global clock
        self.clock_speed = clock_speed
        self.time = time.time()

        # Local clock
        self.ticks = 0
        self.is_available = True
        self.last_available=self.time

        self.logging = False

        # Queue of pending messages
        self.network_queue = deque()

        # Create the logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        if not os.path.exists(f"logs/{experiment_dir}"):
            os.makedirs(f"logs/{experiment_dir}")
        if not os.path.exists(f"logs/{experiment_dir}/{name}_log"):
            os.makedirs(f"logs/{experiment_dir}/{name}_log")

        # Log metadata
        self.md_path = f"logs/{experiment_dir}/{name}_log/md.txt"
        with open(self.md_path, 'w') as md:
            md.write(f"Name: {name}\n")
            md.write(f"Port: {port}\n")
            md.write(f"Clock Speed: {clock_speed}\n")
            md.write(f"Experiment Directory: {experiment_dir}\n")

        # Event log
        self.log_path = f"logs/{experiment_dir}/{name}_log/events.csv"
        self.log = open(self.log_path, 'w')
        self.log.write(f"Event,TimeGlob,TimeLocal,QueueLen,FromPort,ToPort\n")

    # Determines whether the client is available to process an event
    def update_availability(self):
        if not self.is_available and self.time - self.last_available > 1/ self.clock_speed:
            self.is_available = True
            self.ticks += 1

    # After performing an event, the client is set to unavailable
    def set_unavailable(self):
        self.is_available = False
        self.last_available = self.time

    # Log an internal event
    def internal_event(self):
        string = f"{Events.INTERNAL_EVENT},{self.time},{self.ticks},{len(self.network_queue)},NULL,NULL\n"
        self.log.write(string)

    # Message is a dictionary
    def send_message(self, message, ports):
        """Sends the given message to the specified port."""
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.host, port))
                    s.sendall(json.dumps(message).encode('utf-8'))
                    if self.logging:
                        print(f"[INFO] Sent message to port {port}: {message}")
                except Exception as e:
                    print(f"[ERROR] Could not send message to port {port}: {e}")

        # Log event,send time, ticks, queue length, from port, to port
        if len(ports) == 1:
            port = ports[0]
            string = f"{Events.SENT_MSG},{self.time},{self.ticks},{len(self.network_queue)},{self.port},{port}\n"
        else:
            string = f"{Events.BROADCAST_MSG},{self.time},{self.ticks},{len(self.network_queue)},{self.port},{':'.join([str(x) for x in ports])}\n"
        self.log.write(string)

    def await_message(self):
        """
        Waits for an incoming message on the specified port.
        Note: This implementation assumes that the port passed in is the same
        as the port this instance is bound to.
        """
        if self.logging:
            print(f"[INFO] Waiting for a message on port {self.port} ...")
        try:
            conn, addr = self.server_socket.accept()
            with conn:
                data = conn.recv(1024)
                # Message is a dictionary
                message = json.loads(data.decode('utf-8'))
                if self.logging:
                    print(f"[INFO] Received message: {message}")

                return message
        except Exception as e:
            return

    # Fast queue adds messages outside of the clock ticks
    def append_message(self, message):
        self.network_queue.append(message)

    # Clock reads message from the queue
    def read_message(self):
        message = self.network_queue.popleft()

        # Update clock based on the message's tick
        msg_tick = message["tick"]
        if msg_tick > self.ticks:
            self.ticks = msg_tick

        from_port = message["port"]

        # Log the event
        string = f"{Events.RECEIVED_MSG},{self.time},{self.ticks},{len(self.network_queue)},{from_port},{self.port}\n"

        self.log.write(string)

        return message

    def close(self):
        self.server_socket.close()
        self.log.close()

