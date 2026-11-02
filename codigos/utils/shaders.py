from enum import StrEnum
from pathlib import Path

SHADERS_DIR = "shaders"
SHADERS_ROOT = Path(__file__).parent.parent

class SHADER_TYPE(StrEnum):
    VERTEX_SHADER = ".vert"
    FRAGMENT_SHADER = ".frag"

def get_shader(shader_name, shader_type):
    shader_path = (SHADERS_ROOT / SHADERS_DIR / shader_name).with_suffix(shader_type)
    if not shader_path.exists():
        print(f"inexistent shader: {shader_path}")
    
    shader_content = shader_path.read_text(encoding="utf-8")
    
    return shader_content


basico_vertex_shader = get_shader("basico", SHADER_TYPE.VERTEX_SHADER)
uniform_vertex_shader = get_shader("uquad", SHADER_TYPE.VERTEX_SHADER)
basico_fragment_shader = get_shader("basico", SHADER_TYPE.FRAGMENT_SHADER)
