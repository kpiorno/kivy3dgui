---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec4  blendIndices;
attribute vec4  blendWeights;

uniform vec3 mesh_pos;

uniform float pitch;
uniform float yaw;
uniform float roll;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 depthMVP;

vec4 quat_from_axis_angle(vec3 axis, float angle)
{ 
  vec4 qr;
  float half_angle = (angle * 0.5) * 3.14159 / 180.0;
  qr.x = axis.x * sin(half_angle);
  qr.y = axis.y * sin(half_angle);
  qr.z = axis.z * sin(half_angle);
  qr.w = cos(half_angle);
  return qr;
}

vec4 quat_conj(vec4 q)
{ 
  return vec4(-q.x, -q.y, -q.z, q.w); 
}
  
vec4 quat_mult(vec4 q1, vec4 q2)
{ 
  vec4 qr;
  qr.x = (q1.w * q2.x) + (q1.x * q2.w) + (q1.y * q2.z) - (q1.z * q2.y);
  qr.y = (q1.w * q2.y) - (q1.x * q2.z) + (q1.y * q2.w) + (q1.z * q2.x);
  qr.z = (q1.w * q2.z) + (q1.x * q2.y) - (q1.y * q2.x) + (q1.z * q2.w);
  qr.w = (q1.w * q2.w) - (q1.x * q2.x) - (q1.y * q2.y) - (q1.z * q2.z);
  return qr;
}

vec4 quat_sum(vec4 q1, vec4 q2)
{ 
  vec4 qr;
  qr.x = q1.x - q2.x;
  qr.y = q1.y - q2.y;
  qr.z = q1.z - q2.z;
  qr.w = q1.w - q2.w;
  return qr;
}

/*vec3 rotate_vertex_position(vec3 position, vec3 axis, float angle)
{ 
  vec4 qr = quat_from_axis_angle(axis, angle);
  vec4 qr_conj = quat_conj(qr);
  vec4 q_pos = vec4(position.x, position.y, position.z, 0);
  
  vec4 q_tmp = quat_mult(qr, q_pos);
  qr = quat_mult(q_tmp, qr_conj);
  
  return vec3(qr.x, qr.y, qr.z);
}*/

vec3 rotate_vertex_position(vec3 position, vec3 axis, float angle)
{ 
  vec4 q = quat_from_axis_angle(axis, angle);
  vec3 v = position.xyz;
  return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

vec3 rotate_vertex_position_q(vec3 position, vec4 q)
{ 
  vec3 v = position.xyz;
  return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}



void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    //projection_mat = mat4(0.750, 0,0,0,0,1,0,0,0,0,-1.003,-1,0,0,-2.00,0.0);
    vec4 pitch_quat = quat_from_axis_angle(vec3(1., 0., 0.), pitch);
    vec4 yaw_quat = quat_from_axis_angle(vec3(0., 1., 0.), yaw);
    vec4 roll_quat = quat_from_axis_angle(vec3(0., 0., 1.), roll);
    
    vec4 res_quat = quat_mult(quat_mult(pitch_quat, yaw_quat), roll_quat);
    //vec3 P = rotate_vertex_position_q(v_pos, res_quat);      
    
    
    vec4 pos = modelview_mat * vec4(v_pos, 1.0);
    
    pos = vec4(rotate_vertex_position_q(pos.xyz - mesh_pos, res_quat) + mesh_pos, 1.0) ;
   
    //pos = projection_mat * pos;
    
    
    gl_Position =  depthMVP * pos;

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

