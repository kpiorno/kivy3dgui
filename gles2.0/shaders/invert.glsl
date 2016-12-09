---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

$HEADER$
void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

$HEADER$
void main (void){
    //vec3 col = vec3(1.0, 1.0, 1.0) - (frag_color * texture2D(texture0, tex_coord0)).xyz;
    vec4 col = (frag_color * texture2D(texture0, tex_coord0));
    vec4 final_color = vec4(1.0 - col.xyz, col.a);
    //vec4 final_color = vec4(col.xyz, col.a);


    if (final_color.a < 0.1)
       final_color = vec4(0.0, 0.0, 0.0, 0.0);
    //final_color.a += 0.0004;   
    gl_FragColor = final_color;
}
