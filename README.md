# pySDL2gui

**pySDLgui** is a simple, low level gui module that handles input and draws multiple
rectangular Regions using hardware GPU rendering. Written in python, pySDLgui
uses pySDL2, a low level SDL2 wrapper also written in pure python with no other
dependencies.  

This module is designed to produce full screen GUIs for lower powered
GNU/Linux based retro handhelds using game controller style input, but it may
prove useful on other hardware.  

The main building block of GUIs built with this module is the Region, which
represents a rectangular area that can display text, lists, and images. Each
Region has numerous attributes that should be defined in the theme.json and
defaults.json files, which can be used to change the look and feel of a GUI without
changing the program's code.  

## CLASSES:
**FontManager** - The class used to load and render fonts onto an sdl2.ext.renderer context  
**Image** - The class used to draw images onto an sdl2.ext.renderer context. An image can be any portion of a texture containing many images, and it can scale, flip, and rotate the image.  
**ImageManager** - The class used to load and cache images in texture memory, and to store associated Image objects.  
**InputHandler** -The class that handles controller and keyboard input, mapping them into simple string events such as 'up', 'left', 'A', and 'start'  
**Rect** - The class that represents rectangular regions and can maniputate them.  
**Region** - This class is the primary building back of pySDL2gui interfaces. It draws a rectangular region with an optional backround, outline, image, text, and/or list. It is defined by attributes in a json file.  
**SoundManager** - This class is used to load and play sound effects and music.  

## DATA:
**AXIS_MAP** - A dict that maps controller axises to input strings ('left', 'right', 'up', etc).  
**BUTTON_MAP** - A dict that maps controller buttons to input strings ('up', 'A', 'L', etc).  
**KEY_MAP** - A dict that maps keyboard keys to input strings ('up', 'A', 'L', etc).  
**char_map** - A string containing each character that FontManager is able to draw.  

## FUNCTIONS:
**deep_merge** - used internally to merge option dicts.  
**deep_print** - available to display nested dict items or save them to disk.  
**deep_update** - used internally to update one options dict from a second one.  
**get_color_mod** - gets the color_mod value of a texture (not working).  
**get_text_size** - gets the size a text string would be if drawn with the given font.  
**keyboard** - displays an onscreen keyboard to enter or edit a text string.  
**make_option_bar** - displays a scrolling options menu to edit program options.  
**range_list** - generates a list of numerical values to select from in a option menu, providing functionality similar to a slider widget.  
**set_color_mod** - sets the color_mod value of a texture (not working).  
**set_globals** - sets the module's global values within eac file's scope.  

# GLOBAL OBJECTS:
**config** - a dict full of options and Region definitions loaded from theme.json and default.json/  
**fonts** - a FontManager used to render all the fonts used by pySDL2gui.  
**images** - an ImageManager used to draw all the images used by pySDL2gui.  
**inp** - an InputManager used to handle input from sdl2 events.  
**RESOURCES** - a resource manager used to load resources from the assets subfolder.  
**sounds** - a SoundManager used to play sounds and music within pySDL2gui.  
**screen** - an sdl2.ext.Renderer context that pySDL2gui displays graphics into.  

 
# FontManager class
The FontManager class loads ttf and otf font files, caches them, and draws text 
into an sdl2.ext.Renderer context.
 
**init**( renderer)  
Initialize FontManager for use with a pySDL2.ext.Renderer context  

- *renderer*: pySDL2.ext.Renderer to draw on

**draw**(text, x, y, color=None, alpha=None, align='topleft', clip=None, wrap=None, linespace=0, font=None)  
Draw a text string onto a pySDL2.ext.Renderer context.
 
- *text*: string to draw
- *x*: x coordinate to draw at
- *y*: y coordinate to draw at
- *color*: (r,g,b) color tuple
- *alpha*: alpha transparency value
- *align*: a string determining the text's alignment. It can be: topleft, midtop, topright, midleft, center, midright, bottomleft, midbottom, bottomright
- *clip*: clip the text to this Rect
- *wrap*: wrap text over multiple lines, using the clip Rect
- *font*: the (filename, size) tuple for a loaded font to draw with, otherwise the most recently loaded font is used.
- *rvalue*: (Rect) the actual area drawn into

**load**(filename, size=None)  
Loads a font for future drawing.  

- *filename*: path to a ttf or otf format font file
- *size*: point size(int) for the font, or a string ending with px(ex '12px') to use pixel height instead
- *rvalue tuple*: a (filename, size) 2-tuple representing the font in 
    future draw() calls

**width**(text, scale=1)  
Calculate the width of given text using the currently loaded font.  
 
- *text*: a text string to calculate the width of
- *rvalue*: (int) width of the string in pixels  
 
# Image class
The Image class is used to draw images onto an sdl2.ext.renderer context. An image can be any portion of a texture that contains multiple images, and it can scale, flip, and rotate the image. The ImageHandler uses this class internally, and while using Image objects to draw images is common, users should rarely need to manually create them.   

**init**(self, texture, srcrect=None, renderer=None)  
Create a new Image from a texture and a source Rect.  
 
- *texture*: an sdl2.ext.Texture object to draw the image from
- *srcrect*: a gui.Rect object defining which part of the texture to draw
- *renderer*: an sdl2.ext.Renderer context to draw into

**draw**()  
Draw the image into its current dstrect, which defaults to full screen maintaining its aspect ratio.  

**draw_at**(x, y, angle=0, flip_x=None, flip_y=None, center=None)  
Draw the image with its topleft corner at x, y and at its original size.  

- *x*: x position to draw at
- *y*: y position to draw at
- *angle*: optional angle to rotate the image
- *flip_x*: optional flag to flip image horizontally
- *flip_y*: optional flag to flip image vertically
- *center*: optional point to rotate the image around if angle provided

**draw_in**(dest, angle=0, flip_x=None, flip_y=None, center=None, fit=False)  
Draw the image inside a given Rect, which may squish or stretch the image unless the optional
fit flag is set positive.
 
- *dest*: Rect area to draw the image into
- *angle*: optional angle to rotate image
- *flip_x*: optional flag to flip image horizontally
- *flip_y*: optional flag to flip image vertically
- *center*: optional point to rotate the image around if angle provided
- *fit*: set true to fit the image into dest without changing its aspect ratio  
 
# ImageManager class   
The ImageManager class loads images into Textures and caches them for later use.  
 
**init**(screen, max=None)  
Create a new Image manager that can load images into textures.  
 
- *screen*: the sdl2.ext.Renderer context that the image will draw
    into. A renderer must be provided to create new Texture
    objects
- *max*: the maximum number of images to cache before old ones are
    unloaded. Defaults to ImageManager.MAX_IMAGES, currently 20

**load**(fn)  
Load an image file into a Texture or receive a previously cached
Image with that name.  
 
- *fn*: filename(str) to load
- *rvalue*: a reference to the gui.Image that was loaded from disk or cache

**load_atlas**(self, fn, atlas)  
Load image fn, create Images from an atlas dict, and create
a named shortcut for each image in the atlas.  
 
- *fn*: (str) the filename of an image file to load into a texture
- *atlas*: a dict representing each image in the file, with each key being the image's name, and the value being a tuple. The tuple should be either (x, y, width, height), or optionally (x, y, width, height, flip_x, flip_y, angle)

```py
        #example atlas:
        atlas = {
            'str_name': (x, y, width, height),
            'another_img': (32, 0, 32, 32)
        }
```
- *rvalue*: dict of gui.Images in {name: Image} format

# InputHandler class

The InputHandler class reads the SDL2 event que and generates a simple set of inputs
that can be read throughout your program. You should call InputHandler.process() every
frame and read its 3 member variables as needed.  
 
- *quit:*   a quit message has been generated by the user or operating system.
You should exit if this variable is True.  

- *update:* your operating system has requested that your program redraws
itself. Update the screen when this variable is True.

- *pressed:* a button has been pressed, or a key with repeat enabled has
been held long enough to trigger another event. Pressed will be None if
there are no new inputs, or one of several string values:

    up, down, left, right, A, B, X, Y, L, R, start, select  

**init**()

Initialize the InputHandler  

**process**()

Polls the sdl2 event handler for events and updates the quit, update and pressed variables.  


# Rect class
This class defines a rectangular region and allows you to manipulate them.

**init**(x, y, width, height)  

- *x*: x coordinate for Rect (left side)
- *y*: y coordinate for Rect (top side)
- *width*: the width of the Rect, in pixels
- *height*: the height of the Rect, in pixels

**\_\_mul\_\_**(self, v)  
Scales the Rect by scalar v, keeping its center in the same position. This function overloads the * operator, so _r * 2_ will double the size Rect r, and _q * .5_ will halve the size of Rect q.

**clip**(other)  
Returns a copy of the Rect cropped to fit inside another Rect.

**copy**()  
Returns a new copy of the Rect.

**fit**( other)  
Moves and resizes this Rect(self) to fill another Rect(other), maintaining its aspect ratio while centering it.

**fitted**(other) 
Return a new Rect that is a copy of another Rect(other) that has been centered and resized to fill this Rect(self). Its aspect ratio is retained.

**from_corners**(x, y, x2, y2)  
A static method that creates a new rect using the bottom and right coordinates instead of width and height.

**from_sdl**( r )  
A static method that creates a new rect based on the position and size of an sdl_rect object

**inflate**(x, y=None)  
Add x to the width and y to height to the Rect, or x to both the width and height if y is undefined. The rect remains centered around the same central point. Negative numbers shrink the Rect.

**inflated**(x, y=None)  
Return a copy of the Rect with x added to its width and y to its height,
or x to both the width and height if y is undefined. The rect remains centered around the same central point. Negative numbers shrink the Rect.

**move**(x, y)  
Move the Rect by x pixels horizontally, and y pixels vertically.  

**moved**(x, y)  
Return a copy of the Rect that has been moved x pixels horizontally, and y pixels vertically.  

**sdl**()  
Returns an sdl_rect object with the same size and position of the Rect.

**tuple**()  
Return a 4-tuple copy of the Rect in an (x, y, width, height) format.

**update**(x, y, w, h)  
Update the Rect with a new position and size. Useful for replacing a Rect with a new one while retaining references to the old one. 

**Special Attributes**  
Rects have numerous attributes that allow you to read and change the position of its center, corners, and edges.

- bottom - y coordinate for the bottom edge of the Rect
- bottomleft - (x, y) tuple for the bottom left corner of the Rect
- bottomright - (x, y) tuple for the bottom right corner of the Rect
- center - (x, y) tuple for the Rect's centeral point
- centerx - x coordinate of the Rect's central point
- centery - y coordinate of the Rect's central point
- h - height of the Rect, which when changed, keeps the Rect centered around the same point
- height - height of the Rect, which when changed, keeps the Rect at the same horizontal position
- left - x coordinate for the left edge of the Rect
- midbottom - (x, y) coordinate for the center of the Rect's bottom edge
- midleft - (x, y) coordinate for the center of the Rect's left edge
- midright - (x, y) coordinate for the center of the Rect's right edge
- midtop - (x, y) coordinate for the center of the Rect's top edge
- right - x coordinate for the right edge of the Rect
- size - (w, h) size of the Rect. A Rect remains centered around the same point when its size is changed
- top - y coordinate for the top edge of the Rect
- topleft - (x, y) coordinate for the top left corner of the Rect
- topright - (x, y) coordinate for the top right corner of the Rect
- w - width of the Rect, which when changed, keeps the Rect centered around the same point
- width - height of the Rect, which when changed, keeps the Rect at the same horizontal position

# Region class

For drawing a rectangular region on a renderer context
Regions may have a fill color, outline, and image, as well
as scrolling text, an interactive list, or a horizontal toolbar.

The following attributes can be loaded from a dict or json file:

**FILL AND OUTLINE**  

- *area*: 4-tuple of pixels or screen percent(0.0-1.0),
- *fill*: 3-tuple fill color
- *outline*: 3-typle outline color
- *thickness*: int outline thickness,
- *roundness*: int outline roundness,
- *border*: int border around text x&y
- *borderx*: int left/right border around text
- *bordery*: int top/bottom border around text

**IMAGE RENDERING**  

- *image*: filename for image
- *imagesize*: 2-tuple (w,h) scale to this size
- *imagemode*: 'fit', 'stretch', 'repeat', None or ''
- *imagealign*: same options as text align, but for image
- *patch*: 4-tuple - left, top, right, bottom edges for 9-patch rendering
- *pattern*: bool image is a base64 string
- *pimage*: filename or image to use for patch if different than image

**TEXT RENDERING**  

- *autoscroll*: int speed of auto scroll or 0 disables
- *font*: filename for font
- *fontsize*: int size of font
- *fontcolor*: 3-tuple font color
- *text*: text string (may be multiline)
- *wrap*: allow multiline text wraping
- *linespace*: int extra space between lines
- *align*: text alignment (topleft, topright, midtop
                       midleft, center, midright
                       bottomleft, midbottom, bottomright)

**LIST RENDERING**  

- *list*: a list of items to be displayed and selected from
- *itemsize*: the height that each list item is drawn with
- *select*: a 3-tuple rgb color for the selected item, or a Region for rendering it
- *selectable*: a list of the indexes of the list attribute that may be selected by the user
- *scrollable*: bool that allows up/down events to scroll wrapped text when set to True
- *selected*: the currently selected list item, which will be drawn using the color or Region referenced by the select attribute

**BARS** (toolbars)  

- *bar: a list of strings, Images, or str names for images in the ImageManager.
A single null value may split the bar into left and right aligned sides
- *barspace*: additional space between each bar item beyone its natural size
- *barwidth*: the minimum width for each bar item
- *selectablex*: TODO a list of the indexes of the bar that may be selected by the user 
- *selectedx*: the currently selected list item, or -1 if nothing selected.
The selected item will be drawn in the color of or with the Region referenced by the select attribute.

**init**(data, renderer=None, images=None, fonts=None)  
Create a new Region for future drawing.

- *data*: a dict including various Region attributes
- *renderer*: an sdl2.ext.Renderer context to draw into
- *images*: the ImageManager used to load images from
- *fonts*: the FontManager used to draw fonts with
 
**draw**(area=None, text=None, image=None)  
    Draw the Region and all of its features  
     
- *area*: override Region's area, used internally
- *text*: override Region's text and list, used internally
- *image*: override Region's image, used internally

**set_defaults**(data, renderer, images, fonts)
    Set global defaults for all Regions to reduce later parameter requirements.  
    This is a static method and should be called before initiating any Region
    objects
     
- *data*: a dict of Region parameters that will apply to all regions, but will
be overriden by parameters sent when creating Region objects later
- *renderer*: a sdl2.ext.renderer context to draw onto
- *images*: a gui.ImageManager reference for loading images
- *fonts*: a gui.FontManager reference for loading fonts

**update**(inp)
    Update the current region based on user input, the autoscrolling setting, and
    other conditions.
     
- *inp*: reference to an gui.InputHandler to receive input
- *rvalue*: True if the region needs to be redrawn, otherwise False

# SoundManager class
   	The SoundManager class loads and plays sound files.
 
**play**(name, volume=1)
Play a loaded sound with the given name
 
- *name*: name of sound, either the filename(without extension) or
    an alternate name provided to the load() method
- *volume*: volume to play sound at, from 0.0 to 1.

**init**()
Initialize the sound system

**load**(fn, name=None, volume=1)  
Load a given sound file into the Sound Manager  
 
- *fn*: filename for sound file to load
- *name*: alternate name to use to play the sound instead of its filename
- *volume*: default volume level to play the sound at, from 0.0 to 1.0

**music**(fn, loops=-1, volume=1)  
Loads a music file and plays immediately plays it  
 
- *fn*: path to music file to load and play
- *loops*: number of times to play song, or loop forever by default
- *volume*: volume level to play music, between 0.0 and 1.0

**volume** variable to change master volume from 0.0 to 1.0
 
# Functions
      	 	
**deep_merge**(d, u, r=False)  
Add contents of dict u into a copy of dict d. This will not change the
provided d parameter dict, only return a new copy.
 
- *d*: dict to add new values to
- *u*: dict with values to add into d
- *rvalue* the new dict with u merged into d

**deep_print**(d, name=None, l=0, file=None)  
Pretty print a dict recursively, included all child dicts  
 
- *d*: dict to pring
- *name*: name of dict to use in printing
- *l*: used internaly
- *file*: open file to print into instead of to the console

**deep_update**(d, u, r=False)  
Add contents of dict u into dict d. This will change the provided d
parameter dict
 
- *d*: dict to add new values to
- *u*: dict with values to add into d
- *rvalue* the updated dict, same as d

**get_color_mod**(texture)  
Get color_mod value of a texture as an RGB 3-tuple NOT WORKING  

**get_text_size**(font, text='')  
Calculate the size of given text using the given font, or if
no text is provided, then return the font's height instead
 
- *font*: an existing sdl2.ext.FontTTF object
- *text*: optional text string to generate size of
- *rvalue*: (width(int), height(int)) tuple if text provided,
        or height(int) otherwise

**keyboard**(options, kbl, kbu, text='')
Display an on screen keyboard and allow user to enter/modify
a text string

- *options*: dict of Region attributes for theming
- *kbl*: list of strings or bar lists to represent keyboard keys. Tthe final row
must be: shift, space, backspace, and then Enter/Done
- *kbu*: same as kbl but with upper case letters
- *test*: optional string to edit, or blank by default

**make_option_bar**(d)
Converts a option dict into a list of bars compatible with the Region
class.
     
- *d*: dict that works with the option_menu() function
- *rvalue*: a list of bars compatible with the Region list feature

**option_menu**(foreground, options, background=None, regions=[])
Display an option menu, handle input, and return selected
values. Users map press up or left to select an option, 
or press left, right, or left to adjust the selected option.
Press start to exit option screen, or B to exit option screen
reverting any changes to their original values.  
     
- *foreground*: a Region to draw option menu into
- *options*: a dict of options to include in the menu. Each key is 
the name/description of the entry. Each value defines the options.
- *background*: a background Region, or config['background'] by default
- *regions*: a list of optional Regions to update() and draw() in
addition to the option_menu and background
     
    **OPTIONS**
- checkbox: If the dict value is the str 'checked' or 'unchecked'
          a checkbox is displayed with the 'checked' or 'unchecked'
          image loaded from the ImageManager
- list:   If the dict value is a list the first item is displayed
          and others can be selected with left or right, rotating
          the list. May use range_list function to create list of
          numerical values to simulate a slider.
- option  If the dict value is a string the key is displayed, along
          with the 'more' image from ImageManager. If the option is
          selected, option_menu returns the dict value

**range_list**(start, low, high, step)  
Creates a list of strings representing numbers within a given range. 
Meant for use with gui.options_menu as an alternative to a slider widget.
The values will be a listin numerical order, but rotated to have the
start value first.
 
- *start*: the value to start at (first value)
- *low*: lowest value for list
- *hight*: highest value for list
- *step*: the numerical value between each item in the list
- *rvalue*: a list of numerical values, rotated to have start value first

```py 
        example*: range_list(50, 0, 100, 10) ->
                [50, 60, 70, 80, 90, 100, 0, 10, 20, 30, 40]
```

**set_color_mod**(texture, color)  
Set color_mod value of a texture using an RGB 3-tuple NOT WORKING

**set_globals**(*globs)  
Set the global values within this files scope

Copyright (C) 2023, Michael C Palmer <michaelcpalmer1980@gmail.com>  

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