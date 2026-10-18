"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a janela
"""
from pathlib import Path

import glfw
import moderngl
import numpy as np
from utils.base_window import get_window

janela = get_window(600, 600, "quadradooooo")

SHADERS = Path(__file__).parent / "shaders"

VERTICES = np.array([
    -0.5, -0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,   # v0 vermelho
     0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,   # v1 verde
     0.5,  0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0,   # v2 azul
    -0.5,  0.5, 0.0, 1.0,   1.0, 1.0, 0.0, 1.0,   # v3 amarelo
], dtype='f4')

# Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
# o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
DIAGONAL_02 = np.array([0, 1, 2,  2, 3, 0], dtype='u4')
DIAGONAL_13 = np.array([0, 1, 3,  1, 2, 3], dtype='u4')
BRANCO = (1.0, 1.0, 1.0, 1.0, )
PRETO = (0.0, 0.0, 0.0, 0.0, )

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader=(SHADERS / "basico.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
)

vbo = ctx.buffer(VERTICES.tobytes())
ebo = ctx.buffer(DIAGONAL_02.tobytes())

vao = ctx.vertex_array(
    prog, [(vbo, '4f 4f', 'vPosition', 'vColors')], index_buffer=ebo
)

DIAGONAL_ALTERNATIVA = False
MODO_ESCURO = False

def tecla(window, key, scancode, action, mode):
    global DIAGONAL_ALTERNATIVA, MODO_ESCURO
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_D:
        MODO_ESCURO = not MODO_ESCURO
    elif key == glfw.KEY_SPACE:
        DIAGONAL_ALTERNATIVA = not DIAGONAL_ALTERNATIVA
        novos = DIAGONAL_13 if DIAGONAL_ALTERNATIVA else DIAGONAL_02
        ebo.write(novos.tobytes())


while not glfw.window_should_close(janela):
    glfw.set_key_callback(janela, tecla)
    ctx.clear(*(PRETO if MODO_ESCURO else BRANCO))
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(janela)
    glfw.poll_events()


for recurso in (vao, ebo, vbo, prog):
    recurso.release()

glfw.terminate()
print("Execucao finalizada.")
