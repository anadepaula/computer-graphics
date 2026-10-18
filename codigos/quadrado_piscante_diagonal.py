"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a janela
"""
import glfw
import moderngl
from utils import (
    basico_fragment_shader,
    basico_vertex_shader,
    create_colors_and_positions_byte_array,
    create_unsigned_int_array,
    get_window,
    teardown,
)
from utils.basics import (
    BRANCO,
    FLOAT_32_FOR_VAO,
    POSITIONS_SQUARE,
    PRETO,
    VARIABLE_SHADERS_COLORS,
    VARIABLE_SHADERS_POSITION,
)

VERTICES = create_colors_and_positions_byte_array([
    -0.5, -0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,   # v0 vermelho
     0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,   # v1 verde
     0.5,  0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0,   # v2 azul
    -0.5,  0.5, 0.0, 1.0,   1.0, 1.0, 0.0, 1.0,   # v3 amarelo
])

# Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
# o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
DIAGONAL_02 = create_unsigned_int_array([0, 1, 2,  2, 3, 0])
DIAGONAL_13 = create_unsigned_int_array([0, 1, 3,  1, 2, 3])
 
DIAGONAL_ALTERNATIVA = False
MODO_ESCURO = False

def render_image(window, ctx, vao, callback_function):
    glfw.set_key_callback(window, callback_function)
    while not glfw.window_should_close(window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        ctx.clear(*POSITIONS_SQUARE)
        ctx.clear(*(PRETO if MODO_ESCURO else BRANCO))
        vao.render(moderngl.TRIANGLES)
        glfw.swap_buffers(window)
        glfw.poll_events()

def main(
    window_width=600,
    window_height=600,
):

    def tecla(janela, key, scancode, action, mode):
        global DIAGONAL_ALTERNATIVA, MODO_ESCURO
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(janela, True)
        elif key == glfw.KEY_D:
            MODO_ESCURO = not MODO_ESCURO
        elif key == glfw.KEY_SPACE:
            DIAGONAL_ALTERNATIVA = not DIAGONAL_ALTERNATIVA
            novos = DIAGONAL_13 if DIAGONAL_ALTERNATIVA else DIAGONAL_02
            
            ebo.write(novos)

        glfw.swap_buffers(janela)
        glfw.poll_events()
    

    window = get_window(window_width, window_height, "quadrado com EBO")
    ctx = moderngl.create_context()
    prog = ctx.program(
        vertex_shader=basico_vertex_shader,
        fragment_shader=basico_fragment_shader,
    )

    vbo = ctx.buffer(VERTICES)
    ebo = ctx.buffer(DIAGONAL_02)

    vao = ctx.vertex_array(
        prog, 
        [
            (
                vbo,
                f'{FLOAT_32_FOR_VAO} {FLOAT_32_FOR_VAO}',
                VARIABLE_SHADERS_POSITION,
                VARIABLE_SHADERS_COLORS,
            ),
        ],
        index_buffer=ebo,
    )

    render_image(window, ctx, vao, tecla)
    teardown(glfw, (vao, ebo, vbo, prog))


if __name__ == "__main__":
    main()
