import moderngl
from gpuproglib import WindowInterface, run_interface
from pathlib import Path
import numpy as np
import sys


class Fractal(WindowInterface):
    def reload(self):
        self.prog = self.load_prog()
        self.center = self.prog['Center']
        self.iter = self.prog['Iter']
        self.vao.release()
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')
        for res_key in self.prog:
            resource = self.prog[res_key]
            for attribute_key in dir(resource):
                if attribute_key.startswith('_'):
                    continue
                if attribute_key in ('extra', 'mglo'):
                    continue
                try:
                    print(f'{resource}.{attribute_key}: {getattr(resource, attribute_key)}')
                except AttributeError as ae:
                    print(ae)

        if 'u_time' in self.prog:
            self.u_time = self.prog['u_time']
        else:
            self.u_time = None

    def __init__(self):
        self.ctx = moderngl.create_context()
        self.fs_path = Path.cwd() / 'fsq.frag'
        if len(sys.argv) > 1:
            pth = Path(sys.argv[1]).absolute()
            print(f'using fragment shader: {pth}')


        self.vs_path = Path(__file__).parent / 'fsq.vert'


        self.prog = self.load_prog()

        self.center: moderngl.Uniform = self.prog['Center']
        self.iter: moderngl.Uniform = self.prog['Iter']
        self.u_time: moderngl.Uniform = None
        if 'u_time' in self.prog:
            self.u_time = self.prog['u_time']

        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def load_prog(self):
        try:
            newprog = self.ctx.program(
                vertex_shader=self.vs_path.read_text(),
                fragment_shader=self.fs_path.read_text()
            )
            return newprog
        except moderngl.Error as e:
            print(e)
            return self.prog

    def render(self):
        self.ctx.viewport = self.wnd.viewport
        self.ctx.clear(1.0, 1.0, 1.0)

        self.center.value = (0.49, 0.32)
        self.iter.value = 100
        if self.u_time:
            self.u_time.value = self.wnd.time
            # print(self.wnd.time)

        self.vao.render(moderngl.TRIANGLE_STRIP)


if __name__ == '__main__':
    print(__file__)
    run_interface(Fractal)
