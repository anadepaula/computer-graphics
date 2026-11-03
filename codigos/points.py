import numpy as np

N_POS_COORDS = 4
N_COL_COORDS = 4

class MaldefinedPointError(Exception):
    def __init__(self, position_coordinates, color_coordinates):
        message = (
            f"maldefined point ({position_coordinates}, {color_coordinates}), "
            f"there are ({len(position_coordinates)}, {len(color_coordinates)}) "
            f"and there must be ({N_POS_COORDS}, {N_COL_COORDS})"
        )
        super().__init__(message)
    

def create_4f_array(values):
    return np.array(values, dtype='4f')
    
class Points:
    def __init__(self, position_coordinates, color_coordinates):
        self._validate_coordinates_length(position_coordinates, color_coordinates)
        self.position = create_4f_array(position_coordinates)
        self.colors = create_4f_array(color_coordinates)
    
    @classmethod
    def _validate_coordinates_length(cls, position_coordinates, color_coordinates):
        n_pos_coords = len(position_coordinates)
        n_col_coords = len(color_coordinates)

        if n_pos_coords != N_POS_COORDS or n_col_coords != N_COL_COORDS:
            raise MaldefinedPointError(position_coordinates, color_coordinates)
