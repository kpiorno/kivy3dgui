# kivy3dgui

Kivy 3D. A pure Kivy library to display and interact with Kivy widgets in a 3D mesh.

If you want to help with the development you can mail me: kpiorno@gmail.com

It's easy to test, just download the code a run the examples. Enjoy it!!!

You can watch a video example [here](https://www.youtube.com/watch?v=V3lhi2OGz0U).
Another [video](https://www.youtube.com/watch?v=rpZFwcV-H0A) for Tour3D Example.
### Work in progress
The 3D Editor is in the early stage. Baby steps, many issues :) anyway, you can test it at ```editor_3d``` branch.

![](https://github.com/kpiorno/kivy3dgui/blob/master/screenshots/3DEditor.gif)

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

You can change the position of the camera using the 'lookat' property,
which sets the [gluLookAt transformation](https://www.opengl.org/sdk/docs/man2/xhtml/gluLookAt.xml).
It defaults to (0, 0, 10, 0, 0, 0, 0, 1, 0).


#### Step 3
Create nodes and add them to the Layout3D. Nodes are used to apply 3D
effects, transformations and display 3D meshes in Kivy layouts.

Nodes may be a set of 3D meshes (obj format is only supported at now). Be sure
to set the UV mapping correctly. If you add a FloatLayout to the node it will be
used as a texture for the meshes and you will be able to interact with
the widgets that are seen on the surface of the meshes, no matter the shape:
touch events are accurately translated to preserve behavior.

The possibilities are endless. Just use your imagination.

```python
    Node:
        id: Node1
        name: 'Node 0'
        rotate: (90, 0.3, 1, 0)  # Angle and x, y, z axis of the rotation matrix
        scale: (0.4, 0.4, 0.4)  # x, y, z of scaling matrix
        translate: (20, -10.0, -110)  # x, y, z of translation matrix
        effect: True
        meshes: ("./data/obj/sphere.obj", ) #List of meshes (obj only)
```
For more detail on these parameters and matrices, please see the
[glRotate matrix](https://www.opengl.org/sdk/docs/man2/xhtml/glRotate.xml),
[glScale matrix](https://www.opengl.org/sdk/docs/man2/xhtml/glScale.xml)
and [glTranslate](https://www.opengl.org/sdk/docs/man2/xhtml/glTranslate.xml)
documentation.

#### Step 4
Create interaction widgets.
The root widgets for Nodes must be a Layout3D. All its children will use this as
the texture for the set of meshes. As mentioned, you will be able to interact
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
