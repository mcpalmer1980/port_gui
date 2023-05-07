import sys, os, random, json
import sdl2, sdl2.ext
from rect import Rect
from utility import Rect, Image, ImageManager, FontManager
from gui import Region, InputHandler

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

    atlas = images.load_atlas('nine.png', d['nine.png'])
    title = Region(screen, d['title'], images, fonts)
    #title.list = game_list
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



if __name__ == "__main__":
    main()
    sys.exit()