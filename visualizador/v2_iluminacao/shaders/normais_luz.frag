#version 400 core

// A cor da normal faz o papel do material (ka e kd); o brilho
// especular vem do material corrente.

in vec3 fP;
in vec3 fN;
in vec3 fNmundo;

uniform vec4 u_luz;          // w = 1 pontual, w = 0 direcional
uniform vec3 u_ks;
uniform vec3 u_ia, u_id, u_is;
uniform float u_alfa;
uniform bool u_blinn;

out vec4 outfragcolor;

const float PESO_AMBIENTE = 0.2;

void main() {
    vec3 cor_normal = normalize(fNmundo) * 0.5 + 0.5;
    vec3 ka = PESO_AMBIENTE * cor_normal;
    vec3 kd = (1.0 - PESO_AMBIENTE) * cor_normal;

    // daqui em diante, a mesma equacao de phong.frag
    vec3 N = normalize(fN);
    vec3 L = (u_luz.w == 1.0) ? normalize(u_luz.xyz - fP)
                             : normalize(u_luz.xyz);
    vec3 V = normalize(-fP);
    float NdotL = max(dot(N, L), 0.0);

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

    vec3 cor = ka * u_ia + kd * u_id * NdotL
             + u_ks * u_is * brilho;
    outfragcolor = vec4(cor, 1.0);
}
