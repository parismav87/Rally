import logging
import threading

import websocket


class RallyConnection:
    """
    This class handles the connection, sending and receiving of messages to the Rally SUT

    Attributes:
        handler (adapter.rally.Handler)
        endpoint (str): URL of the Rally SUT
    """

    def __init__(self, handler, endpoint):
        self.handler = handler
        self.endpoint = endpoint

        self.websocket = None
        self.wst = None

    def connect(self):
        """
            Connect to the Rally SUT
        """
        logging.info('Connecting to Rally')

        # Use lambda functions to correctly pass the self variable.
        self.websocket = websocket.WebSocketApp(
            self.endpoint,
            on_open=lambda _: self.on_open(),
            on_close=lambda _, close_status_code, close_msg: self.on_close(),
            on_message=lambda _, msg: self.on_message(msg),
            on_error=lambda _, msg: self.on_error(msg)
        )

        self.wst = threading.Thread(target=self.websocket.run_forever)
        self.wst.daemon = True
        self.wst.start()

    def send(self, message):
        """
        Send a message to the SUT

        Args:
            message (str): Message to send
        """
        logging.debug('Sending message to SUT: {msg}'.format(msg=message))

        self.websocket.send(message)

    def on_open(self):
        """
        Callback that is called when the socket to the SUT is opened.
        """
        logging.info('Connected to SUT')
        self.send('RESET')

    def on_close(self):
        """
        Callback that is called when the socket is closed
        """
        logging.debug('Closed connection to SUT')

    def on_message(self, msg):
        """
        Callback that is called when the SUT sends a message

        Args:
            msg (str): Message of the Rally SUT
        """
        logging.debug('Received message from sut: {msg}'.format(msg=msg))
        self.handler.send_message_to_amp(msg)

    def on_error(self, msg):
        """
        Callback that is called when something is wrong with the websocket connection

        Args:
            msg (str): Error message
        """
        logging.error("Error with connection to sut: {e}".format(e=msg))

    def stop(self):
        """
        Perform any cleanup if the SUT is closed
        """
        if self.websocket:
            self.websocket.close()
            logging.debug('Stopping thread which handles WebSocket connection with SUT')
            self.websocket.keep_running = False
            self.wst.join()
            logging.debug('Thread stopped')
            self.wst = None
