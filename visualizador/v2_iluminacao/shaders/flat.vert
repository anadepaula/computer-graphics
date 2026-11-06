#version 400 core

// Sombreamento flat: a mesma equacao de gouraud.vert, mas a
// saida tem o qualificador flat. O rasterizador nao interpola:
// usa a cor do vertice provocante no triangulo inteiro.

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec3 vNormal;

uniform mat4 u_modelo, u_visao, u_projecao;
uniform mat3 u_normal;       // inversa transposta de u_modelo
uniform vec4 u_luz;          // w = 1 pontual, w = 0 direcional
uniform vec3 u_ka, u_kd, u_ks;
uniform vec3 u_ia, u_id, u_is;
uniform float u_alfa;
uniform bool u_blinn;

flat out vec4 v2fcolor;

// Modelo de Phong no ponto P, com normal unitaria N.
vec3 phong(vec3 P, vec3 N) {
    vec3 L = (u_luz.w == 1.0)
           ? normalize(u_luz.xyz - P)    // pontual
           : normalize(u_luz.xyz);       // direcional
    vec3 V = normalize(-P);              // camera na origem
    float NdotL = max(dot(N, L), 0.0);

    vec3 ambiente = u_ka * u_ia;
    vec3 difusa   = u_kd * u_id * NdotL;

    // sem brilho especular onde a luz nao chega
    float brilho = 0.0;
    if (NdotL > 0.0) {
        if (u_blinn) {
            vec3 H = normalize(L + V);
            brilho = pow(max(dot(N, H), 0.0), u_alfa);
        } else {
            vec3 R = reflect(-L, N);
            brilho = pow(max(dot(R, V), 0.0), u_alfa);
        }
    }
    return ambiente + difusa + u_ks * u_is * brilho;
}

void main() {
    vec4 pos_camera = u_visao * u_modelo * vPosition;
    gl_Position = u_projecao * pos_camera;
    vec3 N = normalize(mat3(u_visao) * u_normal * vNormal);
    v2fcolor = vec4(phong(pos_camera.xyz, N), 1.0);
}
