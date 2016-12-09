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

//uniform mat4 oldTransformation;
uniform mat4 oldTransformation0;
uniform mat4 oldTransformation1;
uniform mat4 oldTransformation2;
uniform mat4 oldTransformation3;
uniform mat4 oldTransformation4;
uniform mat4 oldTransformation5;
uniform mat4 oldTransformation6;
uniform mat4 oldTransformation7;
uniform mat4 oldTransformation8;
uniform mat4 oldTransformation9;
uniform mat4 oldTransformation10;
uniform mat4 oldTransformation11;
uniform mat4 oldTransformation12;
uniform mat4 oldTransformation13;
uniform mat4 oldTransformation14;
uniform mat4 oldTransformation15;
uniform mat4 oldTransformation16;
uniform mat4 oldTransformation17;
uniform mat4 oldTransformation18;
uniform mat4 oldTransformation19;
uniform mat4 oldTransformation20;



varying vec3 speed;
uniform float id;
 
vec3 getSpeed()
{
  //mat4 oldTransformation = mat4(1, 0 ,0 , 900, 0, 1 ,0 ,0 ,0,0,1,1200,0,0,0,1.0);
  
  //vec4 oldScreenCoord = oldTransformation * vec4(v_pos, 1);
  mat4 oldTransformation = mat4(1);
   
  if (int(id) == 0) oldTransformation = oldTransformation0;
  else if (int(id) == 1) oldTransformation = oldTransformation1;
  else if (int(id) == 2) oldTransformation = oldTransformation2;
  else if (int(id) == 3) oldTransformation = oldTransformation3;
  else if (int(id) == 4) oldTransformation = oldTransformation4;
  else if (int(id) == 5) oldTransformation = oldTransformation5;
  else if (int(id) == 6) oldTransformation = oldTransformation6;
  else if (int(id) == 7) oldTransformation = oldTransformation7;
  else if (int(id) == 8) oldTransformation = oldTransformation8;
  else if (int(id) == 9) oldTransformation = oldTransformation9;
  else if (int(id) == 10) oldTransformation = oldTransformation10;
  else if (int(id) == 11) oldTransformation = oldTransformation11;
  else if (int(id) == 12) oldTransformation = oldTransformation12;
  else if (int(id) == 13) oldTransformation = oldTransformation13;
  else if (int(id) == 14) oldTransformation = oldTransformation14;
  else if (int(id) == 15) oldTransformation = oldTransformation15;
  else if (int(id) == 16) oldTransformation = oldTransformation16;
  else if (int(id) == 17) oldTransformation = oldTransformation17;
  else if (int(id) == 18) oldTransformation = oldTransformation18;
  else if (int(id) == 18) oldTransformation = oldTransformation19;
  else if (int(id) == 20) oldTransformation = oldTransformation20;
  
  
  vec4 oldScreenCoord = oldTransformation * vec4(v_pos, 1);
  vec4 newScreenCoord = projection_mat * vec4(v_pos, 1);
  vec2 v = newScreenCoord.xy / newScreenCoord.w - oldScreenCoord.xy / oldScreenCoord.w;
  float norm = length(v);
  return vec3(normalize(v), norm);
  //return vec2(0.0, 0.0);
  //return vec3(normalize(v), norm);
}



void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    //projection_mat = mat4(0.750, 0,0,0,0,1,0,0,0,0,-1.003,-1,0,0,-2.00,0.0);
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
   
    pos = projection_mat * pos;
    
    speed = getSpeed();
    gl_Position = pos;
        

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
 

 
void main(){
    // Not really needed, OpenGL does it anyway
    //fragmentdepth = gl_FragCoord.z;
    //if (int(id) > 2)
    //   return vec4();
    /*gl_FragColor.x = gl_FragCoord.z;
    gl_FragColor.y = gl_FragCoord.z;
    gl_FragColor.z = gl_FragCoord.z;
    gl_FragColor.a = 1.0;*/
    gl_FragColor.xyz = getSpeedColor();
    gl_FragColor.a = 1.0;
    //if (cast_shadows==0) gl_FragColor.a = 1.0;
    //gl_FragColor = vec4(gl_FragCoord.z);
}

