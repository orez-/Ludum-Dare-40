import arcade
import attr


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

TILE_SIZE = 100
TILE_GAP = 5


TEXTURES = {
    'item_shape': arcade.load_texture('assets/shape.png'),
}


@attr.s(slots=True)
class InventoryTile:
    x = attr.ib()
    y = attr.ib()
    size = attr.ib(default=TILE_SIZE)

    def draw(self):
        """ Draw our rectangle """
        arcade.draw_rectangle_filled(
            center_x=self.x,
            center_y=self.y,
            width=self.size,
            height=self.size,
            color='CCCCCC',
        )


class InventoryItem(arcade.sprite.Sprite):
    def __init__(self, *, shape, **kwargs):
        super().__init__(**kwargs)
        self.shape = shape

    @classmethod
    def get_thing(cls, x, y):
        ii = InventoryItem(
            center_x=x,
            center_y=y,
            shape=[
                (1, 0),
                (0, 1),
                (1, 1),
                (2, 1),
                (2, 2),
            ],
        )
        ii.append_texture(TEXTURES['item_shape'])
        ii.set_texture(0)
        return ii


class InventoryScreen:
    def __init__(self):
        offset_x = 55
        offset_y = 55
        self.tiles = {
            (x, y): InventoryTile(
                x=x * (TILE_SIZE + TILE_GAP) + offset_x,
                y=y * (TILE_SIZE + TILE_GAP) + offset_y,
            )
            for x in range(5)
            for y in range(4)
        }
        self.items = [
            InventoryItem.get_thing(300, 300),
        ]

    def draw(self):
        for tile in self.tiles.values():
            tile.draw()

        for item in self.items:
            item.draw()


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
