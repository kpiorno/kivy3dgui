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
attribute vec4  blendIndices;
attribute vec4  blendWeights;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 matrix_view;
uniform vec2 val_sin;
uniform mat4 depthMVP;
uniform float enabled_shadow;
uniform mat4 normal_mat;

varying vec4 normal_vec;
varying vec3 vertex_pos;
varying vec2 tex_coord0;
varying vec4 ShadowCoord;
varying vec3 Normal;
varying vec4 lightPosition;
varying float edge;
varying vec3 L;
varying vec3 N;
uniform sampler2D texture0;
uniform sampler2DShadow texture1;

mat4 depthBiasMVP = mat4(0.5, 0.0, 0.0, 0.0,
0.0, 0.5, 0.0, 0.0,
0.0, 0.0, 0.5, 0.0,
0.5, 0.5, 0.5, 1.0);

mat4 M = mat4(1.0, 0.0, 0.0, 0.0,
0.0, 1.0, 0.0, 0.0,
0.0, 0.0, 1.0, 0.0,
0.0, 0.0, 0.0, 1.0);


void main (void) {
	normal_vec = vec4(v_normal,0.0);
	vec4 pos = modelview_mat * vec4(v_pos,1.0);
        vec3 N = normalize(normal_mat * normal_vec).xyz;
	vec3 E = normalize(vec3(0,0,0)-pos.xyz);
	//Normal = normalize(gl_NormalMatrix * v_normal).xyz;
	#ifdef __GLSL_CG_DATA_TYPES // Fix clipping for Nvidia and ATI
	gl_ClipVertex = projection_mat * gl_Vertex;
	#endif
	//gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	float dne = dot(N, E);
	edge = dne > 0.0 ? dne : 0.0;
	lightPosition = modelview_mat * vec4(0.5, 200, 0, 1);
	vec4 e_pos = projection_mat *  pos;
	tex_coord0 = v_tc0;
	ShadowCoord  = depthBiasMVP*depthMVP * pos;
	//ShadowCoord  = depthMVP * pos;
	
	 
	// Position of the vertex, in worldspace : M * position
	//Position_worldspace = (M*v_pos).xyz;
	 
	// Vector that goes from the vertex to the camera, in camera space.
	// In camera space, the camera is at the origin (0,0,0).
	vec3 vertexPosition_cameraspace = (pos).xyz;
	vec3 EyeDirection_cameraspace = vec3(0,0,0) - vertexPosition_cameraspace;
	 
	// Vector that goes from the vertex to the light, in camera space. M is ommited because it's identity.
	vec3 LightPosition_cameraspace = vec4(vec3(0.5, 200, 100),0).xyz;
	L = LightPosition_cameraspace + EyeDirection_cameraspace;
	//L = LightPosition_cameraspace + EyeDirection_cameraspace;
	 
	// Normal of the the vertex, in camera space
	N = ( modelview_mat * vec4(v_normal,0)).xyz; // Only correct if ModelMatrix does not scale the model ! Use its inverse transpose if not.	
	gl_Position = e_pos;
	vertex_pos = e_pos.xyz;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

uniform vec2  cond;


varying vec4 normal_vec;
varying vec3 vertex_pos;
varying vec2 tex_coord0;
varying float edge;
uniform float enabled_shadow;
uniform float lighting;
uniform float flip_coords;
uniform vec4 light_intensity;
uniform sampler2D texture0;
uniform sampler2DShadow texture1;

uniform mat4 normal_mat;
varying vec3 Normal;
varying vec4 lightPosition;
varying vec4 ShadowCoord;
uniform vec3 L;
uniform vec3 N;
vec3 LightPosition = vec3(0.5, 50, 100);
vec2 poissonDisk[4]; 

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
    
    //vec4 v_normal = normalize( normal_mat * normal_vec ) ;
    vec4 v_normal = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vec4(vertex_pos, 1) );    

    float intensity = dot(normalize(LightPosition),v_normal.xyz);

    if (intensity > 0.80)      color2 = vec4(1.0, 1.0, 1.0, 1.0);
    else if (intensity > 0.75) color2 = vec4(0.8, 0.8, 0.8, 1.0);
    else if (intensity > 0.50) color2 = vec4(0.6, 0.6, 0.6, 1.0);
    else if (intensity > 0.25) color2 = vec4(0.4, 0.4, 0.4, 1.0);
    else                       color2 = vec4(0.2, 0.2, 0.2, 1.0);
    
    if (lighting == 0.0) color2 = light_intensity;

    float visibility = 1.1;
    vec3 n = normalize(N);
    vec3 l = normalize(L);
    float dnl = dot( n,l);
    
    float mct = dnl > 0.0 ? dnl : 0.0;
    float cosTheta = mct < 1.0 ? mct : 1.0;
    //float cosTheta = clamp( dot( n,l), 0,1 );
    float bias = 0.005*tan(acos(cosTheta)); // cosTheta is dot( n,l ), clamped between 0 and 1
    
    float mbias = bias > 0.0 ? bias : 0.0;
    bias = bias < 0.01 ? bias : 0.01;
    //bias = clamp(bias, 0,0.01);

    vec4 color = shadow2D( texture1, ShadowCoord.xyz );


    //if ( color.z  <  ShadowCoord.z-bias){
    //    visibility = 0.3;
    //}
    for (int i=0;i<4;i++){
      if ( shadow2D( texture1, vec3(ShadowCoord.xy + poissonDisk[i]/700.0, ShadowCoord.z) ).z  <  ShadowCoord.z-bias ){
        visibility-=0.15;
      }
    }

    if (enabled_shadow == 0.0) visibility = 1.0;
    float res_alpha = 1.0;
    res_alpha = color1.a;

    visibility += 0.4;
    if (edge >= 0.00){
        vec4 f_color;
        f_color = vec4((color1 * color2).xyz*visibility, res_alpha);
        gl_FragColor = f_color;
    }	
    else
        //gl_FragColor = vec4((color1 * color2).xyz*0.8, 1);
	gl_FragColor = vec4(0, 0, 0, 1.0);
    
    //if (visibility == 0.5)
    //	    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
	
    //gl_FragColor = color;
    //gl_FragColor = color1;
    

}

