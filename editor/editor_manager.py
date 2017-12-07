import math
import os
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
        self.c_dict = args[0].get_properties()
        self.layout = args[1]
        self.callback = args[2]

    def restore(self, *args):
        node = Node(**self.c_dict)
        selector = node.fbo_widget
        for e in args[0][:-1]:
            if e.obj == self.obj:
                e.obj = node
        self.callback(node, node.translate, node.scale, selector, [node.pitch, node.yaw, node.roll])

class EditorManager:
    commands = []
    editor = None

    def __init__(self, editor):
        self.editor = editor
        self.commands = []

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
                self.commands = self.commands[0:-1]

    def load_scene(self, file_name, parent):
        layout3d = Builder.load_file(file_name)
        if layout3d:
            for e in layout3d.get_nodes():
                if isinstance(e, Node):
                    if e.meta_value != -1:
                        e.fbo_widget.bind(on_touch_down=parent.on_select_button)
                        e.fbo_widget.s_mesh = e
                        e.id = e.name
        return layout3d

    def export_scene(self, folder_name):
        print("A")
        template_launcher = dedent("""
        import os
        import sys
        from kivy.app import App
        from kivy.lang import Builder
        
        class {0}(App):
            def build(self):
                self.current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
                self.assets_dir = os.path.join(self.current_dir, "assets")
                scene = Builder.load_file(os.path.join("{1}"))
                return scene
                
        if __name__ == \"__main__\":
            {0}().run()
        
        """)
        export_dir = os.path.join(self.editor.current_dir, "export")
        print("JArra:", export_dir)
        t_launcher_file = open(os.path.join(export_dir, "launcher.py"), "w")
        t_launcher_file.write(template_launcher.format("SceneLauncher", "scene.kv"))
        t_launcher_file.close()
        template_str = dedent("""
        #: kivy 1.0
        #: import os os
        #: import Layout3D kivy3dgui.layout3d
        #: import Animation kivy.animation.Animation        
        Layout3D:
            id: board3d
            look_at: [0, 0, 10, 0, 0, -20, 0, 1, 0]
            canvas_size: (1366, 768)
            shadow_offset: 2
            light_position: [-24.5, 150, 100]
            shadow_origin: [-4,  1., -20.]
            shadow_target: [-4.01, 0., -23.0]
            size_hint: 0.8, 1.0
            post_processing: True
            
            Node:
                id: ____editor_3d_bottom____
                rotate: (-90, 1, 0, 0)
                scale: (1.0, 0.8, 0.1)
                translate: (0, -10, -15)
                min_light_intensity: 0.5
                receive_shadows: True   
                meta_value: -1                
                meshes: ("./meshes/2dbox.obj",)

                # Button:
                    # id: bottom_floor
                    # text: "Create a Box"
                FloatLayout:    
                    canvas:
                        Color:
                            rgb: 0.5, 0.5, 0.5, 1.0
                        Rectangle:
                            size: self.size
                            pos: self.pos  
                
            {0}
            
            Button:
                id: undo
                size_hint: (0.1, 0.1)
                pos_hint: {{"x": 0.80, "y": 0}}
                text: "Undo"
                
            Button:
                id: delete
                pos_hint: {{"x": 0.90, "y": 0}}
                size_hint: (0.1, 0.1)
                
                text: "Remove"     
            
            BoxLayout:    
                pos_hint: {{"x": 0.85, "y": 0.1}}
                size_hint: (0.14, 0.05) 
                canvas:
                    Color:
                        rgb: 0.5, 0.5, 0.5, 1.0
                    Rectangle:
                        size: self.size
                        pos: self.pos                             
                Label:
                    text: "Lock Camera"
                CheckBox:
                    id: lock_camera
                    active: False
                    #on_active: self.lock_camera(*args)        
        """)
        node_str = dedent("""
                Node:
            {0}
        """)
        node_list = ""
        output = open(os.path.join(export_dir, "scene.kv"), "w")
        if self.editor.layout3d:
            for e in self.editor.layout3d.get_nodes():
                if isinstance(e, Node):
                    if e.meta_value != -1:
                        mesh_target = []
                        mesh_res = "[{0}]"
                        props = e.get_properties()
                        for m in props["meshes"]:
                            mesh_target += ["os.path.join(app.assets_dir, '{0}')".format(os.path.basename(m))]
                        mesh_res = mesh_res.format(",".join(mesh_target))
                        print(mesh_res)
                        res = "        id: {0}\n".format(props["id"])
                        res += "        name: '{0}'\n".format(props["name"])
                        res += "        translate: {0}\n".format(props["translate"])
                        res += "        scale: {0}\n".format(props["scale"])
                        res += "        pitch: {0}\n".format(props["pitch"])
                        res += "        yaw: {0}\n".format(props["yaw"])
                        res += "        roll: {0}\n".format(props["roll"])
                        res += "        effect: {0}\n".format(props["effect"])
                        res += "        light_intensity: {0}\n".format(props["light_intensity"])
                        res += "        min_light_intensity: {0}\n".format(props["min_light_intensity"])
                        res += "        specular_intensity: {0}\n".format(props["specular_intensity"])
                        res += "        specular_power: {0}\n".format(props["specular_power"])
                        res += "        normal_map: {0}\n".format(props["normal_map"]) if props["normal_map"] else ""
                        res += "        alpha: {0}\n".format(props["alpha"])
                        res += "        alpha_threshold: {0}\n".format(props["alpha_threshold"])
                        res += "        shadows_bias: {0}\n".format(props["shadows_bias"])
                        res += "        meshes: {0}".format(mesh_res)
                        node_list += node_str.format(res) + "\n"

            output.write(template_str.format(node_list))
        output.close()
