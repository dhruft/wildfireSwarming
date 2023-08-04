from vars import *

primaryColor = "#BA1200"
bgColor = "#9DD1F1"

class Cell:
    def __init__(self, posx, posy, isTree, isCR):
        global c
        c = canvas[0]

        self.posx = posx
        self.posy = posy
        self.isTree = isTree
        self.isCR = isCR
        self.targeted = -1

        if isTree:
            self.height = random.randint(heightRange[0], heightRange[1])
            self.certainty = 0
            #self.heightKnown = False


        color = bgColor
        if isCR:
            color = "black"

        self.r = c.create_rectangle(
                self.posx*cw-cw, self.posy*cw-cw, 
                self.posx*cw, self.posy*cw, 
                fill=color)
        c.tag_lower(self.r)

    #CHANGE PLS
    def visit(self, certainty):

        graphHeight = self.height - heightRange[0]
        for density in range(self.density - densityInsertRadius, self.density + densityInsertRadius + 1):

            for height in range(graphHeight - heightInsertRadius, graphHeight + heightInsertRadius+1):
                if height < 0 or height > heightRange[1] - heightRange[0] or density < 0 or density > 32:
                    continue
                
                #update threshold
                maxDist = getDist(0, 0, densityInsertRadius, heightInsertRadius)
                value = normalize(getDist(self.density, graphHeight, density, height), [0, maxDist], True)
                value = certainty*(-(1/2*math.cos(value*math.pi)+1/2)**2 + 1)
                current = threshold[height][density]
                threshold[height][density] = current + (1-current)*value

        # for density in range(self.density - densityInsertRadius, self.density + densityInsertRadius + 1):
        #     column = sum(threshold[:, density])
        #     value = normalize(column, [0, heightRange[1]-heightRange[0]+1])
        #     #https://www.desmos.com/calculator/cnh6ilimot
        #     densityThreshold[density] = -(1/2*math.cos(value*math.pi)+1/2)**2 + 1

        #self.heightKnown = True

        #plt.imshow(threshold, cmap='hot', interpolation='nearest')
        #plt.show()
        #updatePlot()

        c.tag_lower(self.r)
    
    def setDensity(self, density):
        self.density = density
        cmap = cm.Reds
        norm = matplotlib.colors.Normalize(vmin=0, vmax=32)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        color = matplotlib.colors.rgb2hex(rgb)
        c.itemconfig(self.r, fill=color)
    
    def setColor(self, color):
        c.itemconfig(self.r, fill=color)

    # def setCluster(self, clusterNum):
    #     self.cluster = clusterNum
    #     c.itemconfig(self.r, fill=clusters[clusterNum]["color"])