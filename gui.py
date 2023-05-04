import os, sys
import sdl2, sdl2.ext
from rect import Rect

'''
TODO
    Rounded rects (sdl2_gfx, manually)
    Patches (9-patched image rendering)
    Imagelist (separate image for each list item, with alignment)
    Text animation (rotation, scaling, color changing)
    tiled image rendering
    Map controller axes to inp.pressed'''

'''
    FILL MODE
    area: 4-tuple of pixels or screen percent(0.0-1.0),
    color: 3-tuple fill color
    outline: 3-typle outline color
    thickness: int outline thickness,
    roundness: int outline roundness,
    border: int border around text x or x&y
    bordery: int top/bottom border around text
    
    IMAGE RENDERING
    image: filename for image
    imagerect: 4-tuple (x,y,w,h) region of image to use
    imagesize: 2-tuple (w,h) scale to this size
    imagemode: 'fit', 'stretch', 'repeat', None or ''
    imagealign: same options as text align, but for image
    patch: 4-tuple left, top, right, bottom edges for 9-patch rendering
    pattern: bool image is a base64 string

    TEXT RENDERING
    font: filename for font
    fontsize: int size of font
    fontcolor: 3-tuple font color
    text: text string (may be multiline)
    wrap: allow multiline text wraping
    linespace: int extra space between lines
    align: text alignment (topleft, topright, midtop
                           midleft, center, midright
                           bottomleft, midbottom, bottomright)

    LIST RENDERING
    list: list of items (ignores wrap, allows navigation)
    imagelist: list of filenames or Image objects
    ilistalign: alignment for list images
    itemsize: item height for vertical lists (width for horiz ones)
    selected: 3-tuple color for selected item, or a Region for rendering it
    scrollable: bool allow up/down to scroll wrapped text
    autoscroll: int speed of auto scroll or 0 disables
    '''


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
        self.dstrect = Rect.from_sdl(self.srcrect).fitted(
                    Rect(0,0, *self.renderer.logical_size)).sdl()

   
    def draw_at(self, x, y, angle=0, flip_x=None, flip_y=None, center=None):
        center = center or self.center
        angle = angle or self.angle
        if flip_x == None and flip_y == None:
            flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        else:
            flip = 1 * bool(flip_x) | 2 * bool(flip_y)

        self.renderer.copy(self.texture, self.srcrect,
                dstrect=(x, y), angle=angle, flip=flip, center=center)

    def draw_in(self, dest, angle=0, flip_x=None, flip_y=None, center=None):
        center = center or self.center
        angle = angle or self.angle
        if flip_x == None and flip_y == None:
            flip = 1 * bool(self.flip_x) | 2 * bool(self.flip_y)
        else:
            flip = 1 * bool(flip_x) | 2 * bool(flip_y)

        self.renderer.copy(self.texture, self.srcrect,
                dstrect=dest, angle=angle, flip=flip, center=center)

    def draw(self):
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
        
        surf = sdl2.ext.image.load_img(fn)
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
        surf = sdl2.ext.image.load_img(fn)
        texture = sdl2.ext.renderer.Texture(self.screen, surf)
        for name, item in atlas.items():
            r = item[:4] 
            flip_x, flip_y, angle, *_ = item[4:] + (0,0,0)
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

class Region:
    '''
    For drawing a rectangular region on a renderer context
    Regions may have a fill color, outline, image, and/or text
    Attributes are loaded from a json file
    
    area, color, thickness, outline, roundness, 
    image, pattern, repeat, stretch
    borderx, border
    font, fontsize, fontcolor, text, align
    scrollable, autoscroll, wrap, linespace
    '''
    def __init__(self, renderer, data, images, fonts):
        self._dict = data
        self.renderer = renderer
        self.images = images
        self.fonts = fonts

        self.area = self._verify_rect('area')
        self.color = self._verify_color('color', (0,0,0))
        self.outline = self._verify_color('outline', optional=True)
        self.thickness = self._verify_int('thickness', 0)
        self.roundness = self._verify_int('roundness', 0)
        self.borderx = self._verify_int('border', 0)
        self.bordery = self._verify_int('bordery', self.borderx) or 0

        self.image = self._verify_file('image', optional=True)
        self.imagerect = 0 ## TODO
        self.imagesize = self._verify_ints('imagesize', 2, None, optional=True)
        self.imagemode = self._verify_option('imagemode', 
                ('fit', 'stretch', 'repeat', None), 'fit')
        self.imagealign = self._verify_option('imagealign', Rect.POINTS, None)
        self.patch = 0 ## TODO
        self.pattern = False
        
        # TODO figure out how to use default/system fonts
        self.font = self._verify_file('font', optional=True)
        self.fontsize = self._verify_int('fontsize', 30)
        self.fontcolor = self._verify_color('fontcolor', (255,255,255))
        self._text = self._verify_text('text', optional=True)
        self.wrap = self._verify_bool('wrap', False, True)
        self.linespace = self._verify_int('linespace', 0, True)
        self.align = self._verify_option('align', Rect.POINTS, 'topleft')

        self.list = self._verify_string_list('list', optional=True)
        self.imagelist = 0 ## TODO
        self.ilistalign = 0 ## TODO
        self.itemsize = self._verify_int('itemsize', None, True)
        self.select = self._verify_color('selected', optional=True)

        self.scrollable = self._verify_bool('scrollable', False, True)
        self.autoscroll = self._verify_int('autoscroll', 0, True)

        if self._text and self.list:
            raise Exception('Cannot define text and a list')

        self.life = 0
        self.selected = 0

    def draw(self, area=None, text=None):
        '''
        Draw all features of this Region'''

        area = area or self.area
        # Draw Rect and outline
        if self.outline:
            self._draw_rect(area, self.outline, self.roundness)
            r = area.inflated(-self.thickness*2)
            self._draw_rect(r, self.color, self.roundness)
        else:
            self._draw_rect(r, self.color, self.roundness)

        # Draw image
        if self.image:
            image = self.images.load(self.image)
            dest = Rect.from_sdl(image.srcrect)
            if self.imagesize:
                dest.size = self.imagesize
            
            print('imagemode', self.imagemode)
            
            if self.imagemode == 'fit':
                dest.fit(area)
                if self.imagealign:
                    w = getattr(area, self.imagealign)
                    setattr(dest, self.imagealign, w)
                image.draw_in(dest.tuple())
            else:
                print('not fit', dest)
                dest.topleft = area.topleft
                print(area, dest)
                image.draw_in(dest.tuple())

            '''elif self.imagemode == 'stretch':
                image.draw_in(area.tuple())
            elif self.imagemode == 'repeat':
                pass
            else:
                dest.topleft = area.topleft
                image.draw_in(dest)'''

        # Draw text
        text_area = area.inflated(-self.borderx*2, -self.bordery*2)
        if self.font and text:
            x, y = getattr(text_area, self.align, text_area.topleft)
            self.fonts.draw(text, x, y, self.fontcolor, 255,
                    self.align, text_area).height + self.linespace
        elif self.font and self._text:
            pos = self.selected % len(self._text)

            self.fonts.load(self.font, self.fontsize)
            x, y = getattr(text_area, self.align, text_area.topleft)
            for l in self._text[pos:]:
                if y + self.fonts.height > text_area.bottom:
                    break
                y += self.fonts.draw(l, x, y, self.fontcolor, 255,
                        self.align, text_area).height + self.linespace

        elif self.font and self.list:
            itemsize = self.itemsize or self.font.height + self.bordery
            self.page_size = area.height // itemsize
            self.selected = self.selected % len(self.list)

            self.fonts.load(self.font, self.fontsize)
            start = max(0, self.selected - self.page_size//3)
            irect = text_area.copy()
            irect.height = itemsize
            for i, t in enumerate(self.list[start: start + self.page_size]):
                if self.selected == i + start:
                    if isinstance(self.select, Region):
                        self.select.draw(irect, t)
                    else:
                        self.fonts.draw(t, *irect.topleft, self.select, 255,
                                self.align, text_area)             
                else:           
                    self.fonts.draw(t, *irect.topleft, self.fontcolor, 255,
                            self.align, text_area)
                irect.y += self.itemsize

    def update(self):
        updated = False
        self.life += 1
        if self.autoscroll:
            if not self.life % self.autoscroll:
                self.selected += 1
                updated = True
        return updated
        
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, val):
        if self.wrap:
            self.fonts.load(self.font, self.fontsize)
            text_area = self.area.inflated(-self.borderx*2, -self.bordery*2)
            self._text = self.fonts._split_lines(val, text_area)
        else:
            self._text = val.split('\n')
        print(f'text set to:\n{self._text}')

    def _draw_rect(self, rect, color, round=0):        
        self.renderer.fill(rect.sdl(), color)

    def _verify_rect(self, name, default=None, optional=False):
        # AREA
        val = self._dict.get(name, default)
        if val == None and optional: return None

        try:
            if len(val) != 4:
                raise Exception('Region area incorrect length')
        except TypeError:
            print('Region area not iterable')
            raise
        for i, p in enumerate(val):
            if not isinstance(p, (int, float)):
                raise Exception(f'point {i}{p} is not a number')
            if type(p)==float and 0 < p <= 1:
                val[i] = p * self.renderer.logical_size[i % 2]
        val = Rect(*val)
        print(f'{name}: {val}')
        return val

    def _verify_color(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        try:
            if len(val) != 3:
                raise Exception('color incorrect length')
        except TypeError:
            print('color not iterable')
            raise
        for i, p in enumerate(val):
            if not isinstance(p, (int)):                
                raise Exception(f'{i},{p} - invalid color type')
            if p<0 or p>255:
                raise Exception(f'{i},{p} - invalid color value')
        print(f'{name}: {val}')
        return val

    def _verify_int(self, name, default=0, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, int):
            raise Exception(f'{name} is not an int')
        print(f'{name}: {val}')
        return val
    
    def _verify_file(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, str):
            raise Exception(f'{name} is not a string')        
        if not os.path.exists(val):
            raise Exception(f'{name} is not a file')
        print(f'{name}: {val}')
        return val
    
    def _verify_bool(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if val in (True, False, 0, 1):
            val = True if val else False
            print(f'{name}: {val}')
            return val
        else:
            raise Exception(f'{name} is not BOOL')
    
    def _verify_option(self, name, options, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None
      
        if val not in options:
            val = default
        return val
    
    def _verify_text(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if isinstance(val, str):
            print(f'{name}: {val}')
            return val
        else:
            raise(f'{name} is not text')
    
    def _verify_string_list(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, (list, tuple)):
            raise Exception(f'{name} is not a list')
        for i, v in enumerate(val):
            if not isinstance(v, str):
                raise Exception(f'{name}[{i}] == {v}, not a string')
        return val
    
    def _verify_ints(self, name, count, default=None, optional=False):
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, (list, tuple)):
            raise Exception(f'{name} is not a list')
        elif len(val) != count:
            raise Exception(f'{name} must have {count} int values')
        for i, v in enumerate(val):
            if not isinstance(v, int):
                raise Exception(f'{name}[{i}] == {v}, not an int')
        return val






if __name__ == '__main__':
    main()  