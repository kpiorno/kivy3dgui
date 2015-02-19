__author__ = 'kpiorno'
import os
from xml.dom.minidom import parse
from itertools import *
from kivy.graphics import *
from kivy.resources import resource_find
from kivy3dgui.objloader import ObjFile
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy3dgui.fbowidget import FboFloatLayout
from kivy.base import EventLoop
from kivy3dgui.canvas3d import PICKING_BUFFER_SIZE


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def cpickle(filename, obj):
    #filename = filename.replace("/", "_")
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
    #mesh.SetFrame(10)
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
                    #print ("Indices", v_indices)
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
    scale = ListProperty([1., 1., 1.])
    rotate = ListProperty([1., 0., 1., 0.])
    translate = ListProperty([0.0, 0.0, 0.0])
    effect = BooleanProperty(False)
    receive_shadows = BooleanProperty(True)
    cast_shadows = BooleanProperty(True)
    alpha_blending = BooleanProperty(False)
    flip_coords = BooleanProperty(True)
    lighting = BooleanProperty(True)
    texture = StringProperty("")
    light_intensity = [1.0, 1.0, 1.0, 1.0]
    old_transformation = [1.0, 0.0, 0.0, 1300.0, True]
    orientation_vector = [1.0, 1.0, 1.0, 1.0]
    _translate = None
    _rotate = None
    _scale = None
    vertices = []
    mesh = 0
    objs = []
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
        self.translate = kwargs.get("translate", (0., 0., 0.))
        self.rotate = kwargs.get("rotate", (1., 0., 1., 0.))
        self.scale = kwargs.get("scale", (1., 1., 1.))
        self._objs = kwargs.get("objs", ())
        self._objs = kwargs.get("meshes", ())
        self._anims = kwargs.get("anims", [])
        self.effect = kwargs.get("effect", False)
        self.current_anim_index = kwargs.get("current_anim_index", 0)
        self.light_intensity = kwargs.get("light_intensity", [1.0, 1.0, 1.0, 1.0])
        self.objs = []
        if '__no_builder' in kwargs:
            self._start_objs = False

        self.has_gui = False
        self.fbo_widget = FboFloatLayout(size=PICKING_BUFFER_SIZE, size_hint=(None, None),
                                         pos_hint={"x": 0.0, "y": 0.0})

        super(Widget, self).__init__(**kwargs)

    def get_pos(self):
        return self.orientation_vector[0:3]

    def update_pos(self):
        if self.old_transformation[4]:
            self.old_transformation[0:3] = self.translate[:]
            self.old_transformation[4] = False


    def on_alpha_blending(self, widget, value):
        if self.fbo_widget is not None:
            self.fbo_widget.alpha_blending = self.alpha_blending

    def on_meshes(self, widget, value):
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
                self.fbo_widget.size = PICKING_BUFFER_SIZE
                self.fbo_widget.fbo.size = PICKING_BUFFER_SIZE
                obj.texture = self.fbo_widget.fbo.texture
                with self.fbo_widget.fbo:
                        ClearColor(1, 1, 1, 1)
        self.flip_coords = False

    def start(self):
        if self.init == 0:
            Color(1, 1, 1, 1)
            s = ChangeState(enabled_shadow=(float(self.receive_shadows)),
                        lighting=(float(self.lighting)),
                        light_intensity=self.light_intensity,
                        flip_coords=(float(self.flip_coords)))
            self._translate = Translate(*self.translate)
            self._rotate = Rotate(*self.rotate)
            self._scale = Scale(*self.scale)
        elif self.init == 1:
            ChangeState(cast_shadows=(float(self.cast_shadows)))
            self._shadow_translate = Translate(*self.translate)
            self._shadow_rotate = Rotate(*self.rotate)
            self._shadow_scale = Scale(*self.scale)
        elif self.init == 2:
            range = 0
            if self.effect:
                range = 0.50
            ChangeState(id_color=(round(self.pick_id + range, 2), float(self.effect), 0.0))
            self._picking_translate = Translate(*self.translate)
            self._picking_rotate = Rotate(*self.rotate)
            self._picking_scale = Scale(*self.scale)
        elif self.init == 3:
            ChangeState(id=(self.motion_id))
            self._motion_blur_translate = Translate(*self.translate)
            self._motion_blur_rotate = Rotate(*self.rotate)
            self._motion_blur_scale = Scale(*self.scale)

        UpdateNormalMatrix()
        for e in self._objs:
            _vertices = []
            _indices = []
            if ".obj" in e:
                m = ObjFile(resource_find(e))
                m = list(m.objects.values())[0]
                res = []
                for i, o in enumerate(m.vertices):
                    res.append(o)
                    if (i + 1) % 8 == 0:
                        res.append(i // 8)
                        res.append(i // 8)
                m.vertices = res
                _vertices = m.vertices
                _indices = m.indices
                mesh = Mesh(
                    vertices=_vertices,
                    indices=_indices,
                    fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                         (b'vert_pos', 2, 'float')],
                    mode='triangles',
                    source=e+".png",
                )
                self.objs.append(mesh)

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

        self.init += 1



