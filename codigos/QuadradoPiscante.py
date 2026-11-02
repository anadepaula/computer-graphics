import glfw
import moderngl
from BaseImageClass import BaseImage
from utils import (
    FLOAT_32_FOR_VAO,
    POSITIONS_SQUARE,
    VARIABLE_SHADERS_COLORS,
    VARIABLE_SHADERS_POSITION,
    Colors,
    basico_fragment_shader,
    basico_vertex_shader,
    create_colors_and_positions_byte_array,
    create_unsigned_int_array,
)


class QuadradoTrocaPisca(BaseImage):
    
    def __init__(self, window_width, window_height, window_title):
        vertex_shader = basico_vertex_shader
        fragment_shader = basico_fragment_shader

        super().__init__(window_width, window_height, vertex_shader, fragment_shader, window_title)
        
    def define_colors_and_positions(self):
        self.vertices = create_colors_and_positions_byte_array([
            -0.5, -0.5, 0.0, 1.0, *(Colors.RED.value),
             0.5, -0.5, 0.0, 1.0, *(Colors.GREEN.value),
             0.5,  0.5, 0.0, 1.0, *(Colors.BLUE.value),
            -0.5,  0.5, 0.0, 1.0, *(Colors.YELLOW.value),
        ])

        # Dois triangulos pela diagonal 0-2. Os indices sao inteiros SEM sinal:
        # o arranjo de elementos do OpenGL e GL_UNSIGNED_INT.
        self.diagonal_02 = create_unsigned_int_array([0, 1, 2,  2, 3, 0])
        self.diagonal_13 = create_unsigned_int_array([0, 1, 3,  1, 2, 3])
        self.diagonal_alternativa = False
        self.dark_mode = False
        return self.configure_colors_and_positions_base_objects()
    
    def configure_colors_and_positions_base_objects(self):
        vbo = self.ctx.buffer(self.vertices)
        ebo = self.ctx.buffer(self.diagonal_02)

        vao = self.ctx.vertex_array(
            self.prog, 
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
        return vbo, ebo, vao

    def render_image(self):
        def tecla(janela, key, _scancode, action, _mode):
            if action != glfw.PRESS:
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
            if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.window, True)

            self.ctx.clear(*POSITIONS_SQUARE)
            
            background_color = (Colors.BLACK if self.dark_mode else Colors.WHITE).value
            self.ctx.clear(*background_color)
            
            self.vao.render(moderngl.TRIANGLES)
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()


def main():
    quadtropis = QuadradoTrocaPisca(600, 600, "quadrado troca pisca")
    try:
        quadtropis.render_image()
    finally:
        quadtropis.close()

if __name__ == "__main__":
    main()
