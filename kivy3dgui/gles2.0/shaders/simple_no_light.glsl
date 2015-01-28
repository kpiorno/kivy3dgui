---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc0;
attribute vec2  vert_pos;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform vec2 val_sin;


varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec2 tex_coord0;


uniform sampler2D texture0;

void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    //projection_mat = mat4(0.750, 0,0,0,0,1,0,0,0,0,-1.003,-1,0,0,-2.00,0.0);
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);
    tex_coord0 = v_tc0;
    gl_Position = projection_mat * pos;
    //gl_Position = projection_mat * vec4(pos[0]*mul1, pos[1]*mul2, pos[2], pos[3]);
    //gl_Position = projection_mat * vec4(pos[0]*sin(vert_pos.x/val_sin.x), pos[1]*sin(vert_pos.x/val_sin.x), pos[2], pos[3]);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

uniform vec2  cond;


varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec2 tex_coord0;
uniform sampler2D texture0;

uniform mat4 normal_mat;

void main (void){
    //correct normal, and compute light vector (assume light at the eye)
    vec2 uv = tex_coord0;
    vec4 col = texture2D(texture0,uv);

    gl_FragColor = col;
 

}

