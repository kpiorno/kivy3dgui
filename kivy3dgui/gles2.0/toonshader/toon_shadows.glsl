/* simple.glsl

simple diffuse lighting based on laberts cosine law; see e.g.:
    http://en.wikipedia.org/wiki/Lambertian_reflectance
    http://en.wikipedia.org/wiki/Lambert%27s_cosine_law
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc0;
attribute vec3  tangent;
attribute vec4  blendIndices;
attribute vec4  blendWeights;


uniform mat4 projection_mat;
uniform mat4 camera;
uniform mat4 matrix_view;
uniform vec2 val_sin;
uniform mat4 depthMVP;
uniform float enabled_shadow;
uniform float min_light_intensity;
uniform mat4 normal_mat;
uniform vec4 ambient_light;
uniform vec4 light_intensity;
uniform float light_visibility;
uniform vec3 eye_position;
uniform mat4 modelview_mat;
uniform vec3 light_position;
uniform vec3 light_orientation;
uniform vec3 light_0;
uniform vec3 light_1;

uniform vec3 mesh_pos;

uniform float specular_intensity;
uniform float specular_power;
uniform float pitch;
uniform float yaw;
uniform float roll;
uniform int axis_type;

varying mat4 modelview_mat_frag;
varying vec3 eye_position_frag;
varying vec3 world_vertex_pos;
varying mat4 normal_mat_frag;
varying vec4 normal_vec;
varying vec3 vertex_pos;
varying vec4 mv_vertex_pos;

varying vec2 tex_coord0;
varying vec3 t_tangent;
varying vec4 ShadowCoord;
varying vec3 Normal;
varying vec4 lightPosition;
varying float edge;
varying vec3 L;
varying vec3 N;
varying vec3 light_position_frag;
varying vec3 light_orientation_frag;
varying vec3 light_0_frag;
varying vec3 light_1_frag;
varying float normal_map_enabled_frag;

uniform sampler2D texture0;
uniform sampler2D texture1;
uniform sampler2D texture2;
uniform float normal_map_enabled;

mat4 depthBiasMVP = mat4(0.5, 0.0, 0.0, 0.0,
0.0, 0.5, 0.0, 0.0,
0.0, 0.0, 0.5, 0.0,
0.5, 0.5, 0.5, 1.0);

mat4 M = mat4(1.0, 0.0, 0.0, 0.0,
0.0, 1.0, 0.0, 0.0,
0.0, 0.0, 1.0, 0.0,
0.0, 0.0, 0.0, 1.0);

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
	normal_vec = vec4(v_normal,1.0);
    vec4 pitch_quat = quat_from_axis_angle(vec3(1., 0., 0.), pitch);
    vec4 yaw_quat = quat_from_axis_angle(vec3(0., 1., 0.), yaw);
    vec4 roll_quat = quat_from_axis_angle(vec3(0., 0., 1.), roll);
    
    vec4 res_quat = vec4(0, 0, 0, 1);
    res_quat = quat_mult(quat_mult(pitch_quat, yaw_quat), roll_quat);

    //vec4 res_quat = quat_sum(quat_sum(pitch_quat, yaw_quat), roll_quat);

    vec3 P = rotate_vertex_position_q(v_pos, res_quat);
	vec4 pos = modelview_mat * vec4(v_pos, 1.0);
    
    pos = vec4(rotate_vertex_position_q(pos.xyz - mesh_pos, res_quat) + mesh_pos, 1.0) ;
    //vec4 pos = modelview_mat * vec4(P, 1.0);

	#ifdef __GLSL_CG_DATA_TYPES // Fix clipping for Nvidia and ATI
	gl_ClipVertex = projection_mat * gl_Vertex;
	#endif

	lightPosition = modelview_mat * camera* vec4(0.5, 200, 0, 1) ;

    
	vec4 e_pos = projection_mat * camera * pos;
    normal_vec =  /*modelview_mat * projection_mat * */ vec4(rotate_vertex_position_q(normal_vec.xyz, res_quat), 1.0);
    
	tex_coord0 = v_tc0;
	ShadowCoord  = depthBiasMVP*depthMVP * pos;
	//t_tangent = (projection_mat * camera * vec4(tangent, 1.0)).xyz;
	t_tangent = (normal_mat * vec4(tangent, 1.0)).xyz;

	normal_mat_frag = normal_mat;
	modelview_mat_frag = modelview_mat;
	eye_position_frag = (projection_mat * modelview_mat * camera * vec4(eye_position,1.0)).xyz;

	light_position_frag = light_position;
    light_orientation_frag = light_orientation;
    normal_map_enabled_frag = normal_map_enabled;
    //world_vertex_pos = (vec4(v_pos.xyz, 1.0)).xyz;
    //world_vertex_pos = (projection_mat * modelview_mat * camera * vec4(P, 1.0)).xyz;
    world_vertex_pos = e_pos.xyz;
    light_0_frag = light_0;
    light_1_frag = light_1;


	//gl_Position = e_pos;
	gl_Position = e_pos;
    vertex_pos = e_pos.xyz;
    mv_vertex_pos =  modelview_mat * vec4(P, 1.0);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

uniform vec2  cond;


varying vec4 normal_vec;
varying vec3 vertex_pos;
varying vec4 mv_vertex_pos;

varying vec2 tex_coord0;
varying vec3 t_tangent;
varying vec3 eye_position_frag;

varying float edge;
varying mat4 modelview_mat_frag;
varying mat4 normal_mat_frag;

uniform float alpha;
uniform float alpha_threshold;
uniform float shadows_bias;
uniform float enabled_shadow;
uniform float min_light_intensity;
uniform float lighting;
uniform float flip_coords;
uniform vec4 light_intensity;
uniform sampler2D texture0;
uniform sampler2D texture1;
uniform sampler2D texture2;
uniform vec4 ambient_light;
uniform float light_visibility;
uniform float normal_map_enabled;
uniform vec3 light_position;
uniform vec3 light_orientation;
uniform float specular_intensity;
uniform float specular_power;

varying vec3 Normal;
varying vec4 lightPosition;
varying vec4 ShadowCoord;
varying vec3 light_position_frag;
varying vec3 light_orientation_frag;
varying vec3 light_0_frag;
varying vec3 light_1_frag;
varying float normal_map_enabled_frag;
varying vec3 world_vertex_pos;

uniform vec3 L;
uniform vec3 N;
vec2 poissonDisk[4];


/*
normal mapping based on:
http://ogldev.atspace.co.uk/www/tutorial26/tutorial26.html
*/
vec3 calc_bumped_normal(vec3 normal, vec2 text_coords)
{
    vec3 c_normal = normalize(normal);
    vec3 tangent = normalize(t_tangent);
    tangent = normalize(tangent - dot(tangent, c_normal) * c_normal);
    vec3 bitangent = cross(tangent, c_normal);
    vec3 bump_map_normal = texture2D(texture2, text_coords).xyz;
    bump_map_normal = 2.0 * bump_map_normal - vec3(1.0, 1.0, 1.0);
    vec3 result;
    mat3 TBN = mat3(tangent, bitangent, c_normal);
    result = TBN * bump_map_normal;
    result = normalize(result);
    return result;
}

void main (void){
    poissonDisk[0] = vec2( -0.94201624, -0.39906216 );
    poissonDisk[1] = vec2( 0.94558609, -0.76890725 );
    poissonDisk[2] = vec2( -0.094184101, -0.92938870 );
    poissonDisk[3] = vec2( 0.34495938, 0.29387760 );
    vec4 color1 = vec4(1.0,1.0,1.0,1.0);
    vec2 t_coords = tex_coord0;
    if (int(flip_coords) == 1)
        t_coords = vec2(tex_coord0.x, 1.0 - tex_coord0.y);

    color1 = texture2D( texture0, t_coords );
    vec4 color2;
    
    vec4 v_normal = normalize(  normal_mat_frag *  normal_vec ) + vec4(0.3, 0.3, 0.3, 1.0);
    //vec3 light_position_f = normalize(vec4(10, 100, 100, 1) - mv_vertex_pos).xyz;
    vec3 light_position_f = light_position_frag - mv_vertex_pos.xyz;

    
    if (normal_map_enabled == 1.0)
        v_normal = vec4(calc_bumped_normal(v_normal.xyz, vec2(t_coords.x, 1.0 - t_coords.y)).xyz, .0);

    float diffuse = max(dot(v_normal.xyz, normalize(light_position_f)), 0.0);


    if (diffuse < min_light_intensity) diffuse = min_light_intensity;
    
    /*float cosTheta = dot((normal_mat_frag *  normal_vec).xyz, normalize(vec3(0.01, 1., 0.01)));
    float bias = 0.005*tan(acos(cosTheta)); 
    bias = clamp(bias, 0.,shadows_bias);*/

    float visibility = 1.1;
    if (ShadowCoord.x >= 0.0 && ShadowCoord.y >= 0.0 &&  ShadowCoord.x <= 1.0 && ShadowCoord.y <= 1.0)
    for (int i=0;i<4;i++){
      if ( texture2D( texture1, ShadowCoord.xy + poissonDisk[i]/700.0).z <  ShadowCoord.z-shadows_bias  ){
            visibility-=0.1;
      }
    }
    
    
/*if ( texture2D( texture1, ShadowCoord.xy).z <  ShadowCoord.z-shadows_bias){
    visibility = 0.5;
} */   

    if (enabled_shadow == 0.0) visibility = 1.0;
    float res_alpha = 1.0;
    res_alpha = color1.a;

    if (lighting == 0.0) {
       visibility = light_intensity.x;
       diffuse = 1.0;
    }
	gl_FragColor = vec4(0, 0, 0, 1.0);
    vec4 f_color;
    visibility += light_visibility;

    vec4 DiffuseColor = vec4(0, 0, 0, 0);
    vec4 SpecularColor = vec4(0, 0, 0, 0);

    //vec3 eye_position_fragx = vec3(-4, 10, -109.7);
    vec3 VertexToEye = normalize(eye_position_frag - world_vertex_pos);
    vec3 LightReflect = normalize(reflect(vec3(normalize(light_position_f.xyz-world_vertex_pos)), v_normal.xyz));

    /*vec4 v_light = normalize( vec4(light_position_f, 1.0) - vec4(world_vertex_pos.xyz, 1.0));
    vec3 LightReflect =  vec3(1.0, 1.0, 1.0) * pow(max(dot(v_light, vec4(v_normal.xyz,1)), 0.0), 0.9);
    SpecularColor = vec4(LightReflect, 1.0);*/

    vec3 LightReflect2 = normalize(reflect(vec3(normalize(light_orientation_frag.xyz-world_vertex_pos)), v_normal.xyz));
    vec3 LightReflect3 = normalize(reflect(vec3(normalize(light_0_frag.xyz-world_vertex_pos)), v_normal.xyz));
    vec3 LightReflect4 = normalize(reflect(vec3(normalize(light_1_frag.xyz-world_vertex_pos)), v_normal.xyz));

    float SpecularFactor = dot(VertexToEye, LightReflect);
    float SpecularFactor2 = dot(VertexToEye, LightReflect2);
    float SpecularFactor3 = dot(VertexToEye, LightReflect3);
    float SpecularFactor4 = dot(VertexToEye, LightReflect4);
    SpecularFactor = 0.01;
    //if (SpecularFactor > 0.0) {
  
        SpecularFactor = SpecularFactor > 0.0 ? pow(SpecularFactor, specular_power) : 0.0;
        SpecularFactor2 = SpecularFactor2 > 0.0 ? pow(SpecularFactor2, specular_power) : 0.0;
        SpecularFactor3 = SpecularFactor3 > 0.0 ? pow(SpecularFactor3, specular_power) : 0.0;
        SpecularFactor4 = SpecularFactor4 > 0.0 ? pow(SpecularFactor4, specular_power) : 0.0;

        if (SpecularFactor  < 0.0)  SpecularFactor = 0.0;
        if (SpecularFactor2 < 0.0) SpecularFactor2 = 0.0;
        if (SpecularFactor3 < 0.0) SpecularFactor3 = 0.0;
        if (SpecularFactor4 < 0.0) SpecularFactor4 = 0.0;

        if (SpecularFactor2 < 0.0) SpecularFactor2 = 0.0;
        if (SpecularFactor3 < 0.0) SpecularFactor3 = 0.0;
        if (SpecularFactor4 < 0.0) SpecularFactor4 = 0.0;

        float spec_result = SpecularFactor+SpecularFactor2+SpecularFactor3+SpecularFactor4;
        SpecularColor = vec4(specular_intensity * spec_result,
                             specular_intensity * spec_result,
                             specular_intensity * spec_result, 1.0);
    //}


    f_color = vec4((color1).xyz*visibility*diffuse, res_alpha) + SpecularColor;
    if (color1.r <= alpha_threshold && color1.g <= alpha_threshold && color1.b <= alpha_threshold)
        f_color.a = alpha;
    else    
        f_color.a = 1.0;
    f_color += ambient_light;
    gl_FragColor = f_color;


}

