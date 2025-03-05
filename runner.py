import time
import argparse
import yaml
import threading
from random import randint
from client import ClientProcess

"""
    Handles logic for communicating between clients.
    This is the main entry point for the program.
"""
def main():
    # Set up argument parsing for the configuration file.
    parser = argparse.ArgumentParser(description="Runner for ProcessCommunicator.")
    # -c or --config : .yaml file containing the configuration
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.")
    # -t or --time : time (seconds) to run the simulation
    parser.add_argument("-t", "--time", type=int, help="Time to run the simulation in seconds.")
    args = parser.parse_args()

    if args.config is None:
        print("[ERROR] No configuration file provided.")

    # Load the configuration file.
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
        print(f"[INFO] Configuration loaded: {config}")

    port = config['port']
    other_ports = config['other_ports']
    clock_speed = config['clock_speed']
    name = config['name']
    experiment_dir = config['experiment_dir']
    randn_UB = config['randn_UB']

    time_limit = args.time

    # Create an instance bound to the local port.
    communicator = ClientProcess(clock_speed, port, name, experiment_dir)

    # Separate thread to listen for incoming messages.
    def listen_for_messages():
        while True:
            received = communicator.await_message()
            if received is not None:
                communicator.append_message(received)
                # print(f"[INFO] Message received: {received}")
            else:
                print("Socket closed. Exiting listener thread.")
                break

    listener_thread = threading.Thread(target=listen_for_messages)
    listener_thread.daemon = True
    listener_thread.start()

    # Wait for a bit before starting the main loop
    time.sleep(1)

    start_time = time.time()

    # Main loop
    while True:
        # Get current time
        communicator.time = time.time()
        # If time_limit seconds have passed, break and close the communicator
        if communicator.time - start_time > time_limit:
            communicator.close()
            # Stop the listener thread
            listener_thread.join()
            break

        # Update availability
        communicator.update_availability()

        # If ready for an event
        if communicator.is_available:
            # Check if there is a message in the queue
            if len(communicator.network_queue) > 0:
                message = communicator.read_message()
            else:
                randn = randint(1,randn_UB + 1)

                if randn >= 4:
                    communicator.internal_event()
                    continue

                if randn == 3:
                    curr_ports = other_ports 
                else:
                    curr_ports = [other_ports[randn - 1]]

                for send_port in curr_ports:
                    tick = communicator.ticks
                    message = {"tick": tick, "port": communicator.port}
                    communicator.send_message(message, send_port)

            # After executing, return to unavailable
            communicator.set_unavailable()
            print(f"Process {name} : Tick {communicator.ticks}")

if __name__ == '__main__':
    main()