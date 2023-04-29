from ctypes import c_int, byref
import sdl2, sdl2.ext
from sdl2.ext import FontTTF
from rect import Rect

def get_text_size(font, text=''):
    f = font.get_ttf_font()
    text_w, text_h = c_int(0), c_int(0)
    sdl2.sdlttf.TTF_SizeText(f, text.encode(), byref(text_w), byref(text_h))
    if not text:
        return text_h.value
    return  text_w.value, text_h.value

char_map = ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,?!-:'"_=+<>~@/\\|(%)'''
class TextureFont():
    '''
    Font renderer for use with pygame._sdl2
    '''
    def __init__(self, renderer, filename, size):
        '''
        Initialize TextureFont for use with pygame._sdl2 GPU renderer

        :param renderer: pygame._sdl2.video.Renderer to draw on
        :param filename: path to a pygame.font.Font compatible file (ttf)
        :param size: point size for font
        '''
        self.renderer = renderer
        self.filename = filename

        font = FontTTF(filename, size, (255,255,255))
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
        self.texture = sdl2.ext.renderer.Texture(renderer, surface)


    def draw(self, text, x, y, color=None, alpha=None, align=False, valign=False):
        '''
        Draw text string onto pygame._sdl2 GPU renderer

        :param text: string to draw
        :param x: x coordinate to draw at
        :param y: y coordinate to draw at
        :param color: (r,g,b) color tuple
        :param alpha: alpha transparency value
        :param align: treat x as 'center' or 'right' pos (def left)
        :param valign: treat y as 'center' or 'bottom' pos (def top)
        :rvalue rect: actual area drawn into
        '''
        dest = Rect(x, y, 1, self.height)
        sdl2.SDL_SetTextureAlphaMod(self.texture.tx, alpha or 255)
        color = color or (255,255,255)
        sdl2.SDL_SetTextureColorMod(self.texture.tx, *color)

        if align == 'right':
            dest.left -= self.width(text)
        elif align == 'center':
            dest.left -= self.width(text) // 2
        if valign == 'bottom':
            dest.top -= self.height
        elif valign == 'center':
            dest.top -= self.height // 2

        x, y = dest.x, dest.top
        width = 0
        for c in text:
            src = self.cmap.get(c, self.blank)
            dest.width = src.width


            self.renderer.copy(self.texture, src.sdl(), dest.sdl())
            dest.x += src.width
            width += src.width
        return Rect(x, y, width, self.height)

