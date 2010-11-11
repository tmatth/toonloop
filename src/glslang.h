#ifndef __GLSLANG_H__
#define __GLSLANG_H__
#include <clutter/clutter.h>

/**
 * Utilities to load and use GLSL shaders in Clutter.
 */

// TODO:2010-11-10:aalex:Actually use this file.

gboolean toon_load_fragment_source_file(ClutterShader *shader, gchar *file_name)
gchar *toon_find_shader_file(const gchar *file_name)

#endif
