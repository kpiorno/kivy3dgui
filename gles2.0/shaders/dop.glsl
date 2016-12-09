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


varying vec3 speed;
varying vec4 m_pos;
uniform float id;
 
vec3 getSpeed()
{
  return vec3(0.0, 0.0, 0.0);
  //return vec3(normalize(v), norm);
}



void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    //projection_mat = mat4(0.750, 0,0,0,0,1,0,0,0,0,-1.003,-1,0,0,-2.00,0.0);
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
   
    pos = projection_mat * pos;
    
    gl_Position = pos;
    m_pos = pos;    

}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif


uniform float cast_shadows;
uniform float id;
// Ouput data
//layout(location = 0) out float fragmentdepth;

varying vec3 speed;
vec3 getSpeedColor()
{
  //return vec3(0.5 + 0.5 * speed, 0.);
  return vec3(0.5 + 0.5 * speed.xy, pow(speed.z, 0.5));
}
 
varying vec4 m_pos;
 
void main(){
    // Not really needed, OpenGL does it anyway
    //fragmentdepth = gl_FragCoord.z;
    //if (int(id) > 2)
    //   return;
    gl_FragColor.x = 1.0-390.0/m_pos.w;
    gl_FragColor.y = 1.0-390.0/m_pos.w;
    gl_FragColor.z = 1.0-390.0/m_pos.w;
    gl_FragColor.a = 1.0-1.0;
    //gl_FragColor.xyz = getSpeedColor();
    gl_FragColor.a = 1.0;
    //if (cast_shadows==0) gl_FragColor.a = 1.0;
    //gl_FragColor = vec4(gl_FragCoord.z);
}

