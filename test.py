import sys, os, random, json
import sdl2, sdl2.ext
from rect import Rect
from tfont import FontManager
from gui import ImageManager, Region

DEFAULT_SIZE= 480, 320
desc = "Dungeon & Dragons: Warriors of the Eternal Sun is set in the world of Mystara, a setting of the Dungeons & Dragons game. The characters find themselves in a strange, red-hued world in which the horizon slopes upward in all directions, eventually vanishing into a crimson haze at the limits of sight. Their mission is to find and make allies in this new world or else the kingdom and its culture will perish."


def main():
    with open('data.json') as inp:
        d = json.load(inp)
    display_size = d.get('options', {}).get('display_size', DEFAULT_SIZE)

    sdl2.ext.init()
    window = sdl2.ext.Window("Harbour Master", size=display_size)
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED)
    screen.clear((255,0,0))
    fonts = FontManager(screen)
    tf = fonts.load('font.ttf', 25)
    f = fonts.load('font2.ttf', 30)

    

    images = ImageManager(screen)
    ipath = '/home/michael/Roms/genesis/media/images'
    files = [os.path.join(ipath,f) for f in os.listdir(ipath)[:15] if f.endswith('.png')]
    for fn in files:
        images.load(fn)
    texture = images.load(random.choice(images.cache))

    title = Region(screen, d['title'], images, fonts)
    window.show()

    inp = InputHandler()

    running = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)
        if inp.quit:
            running = False
        if inp.pressed:
            print(inp.pressed)


        screen.copy(texture)
        #fonts.draw(desc, 20,60, (0,0,255), clip=Rect(10,10, 500,200), wrap=-10, align='center')
        title.draw()
        screen.present()
        window.refresh()
        sdl2.timer.SDL_Delay(1000//30)

        if not running % 90:
            texture = images.load(random.choice(images.cache))
    return 0

KEY_MAP = {
    sdl2.SDLK_UP: 'up',
    sdl2.SDLK_RIGHT: 'right',
    sdl2.SDLK_DOWN: 'down',
    sdl2.SDLK_LEFT: 'left',
    sdl2.SDLK_KP_ENTER: 'start',
    sdl2.SDLK_RETURN: 'start',
    sdl2.SDLK_SPACE: 'A',
    sdl2.SDLK_z: 'A',
    sdl2.SDLK_x: 'B'}
BUTTON_MAP = {11: 'up', 12: 'down',
           13: 'left', 14: 'right',
           0: 'A', 1: 'B', 6: 'start'}


class InputHandler():
    REPEAT_RATE = 5
    REPEAT_DELAY = 10
    CAN_REPEAT = ('up', 'down', 'right', 'left')
    AXIS_MOD = 2 ** 15
    def __init__(self):
        sdl2.ext.common.init(controller=True)
        try:
            self.joy = sdl2.SDL_GameControllerOpen(0)
        except:
            self.joy = None
        self.quit = False
        self.buttons = {}
        self.keys = {}
        self.axes = {}
        self.last_press = None
        self.held_for = 0

    def process(self, events):
        self.pressed = None
        for e in events:
            if e.type == sdl2.SDL_QUIT:
                self.quit = True
            elif e.type == sdl2.SDL_CONTROLLERDEVICEADDED:
                sdl2.ext.common.init(controller=True)
                self.joy = sdl2.SDL_GameControllerOpen(0)
                print('controller connected')
            
            # KEYBOARD
            elif e.type == sdl2.SDL_KEYDOWN:
                key = e.key.keysym.sym
                if key == sdl2.SDLK_ESCAPE:
                    self.quit = True

                if not self.keys.get(key):
                    self.keys[key] = True
                    if key in KEY_MAP:
                        self.last_press = self.keys, key
                        self.pressed = KEY_MAP[key]
                        self.held_for = -self.REPEAT_DELAY
                    print('pressed', key)
            elif e.type == sdl2.SDL_KEYUP:
                key = e.key.keysym.sym
                self.keys[key] = False
                print('released', key)

            # BUTTONS
            elif e.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                butt = e.cbutton.button
                self.buttons[butt] = True
                if butt in BUTTON_MAP:
                    self.last_press = self.buttons, butt
                    self.pressed = BUTTON_MAP[butt]
                    self.held_for = -self.REPEAT_DELAY
                print('pressed', butt)
            elif e.type == sdl2.SDL_CONTROLLERBUTTONUP:
                butt = e.cbutton.button
                self.buttons[butt] = False
                print('released', butt)

            elif e.type == sdl2.SDL_CONTROLLERAXISMOTION:
                self.axes[e.caxis.axis] = e.caxis.value / self.AXIS_MOD
                print(self.axes[e.caxis.axis])
            
        # HANDLE KEY REPEATS
        if self.last_press:
            pressed = None
            m, k = self.last_press
            if m.get(k):
                self.held_for += 1
                if self.held_for > self.REPEAT_RATE:
                    self.held_for = 0
                    if m == self.keys:
                        pressed = KEY_MAP[k]
                    elif m == self.buttons:
                        pressed = BUTTON_MAP[k]
                    if pressed in self.CAN_REPEAT:
                        self.pressed = pressed


def trace(e, l=0):
    for i in dir(e):
        if not i.startswith('_'):
            print(i, getattr(e, i))

    print()

        #trace(i)


#SDLK_UP,

if __name__ == "__main__":
    main()
    sys.exit()