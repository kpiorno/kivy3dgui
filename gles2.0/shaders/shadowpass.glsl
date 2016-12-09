---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec4  blendIndices;
attribute vec4  blendWeights;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 depthMVP;





void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    //projection_mat = mat4(0.750, 0,0,0,0,1,0,0,0,0,-1.003,-1,0,0,-2.00,0.0);
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
   
    //pos = projection_mat * pos;
    
    
    gl_Position =  depthMVP * pos;
    //gl_Position = projection_mat * vec4(pos[0]*mul1, pos[1]*mul2, pos[2], pos[3]);
    //gl_Position = projection_mat * vec4(pos[0]*sin(vert_pos.x/val_sin.x), pos[1]*sin(vert_pos.x/val_sin.x), pos[2], pos[3]);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif


uniform float cast_shadows;
// Ouput data
//layout(location = 0) out float fragmentdepth;
 
void main(){
    // Not really needed, OpenGL does it anyway
    //fragmentdepth = gl_FragCoord.z;
    
    gl_FragColor.x = gl_FragCoord.z;
    gl_FragColor.y = gl_FragCoord.z;
    gl_FragColor.z = gl_FragCoord.z;
    gl_FragColor.a = 1.0;
    if (cast_shadows==0.0) gl_FragColor.a = 0.0;
    //gl_FragColor = vec4(gl_FragCoord.z);
}

