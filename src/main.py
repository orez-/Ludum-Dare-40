import enum

import arcade
import attr


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

TILE_SIZE = 100
TILE_GAP = 5


TEXTURES = {
    'item_grapple_hook': arcade.load_texture('assets/grapplehook.png'),
    'item_mushroom': arcade.load_texture('assets/mushroom.png'),
    'pointer': arcade.load_texture('assets/pointer.png'),
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
    def __init__(self, *, shape, name, **kwargs):
        super().__init__(**kwargs)
        self.shape = shape
        self.name = name

    @classmethod
    def get_grapple_hook(cls, x, y):
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
            name='grapple hook',
        )
        ii.append_texture(TEXTURES['item_grapple_hook'])
        ii.set_texture(0)
        return ii


    @classmethod
    def get_mushroom(cls, x, y):
        ii = InventoryItem(
            center_x=x,
            center_y=y,
            shape=[
                (0, 0),
                (1, 0),
                (2, 0),
                (1, 1),
                (1, 2),
            ],
            name='mushroom',
        )
        ii.append_texture(TEXTURES['item_mushroom'])
        ii.set_texture(0)
        return ii


class Pointer(arcade.sprite.Sprite):
    def __init__(self):
        super().__init__(

        )
        self.append_texture(TEXTURES['pointer'])
        self.set_texture(0)


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
            InventoryItem.get_grapple_hook(105 * 1.5, 105 * 1.5),
            InventoryItem.get_mushroom(105 * 3.5, 105 * 1.5),
        ]
        self.pointer = Pointer()

    def draw(self):
        for tile in self.tiles.values():
            tile.draw()

        for item in self.items:
            item.draw()

        self.pointer.draw()

    def handle_action(self, action):
        if action == PlayerAction.up:
            self.pointer.top += 105
        elif action == PlayerAction.down:
            self.pointer.top -= 105
        elif action == PlayerAction.right:
            self.pointer.left += 105
        elif action == PlayerAction.left:
            self.pointer.left -= 105


class PlayerAction(enum.Enum):
    right = 'right'
    down = 'down'
    left = 'left'
    up = 'up'


key_config = {
    arcade.key.RIGHT: PlayerAction.right,
    arcade.key.LEFT: PlayerAction.left,
    arcade.key.UP: PlayerAction.up,
    arcade.key.DOWN: PlayerAction.down
}


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

    def on_key_press(self, symbol, modifier):
        if (symbol, modifier) == (arcade.key.Q, arcade.key.MOD_COMMAND):
            self.close()
            return
        action = key_config.get(symbol)
        if action:
            self.ui.handle_action(action)
        else:
            print(symbol, modifier)

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
