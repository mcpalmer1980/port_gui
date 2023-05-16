import sys, os, random, json
import sdl2, sdl2.ext
from utility import Rect, Image, ImageManager, FontManager, SoundManager
from gui import Region, InputHandler

DEFAULT_SIZE = 480, 320
image_path = '/home/michael/Roms/genesis/media/images'
PlaySound = SoundManager('assets')

def main():
    global config, screen, fonts, images, inp

    with open('theme.json') as inp:
        config = json.load(inp)
    if os.path.isfile('defaults.json'):
        with open('defaults.json') as inp:
            defaults = json.load(inp)
        defaults.update(config) # TODO DEEP UPDATE
        config = defaults
    logical_size = config.get('options', {}).get('logical_size', DEFAULT_SIZE)

    sdl2.ext.init()
    mode = sdl2.ext.displays.DisplayInfo(0).current_mode
    if 'window' in sys.argv:
        screen_size = config['options'].get('screen_size') or logical_size
        flags = None
    else:
        screen_size = config['options'].get('screen_size') or mode.w, mode.h
        flags = sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP # TODO should not use fullscreen_desktop on actual device
    print(f'Current display mode: {mode.w}x{mode.h}@{mode.refresh_rate}Hz')
    print(f'Logical Size: {logical_size}, Screen Size: {screen_size}')

    window = sdl2.ext.Window("Harbour Master",
            size=screen_size, flags=flags)
    screen = sdl2.ext.renderer.Renderer(window,
            flags=sdl2.SDL_RENDERER_ACCELERATED, logical_size=logical_size)
    screen.clear((0,0,0))
    sdl2.ext.renderer.set_texture_scale_quality('linear') #nearest, linear, best

    Image.renderer = screen
    images = ImageManager(screen)
    fonts = FontManager(screen)
    inp = InputHandler()
    window.show()

    if 'click' in config['options']:
        PlaySound.init()
        PlaySound.load(config['options']['click'])
    if 'music' in config['options']:
        PlaySound.init()
        PlaySound.music(config['options']['music'])

    background = Region(screen, config['background'], images, fonts)
    mainlist = Region(screen, config['mainlist'], images, fonts)
    maininfo = Region(screen, config['maininfo'], images, fonts)
    mainlist.select = Region(screen, config['list'], images, fonts)
    buttons = images.load_atlas('buttons.png', config['buttons.png'])

    blist = list(buttons.keys()) ; picked = 0 ; where = Rect(340,240, 90,90)

    update = True
    running = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)

        if inp.quit:
            running = False
        if inp.pressed:
            #print(inp.pressed)
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
                    print(keyboard('default'))
            elif inp.pressed == 'right':
                picked += 1
                update = True
            elif inp.pressed == 'left':
                picked -= 1
                update = True
            picked = picked % len(blist)

        if update:
            mainlist.selected = mainlist.selected % len (mainlist.list)
            maininfo.text = config['mainlist']['info'][mainlist.selected]
            background.draw()
            mainlist.draw()
            maininfo.draw()

            r = Rect.from_sdl(buttons[blist[picked]].srcrect) * 0.5
            r.topleft = (340,240)
            buttons[blist[picked]].draw_in(r.sdl())
            fonts.draw(blist[picked], 340, 400, color=(0,0,0))

            screen.present()

        sdl2.timer.SDL_Delay(1000//30)
        update = False

    screen.destroy()
    return 0


def keyboard(text=''):
    kbl = [
        list('1234567890'),
        list('qwertyuiop'),
        list('asdfghjkl"'),
        list('zxcvbnm,.?'),
        (' ^ ', ' __ ', ' << ', None, 'DONE')]
    kbu = [
        list('1234567890'),
        list('QWERTYUIOP'),
        list('ASDFGHJKL"'),
        list('ZXCVBNM,.?'),
        (' ^ ', ' __ ', ' << ', None, 'DONE')]

    d = {
        "area": [.05,0.2,0.95,0.95],
        "fill": [230,230,230],
        "font": "Roboto.ttf",
        "fontsize": 60,
        "fontcolor": [0,0,0],
        "barspace": 0,
        "barwidth": 50,
        "roundness": 12}

    upper = False
    fakeimages = ImageManager(screen)
    keyboard = Region(screen, d, fakeimages, fonts)
    keyboard.list = kbl
    kb = [[k for k in row if k] for row in keyboard.list]
    keyboard.selected = keyboard.selectedx = 1
    keyboard.select = Region(screen, config['list'], images, fonts)
    keyboard.select.fontsize = keyboard.fontsize
    keyboard.select.align = 'center'
    background = Region(screen, config['background'], images, fonts)
    background.fontsize = keyboard.fontsize
    background.borderx = keyboard.area.x
    #background.align = 'topright'
    
    background.text = old_text = text
    running = update = 1
    while running:
        running += 1
        events = sdl2.ext.get_events()
        inp.process(events)

        if inp.pressed:
            update = True
            if inp.quit or inp.pressed in ('select', 'B'):
                return ''
            if inp.pressed == 'up':
                keyboard.selected = (keyboard.selected - 1) % len(keyboard.list)
                keyboard.selectedx = min(max(keyboard.selectedx, 0), len(kb[keyboard.selected])-1)
            elif inp.pressed == 'down':
                keyboard.selected = (keyboard.selected + 1) % len(keyboard.list)
                keyboard.selectedx = min(len(kb[keyboard.selected])-1, max(keyboard.selectedx, 0))
            elif inp.pressed == 'right':
                keyboard.selectedx = (keyboard.selectedx+1) % len(kb[keyboard.selected])
            elif inp.pressed == 'left':
                keyboard.selectedx = (keyboard.selectedx-1) % len(kb[keyboard.selected])
            elif inp.pressed == 'start':
                return text.replace('_', ' ')
            elif inp.pressed in ('X', 'Y'):
                    keyboard.list = kbl if upper else kbu
                    upper = not upper
                    kb = [[k for k in row if k] for row in keyboard.list]
            elif inp.pressed == 'L':
                text = text[:-1]
            elif inp.pressed == 'R':
                text += '_'
            elif inp.pressed == 'A':
                key = kb[keyboard.selected][keyboard.selectedx]
                if len(key) == 1:
                    text += key
                elif key == ' __ ':
                    text += '_'
                elif key == ' << ':
                    text = text[:-1]
                elif key == ' ^ ':
                    keyboard.list = kbl if upper else kbu
                    upper = not upper
                    kb = [[k for k in row if k] for row in keyboard.list]
                elif key == 'DONE':
                    return text.replace('_', ' ')

            if text != old_text:
                background.text = text
                if fonts.width(text) > keyboard.area.width:
                    background.align = 'topright'
                else: background.align = 'topleft'

        if update:
            background.draw()
            keyboard.draw()
            screen.present()
            old_text = text
        update = False
        sdl2.timer.SDL_Delay(1000//30)
    




def game_list():
    #global config, screen, fonts, images, inp
    files = sorted([os.path.join(image_path,f) for f in os.listdir(image_path) if f.endswith('.png')])
    names = [os.path.splitext(os.path.split(f)[-1])[0] for f in files]

    background = Region(screen, config['background'], images, fonts)
    gamelist = Region(screen, config['gamelist'], images, fonts)
    
    gamelist.select = Region(screen, config['list'], images, fonts)
    gamelist.select.fontsize = gamelist.fontsize
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