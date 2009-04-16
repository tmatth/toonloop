#!/usr/bin/env python
"""
GLSL shaders with SDL, OpenGL texture and Python
"""
import os
import sys
import pygame
import pygame.image
import pygame.camera
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from rats.glsl import ShaderProgram
from rats.glsl import ShaderError

# ---------------------------- glsl vertex shader ----------------------------
vert = """
// Does the standard action a vertex shader should do.
// Passes texcoord to the fragment shader.
//varying vec2 texcoord;

void main (void)
{
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = ftransform();

    //texcoord = vec2(gl_TextureMatrix[0] * gl_MultiTexCoord0);
}
"""
# ---------------------------- glsl fragment shader ----------------------------
frag = """
//varying vec2 texcoord;
uniform sampler2DRect image;
//uniform sampler2D image;

void main (void)
{
    //vec3 texColor = texture2DRect(image, texcoord).bgr;
    //gl_FragColor = texture2D(image, gl_TexCoord[0].st).gbra;
    gl_FragColor = texture2DRect(image, gl_TexCoord[0].st).gbra;
}
"""

def set_program_uniforms():
    global program
    program.glUniform1i("image", 0)
    pass


textures = [0] # list of texture ID 
program = None

def resize((width, height)):
    """
    Called when we resize the window.
    (fullscreen on/off)
    """
    if height == 0:
        height = 1
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-4.0, 4.0, -3.0, 3.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def gl_init():
    """
    Init the window
    """
    global program 
    global textures

    glEnable(GL_TEXTURE_RECTANGLE_ARB) 
    glShadeModel(GL_SMOOTH)
    textures[0] = glGenTextures(1)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1., 1., 1.)

    program = ShaderProgram()
    program.add_shader_text(GL_VERTEX_SHADER_ARB, vert)
    program.add_shader_text(GL_FRAGMENT_SHADER_ARB, frag)
    program.linkShaders()

def draw():
    """
    Called on every frame rendering
    """
    global program 
    global textures
    
    # w = 1; h = 1
    w = 640.0
    h = 480.0

    program.enable()
    set_program_uniforms()
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(-4.0, -3.0) # Bottom Left
    glTexCoord2f(w, 0.0)
    glVertex2f(4.0, -3.0) # Bottom Right
    glTexCoord2f(w, h)
    glVertex2f(4.0, 3.0) # Top Right
    glTexCoord2f(0.0, h)
    glVertex2f(-4.0, 3.0) # Top Left
    glEnd()
    glPopMatrix()

    program.disable()
    glPushMatrix()
    glTranslate(2, 1.5, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(-1.333, -1.) # Bottom Left
    glTexCoord2f(w, 0.0)
    glVertex2f(1.333, -1.) # Bottom Right
    glTexCoord2f(w, h)
    glVertex2f(1.333, 1.) # Top Right
    glTexCoord2f(0.0, h)
    glVertex2f(-1.333, 1.) # Top Left
    glEnd()
    glPopMatrix()

class VideoCapturePlayer(object):
    size = (640, 480)
    def __init__(self, **argd):
        self.__dict__.update(**argd)
        super(VideoCapturePlayer, self).__init__(**argd)

        # create a display surface. standard pygame stuff
        self.screen = pygame.display.set_mode(self.size, OPENGL | DOUBLEBUF | HWSURFACE)
        pygame.display.set_caption("GLCamera")
        resize(self.size)
        gl_init()

        # gets a list of available cameras.
        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        
        if os.uname()[0] == 'Darwin':
            self.isMac = True
            # creates the camera of the specified size and in RGB colorspace
            self.camera = pygame.camera.Camera(0, self.size, 'RGBA')
        else:
            self.isMac = False
            # creates the camera of the specified size and in RGB colorspace
            self.camera = pygame.camera.Camera('/dev/video0', self.size, "RGBA")

    
        # starts the camera
        self.camera.start()
        self.clock = pygame.time.Clock()

        # create a surface to capture to.  for performance purposes, you want the
        # bit depth to be the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.screen)

    def get_and_flip(self):
        """
        Grabs a frame from the camera (to a texture) and renders the screen.

        if you don't want to tie the framerate to the camera, you can check and
        see if the camera has an image ready.  note that while this works
        on most cameras, some will never return true.
        """
        global textures

        if 0 and self.camera.query_image():
            # capture an image
            self.snapshot = self.camera.get_image(self.snapshot)
        
        self.snapshot = self.camera.get_image(self.snapshot)
        textureData = pygame.image.tostring(self.snapshot, "RGBX", 1)
    
        glActiveTexture(GL_TEXTURE0) # IMPORTANT ! sets the texture unit to 0. 
        glBindTexture(GL_TEXTURE_RECTANGLE_ARB, textures[0]) # GL_TEXTURE_2D
        glTexImage2D(GL_TEXTURE_RECTANGLE_ARB, 0, GL_RGBA, self.snapshot.get_width(), self.snapshot.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, textureData )
        glTexParameterf(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, GL_NEAREST) # GL_TEXTURE_RECTANGLE_ARB
        glTexParameterf(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        draw()
        pygame.display.flip()
    
    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    going = False
                elif e.type == KEYDOWN:
                    if e.key == K_f:
                        pygame.display.toggle_fullscreen()

            self.get_and_flip()
            self.clock.tick(30)
            #print "FPS:", self.clock.get_fps()

def main():
    pygame.init()
    pygame.camera.init()
    VideoCapturePlayer().main()
    pygame.quit()

if __name__ == '__main__':
    main()


# frag = """
# /**
#  * Fragment shader for chroma-keying. 
#  * :author: Alexandre Quessy <alexandre@quessy.net> 2009
#  * :license: GNU Public License version 3
#  * Main thing is, make sure the texcoord's arent 
#  * normalized (so they are in the range of [0..w, 0..h] )
#  * :param keying_color: The RGB keying color that will be made transparent.
#  * :param thresh: The distance from the color for a pixel to disappear.
#  */
# // user-configurable variables (read-only)
# //uniform vec3 keying_color;
# //uniform vec3 thresh; 
# const vec3 keying_color = vec3(0., 1., 0.);
# const vec3 thresh = vec3(0.2, 0.2, 0.2);
# 
# // the texture
# uniform sampler2DRect image;
# 
# // data passed from vertex shader:
# //varying vec2 texcoord0;
# //varying vec2 texdim0;
# 
# void main(void)
# {
#   // sample from the texture 
#   //gl_FragColor.rgba = vec4(texture2DRect(image, gl_TexCoord[0].xy).rgb, 1.0);
# 
#   vec3 input_color = texture2DRect(image, gl_TexCoord[0].xy);
#   float output_alpha = 0.8;
# 
#   //vec3 input_color = texture2DRect(image, texcoord0).rgb;
#   //    float output_alpha = 1.0;
#   //  
#   //    // measure distance from keying_color
#   //    vec3 delta = abs(input_color - keying_color);
#   //    
#   //    // for now, not visible if under threshold of proximity
#   //    // TODO: mix() according the 3 factors of proximity.
#   //    if (delta.r <= thresh.r && delta.g <= thresh.g && delta.b <= thresh.b)
#   //    {
#   //       output_alpha = 0.5;
#   //    }
#   //    
#     gl_FragColor.rgba = vec4(input_color, output_alpha); 
# }
# """