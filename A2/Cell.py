from vars import *

class Cell:
    def __init__(self, posx, posy, height, dbh):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.visited = False
        self.height = height
        self.dbh = dbh

    def draw(self):
        self.r = c.create_rectangle(
                self.posx*cw-cw, self.posy*cw-cw, 
                self.posx*cw, self.posy*cw, 
                fill=self.color,
                outline=self.color)
        c.tag_lower(self.r)

    #CHANGE PLS
    def visit(self):
        self.visited = True
    
    def setDensity(self, density):
        self.density = density
        cmap = cm.cool
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxDensity)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        self.color = matplotlib.colors.rgb2hex(rgb)