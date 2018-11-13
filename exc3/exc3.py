import moderngl
from pathlib import Path

import numpy as np

from gpuproglib import WindowInterface, run_interface


class Exc3(WindowInterface):
    def __init__(self):
        self.ctx = moderngl.create_context()
        vs_path = Path.cwd() / 'exc3.vert'
        fs_path = Path.cwd() / 'exc3.frag'

        self.prog = self.ctx.program(
            vertex_shader=vs_path.read_text(),
            fragment_shader=fs_path.read_text()
        )

        vertices = np.array([
            0.0, 0.8,
            -0.6, -0.8,
            0.6, -0.8,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self):
        self.ctx.viewport = self.wnd.viewport
        self.ctx.clear(1.0, 1.0, 1.0)
        self.vao.render()


if __name__ == '__main__':
    run_interface(Exc3)
