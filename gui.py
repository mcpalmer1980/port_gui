#!/bin/python3
import pygame as pg

screen_size = 480, 320
text = "Dungeon & Dragons: Warriors of the Eternal Sun is set in the world of Mystara, a setting of the Dungeons & Dragons game. The characters find themselves in a strange, red-hued world in which the horizon slopes upward in all directions, eventually vanishing into a crimson haze at the limits of sight. Their mission is to find and make allies in this new world or else the kingdom and its culture will perish."
names = ["3 Ninjas Kick Back", "AD&D - Warriors of the Eternal Sun", "AWS Pro Moves Soccer", "Aa Harimanada", "Aaahh!!! Real Monsters", "Action 52-in-1", "Addams Family Values", "Addams Family", "Advanced Busterhawk Gleylancer", "Advanced Military Commander", "Adventures of Batman & Robin", "Adventures of Mighty Max", "Adventures of Rocky and Bullwinkle", "Aero The Acro-bat I", "Aero The Acro-bat II", "Aerobiz Supersonic", "Aerobiz", "After Burner Complete", "After Burner II", "Air Buster", "Air Diver", "Aladdin", "Alex Kidd In The Enchanted Castle", "Alien III", "Alien Soldier", "Alien Storm", "Alisia Dragoon", "Altered Beast", "American Gladiators", "Andre Agassi Tennis"]
fake_title = names[1]

class port_list():
    def __init__(self, screen, **dargs):
        w, h = screen.get_size()
        self.screen = screen
        self.font = dargs.get('font', pg.font.Font(size = 25))
        self.fcolor = dargs.get('tcolor', (0,0,0))
        self.tfont = dargs.get('tfont', pg.font.Font(size = 40))
        self.tcolor = dargs.get('tcolor', (0,0,0))
        self.vspace = dargs.get('vspace', 2)
        self.hspace = dargs.get('hspace', self.vspace)
        self.box_color = (100,100,100), (0,0,0)
        self.list_color = (0,0,0), (255,255,255)

        self.rTitle = pg.Rect(0,0, w, self.tfont.get_height() + self.vspace*2, )

        self.rImage1 = pg.Rect(0,self.rTitle.h, w*.33, h*.33)
        self.rImage1.right = w
        self.rImage2 = self.rImage1.copy()
        self.rImage2.top = self.rImage1.bottom
        self.image = pg.image.load('image.png')

        self.rText = pg.Rect(0, self.rImage2.bottom, w, h-self.rImage2.bottom)
        self.rList = pg.Rect(0, self.rTitle.bottom, self.rImage1.left, self.rImage1.height*2)

        self.selected = 1
        self.needs_update = True


    
    def _fit_image(self, image, dest):
        r = pg.Rect(0,0,*image.get_size()).fit(dest)
        n = pg.transform.smoothscale(image, r.size)
        self.screen.blit(n, r)

    def _split_lines(self, text, font, dest):
        '''Create a series of lines that will fit on the provided
        rectangle.'''        
        final_lines = []

        max_height = dest.height
        width = dest.width - (self.hspace * 2)
        requested_lines = text.splitlines()

        for requested_line in requested_lines:
            if font.size(requested_line)[0] > width:
                words = requested_line.split(' ')
                # if any of our words are too long to fit, return.
                for word in words:
                    if font.size(word)[0] >= width:
                        raise MenuException    ("The word " + word + " is too long to fit in the rect passed.")
                # Start a new line
                accumulated_line = ""
                for word in words:
                    test_line = accumulated_line + word + " "
                    # Build the line while the words fit.
                    if font.size(test_line)[0] < width:
                        accumulated_line = test_line
                    else:
                        final_lines.append(accumulated_line)
                        accumulated_line = word + " "
                final_lines.append(accumulated_line)
            else:
                final_lines.append(requested_line)

        line_count = len(final_lines)
        line_height = font.get_height()
        total_height = line_height * line_count

        return final_lines

    def update(self):
        if self.needs_update:
            self.needs_update = False
            return True

    def draw(self):
        # Draw Title
        pg.draw.rect(self.screen, self.box_color[0], self.rTitle)
        s = self.tfont.render(names[self.selected], True, self.box_color[1])
        self.screen.blit(s, (self.rTitle.left+self.hspace, self.rTitle.top+self.vspace))

        # Draw Images
        pg.draw.rect(self.screen, self.box_color[0], self.rImage1)
        pg.draw.rect(self.screen, self.box_color[0], self.rImage2)
        self._fit_image(self.image, self.rImage1)
        self._fit_image(self.image, self.rImage2)

        # Draw List Box
        pg.draw.rect(self.screen, self.list_color[0], self.rList)
        y = self.vspace
        rClip = pg.Rect(0,0, self.rList.w-self.hspace*2, self.rList.h)
        for i, n in enumerate(names):
            if y + self.tfont.get_height() > self.rList.height:
                break

            if i == self.selected:
                r = pg.Rect(self.rList.left, self.rList.top+y, self.rList.w, self.tfont.get_height())
                pg.draw.rect(self.screen, self.box_color[0], r)
                s = self.tfont.render(n, True, self.box_color[1])
                self.screen.blit(s, (self.rList.left+self.hspace, self.rList.top+y), rClip)
            else:
                s = self.tfont.render(n, True, self.list_color[1])
                self.screen.blit(s, (self.rList.left+self.hspace, self.rList.top+y), rClip)
            y += s.get_height() + self.vspace

        # Draw Text Description
        pg.draw.rect(self.screen, self.box_color[0], self.rText)
        lines = self._split_lines(text, self.font, self.rText)
        y = self.vspace
        for l in lines:
            if y + self.font.get_height() > self.rText.height:
                break
            s = self.font.render(l, True, self.box_color[1])
            self.screen.blit(s, (self.rText.left+self.hspace, self.rText.top+y))
            y += s.get_height() + self.vspace
            
def main():
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(screen_size)

    pl = port_list(screen)

    running = True
    while running:
        for e in pg.event.get():
            if e.type in (pg.QUIT, pg.KEYDOWN):
                running = False
        if pl.update():
            pl.draw()
        pg.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()