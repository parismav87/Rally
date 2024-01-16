import zmq
import json

class CommunicationClient:
    def __init__(self, receive_port_number, transmit_port_number):
        self.context = zmq.Context()
        self.receive_socket = self.context.socket(zmq.SUB)
        self.receive_socket.connect('tcp://localhost:{}'.format(receive_port_number))
        self.receive_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.transmit_socket = self.context.socket(zmq.PUB)
        self.transmit_socket.bind('tcp://*:{}'.format(transmit_port_number))

        
    def receive(self):
        pass
        try:
            serialized = self.receive_socket.recv_string(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            return None
        #serialized = json.dumps('w')
        # print(serialized)
        obj = json.loads(serialized)
        # print("Received reply")
        # print(obj)
        return obj
        # print(obj)
        
    def send(self, message = None):
        serialized = json.dumps(message)
        # print(serialized)
        self.transmit_socket.send_string(serialized)
        
def apply_input(held_keys, external_command):
    if external_command is None:
        return held_keys
    held_keys[external_command] = 1
    return held_keys
        
def extract_game_state(car):
    game_state = {
        'x' : car.x,
        'y' : car.y,
        'z' : car.z,
        'speed' : car.speed,
        'velocity_y' : car.velocity_y,
        'rotation_speed' : car.rotation_speed,
        'acceleration' : car.acceleration,
        'max_rotation_speed' : car.max_rotation_speed,
        'steering_amount' : car.steering_amount,
        'topspeed' : car.topspeed,
        'braking_strenth' : car.braking_strenth,
        'camera_speed' : car.camera_speed,
        'friction' : car.friction,
        'drift_speed' : car.drift_speed,
        'drift_amount' : car.drift_amount,
        'turning_speed' : car.turning_speed,
        'max_drift_speed' : car.max_drift_speed,
        'min_drift_speed' : car.min_drift_speed,
        'pivot_rotation_distance' : car.pivot_rotation_distance,
    }
    return game_state
