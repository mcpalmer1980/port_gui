import sdl2

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
    def __repr__(self):
        return f'Rect({self.x},{self.y},{self.width},{self.height})'
    
    def __mul__(self, v):
        'Scale by v keeping center in position'
        cx, cy = self.center
        r = Rect(self.x, self.y, self.width, self.height)
        r.width *= v
        r.height *= v
        r.center = cx, cy
        return r

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)    

    def fit(self, other):
        'Move and resize myself to fill other rect maintaining aspect ratio'
        r = self.fitted(other)
        self.x = r.x; self.width = r.width
        self.y = r.y; self.height = r.height

    def fitted(self, other):
        '''
        Return new Rect whith other centered and resized to fill self
        Aspect ration is retained'''
        xr = self.width / other.width
        yr = self.height / other.height
        mr = xr if yr < xr else yr

        w = int(self.width / mr)
        h = int(self.height / mr)
        x = int(other.x + (other.width - w) / 2)
        y = int(other.y + (other.height - h) / 2)
        return Rect(x, y, w, h)

    def from_corners(x, y, x2, y2):
        '''
        Return a new rect using bottom and right coordinates instead
        of width and height'''
        return Rect(x, y, x2-x, y2-y)

    def inflate(self, x, y=None):
        '''
        Add x to width and y to height of rect, or x to both
        The rect will remain centered around the same point'''

        y = y if y != None else x
        self.x += x
        self.y += y
        self.width -= x//2
        self.height -= y//2
    def inflated(self, x, y=None):
        '''
        Return a copy of self with x added to the width and y to the
        height of rect, or x to both. The rect will remain centered
        around the same point'''

        y = y if y != None else x
        nx = self.x + x
        ny = self.y + y
        nw = self.width - x//2
        nh = self.height - y//2
        return Rect(nx, ny, nw, nh)
    
    def move(self, x, y):
        'Move self by x/y pixels'
        self.x += x
        self.y += y
    def moved(self, x, y):
        'Return copy of rect moved by x/y pixels'
        return Rect(
            self.x + x, self.y + y,
            self.width, self.height)


    def sdl(self):
        'Return my value as an sdl_rect'
        return sdl2.SDL_Rect(self.x, self.y, self.width, self.height)
    def tuple(self):
        'Return my value as a 4-tuple'
        return self.x, self.y, self.width, self.height

    def update(self, x, y, w, h):
        'Update myself with new position and size'
        self.x = x; self.width = w
        self.y = y; self.height = h

    @property
    def w(self):
        return self.width
    @w.setter
    def w(self, v):
        self.width = v
        self.x -= v//2
    @property
    def h(self):
        return self.height
    @h.setter
    def h(self, v):
        self.height = v
        self.y -= v//2

    @property
    def top(self):
        return self.y
    @top.setter
    def top(self, v):
        self.y = v

    @property
    def bottom(self):
        return self.y + self.height
    @bottom.setter
    def bottom(self, v):
        self.y = v - self.height

    @property
    def left(self):
        return self.x
    @left.setter
    def left(self, v):
        self.x = v

    @property
    def right(self):
        return self.x + self.width
    @right.setter
    def right(self, v):
        self.x = v - self.width

    @property
    def bottomleft(self):
        return self.x, self.y + self.height
    @bottomleft.setter
    def bottomleft(self, v):
        x, y = v
        self.x = x
        self.y = y - self.height

    @property
    def topleft(self):
        return self.x, self.y
    @topleft.setter
    def topleft(self, v):
        x, y = v
        self.x = x
        self.y = y

    @property
    def topright(self):
        return self.x + self.width, y
    @topright.setter
    def topright(self, v):
        x, y = v
        self.x = x - self.width
        self.y = y

    @property
    def center(self):
        return self.x + (self.width//2), self.y + (self.height//2)
    @center.setter
    def center(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y - self.height//2
    
    @property
    def centerx(self):
        return self.x + self.width//2
    @centerx.setter
    def centerx(self, v):
        self.x = v - self.width//2
    @property
    def centery(self):
        return self.y + self.height//2
    @centery.setter
    def centery(self, v):
        self.y = v - self.height//2

    @property
    def midleft(self):
        return self.x, self.y + self.height//2
    @midleft.setter
    def midleft(self, v):
        x, y = v
        self.x = x
        self.y = y - self.height//2
    @property
    def midright(self):
        return self.x+self.width, self.y + self.height//2
    @midright.setter
    def midright(self, v):
        x, y = v
        self.x = x - self.width
        self.y = y - self.height//2
    
    @property
    def midtop(self):
        return self.x+self.width//2, self.y
    @midtop.setter
    def midtop(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y
    @property
    def midbottom(self):
        return self.x+self.width//2, self.y+self.height
    @midbottom.setter
    def midbottom(self, v):
        x, y = v
        self.x = x - self.width//2
        self.y = y - self.height

    @property
    def size(self):
        return self.width, self.height
    @size.setter
    def size(self, v):
        cx, cy = self.center
        self.width, self.height = v
        self.center = cx, cy
   
    