'''
Copyright (C) 2020, Michael C Palmer <michaelcpalmer1980@gmail.com>

This file is part of pySDL2gui

pySDL2gui is a python package providing higher level features for
pySDL2. It uses the pySDL2.ext API to provide hardware GPU
texture rendering.

pySDL2gui is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
pytmx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public
License along with pySDL2gui.

If not, see <http://www.gnu.org/licenses/>.
'''
import os, sys, json
import sdl2, sdl2.ext

_version = '0.0.1'
if True:
    print('pySDL2gui {} running on pySDL2 {}.{}.{} (python {}.{}.{})\n'.format(
            _version, *sdl2.version_info, *sys.version_info[:3]))


global config, screen, fonts, images, inp
config = screen = fonts = images = inp = None
from .utility import *
from .gui import *

DEFAULT_SIZE = 480, 320

def init():
    with open('theme.json') as inp:
        config = json.load(inp)
    if os.path.isfile('defaults.json'):
        with open('defaults.json') as inp:
            defaults = json.load(inp)
        config = deep_update(defaults, config)
    deep_print(config, 'config')

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

    if 'sounds' in config:
        PlaySound.init()
        for k, v in config['sounds'].items():
            print('loading sound: ', v)
            PlaySound.load(v, k)
    if config['options'].get('music'):
        PlaySound.init()
        PlaySound.music(config['options']['music'], volume=.3)

    defaults = config.get('defaults', {})
    print('Defaults:', defaults)
    Region.set_defaults(defaults, screen, images, fonts)

    gui.set_globals(config, screen, images, fonts, inp)
    utility.set_globals(config, screen, images, fonts, inp)

    return config, screen, fonts, images, inp
