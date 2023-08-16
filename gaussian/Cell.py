from vars import *

primaryColor = "#BA1200"
bgColor = "#9DD1F1"

class Cell:
    def __init__(self, posx, posy, isCR):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.isTree = False
        self.isCR = isCR

        self.color = bgColor
        if isCR:
            self.color = "black"
        self.visited = False

        self.targeted = -1

    def initTree(self,height,DBH):
        self.isTree = True
        self.height = height
        self.DBH = DBH

    def draw(self):
        self.r = c.create_rectangle(
                self.posx*cw-cw, self.posy*cw-cw, 
                self.posx*cw, self.posy*cw, 
                fill=self.color)
        c.tag_lower(self.r)

    #CHANGE PLS
    def visit(self):

        self.visited = True
    
    def visitT(self):
        selected_X.append(self.height)
        selected_Y.append(self.density)
        selected_z.append(self.DBH)

        graphHeight = int(self.height)
        for density in range(self.density - densityInsertRadius, self.density + densityInsertRadius + 1):

            for height in range(graphHeight - heightInsertRadius, graphHeight + heightInsertRadius+1):
                if height < 0 or height > maxHeight or density < 0 or density > maxDensity:
                    continue
                
                #update threshold
                maxDist = getDist(0, 0, densityInsertRadius, heightInsertRadius)
                dist = getDist(self.density, graphHeight, density, height)
                value = normalize(dist, [0, maxDist], True)

                if dist != 0:
                     value /= 2
                #print(value)
                #value = certainty*(-(1/2*math.cos(value*math.pi)+1/2)**2 + 1)
                current = threshold[height][density]
                threshold[height][density] = current + (1-current)*value

        c.tag_lower(self.r)
    
    def setDensity(self, density):
        self.density = density
        cmap = cm.Reds
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxDensity)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        self.color = matplotlib.colors.rgb2hex(rgb)
    
    def setColor(self, color):
        c.itemconfig(self.r, fill=color)

    # def setCluster(self, clusterNum):
    #     self.cluster = clusterNum
    #     c.itemconfig(self.r, fill=clusters[clusterNum]["color"])