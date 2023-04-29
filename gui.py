import os, sys
import sdl2, sdl2.ext
from rect import Rect

class ImageManager():
    '''
    Load images into Textures and cache them for later use'''
    
    MAX_IMAGES = 20
    def __init__(self, screen):
        'Pass a pySLD2.ext.Renderer to render into'
        self.screen = screen
        self.images = {}
        self.cache = []
    
    def load(self, fn):
        '''
        Load an image file into a Texture or receive a cached Texture'''
        if fn in self.cache:
            i = self.cache.index(fn)
            self.cache.insert(0, self.cache.pop(i))
            image = self.images[fn]
            return image
        
        surf = sdl2.ext.image.load_img(fn)
        texture = sdl2.ext.renderer.Texture(self.screen, surf)
        self.images[fn] = texture
        self.cache.insert(0, fn)
        self._clean()
        return texture
    
    def _clean(self):
        for fn in self.cache[self.MAX_IMAGES:]:
            texture = self.images.pop(fn)
            texture.destroy()
        self.cache = self.cache[:self.MAX_IMAGES]

class Region:
    def __init__(self, renderer, data, images, fonts):
        self._dict = data
        self.renderer = renderer
        self.images = images
        self.fonts = fonts
        self.area = self._verify_rect('area')
        self.color = self._verify_color('color', (0,0,0))
        self.thickness = self._verify_int('thickness', 0)
        self.outline = self._verify_color('outline', optional=True)
        self.roundness = self._verify_int('roundness', 0)

        self.borderx = self._verify_int('border', 0)
        self.bordery = self._verify_int('bordery', self.borderx, True)

        self.image = self._verify_file('image', optional=True)
        self.pattern = None # TODO add base64 image loading
        self.repeat = self._verify_bool('repeat', False)
        self.stretch = self._verify_bool('stretch', False)
        
        # TODO figure out how to use default/system fonts
        self.font = self._verify_file('font', optional=True)
        self.fontsize = self._verify_int('fontsize', 30)
        self.fontcolor = self._verify_color('fontcolor', (255,255,255))
        self.text = self._verify_text('text', optional=True)
        self.list = self._verify_string_list('list', optional=True)
        self.align = self._verify_option('align', ('center', 'right'), None)
        if self.text and self.list:
            raise Exception('Cannot define text and a list')
        self.scrollable = self._verify_bool('scrollable', False, True)
        self.auto_scroll = self._verify_bool('autoscroll', False, True)

    def draw(self):
        self.renderer.fill(self.area.tuple(), self.color)

        if self.image:
            image = self.images.load(self.image)
            if self.repeat:
                pass
            elif self.stretch:
                self.renderer.copy(image, dstrect=Rect(
                        0,0, *image.size).fitted(self.area).sdl())
            else:
                self.renderer.copy(image, dstrect=self.area.sdl())




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

    def _verify_int(self, name, default=None, optional=False):
        val = self._dict.get(name, default)
        print(val)
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
        print(f'{name}: {val}')
        return val




if __name__ == '__main__':
    main()  