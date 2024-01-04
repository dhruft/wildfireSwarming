from vars import *

primaryColor = "#BA1200"
bgColor = "#9DD1F1"

class Cell:
    def __init__(self, posx, posy, hasData):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.hasData = hasData

        color = bgColor

        if hasData:
            color = primaryColor
            self.height = random.randrange(heightRange[0], heightRange[1]+1)
            
        self.r = c.create_rectangle(
                self.posx*cw-cw, self.posy*cw-cw, 
                self.posx*cw, self.posy*cw, 
                fill=color)
        c.tag_lower(self.r)

    #CHANGE PLS
    def visit(self, certainty):
        c.tag_lower(self.r)
    
    def setDensity(self, density):
        self.density = density
        cmap = cm.Reds
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxDensity)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        color = matplotlib.colors.rgb2hex(rgb)
        c.itemconfig(self.r, fill=color)
    
    def setColor(self, color):
        c.itemconfig(self.r, fill=color)

    # def setCluster(self, clusterNum):
    #     self.cluster = clusterNum
    #     c.itemconfig(self.r, fill=clusters[clusterNum]["color"])