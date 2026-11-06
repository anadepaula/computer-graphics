"""Camera LookAt e as projecoes perspectiva e ortografica."""
import glm

FOVY = 45.0          # abertura vertical, em graus
FOLGA = 1.8          # distancia do centro ate os planos near e far
NEAR_MIN = 0.05


class Camera:
    def __init__(self, distancia=3.0):
        self.distancia = distancia
        self.centro = glm.vec3(0.0, 0.0, 0.0)
        self.cima = glm.vec3(0.0, 1.0, 0.0)
        self.aspecto = 1.0
        self.fovy = glm.radians(FOVY)
        self.perspectiva = True

    @property
    def olho(self):
        return self.centro + glm.vec3(0.0, 0.0, self.distancia)

    # near e far acompanham a distancia: o near fica o mais longe
    # possivel da camera, o que preserva a precisao do depth buffer.
    @property
    def near(self):
        return max(NEAR_MIN, self.distancia - FOLGA)

    @property
    def far(self):
        return self.distancia + FOLGA

    def visao(self):
        return glm.lookAt(self.olho, self.centro, self.cima)

    def projecao(self):
        if self.perspectiva:
            return glm.perspective(self.fovy, self.aspecto,
                                   self.near, self.far)
        # Meia-altura que mostra o centro com o mesmo tamanho
        # aparente da perspectiva.
        t = self.distancia * glm.tan(self.fovy / 2.0)
        r = t * self.aspecto
        return glm.ortho(-r, r, -t, t, self.near, self.far)
