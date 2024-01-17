import zmq
import json

class CommunicationClient:
    def __init__(self, identity = "rally"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://localhost:7777")
        self.identity = identity
        
    def receive(self):
        try:
            serialized = self.socket.recv_string(flags=zmq.NOBLOCK)
            print ("recv command: ", serialized)
            return serialized
        except zmq.Again as e:
            return None
        #obj = json.loads(serialized)
        #return obj
        # print(obj)
        
    def send(self, message = None):
        serialized = json.dumps(message)
        # print(serialized)
        self.socket.send_string(self.identity + ' ' + serialized)
        
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
