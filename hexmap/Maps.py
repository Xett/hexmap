from hexmap import Iterators
from hexmap.Coords import Cube
from hexmap.Coords import Axial
class Tile:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def distance_from_center_pass(self):
        return (abs(self.x-0)+abs(self.y-0)+abs(self.z-0))/2
    def distance_from_tile_pass(self,tile):
        return (abs(self.x-tile.x)+abs(self.y-tile.y)+abs(self.z-tile.z))/2
class HexMap:
    def __init__(self,tile_class=Tile):
        self.tiles={}
        self.tile_class=tile_class
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
    def __delitem__(self,key):
        if key.__class__.__name__=='Cube':
            del self.tiles[(key.x,key.z)]
        elif key.__class__.__name__=='Axial':
            del self.tiles[(key.q,key.r)]
        elif key.__class__.__name__=='OddRowAxial':
            del self.tiles[(key.toCube().x,key.toCube().z)]
        elif key.__class__.__name__=='EvenRowAxial':
            del self.tiles[(key.toCube().x,key.toCube().z)]
        elif key.__class__.__name__=='OddColumnAxial':
            del self.tiles[(key.toCube().x,key.toCube().z)]
        elif key.__class__.__name__=='EvenColumnAxial':
            del self.tiles[(key.toCube().x,key.toCube().z)]
    def addTile(self,x,y,z):
        tile=self.tile_class(x,y,z)
        self[Cube(x,y,z)]=tile
    @property
    def length(self):
        return len(self.tiles)
class RadialMap(HexMap):
    def __init__(self,radius,tile_class=Tile):
        super().__init__(tile_class)
        self.radius=radius
        self.populateMap(self.radius)
    def populateMap(self,radius):
        # add missing or delete unneeded
        iterator=Iterators.RingIterator(radius,6)
        if self.length>iterator.length:
            # delete unneeded
            for i,coords in enumerate(Iterators.RingIterator(radius+1,6)):
                if i>iterator.length-1:
                    del self[Cube(coords[0],coords[1],coords[2])]
        else:
            # add missing
            iterator.index=self.length-1
            for x,y,z in iterator:
                self.addTile(x,y,z)
        self.radius=radius
class SquareMap(HexMap):
    def __init__(self,width,height,tile_class=Tile):
        super().__init__(tile_class)
        self.width=width
        self.height=height
        self.populateMap(self.width,self.height)
    def populateMap(self,width,height):
        for x in range(width):
            for y in range(height):
                coord=Axial(x,y).toCube()
                self.addTile(coord.x,coord.y,coord.z)
