"""
The MIT License (MIT)
Copyright (c) 2015-2017 Karel Piorno Charchabal
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
import copy
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, ListProperty, StringProperty
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.graphics.texture import Texture
from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.uix.label import Label

PICKING_BUFFER_SIZE = Window.size
TRANS_TOUCH_SIZE = Window.size

label = Label(pos_hint={"x": 0.0, "y": 0.0},
              size_hint=(0.2, 0.2))
label_debug = Label(pos_hint={"x": 0.2, "y": 0.2},
                    size_hint=(0.2, 0.2))


class Canvas3D(FloatLayout):
    adding_queue = ListProperty([])
    '''adding_queue_doc
    '''

    translate = ListProperty([0.0, 0.0, 0.0])
    ''' Translate all children widgets around the value
    '''

    rotate = ListProperty([0.0, 0.0, 0.0, 0.0])
    ''' Rotate all children widgets around the value
    '''

    _translate = None

    ''' Shadow FBO translate value
    '''

    _translate_fbo = None
    ''' Shadow FBO translate value
    '''

    _translate_picking = None
    ''' Picking FBO translate value
    '''

    _translate_motion = None
    ''' Motion FBO translate value
    '''

    nodes = ListProperty([])
    ''' Nodes list
    '''

    shadow = True
    ''' Shadow state, at now always the shadows is enable
    '''

    picking = True
    ''' Allow picking. At now always the picking is enable
    '''

    fbo = None
    ''' Shadow FBO
    '''

    fbo_list = {}
    ''' List of elements attached to a Mesh
    '''

    shadow_threshold = NumericProperty(1.0)
    ''' Shadow Distance
    '''

    _update_fbo = 0

    current_id = 0.01
    '''Mesh ID counter
    '''

    last_touch_pos = [-1, -1, -1, -1]
    '''last_touch_pos counter
    '''

    perspective_value = NumericProperty(35.)
    '''Perspective value
    '''
    look_at = ListProperty([0, 0, 10, 0, 0, 0, 0, 1, 0])
    '''look_at value
    '''
    rot_angle = 0.0
    '''rot_angle value
    '''

    _shadow_pos = ListProperty([0, 0, 0])
    '''shadow_pos
    '''

    _shadow_target = ListProperty([0, -50, -100])
    '''shadow_target
    '''

    _shadow_offset = NumericProperty(0)
    '''shadow_offset
    '''

    picking_scale = NumericProperty(0)
    '''shadow_offset
    '''

    ambient_light = ListProperty([0, 0, 0, 0])
    '''ambient_light
    '''

    light_intensity = NumericProperty(0.0)
    '''light_intensity
    '''

    light_position = ListProperty([-24.5, 120, 95])
    '''light_position
    '''

    light_orientation = ListProperty([0.01, 0.01, 0.01])
    '''light_position
    '''
    light_0 = ListProperty([0.01, 0.01, 0.01])
    '''light_0
    '''

    light_1 = ListProperty([0.01, 0.01, 0.01])
    '''light_1
    '''

    MPICKING_BUFFER_SIZE = ListProperty([320, 240])

    canvas_size = ListProperty([1366, 768])

    last_widget_str = StringProperty("")

    def __init__(self, **kwargs):
        self.shadow = kwargs.get("shadow", False)
        self.canvas_size = 1366, 768

        global PICKING_BUFFER_SIZE
        PICKING_BUFFER_SIZE = kwargs.get("canvas_size", Window.size)
        self.shadow = True
        self.picking = True
        self.fbo_list = {}
        self.co = self.canvas
        #self.canvas = RenderContext(compute_normal_mat=False)

        self.canvas = Fbo(size=self.canvas_size,
                       with_depthbuffer=True,
                       compute_normal_mat=True,
                       clear_color=(1.0, 1.0, 1.0, 0.0))

        self.canvas.texture.mag_filter = 'linear'
        self.canvas.texture.min_filter = 'linear'

        # self.canvas.shader.source = resource_find('./kivy3dgui/gles2.0/shaders/simple_no_light.glsl')
        # self.canvas.shader.source = resource_find('./kivy3dgui/gles2.0/toonshader/toon.glsl')
        self.canvas.shader.source = resource_find('./kivy3dgui/gles2.0/toonshader/toon_shadows.glsl')
        self.alpha = 0.0
        self._touches = []
        with self.canvas:
            self._translate = Translate(0, 0, 0)
            self._rotate = Rotate(0.0, 1.0, 0.0, 0.0)
            PushMatrix()
            self.cbs = Callback(self.setup_gl_context)

            if self.shadow:
                self.create_fbo()
            if self.picking:
                self.create_picking_fbo()
            self.create_motion_blur()

        with self.canvas.before:
            self.cbs = Callback(self.setup_gl_context)
            if self.shadow:
                BindTexture(texture=self.fbo.texture, index=1)
                BindTexture(texture=self.motion_blur_fbo.texture, index=5)

            PushMatrix()

            self.setup_scene()
            PopMatrix()
            PushMatrix()
            self.cc = Callback(self.check_context)
            PopMatrix()
            UpdateNormalMatrix()

        with self.canvas.after:
            self.cbr = Callback(self.reset_gl_context)
            PopMatrix()
            # Fixing Shadow and Picking
        self.shadow = True
        self.picking = True
        if self.shadow:
            self.init_fbo()
        if self.picking:
            self.init_picking()
        self.init_motion_blur()
        try:
            self.size_hint = kwargs.pop("size_hint")
            self.canvas_size = kwargs.pop("canvas_size")
            self.id = kwargs.pop("id")
            self.shadow = kwargs.pop("shadow")
            self.picking = kwargs.pop("picking")
            super(Canvas3D, self).__init__(**kwargs)

        except:
            print(kwargs)  
        self.nt = Clock.schedule_interval(self.update_glsl, 1 / 60.)
        self._touches = {}

    def on_picking_scale(self, *args):
        self.MPICKING_BUFFER_SIZE = [PICKING_BUFFER_SIZE[0] * self.picking_scale,
                                     PICKING_BUFFER_SIZE[1] * self.picking_scale]

    def pitch(self, value, time):
        self.rotate = [value, 1.0, 0.0, 0.0]
        Animation.stop_all(self)
        Animation(rotate=[0.0, 1.0, 0.0, 0.0], duration=time).start(self)

    def walk(self, value, time):
        self.translate = [0.0, 0.0, value]
        Animation.stop_all(self)
        Animation(translate=(0.0, 0.0, 0.0), duration=time).start(self)

    def strafe(self, value, time):
        self.translate = [value, 0.0, 0.0]
        Animation.stop_all(self)
        Animation(translate=(0.0, 0.0, 0.0), duration=time).start(self)

    def up(self, value, time):
        self.translate = [0.0, value, 0.0]
        Animation.stop_all(self)
        Animation(translate=(0.0, 0.0, 0.0), duration=time).start(self)

    def on_translate(self, widget, value):
        self._translate.xyz = value[0:3]
        self._translate_picking.xyz = value[0:3]
        self._translate_motion.xyz = value[0:3]
        self._translate_fbo.xyz = value[0:3]

    def on_rotate(self, widget, value):
        self._rotate.set(*value)
        self._rotate_picking.set(*value)
        self._rotate_motion.set(*value)
        self._rotate_fbo.set(*value)

    def init_picking(self):
        with self.picking_fbo:
            self._translate_picking = Translate(0, 0, 0)
            self._rotate_picking = Rotate(0.0, 1.0, 0.0, 0.0)
            PushMatrix()
            self.setup_scene()
            self._picking_instruction = InstructionGroup()

        with self.picking_fbo.after:
            self.cb = Callback(self.reset_gl_context)
            PopMatrix()

        self._picking_instruction.add(Callback(self.setup_gl_context_picking))

    def add_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        ret = super(Canvas3D, self).add_widget(*largs)
        self.canvas = canvas
        return ret

    def _remove_node(self, widget):
        if widget in self.nodes:
            self.nodes.remove(widget)

        for e in widget._instructions:
            if e in self.canvas.before.children:
                self.canvas.before.remove(e)
        widget._instructions = []

        for e in widget._shadow_instructions:
            if e in self.fbo.children:
                self.fbo.remove(e)
        widget._shadow_instructions = []

        for e in widget._picking_instructions:
            if e in self.picking_fbo.children:
                self.picking_fbo.remove(e)
        widget._pick_instruction = []

        for e in widget._blur_instructions:
            if e in self.motion_blur_fbo.children:
                self.motion_blur_fbo.remove(e)
        widget._blur_instructions = []
        widget.clear()

    def init_fbo(self):
        with self.fbo:
            self._translate_fbo = Translate(0, 0, 0)
            self._rotate_fbo = Rotate(0.0, 1.0, 0.0, 0.0)
            PushMatrix()
            # ClearBuffers(clear_depth=True)
            self.cb = Callback(self.setup_gl_context_shadow)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self._instruction = InstructionGroup()

        with self.fbo.after:
            self.cb = Callback(self.reset_gl_context)
            PopMatrix()

        self._instruction.add(Callback(self.setup_gl_context_shadow))

    def create_picking_fbo(self):
        self.picking_fbo = Fbo(size=self.MPICKING_BUFFER_SIZE,
                               with_depthbuffer=True,
                               compute_normal_mat=True,
                               clear_color=(0.0, 0.0, 0.0, 0.0))


        self.picking_fbo.shader.source = resource_find('./kivy3dgui/gles2.0/shaders/selection.glsl')

    def create_fbo(self):
        self.fbo = Fbo(size=PICKING_BUFFER_SIZE,
                       with_depthbuffer=True,
                       compute_normal_mat=True,
                       clear_color=(1.0, 1.0, 1.0, 0.0))

        self.fbo.shader.source = resource_find('./kivy3dgui/gles2.0/shaders/shadowpass.glsl')

    def create_motion_blur(self):
        self.motion_blur_fbo = Fbo(size=PICKING_BUFFER_SIZE,
                                   with_depthbuffer=True,
                                   compute_normal_mat=True,
                                   clear_color=(1.0, 1.0, 1.0, 0.0))

        self.motion_blur_fbo.shader.source = resource_find('./kivy3dgui/gles2.0/shaders/dop.glsl')

    def init_motion_blur(self):
        with self.motion_blur_fbo:
            self._translate_motion = Translate(0, 0, 0)
            self._rotate_motion = Rotate(0.0, 1.0, 0.0, 0.0)
            PushMatrix()
            self.cb = Callback(self.setup_gl_context_motion_blur)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self._instruction_motion_fbo = InstructionGroup()

        with self.motion_blur_fbo.after:
            self.cb = Callback(self.reset_gl_context)
            PopMatrix()

        self._instruction_motion_fbo.add(Callback(self.setup_gl_context_motion_blur))

    def setup_gl_context(self, *args):
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glDisable(GL_POLYGON_OFFSET_FILL)

        glEnable(GL_BLEND)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)

    def change_params(self, mesh):
        self.canvas['pitch'] = float(mesh.pitch)
        self.canvas['yaw'] = float(mesh.yaw)
        self.canvas['roll'] = float(mesh.roll)
        self.canvas['mesh_pos'] = mesh.translate[:]
        self.canvas['min_light_intensity'] = (float(mesh.min_light_intensity))
        self.canvas['specular_power'] = (float(mesh.specular_power))
        self.canvas['specular_intensity'] = (float(mesh.specular_intensity))
        self.canvas['shadows_bias'] = (float(mesh.shadows_bias))
        self.canvas['alpha'] = (float(mesh.alpha))
        self.canvas['alpha_threshold'] = (float(mesh.alpha_threshold))
        self.canvas['enabled_shadow'] = (float(mesh.receive_shadows))
     
     
        #self.canvas['axis_type'] = mesh.axis_type
        
    def change_params_fbo(self, mesh):
        self.fbo['pitch'] = float(mesh.pitch)
        self.fbo['yaw'] = float(mesh.yaw)
        self.fbo['roll'] = float(mesh.roll)
        self.fbo['cast_shadows'] = (float(mesh.cast_shadows))   
       
        self.fbo['mesh_pos'] = mesh.translate[:]

    def change_params_picking_fbo(self, mesh):
        self.picking_fbo['pitch'] = float(mesh.pitch)
        self.picking_fbo['yaw'] = float(mesh.yaw)
        self.picking_fbo['roll'] = float(mesh.roll)
        self.picking_fbo['mesh_pos'] = mesh.translate[:]

    def setup_gl_context_shadow(self, *args):
        self.fbo.clear_buffer()
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(10, 1.0)     
      
        #glCullFace(GL_FRONT)
        self.fbo["pitch"] = float(0)
        self.fbo["yaw"] = float(0)
        self.fbo["roll"] = float(0)


    def setup_gl_context_motion_blur(self, *args):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.motion_blur_fbo.clear_buffer()

    def setup_gl_context_picking(self, *args):
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_POLYGON_OFFSET_FILL)
        self.picking_fbo.clear_buffer()

    def check_context(self, *args):
        self.canvas.clear_buffer()
        pass

    def add_node(self, node):
        node.motion_id = len(self.nodes)
        self.adding_queue.append(node)
        self.nodes.append(node)
        with self.canvas.before:
            PushMatrix()
            Translate(bind=self._translate)
            node.start(self.change_params)
            PopMatrix()

        if self.shadow:
            with self.fbo:
                PushMatrix()
                node.start(self.change_params_fbo)
                PopMatrix()

        if self.picking:
            with self.picking_fbo:
                PushMatrix()
                node.start(self.change_params_picking_fbo)
                PopMatrix()

        with self.motion_blur_fbo:
            PushMatrix()
            node.start(self.change_params)
            PopMatrix()

        node.populate_fbo(node)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
                
    def update_fbo(self, time):
        width = self.width if self.width > 1 else 100
        height = self.height if self.height > 1 else 100

        asp = (width / float(height))
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 1600, 1)
        proj = Matrix()
        proj.perspective(self.perspective_value, asp, 1, 1000)

        lightInvDir = (0.5, 2, 2)
        depthProjectionMatrix = Matrix().view_clip(-100 * self.shadow_threshold, 100 * self.shadow_threshold,
                                                   -100 * self.shadow_threshold, 100 * self.shadow_threshold,
                                                   -100 * self.shadow_threshold, 200 * self.shadow_threshold * 2, 0)
        _shadow_pos = self._shadow_pos
        _shadow_target = self._shadow_target

        depthViewMatrix = Matrix().look_at(_shadow_target[0], _shadow_target[1], _shadow_target[2] + self._shadow_offset,
                                           _shadow_pos[0], _shadow_pos[1], _shadow_pos[2], 0, 1, 0)
        depthModelMatrix = Matrix().identity()
        depthMVP = depthProjectionMatrix.multiply(depthViewMatrix).multiply(depthModelMatrix)

        self.fbo['projection_mat'] = proj
        self.fbo['depthMVP'] = depthMVP
        self.fbo['diffuse_light'] = (0.0, 1.0, 0.0)
        self.fbo['ambient_light'] = self.ambient_light
        for m_pos in range(len(self.nodes)):
            motion_matrix = Matrix().view_clip(-asp, asp, -1, 1, 1, 600, 1)
            angle = self.nodes[m_pos].rotate[0] * 3.14 / 180
            pos = self.nodes[m_pos].get_pos()

            trans = self.nodes[m_pos].translate[:]

            result = [0, 0, 0]
            result[0] = 0.3 if trans[0] < pos[0] else -0.3
            result[1] = 0.3 if trans[1] < pos[1] else -0.3
            result[2] = 0.3 if trans[2] < pos[2] else -0.3

            motion_matrix = motion_matrix.translate(trans[0] + 0.1,
                                                    trans[1] + 0.1,
                                                    trans[2])
            self.motion_blur_fbo['oldTransformation{0}'.format(str(m_pos))] = motion_matrix

        self.motion_blur_fbo['projection_mat'] = proj
        self.motion_blur_fbo['depthMVP'] = depthMVP

        matrix_camera = Matrix().identity()
        matrix_camera = matrix_camera.look_at(*self.look_at)

        if self.picking_fbo:
            self.picking_fbo['projection_mat'] = proj
            self.picking_fbo['camera'] = matrix_camera

        self.alpha += 10 * time
        self.fbo['cond'] = (0.0, 0.7)
        self.fbo['val_sin'] = (self.alpha, 0.0)
        # self.perspective_value += 0.04
        #self.picking_fbo.texture.save("debug.png")
        #self.fbo.texture.save("debug_shadows.png")

    def update_glsl(self, *largs):
        width = self.width if self.width > 1 else 100
        height = self.height if self.height > 1 else 100

        asp = width / float(height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 600, 1)
        proj = Matrix()
        proj.perspective(self.perspective_value, asp, 1, 1000)

        matrix_camera = Matrix().identity()
        matrix_camera = matrix_camera.look_at(*self.look_at)

        self.canvas['projection_mat'] = proj
        self.canvas['camera'] = matrix_camera

        self.canvas['diffuse_light'] = (0.0, 1.0, 0.0)
        self.canvas['ambient_light'] = [v for v in self.ambient_light]
        self.canvas['light_visibility'] = self.light_intensity
        self.canvas['eye_position'] = [self.look_at[0], self.look_at[1], self.look_at[2]]
        self.canvas['light_position'] = [self.light_position[0], self.light_position[1],
                                         self.light_position[2]]

        self.canvas['light_orientation'] = [self.light_orientation[0], self.light_orientation[1],
                                            self.light_orientation[2]]
        self.canvas['light_0'] = [self.light_0[0], self.light_0[1],
                                            self.light_0[2]]
        self.canvas['light_1'] = [self.light_1[0], self.light_1[1],
                                            self.light_1[2]]

        if self.shadow:
            self.canvas['texture1'] = 1
            self.canvas['texture2'] = 2
            self.canvas["enabled_shadow"] = 1.0
        else:

            self.canvas["enabled_shadow"] = 0.0
            self.canvas["texture1"] = 0

        depthProjectionMatrix = Matrix().view_clip(-100 * self.shadow_threshold, 100 * self.shadow_threshold,
                                                   -100 * self.shadow_threshold, 100 * self.shadow_threshold,
                                                   -100 * self.shadow_threshold, 200 * self.shadow_threshold * 2, 0)
        _shadow_pos = self._shadow_pos
        _shadow_target = self._shadow_target
        depthViewMatrix = Matrix().look_at(_shadow_target[0], _shadow_target[1],
                                           _shadow_target[2] + self._shadow_offset,
                                           _shadow_pos[0], _shadow_pos[1], _shadow_pos[2], 0, 1, 0)

        depthModelMatrix = Matrix().identity()
        depthMVP = depthProjectionMatrix.multiply(depthViewMatrix).multiply(depthModelMatrix)
        self.canvas['depthMVP'] = depthMVP
        self.canvas['cond'] = (0.0, 0.7)
        self.canvas['val_sin'] = (self.alpha, 0.0)

        if self.shadow:
            self.update_fbo(largs[0])
            # label.text = str(Clock.get_rfps())

        if self.parent.parent is None:
            # del self.parent

            self.parent.canvas3d = None
            self.fbo_list.clear()
            self.fbo = None
            for a in self.nodes:
                a.remove_a()
            self.nodes = []
            self.parent._nodes = []
            self.parent.clear_widgets()
            self.adding_queue = []
            self.nt.cancel()
            # self.parent = None

    def on_size(self, instance, value):
        self._update_fbo = 0
        self.picking_fbo.size = self.MPICKING_BUFFER_SIZE
        self.motion_blur_fbo.size = PICKING_BUFFER_SIZE

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, 0)
        UpdateNormalMatrix()
        PopMatrix()

    def define_rotate_angle(self, touch):
        x_angle = (touch.dx / self.width) * 360
        y_angle = -1 * (touch.dy / self.height) * 360
        return x_angle, y_angle

    def get_pixel_color(self, x, y):
        w = self.MPICKING_BUFFER_SIZE[0]
        h = self.MPICKING_BUFFER_SIZE[1]
        x = int(x)
        y = int(y)
        p = self.picking_fbo.pixels
        z = p[int(y * w * 4 + x * 4):int(y * w * 4 + x * 4 + 4)]
        try:
            z = [float(r) / 255.0 for i, r in enumerate(z)]
        except:
            z = [ord(r) / 255.0 for r in z]
        return z

    def get_fixed_points(self, x, y, move=False):
        # _size = EventLoop.window.system_size
        _size = Window.size
        _size = self.size
        if move:
            _x = x / _size[0]
            _y = y / _size[1]
            return _x * self.MPICKING_BUFFER_SIZE[0], _y * self.MPICKING_BUFFER_SIZE[1]

        #_x = x / _size[0]
        #_y = y / _size[1]
        pos = self.parent.pos
        if x < pos[0] or x > pos[0]+_size[0] or y < pos[1] or y > pos[1]+_size[1]:
            return -1, -1

        _x = (x-pos[0]) / _size[0]
        _y = (y-pos[1]) / _size[1]

        return _x * self.MPICKING_BUFFER_SIZE[0], _y * self.MPICKING_BUFFER_SIZE[1]

    def on_touch_down(self, touch):
        self.last_widget_str = "NONE"
        # transform the touch coordinate to local space
        x, y = self.get_fixed_points(touch.x, touch.y)
        if x == -1:
            return False
        pc = self.get_pixel_color(x, y)
        if not pc:
            return False
        if pc[0] == 0:
            return False

        pc[1] = pc[1]
        pc[2] = pc[2]

        t_touch = copy.copy(touch)
        t_touch = touch
        t_touch.x = int(pc[1] * PICKING_BUFFER_SIZE[0])
        t_touch.y = int(pc[2] * PICKING_BUFFER_SIZE[1])

        self.last_touch_pos = [t_touch.x, t_touch.y,
                               float(t_touch.x) / float(self.size[0]),
                               float(t_touch.x) / float(self.size[1])]
        t_touch.pos = (t_touch.x, t_touch.y)
        if pc[0] != 0:
            float_str = str(round(pc[0], 2))[0:4]
            if float(float_str) >= 0.50:
                float_str = str(round(float(float_str) - 0.50, 2))[0:4]
            if float_str in self.fbo_list:
                self.last_widget_str = float_str
                touch.ud["pick_value"] = float_str
                #ret = self.fbo_list[float_str].on_touch_down(t_touch)
                _size = self.fbo_list[float_str].size
                t_touch.x = int(pc[1] * _size[0])
                t_touch.y = int(pc[2] * _size[1])

                self.last_touch_pos = [t_touch.x, t_touch.y,
                                       float(t_touch.x) / float(self.size[0]),
                                       float(t_touch.x) / float(self.size[1])]
                t_touch.pos = (t_touch.x, t_touch.y)
                ret = self.fbo_list[float_str].dispatch("on_touch_down", t_touch)
                return True
                #return ret
        else:
            return False
        return True

    def on_touch_move(self, touch):
        if self.last_widget_str == "NONE":
           return False

        x, y = self.get_fixed_points(touch.x, touch.y)
        if x == -1:
            return False

        pc = self.get_pixel_color(x, y)
        if not pc:
            return False
        if pc[0] == 0:
            return False

        pc[1] = pc[1]
        pc[2] = pc[2]
        # fix
        if pc[0] != 0:
            float_str = str(round(pc[0], 2))[0:4]
            if float_str != self.last_widget_str:
               touch.x = self.last_touch_pos[0]
               touch.y = self.last_touch_pos[1]
               touch.sx = self.last_touch_pos[2]
               touch.sy = self.last_touch_pos[3]

            if float(float_str) >= 0.50:
                float_str = str(round(float(float_str) - 0.50, 2))[0:4]
            try:
                if touch.ud["pick_value"] != float_str:
                    return
            except:
                pass
             
 
        t_touch = copy.copy(touch)
        t_touch = touch
        t_touch.x = int(pc[1] * PICKING_BUFFER_SIZE[0])
        t_touch.y = int(pc[2] * PICKING_BUFFER_SIZE[1])

        if hasattr(touch, 'button'):
            if 'right' in t_touch.button:
                t_touch.pos = (t_touch.x, t_touch.y)
                return

        t_touch.sx = float(touch.x) / float(EventLoop.window.system_size[0])
        t_touch.sy = float(touch.y) / float(EventLoop.window.system_size[1])

        t_touch.sx = float(touch.x) / float(self.size[0])
        t_touch.sy = float(touch.y) / float(self.size[1])

        self.last_touch_pos = [t_touch.x, t_touch.y, t_touch.sx, t_touch.sy]
        if pc[0] != 0:
            float_str = str(round(pc[0], 2))[0:4]
            if float(float_str) >= 0.50:
                float_str = str(round(float(float_str) - 0.50, 2))[0:4]
            if float_str in self.fbo_list and float_str == self.last_widget_str:
                _size = self.fbo_list[float_str].size
                t_touch.x = int(pc[1] * _size[0])
                t_touch.y = int(pc[2] * _size[1])
                self.last_touch_pos = [t_touch.x, t_touch.y, t_touch.sx, t_touch.sy]

                ret = self.fbo_list[float_str].dispatch("on_touch_move", t_touch)
                #ret = self.fbo_list[float_str].on_touch_move(t_touch)
                return True
                #return ret
        else:
            return False

        return True

    def on_touch_up(self, touch):
        if self.last_widget_str == "NONE":
           return False

        x, y = self.get_fixed_points(touch.x, touch.y)
        if x == -1:
            return False

        pc = self.get_pixel_color(x, y)
        if not pc:
            return False
        if pc[0] == 0:
            return False

        pc[1] = pc[1]
        pc[2] = pc[2]
        t_touch = copy.copy(touch)
        t_touch = touch

        t_touch.x = self.last_touch_pos[0]
        t_touch.y = self.last_touch_pos[1]

        if pc[0] != 0:
            float_str = str(round(pc[0], 2))[0:4]
            if float(float_str) >= 0.50:
                float_str = str(round(float(float_str) - 0.50, 2))[0:4]
            if float_str in self.fbo_list:
                t_touch.sx = float(touch.x) / float(self.size[0])
                t_touch.sy = float(touch.y) / float(self.size[1])
                #t_touch.x = int(pc[1] * 128)
                #t_touch.y = int(pc[2] * 128)

                #ret = self.fbo_list[float_str].on_touch_up(t_touch)
                #ret = self.fbo_list[float_str].dispatch("on_touch_up", t_touch)
                return True
        else:
            return False
        return True
