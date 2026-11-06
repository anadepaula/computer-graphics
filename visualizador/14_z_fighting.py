"""
Z-fighting.

MCCC007-23 - Computacao Grafica - UFABC

Executar: python 14_z_fighting.py
Teclas:   CIMA e BAIXO dobram e dividem n
          DIREITA e ESQUERDA dobram e dividem f
          ESPACO pausa | ESC sai
"""
import math
import sys 
from pathlib import Path

import glfw
import glm
import moderngl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SHADERS = Path(__file__).parent / "shaders"

# Janela: vista da camera (quadrada) a esquerda; a direita, um
# painel desenhado com o Pillow, com a vista lateral e o grafico.
LADO = 600
LARGURA_PAINEL = 600
ALTURA_LATERAL = 200
BITS_PROFUNDIDADE = 24
# A GPU calcula z_ndc em float32, que em [1/2, 1) tem o mesmo
# espacamento do buffer: o arredondamento custa cerca de um passo,
# e os empates comecam quando a folga cai abaixo de dois passos.
PASSOS_EMPATE = 2
FATIAS = 16

# Nave: triangulo no plano xy, com o bico em +y.
TAMANHO_NAVE = 5.0
NAVE = TAMANHO_NAVE * np.array([
     0.0,  1.0, 0.0,
    -0.8, -0.8, 0.0,
     0.8, -0.8, 0.0,
], dtype='f4')
INCLINACAO = glm.radians(50.0)   # o bico aponta para o fundo
# Distancia da azul atras. Nao pode ser muito menor: como as naves
# sao inclinadas, o arredondamento dos vertices para a grade de
# subpixel ja desloca a profundidade de cada uma em ~1e-4.
FOLGA = 2e-3
AFASTAMENTO_X = 0.6 * TAMANHO_NAVE   # e ao lado da vermelha

FOV = glm.radians(45.0)
# Chao: grade no plano y = -ALTURA_CHAO, com |x| ate MEIA_LARGURA
# e uma linha a cada PASSO_CHAO.
ALTURA_CHAO = 4.0
MEIA_LARGURA = 40.0
PASSO_CHAO = 10.0

D_MIN, D_MAX = 20.0, 95.0
SEGUNDOS_POR_TRECHO = 8.0
VELOCIDADE = (D_MAX - D_MIN) / SEGUNDOS_POR_TRECHO

N_INICIAL, N_MIN, N_MAX = 1 / 16, 0.01, 32.0
F_INICIAL, F_MIN, F_MAX = 100.0, 100.0, 1600.0
FATOR = 2.0                      # passo das teclas de n e f

# Eixo D comum aos dois paineis da direita, em pixels.
D_VISTA = 110.0
X0, X1 = 60, LARGURA_PAINEL - 30
LAT_TOPO, LAT_BASE = 60, 130
GRAF_TOPO, GRAF_BASE = ALTURA_LATERAL + 50, LADO - 50
DIVISAO_D = 10.0                 # marcas do eixo D
TAMANHO_FONTE = 14
ESPACO_TEXTO = 18                # entre linhas de texto, em px
RAIO_MARCA = 5                   # naves nos paineis, em px

VERMELHO = (230, 51, 51)
AZUL = (64, 115, 255)
FUNDO = (10, 13, 23)
PAPEL = (250, 250, 250)
TINTA = (40, 40, 40)
CINZA = (180, 180, 180)
VERDE = (0, 105, 62)
VOLUME = (222, 236, 228)
ZONA = (250, 210, 210)
CHAO = (70, 80, 100)


def cor_gl(cor):
    return tuple(c / 255.0 for c in cor) + (1.0,)


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


glfw.set_error_callback(erro_glfw)
if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)  # macOS
glfw.window_hint(glfw.RESIZABLE, False)
glfw.window_hint(glfw.DEPTH_BITS, BITS_PROFUNDIDADE)

janela = glfw.create_window(LADO + LARGURA_PAINEL, LADO,
                            "Z-fighting", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: nao foi possivel criar a janela")

glfw.make_context_current(janela)
glfw.swap_interval(1)
ctx = moderngl.create_context()

# Em telas de alta densidade, o framebuffer e maior que a janela.
ESCALA = glfw.get_framebuffer_size(janela)[1] / LADO

# Naves, com z_fighting.vert e basico.frag.
prog_naves = ctx.program(
    vertex_shader=(SHADERS / "z_fighting.vert")
    .read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag")
    .read_text(encoding="utf-8"))
vbo_nave = ctx.buffer(NAVE.tobytes())
vao_nave = ctx.vertex_array(prog_naves,
                            [(vbo_nave, '3f', 'vPosition')])


def linhas_do_chao():
    """Linhas ao longo de z, de 0 a -F_MAX, e travessas a
    cada PASSO_CHAO, ate D_MAX."""
    y, m, p = -ALTURA_CHAO, MEIA_LARGURA, PASSO_CHAO
    v = []
    for x in np.arange(-m, m + p, p):
        v += [x, y, 0.0, x, y, -F_MAX]
    for z in np.arange(p, D_MAX + p, p):
        v += [-m, y, -z, m, y, -z]
    return np.array(v, dtype='f4')


vbo_chao = ctx.buffer(linhas_do_chao().tobytes())
vao_chao = ctx.vertex_array(prog_naves,
                            [(vbo_chao, '3f', 'vPosition')])

# Painel: uma imagem em um quadrado, com os shaders de
# 12_textura_2d.py. A linha de cima da imagem do Pillow vai para
# t = 0, por isso o t do quadrado cresce para baixo.
prog_painel = ctx.program(
    vertex_shader=(SHADERS / "textura2d.vert")
    .read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "textura2d.frag")
    .read_text(encoding="utf-8"))
QUADRADO = np.array([
    # x,    y,   cor,           s,   t
    -1.0, -1.0,  1.0, 1.0, 1.0,  0.0, 1.0,
     1.0, -1.0,  1.0, 1.0, 1.0,  1.0, 1.0,
    -1.0,  1.0,  1.0, 1.0, 1.0,  0.0, 0.0,
     1.0,  1.0,  1.0, 1.0, 1.0,  1.0, 0.0,
], dtype='f4')
vbo_painel = ctx.buffer(QUADRADO.tobytes())
vao_painel = ctx.vertex_array(
    prog_painel,
    [(vbo_painel, '2f 3f 2f', 'vPosition', 'vCor', 'vTexCoord')])
textura = ctx.texture((LARGURA_PAINEL, LADO), 3)
prog_painel['u_imagem'].value = 0
prog_painel['u_efeito'].value = 0       # so a imagem


def carregar_fonte():
    try:
        return ImageFont.load_default(size=TAMANHO_FONTE)
    except TypeError:                   # Pillow anterior a 10.1
        return ImageFont.load_default()


FONTE = carregar_fonte()

d, sentido = D_MIN, 1.0
n, f = N_INICIAL, F_INICIAL
pausado = False


def tecla(window, key, scancode, action, mods):
    global n, f, pausado
    if action == glfw.RELEASE:
        return
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_UP:
        n = min(n * FATOR, N_MAX)
    elif key == glfw.KEY_DOWN:
        n = max(n / FATOR, N_MIN)
    elif key == glfw.KEY_RIGHT:
        f = min(f * FATOR, F_MAX)
    elif key == glfw.KEY_LEFT:
        f = max(f / FATOR, F_MIN)
    elif key == glfw.KEY_SPACE and action == glfw.PRESS:
        pausado = not pausado


glfw.set_key_callback(janela, tecla)


# ------------------------------------------------- as contas

def profundidade(d, n, f):
    """z_w da distancia d."""
    return f * (d - n) / ((f - n) * d)


def distancia(zw, n, f):
    """Distancia cuja profundidade e zw (inversa da anterior)."""
    return f * n / (f - zw * (f - n))


def passo(d, n, f):
    """Menor diferenca de distancia que o buffer separa em d."""
    return d * d * (f - n) / (2 ** BITS_PROFUNDIDADE * f * n)


def inicio_z_fighting(n, f):
    """Distancia em que a FOLGA fica menor que PASSOS_EMPATE
    passos."""
    return math.sqrt(2 ** BITS_PROFUNDIDADE * FOLGA * f * n
                     / (PASSOS_EMPATE * (f - n)))


# ------------------------------------------ vista da camera

def desenhar_nave(x, z, cor):
    modelo = glm.translate(glm.vec3(x, 0.0, z))
    modelo = glm.rotate(modelo, -INCLINACAO, glm.vec3(1, 0, 0))
    prog_naves['u_modelo'].write(modelo.to_bytes())
    prog_naves['u_cor'].value = cor_gl(cor)
    vao_nave.render(moderngl.TRIANGLES)


def desenhar_camera():
    projecao = glm.perspective(FOV, 1.0, n, f)
    prog_naves['u_projecao'].write(projecao.to_bytes())

    # Camera na origem, olhando para -z: visao = identidade.
    ctx.enable(moderngl.DEPTH_TEST)
    prog_naves['u_modelo'].write(glm.mat4(1.0).to_bytes())
    prog_naves['u_cor'].value = cor_gl(CHAO)
    vao_chao.render(moderngl.LINES)

    # A azul vem primeiro. Num empate, o teste '<' rejeita a
    # vermelha, e a azul, que esta atras, aparece na frente.
    desenhar_nave(AFASTAMENTO_X, -(d + FOLGA), AZUL)
    desenhar_nave(0.0, -d, VERMELHO)
    ctx.disable(moderngl.DEPTH_TEST)


# -------------------------------------------------- painel

def x_de(dist):
    """Coluna do painel que corresponde a distancia dist."""
    return X0 + (X1 - X0) * min(dist, D_VISTA) / D_VISTA


def desenhar_lateral(g):
    meio = (LAT_TOPO + LAT_BASE) / 2
    fim = x_de(f)
    inicio = x_de(inicio_z_fighting(n, f))

    g.text((X0, ESPACO_TEXTO),
           "Vista lateral: volume de n a f "
           "(verde: metade dos valores de z_w)",
           fill=TINTA, font=FONTE)
    g.rectangle((x_de(n), LAT_TOPO, fim, LAT_BASE), fill=VOLUME)
    if inicio < fim:
        g.rectangle((inicio, LAT_TOPO, fim, LAT_BASE), fill=ZONA)
    for k in range(1, FATIAS):
        x = x_de(distancia(k / FATIAS, n, f))
        if x < fim:
            metade = 2 * k == FATIAS
            g.line((x, LAT_TOPO, x, LAT_BASE),
                   fill=VERDE if metade else CINZA,
                   width=2 if metade else 1)

    # Bordas do volume; a de f so aparece se couber no painel.
    g.line((x_de(n), LAT_TOPO, fim, LAT_TOPO), fill=TINTA)
    g.line((x_de(n), LAT_BASE, fim, LAT_BASE), fill=TINTA)
    g.line((x_de(n), LAT_TOPO, x_de(n), LAT_BASE), fill=TINTA)
    acima = LAT_TOPO - RAIO_MARCA
    g.text((x_de(n), acima), "n", fill=TINTA, font=FONTE,
           anchor="ms")
    if f <= D_VISTA:
        g.line((fim, LAT_TOPO, fim, LAT_BASE), fill=TINTA)
        g.text((fim, acima), "f", fill=TINTA, font=FONTE,
               anchor="ms")
    else:
        g.text((fim, acima), f"f = {f:g} ->", fill=TINTA,
               font=FONTE, anchor="rs")

    # Camera: um triangulo olhando para +D.
    lado = 2 * RAIO_MARCA
    g.polygon([(X0 - lado, meio - RAIO_MARCA),
               (X0 - lado, meio + RAIO_MARCA), (X0, meio)],
              fill=TINTA)
    g.text((X0 - lado, LAT_BASE + 2), "camera", fill=TINTA,
           font=FONTE)

    xn = x_de(d)
    g.polygon([(xn - RAIO_MARCA, meio - RAIO_MARCA),
               (xn - RAIO_MARCA, meio + RAIO_MARCA),
               (xn + RAIO_MARCA, meio)], fill=VERMELHO)


def desenhar_grafico(g):
    def y_de(zw):
        return GRAF_BASE - (GRAF_BASE - GRAF_TOPO) * zw

    fim = x_de(f)
    inicio = x_de(inicio_z_fighting(n, f))
    g.text((X0, ALTURA_LATERAL + ESPACO_TEXTO),
           "z_w = f (D - n) / ((f - n) D)", fill=TINTA,
           font=FONTE)
    if inicio < fim:
        g.rectangle((inicio, GRAF_TOPO, fim, GRAF_BASE),
                    fill=ZONA)

    # As mesmas fatias da vista lateral, agora no eixo z_w.
    for k in range(1, FATIAS):
        zw = k / FATIAS
        x = x_de(distancia(zw, n, f))
        metade = 2 * k == FATIAS
        g.line((X0, y_de(zw), x, y_de(zw)),
               fill=VERDE if metade else CINZA,
               width=2 if metade else 1)

    pontos = [(x_de(n), y_de(0.0))]
    for x in range(math.ceil(x_de(n)), math.floor(fim) + 1):
        dist = (x - X0) * D_VISTA / (X1 - X0)
        pontos.append((x, y_de(profundidade(dist, n, f))))
    g.line(pontos, fill=TINTA, width=2)

    # Eixos e marcas.
    g.line((X0, GRAF_BASE, X1, GRAF_BASE), fill=TINTA)
    g.line((X0, GRAF_TOPO, X0, GRAF_BASE), fill=TINTA)
    for i in range(int(D_VISTA / DIVISAO_D) + 1):
        x = x_de(i * DIVISAO_D)
        g.line((x, GRAF_BASE, x, GRAF_BASE + RAIO_MARCA),
               fill=TINTA)
        g.text((x, GRAF_BASE + ESPACO_TEXTO),
               f"{i * DIVISAO_D:g}", fill=TINTA, font=FONTE,
               anchor="ms")
    for zw in (0.0, 0.5, 1.0):
        g.text((X0 - RAIO_MARCA, y_de(zw)), f"{zw:g}",
               fill=TINTA, font=FONTE, anchor="rm")
    g.text((X1, GRAF_BASE + 2 * ESPACO_TEXTO), "D",
           fill=TINTA, font=FONTE, anchor="rs")

    if n <= d:
        x, y = x_de(d), y_de(profundidade(d, n, f))
        g.ellipse((x - RAIO_MARCA, y - RAIO_MARCA,
                   x + RAIO_MARCA, y + RAIO_MARCA), fill=VERMELHO)
        sobre_d = f"passo em D = {passo(d, n, f):.1e}"
    else:
        sobre_d = "naves antes de n: recortadas"
    linhas = [f"D = {d:.1f}   n = {n:g}   f = {f:g}", sobre_d,
              f"folga = {FOLGA:.1e}"]
    for i, linha in enumerate(linhas):
        g.text((X1, GRAF_BASE - (len(linhas) - i) * ESPACO_TEXTO),
               linha, fill=TINTA, font=FONTE, anchor="rs")


def desenhar_painel():
    imagem = Image.new("RGB", (LARGURA_PAINEL, LADO), PAPEL)
    g = ImageDraw.Draw(imagem)
    desenhar_lateral(g)
    desenhar_grafico(g)
    textura.write(imagem.tobytes())
    textura.use(0)
    vao_painel.render(moderngl.TRIANGLE_STRIP)


# ------------------------------------------- laco principal

def viewport(x, y, largura, altura):
    ctx.viewport = tuple(int(v * ESCALA)
                         for v in (x, y, largura, altura))


anterior = glfw.get_time()
while not glfw.window_should_close(janela):
    agora = glfw.get_time()
    dt, anterior = agora - anterior, agora

    if not pausado:
        d += sentido * VELOCIDADE * dt
        if d > D_MAX:
            d, sentido = D_MAX, -1.0
        elif d < D_MIN:
            d, sentido = D_MIN, 1.0

    ctx.clear(*cor_gl(FUNDO), depth=1.0)
    viewport(0, 0, LADO, LADO)
    desenhar_camera()
    viewport(LADO, 0, LARGURA_PAINEL, LADO)
    desenhar_painel()

    glfw.swap_buffers(janela)
    glfw.poll_events()

for recurso in (vao_nave, vbo_nave, vao_chao, vbo_chao,
                prog_naves, vao_painel, vbo_painel, prog_painel,
                textura):
    recurso.release()
glfw.terminate()
