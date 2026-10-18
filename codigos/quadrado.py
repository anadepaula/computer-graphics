"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a window
import sys
"""
from pathlib import Path

import glfw
import moderngl
import numpy as np
from utils import (
    basico_fragment_shader,
    basico_vertex_shader,
    create_colors_and_positions_byte_array,
    create_unsigned_int_array,
    get_window,
    setup,
    teardown,
)
from utils.basics import (
    FLOAT_32_FOR_VAO,
    POSITIONS_SQUARE,
    VARIABLE_SHADERS_COLORS,
    VARIABLE_SHADERS_POSITION,
)


def configure_colors_and_positions(prog, ctx):
    vertices = create_colors_and_positions_byte_array([
        -0.5, -0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,   # v0 vermelho
         0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,   # v1 verde
         0.5,  0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0,   # v2 azul
        -0.5,  0.5, 0.0, 1.0,   1.0, 1.0, 0.0, 1.0,   # v3 amarelo
    ])

    # Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
    # o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
    indices = create_unsigned_int_array([0, 1, 2,  2, 3, 0])

    vbo = ctx.buffer(vertices)
    ebo = ctx.buffer(indices)

    vao = ctx.vertex_array(
        prog, [(vbo, f'{FLOAT_32_FOR_VAO} {FLOAT_32_FOR_VAO}', VARIABLE_SHADERS_POSITION, VARIABLE_SHADERS_COLORS)], index_buffer=ebo
    )
    return vao, vbo, ebo
    

def render_image(window, ctx, vao):
    while not glfw.window_should_close(window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        ctx.clear(*POSITIONS_SQUARE)
        vao.render(moderngl.TRIANGLES)
        glfw.swap_buffers(window)
        glfw.poll_events()


def main(
    window_width=600,
    window_height=600,
):
    window = get_window(window_width, window_height, "quadrado com EBO")
    ctx, prog = setup(
        window,
        basico_vertex_shader,
        basico_fragment_shader,
    )
    vao, vbo, ebo = configure_colors_and_positions(prog, ctx)
    render_image(window, ctx, vao)
    teardown(glfw, [vao, vbo, ebo, prog])

if __name__ == "__main__":
    main()
