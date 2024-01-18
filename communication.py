import zmq
import json

from ai import AICar, PathObject
from goto_controller import go_to_waypoint

# Return key + send_flag if the key == -1
def task_forward(held_keys, context):
    if context.execution_frame == 0:
        held_keys['w'] = 1
        complete_code = 0
        response_code = 0
    else:
        complete_code = 1
        response_code = 1
        
    return held_keys, complete_code, response_code
    
def task_reset(held_keys, context):
    complete_code = 1
    response_code = 2
    
    return held_keys, complete_code, response_code

def task_go_to(held_keys, context):
    current_sap = context.par['current_sap']
    held_keys, arrived = go_to_waypoint(context.car, context.saps[current_sap], held_keys, nr_rays=13, check_collision=True)
    
    complete_code = 0
    response_code = 0
    print('sap ', context.par['current_sap'])
    
    if arrived:
        context.par['current_sap'] += 1
        if context.par['current_sap'] == len(context.saps) - 1: 
            complete_code = 1
            response_code = 1
    else:
        complete_code = 0
        response_code = 0
        
    return held_keys, complete_code, response_code
    
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
    def __init__(self, car, identity = "rally"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://localhost:7777")
        self.identity = identity
        
        self.car = car
        self.sap1 = PathObject((-41, -50, -7), 90)
        self.sap2 = PathObject((-20, -50, -30), 180)
        self.sap3 = PathObject((-48, -47, -55), 270)
        self.sap4 = PathObject((-100, -50, -61), 270)
        self.sap5 = PathObject((-128, -50, -80), 150)
        self.sap6 = PathObject((-100, -50, -115), 70)
        self.sap7 = PathObject((-80, -46, -86), -30)
        self.sap8 = PathObject((-75, -50, -34), 0)
        self.saps = [self.sap1, self.sap2, self.sap3, self.sap4, self.sap5, self.sap6, self.sap7, self.sap8]
        
        self.par = {'current_sap' : 0}
        self.current_task_name = None
        self.execution_frame = 0
        self.send_flag = -1
        self.name_to_task = {
            b'"w"' : task_forward,
            #'s' : task_back,
            #'a' : task_left,
            #'d' : task_right,
            b'"go_to"' : task_go_to,
            b'RESET' : task_reset
        }
        
    def receive(self):
        try:
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
    
    def perform_task(self, held_keys):
        res_keys, complete_code, response_code = self.name_to_task[self.current_task_name](held_keys, self)
        self.execution_frame += 1
        
        if complete_code == 1:
            self.current_task_name = None
            self.execution_frame = 0
            self.send_flag = response_code
            
            #if arrived:
            #self.par['current_sap'] = (self.par['current_sap'] + 1) % len(self.saps)
            #self.current_task_name = 'go_to'
            
        return res_keys
                
    def send_response(self):
        if self.send_flag == 1:
            # Sending game state
            state = extract_game_state(self.car)
            serialized = json.dumps(state)
            print('Sending message: ', serialized)
            self.socket.send_string(serialized)
            self.send_flag = -1
        if self.send_flag == 2:
            # Sending RESET_PERFORMED
            self.socket.send_string('RESET_PERFORMED')
            self.send_flag = -1
