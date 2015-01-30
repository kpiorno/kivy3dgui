from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder


class ExampleApp(App):
    def build(self):
        root = Builder.load_string('''
#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
#: import Animation kivy.animation.Animation
Layout3D:
    id: par
    size_hint: (1.0, 1.0)
    post_processing: True
    Node:
        id: Node1
        name: 'Node 0'
        rotate: (-20, 0, 1, 0)
        scale: (1.0, 1.0, 1.0)
        translate: (0, -20.0, -30)
        effect: True
        meshes: ("./data/obj/athene.obj", )
        FloatLayout:
            canvas:
                Color:
                    rgb: 1, 1, 1,0.1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: "./data/imgs/terr_rock6.jpg"
            on_touch_up: self.parent.fbo.texture.save("./data/.debug/guide.jpg")
            GridLayout:
                cols: 4
                Label:
                    text: "Click me"

                Label:
                    text: "Click me 2"

                Label:
                    text: "Click me 3"

                Switch:
                    text: "Click me"

                Slider:

                GridLayout:
                    cols: 1
                    Label:
                    TextInput:
                        pos_hint: {"x": 0.1, "y": 0.1}
                        size_hint: (0.9, 0.3)
                        font_size: 20
                        text: "Nombre"
                        on_focus:
                            if args[1]: Animation(translate=(0, -10.0, -12), rotate=(-45, 0., 1., 0.),
                            duration=0.3).start(Node1)
                            if not args[1]: Animation(translate=(0, -20.0, -30), rotate=(-20, 0, 1, 0),
                            duration=0.3).start(Node1)
                    Label:
                GridLayout:
                    cols: 1
                    TextInput:
                        text: "Testing 1"
                    TextInput:
                        text: "Testing 2"
                    TextInput:
                        text: "Testing 3"
                        font_size: 30
                        on_focus:
                            if args[1]: Animation(translate=(0, -3.0, -10), rotate=(35, 0., 1., 0.),
                            duration=0.3).start(Node1)
                            if not args[1]: Animation(translate=(0, -20.0, -30), rotate=(-20, 0, 1, 0),
                            duration=0.3).start(Node1)


    AsyncImage:
        pos_hint: {"x":0.6, "y": 0.3}
        size_hint: (0.4, 0.3)
        allow_strecht: True
        source: "./data/.debug/guide.jpg"

    CheckBox:
        text: 'Disable'
        active: True
        size_hint: 0.3, 0.3
        on_active: par.post_processing = self.active
        ''')
        self.root = root
        return root


if __name__ == '__main__':
    ExampleApp().run()
