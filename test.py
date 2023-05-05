import sys, os, random, json
import sdl2, sdl2.ext
from rect import Rect
from tfont import FontManager
from gui import ImageManager, Region, Image

DEFAULT_SIZE= 480, 320
desc = "Dungeon & Dragons: Warriors of the Eternal Sun is set in the world of Mystara, a setting of the Dungeons & Dragons game. The characters find themselves in a strange, red-hued world in which the horizon slopes upward in all directions, eventually vanishing into a crimson haze at the limits of sight. Their mission is to find and make allies in this new world or else the kingdom and its culture will perish."
game_list = ["3 Ninjas Kick Back", "AD&D - Warriors of the Eternal Sun", "AWS Pro Moves Soccer", "Aa Harimanada", "Aaahh!!! Real Monsters", "Action 52-in-1", "Addams Family Values", "Addams Family", "Advanced Busterhawk Gleylancer", "Advanced Military Commander", "Adventures of Batman & Robin", "Adventures of Mighty Max", "Adventures of Rocky and Bullwinkle", "Aero The Acro-bat I", "Aero The Acro-bat II", "Aerobiz Supersonic", "Aerobiz", "After Burner Complete", "After Burner II", "Air Buster", "Air Diver", "Aladdin", "Alex Kidd In The Enchanted Castle", "Alien III", "Alien Soldier", "Alien Storm", "Alisia Dragoon", "Altered Beast", "American Gladiators", "Andre Agassi Tennis"]

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

    Image.renderer = screen
    images = ImageManager(screen)
    ipath = '/home/michael/Roms/genesis/media/images'
    files = [os.path.join(ipath,f) for f in os.listdir(ipath)[:15] if f.endswith('.png')]
    for fn in files:
        images.load(fn)
    image = images.load(random.choice(images.cache))

    title = Region(screen, d['title'], images, fonts)
    title.list = game_list
    select = Region(screen, d['list'], images, fonts)
    title.select = select
    window.show()

    atlas = images.load_atlas('nine.png', d['nine.png'])
    arrow = images.load('arrow_r')

    inp = InputHandler()

    update = True
    running = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)
        if inp.quit:
            running = False
        if inp.pressed:
            print(inp.pressed)
            if inp.pressed == 'up':
                update = True
                title.selected -= 1
            elif inp.pressed == 'down':
                update = True
                title.selected += 1

        if title.update():
            update = True

        if not running % 90:
            update = True
            image = images.load(random.choice(images.cache))

        if update:
            update = False
            #screen.clear()
            image.draw()
            arrow.draw_at(30,30)
            atlas['circle'].draw_at(30,60)
            title.draw()


        screen.present()
        window.refresh()
        sdl2.timer.SDL_Delay(1000//30)

    screen.destroy()
    return 0

KEY_MAP = {
    sdl2.SDLK_UP: 'up',
    sdl2.SDLK_RIGHT: 'right',
    sdl2.SDLK_DOWN: 'down',
    sdl2.SDLK_LEFT: 'left',
    sdl2.SDLK_KP_ENTER: 'start',
    sdl2.SDLK_RETURN: 'start',
    sdl2.SDLK_ESCAPE: 'select',
    sdl2.SDLK_SPACE: 'A',
    sdl2.SDLK_z: 'A',
    sdl2.SDLK_x: 'B',
    sdl2.SDLK_a: 'X',
    sdl2.SDLK_s: 'Y',
    sdl2.SDLK_LCTRL: 'L',
    sdl2.SDLK_LALT: 'R'}
BUTTON_MAP = {11: 'up', 12: 'down',
           13: 'left', 14: 'right',
           0: 'A', 1: 'B', 2: 'X', 3: 'Y',
           9: 'L', 10: 'R',
           4: 'select', 6: 'start'}
AXIS_MAP = {
    (1,-1): 'up',
    (1,1): 'down',
    (0,-1): 'left',
    (0,1): 'right' }

class InputHandler():
    REPEAT_RATE = 5
    REPEAT_DELAY = 10
    CAN_REPEAT = ('up', 'down', 'right', 'left')
    AXIS_MOD = 2 ** 15 * 1.2
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
        self.selected = 0

    def process(self, events):
        self.pressed = None
        for e in events:
            if e.type == sdl2.SDL_QUIT:
                self.quit = True
            elif e.type == sdl2.SDL_CONTROLLERDEVICEADDED:
                sdl2.ext.common.init(controller=True)
                self.joy = sdl2.SDL_GameControllerOpen(0)
                print('Controller connected')
            
            # KEYBOARD
            elif e.type == sdl2.SDL_KEYDOWN:
                key = e.key.keysym.sym
                if key == sdl2.SDLK_ESCAPE:
                    self.quit = True

                if not self.keys.get(key):
                    self.keys[key] = True
                    if key in KEY_MAP:
                        self.pressed = KEY_MAP[key]
                        self.last_press = self.keys, key, self.pressed
                        self.held_for = -self.REPEAT_DELAY
            elif e.type == sdl2.SDL_KEYUP:
                key = e.key.keysym.sym
                self.keys[key] = False

            # BUTTONS
            elif e.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                butt = e.cbutton.button
                self.buttons[butt] = True
                if butt in BUTTON_MAP:
                    self.pressed = BUTTON_MAP[butt]
                    self.last_press = self.buttons, butt, self.pressed
                    self.held_for = -self.REPEAT_DELAY
            elif e.type == sdl2.SDL_CONTROLLERBUTTONUP:
                butt = e.cbutton.button
                self.buttons[butt] = False

            elif e.type == sdl2.SDL_CONTROLLERAXISMOTION:
                a = e.caxis.axis
                v = round(e.caxis.value / self.AXIS_MOD)
                if (a,v) in AXIS_MAP:
                    if v and self.axes.get(a) != v:
                        self.pressed = AXIS_MAP[(a,v)]
                        self.last_press = self.axes, a, self.pressed 
                        self.held_for = -self.REPEAT_DELAY
                self.axes[a] = v
            
        # HANDLE KEY REPEATS
        if self.last_press:
            pressed = None
            m, k, b = self.last_press
            
            if b in self.CAN_REPEAT and m.get(k):
                self.held_for += 1
                if self.held_for > self.REPEAT_RATE:
                    self.held_for = 0
                    self.pressed = b


if __name__ == "__main__":
    main()
    sys.exit()