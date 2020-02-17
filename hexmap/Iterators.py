class RingIterator:
    def __init__(self,radius,ring_step):
        self.radius=radius
        self.ring_step=ring_step
        self.index=-1
        self.length_cache=0
    def __iter__(self):
        return self
    def __next__(self):
        if self.index==self.length-1:
            raise StopIteration
        else:
            self.index+=1
            if self.index==0:
                return 0,0,0
            else:
                current_ring=self.current_ring
                tiles_left_over=self.tiles_progressed_on_ring
                tr=current_ring-1
                quad_one=(((tr*self.ring_step)//3))
                quad_two=(((tr*self.ring_step)//3)*2)
                xs=list(range(tr))+([tr]*current_ring)+list(range(tr-1,-tr,-1))+([-tr]*current_ring)+list(range(-tr+1,0))
                ys=list(range(tr))+([tr]*current_ring)+list(range(tr-1,-tr,-1))+([-tr]*current_ring)+list(range(-tr+1,0))
                for i in range(quad_one):
                    ys.append(ys.pop(0))
                zs=list(range(tr))+([tr]*current_ring)+list(range(tr-1,-tr,-1))+([-tr]*current_ring)+list(range(-tr+1,0))
                for i in range(quad_two):
                    zs.append(zs.pop(0))
                return xs[tiles_left_over-1],ys[tiles_left_over-1],zs[tiles_left_over-1]
    @property
    def tiles_progressed_on_ring(self):
        index_counter=self.index
        current_ring=1
        while index_counter>0:
            current_ring+=1
            if index_counter-((current_ring-1)*self.ring_step)<=0:
                return index_counter
            index_counter-=(current_ring-1)*self.ring_step
        return index_counter
    @property
    def length(self):
        if self.length_cache==0:
            length=1
            for i in range(1,self.radius):
                length+=self.ring_step*i
            self.length_cache=length
        return self.length_cache
    @property
    def current_ring(self):
        index_counter=self.index
        current_ring=1
        while index_counter>0:
            current_ring+=1
            index_counter-=(current_ring-1)*self.ring_step
        return current_ring
class HexmapIterator:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.length=(self.width*self.height)-1
        self.index=-1
    def __iter__(self):
        return self
    def __next__(self):
        if self.index==self.length:
            raise StopIteration
        else:
            self.index+=1
            return list(range(self.index%self.height))
