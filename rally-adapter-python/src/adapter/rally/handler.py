import logging
from datetime import datetime

from generic.api.configuration import ConfigurationItem, Configuration
from generic.api.label import Label, Sort
from generic.api.parameter import Type, Parameter
from generic.handler import Handler as AbstractHandler
from rally.rally_connection import RallyConnection


def _response(name, channel='rally', parameters=None):
    return Label(Sort.RESPONSE, name, channel, parameters=parameters)


def _stimulus(name, channel='rally', parameters=None):
    return Label(Sort.STIMULUS, name, channel, parameters=parameters)


class Handler(AbstractHandler):
    """
    This class handles the interaction between AMP and the rally SUT.
    """

    def __init__(self):
        super().__init__()
        self.sut = None

    def send_message_to_amp(self, raw_message: str):
        """
        Send a message back to AMP. The message from the SUT needs to be converted to a Label.

        Args:
            raw_message (str): The message to send to AMP.
        """
        logging.debug('response received: {label}'.format(label=raw_message))

        if raw_message == 'RESET_PERFORMED':
            # After 'RESET_PERFORMED', the SUT is ready for a new test case.
            self.adapter_core.send_ready()
        else:
            label = self._message2label(raw_message)
            self.adapter_core.send_response(label)

    def start(self, configuration: Configuration):
        """
        Start a test.

        Args:
            configuration (Configuration): The configuration to be used for this test run. First item contains the
                url of the Rally SUT.
        """
        self.sut = RallyConnection(self, configuration.items[0].value)
        self.sut.connect()

    def reset(self):
        """
        Prepare the SUT for the next test case.
        """
        logging.info('Resetting the sut for new test cases')
        self.sut.send('RESET')

    def stop(self):
        """
        Stop the SUT from testing.
        """
        logging.info('Stopping the plugin adapter from plugin handler')

        self.sut.stop()
        self.sut = None

        logging.debug('Finished stopping the plugin adapter from plugin handler')

    def stimulate(self, label: Label):
        """
        Processes a stimulus of a given Label message.

        Args:
            label (Label)

        Returns:
            str: The raw message send to the SUT (in a format that is understood by the SUT).
        """
        logging.debug('Stimulate is called, passing the message to the SUT')
        sd_msg = self._label2message(label)
        self.sut.send(sd_msg)
        return bytes(sd_msg, 'UTF-8')

    def supported_labels(self):
        """
        The labels supported by the adapter.

        Returns:
             [Label]: List of all supported labels of this adapter
        """
        return [
            
            _stimulus('right'),
            _stimulus('left'),
            _stimulus('forward'),
            _stimulus('back'),
            _stimulus('forward_right'),
            _stimulus('forward_left'),
            _stimulus('backward_right'),
            _stimulus('backward_left'),
            _response('coordinates'),
            #_stimulus('lock', parameters=[Parameter('passcode', Type.INTEGER)]),
        ]

    def configuration(self):
        """
        The configuration items exposed and needed by this adapter.

        Returns:
            Configuration
        """
        return Configuration([ConfigurationItem(\
            name='endpoint',
            tipe=Type.STRING,
            description='Base websocket URL of the Rally API',
            value='ws://localhost:3001'),
        ])

    def _label2message(self, label: Label):
        """
        Converts a Protobuf label to a SUT message.

        Args:
            label (Label)
        Returns:
            str: The message to be sent to the SUT.
        """

        sut_msg = None
        command_name = label.name.upper()
        #if label.name in ['lock', 'unlock']:
        #    sut_msg = '{msg}:{passcode}'.format(msg=command_name, passcode=label.parameters[0].value)
        #else:
        #    sut_msg = '{msg}'.format(msg=command_name)
        sut_msg = '{msg}'.format(msg=command_name)

        return sut_msg

    def _message2label(self, message: str):
        """
        Converts a SUT message to a Protobuf Label.

        Args:
            message (str)
        Returns:
            Label: The converted message as a Label.
        """

        label_name = message.lower()
        label = Label(
            sort=Sort.RESPONSE,
            name=label_name,
            channel='rally',
            physical_label=bytes(message, 'UTF-8'),
            timestamp=datetime.now())

        return label
