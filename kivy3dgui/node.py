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
try:
    import collada
except:
    print("Not collada")


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def cpickle(filename, obj):
    #filename = filename.replace("/", "_")
    f = open(filename, "wb")
    d = pickle.dumps(obj)
    pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)
    f.close()


def cload(filename):
    #t_file = "./kivy3dgui/cache/" + filename.replace("/", "_")
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
                    #source="./kivy3dgui/imgs/duckCM.png",

                    #texture=video.texture,
             )
        obj.ChooseBufferedAnimation(0)
        result.append(obj)
        return result
        #return obj

    mesh = MD5_Model()
    mesh.LoadMesh(filename)

    #mesh.AddAnimation("./kivy3dgui/md5/bomb/bob_lamp_update.md5mesh")
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
            #print (bones_data)
            if i in bones_data:
                for j, b in enumerate(bones_data[i]):
                    v_indices[j] = b[1]
                    v_weights[j] = b[2]
                    #print ("Indices", v_indices)
            for e in v_indices:
                verts.append(e)

            for e in v_weights:
                verts.append(e)

        #print("indices", indices)
        m = Mesh(
            vertices=verts,
            indices=indices,
            fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                 (b'blendIndices', 4, 'float'), (b'blendWeights', 4, 'float')],
            mode='triangles',
            #source=e+".png",
            #texture=video.texture,
        )

        yield m, bones_data, skeleton, verts



def load_dae_scene(filename):
    if filename == "./kivy3dgui/dae/porshe.dae":
        Rotate(0, 0, 1, 1).angle = 180.0

    file = "./kivy3dgui/cache/" + filename.replace("/", "_")
    obj, res = cload(file)
    if res:
        for mobj in obj.objs:
            mesh = Mesh(
                vertices=mobj.vertex,
                indices=mobj.index,
                fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                     (b'vert_pos', 2, 'float')],
                mode='triangles',
                source=mobj.source,
                #texture=video.texture,
            )
            yield mesh

    if not res:
        collada_file = collada.Collada(filename, ignore=[collada.DaeUnsupportedError,
                                                         collada.DaeBrokenRefError])

    pobject = ModelPickle()
    if not res and collada_file.scene is not None:
        for geom in collada_file.scene.objects('geometry'):
            for prim in geom.primitives():
                mat = prim.material
                diff_color = (0.3, 0.3, 0.3, 1.0)
                spec_color = None
                shininess = None
                amb_color = None
                tex_id = None
                #shader_prog = self.shaders[mat.effect.shadingtype]
                if mat is None:
                    continue
                for prop in mat.effect.supported:
                    value = getattr(mat.effect, prop)
                    # it can be a float, a color (tuple) or a Map
                    # ( a texture )
                    if isinstance(value, collada.material.Map):
                        colladaimage = value.sampler.surface.image
                        tex_id = colladaimage
                        # Accessing this attribute forces the
                        # loading of the image using PIL if
                        # available. Unless it is already loaded.
                        img = colladaimage.pilimage
                        if img: # can read and PIL available
                            #shader_prog = self.shaders['texture']
                            # See if we already have texture for this image
                            if self.textures.has_key(colladaimage.id):
                                tex_id = self.textures[colladaimage.id]
                            else:
                                # If not - create new texture
                                try:
                                    # get image meta-data
                                    # (dimensions) and data
                                    (ix, iy, tex_data) = (img.size[0], img.size[1], img.tostring("raw", "RGBA", 0, -1))
                                except SystemError:
                                    # has no alpha channel,
                                    # synthesize one
                                    (ix, iy, tex_data) = (img.size[0], img.size[1], img.tostring("raw", "RGBX", 0, -1))
                                    # generate a texture ID
                                tid = GLuint()
                                glGenTextures(1, ctypes.byref(tid))
                                tex_id = tid.value
                                # make it current
                                glBindTexture(GL_TEXTURE_2D, tex_id)
                                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                                # copy the texture into the
                                # current texture ID
                                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)

                                self.textures[colladaimage.id] = tex_id
                        else:
                            print("T")
                    else:
                        if prop == 'diffuse' and value is not None:
                            diff_color = value
                        elif prop == 'specular' and value is not None:
                            spec_color = value
                        elif prop == 'ambient' and value is not None:
                            amb_color = value
                        elif prop == 'shininess' and value is not None:
                            shininess = value

                # use primitive-specific ways to get triangles
                prim_type = type(prim).__name__
                if prim_type == 'BoundTriangleSet':
                    triangles = prim
                elif prim_type == 'BoundPolylist':
                    triangles = prim.triangleset()
                else:
                    print('Unsupported mesh used:', prim_type)
                    triangles = None

                _vertices = []
                _indices = []
                _uv = []
                if triangles is not None:
                    triangles.generateNormals()
                    # We will need flat lists for VBO (batch) initialization
                    vertices = triangles.vertex.flatten().tolist()
                    batch_len = len(vertices) // 3
                    indices = triangles.vertex_index.flatten().tolist()
                    normals = triangles.normal.flatten().tolist()
                    # Track maximum and minimum Z coordinates
                    # (every third element) in the flattened
                    # vertex list
                    if tex_id is not None:
                        # This is probably the most inefficient
                        # way to get correct texture coordinate
                        # list (uv). I am sure that I just do not
                        # understand enough how texture
                        # coordinates and corresponding indexes
                        # are related to the vertices and vertex
                        # indicies here, but this is what I found
                        # to work. Feel free to improve the way
                        # texture coordinates (uv) are collected
                        # for batch.add_indexed() invocation.
                        uv = [[0.0, 0.0]] * batch_len
                        for t in triangles:
                            nidx = 0
                            texcoords = t.texcoords[0]
                            for vidx in t.indices:
                                uv[vidx] = texcoords[nidx].tolist()
                                nidx += 1
                                # Flatten the uv list
                        uv = [item for sublist in uv for item in sublist]
                        _uv = uv
                    else:
                        pass

                    _v = grouper(vertices, 3)
                    _n = iter(grouper(normals, 3))
                    _u = iter(grouper(_uv, 2))

                    for i, e in enumerate(_v):
                        f = chain(e, _n.__next__())
                        if _uv != []:
                            f = chain(f, _u.__next__())
                        else:
                            f = chain(f, [0, 0])
                        f = chain(f, [i, i])
                        _vertices = chain(_vertices, f)

                    _indices = indices
                    c_path = ""
                    if tex_id is not None:
                        c_path = "./kivy3dgui/imgs/" + tex_id.path

                f_vertices = list(_vertices)[:]
                f_indices = list(_indices)[:]

                value = ValuePickle()
                value.vertex = f_vertices
                value.index = f_indices
                value.source = c_path
                pobject.objs.append(value)

                mesh = Mesh(
                    vertices=f_vertices,
                    indices=f_indices,
                    fmt=[(b'v_pos', 3, 'float'), (b'v_normal', 3, 'float'), (b'v_tc0', 2, 'float'),
                         (b'vert_pos', 2, 'float')],
                    mode='triangles',
                    source=c_path,
                    #texture=video.texture,
                )
                yield mesh
        cpickle(file, pobject)


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
        #self.fbo_widget.alpha_blending = self.alpha_blending
        #self.fbo_widget.fbo.add_reload_observer(self.populate_fbo)

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
        if not self._start_objs:
            #self._objs = self.meshes[:]
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
            #print (self.old_transformation, "O", value, "I")
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
        # trick to attach kivy3dgui instructino to fbo instead of canvas
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
        #self._update_fbo += 1
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
                    #source="./kivy3dgui/imgs/backhouse/imgback.jpg",
                    #texture=video.texture,
                )
                self.objs.append(mesh)

            if (".dae" in e) or ('.xml' in e and not ".mesh.xml" in e):
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
                for o in load_md5(e, self._anims):
                    self.objs.append(o)
                    if self.init == 0:
                        self.mesh = o

        self.init += 1



