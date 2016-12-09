'''
FBO example
===========

This is an example of how to use FBO (Frame Buffer Object) to speedup graphics.
An Fbo is like a texture that you can draw on it.

By default, all the children are added in the canvas of the parent.
When you are displaying thousand of widget, you'll do thousands of graphics
instructions each frame.
The idea is to do this drawing only one time in a Fbo, and then, draw the Fbo
every frame instead of all children's graphics instructions.

We created a FboFloatLayout that create his canvas, and a Fbo.
After the Fbo is created, we are adding Color and Rectangle instruction to
display the texture of the Fbo itself.
The overload of on_pos/on_size are here to update size of Fbo if needed, and
adapt the position/size of the rectangle too.

Then, when a child is added or removed, we are redirecting addition/removal of
graphics instruction to our Fbo. This is why add_widget/remove_widget are
overloaded too.

.. note::

    This solution can be helpful but not ideal. Multisampling are not available
    in Framebuffer. We will work to add the support of it if the hardware is
    capable of, but it could be not the same.

'''


# needed to create Fbo, must be resolved in future kivy version
from kivy.core.window import Window

from kivy.graphics import Color, Rectangle, Canvas, Callback
from kivy.graphics.fbo import Fbo
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.resources import resource_find
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.graphics.texture import Texture


class FboFloatLayout(FloatLayout):

    texture = ObjectProperty(None, allownone=True)

    alpha_blending = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.canvas = Canvas()
        with self.canvas.before:
            Callback(self._set_blend_func)

        self.fbo_texture = Texture.create(size=self.size,
                                                  colorfmt='rgba',)
        self.fbo_texture.mag_filter='nearest'

        with self.canvas:
            #self.cbs = Callback(self.prepare_canvas)
            self.fbo = Fbo(size=self.size, texture=self.fbo_texture)
            #Color(1, 1, 1, 0)
            #self.fbo_rect = Rectangle()


        with self.fbo:
            ClearColor(0.0, 0.0, 0.0, 0.0)
            ClearBuffers()
            self.fbo_rect = Rectangle(size=self.size)


        #self.fbo.shader.source = resource_find('./kivy3dgui/gles2.0/shaders/invert.glsl')
        #with self.fbo.after:
        #    self.cbr = Callback(self.reset_gl_context)
        #    PopMatrix()

        with self.canvas.before:
            Callback(self._set_blend_func)

        # wait that all the instructions are in the canvas to set texture

        self.texture = self.fbo.texture
        super(FboFloatLayout, self).__init__(**kwargs)

    def prepare_canvas(self, *args):
        glEnable(GL_BLEND)
        glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)
        glEnable(GL_DEPTH_TEST)

    def _set_blend_func(self, instruction):
        # clobber the blend mode
        if self.alpha_blending:
            glBlendFunc(GL_ONE,
                        GL_ZERO)
        else:

        #glBlendFuncSeparate(GL_ONE, GL_ONE_MINUS_SRC_ALPHA,GL_ONE,GL_ONE_MINUS_SRC_ALPHA)
            #glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)
            #glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
            glBlendFunc(GL_SRC_ALPHA,
                    GL_ONE_MINUS_SRC_ALPHA)


        # draw the buffer, not the whole freakin canvas
        glDisable(GL_CULL_FACE)
        self.fbo.draw()
        # unclobber the buffer
        glBlendFunc(GL_SRC_ALPHA,
                    GL_ONE_MINUS_SRC_ALPHA)

    def setup_gl_context(self, *args):
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    def add_widget(self, *largs):
        # trick to attach kivy3dgui instructino to fbo instead of canvas
        canvas = self.canvas
        self.canvas = self.fbo
        ret = super(FboFloatLayout, self).add_widget(*largs)
        self.canvas = canvas
        return ret

    def remove_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        super(FboFloatLayout, self).remove_widget(*largs)
        self.canvas = canvas

    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo_texture
        self.fbo_rect.size = value

    def on_pos(self, instance, value):
        self.fbo_rect.pos = value

    def on_texture(self, instance, value):
        self.fbo_rect.texture = value

    def on_touch_down(self, touch):
        return super(FboFloatLayout, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        return super(FboFloatLayout, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        return super(FboFloatLayout, self).on_touch_up(touch)


if __name__ == '__main__':
    from kivy.uix.button import Button
    from kivy.app import App

    class TestFboApp(App):
        def build(self):

            # test with FboFloatLayout or FloatLayout
            # comment/uncomment to test it
            root = FboFloatLayout()
            #root = FloatLayout()

            # this part of creation can be slow. try to optimize the loop a
            # little bit.
            s = 30
            size = (s, s)
            sh = (None, None)
            add = root.add_widget
            print('Creating 5000 widgets...')
            for i in range(5000):
                x = (i % 40) * s
                y = int(i / 40) * s
                add(Button(text=str(i), pos=(x, y), size_hint=sh, size=size))
                if i % 1000 == 1000 - 1:
                    print(5000 - i - 1, 'left...')

            return root

    TestFboApp().run()

