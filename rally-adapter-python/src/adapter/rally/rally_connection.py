import logging
import os
import subprocess
import sys
import socket
import threading
from time import sleep
from typing import List

import zmq
#from zmq.eventloop.zmqstream import ZMQStream


# RALLY_PATH = "C:\\Users\Arwin\\PycharmProjects\\Rally" # Used for testing, please change this in a later version!!


class RallyConnection:
    """
    This class handles the the rally game

    Attributes:
        handler (adapter.smartdoor.Handler)
        endpoint (str): URL of the SmartDoor SUT
    """

    def __init__(self, handler, port_number=7777):
        self.handler = handler

        self.process = None
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(f'tcp://*:{port_number}')

    def connect(self):
        """
            Connect to the SmartDoor SUT
        """
        logging.info('Opening a socket for the game')

        # make a thread
        self.wst = threading.Thread(target=self.run_forever)
        self.wst.daemon = True
        self.wst.start()

        # self.stream = ZMQStream(self.receive_socket)
        # self.stream.on_recv(self.on_message)
        # print("Connected to the game")

        logging.info('Starting the Rally Game')
        #self.process = subprocess.Popen('python main.py',
        #                                shell=True, stdout=sys.stdout)
        # print("Started the game")
        # while True:
        #     self.send_socket.send_string('"w"')
        # print("Received a message")
        # message = self.receive_socket.recv()
        # print(message)
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

    def run_forever(self):
        while True:
            #identity, message = self.socket.recv()
            identity, message = self.socket.recv_multipart()
            echo_msg = "w"
            self.socket.send_multipart([identity, echo_msg.encode()])
            #self.socket.send_string("w")
            sleep(2)
            print (message)
            #self.handler.send_message_to_amp(message)

    def send(self, message):
        """
        Send a message to the SUT

        Args:
            message (str): Message to send
        """
        logging.debug('Sending message to SUT: {msg}'.format(msg=message))

        self.socket.send_string(message)
        #self.handler.send_message_to_amp(message)

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
    # def on_message(self, msg: List[str]):
    #     """
    #     Callback that is called when the SUT sends a message
    #
    #     Args:
    #         msg (str): Message of the SmartDoor SUT
    #    """
    #     logging.debug('Received message from sut: {msg}'.format(msg=msg))
    # print("We received a message!!!!")
    # self.handler.send_message_to_amp('\n'.join(msg))  # Send an enter separated list to AMP
    # print(msg)

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
    connection = RallyConnection(None, 7777)
    connection.connect()
    sleep(60)
    # connection.stop()
