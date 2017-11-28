import math
from textwrap import dedent
from editor.editor_manager import Move, Scale, Rotate, Create, Remove
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, NumericProperty, StringProperty

class NodeHelper(object):
    meshes = []
    pos = [0, 0, 0]
    rot = [0, 0, 0]
    scale = [1, 1, 1]
    current_rot = [0, 0, 0]
    
    def __init__(self):
        self.pos = [0.01, 0.01, 0.01]
        self.meshes = []
        self.rot = [0.01, 0.01, 0.01]
        self.scale = [0.01, 0.01, 0.01]
        self.current_rotrot = [0.01, 0.01, 0.01]
        self.current_mesh = None
        self.last_op = 0
        
    def add_mesh(self, mesh):
        self.meshes += [[
          mesh,
          mesh.translate[:],
          mesh.rotate[:],
          mesh.scale[:]
        ]]
        
    def save_command(self, last_op=0, layout3d=None, callback=None):
        self.last_op = last_op
        if self.last_op == 0 and self.current_mesh:
            self.editor_manager.add_command(Move(self.current_mesh, self.current_mesh.translate))
        elif self.last_op == 1 and self.current_mesh:    
            self.editor_manager.add_command(Scale(self.current_mesh, self.current_mesh.scale))
        elif self.last_op == 2 and self.current_mesh:    
            self.editor_manager.add_command(Rotate(self.current_mesh, [self.current_mesh.pitch, 
                                            self.current_mesh.yaw, self.current_mesh.roll]))
        elif self.last_op == 3 and self.current_mesh:    
            self.editor_manager.add_command(Create(self.current_mesh, layout3d))                                            
        elif self.last_op == 4 and self.current_mesh:    
            self.editor_manager.add_command(Remove(self.current_mesh, layout3d, callback))            

    def save_current_state(self):
        self.current_rot = self.rot[:]
        self.current_pos = self.pos[:]
        self.current_scale = self.scale[:]
        
    def add_command(self, command):
        if self.current_mesh:
           self.editor_manager.add_command(command)
           
    def move_to(self, pos):
        self.pos = pos    
        for e in self.meshes:
            c_t = e[1]
            c_t = [c_t[0] + pos[0], c_t[1] + pos[1], c_t[2] + pos[2]]
            e[0].translate = c_t[:]
        if self.current_mesh:
           self.current_mesh.translate = pos[:]     
        self.last_op = 0
           
    def set_scale(self, scale):
        self.scale = scale
        for i in range(0, 3):
            if self.scale[i] <= 0:
                self.scale[i] = 0.01           
        print(self.scale)                
           
        #for e in self.meshes:
        #    c_t = e[3]
        #    c_t = [c_t[0] + scale[0], c_t[1] + scale[1], c_t[2] + scale[2]]
        #    e[0].scale = c_t[:]
        if self.current_mesh:
           self.current_mesh.scale = self.scale[:]   
        self.last_op = 1   

    def yaw(self, value):
        rot = self.rot
        x = value                     
        y = value
        #z = value * math.cos(rot[0])*math.sin(rot[2])

        #rot[0] += x*2
        #rot[1] += y*2
        rot[1] += x*2
        if rot[1] > 180:
            rot[1] = -180 + (rot[1]-180)
        elif rot[1] < -180:
            rot[1] = 180  + (180 - rot[1])     



        if self.current_mesh:
           self.current_mesh.axis_type = 1     
        self.rotate(rot)
        
    def pitch(self, value):
        rot = self.rot
        x = value                 
        y = value
        z = value * math.cos(rot[1])*math.sin(rot[2])

        #rot[0] += x*2
        #rot[1] += y*2
        rot[0] += y*2
        if rot[0] > 180:
            rot[0] = -180 + (rot[0]-180)
        elif rot[0] < -180:
            rot[0] = 180  + (180 - rot[0])     
        
        if self.current_mesh:
           self.current_mesh.axis_type = 0           
        self.rotate(rot)
        
    def roll(self, value):
        rot = self.rot
        current_rot = self.current_rot
      
        
        #x = rad * math.sin(azimuth) * math.sin(polar)                     
        #y = rad * math.cos(polar)
        #z = rad * math.cos(azimuth) * math.sin(polar)   
        
        z = math.sin( math.radians(current_rot[0]) ) * value + math.sin( math.radians(current_rot[1]) ) * value 
        x = math.sin( math.radians(current_rot[1]) ) * value + math.sin( math.radians(current_rot[2]) ) * value 
        y = math.cos(math.radians(current_rot[2])) * value

        #rot[0] += x
        #rot[1] += y        
        #rot[2] += z
        rot[2] += value
        if rot[2] > 180:
            rot[2] = -180 + (rot[2]-180)
        elif rot[2] < -180:
            rot[2] = 180  + (180 - rot[2])        
         
        if self.current_mesh:
           self.current_mesh.axis_type = 2           
        self.rotate(rot)
        
    def rotate(self, rot):
        self.rot = rot
        if self.current_mesh:
           self.move_to(self.pos)
           self.current_mesh.pitch = rot[0]
           self.current_mesh.yaw = rot[1]
           self.current_mesh.roll = rot[2]
        #for e in self.meshes[6:9]:
        #    e[0].pitch = rot[0]
        #    e[0].yaw = rot[1]
        #    e[0].roll = rot[2]
        for e in self.meshes[3:6]:
            e[0].pitch = rot[0]
            e[0].yaw = rot[1]
            e[0].roll = rot[2]
        self.last_op = 2            
