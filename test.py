import sys, os, random, json
import sdl2, sdl2.ext
from rect import Rect
from tfont import FontManager
from gui import ImageManager, Region

screen_size = 640,480
desc = "Dungeon & Dragons: Warriors of the Eternal Sun is set in the world of Mystara, a setting of the Dungeons & Dragons game. The characters find themselves in a strange, red-hued world in which the horizon slopes upward in all directions, eventually vanishing into a crimson haze at the limits of sight. Their mission is to find and make allies in this new world or else the kingdom and its culture will perish."


def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("Harbour Master", size=(640, 480))
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED)
    screen.clear((255,0,0))
    fonts = FontManager(screen)
    tf = fonts.load('font.ttf', 25)
    f = fonts.load('font2.ttf', 30)

    with open('data.json') as inp:
        d = json.load(inp)

    images = ImageManager(screen)
    ipath = '/home/michael/Roms/genesis/media/images'
    files = [os.path.join(ipath,f) for f in os.listdir(ipath)[:15] if f.endswith('.png')]
    for fn in files:
        images.load(fn)
    texture = images.load(random.choice(images.cache))

    title = Region(screen, d['title'], images, fonts)
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
        #fonts.draw(desc, 20,60, (0,0,255), clip=Rect(10,10, 500,200), wrap=-10, align='center')
        title.draw()
        screen.present()
        window.refresh()
        sdl2.timer.SDL_Delay(1000//30)

        if not running % 90:
            texture = images.load(random.choice(images.cache))
    return 0




if __name__ == "__main__":
    main()
    sys.exit()