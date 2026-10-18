import glfw
import moderngl
import numpy as np
from utils import (
    basico_fragment_shader,
    basico_vertex_shader,
    get_window,
    setup,
    teardown,
)

window = get_window(600, 600, "triangulo gradiente")
ctx, prog = setup(
    window,
    basico_vertex_shader,
    basico_fragment_shader,
)

positions = np.array([
    ( 0.0, 0.5,0.0,1.0,),
    (-0.5,-0.5,0.0,1.0,),
    ( 0.5,-0.5,0.0,1.0,),
], dtype='f4').tobytes()
colors = np.array([
    (1.0, 0.0, 0.0, 1.0),  # v0 topo, vermelho
    (0.0, 1.0, 0.0, 1.0),  # v1 esquerda, verde
    (0.0, 0.0, 1.0, 1.0),  # v2 direita, azul
], dtype='f4').tobytes()

vbo_colors = ctx.buffer(colors)
vbo_positions = ctx.buffer(positions)
vao = ctx.vertex_array(
    prog, 
    [
        (vbo_positions, "4f", "vPosition"),
        (vbo_colors, "4f", "vColors"),
    ],
)

while not glfw.window_should_close(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    ctx.clear(1.0, 1.0, 1.0, 1.0)
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(window)
    glfw.poll_events()

teardown(glfw, [vao, vbo_positions, vbo_colors, prog])
