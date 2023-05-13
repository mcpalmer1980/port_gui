import sys, os, random, json
import sdl2, sdl2.ext
from utility import Rect, Image, ImageManager, FontManager, SoundManager
from gui import Region, InputHandler

DEFAULT_SIZE = 480, 320
image_path = '/home/michael/Roms/genesis/media/images'
PlaySound = SoundManager('assets')

def main():
    global config, screen, fonts, images, inp

    with open('data.json') as inp:
        config = json.load(inp)
    display_size = config.get('options', {}).get('display_size', DEFAULT_SIZE)

    sdl2.ext.init()
    mode = sdl2.ext.displays.DisplayInfo(0).current_mode
    print(f'Current display mode: {mode.w}x{mode.h}@{mode.refresh_rate}Hz')
    size = mode.w, mode.h
    size = display_size

    window = sdl2.ext.Window("Harbour Master",
            size=size, )
            #flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED, logical_size=display_size)
    screen.clear((0,0,0))
    sdl2.ext.renderer.set_texture_scale_quality('best')

    Image.renderer = screen
    images = ImageManager(screen)
    fonts = FontManager(screen)
    inp = InputHandler()
    window.show()

    if 'click' in config['options']:
        PlaySound.init()
        PlaySound.load(config['options']['click'])

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
                PlaySound('click')
            elif inp.pressed == 'down':
                update = True
                mainlist.selected += 1
                PlaySound('click')
            elif inp.pressed in ('A', 'start'):
                update = True
                selected = mainlist.list[mainlist.selected]
                if selected == 'Exit':
                    running = 0
                elif selected == 'Install Port':
                    PlaySound('click')
                    game_list()
                elif selected == "Remove Port":
                    keyboard()

        if update:
            mainlist.selected = mainlist.selected % len (mainlist.list)
            maininfo.text = config['mainlist']['info'][mainlist.selected]
            background.draw()
            mainlist.draw()
            maininfo.draw()
            screen.present()

        sdl2.timer.SDL_Delay(1000//30)
        update = False

    screen.destroy()
    return 0


def keyboard():
    kbl = [ [' '],
        list('1234567890'),
        list('qwertyuiop'),
        list('asdfghjkl'),
        list('zxcvbnm.,'),
        (' ^ ', ' __ ', ' << ', 'DONE')]
    kbu = [ [' '],
        list('1234567890'),
        list('QWERTYUIOP'),
        list('ASDFGHJKL'),
        list('ZXCVBNM.,'),
        (' ^ ', ' __ ', ' << ', 'DONE')]

    d = {
        "area": [0,0,1.0,1.0],
        "fill": [60,60,60],
        "font": "Roboto.ttf",
        "fontsize": 60,
        "fontcolor": [0,0,0],
        "barspace": 8,
        "barwidth": 50}

    upper = False
    fakeimages = ImageManager(screen)
    keyboard = Region(screen, d, fakeimages, fonts)
    kb = kbl
    keyboard.list = kb
    keyboard.selected = keyboard.selectedx = 1
    text = ''
    
    running = update = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)


        if inp.pressed:
            print(inp.pressed)
            if inp.quit or inp.pressed in ('B', 'start'):
                running = 0
                break
            if inp.pressed == 'up':
                keyboard.selected -= 1
                update = True
                keyboard.selected = keyboard.selected if keyboard.selected > 0 else 5
                keyboard.selectedx = min(max(keyboard.selectedx, 0), len(kb[keyboard.selected])-1)
            if inp.pressed == 'down':
                keyboard.selected += 1
                update = True
                keyboard.selected = keyboard.selected if keyboard.selected <= 5 else 1
                keyboard.selectedx = min(len(kb[keyboard.selected])-1, max(keyboard.selectedx, 0))
            if inp.pressed == 'right':
                keyboard.selectedx = (keyboard.selectedx+1) % len(kb[keyboard.selected])
                update = True
            if inp.pressed == 'left':
                keyboard.selectedx = (keyboard.selectedx-1) % len(kb[keyboard.selected])
                update = True
            if inp.pressed == 'A':
                key = kb[keyboard.selected][keyboard.selectedx]
                if len(key) == 1:
                    text += key
                elif key == ' __ ':
                    text += ' '
                elif key == ' << ':
                    text = text[:-1]
                elif key == ' ^ ':
                    kb = kbl if upper else kbu
                    upper = not upper
                    keyboard.list = kb
                keyboard.list[0][0] = text
                update = True

        if update:
            keyboard.draw()
            screen.present()
        update = False
        sdl2.timer.SDL_Delay(1000//30)
    




def game_list():
    #global config, screen, fonts, images, inp
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
    if 'gamebar' in config:
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
                PlaySound('click')
                running = 1
            elif inp.pressed == 'down':
                gamelist.selected += 1
                PlaySound('click')
                running = 1
            elif inp.pressed == 'right':
                gamelist.selected += gamelist.page_size
                PlaySound('click')
                running = 1
            elif inp.pressed == 'left':
                gamelist.selected -= gamelist.page_size
                PlaySound('click')
                running = 1
            elif inp.pressed in ('start', 'select'):
                running = 0

        if running == 1:
            background.text = names[gamelist.selected % len(gamelist.list)]
            update = True
            gametext.text = ''
            gameimage.image = None
        elif running == 20:
            im = images.load(files[gamelist.selected])
            gameimage.image = im
            gametext.text = files[gamelist.selected].replace('/', ' ') * 5
            update = True
        
        if gametext.update():
            update = True
        
        if update:
            background.draw()
            gamelist.draw()
            gametext.draw()
            gameimage.draw()
            if 'gamebar' in config:
                gamebar.draw()

            screen.present()
        sdl2.timer.SDL_Delay(1000//30)
        update = False

if __name__ == "__main__":
    main()
    sys.exit()