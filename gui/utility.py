"""
Copyright (C) 2020, Michael C Palmer <michaelcpalmer1980@gmail.com>

This file is part of pySDL2gui

pySDLgui is a simple, low level gui module that handles input and draws multiple
rectangular Regions using hardware GPU rendering. Written in python, pySDLgui
uses pySDL2, a low level SDL2 wrapper also written in pure python with no other
dependencies.

This module is designed to produce full screen GUIs for lower powered
GNU/Linux based retro handhelds using game controller style input, but it may
prove useful on other hardware.

The main building block of GUIs built with this module is the Region, which
represents a rectangular area that can display text, lists, and images. Each
Region has numerous attributes that should be defined in theme.json or
defaults.json and can be used to change the look and feel of a GUI without
change the program's code.

CLASSES:
    FontManager: class used to load and render fonts onto a pySDL
        render context
    Image: simple class to represent and draw textures and subtexture
        regions onto a pySDL render context
    ImageManager: class to load and cache images as Image objects in
        texture memory
    Rect: class used to represent and modify Rectangular regions
    SoundManager: class used to load and play sound effects and music

FUNCTIONS:
    deep_merge: used internally to merge option dicts
    deep_print: available to display nested dict items or save them to disk
    deep_update: used internally to update an options dict from a second one
    get_color_mod: get the color_mod value of a texture (not working)
    get_text_size: get the size a text string would be if drawn with given font
    range_list: generate a list of numerical values to select from in a option
        menu, similar to a slider widget
    set_color_mod: set the color_mod value of a texture (not working)
    set_globals: sets the modules global values within this file's scope

pySDL2gui is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
pytmx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public
License along with pySDL2gui.

If not, see <http://www.gnu.org/licenses/>.
"""

from ctypes import c_int, c_ubyte, byref
import sdl2, sdl2.ext
import os
global RESOURCES, sounds
RESOURCES = sdl2.ext.Resources(__file__, '../assets')

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rect:
    POINTS = ('topleft midtop topright midleft center midright '+
              'bottomleft midbottom bottomright').split()
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
    def __repr__(self):
        return f'Rect({self.x},{self.y},{self.width},{self.height})'
    
    def __mul__(self, v):
        'Scale by v keeping center in position'
        cx, cy = self.center
        r = Rect(self.x, self.y, self.width, self.height)
        r.width = int(r.width*v)
        r.height = int(r.height*v)
        r.center = cx, cy
        return r

    def copy(self):
        'Returns a copy of the called Rect object'
        return Rect(self.x, self.y, self.width, self.height)    

    def fit(self, other):
        'Move and resize myself to fill other rect maintaining aspect ratio'
        r = self.fitted(other)
        self.x = r.x; self.width = r.width
        self.y = r.y; self.height = r.height

    def fitted(self, other):
        '''
        Return new Rect with other centered and resized to fill self.
        Aspect ration is retained'''
        xr = self.width / other.width
        yr = self.height / other.height
        mr = xr if yr < xr else yr

        w = int(self.width / mr)
        h = int(self.height / mr)
        x = int(other.x + (other.width - w) / 2)
        y = int(other.y + (other.height - h) / 2)
        return Rect(x, y, w, h)

    def from_corners(x, y, x2, y2):
        '''
        Creat a new rect using bottom and right coordinates instead
        of width and height'''
        return Rect(x, y, x2-x, y2-y)
    def from_sdl(r):
        '''
        Create a new rect based on the position and size of an sdl_rect
        object'''
        return Rect(r.x, r.y, r.w, r.h)

    def inflate(self, x, y=None):
        '''
        Add x to width and y to height of rect, or x to both.
        The rect will remain centered around the same point'''
        y = y if y != None else x
        self.x -= x // 2
        self.y -= y // 2
        self.width += x
        self.height += y
    def inflated(self, x, y=None):
        '''
        Return a copy of self with x added to the width and y to the
        height of rect, or x to both. The rect will remain centered
        around the same point'''
        y = y if y != None else x
        nx = self.x - x // 2
        ny = self.y - y // 2
        nw = self.width + x
        nh = self.height + y
        return Rect(nx, ny, nw, nh)
    
    def move(self, x, y):
        'Move self by x/y pixels'
        self.x += x
        self.y += y
    def moved(self, x, y):
        'Return copy of self moved by x/y pixels'
        return Rect(
            self.x + x, self.y + y,
            self.width, self.height)

    def sdl(self):
        'Return my value as an sdl_rect'
        return sdl2.SDL_Rect(self.x, self.y, self.width, self.height)
    def tuple(self):
        'Return my value as a 4-tuple'
        return self.x, self.y, self.width, self.height

    def update(self, x, y, w, h):
        'Update myself with new position and size'
        self.x = x; self.width = w
        self.y = y; self.height = h

    def clip(self, other):
        'Return copy of self cropped to fit inside other Rect'
        # LEFT
        if self.x >= other.x and self.x < other.x + other.width:
            x = self.x
        elif other.x >= self.x and other.x < self.x + self.width:
            x = other.x
        else:
            return Rect(self.x, self.y, 0,0)

        # RIGHT
        if self.x + self.width > other.x and self.x + self.width <= other.x + other.width:
            w = self.x + self.width - x
        elif other.x + other.width > self.x and other.x + other.width <= self.x + self.width:
            w = other.x + other.width - x
        else:
            return Rect(self.x, self.y, 0,0)

        # TOP
        if self.y >= other.y and self.y < other.y + other.height:
            y = self.y
        elif other.y >= self.y and other.y < self.y + self.height:
            y = other.y
        else:
            return Rect(self.x, self.y, 0,0)

        # BOTTOM
        if self.y + self.height > other.y and self.y + self.height <= other.y + other.height:
            h = self.y + self.height - y
        elif other.y + other.height > self.y and other.y + other.height <= self.y + self.height:
            h = other.y + other.height - y
        else:
            return Rect(self.x, self.y, 0,0)

        return Rect(x, y, w, h)

    @property
    def w(self):
        return self.width
    @w.setter
    def w(self, v):
        self.width = v
        self.x -= v//2
    @property
    def h(self):
        return self.height
    @h.setter
    def h(self, v):
        self.height = v
        self.y -= v//2

    # EDGES
    @property
    def top(self):
        return self.y
    @top.setter
    def top(self, v):
        self.y = v

    @property
    def bottom(self):
        return self.y + self.height
    @bottom.setter
    def bottom(self, v):
        self.y = v - self.height

    @property
    def left(self):
        return self.x
    @left.setter
    def left(self, v):
        self.x = v

    @property
    def right(self):
        return self.x + self.width
    @right.setter
    def right(self, v):
        self.x = v - self.width

    @property
    def centerx(self):
        return self.x + self.width//2
    @centerx.setter
    def centerx(self, v):
        self.x = v - self.width//2
    @property
    def centery(self):
        return self.y + self.height//2
    @centery.setter
    def centery(self, v):
        self.y = v - self.height//2

    # FIRST ROW
    @property
    def topleft(self):
        return self.x, self.y
    @topleft.setter
    def topleft(self, v):
        x, y = v
        self.x = x
        self.y = y
    @property
    def midtop(self):
        return self.x+self.width//2, self.y
    @midtop.setter
    def midtop(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y
    @property
    def topright(self):
        return self.x + self.width, self.y
    @topright.setter
    def topright(self, v):
        x, y = v
        self.x = x - self.width
        self.y = y

    # SECOND ROW
    @property
    def midleft(self):
        return self.x, self.y + self.height//2
    @midleft.setter
    def midleft(self, v):
        x, y = v
        self.x = x
        self.y = y - self.height//2

    @property
    def center(self):
        return self.x + (self.width//2), self.y + (self.height//2)
    @center.setter
    def center(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y - self.height//2

    @property
    def midright(self):
        return self.x+self.width, self.y + self.height//2
    @midright.setter
    def midright(self, v):
        x, y = v
        self.x = x - self.width
        self.y = y - self.height//2
    
    # THIRD ROW
    @property
    def bottomleft(self):
        return self.x, self.y + self.height
    @bottomleft.setter
    def bottomleft(self, v):
        x, y = v
        self.x = x
        self.y = y - self.height
    @property
    def midbottom(self):
        return self.x+self.width//2, self.y+self.height
    @midbottom.setter
    def midbottom(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y - self.height
    @property
    def bottomright(self):
        return self.x+self.width, self.y+self.height
    @bottomright.setter
    def botomright(self, v):
        x, y = v
        self.x = x - self.width
        self.y = y - self.height

    @property
    def size(self):
        return self.width, self.height
    @size.setter
    def size(self, v):
        cx, cy = self.center
        self.width, self.height = v
        self.center = cx, cy
   
class Image():
    renderer = None
    '''
    The Image class represents an image with its position, angle,
    and flipped(x/y) status. An image references a Texture and
    has a srcrect(Rect) to define which part of the Texture to
    draw'''
    def __init__(self, texture, srcrect=None, renderer=None):
        '''
        Create a new Image from a texture and a source Rect.

        :param texture: a sdl2.ext.Texture object to draw the image from
        :param srcrect: a gui.Rect object defining which part of the
            texture to draw
        :param renderer: a sdl2.ext.Renderer context to draw into
        '''
        renderer = renderer or Image.renderer
        if not renderer:
            raise Exception('No renderer context provided')
        Image.renderer = Image.renderer or renderer # set default

        self.texture = texture
        if isinstance(srcrect, Rect):
            self.srcrect = srcrect.sdl()
        elif isinstance(srcrect, (list, tuple)) and len(srcrect)==4:
            self.srcrect = sdl2.SDL_Rect(*srcrect)
        elif isinstance(srcrect, (sdl2.SDL_Rect)):
            self.srcrect =srcrect
        elif srcrect == None:
            self.srcrect = sdl2.SDL_Rect(0,0, *texture.size)
        else:
            raise Exception('srcrect not a supported type')

        self.x = self.y = 0
        self.flip_x = self.flip_y = 0
        self.angle = 0
        self.center = self.srcrect.w//2, self.srcrect.h//2

        # default dest rect is fitted to full screen
        self.dstrect = Rect.from_sdl(self.srcrect).fitted(
                    Rect(0,0, *self.renderer.logical_size)).sdl()

   
    def draw_at(self, x, y, angle=0, flip_x=None, flip_y=None, center=None):
        '''
        Draw image with topleft corner at x, y and at the original size.

        x: x position to draw at
        y: y position to draw at
        angle: optional angle to rotate image
        flip_x: optional flag to flip image horizontally
        flip_y: optional flag to flip image vertically
        center: optional point to rotate the image around if angle provided        
        '''
        center = center or self.center
        angle = angle or self.angle
        if flip_x == None and flip_y == None:
            flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        else:
            flip = 1 * bool(flip_x) | 2 * bool(flip_y)

        self.renderer.copy(self.texture, self.srcrect,
                dstrect=(x, y), angle=angle, flip=flip, center=center)

    def draw_in(self, dest, angle=0, flip_x=None, flip_y=None,
                center=None, fit=False):
        '''
        Draw image inside given Rect region (may squish or stretch image)

        dest: Rect area to draw the image into
        angle: optional angle to rotate image
        flip_x: optional flag to flip image horizontally
        flip_y: optional flag to flip image vertically
        center: optional point to rotate the image around if angle provided
        fit: set true to fit the image into dest without changing its aspect
             ratio    
        '''
        center = center or self.center
        angle = angle or self.angle

        if fit:
            dest = self.srcrect.fitted(dest)
        if flip_x == None and flip_y == None:
            flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        else:
            flip = 1 * bool(flip_x) | 2 * bool(flip_y)

        self.renderer.copy(self.texture, self.srcrect,
                dstrect=dest, angle=angle, flip=flip, center=center)

    def draw(self):
        ''''Draw image to its current destrect(Rect region), which defaults to
        full screen maintaining aspect ratio'''
        flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        self.renderer.copy(self.texture, self.srcrect, 
                dstrect=self.dstrect, angle=self.angle,
                flip=flip, center=self.center)

class ImageManager():
    '''
    The ImageManager class loads images into Textures and caches them for later use
    '''
    MAX_IMAGES = 20 # maximum number of images to cache
    def __init__(self, screen, max=None):
        '''
        Create a new Image manager that can load images into textures
        
        screen: sdl2.ext.Renderer context that the image will draw
            into. A renderer must be provided to create new Texture
            objects.
        max: maximum number of images to cach before old ones are
            unloaded. Defaults to ImageManager.MAX_IMAGES(20) 
        '''
        self.MAX_IMAGES = max or ImageManager.MAX_IMAGES
        self.screen = screen
        self.images = {}
        self.textures = {}
        self.cache = []
    
    def load(self, fn):
        '''
        Load an image file into a Texture or receive a previously cached
        Texture with that name.
        
        :param fn: filename(str) to load
        :rvalue gui.Image: reference to the image just loaded or from cache
        '''
        if fn in self.cache:
            i = self.cache.index(fn)
            self.cache.insert(0, self.cache.pop(i))
            return self.images[fn]
        elif fn in self.images:
            return self.images[fn]

        elif isinstance(fn, str):
            try:
                if os.path.exists(fn):
                    surf = sdl2.ext.image.load_img(fn)
                else:
                    surf = sdl2.ext.image.load_img(RESOURCES.get_path(fn))
            except:
                return
            texture = sdl2.ext.renderer.Texture(self.screen, surf)
            self.textures[fn] = texture
            self.images[fn] = Image(texture)
            self.cache.insert(0, fn)
            self._clean()
            return self.images[fn]
        
    def load_atlas(self, fn, atlas):
        '''
        Load image fn, create Images from an atlas dict, and create
        a named shortcut for each image in the atlas.

        :param fn: (str) filename of image to load into a texture
        :param atlas: a dict representing each image in the file
        :rvalue {}: dict of gui.Images in {name: Image} format

        example atlas:
        atlas = {
            'str_name': (x, y, width, height),
            'another_img: (32, 0, 32, 32)
        }
        '''
        images = {}
        if os.path.exists(fn):
            surf = sdl2.ext.image.load_img(fn)
        else:
            surf = sdl2.ext.image.load_img(RESOURCES.get_path(fn))
        texture = sdl2.ext.renderer.Texture(self.screen, surf)

        for name, item in atlas.items():
            r = item[:4] 
            flip_x, flip_y, angle, *_ = list(item[4:] + [0,0,0])
            im = Image(texture, r)
            im.flip_x = flip_x
            im.flip_y = flip_y
            im.angle = angle
            if name in images:
                raise Exception('Image names must be unique')
            self.images[name] = im
            images[name] = im
        return images
    
    def _clean(self):
        'Remove old images when MAX_IMAGES is reached'
        for fn in self.cache[self.MAX_IMAGES:]:
            texture = self.textures.pop(fn)
            texture.destroy()
        self.cache = self.cache[:self.MAX_IMAGES]


def get_text_size(font, text=''):
    '''
    Calculate the size of given text using the given font, or if
    no text is provided, then return the font's height instead

    font: an existing sdl2.ext.FontTTF object
    text: optional text string to generate size of
    :rvalue (int, int) or int: (width(int), height(int)) if text provided,
            or height(int) otherwise
    '''
    text_w, text_h = c_int(0), c_int(0)
    f = font.get_ttf_font()
    sdl2.sdlttf.TTF_SizeText(f, text.encode(), byref(text_w), byref(text_h))
    if not text:
        return text_h.value
    return  text_w.value, text_h.value

char_map = ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,?!-:'"_=+&<^>~@/\\|(%)'''
class FontManager():
    '''
    The FontManager class loads ttf TODO (otf?) fonts, caches them, and draws text 
    into a sdl2.ext.Renderer context.
    '''
    def __init__(self, renderer):
        '''
        Initialize FontManager for use with pySDL2.ext.Renderer context

        :param renderer: pySDL2.ext.Renderer to draw on
        '''
        self.renderer = renderer
        self.fonts = {}
        self.cmaps = {}
        self.cache = {}
    def __del__(self):
        for t, h in self.fonts.values():
            t.destroy()
    
    def load(self, filename, size=None):
        '''
        Load a font for later rendering

        :param filename: path to a ttf or otf format font file
        :param size: int point size for font or 'XXpx' for pixel height
        :rvalue tuple: a (filename, size) 2-tuple representing the font in 
            future draw() calls
        '''
        if not size:
            filename, cache = filename
        if (filename, size) in self.fonts:
            self.texture, self.height = self.fonts[(filename, size)]
            self.cmap = self.cmaps[(filename, size)]
            self.blank = self.cmap[' ']
            return filename, size

        file = RESOURCES.get_path(filename)
        font = sdl2.ext.FontTTF(file, size, (255,255,255))
        self.cmap = {}
        tot = 0

        for c in char_map:
            tot += get_text_size(font, c)[0]
        if tot > 1024: # prevent overly wide textures
            width = 1024
            rows = int(tot // 1024) + 1
        else:
            width = tot
            rows = 1
        self.height = get_text_size(font)

        y = 0
        surface = sdl2.SDL_CreateRGBSurface(sdl2.SDL_SWSURFACE, width, self.height*rows,
                32, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
        tot = x = 0

        for c in char_map:
            rend = font.render_text(c)
            wi, hi = rend.w, rend.h
            if x + wi > 1024: # limit texture width
                x = 0
                y += self.height+1
            sdl2.SDL_BlitSurface(rend, None, surface,
                    sdl2.SDL_Rect(x,y,wi,hi))

            self.cmap[c] = Rect(x, y, wi, self.height)
            tot += wi
            x += wi
        self.blank = self.cmap[' ']
        self.texture = sdl2.ext.renderer.Texture(self.renderer, surface)
        self.fonts[(filename, size)] = self.texture, self.height
        self.cmaps[(filename, size)] = self.cmap
        sdl2.SDL_FreeSurface(surface)
        return filename, size


    def draw(self, text, x, y, color=None, alpha=None,
            align='topleft', clip=None, wrap=None, linespace=0, font=None):
        '''
        Draw text string onto pySDL2.ext.Renderer context

        :param text: string to draw
        :param x: x coordinate to draw at
        :param y: y coordinate to draw at
        :param color: (r,g,b) color tuple
        :param alpha: alpha transparency value
        :param align: treat x as 'center' or 'right' pos (def left)
        :param valign: treat y as 'center' or 'bottom' pos (def top)
        :param clip: clip text to Rect
        :param wrap: #TODO wrap text over multiple lines, using clip Rect
        :param font: (filename, size) tuple for font, defaults to last_loaded
        :rvalue rect: actual area drawn into
        '''


        if font in self.fonts: # load texture if argument is in cache
            texture, height = self.fonts[font]
            cmap = self.cmaps[font]
        else:
            texture, height = self.texture, self.height
            cmap = self.cmap

        if wrap and not clip: # must have a clip if wrapping
            w = self.renderer.logical_size[0] - x
            h = self.renderer.logical_size[1] - y
            clip = Rect(x, y, w, h)
        if isinstance(clip, int): # convert clip width into clip rect
            clip = Rect(x, y, clip, self.height)

        if wrap:
            wrapped_text = self._split_lines(text, clip)
            lines = len(wrapped_text)
            if lines > 1:

                if align in ('midleft', 'center', 'midright'):
                    y -= (self.height * lines) // 2 + (linespace * (lines/2))
                elif align in ('bottomleft', 'midbottom', 'bottomright'):
                    y -= (self.height) * lines + linespace * lines
                for line in wrapped_text:
                    self.draw(line, x, y, color, alpha, align, clip)
                    y += self.height + linespace
                    if y + self.height + linespace > clip.bottom:
                        break
            return clip

        out_rect = Rect(0, 0, self.width(text), self.height)
        dx, dy = getattr(out_rect, align, (0,0))
        dest = Rect(x-dx, y-dy, 1, self.height)
        out_rect.topleft = dest.topleft

        sdl2.SDL_SetTextureAlphaMod(texture.tx, alpha or 255)
        color = color or (255,255,255)
        sdl2.SDL_SetTextureColorMod(texture.tx, *color)

        for c in text:
            src = cmap.get(c, self.blank)
            dest.width = src.width
            if clip and dest.right > clip.right:
                break

            self.renderer.copy(texture, src.sdl(), dest.sdl())
            #self.renderer.draw_rect(dest.tuple(), (255,255,255,255))
            dest.x += src.width
        return out_rect

    def width(self, text, scale=1):
        '''
        Calculate width of given text not including motion or scaling effects
        Uses currently loaded font

        :param text: text string to calculate width of
        :rvalue int: width of string in pixels
        '''
        w = 0
        for c in text:
            w += self.cmap.get(c, self.blank).width * scale
        return w

    def _split_lines(self, text, dest, scale=1):
        '''
        Create a series of lines that will fit in the provided rectangle.
        
        :param text: a text string
        :param dest: a Rect object to wrap the text into
        :param scale: scalar to multiply font size by, unused so far
        :rvalue []: list of strings that fit within given area        
        '''        
        final_lines = []

        max_height = dest.height
        width = dest.width
        requested_lines = text.splitlines()

        for requested_line in requested_lines:
            if self.width(requested_line, scale) > width:
                words = requested_line.split(' ')
                # if any of our words are too long to fit, return.
                for word in words:
                    if self.width(word, scale) >= width:
                        # TODO force wrap long words
                        raise Exception("The word " + word + " is too long to fit in the rect passed.")
                # Start a new line
                accumulated_line = ""
                for word in words:
                    test_line = accumulated_line + word + " "
                    # Build the line while the words fit.
                    if self.width(test_line, scale) < width:
                        accumulated_line = test_line
                    else:
                        final_lines.append(accumulated_line)
                        accumulated_line = word + " "
                final_lines.append(accumulated_line)
            else:
                final_lines.append(requested_line)

        #line_count = len(final_lines)
        #line_height = self.height()
        #total_height = line_height * line_count
        return final_lines

class SoundManager():
    '''
    The SoundManager class loads and plays sound files.
    '''
    def __init__(self):
        self.sounds = {}
        self.song = None
        self.is_init = False

    def init(self):
        '''
        Initialize the sound system
        '''
        if not self.is_init:
            if sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO) != 0:
                raise RuntimeError("Cannot initialize audio system: {}".format(SDL_GetError()))

            if sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024):
                raise RuntimeError(f'Cannot open mixed audio: {sdlmixer.Mix_GetError()}')
            self.is_init = True
    
    def load(self, fn, name=None, volume=1):
        '''
        Load a given sound file into the Sound Manager

        :param fn: filename for sound file to load
        :param name: alternate name to use to play the sound instead of its filename
        :param volume: default volume level to play the sound at, from 0.0 to 1.0
        '''
        file = RESOURCES.get_path(fn)
        name = name or os.path.splitext(name)[0]
        sample = sdl2.sdlmixer.Mix_LoadWAV(
                sdl2.ext.compat.byteify(file, 'utf-8'))

        if sample is None:
            raise RuntimeError(f'Cannot open audio file: {sdl2.Mix_GetError()}')
        sdl2.sdlmixer.Mix_VolumeChunk(sample, int(128*volume))
        self.sounds[name] = sample
    
    def music(self, fn, loops=-1, volume=1):
        '''
        Loads a music file and plays immediately plays it

        :param fn: path to music file to load and play
        :param loops: number of times to play song, or loop forever by default
        :param volume: volume level to play music, between 0.0 and 1.0
        '''
        file = RESOURCES.get_path(fn)
        sdl2.sdlmixer.Mix_VolumeMusic(int(volume*128))
        music = sdl2.sdlmixer.Mix_LoadMUS(
                    sdl2.ext.compat.byteify(file, 'utf-8'))
        if music is None:
            raise RuntimeError(f'Cannot open audio file: {sdl2.Mix_GetError()}')

        sdl2.sdlmixer.Mix_PlayMusic(music, loops)
        if self.song:
            sdl2.sdlmixer.Mix_FreeMusic(self.song)
        self.song = music      
    
    @property
    def volume(self):
        return sdl2.sdlmixer.Mix_MasterVolume(-1) / 128
    @volume.setter
    def volume(self, v):
        'Set master volume level between 0.0 and 1.0'
        sdl2.sdlmixer.Mix_MasterVolume(int(v*128))

    def play(self, name, volume=1):
        '''
        Play a loaded sound with the given name

        :param name: name of sound, either the filename(without extension) or
            an alternate name provided to the load() method
        :param volume: volume to play sound at, from 0.0 to 1.
        '''
        sample = self.sounds.get(name)
        if sample:
            channel = sdl2.sdlmixer.Mix_PlayChannel(-1, sample, 0)
            if channel == -1:
                raise RuntimeError(
                    f'Cannot play sample {name}: {sdl2.sdlmixer.Mix_GetError()}')
            sdl2.sdlmixer.Mix_Volume(channel, int(volume*128))

    def __del__(self):
        for s in self.sounds.values():
            sdl2.sdlmixer.Mix_FreeChunk(s)
        if self.song:
            sdl2.sdlmixer.Mix_FreeMusic(self.song)

        sdl2.sdlmixer.Mix_CloseAudio()
        sdl2.SDL_Quit(sdl2.SDL_INIT_AUDIO)
        print('SoundManager closed')
sounds = SoundManager()

from collections.abc import Mapping
def deep_update(d, u, r=False):
    '''
    Add contents of dict u into dict d. This will change the provided
    d parameter dict
    
    :param d: dict to add new values to
    :param u: dict with values to add into d
    :rvalue dict: the updated dict, same as d
    '''
    o = d
    for k, v in u.items():
        if not isinstance(d, Mapping):
            o = u
        elif isinstance(v, Mapping):
            r = deep_update(d.get(k, {}), v, True)
            o[k] = r
        else:
            o[k] = u[k]
    return o

def deep_merge(d, u, r=False):
    '''
    Add contents of dict u into a copy of dict d. This will not change the
    provided d parameter dict, only return a new copy.
    
    :param d: dict to add new values to
    :param u: dict with values to add into d
    :rvalue dict: the new dict with u merged into d
    '''
    n = deep_update({}, d)
    return deep_update(n, u)

def deep_print(d, name=None, l=0, file=None):
    '''
    Pretty print a dict recursively, included all child dicts

    :param d: dict to pring
    :param name: name of dict to use in printing
    :param l: used internaly
    :param file: open file to print into instead of to the console
    '''
    if name: print(f'{"  "*l}{name}', file=file)
    for k, v in d.items():
        if isinstance(v, Mapping):
            deep_print(v, k, l+1, file)
        else:
            print(f'{"  "*(l+1)}{k}: {v}', file=file)


def range_list(start, low, high, step):
    '''
    Creates a list of strings representing numbers within a given
    range. Meant for use with gui.options_menu as an alternative to
    a slider widget. The values will be a listin numerical order, but
    rotated to have the start value first.

    :param start: the value to start at (first value)
    :param low: lowest value for list
    :param hight: highest value for list
    :param step: the numerical value between each item in the list
    :rvalue list: a list of numerical values, rotate to have start value
            first

    example: range_list(50, 0, 100, 10) ->
            [50, 60, 70, 80, 90, 100, 0, 10, 20, 30, 40]
    '''
    return [str(i) for i in range(start, high+1, step)] + [
            str(i) for i in reversed(range(start-step, low-1, -step))]


def get_color_mod(texture):
    '''
    Get color_mod value of a texture as an RGB 3-tuple
    NOT WORKING
    '''
    r, g, b = c_ubyte(0), c_ubyte(0), c_ubyte(0)
    sdl2.SDL_GetTextureColorMod(texture.tx, byref(r), byref(g), byref(b))
    print('inside get', r.value,g.value,b.value)
    return  r.value, g.value, b.value

def set_color_mod(texture, color):
    '''
    Set color_mod value of a texture using an RGB 3-tuple
    NOT WORKING
    '''
    r, g, b = c_ubyte(color[0]), c_ubyte(color[1]), c_ubyte(color[2])
    print('inside set', r.value,g.value,b.value)
    sdl2.SDL_GetTextureColorMod(texture.tx, byref(r), byref(g), byref(b))

def set_globals(*globs):
    '''
    Set the global values within this files scope
    '''
    global config, screen, images, fonts, inp
    config, screen, images, fonts, inp = globs