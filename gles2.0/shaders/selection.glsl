---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 camera;

varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec2 tex_coord0;

void main (void) {
     //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);
    tex_coord0 = v_tc0;
    
    gl_Position = projection_mat * camera * pos;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 normal_vec;
varying vec4 vertex_pos;

uniform mat4 normal_mat;
uniform vec3 id_color;

varying vec2 tex_coord0;

void main (void){
    //gl_FragColor = vec4(0, 0.4, 0.8, 1.0);
    float id = id_color.x;
    gl_FragColor.x = id;
    gl_FragColor.y = tex_coord0.x;
    gl_FragColor.z = tex_coord0.y;
    
    //gl_FragColor.y = gl_FragCoord.x / gl_FragCoord.w;
    //gl_FragColor.z = gl_FragCoord.y / gl_FragCoord.w;
    
    gl_FragColor.a = 1.0;
    if (tex_coord0.x <= 0.01 || tex_coord0.x >= 0.99)
        gl_FragColor.x = 0.99;
	
    if (tex_coord0.y <= 0.01 || tex_coord0.y >= 0.99)
        gl_FragColor.x = 0.99;	
}
