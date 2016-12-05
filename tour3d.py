from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
from kivy3dgui.layout3d import Node

class Note(Scatter):
    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)
        self.opacity = 0
        #Show
        anim = Animation(opacity=1.0, duration=0.3)
        anim.start(self)        
        create_image = kwargs.get('create_image', False)
                
        self.request_del = False
        text_editor = TextInput(size = (120, 90))
        close = Button(size = (20, 20), text="x")
        image = Image(source="./data/imgs/background.jpg", allow_stretch=True, keep_ratio=False)

        self.add_widget(image)
        self.add_widget(text_editor)
        self.add_widget(close)
        
        if create_image:         
            image_front = Image(source="./data/imgs/faust_github.jpg", size=(120,70), allow_stretch=True, keep_ratio=False)
            self.add_widget(image_front)

        self.size = (120, 120)
        self.size_hint = (None, None)
        image.size = (120, 120)
        text_editor.pos = (0, 10)
        close.pos = (100, 100)
        self.pos = kwargs.get('pos', (100, 400))

        close.bind(on_release=self.close_request)
        
    def close_request(self, *args):
        if not self.request_del:
            anim = Animation(opacity=0.0, duration=0.3)
            anim.bind(on_complete=self.on_complete)
            anim.start(self)        
        self.request_del = True
        
    def on_complete(self, *args):
        self.parent.remove_widget(self)
        
class Tour3DApp(App):
    def create_note(self, args):
        self.create_image = not self.create_image	
        return Note(pos=(args[0]-4, args[1]-102), create_image = self.create_image)

    def speed_event(self):
        self.show_speed_control = not self.show_speed_control
        if self.show_speed_control:
            Animation(translate=(16, 15, -10), scale=(0.07, 0.07, 0.07), duration=0.4).start(self.layout3d.ids["SpeedInc"])
            Animation(translate=(12, 15, -10), scale=(0.07, 0.07, 0.07), duration=0.4).start(self.layout3d.ids["SpeedDec"])
        else:
            Animation(translate=(14, 15, -10), scale=(0.07, 0.07, 0.07), duration=0.4).start(self.layout3d.ids["SpeedInc"])
            Animation(translate=(14, 15, -10), scale=(0.07, 0.07, 0.07), duration=0.4).start(self.layout3d.ids["SpeedDec"])
            self.rot_speed = 14.0
            
    def add_speed(self, value):
        self.rot_speed += value    
        
    def build(self):
        from kivy.lang import Builder
        self.create_image = False 
        self.rot_speed = 14.0
        self.show_speed_control = False        
        self.rotating = True
        self.delay = 8.0
        self.red_n = []
        self.green_n = []
        self.layout3d = Builder.load_string('''
#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
#: import Animation kivy.animation.Animation

<Note>

Layout3D:
    id: par
    size_hint: (1.0, 1.0)
    canvas_size: (1366, 768)
    post_processing: False
    shadow: False
    canvas.before:
        Color:
            rgb: 1, 1, 1,0.1
        Rectangle:
            size: self.size
            pos: self.pos
            #source: "./data/imgs/checkerb.png"    
    Node:
        rotate: (90.0, 1.0, 0, 0)
        scale: (80.0,80.0,0.1)
        translate: (0, -25, -110)
        effect: True
        picking: False
        meshes: ("./data/obj/box.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            Button:
                background_normal: "./data/imgs/checkerb.png"        
            
    Node:
        #rotate: (-90.0, 1.0, 0, 0)
        scale: (0.1,0.1,0.1)
        translate: (0, -18, -12)
        effect: True
        picking: False
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            Button:
                background_normal: "./data/imgs/green.png"        
    Node:
        #rotate: (30.0, 0.0, 0, 1.0)
        id: FarSphere
        scale: (0.3,0.3,0.3)
        translate: (-10, 10, -170)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            id: NoteLayout
            Button:
                size_hint: (1.0, 1.0)
                background_normal: "./data/imgs/worldtex.png"   
                on_touch_down: 
                    Animation(translate=(2, 8, -17), scale=(0.45, 0.45, 0.45), duration=2.3).start(FarSphere)
                    Animation(look_at = [0, 15, 20, 0, 14, -20, 0, 1, 0], duration=2.3).start(root)
                    NoteLayout.add_widget(app.create_note((args[1].x, args[1].y)))
                    Animation(translate= (20, -10, -48),duration=2.3).start(Drawer2)
                
            Slider:
                size_hint: (1.0, 0.05)
                pos_hint: {"x": 0.0, "y":0.5}
                opacity: 0.3
		
       
               
    Node:
        rotate: (310.0, 0.0, 1, 0)
        id: Sheet1
        scale: (0.15,0.15,0.15)
        translate: (-10, 14, -10)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
    
            Button:
                text: "Rotate"
                size_hint: (0.3, 0.2)
                font_size: 80
                pos_hint: {"x": 0, "y":0.4}
                on_release: 
                    anim = Animation(rotate=(310, 0, 1, 0), duration=0.3)
                    anim.start(Sheet1)
                    app.rotating = True
            Button:
                text: "Stop"
                size_hint: (0.3, 0.2)
                font_size: 80                
                pos_hint: {"x": 0.5, "y":0.4}
                on_release: 
                    anim = Animation(rotate=(130, 0, 1, 0), duration=0.3)
                    anim.start(Sheet1)
                    app.rotating = False
                    
    Node:
        rotate: (290.0, 0.0, 1, 0)
        id: Speed
        scale: (0.11,0.11,0.11)
        translate: (14, 14, -10)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
    
            Button:
                text: "Speed"
                size_hint: (0.3, 0.2)
                font_size: 80                
                pos_hint: {"x": 0.5, "y":0.4}
                on_release: 
                    app.speed_event()
    Node:
        rotate: (290.0, 0.0, 1, 0)
        id: SpeedInc
        scale: (0.07,0.07,0.07)
        translate: (14, 15, -10)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
    
            Button:
                text: ">>"
                size_hint: (0.3, 0.2)
                font_size: 80                
                pos_hint: {"x": 0.5, "y":0.4}
                on_release: 
                    app.add_speed(14.0)
                    
    Node:
        rotate: (290.0, 0.0, 1, 0)
        id: SpeedDec
        scale: (0.07,0.07,0.07)
        translate: (14, 15, -10)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
    
            Button:
                text: "<<"
                size_hint: (0.3, 0.2)
                font_size: 80                
                pos_hint: {"x": 0.5, "y":0.4}
                on_release: 
                    app.add_speed(-14.0)
                    
    Node:
        #rotate: (-90.0, 1.0, 0, 0)
        scale: (8.4,8.4,8.4)
        translate: (0, -10, -40)
        effect: True
        meshes: ("./data/obj/table.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            Button:
                background_normal: "./data/imgs/table.png"        

    Node:
        #rotate: (-90.0, 1.0, 0, 0)
        scale: (8.4,8.4,8.4)
        translate: (0, -10, -48)
        effect: True
        picking: False
        meshes: ("./data/obj/drawer.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            Button:
                background_normal: "./data/imgs/drawer.png"        
                
    Node:
        #rotate: (-90.0, 1.0, 0, 0)
        scale: (8.4,8.4,8.4)
        id: Drawer2
        translate: (20, -10, -48)
        effect: True
        picking: False
        meshes: ("./data/obj/drawer.obj", )
        FloatLayout:
            size_hint: (1.0, 1.0)
            id: SelfDrawer
            Button:
                background_normal: "./data/imgs/drawer.png"   
                on_release:
                    Animation(look_at = [0, 15, 16, 0, 12, 0, 0, 1, 0], duration=2.3).start(root)
                    Animation(translate= (20, -10, -40),duration=2.3).start(Drawer2)
                   
                    
    
        ''')
    
        """rotate= (120.0, 0.0, 1.0, 0.4),"""        
        self.layout3d.look_at = [0, 15, 86, 0, 8, 0, 0, 1, 0]
        self.y_rotate = 0.0
        Clock.schedule_interval(self.update_time, 1 / 60.)
        
        return self.layout3d

    def update_time(self, delta):
        if self.rotating: 
            self.y_rotate += delta * self.rot_speed
            self.layout3d.ids["FarSphere"].rotate = [self.y_rotate, 0.0, 1.0, 0.0]
	        
   
if __name__ == '__main__':
    Tour3DApp().run()
