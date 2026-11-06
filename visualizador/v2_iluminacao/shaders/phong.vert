#version 400 core

// Sombreamento de Phong: o vertex shader apenas leva a posicao e
// a normal para o espaco da camera. O rasterizador as interpola,
// e a equacao e avaliada uma vez por fragmento, em phong.frag.

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec3 vNormal;

uniform mat4 u_modelo, u_visao, u_projecao;
uniform mat3 u_normal;       // inversa transposta de u_modelo

out vec3 fP;    // posicao no espaco da camera
out vec3 fN;    // normal no espaco da camera, sem normalizar

void main() {
    vec4 pos_camera = u_visao * u_modelo * vPosition;
    gl_Position = u_projecao * pos_camera;
    fP = pos_camera.xyz;
    fN = mat3(u_visao) * u_normal * vNormal;
}
