'''OpenGL extension REND.screen_coordinates

This module customises the behaviour of the 
OpenGL.raw.GL.REND.screen_coordinates to provide a more 
Python-friendly API

Overview (from the spec)
	
	    This extension allows the specification of screen coordinate vertex
	    data. Screen coordinate vertices completely bypass transformation,
	    texture generation, lighting and frustum clipping. It also allow for
	    fewer floating point computations to the performed by OpenGL.
	
	    If we get screen coordinate inputs then in order to perspectively
	    correct data (eg texture), the input data currently has to be
	    specified in one of the following manners
	
		1. Specify all the data normally
		   eg.
			  glTexture2T(s, t);
		   and the coordinates as
			  glVertex4T(x*w, y*w, z*w, w);
		or
		2. Divide each data by w
		   eg.
			  glTexture4T(s/w, t/w, r/w, q/w);
		   and the coordinates as
			  glVertex3T(x, y, z);
	
	    Most hardware already performs some form of correction of the
	    coordinate data with respect to the w term prior to interpolation.
	    This is normally in the form of a multiplication of the terms by the
	    inverse w. It would be much more efficient to simply specify screen
	    coordinates as shown in the following example
		   glTexture2T(s, t, r, q);
	    and the coordinates as
		   glVertex4T(x, y, z, w);
	    and allow the hardware to bring the interpolated terms into a linear
	    screen space.
	
	    Additionally if the application derives screen coordinates it is
	    also highly likely that the 1/w term may already be computed. So it
	    would be advantageous to be able to specify 1/w directly instead of
	    w in the input screen coordinates.
	
	    For hardware that linearly interpolates data, the hardware
	    interpolates the following data:
		s/w, t/w, r/w, q/w, x, y, z
	    If the input w represents the original 1/w, then the hardware can
	    avoid the division and instead interpolate:
		s*w, t*w, r*w, q*w, x, y, z
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/REND/screen_coordinates.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.REND.screen_coordinates import *
from OpenGL.raw.GL.REND.screen_coordinates import _EXTENSION_NAME

def glInitScreenCoordinatesREND():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION