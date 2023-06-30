import asyncio
import matplotlib.colors
import matplotlib.cm as cm

class Cell:

    def __init__(self, posx, posy, canvas, cw, age=0):
        self.posx = posx
        self.posy = posy
        self.c = canvas
        self.cw = cw
        self.age = age
        self.r = 0
    
    def update(self):

        cmap = cm.Reds
        norm = matplotlib.colors.Normalize(vmin=0, vmax=100)

        rgb = cmap(norm(abs(self.age)))[:3]  # will return rgba, we take only first 3 so we get rgb
        color = matplotlib.colors.rgb2hex(rgb)

        if self.r == 0:
            self.r = self.c.create_rectangle(
                self.posx, self.posy, 
                self.posx+self.cw, self.posy+self.cw, 
                fill=color)
        else:
            self.c.itemconfig(self.r, fill=color)
        
        self.c.tag_lower(self.r)