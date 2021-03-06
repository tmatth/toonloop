/*
 * Toonloop
 *
 * Copyright (c) 2010 Alexandre Quessy <alexandre@quessy.net>
 * Copyright (c) 2010 Tristan Matthews <le.businessman@gmail.com>
 *
 * Toonloop is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Toonloop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the gnu general public license
 * along with Toonloop.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <GL/gl.h>
#include "draw.h"
/**
 * Draws a square of 2 x 2 size centered at 0, 0
 * 
 * Make sure to call glDisable(GL_TEXTURE_RECTANGLE_ARB) first.
 */
void draw::draw_square()
{
    glBegin(GL_QUADS);
    glVertex2f(-1.0, -1.0); // Bottom Left of Quad
    glVertex2f(1.0, -1.0); // Bottom Right of Quad
    glVertex2f(1.0, 1.0); // Top Right Of Quad
    glVertex2f(-1.0, 1.0); // Top Left Of Quad
    glEnd();
}

/**
 * Draws a texture square of 2 x 2 size centered at 0, 0
 * 
 * Make sure to call glEnable(GL_TEXTURE_RECTANGLE_ARB) first.
 * 
 * @param width: width of the image in pixels
 * @param height: height of the image in pixels
 */
// FIXME: should be float args
void draw::draw_textured_square(int width, int height)
{
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 0.0);
    glVertex2f(-1.0, -1.0); // Bottom Left
    glTexCoord2f(width, 0.0);
    glVertex2f(1.0, -1.0); // Bottom Right
    glTexCoord2f(width, height);
    glVertex2f(1.0, 1.0); // Top Right
    glTexCoord2f(0.0, height);
    glVertex2f(-1.0, 1.0); // Top Left
    glEnd();
}

/**
 * Draws a line between given points.
 */
void draw::draw_line(float from_x, float from_y, float to_x, float to_y)
{
    glBegin(GL_LINES);
    glVertex2f(from_x, from_y);
    glVertex2f(to_x, to_y);
    glEnd();
}

/**
 * Draws a texture square of 2 x 2 size centered at 0, 0
 * 
 * Make sure to call glEnable(GL_TEXTURE_RECTANGLE_ARB) first.
 * 
 * @param width: width of the image in pixels
 * @param height: height of the image in pixels
 */
void draw::draw_vertically_flipped_textured_square(float width, float height)
{
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, height);
    glVertex2f(-1.0, -1.0); // Bottom Left
    glTexCoord2f(width, height);
    glVertex2f(1.0, -1.0); // Bottom Right
    glTexCoord2f(width, 0.0);
    glVertex2f(1.0, 1.0); // Top Right
    glTexCoord2f(0.0, 0.0);
    glVertex2f(-1.0, 1.0); // Top Left
    glEnd();
}
