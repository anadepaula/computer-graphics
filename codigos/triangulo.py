import glfw
import moderngl
from utils import (
    basico_fragment_shader,
    basico_vertex_shader,
    create_byte_array,
    get_window,
    setup,
    teardown,
)
from utils.basics import BLUE, FLOAT_32_FOR_VAO, GREEN, POSITIONS_SQUARE, RED, VAOType


def configure_colors_and_positions(prog, ctx):
    positions = create_byte_array([
        ( 0.0,  0.5, 0.0, 1.0),
        (-0.5, -0.5, 0.0, 1.0),
        ( 0.5, -0.5, 0.0, 1.0),
    ], VAOType.POSITIONS)
    colors = create_byte_array([
        RED,
        GREEN,
        BLUE,
    ], VAOType.COLORS)

    vbo_colors = ctx.buffer(colors)
    vbo_positions = ctx.buffer(positions)
    vao = ctx.vertex_array(
        prog, 
        [
            (vbo_positions, FLOAT_32_FOR_VAO, "vPosition"),
            (vbo_colors, FLOAT_32_FOR_VAO, "vColors"),
        ],
    )
    return vao, vbo_positions, vbo_colors

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
    window = get_window(window_width, window_height, "triangulo gradiente")
    ctx, prog = setup(
        window,
        basico_vertex_shader,
        basico_fragment_shader,
    )
    vao, vbo_positions, vbo_colors = configure_colors_and_positions(prog, ctx)
    render_image(window, ctx, vao)
    teardown(glfw, [vao, vbo_positions, vbo_colors, prog])

if __name__ == "__main__":
    main()
