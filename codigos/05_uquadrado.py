"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a janela
"""
from pathlib import Path

import glfw
import moderngl
import numpy as np
from utils import (
    FLOAT_32_FOR_VAO,
    VARIABLE_SHADERS_POSITION,
    VAOType,
    basico_fragment_shader,
    create_byte_array,
    create_unsigned_int_array,
    get_window,
    uniform_vertex_shader,
)

SHADERS = Path(__file__).parent / "shaders"

VERTICES = create_byte_array(
    [
        (-0.5, -0.5, 0.0, 1.0),
        ( 0.5, -0.5, 0.0, 1.0),
        ( 0.5,  0.5, 0.0, 1.0),
        (-0.5,  0.5, 0.0, 1.0),
    ], 
    VAOType.POSITIONS
)


# Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
# o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
DIAGONAL_02 = create_unsigned_int_array([0, 1, 2,  2, 3, 0])
DIAGONAL_13 = create_unsigned_int_array([0, 1, 3,  1, 2, 3])
DIAGONAL_ALTERNATIVA = False

MODO_ESCURO = False
VERMELHO = (1.0, 0.0, 0.0, 1.0)
AMARELO  = (1.0, 1.0, 0.0, 1.0)
BRANCO   = (1.0, 1.0, 1.0, 1.0)
PRETO    = (0.0, 0.0, 0.0, 0.0)

ESCALA_PASSO = 0.1
ESCALA_MINIMO = 0.1
ESCALA_MAXIMO = 1

VERTEX_SHADER = uniform_vertex_shader
FRAGMENT_SHADER = basico_fragment_shader
SHADERS = Path(__file__).parent/"shaders"

def load_shaders_and_create_objects():
    print(f"{VERTEX_SHADER=}")
    print(f"{FRAGMENT_SHADER=}")
    glfw.swap_interval(1)
    ctx = moderngl.create_context()
    print(f"{ctx=}")
    vs = (SHADERS/"uquad.vert").read_text(encoding="utf-8")
    print(f"{vs=}")
    fs=(SHADERS/"basico.frag").read_text(encoding="utf-8")
    print(f"{fs=}")
    
    prog = ctx.program(
        # vertex_shader=VERTEX_SHADER,
        # fragment_shader=FRAGMENT_SHADER,
        vertex_shader=vs,
        fragment_shader=fs,
    )
    print(f"{prog=}")

    vbo = ctx.buffer(VERTICES)
    print(f"{vbo=}")
    
    ebo = ctx.buffer(DIAGONAL_02)
    print(f"{ebo=}")

    vao = ctx.vertex_array(
        prog, 
        [(vbo, FLOAT_32_FOR_VAO, VARIABLE_SHADERS_POSITION)], 
        index_buffer=ebo,
    )
    print(f"{vao=}")
    
    glfw.set_key_callback(janela, tecla)
    
    return ctx, prog, vbo, ebo, vao

def tecla(window, key, scancode, action, mode):
    global DIAGONAL_ALTERNATIVA, MODO_ESCURO, ESCALA
    
    if action == glfw.RELEASE:
        return
    
    elif key == glfw.KEY_UP:
        ESCALA = min(ESCALA + ESCALA_PASSO, ESCALA_MAXIMO)
    elif key == glfw.KEY_DOWN:
        ESCALA = max(ESCALA - ESCALA_PASSO, ESCALA_MINIMO)
        
    if action != glfw.RELEASE:
        return

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_D:
        MODO_ESCURO = not MODO_ESCURO
    elif key == glfw.KEY_SPACE:
        DIAGONAL_ALTERNATIVA = not DIAGONAL_ALTERNATIVA
        novos = DIAGONAL_13 if DIAGONAL_ALTERNATIVA else DIAGONAL_02
        ebo.write(novos.tobytes())

def refresh_window(janela, escala):
    while not glfw.window_should_close(janela):
        
        ctx.clear(*(PRETO if MODO_ESCURO else BRANCO))
        
        prog['u_escala'].value = escala
        
        prog['u_cor'].value = VERMELHO
        vao.render(moderngl.TRIANGLES, vertices=3, start=0)
        
        prog['u_cor'].value = VERMELHO
        vao.render(moderngl.TRIANGLES, vertices=3, start=3)
        
        glfw.swap_buffers(janela)
        glfw.poll_events()


def release_memory_and_terminate():
    for recurso in (vao, ebo, vbo, prog):
        recurso.release()

    glfw.terminate()
    print("Execucao finalizada.")

if __name__== "__main__":
    janela = get_window(600, 600, "u_quadrado")

    ctx, prog, vbo, ebo, vao = load_shaders_and_create_objects()
    refresh_window()
    release_memory_and_terminate()
    