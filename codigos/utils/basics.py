from enum import Enum, auto

FLOAT_32_FOR_VAO = "4f"
FLOAT_32_FOR_NUMPY = "f4"
UNSIGNED_INT_32_FOR_NUMPY = "u4"
VBO_ARRAY_LEN = 4

RED =       (1.0, 0.0, 0.0, 1.0)
GREEN =     (0.0, 1.0, 0.0, 1.0)
BLUE =      (0.0, 0.0, 1.0, 1.0)
BRANCO =    (1.0, 1.0, 1.0, 1.0)
PRETO =     (0.0, 0.0, 0.0, 0.0)

POSITIONS_SQUARE = (1.0, 1.0, 1.0, 1.0)

VARIABLE_SHADERS_POSITION = "vPosition"
VARIABLE_SHADERS_COLORS = "vColors"

class Colors(Enum):
    RED =    (1.0, 0.0, 0.0, 1.0)
    GREEN =  (0.0, 1.0, 0.0, 1.0)
    BLUE =   (0.0, 0.0, 1.0, 1.0)
    WHITE =  (1.0, 1.0, 1.0, 1.0)
    BLACK =  (0.0, 0.0, 0.0, 0.0)


class VAOType(Enum):
    COLORS = auto()
    POSITIONS = auto()
    COLORS_AND_POSITIONS = auto()
