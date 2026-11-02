import sys

import glfw
import moderngl


class BaseImage():
    def __init__(
        self,
        window_width,
        window_height,
        vertex_shader,
        fragment_shader,
        window_title,
    ):
        self.window_width = window_width
        self.window_height = window_height
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.window_title = window_title
        self._closed = False
        self.ctx, self.prog, self.window = self.setup()
        self.vbo, self.ebo, self.vao = None, None, None
        self.vbo, self.ebo, self.vao = self.define_colors_and_positions()
        self.resources = (self.vao, self.vbo, self.ebo, self.prog)
    
    @classmethod
    def erro_glfw(cls, codigo, descricao):
        """Substitui o aviso padrão do pyGLFW: imprime código 
        e descrição de qualquer erro do GLFW em stderr"""
        print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)

    def setup(self):
        window = self.get_window()
        ctx = moderngl.create_context()
        prog = ctx.program(
            vertex_shader=self.vertex_shader,
            fragment_shader=self.fragment_shader,
        )
        return ctx, prog, window


    def get_window(self):
        # antes de glfw.init(), de proposito # pq?
        glfw.set_error_callback(self.erro_glfw)

        if not glfw.init():
            sys.exit("FALHA: glfw nao inicializou")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)


        window = glfw.create_window(
            self.window_width,
            self.window_height,
            title=self.window_title,
            monitor=None,
            share=None,
        )
        if not window:
            glfw.terminate()
            sys.exit("FALHA: nao foi possivel criar a janela")

        glfw.make_context_current(window)
        
        return window

    def close(self):
        if self._closed:
            return

        for resource in self.resources:
            resource.release()

        glfw.destroy_window(self.window)
        glfw.terminate()
        self._closed = True
        print("Execucao finalizada.")

    def define_colors_and_positions(self):
        raise NotImplementedError

    def configure_colors_and_positions_base_objects(self):
        raise NotImplementedError
    
    def render_image(self):
        raise NotImplementedError
