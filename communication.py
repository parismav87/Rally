import zmq
import json

# Return key + send_flag if the key == -1
def task_forward(execution_frame):
    if execution_frame == 0:
        return 'w', -1
    else:
        return -1, 1
    
def task_back(execution_frame):
    if execution_frame == 0:
        return 's', -1
    else:
        return -1, 1
    
def task_left(execution_frame):
    if execution_frame == 0:
        return 'a', -1
    else:
        return -1, 1
    
def task_right(execution_frame):
    if execution_frame == 0:
        return 'd', -1
    else:
        return -1, 1
    
def task_reset(execution_frame):
    return -1, 2
    
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

# Really a Task Manager now
class CommunicationClient:
    def __init__(self, identity = b"rally"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://localhost:7777")
        self.identity = identity
        #self.socket.setsockopt(zmq.RCVTIMEO, 500)
        
        self.current_task_name = None
        self.execution_frame = 0
        self.send_flag = -1
        self.name_to_task = {
            '"w"' : task_forward,
            '"s"' : task_back,
            '"a"' : task_left,
            '"d"' : task_right,
            'RESET' : task_reset
        }
        
    def receive(self):
        try:
            #string = self.socket.recv()
            string = self.socket.recv(flags = zmq.NOBLOCK)
            print ("recv command: ", string)
            
            if string not in self.name_to_task.keys():
                print("I don't know this command")
                return None
            
            if self.current_task_name is not None:
                print("Something went wrong. I got a new task, but I already have a task {} :(".format(self.current_task_name))
                return None
        
            self.current_task_name = string
            self.execution_frame = 0
        except zmq.Again as e:
            return None
        return string
    
    def task_from_name(self, name):
        return self.name_to_task[name]
    
    def get_key(self):
        task = self.name_to_task[self.current_task_name]
        key, send_flg = task(self.execution_frame)
        self.execution_frame += 1
        if key == -1:
            print("The task is complete")
            self.current_task_name = None
            self.execution_frame = 0
            self.send_flag = send_flg
        return key
                
    def send_message(self, car):
        if self.send_flag == 1:
            # Sending game state
            state = extract_game_state(car)
            serialized = json.dumps(state)
            print('Sending message: ', serialized)
            self.socket.send_string(self.identity + ' ' + serialized)
            self.send_flag = -1
        if self.send_flag == 2:
            # Sending RESET_PERFORMED
            self.socket.send_string(self.identity + ' ' + 'RESET_PERFORMED')
            self.send_flag = -1
        
def apply_input(held_keys, external_command):
    if external_command is None:
        return held_keys
    held_keys[external_command] = 1
    return held_keys
