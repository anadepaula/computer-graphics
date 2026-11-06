"""
Visualizador de malhas 3D, versao 2: normais, iluminacao e
sombreamento.

Os modos 4 a 7 avaliam a mesma equacao de iluminacao; muda a
frequencia: por face (flat), por vertice (Gouraud) ou por
fragmento (Phong e cartoon).

MCCC007-23 - Computacao Grafica - UFABC

Executar: python main.py [modelo.off]
Mouse:    arrastar gira | roda aproxima e afasta
Modos:    1 profundidade | 2 normais | 3 normais iluminadas
          4 flat | 5 Gouraud | 6 Phong | 7 cartoon
Teclas:   N normal por face/vertice | A ponderacao por area
          B Blinn-Phong/Phong | M material | L luz pontual/direcional
          setas para cima e para baixo: expoente especular
          O abre arquivo | P projecao | W aramado | C descarte
          I inercia | Z zera | ESC sai
"""
import sys
from pathlib import Path

import glfw
import glm
import moderngl
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))   # modulos comuns

from camera import Camera            # noqa: E402
from dialogo import escolher_off     # noqa: E402
from malha import Malha              # noqa: E402
from material import MATERIAIS, Luz  # noqa: E402
from trackball import Trackball      # noqa: E402

AQUI = Path(__file__).parent
LADO = 800
FUNDO = (0.08, 0.09, 0.11)
ZOOM_MIN, ZOOM_MAX = 1.4, 12.0
PASSO_ZOOM = 0.25        # variacao da distancia por clique da roda
PASSO_ALFA = 1.3         # fator do expoente a cada seta
ALFA_MIN, ALFA_MAX = 1.0, 1024.0
BLINN_ALFA = 4.0         # Blinn-Phong pede um expoente ~4 vezes maior
NIVEIS_CARTOON = 4

# O moderngl nao tem nome para este estado do OpenGL.
GL_FRAMEBUFFER_SRGB = 0x8DB9

# nome, programa, malha facetada? (None: a tecla N decide)
MODOS = [
    ("profundidade", "profundidade", False),
    ("normais", "normais", None),
    ("normais iluminadas", "normais_luz", None),
    ("flat", "flat", True),
    ("Gouraud", "gouraud", False),
    ("Phong", "phong", False),
    ("cartoon", "phong", False),
]

# Programas que mostram dados como cor (distancia e normal): o valor
# vai para a tela sem codificacao. Os demais calculam luz linear,
# e o OpenGL a codifica em sRGB na escrita.
SEM_CODIFICACAO = ("profundidade", "normais")

# Atributos do VBO, na ordem em que estao intercalados.
CAMPOS = [('3f', 'vPosition'), ('3f', 'vNormal')]


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


def matriz_normal(modelo):
    """Inversa transposta do bloco 3x3 da matriz de modelo."""
    return glm.transpose(glm.inverse(glm.mat3(modelo)))


def carregar_programa(ctx, nome):
    return ctx.program(
        vertex_shader=(AQUI / "shaders" / f"{nome}.vert")
        .read_text(encoding="utf-8"),
        fragment_shader=(AQUI / "shaders" / f"{nome}.frag")
        .read_text(encoding="utf-8"))


def vao_de(ctx, prog, vbo, ebo=None):
    """VAO que liga so os atributos que o programa declara. No
    formato, '3x4' pula tres valores de 4 bytes."""
    formato, nomes = [], []
    for tamanho, nome in CAMPOS:
        if nome in prog:
            formato.append(tamanho)
            nomes.append(nome)
        else:
            formato.append(f"{tamanho[0]}x4")
    return ctx.vertex_array(prog, [(vbo, " ".join(formato), *nomes)],
                            index_buffer=ebo)


def enviar(prog, **uniformes):
    """Envia os uniformes que o programa declara e ignora os outros,
    como vao_de faz com os atributos."""
    for nome, valor in uniformes.items():
        if nome not in prog:
            continue
        if isinstance(valor, (glm.mat3, glm.mat4)):
            prog[nome].write(valor.to_bytes())    # por colunas
        else:
            prog[nome].value = valor


class Cena:
    """A malha atual, com um VAO por programa e por representacao
    (suave ou facetada)."""

    def __init__(self, ctx, programas):
        self.ctx, self.programas = ctx, programas
        self.malha = None
        self.recursos = []
        self.vaos = {}
        self.enquadramento = glm.mat4(1.0)

    def carregar(self, caminho, ponderar_por_area=True):
        try:
            malha = Malha(caminho, ponderar_por_area)
        except Exception as erro:
            print(f"FALHA ao ler {caminho}: {erro}", file=sys.stderr)
            return False

        self.liberar()
        self.malha = malha
        self.enquadramento = malha.matriz_enquadramento()

        dados, indices = malha.suave()
        vbo = self.ctx.buffer(dados.tobytes())
        ebo = self.ctx.buffer(indices.tobytes())
        vbo_face = self.ctx.buffer(malha.facetada().tobytes())

        for nome, prog in self.programas.items():
            self.vaos[(nome, False)] = vao_de(self.ctx, prog, vbo, ebo)
            self.vaos[(nome, True)] = vao_de(self.ctx, prog, vbo_face)
        self.recursos = list(self.vaos.values()) + [ebo, vbo, vbo_face]

        print(malha.resumo())
        return True

    def liberar(self):
        for r in self.recursos:
            r.release()
        self.recursos, self.vaos = [], {}

    def desenhar(self, programa, facetada):
        self.vaos[(programa, facetada)].render(moderngl.TRIANGLES)


def main():
    glfw.set_error_callback(erro_glfw)
    if not glfw.init():
        sys.exit("FALHA: glfw nao inicializou")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)  # macOS
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.SRGB_CAPABLE, True)

    janela = glfw.create_window(LADO, LADO, "Visualizador v2", None, None)
    if not janela:
        glfw.terminate()
        sys.exit("FALHA: nao foi possivel criar a janela")

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST)

    programas = {n: carregar_programa(ctx, n)
                 for n in ("profundidade", "normais", "normais_luz",
                           "flat", "gouraud", "phong")}
    cena = Cena(ctx, programas)
    camera = Camera(distancia=3.0)
    bola = Trackball()
    luz = Luz()
    estado = {"modo": 5, "por_vertice": True, "por_area": True,
              "blinn": False, "material": 0,
              "aramado": False, "descarte": False}

    inicial = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if inicial is None:
        candidatos = sorted((AQUI / "off").glob("*.off")) \
            or sorted((AQUI.parent / "off").glob("*.off"))
        inicial = candidatos[0] if candidatos else None
    if inicial is None or not cena.carregar(inicial):
        escolhido = escolher_off()
        if escolhido is None or not cena.carregar(escolhido):
            glfw.terminate()
            sys.exit("Nenhuma malha carregada.")

    def tecla(window, key, scancode, action, mods):
        if action not in (glfw.PRESS, glfw.REPEAT):
            return
        mat = MATERIAIS[estado["material"]]
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif glfw.KEY_1 <= key < glfw.KEY_1 + len(MODOS):
            estado["modo"] = key - glfw.KEY_1
        elif key == glfw.KEY_N:
            estado["por_vertice"] = not estado["por_vertice"]
        elif key == glfw.KEY_A:
            estado["por_area"] = not estado["por_area"]
            cena.carregar(cena.malha.caminho, estado["por_area"])
        elif key == glfw.KEY_B:
            estado["blinn"] = not estado["blinn"]
            if estado["blinn"]:
                mat.alfa *= BLINN_ALFA
            else:
                mat.alfa /= BLINN_ALFA
        elif key == glfw.KEY_M:
            estado["material"] = (estado["material"] + 1) % len(MATERIAIS)
        # Setas, e nao colchetes, que mudam de lugar no ABNT2.
        elif key == glfw.KEY_UP:
            mat.alfa = min(ALFA_MAX, mat.alfa * PASSO_ALFA)
        elif key == glfw.KEY_DOWN:
            mat.alfa = max(ALFA_MIN, mat.alfa / PASSO_ALFA)
        elif key == glfw.KEY_L:
            luz.alternar_tipo()
        elif key == glfw.KEY_O:
            caminho = escolher_off()
            if caminho and cena.carregar(caminho, estado["por_area"]):
                bola.zerar()
        elif key == glfw.KEY_P:
            camera.perspectiva = not camera.perspectiva
        elif key == glfw.KEY_W:
            estado["aramado"] = not estado["aramado"]
        elif key == glfw.KEY_C:
            estado["descarte"] = not estado["descarte"]
        elif key == glfw.KEY_I:
            bola.inercia = not bola.inercia
            bola.velocidade = 0.0
        elif key == glfw.KEY_Z:
            bola.zerar()

    def botao(window, button, action, mods):
        if button != glfw.MOUSE_BUTTON_LEFT:
            return
        x, y = glfw.get_cursor_pos(window)
        if action == glfw.PRESS:
            bola.pressionar(x, y)
        elif action == glfw.RELEASE:
            bola.soltar()

    def roda(window, dx, dy):
        camera.distancia = float(np.clip(
            camera.distancia - dy * PASSO_ZOOM, ZOOM_MIN, ZOOM_MAX))

    def soltou_arquivo(window, caminhos):
        for c in caminhos:
            if c.lower().endswith(".off") and cena.carregar(
                    c, estado["por_area"]):
                bola.zerar()
                return

    def redimensionou(window, largura, altura):
        largura, altura = max(1, largura), max(1, altura)
        ctx.viewport = (0, 0, largura, altura)
        camera.aspecto = largura / altura
        lj, aj = glfw.get_window_size(window)
        bola.redimensionar(max(1, lj), max(1, aj))

    glfw.set_key_callback(janela, tecla)
    glfw.set_mouse_button_callback(janela, botao)
    glfw.set_scroll_callback(janela, roda)
    glfw.set_drop_callback(janela, soltou_arquivo)
    glfw.set_framebuffer_size_callback(janela, redimensionou)
    redimensionou(janela, *glfw.get_framebuffer_size(janela))

    print("\n1 profundidade | 2 normais | 3 normais iluminadas")
    print("4 flat | 5 Gouraud | 6 Phong | 7 cartoon")
    print("N face/vertice | A peso por area | B Blinn-Phong")
    print("M material | setas expoente | L luz | ESC sai")

    instante_anterior = glfw.get_time()

    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        dt = agora - instante_anterior
        instante_anterior = agora

        if bola.arrastando:
            bola.mover(*glfw.get_cursor_pos(janela), dt)
        else:
            bola.atualizar(dt)

        nome_modo, programa, facetada = MODOS[estado["modo"]]
        if facetada is None:
            facetada = not estado["por_vertice"]
        prog = programas[programa]
        mat = MATERIAIS[estado["material"]]
        modelo = bola.matriz() * cena.enquadramento
        visao = camera.visao()

        # O fundo ja e uma cor de tela: limpa sem codificar.
        ctx.disable_direct(GL_FRAMEBUFFER_SRGB)
        ctx.clear(*FUNDO, depth=1.0)
        if programa not in SEM_CODIFICACAO:
            ctx.enable_direct(GL_FRAMEBUFFER_SRGB)

        if estado["descarte"]:
            ctx.enable(moderngl.CULL_FACE)
        else:
            ctx.disable(moderngl.CULL_FACE)
        ctx.wireframe = estado["aramado"]

        # A luz vai para o espaco da camera, o dos shaders.
        enviar(prog,
               u_modelo=modelo, u_visao=visao,
               u_projecao=camera.projecao(),
               u_normal=matriz_normal(modelo),
               u_near=camera.near, u_far=camera.far,
               u_luz=visao * luz.posicao,
               u_ia=luz.ia, u_id=luz.id, u_is=luz.is_,
               u_ka=mat.ka, u_kd=mat.kd, u_ks=mat.ks, u_alfa=mat.alfa,
               u_blinn=estado["blinn"],
               u_cartoon=(nome_modo == "cartoon"),
               u_niveis=NIVEIS_CARTOON)

        cena.desenhar(programa, facetada)

        glfw.swap_buffers(janela)
        glfw.poll_events()

        titulo = (f"{cena.malha.caminho.name} - "
                  f"[{estado['modo'] + 1}] {nome_modo}")
        if MODOS[estado["modo"]][2] is None:
            titulo += f" - normal por {'FACE' if facetada else 'VERTICE'}"
        if programa not in SEM_CODIFICACAO:
            titulo += (f" - {'Blinn-Phong' if estado['blinn'] else 'Phong'}"
                       f" - {mat.nome} alfa={mat.alfa:.0f} - luz "
                       f"{'pontual' if luz.posicao.w else 'direcional'}")
        glfw.set_window_title(janela, titulo)

    cena.liberar()
    for prog in programas.values():
        prog.release()
    glfw.terminate()


if __name__ == "__main__":
    main()
