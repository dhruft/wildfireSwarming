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

    def visit(self, isMain, hm):
        
        if isMain:
            self.visited = True
            
            selectedX.append(self.height)
            selectedY.append(self.density)
            selectedZ.append(self.dbh)

            c.itemconfig(self.r, fill="red")
            c.itemconfig(self.r, outline="red")

        graphHeight = int(self.height)
        for density in range(self.density - densityInsertRadius, self.density + densityInsertRadius + 1):

            for height in range(graphHeight - heightInsertRadius, graphHeight + heightInsertRadius + 1):
                if height < 0 or height > maxHeight or density < 0 or density > maxDensity:
                    continue
                
                #update threshold
                maxDist = getDist(0, 0, densityInsertRadius, heightInsertRadius)
                dist = getDist(self.density, graphHeight, density, height)
                value = 0.7+0.4*normalize(dist, [0, maxDist], True)

                if dist != 0:
                     value /= 2
                #print(value)
                #value = certainty*(-(1/2*math.cos(value*math.pi)+1/2)**2 + 1)
                current = hm[height][density]
                hm[height][density] = current + (1-current)*value

        return hm

    #     std = getSTD(machineMain, tree)
    #     if std > 2:
    #         tree.selected = True
    #         updateMachine(machineMain, tree)
    #         tree.setColor()
    #     #print(std)


    def setDensity(self, density):
        self.density = density
        cmap = cm.cool
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxDensity)

        rgb = cmap(norm(abs(density)))[:3]  # will return rgba, we take only first 3 so we get rgb
        self.color = matplotlib.colors.rgb2hex(rgb)
    
    def colorScale(self, value, min, max):
        cmap = cm.cool
        norm = matplotlib.colors.Normalize(vmin=min, vmax=max)

        rgb = cmap(norm(abs(value)))[:3]  # will return rgba, we take only first 3 so we get rgb
        self.color = matplotlib.colors.rgb2hex(rgb)

        c.itemconfig(self.r, fill=self.color)
        c.itemconfig(self.r, outline=self.color)
    
    def setColor(self):
        c.itemconfig(self.r, fill="red")
        c.itemconfig(self.r, outline="red")