import sys, os, random, json
import sdl2, sdl2.ext
from gui import *

image_path = '/home/michael/Roms/genesis/media/images'


def main():
    background = Region(config['background'])
    mainlist = Region(config['mainlist'])
    maininfo = Region(config['maininfo'])
    mainlist.select = Region(config['list'])
    buttons = images.load_atlas('buttons.png', config['buttons.png'])

    blist = list(buttons.keys()) ; picked = 0 ; where = Rect(340,240, 90,90)

    update = True
    running = 1
    while running:
        running += 1
        inp.process()
        update = mainlist.update(inp) or update

        if inp.quit:
            running = False
        if inp.pressed:
            #print(inp.pressed)
            if inp.pressed in ('A', 'start'):
                update = True
                selected = mainlist.list[mainlist.selected]
                if selected == 'Exit':
                    running = 0
                elif selected == 'Install Port':
                    sounds.play('click')
                    game_list()
                elif selected == "Onscreen Keyboard":
                    print(key_test('default'))
                elif selected == "Option Menu":
                    option_test()
            elif inp.pressed == 'right':
                picked += 1
                update = True
            elif inp.pressed == 'left':
                picked -= 1
                update = True
            picked = picked % len(blist)

        if update or inp.update:
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

def key_test(text):
    key1 = [
        '1234567890',
        'qwertyuiop',
        'asdfghjkl"',
        'zxcvbnm,.?',
        (' ^ ', ' __ ', 'left', None, 'DONE')]
    key2 = [
        '1234567890',
        'QWERTYUIOP',
        'ASDFGHJKL"',
        'ZXCVBNM,.?',
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
    return keyboard(d, key1, key2, text)


def option_test():
    region = {
            "area": [.05,0.2,0.95,0.95],
            "fill": [230,230,230],
            "font": "Roboto.ttf",
            'align': 'center',
            "fontsize": 32, 
            "fontcolor": [0,0,0],
            "barspace": 8,
            #"barwidth": None,
            "roundness": 12}
    options = {
        "Enabled Option": "checked",
        "Disabled Thing": "unchecked",
        "Three Options": ["One", "Two", "Three"],
        "A Label": None,
        "Selectable": "Message",
        "Four Options": ["One", "Two", "Three", "Extra"],
        "Clicked": "checked",
        "Another": "Message",
        "Five Options": ["One", "Two", "Three", "Extra", "V"],
        "Volume": range_list(60, 0, 100, 7),
        "Click Me Please": "unchecked",
        "Nothing": None,
        "Labels": None
        }
    r = option_menu(region, options, config['background'])
    




def game_list():
    #global config, screen, fonts, images, inp
    files = sorted([os.path.join(image_path,f) for f in os.listdir(image_path) if f.endswith('.png')])
    names = [os.path.splitext(os.path.split(f)[-1])[0] for f in files]

    background = Region(config['background'])
    gamelist = Region(config['gamelist'], name='gamelist')
    
    gamelist.select = Region(config['list'])
    gamelist.select.fontsize = gamelist.fontsize
    gametext = Region(config['gametext'], name='gametext')
    gameimage = Region(config['gameimage'], name='gameimage')
    if 'gamebar' in config:
        gamebar = Region(config['gamebar'], name='gambar')

    background.text = names[0]
    gamelist.list = names

    running = update = 1
    while running:
        inp.process()
        running = 1 if gamelist.update(inp) else running + 1

        if inp.quit:
            running = 0
        if inp.pressed:
            if inp.pressed == 'right':
                gamelist.selected += gamelist.page_size
                sounds.play('click')
                running = 1
            elif inp.pressed == 'left':
                gamelist.selected -= gamelist.page_size
                sounds.play('click')
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
        
        if gametext.update(inp):
            update = True
        
        if update:
            background.draw()
            gametext.draw()
            gameimage.draw()
            if 'gamebar' in config:
                gamebar.draw()
            gamelist.draw()

            screen.present()
        sdl2.timer.SDL_Delay(1000//30)
        update = False

if __name__ == "__main__":
    config, screen, fonts, images, inp = init()
    main()
    sys.exit()