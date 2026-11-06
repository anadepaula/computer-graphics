#version 400 core

layout(location = 0) in vec4 vPosition;

uniform mat4 u_modelo;
uniform mat4 u_visao;
uniform mat4 u_projecao;

out float f_profundidade;

void main() {
    vec4 pos_camera = u_visao * u_modelo * vPosition;
    gl_Position = u_projecao * pos_camera;

    // Distancia ate a camera, no espaco da camera. Em NDC, z nao
    // seria linear na distancia.
    f_profundidade = -pos_camera.z;
}
