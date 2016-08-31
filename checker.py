from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy3dgui.layout3d import Node

class CheckerApp(App):
    def build(self):
        from kivy.lang import Builder
        self.delay = 8.0
        self.red_n = []
        self.green_n = []
        layout3d = Builder.load_string('''
#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
#: import Animation kivy.animation.Animation
Layout3D:
    id: par
    size_hint: (1.0, 1.0)
    canvas_size: (1366, 768)
    post_processing: False
    canvas.before:
        Color:
            rgb: 1, 1, 1,0.1
        Rectangle:
            size: self.size
            pos: self.pos
            source: "./data/imgs/checkerb.png"    
    Button:
        size_hint: (0.15, 0.1)
        pos_hint: {"x":0.0, "y":0.9}
        text: "perspective"
        on_press:
            app.perspective()
        
    Button:
        size_hint: (0.15, 0.1)
        pos_hint: {"x":0.16, "y":0.9}
        text: "front"
        on_press:
            app.frontal()
        
        ''')
        board = Builder.load_string('''    
Node:
    rotate: (-90.0, 1.0, 0.0, 0)
    scale: (0.4, 0.5, 0.4)
    translate: (-5, -25, -70)
    effect: True
    meshes: ("./data/obj/2dbox.obj", )
    
    FloatLayout:
        id: Board        
        canvas:
            Color:
                rgb: 1, 1, 1,0.1
            Rectangle:
                size: self.size
                pos: self.pos
                source: "./data/imgs/board.png"    
        size_hint: (1.0, 1.0)
        ''')        
        green = '''    
Node:
    rotate: (-90.0, 1.0, 0, 0)
    scale: (0.2,0.2,0.01)
    #translate: (-5, 0, -70)
    translate: (-5, -25, -70)
    effect: False
    picking: False
    meshes: ("./data/obj/spherelow.obj", )
    FloatLayout:
        size_hint: (1.0, 1.0)
        Button:
            background_normal: "./data/imgs/green.png"        
        '''    
        red = '''    
Node:
    rotate: (-90.0, 1.0, 0, 0)
    scale: (0.2,0.2,0.01)
    #translate: (-5, 0, -70)
    translate: (-5, 95, -70)
    picking: False
    effect: True
    meshes: ("./data/obj/spherelow.obj", )
    FloatLayout:
        size_hint: (1.0, 1.0)
        Button:
            background_normal: "./data/imgs/red.png"
                
        '''    
        self.board = board
        layout3d.add_widget(board)
        container = board.fbo_widget
        for x,y in [[x,y] for x in range(8)
                          for y in range(8) if not(x+y)%2]:
                          
            cell = Button(pos_hint={"x":x*0.125, "y":y*0.125}, 
                          size_hint=(0.125, 0.125))
            if y < 3:                           
                figure = Builder.load_string(red)
                self.red_n.append({"node":figure, "front":(-31.5+x*7.8, -28+y*7.35, -108), "persp":(-31.5+x*7.8, -24, -95+y*7.35)})
                layout3d.add_widget(figure)
            if y > 4:                           
                figure = Builder.load_string(green)         
                self.green_n.append({"node":figure, "front":(-31.5+x*7.8, -28+y*7.35, -108), "persp":(-31.5+x*7.8, -24, -169+y*7.35)})                
                layout3d.add_widget(figure)
                
            container.add_widget(cell)
        self.frontal()
        return layout3d
        
    def frontal(self):
        Animation(rotate=(0.0, 1.0, 0.0, 0.0), translate=(-5, 0, -110), duration=1.0).start(self.board)
        for i, n in enumerate(self.red_n):
            (Animation(translate=(-30,20,-40), duration=(i+1)/(self.delay*1.0)) +
            Animation(translate=n["front"], rotate=(0,1.0,0.0,0.0), duration=(i+1)/self.delay+1,t='in_quad')).start(n["node"])
        for i, n in enumerate(self.green_n):
            (Animation(translate=(30,-20,-40), duration=(i+1)/(self.delay*1.0)) +
            Animation(translate=n["front"], rotate=(0,1.0,0.0,0.0), duration=(i+1)/self.delay+1,t='in_quad')).start(n["node"])


    def perspective(self):
        Animation(rotate=(-90.0, 1.0, 0.0, 0.0), translate=(-5, -25, -110),duration=1.0).start(self.board)
        for i, n in enumerate(self.red_n):
            (Animation(translate=(-30,20,-90), duration=(i+1)/(self.delay*1.0)) +
            Animation(translate=n["persp"], rotate=(-90,1.0,0.0,0.0), duration=(i+1)/self.delay+1,t='in_quad')).start(n["node"])
        for i, n in enumerate(self.green_n):
            (Animation(translate=(30,-20,-90), duration=(i+1)/(self.delay*1.0)) +
            Animation(translate=n["persp"], rotate=(-90,1.0,0.0,0.0), duration=(i+1)/self.delay+1,t='in_quad')).start(n["node"])
        

if __name__ == '__main__':
    CheckerApp().run()
