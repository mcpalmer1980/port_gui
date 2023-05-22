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
    InputHandler: handles controller and keyboard input, mapping to simple
        string events such as 'up', 'left', 'A', and 'start'
    Region: draws a rectangular region with a backround, outline, image,
        lists, etc. The main building block of pySDL2gui GUIs

FUNCTIONS:
    keyboard: displays an onscreen keyboard to enter or edit a text string
    make_option_bar: displays a scrolling options menu to edit options
    set_globals: sets the modules global values within this file's scope

DATA:
    AXIS_MAP: maps controller axis to input strings ('left', 'start', 'A', etc.)
    BUTTON_MAP: maps controller buttons to input strings 
    KEY_MAP: maps keyboard keys to input strings
    char_map: a string with each character that FontManager should be able to draw

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
import os, sys
import sdl2, sdl2.ext, sdl2.sdlmixer
from .utility import *

try:
    import sdl2.sdlgfx as sdlgfx
except:
    sdlgfx = False

'''
TODO
    Fix image/text confusion in bars
    Text horiz scrolling
    Text animation (rotation, scaling, color changing)
    Tiled image rendering
    Deque the cache list
    Alpha colors for fill and outline
    Alpha for images
'''

'''
    FILL MODE
    area: 4-tuple of pixels or screen percent(0.0-1.0),
    color: 3-tuple fill color
    outline: 3-typle outline color
    thickness: int outline thickness,
    roundness: int outline roundness,
    border: int border around text x or x&y
    bordery: int top/bottom border around text
    
    IMAGE RENDERING
    image: filename for image
    imagerect: 4-tuple (x,y,w,h) region of image to use
    imagesize: 2-tuple (w,h) scale to this size
    imagemode: 'fit', 'stretch', 'repeat', None or ''
    imagealign: same options as text align, but for image
    patch: 4-tuple left, top, right, bottom edges for 9-patch rendering
    pimage: filename or image to use for patch if different than image
    pattern: bool image is a base64 string

    TEXT RENDERING
    font: filename for font
    fontsize: int size of font
    fontcolor: 3-tuple font color
    text: text string (may be multiline)
    wrap: allow multiline text wraping
    linespace: int extra space between lines
    align: text alignment (topleft, topright, midtop
                           midleft, center, midright
                           bottomleft, midbottom, bottomright)

    LIST RENDERING
    list: list of items (ignores wrap, allows navigation)
    imagelist: list of filenames or Image objects
    ilistalign: alignment for list images
    itemsize: item height for vertical lists (width for horiz ones)
    selected: 3-tuple color for selected item, or a Region for rendering it
    scrollable: bool allow up/down to scroll wrapped text
    autoscroll: int speed of auto scroll or 0 disables
'''

class Region:
    '''
    For drawing a rectangular region on a renderer context
    Regions may have a fill color, outline, image, and/or text
    Attributes are loaded from a dict or json file
    
    area, color, thickness, outline, roundness, 
    image, pattern, repeat, stretch
    borderx, border
    font, fontsize, fontcolor, text, align
    scrollable, autoscroll, wrap, linespace
    '''
    DATA = {}; RENDERER=None; IMAGES=None; FONTS=None
    def __init__(self, data, renderer=None, images=None, fonts=None, name=''):
        'Create a new Region for future drawing.'
        self.name=name
        self._dict = deep_merge(self.DATA, data)

        self.renderer = renderer or Region.RENDERER
        self.images = images or Region.IMAGES
        self.fonts = fonts or Region.FONTS

        self.area = self._verify_rect('area')
        self.fill = self._verify_color('fill', optional=True)
        self.outline = self._verify_color('outline', optional=True)
        self.thickness = self._verify_int('thickness', 0)
        self.roundness = self._verify_int('roundness', 0)
        self.borderx = self._verify_int('border', 0)
        self.bordery = self._verify_int('bordery', self.borderx) or 0
        self.borderx = self._verify_int('borderx', self.borderx)

        self.image = self.images.load(self._dict.get('image'))
        self.imagesize = self._verify_ints('imagesize', 2, None, optional=True)
        self.imagemode = self._verify_option('imagemode', 
                ('fit', 'stretch', 'repeat', None), 'fit')
        self.imagealign = self._verify_option('imagealign', Rect.POINTS, None)
        self.patch = self._verify_ints('patch', 4, optional=True)
        self.pimage = self.images.load(self._dict.get('pimage'))
        if self.patch and not self.pimage:
            self.pimage = self.image
            self.image = None

        self.pattern = False
        
        # TODO figure out how to use default/system fonts
        self.font = self._verify_file('font', optional=True)
        self.fontsize = self._verify_int('fontsize', 30)
        self.fontcolor = self._verify_color('fontcolor', (255,255,255))
        self._text = self._verify_text('text', optional=True)
        self.wrap = self._verify_bool('wrap', False, True)
        self.linespace = self._verify_int('linespace', 0, True)
        self.align = self._verify_option('align', Rect.POINTS, 'topleft')

        self.list = self._verify_list('list', optional=True)
        self.selectable = None
        self.imagelist = 0 ## TODO
        self.ilistalign = 0 ## TODO
        self.itemsize = self._verify_int('itemsize', None, True)
        self.select = self._verify_color('selected', optional=True)

        self.click_sound = self._verify_text('click_sound', optional=True)
        self.cancel_sound = self._verify_text('cancel_sound', optional=True)

        self.scrollable = self._verify_bool('scrollable', False, True)
        self.autoscroll = self._verify_int('autoscroll', 0, True)

        self.barspace = self._verify_int('barspace', 4)
        self.barwidth = self._verify_int('barwidth', 0, optional=True)
        self._bar = self._verify_bar('bar', optional=True)

        if self._text and self.list:
            raise Exception('Cannot define text and a list')

        self.scroll_pos = 0
        self.scroll_delay = -self.autoscroll*2
        self.selected = 0
        self.selectedx = -1

    def set_defaults(data, renderer, images, fonts):
        '''
        Set global defaults for all Regions to reduce later parameter requirements

        data: a dict of Region parameters that will apply to all regions, but will
            be overriden by parameters sent when creating Region objects later
        renderer: a sdl2.ext.renderer context to draw onto
        images: a gui.ImageManager reference for loading images
        fonts: a gui.FontManager reference for loading fonts
        '''
        Region.DATA = data
        Region.RENDERER = renderer
        Region.IMAGES = images
        Region.FONTS = fonts

    def draw(self, area=None, text=None, image=None):
        '''
        Draw all features of this Region
        
        area: override Region's area, used internally
        text: override Region's text and list, used internally
        image: override Region's image, used internally
        '''

        area = area or self.area.copy()
        image = image or self.image

        # FILL AND OUTLINE  
        if self.patch:
            self._draw_patch(area, self.pimage)
            area = Rect.from_corners(
                area.x + self.patch[0], area.y + self.patch[1], 
                area.right - self.patch[2], area.bottom - self.patch[3])

        elif self.fill and self.outline:
            if self.roundness and sdlgfx:
                sdlgfx.roundedBoxRGBA(self.renderer.sdlrenderer,
                    area.x, area.y, area.right, area.bottom,
                    self.roundness, *self.outline, 255)
            area.inflate(-self.thickness)               
            if self.roundness and sdlgfx:
                sdlgfx.roundedBoxRGBA(self.renderer.sdlrenderer,
                    area.x, area.y, area.right, area.bottom,
                    self.roundness, *self.fill, 255)

            else:
                self.renderer.fill(area.sdl(), self.outline)
                area.inflate(-self.thickness)                
                self.renderer.fill(area.sdl(), self.fill)

        elif self.fill:
            if self.roundness and sdlgfx:
                sdlgfx.roundedBoxRGBA(self.renderer.sdlrenderer,
                    area.x, area.y, area.right, area.bottom,
                    self.roundness, *self.fill, 255)
            else:
                self.renderer.fill(area.sdl(), self.fill)

        elif self.outline:
            r = area.sdl()
            for _ in range(self.thickness-1):
                if self.roundness and sdlgfx:
                    sdlgfx.roundedRectangleRGBA(self.renderer.sdlrenderer,
                        r.x, r.y, r.x+r.w, r.y+r.h,
                        self.roundness, *self.outline, 255)
                else:
                    self.renderer.draw_rect(r, self.outline)
                r.x += 1; r.w -= 2
                r.y += 1; r.h -= 2
            area.size = area.w-self.thickness, area.h-self.thickness
 
        # RENDER IMAGE
        if self.image and not self.patch:
            image = self.image #s.load(self.image)
            dest = Rect.from_sdl(image.srcrect)
            if self.imagesize:
                dest.size = self.imagesize
            
            if self.imagemode == 'fit':
                dest.fit(area)
                if self.imagealign:
                    w = getattr(area, self.imagealign)
                    setattr(dest, self.imagealign, w)
                image.draw_in(dest.tuple())
            elif self.imagemode == 'stretch':
                image.draw_in(area.tuple())
            elif self.imagemode == 'repeat':
                pass # TODO

            else:
                dest.topleft = area.topleft
                image.draw_in(dest.clip(area).tuple())

        text_area = area.inflated(-self.borderx*2, -self.bordery*2)

        if self.font and self.fontsize:
            self.fonts.load(self.font, self.fontsize)
        else:
            return

        # RENDER BAR (toolbarish)
        if self._bar:
            self._draw_bar(text_area, self._bar)

        # RENDER TEXT
        elif text:
            x, y = getattr(text_area, self.align, text_area.topleft)
            self.fonts.draw(text, x, y, self.fontcolor, 255,
                    self.align, text_area).height + self.linespace

        elif self._text:
            pos = self.scroll_pos % len(self._text)

            x, y = getattr(text_area, self.align, text_area.topleft)
            #y += self.linespace // 2
            for l in self._text[pos:]:
                if y + self.fonts.height > text_area.bottom:
                    break
                y += self.fonts.draw(l, x, y, self.fontcolor, 255,
                        self.align, text_area).height + self.linespace

        # RENDER LIST
        elif self.list:
            itemsize = self.itemsize or self.fonts.height + self.bordery
            self.page_size = area.height // itemsize
            self.selected = self.selected % len(self.list)

            self.fonts.load(self.font, self.fontsize)
            if len(self.list) > self.page_size:
                start = max(0, min(self.selected - self.page_size//3,
                        len(self.list)-self.page_size))
            else:
                start = 0

            irect = text_area.copy()
            irect.height = itemsize
            i = start
            for t in self.list[start: start + self.page_size]:
                if isinstance(t, (list, tuple)):
                    bar = self._verify_bar(None, t, irect)
                    if i == self.selected and self.selectedx >= 0:
                        x = self.selectedx
                    else: x = None
                    self._draw_bar(irect, bar, x)
                elif self.selected == i:
                    if isinstance(self.select, Region):
                        r = irect.inflated(self.borderx*2, self.bordery*2)
                        self.select.draw(irect, t)
                        self.fonts.load(self.font, self.fontsize)
                    else:
                        self.fonts.draw(t, *irect.midleft, self.select, 255,
                                'midleft', text_area)             
                else:           
                    self.fonts.draw(t,  *irect.midleft, self.fontcolor, 255,
                            "midleft", text_area)
                irect.y += itemsize
                i += 1

    def update(self, inp):
        '''
        Update current region based on given input and autoscrolling parameters

        inp: reference to an gui.InputHandler to receive input
        RETURNS: True if screen should redraw, otherwise False
        '''
        updated = False
        if self.autoscroll:
            self.scroll_delay += 1
            if self.scroll_delay >= self.autoscroll:
                self.scroll_pos += 1
                self.scroll_delay = 0
                if self.scroll_pos > len(self.text):
                    self.scroll_delay = -self.autoscroll
                    self.scroll_pos = 0
                updated = True

        elif self.text and self.scrollable:
            if inp.pressed == 'up':
                updated = True
                self.scroll_pos -= 1
            elif inp.pressed == 'down':
                self.scroll_pos += 1
                updated = True
            self.scroll_pos = min(max(0, self.scroll_pos), len(self.text)-1)

        elif self.list:
            l = len(self.list)
            selectable = self.selectable or range(l)
            selected = self.selected
            if inp.pressed == 'up':
                selected = (selected-1) % l
                while (selected) % l not in selectable:
                    selected = (selected-1) % l
                PlaySound(self.click_sound)
                updated = True
            elif inp.pressed == 'down':
                selected = (selected+1) % l
                while (selected) % l not in selectable:
                    selected = (selected+1) % l
                PlaySound(self.click_sound)
                updated = True
            if updated:
                self.selected = selected
        
        return updated
        
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, val):
        'Process text for proper wrapping when user changes it.'
        if self.wrap:
            self.fonts.load(self.font, self.fontsize)
            text_area = self.area.inflated(-self.borderx*2, -self.bordery*2)
            self._text = self.fonts._split_lines(val, text_area)
            self.scroll_delay = -self.autoscroll
            self.scroll_pos = 0
        else:
            self._text = val.split('\n')
        #print(f'text set to:\n{self._text}')
    
    @property
    def bar(self):
        return self._bar
    @bar.setter
    def bar(self, val):
        self._bar = self._verify_bar(None, val)

    def _verify_bar(self, name, default=None, area=None, optional=True):
        '''
        Process bar list for future display and selection. Used internally.

        name: key for Region dict to read bar list from
        default: default value is None
        area: override Region's area, used internally
        '''
        vals = self._dict.get(name, default)
        if vals == None and optional: return None

        if not isinstance(vals, (list, tuple)):
            raise Exception("bar is not a list")
        vals = [None if v == '' else v for v in vals]
        if vals.count('None') > 1:
            raise Exception('bar has more than one null value separator')

        if not area:
            area = self.area
            if self.patch:
                area = Rect.from_corners(
                    area.x + self.patch[0], area.y + self.patch[1], 
                    area.right - self.patch[2], area.bottom - self.patch[3])
            else:
                area = area.inflated(-self.borderx*2, -self.bordery*2)

        self.fonts.load(self.font, self.fontsize)
        x = area.x
        y = area.centery

        items = left = []; right = []
        for i, v in enumerate(vals):
            im = v if isinstance(v, Image) else self.images.load(v)
            if im:
                dest = Rect.from_sdl(im.srcrect).fitted(area)
                dest.x = x
                dest.width = max(dest.w, self.barwidth)
                x = dest.right + self.barspace
                items.append((dest, im))
            elif isinstance(v, str):
                w = self.fonts.width(v)
                dest = Rect(x, y, max(w, self.barwidth), self.fonts.height)
                dest.centery = area.centery
                x = dest.right + self.barspace
                items.append((dest, v))
            elif v == None:
                items = right
            else:
                raise Exception(f'bar item {i}({v}) not valid type')
        x = area.right
        for dest, item in right:
            dest.right = x
            x -= dest.width + self.barspace

        return left + right

    def _draw_bar(self, area, bar, selected=None):
        '''
        Draw bar in given area. Used internally
        '''
        #mode, self.renderer.blendmode = self.renderer.blendmode, sdl2.SDL_BLENDMODE_BLEND
        #self.fonts.load(self.font, self.fontsize)

        for i, (dest, item) in enumerate(bar):
            if i == selected:
                if isinstance(self.select, Region):
                    if isinstance(item, Image):
                        image = item; text = None
                    else:
                        color = None
                        text = item; image = None
                    r = dest.inflated(self.borderx*2, self.bordery*2)
                    self.select.draw(dest, text, image)
                    self.fonts.load(self.font, self.fontsize)
                
                else:
                    self.renderer.fill(dest.tuple(), [0,0,255,100])

                    if isinstance(item, Image):
                        item.draw_in(Rect.from_sdl(item.srcrect).fitted(dest).tuple())
                    else:
                        x, y = dest.center
                        self.fonts.draw(item, x, y,
                                self.fontcolor, 255, 'center', area)

            elif isinstance(item, Image):
                item.draw_in(Rect.from_sdl(item.srcrect).fitted(dest).tuple())
            else:
                x, y = dest.center
                self.fonts.draw(item, x, y,
                        self.fontcolor, 255, 'center', area)
        #self.renderer.blendmode = mode


    def _draw_patch(self, area, image):
        '''
        Draw 9-patch image in given area
        ''' 
        target = area.copy()
        bounds = Rect.from_sdl(image.srcrect)
        texture = image.texture

        self.renderer.copy(texture,  # TOP
    			srcrect=(bounds.left, bounds.top, self.patch[0], self.patch[1]),
    			dstrect=(target.left, target.top, self.patch[0], self.patch[1]) )
        self.renderer.copy(texture,  # LEFT
    		srcrect=(bounds.left, bounds.top+self.patch[1], self.patch[0],
    				bounds.height-self.patch[1]-self.patch[3]),
    		dstrect=(target.left, target.top+self.patch[1], self.patch[0],
    				target.height-self.patch[1]-self.patch[3]) )
        self.renderer.copy(texture,  # BOTTOM-LEFT
    		srcrect=(bounds.left, bounds.bottom-self.patch[3],
    				self.patch[0], self.patch[3]),
    		dstrect=(target.left, target.bottom-self.patch[3],
    				self.patch[0], self.patch[3]) )

        self.renderer.copy(texture, # TOP-RIGHT
            srcrect=(bounds.right-self.patch[2], bounds.top,
                    self.patch[2], self.patch[1]),
            dstrect=(target.right-self.patch[2], target.top,
                    self.patch[2], self.patch[1]) )		
        self.renderer.copy(texture, # RIGHT
            srcrect=(bounds.right-self.patch[2], bounds.top+self.patch[1],
                    self.patch[2],bounds.height-self.patch[3]-self.patch[1]),
            dstrect=(target.right-self.patch[2], target.top+self.patch[1],
                    self.patch[2], target.height-self.patch[3]-self.patch[1]) )
        self.renderer.copy(texture, # BOTTOM-RIGHT
            srcrect=(bounds.right-self.patch[2], bounds.bottom-self.patch[3],
                    self.patch[2], self.patch[3]),
            dstrect=(target.right-self.patch[2], target.bottom-self.patch[3],
                    self.patch[2], self.patch[3]) ) 

        self.renderer.copy(texture, # TOP
            srcrect=(bounds.left+self.patch[0], bounds.top,
                    bounds.width-self.patch[0]-self.patch[2], self.patch[1]),
            dstrect=(target.left+self.patch[0], target.top,
                    target.width-self.patch[0]-self.patch[2], self.patch[1]) )
        self.renderer.copy(texture, # CENTER
            srcrect=(bounds.left+self.patch[0], bounds.top+self.patch[1],
                    bounds.width-self.patch[2]-self.patch[0],
                    bounds.height-self.patch[1]-self.patch[3]),
            dstrect=(target.left+self.patch[0], target.top+self.patch[1],
                    target.width-self.patch[2]-self.patch[0],
                    target.height-self.patch[1]-self.patch[3]) )
        self.renderer.copy(texture, # BOTTOM
            srcrect=(bounds.left+self.patch[0], bounds.bottom-self.patch[3],
                    bounds.width-self.patch[0]-self.patch[2], self.patch[3]),
            dstrect=(target.left+self.patch[0], target.bottom-self.patch[3],
                    target.width-self.patch[0]-self.patch[2], self.patch[3]) )		


    def _verify_rect(self, name, default=None, optional=False):
        'Verify that value of self._dict[name] is a usable Rect'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        try:
            if len(val) != 4:
                raise Exception('Region area incorrect length')
        except TypeError:
            print('Region area not iterable')
            raise
        for i, p in enumerate(val):
            if not isinstance(p, (int, float)):
                raise Exception(f'point {i}{p} is not a number')
            if type(p)==float and 0 < p <= 1:
                val[i] = p * self.renderer.logical_size[i % 2]
        val = Rect.from_corners(*val)
        #print(f'{name}: {val}')
        return val

    def _verify_color(self, name, default=None, optional=False):
        'verify that value of self._dict[name] is valid RGB 3-tuple color'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        try:
            if len(val) != 3:
                raise Exception('color incorrect length')
        except TypeError:
            print('color not iterable')
            raise
        for i, p in enumerate(val):
            if not isinstance(p, (int)):                
                raise Exception(f'{i},{p} - invalid color type')
            if p<0 or p>255:
                raise Exception(f'{i},{p} - invalid color value')
        #print(f'{name}: {val}')
        return val

    def _verify_int(self, name, default=0, optional=False):
        'verify that value of self._dict[name] is valid int value'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, int):
            raise Exception(f'{name} is not an int')
        #print(f'{name}: {val}')
        return val
    
    def _verify_file(self, name, default=None, optional=False):
        ''''
        verify that value of self._dict[name] is valid relative path,
        absolute path, or RESOURCES asset
        '''
        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, str):
            raise Exception(f'{name} is not a string')        
        if not RESOURCES.get_path(val):
            raise Exception(f'{name} is not a file')
        #print(f'{name}: {val}')
        return val
    
    def _verify_bool(self, name, default=None, optional=False):
        'verify that value of self._dict[name] is valid bool value'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        if val in (True, False, 0, 1):
            val = True if val else False
            #print(f'{name}: {val}')
            return val
        else:
            raise Exception(f'{name} is not BOOL')
    
    def _verify_option(self, name, options, default=None, optional=False):
        'verify that value of self._dict[name] is in given options list'
 
        val = self._dict.get(name, default)
        if val == None and optional: return None
      
        if val not in options:
            val = default
        return val
    
    def _verify_text(self, name, default=None, optional=False):
        'verify that value of self._dict[name] is valid str of text'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        if isinstance(val, str):
            #print(f'{name}: {val}')
            return val
        else:
            raise(f'{name} is not text')
    
    def _verify_list(self, name, default=None, optional=False):
        'verify that value of self._dict[name] is valid list'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, (list, tuple)):
            raise Exception(f'{name} is not a list')
        for i, v in enumerate(val):
            if isinstance(v, (list, tuple)):
                self._verify_bar(None, v, Rect(0,0,100,100))
            elif not isinstance(v, str):
                raise Exception(f'{name}[{i}] == {v}, not a string')
        return val
    
    def _verify_ints(self, name, count, default=None, optional=False):
        'verify that value of self._dict[name] is valid list of ints'

        val = self._dict.get(name, default)
        if val == None and optional: return None

        if not isinstance(val, (list, tuple)):
            raise Exception(f'{name} is not a list')
        elif len(val) != count:
            raise Exception(f'{name} must have {count} int values')
        for i, v in enumerate(val):
            if not isinstance(v, int):
                raise Exception(f'{name}[{i}] == {v}, not an int')
        return val

def option_menu(foreground, options, background=None, regions=[]):
    '''
    Display an option menu, handle input, and return selected
    values. Users map press up or left to select an option, 
    or press left, right, or left to adjust the selected option.
    Press start to exit option screen, or B to exit option screen
    reverting any changes to their original values.

    foreground: a Region to draw option menu into
    options: a dict of options to include in the menu
             Each key is the name/description of the option
             Each value defines the options for the checkbox

    background: a background Region, or config['background'] by default
    regions: a list of optional Regions to update() and draw() in
             addition to the option_menu and background
    
    OPTIONS
    checkbox: If the dict value is the str 'checked' or 'unchecked'
              a checkbox is displayed with the 'checked' or 'unchecked'
              image loaded from the ImageManager
    list:     If the dict value is a list the first item is displayed
              and others can be selected with left or right, rotating
              the list. May use range_list function to create list of
              numerical values to simulate a slider.
    option    If the dict value is a string the key is displayed, along
              with the 'more' image from ImageManager. If the option is
              selected, option_menu returns the dict value
    '''   
    bars, selectable = make_option_bar(options)

    region = Region(foreground)
    region.list = bars
    region.selected = 0; region.selectedx = 0
    region.select = Region(config['list'])
    region.selectable = selectable
    background = Region(config['background'])

    region.selected = selected = 0
    running = update = 1
    while running:
        running += 1
        inp.process()

        update = region.update(inp) or update

        if inp.pressed:
            update = True
            if inp.quit or inp.pressed in ('select', 'B'):
                return ''
            elif inp.pressed in ('right', 'A'):
                k = bars[region.selected][0]
                v = options[k]
                if isinstance(v, (list, tuple)):
                    v.append(v.pop(0))
                elif v == 'checked':
                    options[k] = 'unchecked'
                elif v == 'unchecked':
                    options[k] = 'checked'
                else:
                    return v
                bars, region.selectable = make_option_bar(options)
                region.list = bars
            elif inp.pressed in ('left'):
                k = bars[region.selected][0]
                v = options[k]
                if isinstance(v, (list, tuple)):
                    i = v.pop(-1)
                    v.insert(0, i)
                    bars, region.selectable = make_option_bar(options)
                    region.list = bars   

        if update:
            background.draw()
            region.draw()
            screen.present()
        update = False
        sdl2.timer.SDL_Delay(1000//30)

def make_option_bar(d):
    '''
    Converts a option dict into a list of bars compatible with the Region
    class.

    d: dict that works with the option_menu() function
    RETURNS: a list of bars compatible with the Region list feature
    '''
    checked = images.load('checked')
    unchecked = images.load('unchecked')
    more = images.load('more')
    left = images.load('left')
    right = images.load('right')

    bars = []
    selectable = []
    for i, (k, v) in enumerate(d.items()):
        if v == 'checked':
            bars.append((k, None, 'checked'))
            selectable.append(i)
        elif v == 'unchecked':
            bars.append((k, None, 'unchecked'))
            selectable.append(i)
        elif isinstance(v, (list, tuple)):
            bars.append((k, None, right, v[0], left))
            selectable.append(i)
        elif v:
            bars.append((k, None, more))
            selectable.append(i)
        else:
            bars.append(k)

    #selectable = list(range(len(bars))) tested selectable labels
    return bars, selectable

def keyboard(options, kbl, kbu, text=''):
    '''
    Display an on screen keyboard and allow user to enter/modify
    a text string
    options: dict of Region attributes for theming
    kbl: list of strings or bar lists to represent keyboard keys
         the final row must be: shift, space, backspace, and then Enter/Done
    kbu: same as kbl but with upper case letters
    test: optional string to edit, or blank by default
    '''
    def process_kb_list(key_list):
        '''Expand strings into lists and remove None values
           (for right aligned buttons) '''
        n = []
        for row in key_list:
            if isinstance(row, str):
                row = list(row)
            n.append(row)
        return n, [[k for k in row if k] for row in n]

    upper = False
    keyboard = Region(options)
    keyboard.list, kb = process_kb_list(kbl)
    shift, space, backspace, enter, *_ = keyboard.list[-1] 

    keyboard.selected = keyboard.selectedx = 1
    keyboard.select = Region(config['list'])
    keyboard.select.fontsize = keyboard.fontsize
    keyboard.select.align = 'center'
    background = Region(config['background'])
    background.fontsize = keyboard.fontsize
    background.borderx = keyboard.area.x
    #background.align = 'topright'
    
    background.text = old_text = text
    running = update = 1
    while running:
        running += 1
        inp.process()

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
                    keyboard.list, kb = process_kb_list(kbl if upper else kbu)
                    upper = not upper
            elif inp.pressed == 'L':
                text = text[:-1]
            elif inp.pressed == 'R':
                text += '_'
            elif inp.pressed == 'A':
                key = kb[keyboard.selected][keyboard.selectedx]
                if len(key) == 1:
                    text += key
                elif key == space:
                    text += '_'
                elif key == backspace:
                    text = text[:-1]
                elif key == shift:
                    keyboard.list, kb = process_kb_list(kbl if upper else kbu)
                    upper = not upper
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
    '''
    Reads the SDL2 event que and generates a simple sets of input
    that can be read throughout your program. You should call
    InputHandler.process() every frame and read its 3 member
    variables as needed.

    quit: a quit message has been generated by the user
        or operatin system. You should exit if this variable is True
    update: your operating system has requested that 
        your program redraws itself. Update the screen when this
        variable is true
    pressed: a button has been pressed, or a key with repeat enabled
        has been held long enough to create another key event. Pressed
        will be none if there are no new inputs, or one of several
        string values: 'up', 'down', 'left', 'right', 'A', 'B', 'X',
                       'Y', 'L', 'R', 'start', 'select'

    '''
    REPEAT_RATE = 5
    REPEAT_DELAY = 10
    CAN_REPEAT =  ('up', 'down', 'right', 'left')
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

    def process(self):
        events = sdl2.ext.get_events()
        self.pressed = None
        self.update = False
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
            elif e.type == sdl2.SDL_WINDOWEVENT:
                if e.window.event == sdl2.SDL_WINDOWEVENT_EXPOSED:
                    self.update = True
            
        # HANDLE KEY REPEATS
        if self.last_press:
            pressed = None
            m, k, b = self.last_press
            
            if b in self.CAN_REPEAT and m.get(k):
                self.held_for += 1
                if self.held_for > self.REPEAT_RATE:
                    self.held_for = 0
                    self.pressed = b

def set_globals(*globs):
    '''
    Set the global values within this file's scope
    '''
    global config, screen, images, fonts, inp
    config, screen, images, fonts, inp = globs
    #for k, v in globs.items():
    #    globals()[k] = v





if __name__ == '__main__':
    main()  