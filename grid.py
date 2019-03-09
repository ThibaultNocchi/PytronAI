import random

# Grid
class Grid:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # 0,0 is bottom left.
        self.data = [[(0, 0)]*self.width for i in range(self.height)]
        self.bonus = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 21)

    def get_point(self, x: int, y: int) -> tuple:
        """
        Get the value associated to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        return self.data[y][x]

    def set_point(self, x: int, y: int, value: tuple):
        """
        Set a value to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
            :param value:tuple: Value to set.
        """
        self.data[y][x] = value

    def reset_point(self, x: int, y: int):
        """
        Reset the value associated to the coordinates.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        self.data[y][x] = (0, 0)

    def random_point(self):
        """
        Returns a tuple of random coordinates with nothing in it at this position.
            :param self: 
        """
        bx = random.randint(0, self.width - 1)
        by = random.randint(0, self.height - 1)
        for y in range(self.height):
            by = (by + y) % self.height
            for x in range(self.width):
                bx = (bx + x) % self.width
                if self.data[by][bx] == (0, 0):
                    return (bx, by)
        return None, None

    def show_bonus(self):
        """
        Adds (or not) a bonus on the grid.
            :param self: 
        """
        b = random.choice(self.bonus)
        if b != 0:
            bx, by = self.random_point()
            self.set_point(bx, by, (b, 0))