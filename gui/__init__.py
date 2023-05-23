"""
Copyright (C) 2020, Michael C Palmer <michaelcpalmer1980@gmail.com>

This file is part of pySDL2gui

pySDLgui is a simple, low level gui module that handles input and draws multiple
rectangular Regions using hardware GPU rendering. Written in python, pySDLgui
uses pySDL2, a low level SDL2 wrapper also written in pure python with no other
dependencies.

This module is designed to produce full screen GUIs for lower powered
GNU/Linux based retro handhelds using game controller style input, but it may
prove useful on other hardware.

The main building block of GUIs built with this module is the Region, which
represents a rectangular area that can display text, lists, and images. Each
Region has numerous attributes that should be defined in theme.json or
defaults.json and can be used to change the look and feel of a GUI without
change the program's code.

CLASSES:
    FontManager: class used to load and render fonts onto a pySDL
        render context
    Image: simple class to represent and draw textures and subtexture
        regions onto a pySDL render context
    ImageManager: class to load and cache images as Image objects in
        texture memory
    InputHandler: handles controller and keyboard input, mapping to simple
        string events such as 'up', 'left', 'A', and 'start'
    Rect: class used to represent and modify Rectangular regions
    Region: draws a rectangular region with a backround, outline, image,
        lists, etc. The main building block of pySDL2gui GUIs
    SoundManager: class used to load and play sound effects and music

DATA:
    AXIS_MAP: maps controller axis to input strings ('left', 'start', 'A', etc.)
    BUTTON_MAP: maps controller buttons to input strings 
    KEY_MAP: maps keyboard keys to input strings
    char_map: a string with each character that FontManager should be able to draw

FUNCTIONS:
    deep_merge: used internally to merge option dicts
    deep_print: available to display nested dict items or save them to disk
    deep_update: used internally to update an options dict from a second one
    get_color_mod: get the color_mod value of a texture (not working)
    get_text_size: get the size a text string would be if drawn with given font
    keyboard: displays an onscreen keyboard to enter or edit a text string
    make_option_bar: displays a scrolling options menu to edit options
    range_list: generate a list of numerical values to select from in a option
        menu, similar to a slider widget
    set_color_mod: set the color_mod value of a texture (not working)
    set_globals: sets the modules global values within this file's scope

GLOBAL OBJECTS:
    config: a dict full of options and Region definitions loaded from theme.json
        and default.json
    fonts: a FontManager used to render all the fonts used by pySDL2gui
    images: an ImageManager used to draw all the images used by pySDL2gui
    inp: an InputManager used to handle input from sdl2 events
    sounds: a SoundManager used to play sounds and music within pySDL2gui
    RESOURCES: a resource manager used to load resources from the assets subfolder
    screen: a sdl2.ext.Renderer context that pySDL2gui displays graphics into

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
"""

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
        sounds.init()
        for k, v in config['sounds'].items():
            print('loading sound: ', v)
            sounds.load(v, k)
    if config['options'].get('music'):
        sounds.init()
        sounds.music(config['options']['music'], volume=.3)

    defaults = config.get('defaults', {})
    print('Defaults:', defaults)
    Region.set_defaults(defaults, screen, images, fonts)

    gui.set_globals(config, screen, images, fonts, inp)
    utility.set_globals(config, screen, images, fonts, inp)

    return config, screen, fonts, images, inp
