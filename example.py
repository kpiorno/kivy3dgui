from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.rst import RstDocument

doc = '''
QuickReference for Rst
======================

This is a markup example: [b]Hello[/b] [i]world[/i]
And if i really want to write my code: &amp;bl; Hello world &amp;br;

And video widget
----------------


Inline Markup
-------------

- *emphasis*
- **strong emphasis**
- `interpreted text`
- ``inline literal``
- reference_
- `phrase reference`_
- anonymous__
- _`inline internal target`

.. _top:

Internal crossreferences, like example_, or bottom_.

Image
-----

Woot!

What about a little image ?

.. image:: kivy/data/logo/kivy-icon-256.png

Grid
----

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | column 2   | column 3  |
+------------+------------+-----------+
| body row 3 | column 2   | column 3  |
+------------+------------+-----------+

Term list
---------

:Authors:
    Tony J. (Tibs) Ibbs,
    David Goodger
    (and sundry other good-natured folks)

.. _example:

:Version: 1.0 of 2001/08/08
:Dedication: To my father.

Definition list
---------------

what
  Definition lists associate a term with a definition.

how
  The term is a one-line phrase, and the definition is one or more paragraphs or
  body elements, indented relative to the term. Blank lines are not allowed
  between term and definition.


Block quotes
------------

Block quotes are SecondWindow:

    Indented paragraphs,

        and they may nest.

Admonitions
-----------

.. warning::

    This is SecondWindow a Test.

.. note::

    And this is SecondWindow a note. Let's test some literal::

        $ echo 'Hello world'
        Hello world

Ordered list
------------

#. My item number one
#. My item number two with some more content
   and it's continuing on the second line?
#. My third item::

    Oh wait, we can put code!

#. My four item::

    No way.

.. _bottom:

Go to top_'''

class AtomPlatformApp(App):
    def build(self):
        self.m_doc = doc
        from kivy.lang import Builder
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
        rotate: (90, 0.3, 1, 0)
        scale: (0.4, 0.4, 0.4)
        translate: (20, -10.0, -30)
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
                #size_hint: (0.2, 0.2)
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

                on_release: Animation(rotate=(-60, 0, 1.0, 0.0), scale=(1, 1, 1), duration=4.3).start(SecondWindow)
                on_release: Animation(rotate=(7, 0, 1.0, 0.0), translate=(-240, -80, 380), duration=10.3).start(FirstWindow)

            TextInput:
                id: TextSphere
                text: "Please write or write please?"
                size_hint: (0.8, 0.4)
                on_focus: if args[1]: Animation(translate= (10, -10.0, -20), rotate=(95, 0, 1.0, -0.3), duration=0.3).start(Node1)
                on_focus: if not args[1]: Animation(translate= (20, -10.0, -40), rotate= (90, 0.3, 1, 0), duration=0.3).start(Node1)
                font_size: 40

    Node:
        id: SecondWindow
        name: 'Node 1'
        scale: (0.01, 0.01, 0.01)
        translate: (95, 0, -80)
        effect: True
        meshes: ("./data/obj/2dbox.obj",)
        FloatLayout:
            id: float
            canvas:
                Color:
                    rgb: 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: "./data/imgs/background.jpg"
            size_hint: (1.0, 1.0)
            RstDocument:
                size_hint: (1.0, 1.0)
                pos_hint: {"x": 0.00, "y": 0.00}
                text: app.m_doc
    Node:
        id: FirstWindow
        name: 'Node 1'
        rotate: (10, 0, 1, 0)
        scale: (1, 0.7, 1)
        translate: (0, 0, -40)
        effect: True
        meshes: ("./data/obj/2dbox.obj",)
        FloatLayout:
            canvas:
                Color:
                    rgb: 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: "./data/imgs/background.jpg"
            size_hint: (1.0, 1.0)
            RstDocument:
                size_hint: (0.3, 0.98)
                pos_hint: {"x": 0.7, "y": 0.01}
                text: app.m_doc

            GridLayout:
                cols: 2
                pos_hint: {"x": 0.4, "y": 0.1}

                size_hint: (0.28, 0.5)
                GridLayout:
                    cols: 2
                    Label:
                        text: "Effect"

                    CheckBox:
                        text: 'Disable'
                        active: True
                        on_active: par.post_processing = self.active
                Spinner:
                    values: ["A","B"]
                Button:
                    size_hint: (0.3, 1.0)
                    text: "Dummy Button!!!"


                TextInput:
                Label:
                    size_hint: (0.3, 1.0)
                    text: "Kivy 3D, Enjoy it!!!"


            Image:
                size_hint: (0.26, 0.8)
                pos_hint: {"x": 0.1, "y": 0.1}
                source: "./data/imgs/faust_github.jpg"

            Button:
                size_hint: (0.1, 0.05)
                pos_hint: {"x": 0.5, "y": 0.8}
                text: "Rotate"
                on_release: (Animation(rotate=(30, 0, 1, 0), duration=4.0, t="out_bounce") + Animation(rotate=(10, 0, 1, 0), duration=4.0, t="out_bounce")).start(FirstWindow)
                on_release: Animation.cancel_all(FirstWindow)
            Slider:
                size_hint: (0.3, 0.1)
                pos_hint: {"x": 0.4, "y": 0.6}
                text: "Spinx"

            Label:
                size_hint: (0.3, 0.3)
                pos_hint: {"x": 0.4, "y": 0.62}
                text: TextSphere.text
    Node:
        id: SecondWindowA
        name: 'Node 1'
        rotate: (7, 0, 1, 0)
        scale: (20, 20, 20)
        translate: (-240, -80, 380)
        effect: True
        FloatLayout:
            canvas:
                Color:
                    rgb: 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: "./data/imgs/imgback.jpg"
            size_hint: (1.0, 1.0)
            RstDocument:
                size_hint: (0.3, 0.98)
                pos_hint: {"x": 0.01, "y": 0.01}
                text: app.m_doc


        ''')
        self.root = root
        return root
        #return self.app
        #return self.app


if __name__ == '__main__':
    AtomPlatformApp().run()
