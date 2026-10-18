import glfw
import moderngl


def setup(
    window, 
    vertex_shader, 
    fragment_shader,
    keypress_callback=None,
):
    ctx = moderngl.create_context()
    prog = ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader,
    )
    if keypress_callback is not None:
        glfw.set_key_callback(window, keypress_callback)
    
    return ctx, prog



def teardown(glfw, resources):
    for resource in resources:
        resource.release()

    glfw.terminate()
    print("Execucao finalizada.")
