from vars import *

primaryColor = "#BA1200"
bgColor = "#9DD1F1"

class Cell:
    def __init__(self, posx, posy, status, isCR):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.status = status
        self.isCR = isCR

        color = primaryColor if status else bgColor
        if isCR:
            color = "black"
        self.r = c.create_rectangle(
                self.posx*cw-cw, self.posy*cw-cw, 
                self.posx*cw, self.posy*cw, 
                fill=color)
        c.tag_lower(self.r)

    def update(self):
        c.itemconfig(self.r, fill=bgColor)
        c.tag_lower(self.r)

    def setCluster(self, clusterNum):
        self.cluster = clusterNum
        c.itemconfig(self.r, fill=colors[clusterNum])
    
    def black(self):
        c.itemconfig(self.r, fill="black")
        