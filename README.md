# kivy3dgui

Kivy 3D. A pure Kivy library to display and interact with Kivy widgets in a 3D mesh.

If you want to help with the development you can mail me: kpiorno@uci.cu

It's easy to test, just download the code a run the examples. Enjoy it!!!

You can watch a video example [here](https://vimeo.com/127000600).
Another [video](https://vimeo.com/194306331) for Tour3D Example.

### How to use
#### Step 1

Start by importing the Layout3D. This layout manages 3D Nodes but behaves just
like a normal Kivy FloatLayout.

```python
#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
```
#### Step 2

Create a Layout3D, which you can also do from Python.

```python
Layout3D:
    id: par #id for Layout3D, could be referenced just like any Kivy Widget
    size_hint: (1.0, 1.0)
    canvas_size: (1366, 768) # Canvas resolution
    post_processing: False # Post-processing effects (bloom, hdr,...)
```
#### Step 3
Create nodes and add them to the Layout3D.
Nodes may be a set of 3D meshes (obj format is only supported at now). Be sure
to set the UV mapping correctly. If you add a FloatLayout to the node it will be
used as texture for the meshes and as a bonus you will be able to interact with
the widgets that are seen on the surface of the meshes, no matter the shape. The
possibilities are endless. Just use your imagination.

```python
    Node:
        id: Node1
        name: 'Node 0'
        rotate: (90, 0.3, 1, 0)  # Angle and x, y, z axis of rotation
        scale: (0.4, 0.4, 0.4)  # x, y, z of scaling matrix
        translate: (20, -10.0, -110)  # x, y, z of translation matrix
        effect: True
        meshes: ("./data/obj/sphere.obj", ) #List of meshes (obj only)
```        
#### Step 4
Create interaction widgets.
The root widgets for Nodes must be a Layout3D. All its children will use this as
texture for the set of meshes. As mentioned, you will be able to interact
with the widgets.

```python
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

```
![Screenshot](https://github.com/kpiorno/kivy3dgui/blob/master/screenshots/screenshot1.jpg "Screenshot")
