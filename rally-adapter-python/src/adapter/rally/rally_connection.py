import logging
import os
import subprocess
import sys
import socket
import threading
from time import sleep
from typing import List

import zmq
from zmq.eventloop.zmqstream import ZMQStream

# RALLY_PATH = "C:\\Users\Arwin\\PycharmProjects\\Rally" # Used for testing, please change this in a later version!!


class RallyConnection:
    """
    This class handles the the rally game

    Attributes:
        handler (adapter.smartdoor.Handler)
        endpoint (str): URL of the SmartDoor SUT
    """

    def __init__(self, handler, send_port_number, receive_port_number):

        self.handler = handler
        self.send_port_number = send_port_number
        self.receive_port_number = receive_port_number
        self.send_ip_address = 'tcp://*:{}'.format(send_port_number)
        self.receive_ip_address = 'tcp://localhost:{}'.format(receive_port_number)
        self.context = None
        self.process = None
        self.context = None
        self.socket = None

    def connect(self):
        """
            Connect to the SmartDoor SUT
        """
        logging.info('Opening a socket for the game')

        self.context = zmq.Context()
        self.send_socket = self.context.socket(zmq.PUB)
        self.send_socket.bind(self.send_ip_address)

        self.receive_socket = self.context.socket(zmq.SUB)
        self.receive_socket.connect(self.receive_ip_address)
        self.receive_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.stream = ZMQStream(self.receive_socket)
        self.stream.on_recv(self.on_message)
        # print("Connected to the game")

        logging.info('Starting the Rally Game')
        self.process = subprocess.Popen(f'python main.py {self.send_port_number} {self.receive_port_number}', shell=True, stdout=sys.stdout)
        print("Started the game")
        while True:
            print("Received a message")
            message = self.receive_socket.recv()
            print(message)
            # self.handler.send_message_to_amp(message)

        # self.process = subprocess.Popen('python main.py', shell=True)
        # print("Starting!")

        # Add a function that opens an instance of the rally game
        # if os.name == 'nt':
        #     self.game_pipe = os.popen(os.path.join(RALLY_PATH, "venv\\Scripts\\activate.bat"), mode='w', buffering=1)
        # else:
        #     self.game_pipe = os.popen('source ./venv/bin/activate', mode='w')
        # print("Can't find main")
        # os.popen('python {}'.format(os.path.join(RALLY_PATH, "main.py")), shell=True)


    def send(self, message):
        """
        Send a message to the SUT

        Args:
            message (str): Message to send
        """
        logging.debug('Sending message to SUT: {msg}'.format(msg=message))

        self.send_socket.send(message)

    # def on_open(self):
    #     """
    #     Callback that is called when the socket to the SUT is opened.
    #     """
    #     logging.info('Connected to SUT')
    #     self.send('RESET')
    #
    # def on_close(self):
    #     """
    #     Callback that is called when the socket is closed
    #     """
    #     logging.debug('Closed connection to SUT')
    #
    def on_message(self, msg: List[str]):
        """
        Callback that is called when the SUT sends a message

        Args:
            msg (str): Message of the SmartDoor SUT
        """
        logging.debug('Received message from sut: {msg}'.format(msg=msg))
        # print("We received a message!!!!")
        # self.handler.send_message_to_amp('\n'.join(msg))  # Send an enter separated list to AMP
        print(msg)

    #
    # def on_error(self, msg):
    #     """
    #     Callback that is called when something is wrong with the websocket connection
    #
    #     Args:
    #         msg (str): Error message
    #     """
    #     logging.error("Error with connection to sut: {e}".format(e=msg))

    def stop(self):
        """
        Perform any cleanup if the SUT is closed
        """
        # if self.websocket:
        #     self.websocket.close()
        #     logging.debug('Stopping thread which handles WebSocket connection with SUT')
        #     self.websocket.keep_running = False
        #     self.wst.join()
        #     logging.debug('Thread stopped')
        #     self.wst = None
        self.process.kill()
        self.process.terminate()
        self.stream.close()
        self.socket.close()
        self.context.term()

        self.process = None
        self.socket = None
        self.context = None


if __name__ == "__main__":
    connection = RallyConnection(None, 5555, 5556)
    connection.connect()
    sleep(60)
    # connection.stop()

