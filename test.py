import sys, os, random, json
import sdl2, sdl2.ext
from utility import Rect, Image, ImageManager, FontManager
from gui import Region, InputHandler

DEFAULT_SIZE= 480, 320

def main():
    global config, screen, fonts, images, inp

    with open('data.json') as inp:
        config = json.load(inp)
    display_size = config.get('options', {}).get('display_size', DEFAULT_SIZE)

    sdl2.ext.init()
    window = sdl2.ext.Window("Harbour Master", size=display_size)
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED)
    screen.clear((0,0,0))

    Image.renderer = screen
    images = ImageManager(screen)
    fonts = FontManager(screen)
    inp = InputHandler()
    window.show()

    background = Region(screen, config['background'], images, fonts)
    mainlist = Region(screen, config['mainlist'], images, fonts)
    maininfo = Region(screen, config['maininfo'], images, fonts)
    mainlist.select = Region(screen, config['list'], images, fonts)

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
                mainlist.selected -= 1
            elif inp.pressed == 'down':
                update = True
                mainlist.selected += 1
            elif inp.pressed in ('A', 'start'):
                selected = mainlist.list[mainlist.selected]
                if selected == 'Exit':
                    running = 0

        if update:
            mainlist.selected = mainlist.selected % len (mainlist.list)
            maininfo.text = config['mainlist']['info'][mainlist.selected]
            background.draw()
            mainlist.draw()
            maininfo.draw()


        screen.present()
        window.refresh()
        sdl2.timer.SDL_Delay(1000//30)

    screen.destroy()
    return 0


def game_list():
    ipath = '/home/michael/Roms/genesis/media/images'
    files = [os.path.join(ipath,f) for f in os.listdir(ipath)[:15] if f.endswith('.png')]
    for fn in files:
        images.load(fn)
    image = images.load(random.choice(images.cache))

    select = Region(screen, d['list'], images, fonts)
    title.select = select

    running = 1
    while running:
        if not running % 90:
            update = True
            image = images.load(random.choice(images.cache))

if __name__ == "__main__":
    main()
    sys.exit()