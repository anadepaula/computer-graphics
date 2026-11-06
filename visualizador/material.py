"""Materiais e luz do modelo de Phong.

Os coeficientes estao em luz linear: a codificacao sRGB da saida
e feita pelo OpenGL (GL_FRAMEBUFFER_SRGB).
"""
import glm


class Material:
    def __init__(self, nome, ka, kd, ks, alfa):
        self.nome = nome
        self.ka, self.kd, self.ks = glm.vec3(*ka), glm.vec3(*kd), \
            glm.vec3(*ks)
        self.alfa = alfa


# Tecla M. Cada valor e a cor que se quer ver na tela (sRGB),
# decodificada uma vez, aqui, pela equacao do sRGB.
MATERIAIS = [
    Material("plastico vermelho", (0.004, 0.000, 0.000),
             (0.319, 0.010, 0.010), (0.448, 0.319, 0.319), 32.0),
    Material("borracha azul", (0.000, 0.001, 0.003),
             (0.033, 0.064, 0.263), (0.020, 0.020, 0.027), 8.0),
    Material("latao", (0.012, 0.005, 0.001),
             (0.570, 0.285, 0.012), (0.977, 0.869, 0.621), 128.0),
    Material("gesso", (0.010, 0.010, 0.010),
             (0.477, 0.448, 0.393), (0.002, 0.002, 0.002), 4.0),
]

# Modos de textura: em textura.frag a imagem faz o papel de kd;
# o kd de RELEVO so e usado no mapa de normais sem albedo (tecla X).
TEXTURA = Material("textura", (0.05, 0.05, 0.06), (1.0, 1.0, 1.0),
                   (0.25, 0.25, 0.25), 48.0)
RELEVO = Material("relevo", (0.06, 0.05, 0.05), (0.62, 0.58, 0.54),
                  (0.30, 0.30, 0.30), 48.0)


class Luz:
    def __init__(self):
        # w = 1: pontual; w = 0: direcional (tecla L)
        self.posicao = glm.vec4(1.6, 1.4, 2.4, 1.0)
        self.ia = glm.vec3(1.0, 1.0, 1.0)
        self.id = glm.vec3(1.0, 1.0, 1.0)
        self.is_ = glm.vec3(1.0, 1.0, 1.0)

    def alternar_tipo(self):
        self.posicao.w = 0.0 if self.posicao.w == 1.0 else 1.0
