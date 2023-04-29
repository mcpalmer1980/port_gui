import sys, os, random
import sdl2
import sdl2.ext
from sdl2.ext import FontTTF
from rect import Rect
import tfont

from ctypes import c_int, byref

def get_text_size(font, text=''):
    f = font.get_ttf_font()
    text_w, text_h = c_int(0), c_int(0)
    sdl2.sdlttf.TTF_SizeText(f, text.encode(), byref(text_w), byref(text_h))
    if not text:
        return text_h.value
    return  text_w.value, text_h.value

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Harbour Master", size=(640, 480))
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED)
    screen.clear((255,0,0))
    tf = tfont.TextureFont(screen, 'font.ttf', 45)

    images = ImageManager(screen)
    ipath = '/home/michael/Roms/genesis/media/images'
    files = [os.path.join(ipath,f) for f in os.listdir(ipath)[:15] if f.endswith('.png')]
    for fn in files:
        images.load(fn)
    texture = images.load(random.choice(images.cache))
    window.show()

    running = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        screen.copy(texture)
        tf.draw("Testing it!", 20,20, (255,0,0))
        screen.copy(tf.texture, (0,0,-300,50))
        screen.present()
        window.refresh()
        sdl2.timer.SDL_Delay(1000//30)


        if not running % 45:
            texture = images.load(random.choice(images.cache))
    return 0


class ImageManager():
    MAX_IMAGES = 20
    def __init__(self, screen):
        self.screen = screen
        self.images = {}
        self.cache = []
    
    def load(self, fn):
        if fn in self.cache:
            i = self.cache.index(fn)
            self.cache.insert(0, self.cache.pop(i))
            image = self.images[fn]
            return image
        
        surf = sdl2.ext.image.load_img(fn)
        texture = sdl2.ext.renderer.Texture(self.screen, surf)
        self.images[fn] = texture
        self.cache.insert(0, fn)
        self.clean()
    
    def clean(self):
        for fn in self.cache[self.MAX_IMAGES:]:
            texture = self.images.pop(fn)
            texture.destroy()
        self.cache = self.cache[:self.MAX_IMAGES]


if __name__ == "__main__":
    sys.exit(run())