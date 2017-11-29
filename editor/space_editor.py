import math
from kivy.lang import Builder
from textwrap import dedent
from .node_helper import NodeHelper
from kivy.properties import ObjectProperty

class SpaceEditor:
    def __init__(self, layout, parent, editor_manager):
        self.layout = layout
        self.parent = parent
        self.node_helper = NodeHelper()
        self.node_helper.editor_manager = editor_manager
        axis = '''
            Node:
                translate: (0, 0, 0)
                scale: (0.05, 0.05, 0.05)
                min_light_intensity: 0.8
                alpha: 0.5
                always_on_top: True
                receive_shadows: False
                cast_shadows: False
                meshes: ("{0}",)
                Button:
                    id: c_button
                    text: "Hello"
                    background_normal: "{1}"
            '''
        
        meshes = ["./editor/meshes/x-rot-axis.obj", "./editor/meshes/y-rot-axis.obj", "./editor/meshes/z-rot-axis.obj",
                  "./editor/meshes/x-scale-axis.obj", "./editor/meshes/z-scale-axis.obj", "./editor/meshes/y-scale-axis.obj",
                  "./editor/meshes/x-axis.obj", "./editor/meshes/z-axis.obj", "./editor/meshes/y-axis.obj"]
                  
        colors = ["./editor/images/red.png", "./editor/images/green.png", "./editor/images/blue.png",
                  "./editor/images/green.png", "./editor/images/blue.png", "./editor/images/red.png",
                  "./editor/images/red.png", "./editor/images/green.png", "./editor/images/blue.png"]
                  
        for i, e in enumerate(meshes):
            node = Builder.load_string(dedent(axis.format(e, colors[i])))
            node.ids.c_button.bind(on_touch_down=parent.on_button_touch_down)
            node.ids.c_button.bind(on_touch_up=parent.on_button_touch_up)
            node.ids.c_button.bind(on_touch_move=parent.on_button_touch_move)
            node.ids.c_button.c_id = i
            layout.add_widget(node)
            self.node_helper.add_mesh(node)
            
    def free(self):
        for e in self.node_helper.meshes:
            self.layout.remove_widget(e[0])
            
    
