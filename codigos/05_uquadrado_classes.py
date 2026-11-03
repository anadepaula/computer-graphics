import sys

import glfw
import moderngl
from BaseImageClass import BaseImage
from utils import (
    basico_fragment_shader,
    uniform_vertex_shader,
    create_byte_array,
    create_unsigned_int_array,
)
from utils.basics import (
    FLOAT_32_FOR_VAO,
    POSITIONS_SQUARE,
    VARIABLE_SHADERS_COLORS,
    VARIABLE_SHADERS_POSITION,
    Colors,
    VAOType,
)


class QuadradoUniform(BaseImage):
    
    def __init__(self, window_width, window_height, window_title):
        vertex_shader = uniform_vertex_shader
        fragment_shader = basico_fragment_shader

        super().__init__(window_width, window_height, vertex_shader, fragment_shader, window_title)
        
    def define_colors_and_positions(self):
        self.vertices = create_byte_array(
            [
                -0.5, -0.5, 0.0, 1.0,
                 0.5, -0.5, 0.0, 1.0,
                 0.5,  0.5, 0.0, 1.0,
                -0.5,  0.5, 0.0, 1.0,
            ],
            type=VAOType.POSITIONS,
        )

        # Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
        # o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
        self.diagonal_02 = create_unsigned_int_array([0, 1, 2,  2, 3, 0])
        self.diagonal_13 = create_unsigned_int_array([0, 1, 3,  1, 2, 3])
        self.diagonal_alternativa = False
        self.dark_mode = False

        self.escala_passo = 0.1
        self.escala_minimo = 0.1
        self.escala_maximo = 1

        return self.configure_colors_and_positions_base_objects()
    
    def configure_colors_and_positions_base_objects(self):
        vbo = self.ctx.buffer(self.vertices)
        ebo = self.ctx.buffer(self.diagonal_02)

        vao = self.ctx.vertex_array(
            self.prog, 
            [
                (
                    vbo,
                    FLOAT_32_FOR_VAO,
                    VARIABLE_SHADERS_POSITION,
                ),
            ],
            index_buffer=ebo,
        )
        return vbo, ebo, vao

    def render_image(self):
        def tecla(janela, key, _scancode, action, _mode):

            if action == glfw.RELEASE:
                return
            elif key == glfw.KEY_UP:
                self.escala = min(self.escala + self.escala_passo, self.escala_maximo)
            elif key == glfw.KEY_DOWN:
                self.escala = max(self.escala - self.escala_passo, self.escala_minimo)
                
            if action != glfw.RELEASE:
                return

            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(janela, True)
            elif key == glfw.KEY_D:
                self.dark_mode = not self.dark_mode
            elif key == glfw.KEY_SPACE:
                self.diagonal_alternativa = not self.diagonal_alternativa
                novos = self.diagonal_13 if self.diagonal_alternativa else self.diagonal_02
                self.ebo.write(novos)
        
        glfw.set_key_callback(self.window, tecla)
        
        while not glfw.window_should_close(self.window):
            background_color = (Colors.BLACK if self.dark_mode else Colors.WHITE).value
            self.ctx.clear(*background_color)
            
            self.prog['u_escala'].value = self.escala
            
            self.prog['u_cor'].value = Colors.RED.value
            self.vao.render(moderngl.TRIANGLES, vertices=3, start=0)
            
            self.prog['u_cor'].value = Colors.RED.value
            self.vao.render(moderngl.TRIANGLES, vertices=3, start=3)
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()


def main():
    uniquad = QuadradoUniform(600, 600, "quadrado troca pisca")
    try:
        uniquad.render_image()
    finally:
        uniquad.close()

if __name__ == "__main__":
    main()
