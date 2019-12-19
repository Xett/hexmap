import Iterators
from Coords import Cube
from Coords import Axial
class Tile:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        self.movement_cost=1
        self.isPassable=True
    def distance_from_center_pass(self):
        return (abs(self.x-0)+abs(self.y-0)+abs(self.z-0))/2
    def distance_from_tile_pass(self,tile):
        return (abs(self.x-tile.x)+abs(self.y-tile.y)+abs(self.z-tile.z))/2
class HexMap:
    def __init__(self):
        self.tiles={}
    def __getitem__(self,key):
        if key.__class__.__name__=='Cube':
            try:
                return self.tiles[(key.x,key.z)]
            except:
                return False
        elif key.__class__.__name__=='Axial':
            try:
                return self.tiles[(key.q,key.r)]
            except:
                return False
        elif key.__class__.__name__=='OddRowAxial':
            try:
                return self.tiles[(key.toCube().x,key.toCube().z)]
            except:
                return False
        elif key.__class__.__name__=='EvenRowAxial':
            try:
                return self.tiles[(key.toCube().x,key.toCube().z)]
            except:
                return False
        elif key.__class__.__name__=='OddColumnAxial':
            try:
                return self.tiles[(key.toCube().x,key.toCube().z)]
            except:
                return False
        elif key.__class__.__name__=='EvenColumnAxial':
            try:
                return self.tiles[(key.toCube().x,key.toCube().z)]
            except:
                return False
    def __setitem__(self,key,item):
        if key.__class__.__name__=='Cube':
            self.tiles[(key.x,key.z)]=item
        elif key.__class__.__name__=='Axial':
            self.tiles[(key.q,key.r)]=item
        elif key.__class__.__name__=='OddRowAxial':
            self.tiles[(key.toCube().x,key.toCube().z)]=item
        elif key.__class__.__name__=='EvenRowAxial':
            self.tiles[(key.toCube().x,key.toCube().z)]=item
        elif key.__class__.__name__=='OddColumnAxial':
            self.tiles[(key.toCube().x,key.toCube().z)]=item
        elif key.__class__.__name__=='EvenColumnAxial':
            self.tiles[(key.toCube().x,key.toCube().z)]=item
    def addTile(self,x,y,z):
        tile=Tile(x,y,z)
        self[Cube(x,y,z)]=tile
class RadialMap(HexMap):
    def __init__(self,radius):
        super().__init__()
        self.radius=radius
        self.populateMap()
    def populateMap(self):
        for x,y,z in Iterators.RingIterator(self.radius,6):
            self.addTile(x,y,z)
    def reset(self,radius):
        self.radius=radius
        self.populateMap()
