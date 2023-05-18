"""
Utility functions for pySDL and mypyGUI

Rect: class used to represent and modify Rectangular regions
Image: simple class to represent and draw textures and subtexture
    regions onto a pySDL render context
ImageManager: class to load and cache images as Image objects in
    texture memory
FontManager: class used to load and render fonts onto a pySDL
    render context
"""
from ctypes import c_int, byref
import sdl2, sdl2.ext
import os
global RESOURCES
RESOURCES = sdl2.ext.Resources(__file__, 'assets')

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
        return Rect(self.x, self.y, self.width, self.height)    

    def fit(self, other):
        'Move and resize myself to fill other rect maintaining aspect ratio'
        r = self.fitted(other)
        self.x = r.x; self.width = r.width
        self.y = r.y; self.height = r.height

    def fitted(self, other):
        '''
        Return new Rect whith other centered and resized to fill self
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
        Return a new rect using bottom and right coordinates instead
        of width and height'''
        return Rect(x, y, x2-x, y2-y)
    def from_sdl(r):
        return Rect(r.x, r.y, r.w, r.h)

    def inflate(self, x, y=None):
        '''
        Add x to width and y to height of rect, or x to both
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
        'Return copy of rect moved by x/y pixels'
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
        'Return copy of self cropped to fit inside other'
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
    Class that draws holds the source rect and draws images
    from a Texture'''

    def __init__(self, texture, srcrect=None, renderer=None):
        renderer = renderer or Image.renderer
        if not renderer:
            raise Exception('No renderer context provided')
        Image.renderer = Image.renderer or renderer

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
        'Draw image with topleft corner at x, y and at the original size'
        center = center or self.center
        angle = angle or self.angle
        if flip_x == None and flip_y == None:
            flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        else:
            flip = 1 * bool(flip_x) | 2 * bool(flip_y)

        self.renderer.copy(self.texture, self.srcrect,
                dstrect=(x, y), angle=angle, flip=flip, center=center)

    def draw_in(self, dest, angle=0, flip_x=None, flip_y=None, center=None):
        'Draw image inside given Rect region (may squish or stretch image)'
        center = center or self.center
        angle = angle or self.angle
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
    Load images into Textures and cache them for later use'''
    
    MAX_IMAGES = 20
    def __init__(self, screen):
        'Pass a pySLD2.ext.Renderer to render into'
        self.screen = screen
        self.images = {}
        self.textures = {}
        self.cache = []
    
    def load(self, fn, area=None):
        '''
        Load an image file into a Texture or receive a cached Texture'''
        if fn in self.cache:
            i = self.cache.index(fn)
            self.cache.insert(0, self.cache.pop(i))
            return self.images[fn]
        elif fn in self.images:
            return self.images[fn]

        elif isinstance(fn, str) and os.path.isfile(fn):
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
        Load image fn, create Images from atlas dict, create
        named shortcut in image dict
        {'string_name': x, y, w, h} '''

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
        for fn in self.cache[self.MAX_IMAGES:]:
            texture = self.textures.pop(fn)
            texture.destroy()
        self.cache = self.cache[:self.MAX_IMAGES]


def get_text_size(font, text=''):
    f = font.get_ttf_font()
    text_w, text_h = c_int(0), c_int(0)
    sdl2.sdlttf.TTF_SizeText(f, text.encode(), byref(text_w), byref(text_h))
    if not text:
        return text_h.value
    return  text_w.value, text_h.value

char_map = ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,?!-:'"_=+&<^>~@/\\|(%)'''
class FontManager():
    '''
    Font renderer for use with pygame._sdl2
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
        :param size: int point size for font or 'XXXpx' for pixel height
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
        :rvalue: width of string in pixels
        '''
        w = 0
        for c in text:
            w += self.cmap.get(c, self.blank).width * scale
        return w

    def _split_lines(self, text, dest, scale=1):
        '''Create a series of lines that will fit on the provided
        rectangle.'''        
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
    def __init__(self, folder):
        self.sounds = {}
        self.song = None
        self.is_init = False

    def init(self):
        if not self.is_init:
            if sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO) != 0:
                raise RuntimeError("Cannot initialize audio system: {}".format(SDL_GetError()))

            if sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024):
                raise RuntimeError(f'Cannot open mixed audio: {sdlmixer.Mix_GetError()}')
            self.is_init = True
    
    def load(self, name, volume=1):
        file = RESOURCES.get_path(name)
        sample = sdl2.sdlmixer.Mix_LoadWAV(
                sdl2.ext.compat.byteify(file, 'utf-8'))

        if sample is None:
            raise RuntimeError(f'Cannot open audio file: {sdl2.Mix_GetError()}')
        sdl2.sdlmixer.Mix_VolumeChunk(sample, int(128*volume))
        self.sounds[os.path.splitext(name)[0]] = sample
    
    def music(self, name, loops=-1, volume=1):
        file = RESOURCES.get_path(name)
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
        sdl2.sdlmixer.Mix_MasterVolume(int(v*128))

    def __call__(self, name, volume=1):
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

from collections.abc import Mapping
def deep_update(d, u):
    for k, v in u.items():
        # this condition handles the problem
        if not isinstance(d, Mapping):
            d = u
        elif isinstance(v, Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]

    return d

def range_list(start, low, high, step):
    return [str(i) for i in range(start, high, step)] + [str(i) for i in range(low, start, step)]