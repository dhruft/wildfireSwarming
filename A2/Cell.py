from vars import *

class Cell:
    def __init__(self, posx, posy, isCR):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.isTree = False
        self.isCR = isCR

        if isCR:
            self.color = "black"
        self.visited = False

    def initTree(self,height,DBH):
        self.isTree = True
        self.height = height
        self.DBH = DBH

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
    
    def visitT(self):
        selected_X.append(self.height)
        selected_Y.append(self.density)
        selected_z.append(self.DBH)

        c.tag_lower(self.r)
    
    def setDensity(self, density):
        self.density = density
        cmap = cm.cool
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxDensity)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        self.color = matplotlib.colors.rgb2hex(rgb)
    
    def setColor(self, color):
        c.itemconfig(self.r, fill=color)

    # def setCluster(self, clusterNum):
    #     self.cluster = clusterNum
    #     c.itemconfig(self.r, fill=clusters[clusterNum]["color"])