#version 400 core

// Sombreamento de Phong: a equacao e avaliada uma vez por
// fragmento, com a posicao e a normal interpoladas.

in vec3 fP;
in vec3 fN;

uniform vec4 u_luz;          // w = 1 pontual, w = 0 direcional
uniform vec3 u_ka, u_kd, u_ks;
uniform vec3 u_ia, u_id, u_is;
uniform float u_alfa;
uniform bool u_blinn;
uniform bool u_cartoon;
uniform int u_niveis;        // numero de niveis do cartoon

out vec4 outfragcolor;

// Cartoon: o maior multiplo de 1/u_niveis que nao ultrapassa f.
float quantizar(float f) {
    return floor(f * float(u_niveis)) / float(u_niveis);
}

// A funcao de gouraud.vert, com uma linha a mais para o cartoon.
vec3 phong(vec3 P, vec3 N) {
    vec3 L = (u_luz.w == 1.0)
           ? normalize(u_luz.xyz - P)    // pontual
           : normalize(u_luz.xyz);       // direcional
    vec3 V = normalize(-P);              // camera na origem
    float NdotL = max(dot(N, L), 0.0);

    vec3 ambiente = u_ka * u_ia;
    vec3 difusa   = u_kd * u_id * NdotL;
    if (u_cartoon) difusa = u_kd * u_id * quantizar(NdotL);

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
    vec3 N = normalize(fN);    // a interpolacao encurta a normal
    outfragcolor = vec4(phong(fP, N), 1.0);
}
