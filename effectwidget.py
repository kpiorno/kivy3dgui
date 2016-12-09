'''EffectWidget
============

(highly experimental)

Experiment to make an EffectWidget, exposing part of the shader
pipeline so users can write and easily apply their own glsl effects.

Basic idea: Take implementation inspiration from shadertree example,
draw children to Fbo and apply custom shader to a RenderContext.

Effects
-------

An effect is a string representing part of a glsl fragment shader. It
must implement a function :code:`effect` as below::

    vec4 effect( vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
    {
        ...
    }

The parameters are:

- **color**: The normal colour of the current pixel (i.e. texture sampled at tex_coords)
- **texture**: The texture containing the widget's normal background
- **tex_coords**: The normal texture_coords used to access texture
- **coords**: The pixel indices of the current pixel.

The shader code also has access to two useful uniform variables,
:code:`time` containing the time (in seconds) since the program start,
and :code:`resolution` containing the shape (x pixels, y pixels) of
the widget.

'''

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.graphics import (RenderContext, Fbo, Color, Rectangle,
                           Translate, PushMatrix, PopMatrix,
                           ClearColor, ClearBuffers)
from kivy.base import EventLoop
from kivy.graphics.opengl import *
from kivy.graphics import *

Builder.load_string('''
<EffectWidget>:
    canvas:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            texture: self.texture
            pos: self.pos
            size: self.size
''')

shader_header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;
uniform sampler2D texture4;
uniform sampler2D texture5;
'''

shader_uniforms = '''
uniform vec2 resolution;
uniform float time;
'''

shader_footer_trivial = '''
void main (void){
     gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
}
'''

shader_footer_effect = '''
void main (void){
    vec4 normal_color = frag_color * texture2D(texture0, tex_coord0);
    vec4 effect_color = effect(normal_color, texture0, tex_coord0,
                               gl_FragCoord.xy);
    gl_FragColor = effect_color;
}
'''

effect_trivial = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    return color;
}
'''

effect_monochrome = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    float mag = 1.0/3.0 * (color.x + color.y + color.z);
    return vec4(mag, mag, mag, color.w);
}
'''

effect_red = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return vec4(color.x, 0.0, 0.0, 1.0);
}
'''

effect_green = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return vec4(0.0, color.y, 0.0, 1.0);
}
'''

effect_blue = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return vec4(0.0, 0.0, color.z, 1.0);
}
'''

effect_invert = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return vec4(1.0 - color.xyz, 1.0);
}
'''

effect_mix = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return vec4(color.z, color.x, color.y, 1.0);
}
'''

effect_flash = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    return color * abs(sin(time));
}
'''

effect_blur_h = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
   if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    float dt = 0.5 * 1.0 / resolution.x;
    vec4 sum = vec4(0.0);
    sum += texture2D(texture, vec2(tex_coords.x - 4.0*dt, tex_coords.y)) * 0.05;
    sum += texture2D(texture, vec2(tex_coords.x - 3.0*dt, tex_coords.y)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x - 2.0*dt, tex_coords.y)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x - dt, tex_coords.y)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.16;
    sum += texture2D(texture, vec2(tex_coords.x + dt, tex_coords.y)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x + 2.0*dt, tex_coords.y)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x + 3.0*dt, tex_coords.y)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x + 4.0*dt, tex_coords.y)) * 0.05;
    return sum;
}
'''

effect_blur_v = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    float dt = 0.5 * 1.0 / resolution.y;
    vec4 sum = vec4(0.0);
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 4.0*dt)) * 0.05;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 3.0*dt)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 2.0*dt)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - dt)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.16;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + dt)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 2.0*dt)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 3.0*dt)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 4.0*dt)) * 0.05;
    return sum;
}
'''

effect_postprocessing = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    vec2 q = tex_coords * vec2(1, -1);
    vec2 uv = 0.5 + (q-0.5);//*(0.9);// + 0.1*sin(0.2*time));

    vec3 oricol = texture2D(texture,vec2(q.x,1.0-q.y)).xyz;
    vec3 col;

    col.r = texture2D(texture,vec2(uv.x+0.003,-uv.y)).x;
    col.g = texture2D(texture,vec2(uv.x+0.000,-uv.y)).y;
    col.b = texture2D(texture,vec2(uv.x-0.003,-uv.y)).z;

    col = clamp(col*0.5+0.5*col*col*1.2,0.0,1.0);

    //col *= 0.5 + 0.5*16.0*uv.x*uv.y*(1.0-uv.x)*(1.0-uv.y);

    col *= vec3(0.8,1.0,0.7);

    col *= 0.9+0.1*sin(10.0*time+uv.y*1000.0);

    col *= 0.97+0.03*sin(110.0*time);

    float comp = smoothstep( 0.2, 0.7, sin(time) );
    //col = mix( col, oricol, clamp(-2.0+2.0*q.x+3.0*comp,0.0,1.0) );

    return vec4(col,1.0);
}
'''

effect_plasma = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

   float x = coords.x;
   float y = coords.y;
   float mov0 = x+y+cos(sin(time)*2.)*100.+sin(x/100.)*1000.;
   float mov1 = y / resolution.y / 0.2 + time;
   float mov2 = x / resolution.x / 0.2;
   float c1 = abs(sin(mov1+time)/2.+mov2/2.-mov1-mov2+time);
   float c2 = abs(sin(c1+sin(mov0/1000.+time)+sin(y/40.+time)+
                  sin((x+y)/100.)*3.));
   float c3 = abs(sin(c2+cos(mov1+mov2+c2)+cos(mov2)+sin(x/1000.)));
   return vec4( 0.5*(c1 + color.z), 0.5*(c2 + color.x),
                0.5*(c3 + color.y), 1.0);
}
'''

effect_pixelate = '''
vec4 effect(vec4 vcolor, sampler2D texture, vec2 texcoord, vec2 pixel_coords)
{
    if (texture2D(texture4, texcoord).x <= 0.50)
       return vcolor;

    vec2 pixelSize = 10.0 / resolution;

    vec2 xy = floor(texcoord/pixelSize)*pixelSize + pixelSize/2.0;

    return texture2D(texture, xy);
}
'''

effect_waterpaint = '''
/*
Themaister's Waterpaint shader

Placed in the public domain.

(From this thread: http://board.byuu.org/viewtopic.php?p=30483#p30483
PD declaration here: http://board.byuu.org/viewtopic.php?p=30542#p30542 )
modified by slime73 for use with love2d and mari0
*/


vec4 compress(vec4 in_color, float threshold, float ratio)
{
    vec4 diff = in_color - vec4(threshold);
    diff = clamp(diff, 0.0, 100.0);
    return in_color - (diff * (1.0 - 1.0/ratio));
}

vec4 effect( vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    if (texture2D(texture4, tex_coords).x <= 0.50)
       return color;

    vec2 textureSize = resolution;

    float x = 0.5 * (1.0 / textureSize.x);
    float y = 0.5 * (1.0 / textureSize.y);

    vec2 dg1 = vec2( x, y);
    vec2 dg2 = vec2(-x, y);
    vec2 dx = vec2(x, 0.0);
    vec2 dy = vec2(0.0, y);

    vec3 c00 = texture2D(texture, tex_coords - dg1).xyz;
    vec3 c01 = texture2D(texture, tex_coords - dx).xyz;
    vec3 c02 = texture2D(texture, tex_coords + dg2).xyz;
    vec3 c10 = texture2D(texture, tex_coords - dy).xyz;
    vec3 c11 = texture2D(texture, tex_coords).xyz;
    vec3 c12 = texture2D(texture, tex_coords + dy).xyz;
    vec3 c20 = texture2D(texture, tex_coords - dg2).xyz;
    vec3 c21 = texture2D(texture, tex_coords + dx).xyz;
    vec3 c22 = texture2D(texture, tex_coords + dg1).xyz;

    vec2 texsize = textureSize;

    vec3 first = mix(c00, c20, fract(tex_coords.x * texsize.x + 0.5));
    vec3 second = mix(c02, c22, fract(tex_coords.x * texsize.x + 0.5));

    vec3 mid_horiz = mix(c01, c21, fract(tex_coords.x * texsize.x + 0.5));
    vec3 mid_vert = mix(c10, c12, fract(tex_coords.y * texsize.y + 0.5));

    vec3 res = mix(first, second, fract(tex_coords.y * texsize.y + 0.5));
    vec4 final = vec4(0.26 * (res + mid_horiz + mid_vert) + 3.5 * abs(res - mix(mid_horiz, mid_vert, 0.5)), 1.0);

    final = compress(final, 0.8, 5.0);
    final.a = 1.0;

    return final;
}
'''

effect_fxaa = '''
vec4 effect( vec4 color, sampler2D buf0, vec2 texCoords, vec2 coords)
{
   if (texture2D(texture4, texCoords).x <= 0.50)
       return color;

    vec2 frameBufSize = resolution;

    float FXAA_SPAN_MAX = 8.0;
    float FXAA_REDUCE_MUL = 1.0/8.0;
    float FXAA_REDUCE_MIN = 1.0/128.0;

    vec3 rgbNW=texture2D(buf0,texCoords+(vec2(-1.0,-1.0)/frameBufSize)).xyz;
    vec3 rgbNE=texture2D(buf0,texCoords+(vec2(1.0,-1.0)/frameBufSize)).xyz;
    vec3 rgbSW=texture2D(buf0,texCoords+(vec2(-1.0,1.0)/frameBufSize)).xyz;
    vec3 rgbSE=texture2D(buf0,texCoords+(vec2(1.0,1.0)/frameBufSize)).xyz;
    vec3 rgbM=texture2D(buf0,texCoords).xyz;

    vec3 luma=vec3(0.299, 0.587, 0.114);
    float lumaNW = dot(rgbNW, luma);
    float lumaNE = dot(rgbNE, luma);
    float lumaSW = dot(rgbSW, luma);
    float lumaSE = dot(rgbSE, luma);
    float lumaM  = dot(rgbM,  luma);

    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

    vec2 dir;
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
    dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));

    float dirReduce = max(
        (lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * FXAA_REDUCE_MUL),
        FXAA_REDUCE_MIN);

    float rcpDirMin = 1.0/(min(abs(dir.x), abs(dir.y)) + dirReduce);

    dir = min(vec2( FXAA_SPAN_MAX,  FXAA_SPAN_MAX),
          max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX),
          dir * rcpDirMin)) / frameBufSize;

    vec3 rgbA = (1.0/2.0) * (
        texture2D(buf0, texCoords.xy + dir * (1.0/3.0 - 0.5)).xyz +
        texture2D(buf0, texCoords.xy + dir * (2.0/3.0 - 0.5)).xyz);
    vec3 rgbB = rgbA * (1.0/2.0) + (1.0/4.0) * (
        texture2D(buf0, texCoords.xy + dir * (0.0/3.0 - 0.5)).xyz +
        texture2D(buf0, texCoords.xy + dir * (3.0/3.0 - 0.5)).xyz);
    float lumaB = dot(rgbB, luma);

    vec4 return_color;
    if((lumaB < lumaMin) || (lumaB > lumaMax)){
        return_color = vec4(rgbA, color.w);
    }else{
        return_color = vec4(rgbB, color.w);
    }

    return return_color;
}
'''

effect_bloom = '''
vec4 effect( vec4 color, sampler2D bgl_RenderedTexture, vec2 texcoord, vec2 coords)
{
   if (texture2D(texture4, texcoord).x <= 0.50)
       return color;

   vec4 sum = vec4(0);
   vec4 return_color;
   //vec2 texcoord = vec2(gl_TexCoord[0]);
   int j;
   int i;
   //float glow_threshold = 0.25;
   float glow_threshold = 0.23;
   //float r_color = texture2D(texture4, texcoord).x;

   for( i= -4 ;i < 4; i++)
   {
        for (j = -3; j < 3; j++)
        {
            sum += texture2D(bgl_RenderedTexture, texcoord + vec2(j, i)*0.004) * glow_threshold;
        }
   }
       if (texture2D(bgl_RenderedTexture, texcoord).r < 0.3)
    {
       return_color = sum*sum*0.012 + texture2D(bgl_RenderedTexture, texcoord);
    }
    else
    {
        if (texture2D(bgl_RenderedTexture, texcoord).r < 0.5)
        {
            return_color = sum*sum*0.009 + texture2D(bgl_RenderedTexture, texcoord);
        }
        else
        {
            return_color = sum*sum*0.0075 + texture2D(bgl_RenderedTexture, texcoord);
        }
    }
    return_color.a = 1.0;
    return return_color;
}
'''

effect_dop = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    //if (texture2D(texture4, tex_coords).x <= 0.50)
    //   return color;
    float value = 0.5;
    float depth = texture2D(texture5, tex_coords).z;
    value = 4.0 * (1.0 - depth);
    value = 2.5-((1.0-depth)*500.0);
    //value = 2.0 - depth*3.0;
    //if (value < 4.0) value = 0.0;
    //if (value > 5.0) value = 5.0;
    if (depth < 1.0) value = 0.0;
    //value = -30.0 + depth*20.0;
    value = (depth)*4.0;
    float dt = value * 1.0 / resolution.x;
    vec4 sum = vec4(0.0);
    sum += texture2D(texture, vec2(tex_coords.x - 4.0*dt, tex_coords.y)) * 0.05;
    sum += texture2D(texture, vec2(tex_coords.x - 3.0*dt, tex_coords.y)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x - 2.0*dt, tex_coords.y)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x - dt, tex_coords.y)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.16;
    sum += texture2D(texture, vec2(tex_coords.x + dt, tex_coords.y)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x + 2.0*dt, tex_coords.y)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x + 3.0*dt, tex_coords.y)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x + 4.0*dt, tex_coords.y)) * 0.05;
    return sum;
}
'''
effect_dop_v = '''
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    //if (texture2D(texture4, tex_coords).x <= 0.50)
    //   return color;
    float value = 0.5;
    float depth = texture2D(texture5, tex_coords).z;
    value = 4.0 * (1.0 - depth);
    value = 2.5-((1.0-depth)*500.0);
    //value = 2.0 - (depth)*3.0;
    //if (value < 4.0) value = 0.0;
    //if (value > 5.0) value = 5.0;
    if (depth < 1.0) value = 0.0;
    //value = -30.0 + depth*20.0;
    value = (depth)*4.0;
    float dt = value * 1.0 / resolution.x;

    vec4 sum = vec4(0.0);
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 4.0*dt)) * 0.05;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 3.0*dt)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 2.0*dt)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - dt)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.16;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + dt)) * 0.15;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 2.0*dt)) * 0.12;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 3.0*dt)) * 0.09;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 4.0*dt)) * 0.05;
    return sum;
}
'''
effect_motion = '''
vec4 effect(vec4 color, sampler2D motion, vec2 uv, vec2 uv2)
{
  //if (texture2D(texture4, uv).x <= 0.50)
  //    return color;
  //vec2 speed = 2. * texture2D(texture5, uv).rg - 1.;
  vec3 speedInfo = texture2D(texture5, uv).rgb;
  vec2 speed = (2. * speedInfo.xy - 1.) * pow(speedInfo.z, 2.);
  float intensity = 0.13;
  vec2 offset = intensity * speed;
  vec3 c = vec3(0.);

  float inc = 0.05;
  float weight = 0.;
  for (float i = 0.; i <= 1.; i += inc)
  {
    c += texture2D(motion, uv + i * offset).rgb;
    weight += 1.;
  }
  c /= weight;
  return vec4(c, 1.);
  return vec4(1);
}
'''


effect_bloom_b = '''
vec4 effect( vec4 color, sampler2D bgl_RenderedTexture, vec2 texcoord, vec2 coords)
{
   //if (texture2D(texture4, texcoord).x <= 0.50)
   //    return color;

   vec4 sum = vec4(0);
   vec4 return_color;
   //vec2 texcoord = vec2(gl_TexCoord[0]);
   int j;
   int i;
   //float glow_threshold = 0.25;
   float glow_threshold = 0.10;
   //float glow_threshold = time/10.0;
   //float r_color = texture2D(texture4, texcoord).x;

   for( i= -4 ;i < 4; i++)
   {
        for (j = -3; j < 3; j++)
        {
            sum += texture2D(bgl_RenderedTexture, texcoord + vec2(j, i)*0.004) * glow_threshold;
        }
   }
       if (texture2D(bgl_RenderedTexture, texcoord).r < 0.3)
    {
       return_color = sum*sum*0.012 + texture2D(bgl_RenderedTexture, texcoord);
    }
    else
    {
        if (texture2D(bgl_RenderedTexture, texcoord).r < 0.5)
        {
            return_color = sum*sum*0.009 + texture2D(bgl_RenderedTexture, texcoord);
        }
        else
        {
            return_color = sum*sum*0.0075 + texture2D(bgl_RenderedTexture, texcoord);
        }
    }
    return_color.a = 1.0;
    return return_color;
}
'''
C_SIZE = (1366, 768)

class EffectFbo(Fbo):
    def __init__(self, *args, **kwargs):
        super(EffectFbo, self).__init__(*args, **kwargs)
        self.texture_rectangle = None

    def set_fs(self, value):
        # set the fragment shader to our source code
        shader = self.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')


class EffectWidget(FloatLayout):

    fs = StringProperty(None)

    # Texture of the final Fbo
    texture = ObjectProperty(None)

    # Rectangle clearing Fbo
    fbo_rectangle = ObjectProperty(None)

    # List of effect strings
    effects = ListProperty([])

    # One extra Fbo for each effect
    fbo_list = ListProperty([])

    effect_mask = None
    motion_effect = None

    def __init__(self, **kwargs):
        # Make sure opengl context exists
        EventLoop.ensure_window()
        self.mask_effect = kwargs.get("mask_effect", None)
        self.motion_effect = kwargs.get("motion_effect", None)

        self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True)

        self.size = C_SIZE
        with self.canvas:
            #self._viewport = Rectangle(size=(800,600), pos=self.pos)
            self.fbo = Fbo(size=C_SIZE, with_depthbuffer=True,  compute_normal_mat=True,
                           clear_color=(0.3, 0.3, 0.7, 1))

        with self.fbo.before:
            #Rectangle(size=(800, 600))
            PushMatrix()
            self.fbo_translation = Translate(-self.x, -self.y, 0)
            BindTexture(texture=self.mask_effect.texture, index=4)
            BindTexture(texture=self.motion_effect.texture, index=5)

        with self.fbo:
            Color(0, 0, 0)
            BindTexture(texture=self.mask_effect.texture, index=4)
            BindTexture(texture=self.motion_effect.texture, index=5)
            self.fbo_rectangle = Rectangle(size=C_SIZE)
            self._instructions = InstructionGroup()

        with self.fbo.after:
            PopMatrix()
            self.cbs = Callback(self.reset_gl_context)


        super(EffectWidget, self).__init__(**kwargs)
        self.size = C_SIZE

        Clock.schedule_interval(self.update_glsl, 0)

        self._instructions.add(Callback(self.setup_gl_context))

        self.refresh_fbo_setup()
        Clock.schedule_interval(self.update_fbos, 0)

    def on_pos(self, *args):
        self.fbo_translation.x = -self.x
        self.fbo_translation.y = -self.y

    def on_size(self, instance, value):
        self.fbo.size = C_SIZE
        self.fbo_rectangle.size = C_SIZE
        self.refresh_fbo_setup()

        #self._viewport.texture = self.fbo.texture
        #self._viewport.size = value


    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)
        self.fbo.clear_buffer()

        #for fbo in self.fbo_list:
        #    fbo.clear_buffer()

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        time = Clock.get_boottime()
        resolution = [float(size) for size in C_SIZE]
        self.canvas['time'] = time
        self.canvas['resolution'] = resolution
        self.canvas['texture4'] = 4
        self.canvas['texture5'] = 5
        for fbo in self.fbo_list:
            fbo['time'] = time
            fbo['resolution'] = resolution
            fbo['texture4'] = 4
            fbo['texture5'] = 5


    def on_effects(self, *args):
        self.refresh_fbo_setup()

    def update_fbos(self, *args):
        for fbo in self.fbo_list:
            fbo.ask_update()

    def refresh_fbo_setup(self, *args):
        # Add/remove fbos until there is one per effect
        while len(self.fbo_list) < len(self.effects):
            with self.canvas:
                new_fbo = EffectFbo(size=C_SIZE)
            with new_fbo:
                Color(1, 1, 1, 1)
                new_fbo.texture_rectangle = Rectangle(
                    size=C_SIZE)

                new_fbo.texture_rectangle.size = C_SIZE
            self.fbo_list.append(new_fbo)
        while len(self.fbo_list) > len(self.effects):
            old_fbo = self.fbo_list.pop()
            self.canvas.remove(old_fbo)

        # Do resizing etc.
        self.fbo.size = C_SIZE
        self.fbo_rectangle.size = C_SIZE
        for i in range(len(self.fbo_list)):
            self.fbo_list[i].size = C_SIZE
            self.fbo_list[i].texture_rectangle.size = C_SIZE

        # If there are no effects, just draw our main fbo
        if len(self.fbo_list) == 0:
            self.texture = self.fbo.texture
            return

        for i in range(1, len(self.fbo_list)):
            fbo = self.fbo_list[i]
            fbo.texture_rectangle.texture = self.fbo_list[i - 1].texture

        for effect, fbo in zip(self.effects, self.fbo_list):
            fbo.set_fs(shader_header + shader_uniforms + effect +
                       shader_footer_effect)

        self.fbo_list[0].texture_rectangle.texture = self.fbo.texture
        self.texture = self.fbo_list[-1].texture

    def on_fs(self, instance, value):
        # set the fragment shader to our source code
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def add_widget(self, widget):
        # Add the widget to our Fbo instead of the normal canvas
        c = self.canvas
        self.canvas = self.fbo
        super(EffectWidget, self).add_widget(widget)
        #self._instructions.add(widget.canvas)
        self.canvas = c

    def remove_widget(self, widget):
        # Remove the widget from our Fbo instead of the normal canvas
        c = self.canvas
        self.canvas = self.fbo
        super(EffectWidget, self).remove_widget(widget)
        self.canvas = c

    def clear_widgets(self, children=None):
        # Clear widgets from our Fbo instead of the normal canvas
        c = self.canvas
        self.canvas = self.fbo
        super(EffectWidget, self).clear_widgets(children)
        self.canvas = c


class BlurEffectWidget(EffectWidget):
    #effects = ListProperty([effect_fxaa])
    #effects = ListProperty([effect_bloom_b, effect_fxaa,  effect_dop])
    effects = ListProperty([effect_fxaa, effect_bloom_b])
    #effects = ListProperty([effect_motion])
    #effects = ListProperty()
