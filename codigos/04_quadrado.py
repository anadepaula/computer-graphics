"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a janela
import sys
"""
from pathlib import Path

import glfw
import moderngl
import numpy as np
from codigos.utils.base_window import janela

SHADERS = Path(__file__).parent / "shaders"

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader=(SHADERS / "basico.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
)

vertices = np.array([
    -0.5, -0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,   # v0 vermelho
     0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,   # v1 verde
     0.5,  0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0,   # v2 azul
    -0.5,  0.5, 0.0, 1.0,   1.0, 1.0, 0.0, 1.0,   # v3 amarelo
], dtype='f4')

# Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
# o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
indices = np.array([0, 1, 2,  2, 3, 0], dtype='u4')

vbo = ctx.buffer(vertices.tobytes())
ebo = ctx.buffer(indices.tobytes())

vao = ctx.vertex_array(
    prog, [(vbo, '4f 4f', 'vPosition', 'vColors')], index_buffer=ebo
)

while not glfw.window_should_close(janela):
    if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(janela, True)

    ctx.clear(1.0, 1.0, 1.0, 1.0)
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(janela)
    glfw.poll_events()

vao.release()
ebo.release()
vbo.release()
prog.release()
glfw.terminate()
print("Execucao finalizada.")
