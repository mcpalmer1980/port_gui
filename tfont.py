from ctypes import c_int, byref
import sdl2, sdl2.ext
from rect import Rect

def get_text_size(font, text=''):
    f = font.get_ttf_font()
    text_w, text_h = c_int(0), c_int(0)
    sdl2.sdlttf.TTF_SizeText(f, text.encode(), byref(text_w), byref(text_h))
    if not text:
        return text_h.value
    return  text_w.value, text_h.value

char_map = ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,?!-:'"_=+<>~@/\\|(%)'''
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
        self.cache = []
    
    def load(self, filename, size):
        '''
        Load a font for later rendering

        :param filename: path to a ttf or otf format font file
        :param size: int point size for font or 'XXXpx' for pixel height
        '''
        self.cache.insert(0, (filename, size))

        font = sdl2.ext.FontTTF(filename, size, (255,255,255))
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
        return filename, size


    def draw(self, text, x, y, color=None, alpha=None,
            align=False, valign=False, clip=None, wrap=None, font=None):
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
            align = valign = False
            clip = Rect(x, y, w, h)
        if isinstance(clip, int): # convert clip width into clip rect
            clip = Rect(x, y, clip, self.height)

        if wrap:
            vspace = wrap if isinstance(wrap, int) else 0
            wrapped_text = self._split_lines(text, clip)
            if len(wrapped_text) > 1:
                for line in wrapped_text:
                    self.draw(line, x, y, color, alpha, align, valign, clip)
                    y += self.height + vspace
                    if y + self.height + vspace > clip.height:
                        break
            return clip

        dest = Rect(x, y, 1, self.height)
        sdl2.SDL_SetTextureAlphaMod(texture.tx, alpha or 255)
        color = color or (255,255,255)
        sdl2.SDL_SetTextureColorMod(texture.tx, *color)

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
            src = cmap.get(c, self.blank)
            dest.width = src.width
            if clip and dest.right > clip.right:
                break

            self.renderer.copy(texture, src.sdl(), dest.sdl())
            dest.x += src.width
            width += src.width
        return Rect(x, y, width, height)

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
