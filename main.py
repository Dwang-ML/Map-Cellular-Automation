import arcade
import random
import copy

class CellularAutomation(arcade.Window):
    def __init__(self, width, height, title, cs):
        # Setup window
        super().__init__(width, height, title)
        arcade.set_background_color((8, 122, 194, 255))

        # Setup basic variables
        self.cell_size = cs
        self.HEIGHT = height // cs
        self.WIDTH = width // cs

        # Setup initial map
        self.map = []
        for y in range(self.HEIGHT):
            temp = []
            for x in range(self.WIDTH):
                temp.append((random.choice([1]*30+[0]), 0))  # (type, age) type: {0: sand, 1: water, 2: grass} / age: int
            self.map.append(temp)

        # Setup rendering tools
        self.map_list = arcade.SpriteList()

        # Track iterations
        self.iterations = 0
        self.max_iterations = 18

        # # Schedule update
        arcade.schedule(self.calculate_next, 0.01)

    def render_(self):
        self.map_list = arcade.SpriteList()
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                tile = self.map[y][x][0]
                position_x = self.cell_size // 2 + (x + 1) * self.cell_size
                position_y = self.cell_size // 2 + (y + 1) * self.cell_size
                try:
                    if tile == 2 and self.map[y - 1][x][0] == 0:
                        sprite = arcade.SpriteSolidColor(self.cell_size, self.cell_size,
                                                         position_x + round(self.cell_size),
                                                         position_y - round(self.cell_size), color=(0, 126, 22, 255))
                        self.map_list.append(sprite)
                        continue
                except:
                    pass
                if tile != 0:
                    continue
                sprite = arcade.SpriteSolidColor(self.cell_size, self.cell_size, position_x + round(self.cell_size), position_y - round(self.cell_size), color=(217, 186, 84, 255))
                self.map_list.append(sprite)

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                tile = self.map[y][x][0]
                age = self.map[y][x][1]
                differ = age * 2
                position_x = self.cell_size // 2 + (x + 1) * self.cell_size
                position_y = self.cell_size // 2 + (y + 1) * self.cell_size
                color = (0, 0, 0, 0)
                if tile == 0:
                    color = (237, 206, 104)
                elif tile == 1:
                    continue
                elif tile == 2:
                    r, g, b = 28, 156, 62
                    color = (max(r - min(differ, r), 14), max(g - min(differ, g), 135), max(b - min(differ, b), 40))
                sprite = arcade.SpriteSolidColor(self.cell_size, self.cell_size, position_x, position_y, color=color)
                self.map_list.append(sprite)

    def calculate_next(self, delta_time):
            # Create temporary variable for the next map
            temp_map = copy.deepcopy(self.map)

            # Track iterations
            self.iterations += 1
            if self.iterations >= self.max_iterations:
                self.clean()
                arcade.unschedule(self.calculate_next)

            # Calculate
            for y in range(self.HEIGHT):
                for x in range(self.WIDTH):
                    surrounding = self.check_surrounding(x, y)
                    if surrounding:
                        if self.map[y][x][0] == 0:
                            temp_map[y][x] = self.calculate_sand(self.map[y][x], surrounding)
                        elif self.map[y][x][0] == 1:
                            temp_map[y][x] = self.calculate_water(self.map[y][x], surrounding)
                        else:
                            temp_map[y][x] = self.calculate_grass(self.map[y][x], surrounding, 10)
                    else:
                        pass

            # Set the actual map to the new map
            self.map = copy.deepcopy(temp_map)

    def calculate_sand(self, current_cell, surrounding):
        if surrounding['1'] == 0:
            return (2, 0)
        return (0, current_cell[1] + 1)

    def calculate_water(self, current_cell, surrounding):
        if surrounding['0'] >= 3:
            return (0, 0)

        return (1, current_cell[1] + 1)

    def calculate_grass(self, current_cell, surrounding, death_age):
        return (2, current_cell[1] + 1)


    def check_surrounding(self, x, y):
        temp_list = []
        temp_dict = {}
        try:
            temp_list.append(self.map[y][x + 1][0])
            temp_list.append(self.map[y][x - 1][0])
            temp_list.append(self.map[y + 1][x][0])
            temp_list.append(self.map[y - 1][x][0])
            temp_list.append(self.map[y + 1][x + 1][0])
            temp_list.append(self.map[y + 1][x - 1][0])
            temp_list.append(self.map[y - 1][x + 1][0])
            temp_list.append(self.map[y - 1][x - 1][0])
            temp_dict['0'] = temp_list.count(0)
            temp_dict['1'] = temp_list.count(1)
            temp_dict['2'] = temp_list.count(2)
            return temp_dict
        except:
            return False

    def clean(self):
        # Create a temporary map to store the updated values
        temp_map = []
        for y in range(self.HEIGHT):
            temp = []
            for x in range(self.WIDTH):
                temp.append((0, 0))  # Initialize with (0, 0)
            temp_map.append(temp)

        # Update each cell based on the isolation condition
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.is_isolated_sand(x, y):
                    temp_map[y][x] = (0, 0)  # Change isolated cells to (0, 0)
                else:
                    temp_map[y][x] = self.map[y][x]  # Keep non-isolated cells unchanged

                if self.is_isolated_water(x, y):
                    temp_map[y][x] = (1, 0)  # Change isolated cells to (0, 0)
                else:
                    temp_map[y][x] = self.map[y][x]  # Keep non-isolated cells unchanged

        # Replace the original map with the updated map
        self.map = copy.deepcopy(temp_map)

    def is_isolated_sand(self, x, y):
        temp_list = []
        try:
            temp_list.append(self.map[y][x + 1][0])
            temp_list.append(self.map[y][x - 1][0])
            temp_list.append(self.map[y + 1][x][0])
            temp_list.append(self.map[y - 1][x][0])
            if temp_list.count(0) >= 3:
                return True
            return False
        except:
            return True

    def is_isolated_water(self, x, y):
        temp_list = []
        try:
            temp_list.append(self.map[y][x + 1][0])
            temp_list.append(self.map[y][x - 1][0])
            temp_list.append(self.map[y + 1][x][0])
            temp_list.append(self.map[y - 1][x][0])
            if temp_list.count(1) >= 2:
                return True
            return False
        except:
            return True

    def on_draw(self):
        self.clear()
        self.render_()
        self.map_list.draw()


if __name__ == '__main__':
    cell_size = 5
    window = CellularAutomation(800, 600, 'Map Cellular Automation', cell_size)
    arcade.run()
