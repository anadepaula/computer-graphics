"""
Visualizador de malhas 3D, versao 1: camera, projecoes e trackball.

MCCC007-23 - Computacao Grafica - UFABC

Executar: python main.py [modelo.off]
Mouse:    arrastar gira | roda aproxima e afasta
Teclas:   O abre arquivo | P perspectiva/ortografica | W aramado
          C descarte de faces | I inercia | Z zera | ESC sai
Tambem:   arraste um .off para dentro da janela
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
from trackball import Trackball      # noqa: E402

AQUI = Path(__file__).parent
LADO = 800
FUNDO = (0.08, 0.09, 0.11)
ZOOM_MIN, ZOOM_MAX = 1.4, 12.0
PASSO_ZOOM = 0.25        # variacao da distancia por clique da roda


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


class Cena:
    """A malha atual e os objetos da GPU criados a partir dela."""

    def __init__(self, ctx, prog):
        self.ctx, self.prog = ctx, prog
        self.malha = None
        self.vbo = self.ebo = self.vao = None
        self.enquadramento = glm.mat4(1.0)

    def carregar(self, caminho):
        try:
            malha = Malha(caminho)
        except Exception as erro:
            print(f"FALHA ao ler {caminho}: {erro}", file=sys.stderr)
            return False

        self.liberar()
        self.malha = malha
        self.enquadramento = malha.matriz_enquadramento()
        self.vbo = self.ctx.buffer(malha.vertices.astype('f4').tobytes())
        self.ebo = self.ctx.buffer(malha.faces.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, '3f', 'vPosition')],
            index_buffer=self.ebo)
        print(malha.resumo())
        return True

    def liberar(self):
        for recurso in (self.vao, self.ebo, self.vbo):
            if recurso is not None:
                recurso.release()
        self.vao = self.ebo = self.vbo = None

    def desenhar(self):
        if self.vao is not None:
            self.vao.render(moderngl.TRIANGLES)


def main():
    glfw.set_error_callback(erro_glfw)
    if not glfw.init():
        sys.exit("FALHA: glfw nao inicializou")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)  # macOS
    glfw.window_hint(glfw.SAMPLES, 4)

    janela = glfw.create_window(LADO, LADO, "Visualizador v1", None, None)
    if not janela:
        glfw.terminate()
        sys.exit("FALHA: nao foi possivel criar a janela")

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST)

    prog = ctx.program(
        vertex_shader=(AQUI / "shaders" / "profundidade.vert")
        .read_text(encoding="utf-8"),
        fragment_shader=(AQUI / "shaders" / "profundidade.frag")
        .read_text(encoding="utf-8"))

    cena = Cena(ctx, prog)
    camera = Camera(distancia=3.0)
    bola = Trackball()
    estado = {"aramado": False, "descarte": False}

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
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_O:
            caminho = escolher_off()
            if caminho and cena.carregar(caminho):
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
        for caminho in caminhos:
            if caminho.lower().endswith(".off") and cena.carregar(caminho):
                bola.zerar()
                return

    def redimensionou(window, largura, altura):
        # O viewport e medido em pixels do framebuffer.
        largura, altura = max(1, largura), max(1, altura)
        ctx.viewport = (0, 0, largura, altura)
        camera.aspecto = largura / altura
        # O cursor vem em coordenadas da janela, que diferem dos pixels
        # em telas de alta densidade.
        lj, aj = glfw.get_window_size(window)
        bola.redimensionar(max(1, lj), max(1, aj))

    glfw.set_key_callback(janela, tecla)
    glfw.set_mouse_button_callback(janela, botao)
    glfw.set_scroll_callback(janela, roda)
    glfw.set_drop_callback(janela, soltou_arquivo)
    glfw.set_framebuffer_size_callback(janela, redimensionou)
    redimensionou(janela, *glfw.get_framebuffer_size(janela))

    print("\nO abre | P projecao | W aramado | C descarte | I inercia")
    print("Z zera | ESC sai | arraste um .off para a janela")

    instante_anterior = glfw.get_time()

    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        dt = agora - instante_anterior
        instante_anterior = agora

        if bola.arrastando:
            bola.mover(*glfw.get_cursor_pos(janela), dt)
        else:
            bola.atualizar(dt)

        ctx.clear(*FUNDO, depth=1.0)
        if estado["descarte"]:
            ctx.enable(moderngl.CULL_FACE)
        else:
            ctx.disable(moderngl.CULL_FACE)
        ctx.wireframe = estado["aramado"]

        # Primeiro o enquadramento, depois a rotacao do trackball.
        # to_bytes() devolve a matriz por colunas, como o GLSL espera.
        modelo = bola.matriz() * cena.enquadramento
        prog['u_modelo'].write(modelo.to_bytes())
        prog['u_visao'].write(camera.visao().to_bytes())
        prog['u_projecao'].write(camera.projecao().to_bytes())
        prog['u_near'].value = camera.near
        prog['u_far'].value = camera.far

        cena.desenhar()

        glfw.swap_buffers(janela)
        glfw.poll_events()

        glfw.set_window_title(
            janela,
            f"{cena.malha.caminho.name} - "
            f"{'perspectiva' if camera.perspectiva else 'ortografica'}"
            f" - d={camera.distancia:.2f} "
            f"near={camera.near:.2f} far={camera.far:.2f}"
            f"{' - aramado' if estado['aramado'] else ''}"
            f"{' - descarte' if estado['descarte'] else ''}")

    cena.liberar()
    prog.release()
    glfw.terminate()


if __name__ == "__main__":
    main()
