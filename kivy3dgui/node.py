__author__ = 'kpiorno'
import os
import math
from textwrap import dedent 
from xml.dom.minidom import parse

from itertools import *
from kivy.graphics import *
from kivy.core.image import Image
from kivy.resources import resource_find
from kivy3dgui.objloader import ObjFile
from kivy.uix.widget import Widget
from kivy.properties import (BooleanProperty, ListProperty, StringProperty,
                             NumericProperty, ObjectProperty)
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.graphics.texture import Texture                             
from kivy3dgui.fbowidget import FboFloatLayout
from kivy.base import EventLoop
from kivy3dgui import canvas3d
from kivy.lang import Builder




def normalize(v):
    vmag = magnitude(v)
    if vmag == 0:
        vmag = 0.01
    return [v[i] / vmag for i in range(len(v))]


def min_vector(v1, v2):
    return [v1[i] - v2[i] for i, _ in enumerate(v1)]


def sum_vector(v1, v2):
    return [v1[i] + v2[i] for i, _ in enumerate(v1)]


def magnitude(v):
    return math.sqrt(sum(v[i] * v[i] for i in range(len(v))))


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def cpickle(filename, obj):
    # filename = filename.replace("/", "_")
    f = open(filename, "wb")
    d = pickle.dumps(obj)
    pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)
    f.close()


def cload(filename):
    if os.path.exists(filename):
        f = open(filename, "rb")
        print("")
        p = pickle.load(f)
        return pickle.loads(p), True
    return None, False


class ValuePickle:
    vertex = []
    index = []
    source = []


class ModelPickle:
    objs = []

    def __init__(self):
        self.objs = []


def load_md5(filename, anims):
    Rotate(0, 1.0, 1, 0).angle = 180.0
    t_file = "./kivy3dgui/cache/" + filename.replace("/", "_")
    obj, res = cload(t_file)
    result = []
    if res:
        for i in range(obj.numMeshes):
            obj.Meshes[i].kmesh = Mesh(
                vertices=obj.Meshes[i].kVertex[:],
                indices=obj.Meshes[i].Index,
                fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                     (b'blendIndices', 4, 'float'), (b'blendWeights', 4, 'float')],
                mode='triangles',
                source="./kivy3dgui/md5/" + obj.Meshes[i].texture,
            )
        obj.ChooseBufferedAnimation(0)
        result.append(obj)
        return result

    mesh = MD5_Model()
    mesh.LoadMesh(filename)
    for anim in anims:
        mesh.AddAnimation(anim)
    mesh.BufferAllBone()
    mesh.ChooseBufferedAnimation(0)
    # mesh.SetFrame(10)
    mesh.pickle()
    result.append(mesh)
    return result


def load_ogre(filename):
    _dom = parse(filename)
    root = _dom.getElementsByTagName("mesh")[0]
    skeleton_dom = root.getElementsByTagName("skeletonlink")[0]
    skeleton = Skeleton("./kivy3dgui/ogre/" + skeleton_dom.getAttribute("name") + ".xml")
    for mesh in root.getElementsByTagName("submeshes"):
        faces = mesh.getElementsByTagName("faces")[0].getElementsByTagName("face")
        indices = []
        verts = []
        bones_data = {}

        for face in faces:
            indices.append(int(face.getAttribute("v1")))
            indices.append(int(face.getAttribute("v2")))
            indices.append(int(face.getAttribute("v3")))

        bones = mesh.getElementsByTagName("boneassignments")[0].getElementsByTagName("vertexboneassignment")
        for bone in bones:
            b = [int(bone.getAttribute("vertexindex")), int(bone.getAttribute("boneindex")),
                 float(bone.getAttribute("weight"))]
            if b[0] not in bones_data:
                bones_data[b[0]] = [b]
            else:
                if len(bones_data[b[0]]) < 4:
                    bones_data[b[0]].append(b)

        vertices = mesh.getElementsByTagName("geometry")[0]. \
            getElementsByTagName("vertexbuffer")[0].getElementsByTagName("vertex")
        for i, vertex in enumerate(vertices):
            pos = vertex.getElementsByTagName("position")[0]
            normal = vertex.getElementsByTagName("normal")[0]
            texcoord = vertex.getElementsByTagName("texcoord")[0]
            pos = [float(pos.getAttribute("x")), float(pos.getAttribute("y")), float(pos.getAttribute("z"))]
            verts.append(pos[0])
            verts.append(pos[1])
            verts.append(pos[2])
            normal = [float(normal.getAttribute("x")), float(normal.getAttribute("y")), float(normal.getAttribute("z"))]
            verts.append(normal[0])
            verts.append(normal[1])
            verts.append(normal[2])

            texcoord = [float(texcoord.getAttribute("u")), float(texcoord.getAttribute("v"))]
            verts.append(texcoord[0])
            verts.append(texcoord[1])
            v_indices = [0, 0, 0, 0]
            v_weights = [0, 0, 0, 0]
            if i in bones_data:
                for j, b in enumerate(bones_data[i]):
                    v_indices[j] = b[1]
                    v_weights[j] = b[2]
                    # print ("Indices", v_indices)
            for e in v_indices:
                verts.append(e)

            for e in v_weights:
                verts.append(e)

        m = Mesh(
            vertices=verts,
            indices=indices,
            fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                 (b'blendIndices', 4, 'float'), (b'blendWeights', 4, 'float')],
            mode='triangles',
        )

        yield m, bones_data, skeleton, verts


class Node(Widget):
    name = StringProperty("None")
    scale = ListProperty([1., 1., 1.])
    rotate = ListProperty([1., 0., 1., 0.])
    pitch = NumericProperty(0.)
    yaw = NumericProperty(0.)
    roll = NumericProperty(0.)
    translate = ListProperty([0.0, 0.0, 0.0])
    effect = BooleanProperty(False)
    receive_shadows = BooleanProperty(True)
    cast_shadows = BooleanProperty(True)
    alpha_blending = BooleanProperty(False)
    flip_coords = BooleanProperty(True)
    lighting = BooleanProperty(True)
    texture = StringProperty("")
    normal_map = StringProperty("")
    _normal_map = StringProperty("")
    _instruction_group = ObjectProperty(None, allownone=True)
    specular_intensity = NumericProperty(0.0)
    specular_power = NumericProperty(0.0)
    min_light_intensity = NumericProperty(0.0)
    always_on_top = BooleanProperty(False)

    alpha = NumericProperty(1.0)
    alpha_threshold = NumericProperty(1.0)
    axis_type = NumericProperty(0)
    
    shadows_bias = NumericProperty(0.01)
    meta_value = NumericProperty(1)
    
    light_intensity = [1.0, 1.0, 1.0, 1.0]
    old_transformation = [1.0, 0.0, 0.0, 1300.0, True]
    orientation_vector = [1.0, 1.0, 1.0, 1.0]
    texture_size = ListProperty([-1, -1])
    _instructions = ListProperty([])
    _shadow_instructions = ListProperty([])
    _picking_instructions = ListProperty([])
    _blur_instructions = ListProperty([])

    _translate = None
    _rotate = None
    _scale = None
    
    vertices = []
    mesh = 0
    objs = ListProperty([])
    meshes = ListProperty([])
    bones_data = []
    skeletons = []
    init = 0
    _start_objs = True
    fbo_widget = None
    has_gui = False
    _update_fbo = 0
    pick_id = '0.01'
    current_anim_index = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Default")
        self.translate = kwargs.get("translate", (0., 0., 0.))
        self.rotate = kwargs.get("rotate", (0., 0., 1., 0.))
        self.pitch = kwargs.get("pitch", 0.)
        self.yaw = kwargs.get("yaw", 0.)
        self.roll = kwargs.get("roll", 0.)
        self.scale = kwargs.get("scale", (1., 1., 1.))
        self._objs = kwargs.get("objs", ())
        self._objs = kwargs.get("meshes", ())
        self._anims = kwargs.get("anims", [])
        self.effect = kwargs.get("effect", False)
        self.current_anim_index = kwargs.get("current_anim_index", 0)
        self.axis_type = kwargs.get("axis_type", 0)
        self.light_intensity = kwargs.get("light_intensity", [1.0, 1.0, 1.0, 1.0])
        self.min_light_intensity = kwargs.get("min_light_intensity", 0.0)
        self.specular_intensity = kwargs.get("specular_intensity", 0.0)
        self.specular_power = kwargs.get("specular_power", 0.0)
        self.normal_map = kwargs.get("normal_map", "")
        self._normal_map = kwargs.get("normal_map", "")
        self.alpha = kwargs.get("alpha", 1.0)
        self.alpha_threshold = kwargs.get("alpha_threshold", 1.0)
        self.shadows_bias = kwargs.get("shadows_bias", 0.01)
        self.meta_value = kwargs.get("meta_value", 1)
        
        self.objs = []

        if '__no_builder' in kwargs:
            self._start_objs = False

        self.has_gui = False
        self.fbo_widget = FboFloatLayout(size=(800, 600), size_hint=(None, None),
                                         clear_color=(0, 0, 0, 1.0))
        #self.fbo_widget.texture_size = self.texture_size
        super(Node, self).__init__(**kwargs)

    def get_pos(self):
        return self.orientation_vector[0:3]

    def update_pos(self):
        if self.old_transformation[4]:
            self.old_transformation[0:3] = self.translate[:]
            self.old_transformation[4] = False

    def on_alpha_blending(self, widget, value):
        if self.fbo_widget is not None:
            self.fbo_widget.alpha_blending = self.alpha_blending
            
    def load_kv_file(self, file_path):
        for e in self.fbo_widget.children:
            self.fbo_widget.remove_widget(e)
            
        if os.path.isfile(file_path):
            res = Builder.load_file(file_path)
            self.add_widget(res)
            
    def on_meshes(self, widget, value):
        if self.init == -1:
            return
        self._objs = value[:]
        if not self._start_objs:
            for obj in value[:]:
                if ".md5anim" in obj:
                    self._anims.append(obj)

            self._objs = value[:]

            self.parent.add_node(self)
            self._start_objs = True
            if self.init >= 3:
                self._start_objs = True

        self.populate_fbo(self.fbo_widget)

    def on_scale(self, widget, value):
        if self._scale is not None:
            self._scale.xyz = value[0:3]
            self._shadow_scale.xyz = value[0:3]
            self._picking_scale.xyz = value[0:3]
            self._motion_blur_scale.xyz = value[0:3]

    def on_translate(self, widget, value):
        if self._translate is not None:
            self.orientation_vector = [self.old_transformation[0],
                                       self.old_transformation[1],
                                       self.old_transformation[2]]
            self._translate.xyz = value[0:3]
            self._shadow_translate.xyz = value[0:3]
            self._picking_translate.xyz = value[0:3]
            self._motion_blur_translate.xyz = value[0:3]
            self.old_transformation[0:3] = value[0:3]

    def on_rotate(self, widget, value):
        if self._rotate is not None:
            self._rotate.set(*value)
            self._shadow_rotate.set(*value)
            self._picking_rotate.set(*value)
            self._motion_blur_rotate.set(*value)
            
            

    def add_widget(self, *largs):
        self.has_gui = True
        self.fbo_widget.add_widget(largs[0])
        self.populate_fbo(self.fbo_widget)

    def populate_fbo(self, fbo):
        if not self.has_gui:
            return
        EventLoop.ensure_window()
        if self._update_fbo < 2:
            for obj in self.objs:
                if self.texture_size[0] == -1:
                    self.fbo_widget.size = canvas3d.PICKING_BUFFER_SIZE
                    #self.fbo_widget.size = (512, 512)
                else:
                    self.fbo_widget.size = self.texture_size
                    #self.fbo_widget.size = (512, 512)

                if self.texture_size[0] == -1:
                    self.fbo_widget.fbo.size = canvas3d.PICKING_BUFFER_SIZE
                    #self.fbo_widget.fbo.size  = (512, 512)
                else:
                    self.fbo_widget.fbo.size = self.texture_size
                    #self.fbo_widget.fbo.size = (512, 512)
                obj.texture = self.fbo_widget.fbo.texture
                with self.fbo_widget.fbo:
                    ClearColor(1, 1, 1, 1)
        self.flip_coords = False

    def on_normal_map(self, widget, value):
        self._normal_map = value

        if len(self._normal_map) > 0 and self._instruction_group:
            image = Image(value)
            bind_texture = BindTexture(texture=image.texture, index=2)
            state = ChangeState(#enabled_shadow=(float(self.receive_shadows)),
                                lighting=(float(self.lighting)),
                                light_intensity=self.light_intensity,
                                flip_coords=(float(self.flip_coords)),
                                #alpha=(float(self.alpha)),
                                #shadows_bias=(shadows_bias(self.alpha)),
                                normal_map_enabled=(float(1)),
                                #specular_intensity=(float(self.specular_intensity)),
                                #specular_power=(float(self.specular_power)),
                                #min_light_intensity=(float(self.min_light_intensity))"""
                                )


            self._instruction_group.remove(self.state)
            self._instruction_group.add(bind_texture)
            self._instruction_group.add(state)
            
            
    def before_render(self, *args):
        if self.always_on_top:
            m_origin_depth = glGetBooleanv(GL_DEPTH_TEST)
            m_origin_cull = glGetBooleanv(GL_CULL_FACE);

            #setAlphaBlending(True)
            
            glEnable (GL_BLEND)
            glBlendFunc (GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
            

            glDisable(GL_DEPTH_TEST)
            glDisable(GL_CULL_FACE)   
        
    def after_render(self, *args):
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glEnable(GL_BLEND)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)        
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        

    def update_params(self, *args):
        self.current_callback(self)

    def update_params_fbo(self, *args):
        self.current_callback_fbo(self)

    def update_params_picking_fbo(self, *args):
        self.current_callback_picking_fbo(self)
        
    def start(self, current_callback):
        if self.init == 0:
            self.current_callback = current_callback
            Color(1, 1, 1, 1)

            normal_map_value = 0
            if len(self._normal_map) > 0:
                normal_map_value = 1
                image = Image(self._normal_map)
                bind_texture = BindTexture(texture=image.texture, index=2)
            
            self._instruction_group = InstructionGroup()
            
            
            self._instruction_group.add(Callback(self.update_params))  
            
            self.state = ChangeState(#enabled_shadow=(float(self.receive_shadows)),
                                     lighting=(float(self.lighting)),
                                     light_intensity=self.light_intensity,
                                     flip_coords=(float(self.flip_coords)),
                                     #alpha=(float(self.alpha)),
                                     #pitch=(float(self.pitch)),
                                     #yaw=self.yaw,
                                     #roll=(float(self.roll)),
                                     #shadows_bias = (float(self.shadows_bias)),
                                     normal_map_enabled=(float(normal_map_value)),
                                     #specular_intensity = (float(self.specular_intensity)),
                                     #specular_power = (float(self.specular_power)),
                                     #min_light_intensity=(float(self.min_light_intensity))
                                     )

        

            self._instruction_group.add(self.state)
            self._translate = Translate(*self.translate)


            self._rotate = Rotate(*self.rotate)
            self._scale = Scale(*self.scale)

            self._instructions.append(self.state)
            self._instructions.append(self._translate)
            self._instructions.append(self._rotate)
            self._instructions.append(self._scale)
            self._instructions.append(self._instruction_group)
            self._instructions.append(Callback(self.before_render))
            


        elif self.init == 1:
            self.current_callback_fbo = current_callback
            self._shadow_instructions.append(Callback(self.update_params_fbo)) 
            #state = ChangeState(cast_shadows=(float(self.cast_shadows)))
                                             
            self._shadow_translate = Translate(*self.translate)
            self._shadow_rotate = Rotate(*self.rotate)
            #self._scale = Scale(*self.scale)
            
            self._shadow_scale = Scale(*self.scale)
            #self._shadow_instructions.append(state)
            self._shadow_instructions.append(self._shadow_translate)
            self._shadow_instructions.append(self._shadow_rotate)
            
            self._shadow_instructions.append(self._shadow_scale)
            #self._instructions.append(Callback(self.before_render))

        elif self.init == 2:
            self.current_callback_picking_fbo = current_callback
            mrange = 0
            if self.effect:
                mrange = 0.50
            
            self._picking_instructions.append(Callback(self.update_params_picking_fbo))     
            state = ChangeState(id_color=(round(self.pick_id + mrange, 2), float(self.effect), 0.0))
            self._picking_translate = Translate(*self.translate)
            self._picking_rotate = Rotate(*self.rotate)
            
            self._picking_scale = Scale(*self.scale)
            self._picking_instructions.append(state)
            self._picking_instructions.append(self._picking_translate)
            self._picking_instructions.append(self._picking_rotate)
            
            self._picking_instructions.append(self._picking_scale)
            self._instructions.append(Callback(self.before_render))

        elif self.init == 3:
            state = ChangeState(id=(self.motion_id))
            self._motion_blur_translate = Translate(*self.translate)
            self._motion_blur_rotate = Rotate(*self.rotate)
            self._motion_blur_scale = Scale(*self.scale)
            self._blur_instructions.append(state)
            self._blur_instructions.append(self._motion_blur_translate)
            self._blur_instructions.append(self._motion_blur_rotate)
            self._blur_instructions.append(self._motion_blur_scale)
            self._instructions.append(Callback(self.before_render))

        UpdateNormalMatrix()
        for e in self._objs:
            _vertices = []
            _indices = []
            if ".obj" in e:
                filename = resource_find(e)
                if not filename:
                    raise IOError("File: '{0}' not found".format(e))
                m = ObjFile(resource_find(e))
                m = list(m.objects.values())[0]
                res = []
                count = 0
                for i, o in enumerate(m.vertices):
                    res.append(o)
                    if (i + 1) % 8 == 0:
                        count += 1
                        res.append(0.0)
                        res.append(0.0)
                        res.append(0.0)

                        res.append(i // 8)
                        res.append(i // 8)

                        if count >= 3:
                            l = len(res)
                            v0 = [res[l - 13 * 3], res[l - 13 * 3 + 1], res[l - 13 * 3 + 2]]
                            v1 = [res[l - 13 * 2], res[l - 13 * 2 + 1], res[l - 13 * 2 + 2]]
                            v2 = [res[l - 13 * 1], res[l - 13 * 1 + 1], res[l - 13 * 1 + 2]]

                            t0xy = [res[l - 13 * 3 + 6], res[l - 13 * 3 + 7]]
                            t1xy = [res[l - 13 * 2 + 6], res[l - 13 * 2 + 7]]
                            t2xy = [res[l - 13 + 6], res[l - 13 + 7]]

                            edge1 = min_vector(v1, v0)
                            edge2 = min_vector(v2, v0)

                            delta_u1 = t1xy[0] - t0xy[0]
                            delta_v1 = t1xy[1] - t0xy[1]

                            delta_u2 = t2xy[0] - t0xy[0]
                            delta_v2 = t2xy[1] - t0xy[1]

                            d = (delta_u1 * delta_v2 - delta_u2 * delta_v1)
                            if d == 0:
                                d = 0.01
                            f = 1.0 / d;

                            tangent_x = f * (delta_v2 * edge1[0] - delta_v1 * edge2[0])
                            tangent_y = f * (delta_v2 * edge1[1] - delta_v1 * edge2[1])
                            tangent_z = f * (delta_v2 * edge1[2] - delta_v1 * edge2[2])

                            for _i in range(1, 4):
                                res[l - 13 * _i + 8] += tangent_x
                                res[l - 13 * _i + 9] += tangent_y
                                res[l - 13 * _i + 10] += tangent_z

                            count = 0

                for i in range(len(res)):
                    if (i + 1) % 13 == 0:
                        vec = [res[i - 12 + 8], res[i - 12 + 9], res[i - 12 + 10]]
                        n_vec = normalize(vec)
                        res[i - 12 + 8] = n_vec[0]
                        res[i - 12 + 9] = n_vec[1]
                        res[i - 12 + 10] = n_vec[2]

                m.vertices = res
                _vertices = m.vertices
                _indices = m.indices
                if self.init != 3:
                    mesh = Mesh(
                        vertices=_vertices,
                        indices=_indices,
                        fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                             (b'tangent', 3, 'float'), (b'vert_pos', 2, 'float')],
                        mode='triangles',
                        source=e + ".png",
                    )
                    self.objs.append(mesh)
                    if self.init == 0:
                        self._instructions.append(mesh)
                    if self.init == 1:
                        self._shadow_instructions.append(mesh)
                    if self.init == 2:
                        self._picking_instructions.append(mesh)
                    if self.init == 3:
                        self._blur_instructions.append(mesh)

            if (".dae" in e) or ('.xml' in e and not ".mesh.xml" in e):
                raise Exception("Collada not yet implemented")
                for o in load_dae_scene(e):
                    self.objs.append(o)
                    if self.init == 0:
                        self.mesh = o

            if ".mesh.xml" in e:
                for o, ba, skel, vert in load_ogre(e):
                    self.skeletons = skel
                    self.objs.append(o)
                    self.bones_data.append(ba)
                    self.vertices = vert[:]
                    if self.init == 0:
                        self.mesh = o

            if ".md5mesh" in e:
                raise Exception("MD5 not implemented")
                for o in load_md5(e, self._anims):
                    self.objs.append(o)
                    if self.init == 0:
                        self.mesh = o

        self._instructions.append(Callback(self.after_render))
        self.init += 1
    def get_properties(self):
        r_dict = {
            "id": self.id,   
            "name": self.name,                 
            "translate": self.translate,
            "rotate": self.rotate,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "roll": self.roll,
            "scale": self.scale,
            "meshes": self.meshes,
            "anims": self._anims,
            "effect": self.effect,
            "current_anim_index": self.current_anim_index,
            "axis_type": self.axis_type,
            "light_intensity": self.light_intensity,
            "min_light_intensity": self.min_light_intensity,
            "specular_intensity": self.specular_intensity,
            "specular_power": self.specular_power,
            "normal_map": self.normal_map,
            "alpha": self.alpha,
            "alpha_threshold": self.alpha_threshold,
            "shadows_bias": self.shadows_bias
        }
        return r_dict        

    def remove_a(self):
        if self.fbo_widget:
            self.fbo_widget.clear_widgets()
            self.fbo_widget = None

    def clear(self):
        self.init = -1
        self.meshes = []

        self.obj = []

        self.remove_a()

        self.vertices = []
