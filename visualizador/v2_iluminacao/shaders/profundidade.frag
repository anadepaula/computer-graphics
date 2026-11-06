#version 400 core

in float f_profundidade;

uniform float u_near;
uniform float u_far;

out vec4 outfragcolor;

void main() {
    float t = (f_profundidade - u_near) / (u_far - u_near);
    float cinza = 1.0 - clamp(t, 0.0, 1.0);  // claro na frente
    outfragcolor = vec4(vec3(cinza), 1.0);
}
