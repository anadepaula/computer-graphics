#version 400 core
// Vertex shader de repasse. 
// Nao transforma a geometria, apenas a encaminha.
// Usado por 03_triangulo.py, 04_quadrado.py e 05_quadrado_diagonal.py.

layout(location = 0) in vec4 vPosition;

uniform float u_escala;
uniform float u_cor;

out vec4 v2fcolor;

void main() {
    gl_Position = vec4(vPosition.xy * u_escala, vPosition.zw);
    v2fcolor = u_cor;
}
