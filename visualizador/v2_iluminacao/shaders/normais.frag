#version 400 core

in vec3 fN;             // normal interpolada
out vec4 outfragcolor;

void main() {
    // A interpolacao encurta a normal: normaliza de novo.
    vec3 N = normalize(fN);

    // De [-1,1] para [0,1]: x no R, y no G, z no B.
    outfragcolor = vec4(N * 0.5 + 0.5, 1.0);
}
