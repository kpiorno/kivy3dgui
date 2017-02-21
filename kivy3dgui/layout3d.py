"""
The MIT License (MIT)
Copyright (c) 2015 Karel Piorno Charchabal
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy3dgui import canvas3d
from kivy3dgui.canvas3d import Canvas3D
from kivy3dgui import effectwidget
from kivy3dgui.effectwidget import BlurEffectWidget
from kivy3dgui.node import Node
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.graphics import *
from kivy.core.window import Window

# from kivy.graphics.texture import Texture


class Layout3D(FloatLayout):
    canvas3d = ObjectProperty(None, allownone=True)
    '''canvas3d
    '''

    post_processing = BooleanProperty(False)
    '''post_processing
    '''

    shadow = BooleanProperty(True)
    '''shadow
    '''

    _nodes = ListProperty([])
    '''_nodes
    '''

    _init_request = [False, False]
    '''_init_request
    '''

    look_at = ListProperty([0, 0, 10, 0, 0, 0, 0, 1, 0])
    '''_look_at
    '''

    _id_stack = ListProperty([])

    shadow_offset = NumericProperty(0)

    shadow_origin = ListProperty([0, 0, 0])

    shadow_target = ListProperty([0, -90, -100])

    shadow_threshold = NumericProperty(1.0)

    canvas_size = ListProperty(Window.size)

    picking_scale = NumericProperty(1.0)

    def __init__(self, **kwargs):

        self.canvas_size = kwargs.get("canvas_size", Window.size)
        super(Layout3D, self).__init__(**kwargs)
        self._trigger_layout = Clock.create_trigger(self.do_layout, -1)
        effectwidget.C_SIZE = self.canvas_size

        with self.canvas.before:
            Color(1.0, 1.0, 1.0, 1.0)
            ClearColor(1.0, 1.0, 1.0, 1.0)

        self.create_canvas()
        self.bind(look_at=self.canvas3d.setter('look_at'))
        self.bind(shadow_offset=self.canvas3d.setter('_shadow_offset'))
        self.bind(shadow_threshold=self.canvas3d.setter('shadow_threshold'))
        self.bind(shadow_origin=self.canvas3d.setter('_shadow_pos'))
        self.bind(shadow_target=self.canvas3d.setter('_shadow_target'))
        self.bind(picking_scale=self.canvas3d.setter('picking_scale'))
        self.bind(canvas_size=self.canvas3d.setter('canvas_size'))

        self.effect_widget = BlurEffectWidget(mask_effect=self.canvas3d.picking_fbo,
                                              motion_effect=self.canvas3d.motion_blur_fbo)

        if self._init_request[0]:
            self.post_processing = not self._init_request[1]
            self.post_processing = self._init_request[1]
        self._init_request[0] = True
        from kivy3dgui.canvas3d import label, label_debug
        label.parent = None
        try:
            self.add_widget(label)
            self.add_widget(label_debug)
        except Exception as w:
            pass
        self.render_texture = Image(size_hint=(1.0, 1.0),
                                    allow_stretch=True,
                                    keep_ratio=False)
        self.add_widget(self.render_texture, 100000)
        self.render_texture.texture = self.canvas3d.canvas.texture
        self.bind(pos=self.render_texture.setter('pos'))
        self.bind(size=self.render_texture.setter('size'))

    def on_canvas_size(self, widget, value):
        effectwidget.C_SIZE = value
        canvas3d.PICKING_BUFFER_SIZE = value

    def walk(self, value, time):
        self.canvas3d.walk(value, time)

    def strafe(self, value, time):
        self.canvas3d.strafe(value, time)

    def up(self, value, time):
        self.canvas3d.up(value, time)

    def create_canvas(self, *args):
        if self.canvas3d is None:
            self.canvas3d = Canvas3D(shadow=True, picking=True, size_hint=(1, 1),
                                     canvas_size=self.canvas_size, id="CANVAS3D")
            self.add_widget(self.canvas3d)
            self.canvas3d.size = self.size
            self.canvas3d.size_hint = self.size_hint

    def _add_node(self, *args):
        self.canvas3d.add_node(args[0])
        pass

    def on_post_processing(self, widget, value):
        if not self._init_request[0]:
            self._init_request[0] = True
            self._init_request[1] = value
            return

        for children in self.children[:]:
            if isinstance(children, Canvas3D) or isinstance(children, BlurEffectWidget):
                self.remove_widget(children)

        for children in self.effect_widget.children[:]:
            self.effect_widget.remove_widget(children)
        if value:
            self.effect_widget.add_widget(self.canvas3d)
            self.effect_widget.effect_mask = self.canvas3d.picking_fbo
            self.add_widget(self.effect_widget, 100000)
        else:
            self.add_widget(self.canvas3d, 100000)

    def add_widget(self, *largs):
        widget = largs[0]

        if isinstance(widget, Node):

            # print(widget.fbo_widget)
            inc = True
            c_id = self.canvas3d.current_id
            if self._id_stack:
                top = self._id_stack[-1]
                c_id = top
                self._id_stack.remove(top)
                inc = False
            float_str = str(c_id)[0:4]
            self.canvas3d.fbo_list[float_str] = widget.fbo_widget
            widget.pick_id = c_id

            if widget._start_objs:
                if widget._objs != []:
                    widget._start_objs = False
                self._add_node(widget)
            else:
                widget.parent = self.canvas3d
                try:
                    self._nodes.append(widget.__self__)
                    pass
                except:
                    self._nodes.append(widget)
                    pass

            self.canvas3d.add_widget(widget.fbo_widget)
            """Check the increment"""
            if inc:
                self.canvas3d.current_id += 0.01
                self.canvas3d.current_id = round(self.canvas3d.current_id, 2)
            return None
        else:
            ret = super(Layout3D, self).add_widget(*largs)
            return ret

    def remove_widget(self, widget):
        if isinstance(widget, Node):
            if widget in self._nodes:
                self._nodes.remove(widget)
            float_str = str(widget.pick_id)[0:4]
            if float_str in self.canvas3d.fbo_list:
                # self.canvas3d.fbo_list.remove(float_str)
                self.canvas3d.fbo_list.pop(float_str)

            id = widget.pick_id
            self._id_stack.append(id)
            self.canvas3d._remove_node(widget)
        else:
            super(Layout3D, self).remove_widget(widget)

    def on_touch_up(self, touch):
        ret = False
        for e in self.children:
            if not isinstance(e, Image):
                if e.collide_point(touch.x, touch.y):
                    ret = e.on_touch_up(touch)
                    break
        return ret
