"""
Primeiro triangulo: VBO, VAO e o par de shaders.
Único programa do curso com o GLSL embutido em string.
A partir do 03, os shaders passam a ser gravados em arquivos próprios.

MCCC007-23 - Computação Gráfica - UFABC
Prof. João Paulo Gois

Executar: python 02_triangulo.py      Sair: ESC ou fechar a janela
"""

import sys

import glfw
import moderngl
import numpy as np

from pathlib import Path


SHADERS = Path(__file__).parent / "shaders"


def erro_glfw(codigo, descricao):
    """Substitui o aviso padrão do pyGLFW: imprime código
    e descrição de qualquer erro do GLFW em stderr"""
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


glfw.set_error_callback(erro_glfw)

if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)


janela = glfw.create_window(800, 600, "Olá triângulo", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: não foi possível criar a janela")

glfw.make_context_current(janela)
ctx = moderngl.create_context()

# -------------- lado da GPU
# O driver compila   e liga os dois shaders agora, em tempo de execução.
prog = ctx.program(
    vertex_shader=(SHADERS / "basico.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
)

# ------------------- lado da CPU


positions = np.array([
    ( 0.0, 0.5,0.0,1.0,),
    (-0.5,-0.5,0.0,1.0,),
    ( 0.5,-0.5,0.0,1.0,),
])
colors = np.array([
    (1.0, 0.0, 0.0, 1.0),  # v0 topo, vermelho
    (0.0, 1.0, 0.0, 1.0),  # v1 esquerda, verde
    (0.0, 0.0, 1.0, 1.0),  # v2 direita, azul
])
# Dados intercalados: posição (x,y,z,w) e cor (r,g,b,a) de cada vértice,
# vizinhos na memória. 'f4' é float de 32 bits.
# Sem dtype, o numpy usa float64 e a GPU leria lixo.

# O VBO é memória bruta na VRAM.
# VAO diz como lê-la. '4f 4f' significa quatro floats
# para vPosition e quatro para vColors, nessa ordem.
vbo_colors = ctx.buffer(colors.tobytes())
vbo_positions = ctx.buffer(positions.tobytes())
vao_colors = ctx.vertex_array(prog, [(vbo_colors, "4f", "vPosition")])
vao_positions = ctx.vertex_array(prog, [(vbo_positions, "4f", "vColors")])

while not glfw.window_should_close(janela):
    if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(janela, True)

    ctx.clear(1.0, 1.0, 1.0, 1.0)
    vao_colors.render(moderngl.TRIANGLES)  # testar as alternativas
    vao_positions.render(moderngl.TRIANGLES)  # testar as alternativas
    glfw.swap_buffers(janela)
    glfw.poll_events()

vao_positions.release()
vao_colors.release()
vbo_positions.release()
vbo_colors.release()
prog.release()
glfw.terminate()
print("Execucao finalizada.")
