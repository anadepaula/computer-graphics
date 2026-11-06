"""Malha OFF: normais, coordenadas de textura e enquadramento.

Tres formas de enviar a mesma malha para a GPU:

  suave()     -- indexada, uma normal por vertice
  facetada()  -- nao indexada, uma normal por face
  texturada() -- indexada, com coordenada de textura e tangente
"""
from pathlib import Path

import glm
import numpy as np

EPS = 1e-12           # evita divisao por zero ao normalizar


class Malha:
    def __init__(self, caminho, ponderar_por_area=True):
        self.caminho = Path(caminho)
        self.vertices, self.faces = ler_off(self.caminho)
        self.minimo = self.vertices.min(axis=0)
        self.maximo = self.vertices.max(axis=0)
        self.centro = 0.5 * (self.minimo + self.maximo)
        # raio da esfera envolvente, com centro no centro da caixa
        self.raio = float(np.linalg.norm(self.vertices - self.centro,
                                         axis=1).max())
        self.normais_face = normais_de_face(self.vertices, self.faces)
        self.normais_vertice = normais_de_vertice(
            self.vertices, self.faces, ponderar_por_area)

    def matriz_enquadramento(self, alvo=2.0):
        """Translada o centro para a origem e escala para que a malha
        caiba em uma esfera de diametro 'alvo'."""
        k = alvo / (2.0 * self.raio)
        return glm.scale(glm.mat4(1.0), glm.vec3(k)) \
            * glm.translate(glm.mat4(1.0), glm.vec3(*(-self.centro)))

    def suave(self):
        """(dados, indices): posicao e normal de vertice, (V, 6)."""
        dados = np.hstack([self.vertices, self.normais_vertice])
        return dados.astype('f4'), self.faces

    def facetada(self):
        """Dados sem indices: tres vertices proprios por face, todos
        com a normal da face, (3F, 6)."""
        pos = self.vertices[self.faces]                      # (F, 3, 3)
        nor = np.repeat(self.normais_face[:, None], 3, axis=1)
        return np.concatenate([pos, nor], axis=2) \
            .reshape(-1, 6).astype('f4')

    def coordenadas(self, tipo="cilindrico", eixo="y"):
        """Uma coordenada (s, t) por vertice, pelo mapeamento
        cilindrico ou esferico em torno do eixo dado."""
        eixos = {"x": (1, 2, 0), "y": (2, 0, 1), "z": (0, 1, 2)}
        if eixo not in eixos:
            raise ValueError(f"eixo invalido: {eixo}")
        ia, ib, ih = eixos[eixo]

        p = self.vertices - self.centro
        a, b, h = p[:, ia], p[:, ib], p[:, ih]
        s = (np.arctan2(b, a) + np.pi) / (2.0 * np.pi)

        if tipo == "cilindrico":
            hmin, hmax = h.min(), h.max()
            t = (h - hmin) / max(hmax - hmin, 1e-12)
        elif tipo == "esferico":
            r = np.maximum(np.linalg.norm(p, axis=1), 1e-12)
            t = 1.0 - np.arccos(np.clip(h / r, -1.0, 1.0)) / np.pi
        else:
            raise ValueError(f"tipo invalido: {tipo}")

        return np.stack([s, t], axis=1).astype('f4')

    def costurar(self, uv):
        """Duplica os vertices da costura.

        Em um triangulo que cruza a costura, os vertices com s < 0,5
        ganham uma copia com s + 1, e o triangulo passa a usar a copia.
        Devolve (uv, faces, copia, numero de copias), em que copia
        leva o indice original ao indice da copia.
        """
        uv = uv.copy()
        faces = self.faces.copy()
        extras_uv, copia = [], {}
        n = len(uv)

        for f, face in enumerate(faces):
            s = uv[face, 0]
            if s.max() - s.min() <= 0.5:
                continue                      # nao cruza a costura
            for k in range(3):
                v = face[k]
                if uv[v, 0] >= 0.5:
                    continue
                if v not in copia:
                    copia[v] = n + len(extras_uv)
                    extras_uv.append((uv[v, 0] + 1.0, uv[v, 1]))
                faces[f, k] = copia[v]

        if not extras_uv:
            return uv, faces, {}, 0

        uv = np.vstack([uv, np.array(extras_uv, dtype='f4')])
        return uv, faces, copia, len(extras_uv)

    def texturada(self, tipo="cilindrico", eixo="y", costurar=True):
        """(dados, indices) com 12 floats por vertice: posicao (3),
        normal (3), coordenada de textura (2) e tangente (4)."""
        uv = self.coordenadas(tipo, eixo)
        vertices, normais = self.vertices, self.normais_vertice

        if costurar:
            uv, faces, copia, n_extras = self.costurar(uv)
            if n_extras:
                origem = np.array(sorted(copia, key=copia.get),
                                  dtype='u4')
                vertices = np.vstack([vertices, vertices[origem]])
                normais = np.vstack([normais, normais[origem]])
        else:
            faces = self.faces

        tang = tangentes(vertices, faces, normais, uv)
        dados = np.hstack([vertices, normais, uv, tang]).astype('f4')
        return dados, faces.astype('u4')

    def resumo(self):
        return (f"{self.caminho.name}: {len(self.vertices)} vertices, "
                f"{len(self.faces)} faces, raio {self.raio:.4f}")


def normais_de_face(vertices, faces):
    a, b, c = (vertices[faces[:, i]] for i in range(3))
    n = np.cross(b - a, c - b)
    comprimento = np.linalg.norm(n, axis=1, keepdims=True)
    return (n / np.maximum(comprimento, EPS)).astype('f4')


def normais_de_vertice(vertices, faces, ponderar_por_area=True):
    """A funcao criar_normais da apostila, sem o laco em Python.

    Sem normalizar as normais das faces, cada face pesa pela sua
    area (tecla A).
    """
    a, b, c = (vertices[faces[:, i]] for i in range(3))
    n = np.cross(b - a, c - b)
    if not ponderar_por_area:
        n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), EPS)

    normais = np.zeros_like(vertices)
    # normais[faces[:, i]] += n perderia as somas de um indice
    # repetido; np.add.at soma todas.
    for i in range(3):
        np.add.at(normais, faces[:, i], n)

    comprimento = np.linalg.norm(normais, axis=1, keepdims=True)
    return (normais / np.maximum(comprimento, EPS)).astype('f4')


def tangentes(vertices, faces, normais, uv):
    """Uma tangente por vertice, com a lateralidade em w.

    Por face, resolve o sistema 2x2 que escreve as arestas em
    funcao de T e B; acumula por vertice, ortogonaliza em relacao
    a normal (Gram-Schmidt) e normaliza.
    """
    a, b, c = (vertices[faces[:, i]] for i in range(3))
    ta, tb, tc = (uv[faces[:, i]] for i in range(3))

    e1, e2 = b - a, c - a
    d1, d2 = tb - ta, tc - ta

    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    # Face degenerada no espaco da textura: peso zero.
    r = np.where(np.abs(det) > EPS,
                 1.0 / np.where(det == 0, 1.0, det), 0.0)
    r = r[:, None]

    t_face = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r
    b_face = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r

    acc_t = np.zeros_like(vertices, dtype='f8')
    acc_b = np.zeros_like(vertices, dtype='f8')
    for i in range(3):
        np.add.at(acc_t, faces[:, i], t_face)
        np.add.at(acc_b, faces[:, i], b_face)

    n = normais.astype('f8')
    t = acc_t - n * np.sum(n * acc_t, axis=1, keepdims=True)
    comprimento = np.linalg.norm(t, axis=1, keepdims=True)

    # Vertice sem tangente valida: qualquer vetor perpendicular a n.
    orfaos = (comprimento < 1e-9).ravel()
    if orfaos.any():
        eixo = np.zeros((orfaos.sum(), 3))
        menor = np.argmin(np.abs(n[orfaos]), axis=1)
        eixo[np.arange(orfaos.sum()), menor] = 1.0
        t[orfaos] = np.cross(n[orfaos], eixo)
        comprimento = np.linalg.norm(t, axis=1, keepdims=True)

    t = t / np.maximum(comprimento, EPS)

    # w = -1 onde a textura esta espelhada (B contra n x t).
    w = np.where(np.sum(np.cross(n, t) * acc_b, axis=1) < 0.0,
                 -1.0, 1.0)
    return np.hstack([t, w[:, None]]).astype('f4')


def ler_off(caminho):
    """Le um OFF de faces triangulares: (vertices, faces)."""
    campos = []
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.split("#")[0].strip()
        if linha:
            campos.extend(linha.split())

    if campos[0].upper() != "OFF":
        raise ValueError(f"{caminho}: nao comeca com OFF")

    n_vertices, n_faces = int(campos[1]), int(campos[2])
    p = 4                       # campos[3]: numero de arestas, ignorado

    vertices = np.array(campos[p:p + 3 * n_vertices],
                        dtype='f4').reshape(n_vertices, 3)
    p += 3 * n_vertices

    # cada face: o numero de lados (3) e os tres indices
    faces = np.array(campos[p:p + 4 * n_faces],
                     dtype='u4').reshape(n_faces, 4)
    if not (faces[:, 0] == 3).all():
        raise ValueError(f"{caminho}: ha faces nao triangulares; "
                         "triangule a malha antes de exportar")

    return vertices, np.ascontiguousarray(faces[:, 1:])
