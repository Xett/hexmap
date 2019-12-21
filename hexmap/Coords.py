class Cube:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def __add__(self,other):
        return Cube(self.x+other.x,self.y+other.y,self.z+other.z)
    def __round__(self):
        rx=round(self.x)
        ry=round(self.y)
        rz=round(self.z)
        x_diff=abs(rx-self.x)
        y_diff=abs(ry-self.y)
        z_diff=abs(rz-self.z)
        if x_diff>y_diff and x_diff>z_diff:
            rx=-ry-rz
        elif y_diff>z_diff:
            ry=-rx-rz
        else:
            rz=-rx-ry
        return Cube(rx,ry,rz)
    @property
    def neighbours(self):
        return [
            self+Cube(1,-1,0),
            self+Cube(1,0,-1),
            self+Cube(0,1,-1),
            self+Cube(-1,1,0),
            self+Cube(-1,0,1),
            self+Cube(0,-1,1)
        ]
class Axial:
    def __init__(self,q,r):
        self.q=q
        self.r=r
    def toCube(self):
        return Cube(self.q,-self.q-self.r,self.r)
    def __add__(self,other):
        return Axial(self.q+other.q,self.r+other.r)
    @property
    def neighbours(self):
        return [
            self+Axial(1,0),
            self+Axial(1,-1),
            self+Axial(0,-1),
            self+Axial(-1,0),
            self+Axial(-1,1),
            self+Axial(0,1)
        ]
def cube_distance(coord_a, coord_b):
    if coord_a.__class__.__name__!='Cube':
        coord_a=coord_a.toCube()
    if coord_b.__class__.__name__!='Cube':
        coord_b=coord_b.toCube()
    return (abs(coord_a.x - coord_b.x) + abs(coord_a.y - coord_b.y) + abs(coord_a.z - coord_b.z)) / 2
def linear_interpolate(a,b,t):
    return (a+(b-a))*t
def cube_linear_interpolate(a,b,t):
    return Cube(linear_interpolate(a.x,b.x,t),
                linear_interpolate(a.y,b.y,t),
                linear_interpolate(a.z,b.z,t))
def cube_line_draw(a,b):
    n=cube_distance(a,b)
    results=[]
    for i in range(n):
        results.append(round(cube_linear_interpolate(a,b,(1.0/n)*i)))
    return results
