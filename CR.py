class CR:
    radius = 3

    def __init__(self, posx, posy, cw, c):
        self.posx = posx
        self.posy = posy

        circle = c.create_oval(posx-cw*self.radius, posy-cw*self.radius,
                      posx+cw*self.radius, posy+cw*self.radius,
                       fill="black" )
    