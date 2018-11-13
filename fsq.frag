#version 330

in vec2 v_text;
out vec4 f_color;

uniform vec2 Center;
uniform int Iter;
uniform float u_time;

void main() {
    vec2 z = vec2(5.0 * (v_text.x - 0.5), 3.0 * (v_text.y - 0.5));
    vec2 c = Center;

    int i;
    for(i = 0; i < Iter; i++) {
        vec2 v = vec2(
            (z.x * z.x - z.y * z.y) + c.x,
            (z.y * z.x + z.x * z.y) + c.y
        );
        if (dot(v, v) > 4.0) break;
        z = v;
    }

    float cm = fract((i == Iter ? 0.0 : float(i)) * 10 / Iter);
    f_color = vec4(
        fract(cm + 0.0 / 3.0),
        fract(cm + 1.0 / 3.0),
        fract(cm + 2.0 / 3.0),
        1.0
    );
    if (v_text.x < Center.x) {
      f_color = vec4(sin(u_time*4));
    }
}