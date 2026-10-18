from enum import Enum, auto

FLOAT_32_FOR_VAO = "4f"
FLOAT_32_FOR_NUMPY = "f4"
VBO_ARRAY_LEN = 4

RED = (1.0, 0.0, 0.0, 1.0)
GREEN = (0.0, 1.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

POSITIONS_SQUARE = (1.0, 1.0, 1.0, 1.0)

class VAOType(Enum):
    COLORS = auto()
    POSITIONS = auto()

