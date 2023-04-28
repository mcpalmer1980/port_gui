class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    def __repr__(self):
        return f'Rect({self.x},{self.y},{self.width},{self.height})'
    
    def __mul__(self, v):
        'scale by v keeping center in position'
        cx, cy = self.center
        r = Rect(self.x, self.y, self.width, self.height)
        r.width *= v
        r.height *= v
        r.center = cx, cy
        return r

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)    

    def fit(self, other):
        'move and resize self to fill other rect maintaining aspect ratio'
        r = self.fit(other)
        self.x = r.x; self.width = r.width
        self.y = r.y; self.height = r.height

    def fitted(self, other):
        '''
        return Rect whith other centered and resized to fill self
        maintaining aspect ratio'''
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
        return rect using bottom and right coordinates instead
        of width and height'''
        return Rect(x, y, x2-x, y2-y)
    
    def move(self, x, y):
        'move self by x/y pixels'
        self.x += x
        self.y += y
    def moved(self, x, y):
        'return copy of rect moved by x/y pixels'
        return Rect(
            self.x + x, self.y + y2,
            self.width, self.height)

    def update(self, x, y, w, h):
        'update self with new position and size'
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
   
    