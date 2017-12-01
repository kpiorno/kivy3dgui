import math
import os
import sys
from textwrap import dedent
from kivy.app import App
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.graphics.transformation import Matrix
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from editor.space_editor import SpaceEditor
from editor.editor_manager import EditorManager
from kivy.core.window import Window, Keyboard

class Editor3dApp(App):
    editor_manager = ObjectProperty(None, allownone=True)
    
    def build(self):
        self.title = "Editor 3D"
        self.data = [""]
        self.mesh_count = 1

        self.current_mesh_path = ""
        self.current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.current_assets_dir = os.path.join(self.current_dir, "assets")

        self.editor_manager = EditorManager(self)
        self.move_camera = True   
        self.cam_distance = 10
        self.super = []
        
        init_dist = []
        rad = 70.0
        azimuth = 19 #0 to 2PI
        polar = 73 #0 to PI
        
        self.m_sx = 0

        x = rad * math.cos(azimuth) * math.sin(polar)                     
        y = rad * math.sin(azimuth) * math.sin(polar)                     
        z = rad * math.cos(polar)

        self.rad = rad
        self.azimuth = azimuth
        self.polar = polar
        
        layout3d = Builder.load_string(dedent('''
                    #:kivy 1.0
                    #: import Layout3D kivy3dgui.layout3d
                    #: import Animation kivy.animation.Animation
                    Layout3D:
                        id: board3d
                        look_at: [0, 0, 10, 0, 0, -20, 0, 1, 0]
                        canvas_size: (1920, 1080)
                        shadow_offset: 2
                        light_position: [-24.5, 150, 100]
                        shadow_origin: [-4,  1., -20.]
                        shadow_target: [-4.01, 0., -23.0]
                        size_hint: 0.8, 1.0
                        

                        
                        shadow_threshold: 0.3 
                        post_processing: True                        
                        Node:
                            id: ____editor_3d_bottom____
                            rotate: (-90, 1, 0, 0)
                            scale: (1.0, 0.8, 0.1)
                            translate: (0, -10, -15)
                            min_light_intensity: 0.5
                            receive_shadows: True                            
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
 
                        Button:
                            id: undo
                            size_hint: (0.1, 0.1)
                            pos_hint: {"x": 0.80, "y": 0}
                            text: "Undo"
                            
                        Button:
                            id: delete
                            pos_hint: {"x": 0.90, "y": 0}
                            size_hint: (0.1, 0.1)
                            
                            text: "Remove"                            

                                        
                                        
                                        
                    '''))
                    
        self.box_str = '''
            Node:
                id: {5}
                rotate: ({3}, 0, 1, 0)
                yaw: 45
                pitch: 0
                scale: (2.8, 2.8, 2.8)
                translate: ({0}, {1}, {2})
                shadows_bias: 0.02 
                min_light_intensity: 0.4
                specular_intensity: 1
                specular_power: 320
                receive_shadows: True
                #normal_map: "./editor/images/normal.png"
                
                #meshes: ("{4}",)
            '''
        str_prop = '''    

            BoxLayout
                cols: 1
                size_hint: 0.2, 1.0
                GridLayout:
                    cols: 1
                    GridLayout:
                        
                        cols: 1
                        BoxLayout:
                            id: box_pos
                            orientation: 'vertical'

                            FloatLayout:
                                id: zone
                            
                            #SelectableView:


                            Button:
                                id: create_selected
                                size_hint: (1.0, 0.2)
                                text: "Create"
 
                        GridLayout:
                            cols: 2
                            size_hint_y: 0.3


                            Label:
                                text: "Primitives:"
                                size_hint: 1.0, 0.2
                            Label:    
                                size_hint: 1.0, 0.2
                            Button:
                                id: create_box
                                text: "Box"
                                size_hint: 0.1, 0.2
                                on_press: app.create_box()
                            Button:
                                text: "Sphere"
                                id: create_sphere
                                size_hint: 0.1, 0.1
                                on_press: app.create_sphere()
                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                text: "Name"
                            TextInput:    
                                id: object_name
                                text: "Object1"
                                on_text: app.name_change(*args)
                                    
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                text: "Position (X, Y, Z)"
                            GridLayout:
                                cols: 3
                                TextInput:
                                    id: x_pos
                                TextInput:
                                    id: y_pos
                                TextInput:
                                    id: z_pos
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'justify'
                                text: "Scale (X, Y, Z)"
                            GridLayout:
                                cols: 3
                                TextInput:
                                    id: x_scale
                                TextInput:
                                    id: y_scale
                                TextInput:
                                    id: z_scale                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'center'
                                text: "Rotation (X, Y, Z)"
                            GridLayout:
                                cols: 3
                                TextInput:
                                    id: x_rot
                                TextInput:
                                    id: y_rot
                                TextInput: 
                                    id: z_rot                                
                            
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Cast Shadows"
                            CheckBox:  
                                id: cast_shadows
                                active: True
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Receive Shadows"
                            CheckBox:  
                                id: receive_shadows
                                active: True

                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Light Intensity"
                            Slider: 
                                id: intensity
                                min: 0.0
                                max: 1.0
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Specular Intensity"
                            Slider: 
                                id: specular_intensity
                                min: 0.0
                                max: 10                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Specular Power"
                            Slider: 
                                id: specular_power
                                min: 0.0
                                max: 300                                
                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Shadow Bias"
                            Slider: 
                                id: shadows_bias
                                min: 0.0
                                max: 0.3                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Alpha"
                            Slider: 
                                id: alpha
                                min: 0.0
                                max: 1.0
                                value: 1.0
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Alpha Threshold"
                            Slider: 
                                id: alpha_threshold
                                min: 0.0
                                max: 1.0
                                value: 1.0                                
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Kv File"
                            Button: 
                                id: load_kv
                                text: "Load"  
                                on_press: app.load_kv_file(*args)    
                        BoxLayout:        
                            size_hint_y: 0.1
                            
                        GridLayout:
                            cols: 2
                            size_hint: 1.0, 0.1
                            Label:
                                halign: 'left'
                                size_hint: 0.8, 1.0
                                text: "Scene"
                            Button: 
                                id: save_scene
                                text: "Save"  
                                on_press: app.save_scene(*args)                                    
                                
                                
                                                        
                        GridLayout:
                            cols: 1
                            size_hint: 1.0, 0.2
                            

                            
                     
                            
                

        ''' 
        assets_path_str= dedent(''' 
                        #: import os os
                        
                        FloatLayout:
                            id: box_pos
                            
                            # BoxLayout:
                                # size: box_pos.size
                                # BoxLayout:
                                    # pos: box_pos.pos
                                    # size_hint_y: None
                                    # height: sp(52)

                                    # Button:
                                        # text: 'Icon View'
                                        # on_press: fc.view_mode = 'icon'
                                    # Button:
                                        # text: 'List View'
                                        # on_press: fc.view_mode = 'list'

                            FileChooser:
                                id: fc
                                rootpath: app.current_assets_dir
                                #pos_hint: {"x": 0.8, "y": 0.8}
                                #size_hint: (1.0, 1.0)
                                FileChooserIconLayout
                                    pos_hint: {"x": 0.8, "y":0.73}
                                    size_hint: (0.2, 0.27)
                                FileChooserListLayout  
                                    pos_hint: {"x": 0.8, "y":0.73}
                                    size_hint: (0.2, 0.27)'''
                                    )
                                    
        save_dialog = dedent(''' 
                        FloatLayout:
                            id: save_dialog
                            pos_hint: {"x": 4.0, "y": 4.0}
                            size_hint: (0.35, 0.35)
                            
                            BoxLayout:
                                pos_hint: {"x": 1.0, "y": 1.0}
                                size_hint: (0.8, 0.6)
                            
                                orientation: 'vertical'
                                Label:
                                    text: "SAVING SCENE"
                                    canvas.before:
                                        Color:
                                            rgb: 0.5, 0.5, 0.5, 1.0
                                        Rectangle:
                                            size: self.size
                                            pos: self.pos                                         
                                GridLayout:    
                                    cols: 2
                                    Label:
                                        text: "Directory Name:"
                                        canvas.before:
                                            Color:
                                                rgb: 0.2, 0.2, 0.2, 1.0
                                            Rectangle:
                                                size: self.size
                                                pos: self.pos                                            
                                    TextInput:
                                        multiline: False
                                        font_size: 42
                                        
                                GridLayout:    
                                    cols: 2
                                    Button:
                                        text: "Accept"
                                    Button:
                                        text: "Cancel"
                                        on_press: save_dialog.pos_hint = {"x": 4.0, "y": 4.0}
                                Label:
                                    text: "El directorio ya existe"
                                    canvas.before:
                                        Color:
                                            rgb: 0.2, 0.2, 0.2, 1.0
                                        Rectangle:
                                            size: self.size
                                            pos: self.pos   
                                
                        ''')                                    
                                    
        
        properties = Builder.load_string(dedent(str_prop))
        assets_path = Builder.load_string(assets_path_str)
        self.save_dialog = Builder.load_string(save_dialog)
        
        layout3d.bind(on_touch_move = self.on_touch_move)
      
        layout3d.ids.undo.bind(on_touch_up = self.undo)
        layout3d.ids.delete.bind(on_touch_up = self.remove)
        
        self.layout3d = layout3d
        self.layout3d.f_type = 0
        self.space_editor = SpaceEditor(layout3d, self, self.editor_manager)
        
        layout3d.bind(on_motion=self.on_motion)        
        
        #keyboard = Window.request_keyboard(self._keyboard_released, self)
        #keyboard.bind(on_key_down=self._keyboard_on_key_down, on_key_up=self._keyboard_released)
        
        float_layaout = FloatLayout()
        grid = GridLayout(cols=2)
        float_layaout.add_widget(grid)
        grid.add_widget(layout3d)
        
        self.properties = properties
        self.assets_path = assets_path
        
        self.editor_manager.properties = self.properties
        grid.add_widget(self.properties)
        float_layaout.add_widget(self.assets_path)
        float_layaout.add_widget(self.save_dialog)

        
        x,y,z = self.get_camera_pos()
        self.layout3d.look_at = [x, y, z-10, 0, 0, -10, 0, 1, 0]
        
        #Selected mesh
        properties.ids.create_selected.bind(on_press = self.create_selected)
        
        return float_layaout
        #return layout3d
        
    def save_scene(self, *args):
        if not self.data[0]:
            self.save_dialog.pos_hint = {"x": 0, "y": 0}
        

    def name_change(self, *args):
        #self.space_editor.node_helper.load_kv(self.current_dir, args[1].replace(" ", "_"))
        self.space_editor.node_helper.set_id(args[1].replace(" ", "_"))
        
    def load_kv_file(self, *args):
        self.space_editor.node_helper.load_kv(self.current_dir)
        #self.space_editor.node_helper.set_id(args[1].replace(" ", "_"))        
        
    def create_selected(self, *args):
        if self.assets_path.ids.fc.selection:
            
            self.current_mesh_path = os.path.join(self.current_assets_dir, os.path.basename(self.assets_path.ids.fc.selection[0]))
            self.create_mesh()
    
    def create_sphere(self, *args):
        self.current_mesh_path = "./meshes/sphere.obj"
        self.create_mesh()
        
    def create_box(self, *args):
        self.current_mesh_path = "./meshes/box.obj"
        self.create_mesh()        
        
    def _keyboard_released(self, window, keycode):
        self.super = []

    def _keyboard_on_key_down(self, window, keycode, text, super):
        print("Values ", self.super)
        if 'lctrl' in self.super and keycode[1] == 'z':
            #self.super = []
            self.undo()
            return False
        elif 'lctrl' not in self.super:
            self.super.append('lctrl')
            return False
        else:
            self.super = []
            return False    
            
    def undo(self, *args):
        self.editor_manager.restore()

        
    def remove(self, *args):
        if self.space_editor.node_helper.current_mesh:
            self.space_editor.node_helper.save_command(4, self.layout3d, self.set_mesh)
            self.layout3d.remove_widget(self.space_editor.node_helper.current_mesh)
            self.space_editor.node_helper.move_to([10000, 10000, 100000])
            
        
    def on_motion(self, etype, motionevent):
        print(etype)
        pass

            
        
    def set_mesh(self, box, g_pos, g_scale, selector=None, c_rot=None):
        self.layout3d.add_widget(box)

        self.space_editor.free()
        self.space_editor = SpaceEditor(self.layout3d, self, self.editor_manager)
        self.space_editor.node_helper.current_mesh = box
        self.space_editor.node_helper.bind_props()
        box.translate = g_pos[:]
        #self.space_editor.node_helper.move_to(g_pos[:])


        
        sel = None
        if not selector:
            #sel = box.ids.a_button
            sel = box.fbo_widget
        else:
            sel = selector
            
        sel.bind(on_touch_down = self.on_select_button)

        #box.fbo_widget.bind(on_touch_up = self.on_select_button)
        sel.s_mesh = box
        
        
        self.space_editor.node_helper.scale = box.scale[:]

        #self.space_editor.node_helper.set_scale(g_scale[:])
        
        if not c_rot:
            self.space_editor.node_helper.rotate(self.space_editor.node_helper.rot[:])
        else:
            self.space_editor.node_helper.rotate(c_rot)
            self.space_editor.node_helper.move_to(g_pos[:])

    
    def create_mesh(self):
        
        g_scale = self.space_editor.node_helper.pos[:]
        name = "object" + str(self.mesh_count)
        box = Builder.load_string(dedent(self.box_str.format(0, 0, 0, 0, self.current_mesh_path, name)))
        box.id = name
        self.mesh_count += 1
        box.meshes = (self.current_mesh_path,)
        self.space_editor.node_helper.unbind_props()
        self.set_mesh(box, self.layout3d.look_at[3:6][:], g_scale)
        self.space_editor.node_helper.set_scale(box.scale[:])
        self.space_editor.node_helper.save_command(3, self.layout3d)        
    
    def bottom_touch(self, widget, touch):
        size = widget.size
        touch_pos = touch.pos
        center = [size[0] / 2, size[1] / 2]
        self.create_mesh()
        #g_pos = self.space_editor.node_helper.pos[:]


        
    def on_select_button(self, *args):        
        self.space_editor.node_helper.unbind_props()
        self.space_editor.node_helper.current_mesh = args[0].s_mesh
        self.space_editor.node_helper.bind_props()
        g_pos = args[0].s_mesh.translate
        rot = [args[0].s_mesh.pitch, args[0].s_mesh.yaw, args[0].s_mesh.roll]
        g_scale = args[0].s_mesh.scale
        self.space_editor.node_helper.move_to(g_pos)
        self.space_editor.node_helper.set_scale(g_scale)
        self.space_editor.node_helper.rotate(rot)
        
    def get_camera_pos(self):
        rad = self.rad
        azimuth = math.radians(self.azimuth)
        polar = math.radians(self.polar)
        x = rad * math.sin(azimuth) * math.sin(polar)                     
        y = rad * math.cos(polar)
        z = rad * math.cos(azimuth) * math.sin(polar)                               
        return [x, y, z]
    
    def on_button_touch_down(self, *args):
        self.c_sx = self.m_sx = args[1].sx
        self.c_sy = self.m_sy = args[1].sy
        self.move_camera = False
        self.space_editor.node_helper.save_current_state()
        c_id = args[0].c_id
        if c_id in [3,4, 5]:
            self.space_editor.node_helper.save_command(1)
        elif c_id in [6, 7, 8]:
            self.space_editor.node_helper.save_command(0)
        elif c_id in [0, 1, 2]:
            self.space_editor.node_helper.save_command(2)
            
        return False

    def on_button_touch_up(self, *args):
        self.move_camera = True
        
    def on_button_touch_move(self, *args):
        c_dis =  args[1].sx - self.m_sx
        c_dis_y =  args[1].sy - self.m_sy
        self.m_sx = args[1].sx
        self.m_sy = args[1].sy

        g_pos = self.space_editor.node_helper.pos[:]
        g_scale = self.space_editor.node_helper.scale[:]

        if args[0].c_id == 3:
            if self.azimuth < 90 and self.azimuth > -90 or (self.azimuth >= 270 and self.azimuth <= 360):
                g_scale[0] += c_dis*self.rad
            else:
                g_scale[0] -= c_dis*self.rad
            self.space_editor.node_helper.set_scale(g_scale)        
        elif args[0].c_id == 5:
            g_scale[1] += c_dis_y*self.rad
            self.space_editor.node_helper.set_scale(g_scale)                
        elif (args[0].c_id == 4):
            if self.azimuth >= 0 and self.azimuth <= 180:
                g_scale[2] -= c_dis*self.rad
            else:
                g_scale[2] += c_dis*self.rad
            self.space_editor.node_helper.set_scale(g_scale)        
        elif args[0].c_id == 6:
            if self.azimuth < 90 and self.azimuth > -90 or (self.azimuth >= 270 and self.azimuth <= 360):
                g_pos[0] += c_dis*self.rad
            else:
                g_pos[0] -= c_dis*self.rad
                         
            self.space_editor.node_helper.move_to(g_pos)     
        elif args[0].c_id == 8:
            g_pos[1] += c_dis_y*self.rad
            self.space_editor.node_helper.move_to(g_pos)             
        elif args[0].c_id == 7:
            if self.azimuth >= 0 and self.azimuth <= 180:
                g_pos[2] -= c_dis*40.0 
            else:
                g_pos[2] += c_dis*40.0 
            self.space_editor.node_helper.move_to(g_pos) 
        elif args[0].c_id == 1:
            if self.azimuth >= 0 and self.azimuth <= 180:
                self.space_editor.node_helper.yaw(c_dis*180.0)        
            else:
                self.space_editor.node_helper.yaw(-c_dis*180.0)
        elif args[0].c_id == 2:
            self.space_editor.node_helper.roll(c_dis_y*180.0)        

        elif args[0].c_id == 0:
            self.space_editor.node_helper.pitch(-c_dis_y*180.0)  
 
  

        return False
      
      
        
    def on_touch_move(self, widget, touch):
        if not self.move_camera or touch.sx > 0.8:
            return True
        polar_angle = (touch.dy / self.layout3d.height) * 360        
        azimuth_angle = (touch.dx / self.layout3d.width) * -360
        
        self.azimuth += azimuth_angle
        self.polar += polar_angle
        if self.polar >= 180:
            self.polar = 180
        if self.polar <= 0:
            self.polar = 0.01
        if self.azimuth >= 360:
           self.azimuth = 0
            
        x,y,z = self.get_camera_pos()
        self.layout3d.look_at = [x, y, z-10, 0, 0, -10, 0, 1, 0]

    
if __name__ == '__main__':
    Editor3dApp().run()