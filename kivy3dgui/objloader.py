from kivy.logger import Logger
import os


class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vertex_format = [
            ('v_pos', 3, 'float'),
            ('v_normal', 3, 'float'),
            ('v_tc0', 2, 'float')]
        self.vertices = []
        self.indices = []

    def calculate_normals(self):
        for i in range(len(self.indices) / (3)):
            fi = i * 3
            v1i = self.indices[fi]
            v2i = self.indices[fi + 1]
            v3i = self.indices[fi + 2]

            vs = self.vertices
            p1 = [vs[v1i + c] for c in range(3)]
            p2 = [vs[v2i + c] for c in range(3)]
            p3 = [vs[v3i + c] for c in range(3)]

            u,v  = [0,0,0], [0,0,0]
            for j in range(3):
                v[j] = p2[j] - p1[j]
                u[j] = p3[j] - p1[j]

            n = [0,0,0]
            n[0] = u[1] * v[2] - u[2] * v[1]
            n[1] = u[2] * v[0] - u[0] * v[2]
            n[2] = u[0] * v[1] - u[1] * v[0]

            for k in range(3):
                self.vertices[v1i + 3 + k] = n[k]
                self.vertices[v2i + 3 + k] = n[k]
                self.vertices[v3i + 3 + k] = n[k]


class ObjFile:
    def finish_object(self):
        if self._current_object == None:
            return

        mesh = [MeshData()]
        cont_mesh=0
        idx = 0
        for f in self.faces:
            verts =  f[0]
            norms = f[1]
            tcs = f[2]
            material_ = list(map(float, f[3]))
            
            if len(mesh[cont_mesh].indices) == 65535:
                mesh.append(MeshData())
                cont_mesh+=1   
                idx=0 
            
            for i in range(3):
                #get normal components
                n = (0.0, 0.0, 0.0)
                if norms[i] != -1:
                    n = self.normals[norms[i]-1]

                #get texture coordinate components
                t = (0.4, 0.4)
                if tcs[i] != -1:
                    t = self.texcoords[tcs[i]-1]

                #get vertex components
                v = self.vertices[verts[i]-1]

                data = [v[0], v[1], v[2], n[0], n[1], n[2], t[0], t[1], material_[0], material_[1], material_[2]]
                mesh[cont_mesh].vertices.extend(data)

            
                
            tri = [idx, idx+1, idx+2]       
            mesh[cont_mesh].indices.extend(tri)
            idx += 3

        self.objects[self._current_object] = mesh
        #mesh.calculate_normals()
        self.faces = []

    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.objects = {}
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.mtl = None

        self._current_object = None

        material = None

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            if line.startswith('s'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'o':
                self.finish_object()
                self._current_object = values[1]
            elif values[0] == 'mtllib':
                mtl_path = mtl_filename = values[1]
                if (os.path.isabs(filename) and not os.path.isabs(mtl_filename)) or \
                   (os.path.dirname(filename) and not os.path.dirname(mtl_filename)):
                    # if needed, correct the mtl path to be relative or same-dir to/as the object path  
                    mtl_path = os.path.join(os.path.dirname(filename), mtl_filename)
                self.mtl = MTL(mtl_path)
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(-1)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(-1)
                self.faces.append((face, norms, texcoords, self.mtl[material]["Kd"] if self.mtl!=None else [1., 1., 1.]))
        self.finish_object()


def MTL(filename):
    contents = {}
    mtl = None
    if not os.path.exists(filename):
        return
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        mtl[values[0]] = values[1:]
    return contents
