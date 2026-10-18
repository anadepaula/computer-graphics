
import numpy as np

from .basics import (
    FLOAT_32_FOR_NUMPY,
    UNSIGNED_INT_32_FOR_NUMPY,
    VBO_ARRAY_LEN,
    VAOType,
)


def create_unsigned_int_array(data):
    return np.array(data, dtype=UNSIGNED_INT_32_FOR_NUMPY)

def create_byte_array(data, type):
    validate_array(data, type)
    array = np.array(
        data,
        dtype=FLOAT_32_FOR_NUMPY
    )
    return array.tobytes()

def validate_array(data, vao_type):
    # assert all values are normalized between min_value and max_value of each VAO type
    match vao_type:
        case VAOType.COLORS:
            min_value, max_value = 0.0, 1.0
        case VAOType.POSITIONS:
            min_value, max_value = -1.0, 1.0
        case _:
            raise Exception("unreachable?")

    assert all(min(quad) >= min_value and max(quad) <= max_value for quad in data)
    # assert data is a list of tuples of length 4
    assert isinstance(data, list)
    assert set(map(type, data)) == {tuple}
    assert set(map(len, data)) == {VBO_ARRAY_LEN}    

def create_colors_and_positions_byte_array(data):
    array = np.array(
        data,
        dtype=FLOAT_32_FOR_NUMPY
    )
    return array.tobytes()
