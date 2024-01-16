import zmq
import json

class CommunicationClient:
    def __init__(self, ip_address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(ip_address)
        
    def receive(self):
        serialized = self.socket.recv()
        #serialized = json.dumps('w')
        obj = json.loads(serialized)
        print("Received reply")
        print(obj)
        
    def send(self, message = None):
        serialized = json.dumps(message)
        print(serialized)
        self.socket.send_string(message)
        
def apply_input(held_keys, external_command):
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
