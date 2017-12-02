import arcade
import attr


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

TILE_SIZE = 100
TILE_GAP = 5

@attr.s(slots=True)
class InventoryTile:
    x = attr.ib()
    y = attr.ib()
    width = attr.ib(default=TILE_SIZE)
    height = attr.ib(default=TILE_SIZE)
    # angle = attr.ib()

    def draw(self):
        """ Draw our rectangle """
        # centers at x, y o_O
        arcade.draw_rectangle_filled(
            self.x,
            self.y,
            self.width,
            self.height,
            # self.color,
            color='CCCCCC',
        )


class InventoryScreen:
    def __init__(self):
        self.tiles = {
            (x, y): InventoryTile(
                x=x * (TILE_SIZE + TILE_GAP),
                y=y * (TILE_SIZE + TILE_GAP),
            )
            for x in range(5)
            for y in range(4)
        }

    def draw(self):
        for tile in self.tiles.values():
            tile.draw()


class MyApplication(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, width, height):
        super().__init__(width, height, title="LD40")
        self.player = None
        self.ui = InventoryScreen()

    def setup(self):
        """ Set up the game and initialize the variables. """

    def update(self, dt):
        """ Move everything """

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()
        self.ui.draw()


def main():
    window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
