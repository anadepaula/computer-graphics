#version 400 core

// Como phong.vert, mas a normal segue tambem no espaco do mundo,
// para dar a mesma cor do modo normais.

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec3 vNormal;

uniform mat4 u_modelo, u_visao, u_projecao;
uniform mat3 u_normal;       // inversa transposta de u_modelo

out vec3 fP;          // posicao no espaco da camera
out vec3 fN;          // normal no espaco da camera
out vec3 fNmundo;     // normal no espaco do mundo, so para a cor

void main() {
    vec4 pos_camera = u_visao * u_modelo * vPosition;
    gl_Position = u_projecao * pos_camera;
    fP = pos_camera.xyz;
    fNmundo = u_normal * vNormal;
    fN = mat3(u_visao) * fNmundo;
}
