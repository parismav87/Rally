import zmq
import json

def task_forward(execution_frame):
    if execution_frame == 0:
        return 'w'
    else:
        return -1
    
def task_back(execution_frame):
    if execution_frame == 0:
        return 's'
    else:
        return -1
    
def task_left(execution_frame):
    if execution_frame == 0:
        return 'l'
    else:
        return -1
    
def task_right(execution_frame):
    if execution_frame == 0:
        return 'r'
    else:
        return -1

# Really a Task Manager now
class CommunicationClient:
    def __init__(self, identity = "rally"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://localhost:7777")
        self.identity = identity
        
        self.current_task_name = None
        self.execution_frame = 0
        self.send_state_flag = False
        self.name_to_task = {
            'w' : task_forward
        }
        
    def receive(self):
        try:
            string = self.socket.recv_string(flags=zmq.NOBLOCK)
            print ("recv command: ", string)
            if self.current_task_name is None:
                self.current_task_name = string
                self.execution_frame = 0
            else:
                print("Something went wrong. I got a new task, but I already have a task :(")
        except zmq.Again as e:
            return None
        return string
    
    def task_from_name(self, name):
        return self.name_to_task[name]
    
    def get_key(self):
        task = self.name_to_task[self.current_task_name]
        key = task(self.execution_frame)
        self.execution_frame += 1
        if key == -1:
            print("The task is complete")
            self.current_task_name = None
            self.execution_frame = 0
            self.send_state_flag = True
        return key
        
    def send(self, message = None):
        serialized = json.dumps(message)
        print('Sending message: ', serialized)
        self.socket.send_string(self.identity + ' ' + serialized)
        self.send_state_flag = False
        
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
        'collision' : car.collided
    }
    '''
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
    '''
    return game_state
