import math
from textwrap import dedent
from kivy3dgui.node import Node
from kivy.lang import Builder
from textwrap import dedent
from kivy.properties import ObjectProperty, ListProperty

MAX_QUEUE = 20

class Command:
    obj = None
    def __init__(self, *args):
        pass
    def restore(self):
        pass
        
        
class Move(Command):
    obj = None
    pos = [0, 0, 0]
    
    def __init__(self, *args):
        self.obj = args[0]
        self.pos = args[1]
        
    def restore(self):
        self.obj.translate = self.pos[:]
        
class Rotate(Command):
    obj = None
    rot = [0, 0, 0]
    
    def __init__(self, *args):
        self.obj = args[0]
        self.rot = args[1]
        
    def restore(self):
        self.obj.pitch = self.rot[0]
        self.obj.yaw = self.rot[1]
        self.obj.roll = self.rot[2]
    

class Scale(Command):
    obj = None
    scale = [0.01, 0.01, 0.01]
    
    def __init__(self, *args):
        self.obj = args[0]
        self.scale = args[1]
        
    def restore(self):
        self.obj.scale = self.scale[:]
        
class Create(Command):
    obj = None
    layout = None
    
    def __init__(self, *args):
        self.obj = args[0]
        self.layout = args[1]
        
    def restore(self):
        self.layout.remove_widget(self.obj)    

class Remove(Command):
    obj = None
    c_dict = None
    layout = None
    callback = None
    
    def __init__(self, *args):
        self.obj = args[0]
        self.c_dict = {
            "translate": args[0].translate,
            "rotate": args[0].rotate,
            "pitch": args[0].pitch,
            "yaw": args[0].yaw,
            "roll": args[0].roll,
            "scale": args[0].scale,
            "meshes": args[0].meshes,
            "anims": args[0]._anims,
            "effect": args[0].effect,
            "current_anim_index": args[0].current_anim_index,
            "axis_type": args[0].axis_type,
            "light_intensity": args[0].light_intensity,
            "normal_map": args[0].normal_map,
            "alpha": args[0].alpha,
            "shadows_bias": args[0].shadows_bias
        }        
        self.layout = args[1]
        self.callback = args[2]
        
    def restore(self, *args):
        
        node = Node(**self.c_dict)
        float = dedent("""
                FloatLayout:
                    Button:
                        size_hint: (1., 1.)
                        id: a_button""")
        selector = Builder.load_string(float)
        node.add_widget( selector )   
        for e in args[0][:-1]:
            if e.obj == self.obj:
                e.obj = node
        self.callback(node, node.translate, node.scale, selector.ids.a_button, [node.pitch, node.yaw, node.roll])        
        #self.layout.add_widget(node)    
        

class EditorManager:
    commands = []
    editor = None
    def __init__(self, editor):
        self.editor = editor
        self.commands = []
        pass
        
    def add_command(self, command):
        self.commands.append(command)
        
    def restore(self):
        if self.commands:
            
            self.editor.space_editor.node_helper.current_mesh = None
            self.editor.space_editor.node_helper.move_to([100000, 100000, 100000])
            if isinstance(self.commands[-1], Remove):
                self.commands[-1].restore(self.commands)
            else:    
                self.commands[-1].restore()
            if len(self.commands) == 1:
                self.commands = []
            else:
                self.commands = self.commands[0: -1]
            
            #print(self.commands)