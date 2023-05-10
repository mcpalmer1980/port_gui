import sys, os, random, json
import sdl2, sdl2.ext
from utility import Rect, Image, ImageManager, FontManager
from gui import Region, InputHandler

DEFAULT_SIZE= 480, 320
image_path = '/home/michael/Roms/genesis/media/images'

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

    buttons = images.load_atlas('buttons.png', config['buttons.png'])

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
                update = True
                selected = mainlist.list[mainlist.selected]
                if selected == 'Exit':
                    running = 0
                if selected == 'Install Port':
                    game_list()

        if update:
            mainlist.selected = mainlist.selected % len (mainlist.list)
            maininfo.text = config['mainlist']['info'][mainlist.selected]
            background.draw()
            mainlist.draw()
            maininfo.draw()


        screen.present()
        #window.refresh()
        sdl2.timer.SDL_Delay(1000//30)
        update = False

    screen.destroy()
    return 0




def game_list():
    global config, screen, fonts, images, inp
    files = sorted([os.path.join(image_path,f) for f in os.listdir(image_path) if f.endswith('.png')])
    names = [os.path.splitext(os.path.split(f)[-1])[0] for f in files]

    '''
    for fn in files:
        images.load(fn)
    image = images.load(random.choice(images.cache))

    select = Region(screen, d['list'], images, fonts)
    title.select = select
    '''
    background = Region(screen, config['background'], images, fonts)
    gamelist = Region(screen, config['gamelist'], images, fonts)
    gametext = Region(screen, config['gametext'], images, fonts)
    gameimage = Region(screen, config['gameimage'], images, fonts)
    gamebar = Region(screen, config['gamebar'], images, fonts)

    background.text = names[0]
    gamelist.list = names

    running = update = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)

        if inp.quit:
            running = 0
        if inp.pressed:
            if inp.pressed == 'up':
                gamelist.selected -= 1
                running = 1
            elif inp.pressed == 'down':
                gamelist.selected += 1
                running = 1
            elif inp.pressed == 'right':
                gamelist.selected += gamelist.page_size
                running = 1
            elif inp.pressed == 'left':
                gamelist.selected -= gamelist.page_size
                running = 1
            elif inp.pressed in ('start', 'select'):
                running = 0

        if running == 1:
            background.text = names[gamelist.selected]
            update = True
            gametext.text = ''
            gameimage.image = None
        elif running == 20:
            im = images.load(files[gamelist.selected])
            gameimage.image = im
            gametext.text = files[gamelist.selected].replace('/', ' ') * 5
            update = True
            print(files[gamelist.selected])
        
        if gametext.update():
            update = True
        
        if update:
            background.draw()
            gamelist.draw()
            gametext.draw()
            gameimage.draw()
            gamebar.draw()

        screen.present()
        sdl2.timer.SDL_Delay(1000//30)
        update = False

if __name__ == "__main__":
    main()
    sys.exit()