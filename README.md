# kivy3dgui

Kivy 3D. A set of widgets to display and interact with Kivy widgets in a 3D mesh.

If you want to help with the development you can mail me: kpiorno@uci.cu

![Screenshot](https://github.com/kpiorno/kivy3dgui/blob/master/screenshots/screenshot1.jpg "Screenshot")

# Example
```python
#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
Layout3D:
    id: par
    size_hint: (1.0, 1.0)
    canvas_size: (1366, 768)
    post_processing: False
    Node:
        id: Node1
        name: 'Node 0'
        rotate: (90, 0.3, 1, 0)
        scale: (0.4, 0.4, 0.4)
        translate: (20, -10.0, -110)
        effect: True
        meshes: ("./data/obj/sphere.obj", )
        FloatLayout:
            canvas:
                Color:
                    rgb: 1, 1, 1,0.1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: "./data/imgs/background.jpg"
            size_hint: (1.0, 1.0)
            Button:
                pos_hint: {"x":0, "y":0 }
                size_hint: (None, None)
                text: "Hello"

            Button:
                size_hint: (0.3, 0.3)
                text: "Rotate"

            Button:
                size_hint: (0.2, 0.2)
                pos_hint: {"x":0.0, "y":0.6}
                text: "GO!!!"
                font_size: 50

            TextInput:
                id: TextSphere
                text: "Please write or write please?"
                size_hint: (0.8, 0.4)
                font_size: 40
```
