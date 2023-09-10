    
from utils.Vec import Vec


class Rect(tuple):

    @property
    def x1(self) -> float:
        return self[0]
    @property
    def y1(self) -> float:
        return self[1]
    @property
    def x2(self) -> float:
        return self[2]
    @property
    def y2(self) -> float:
        return self[3]
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def size(self) -> Vec:
        return Vec([self.width, self.height])
    
    @property
    def center(self) -> Vec:
        return Vec([(self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2])
    
    @property
    def bottomCenter(self) -> Vec:
        return Vec([(self.x1 + self.x2) / 2, self.y1])

    def offset(self, v: Vec) -> 'Rect':
        return Rect([self.x1 + v.x, self.y1 + v.y, self.x2 + v.x, self.y2 + v.y])
    
    def resize(self, v: Vec) -> 'Rect':
        if type(v) == int or type(v) == float:
            v = Vec([v, v])

        return Rect([self.x1 - v.x, self.y1 - v.y, self.x2 + v.x, self.y2 + v.y])
    
    def intersects(self, other: 'Rect') -> bool: 
        # Check for overlap along the x-axis
        if self.x1 > other.x2 or self.x2 < other.x1:
            return False
        
        # Check for overlap along the y-axis
        if self.y1 > other.y2 or self.y2 < other.y1:
            return False
        
        return True  # Rectangles intersect


    def __repr__(self) -> str:
        return f"Rect({round(self[0], 2)}, {round(self[1], 2)}, {round(self[2], 2)}, {round(self[3], 2)})"
