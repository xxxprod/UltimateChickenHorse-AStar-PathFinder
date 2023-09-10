from typing_extensions import SupportsIndex


class Vec(tuple):

    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]
    
    def empty() -> 'Vec':
        return Vec([0, 0])
    
    def __mul__(self, __value: float) -> 'Vec':
        return Vec([self.x * __value, self.y * __value])
    
    def __add__(self, __value: 'Vec') -> 'Vec':
        return Vec([self.x + __value.x, self.y + __value.y])
    
    def __sub__(self, __value: 'Vec') -> 'Vec':
        return Vec([self.x - __value.x, self.y - __value.y])
    
    def __truediv__(self, __value: float) -> 'Vec':
        return Vec([self.x / __value, self.y / __value])