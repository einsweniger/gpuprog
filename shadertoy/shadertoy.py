from typing import List, Callable, Tuple, Union

import moderngl
import numpy as np
import math
from PIL import Image
import sys
from pathlib import Path
from datetime import datetime

from gpuproglib import WindowInterface, run_interface
from gpuproglib.camera import Camera
from gpuproglib.primitives import create_plane


class ShaderToy(WindowInterface):
    def reload(self):
        print('reload')
        self.reload_prog()
        self.reload_uniforms()
        self.reload_vertex_array()
        sys.stdout.flush()

    def reload_prog(self):
        try:
            version = '#version 430\n'
            header_path = Path(__file__).parent / 'image' / 'header.glsl'
            footer_path = Path(__file__).parent / 'image' / 'footer.glsl'
            header = header_path.read_text()
            footer = footer_path.read_text()
            shadertoy = self.fs_path.read_text()
            newprog = self.ctx.program(
                vertex_shader=self.vs_path.read_text(),
                fragment_shader=version+header+shadertoy+footer
            )
            if self.prog:
                self.prog.release()
            self.prog = newprog
        except moderngl.Error as e:
            print(e)

    def reload_vertex_array(self):
        vao_inputs = ('in_vert',)

        if not self.prog:
            return

        if self.vao:
            self.vao.release()

        if not all([name in self.prog for name in vao_inputs]):
            print(f'missing attribute names in shader, cannot init vertex array object')
            self.vao = None
            return

        self.vao = self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')


    def open_and_create_texture(self, name: str, convert: str = 'RGB', transpose: int = Image.FLIP_TOP_BOTTOM):
        path = Path(__file__).parent / 'textures' / name
        image = Image.open(path).convert(convert).transpose(transpose)
        return self.ctx.texture(image.size, 3, image.tobytes())

    def __init__(self):
        self.light_dir = np.array([1.0, 1.0, 0.0])

        self.ctx = moderngl.create_context()
        self.fs_path = Path.cwd() / 'fsq.frag'
        if len(sys.argv) == 1:
            print('must provide a shadertoy as argument')
            raise SystemExit()

        if len(sys.argv) > 1:
            self.fs_path = Path(sys.argv[1]).absolute()
            print(f'using fragment shader: {self.fs_path}')

        self.vs_path = Path(__file__).parent / 'fsq.vert'

        self.prog: moderngl.Program = None
        self.reload_prog()

        self.active_uniforms: List[moderngl.Uniform] = []

        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao: moderngl.VertexArray = None
        self.reload_vertex_array()

        self.lastRotated = False
        self.mouse = (0.0, 0.0)

        self.reload_uniforms()

    def render(self):
        self.ctx.viewport = self.wnd.viewport
        if self.wnd.mouse_pressed and self.lastRotated:
            dxy = np.array(self.mouse) - np.array(self.wnd.mouse)
            dxy = dxy / np.array(self.WINDOW_SIZE)
        self.mouse = self.wnd.mouse
        self.lastRotated = self.wnd.mouse_pressed

        if self.wnd.keys[0x25]:
            self.light_dir[0] += 0.01
        if self.wnd.keys[0x27]:
            self.light_dir[0] -= 0.01

        self.ctx.clear(1.0, 1.0, 1.0)
        for uniform in self.active_uniforms:
            uniform.extra()
        if self.vao:
            self.vao.render(moderngl.TRIANGLE_STRIP)

    def is_uniform(self, key):
        return type(self.prog[key]) is moderngl.Uniform

    def iTime(self):
        return np.array([self.wnd.time])

    def iResolution(self):
        x, y = self.wnd.size
        return x, y, 0

    def iMouse(self)->Tuple:
        x, y = self.wnd.mouse
        y = self.wnd.size[1] - y
        if self.wnd.mouse_pressed:
            return x, y, x, y
        return x, y, 0., 0.

    def iDate(self):
        d = datetime.now()
        secs = d.hour*3600 + d.minute * 60 + d.second
        secs += d.microsecond / (1000*1000)
        return d.year, d.month, d.day, secs


    def reload_uniforms(self):
        if not self.prog:
            return
        self.active_uniforms.clear()

        uniform_names = filter(self.is_uniform, self.prog)
        for name in uniform_names:
            if name not in self.supported_uniforms:
                print(f'WARNING! Uniform: "{name}" is not supported by this program')
                continue

            uniform = self.prog[name]
            if 'worldViewProjMatrix' == name:
                uniform.extra = set_np_array(uniform, self.get_mvp)
            elif 'lightDirection' == name:
                uniform.extra = set_np_array(uniform, self.get_light)
            elif 'camPos' == name:
                uniform.extra = set_np_array(uniform, self.get_cam_pos)
            elif 'diffTexture' == name:
                uniform.extra = set_single(uniform, 0)
            elif 'iTime' == name:
                uniform.extra = set_np_array(uniform, self.iTime)
            elif 'iResolution' == name:
                uniform.extra = set_tuple(uniform, self.iResolution)
            elif 'iMouse' == name:
                uniform.extra = set_tuple(uniform, self.iMouse)
            elif 'iDate' == name:
                uniform.extra = set_tuple(uniform, self.iDate)
            self.active_uniforms.append(uniform)

    supported_uniforms = (
        'iTime',
        'iResolution',
        'iMouse',
        'iDate',
    )


def set_single(uniform: moderngl.Uniform, data: Union[int, float]):
    def inner():
        uniform.value = data

    return inner


def set_tuple(uniform: moderngl.Uniform, getter: Callable[[], Tuple]):
    def inner():
        uniform.value = getter()

    return inner


def set_np_array(uniform, getter):
    def inner():
        uniform.write(getter().astype('f4').tobytes())

    return inner


if __name__ == '__main__':
    run_interface(ShaderToy)
