#version 400 core

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec3 vNormal;

uniform mat4 u_modelo;
uniform mat4 u_visao;
uniform mat4 u_projecao;
uniform mat3 u_normal;      // inversa transposta de u_modelo

out vec3 fN;                // normal no espaco do mundo

void main() {
    gl_Position = u_projecao * u_visao * u_modelo * vPosition;
    fN = u_normal * vNormal;
}
