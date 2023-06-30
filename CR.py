class CR:
    radius = 20

    def __init__(self, posx, posy, c):
        self.posx = posx
        self.posy = posy

        c.create_oval(posx-self.radius, posy-self.radius,
                      posx+self.radius, posy+self.radius,
                       fill="black" )
    