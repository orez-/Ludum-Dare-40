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
    'bg': arcade.load_texture('assets/bg.png'),
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


TWEEN_RATE = 5
class Pointer(arcade.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.append_texture(TEXTURES['pointer'])
        self.set_texture(0)

        self._tween = {}
        self._tween_progress = 1

    def update(self, dt):
        if self._tween_progress == 1:
            return
        self._tween_progress = min(1, self._tween_progress + dt * TWEEN_RATE)
        for key, (start, end) in self._tween.items():
            setattr(self, key, (end - start) * self._tween_progress + start)
        # need to force rescale :\
        if 'scale' in self._tween:
            self.set_texture(0)
        if self._tween_progress == 1:
            self._tween = {}

    def _set_tween(self, **properties):
        self._tween = {
            key: (getattr(self, key), value)
            for key, value in properties.items()
        }
        self._tween_progress = 0

    def move_left(self):
        if self._tween:
            return
        self._set_tween(left=self.left - 105)

    def move_right(self):
        if self._tween:
            return
        self._set_tween(left=self.left + 105)

    def move_up(self):
        if self._tween:
            return
        self._set_tween(top=self.top + 105)

    def move_down(self):
        if self._tween:
            return
        self._set_tween(top=self.top - 105)


class InventoryScreen:
    def __init__(self):
        offset_x = 55
        offset_y = 55
        self.tiles = {
            ('inventory', x, y): InventoryTile(
                x=x * (TILE_SIZE + TILE_GAP) + offset_x,
                y=y * (TILE_SIZE + TILE_GAP) + offset_y,
            )
            for x in range(5)
            for y in range(4)
        }
        workspace_tile_size = 50
        self.tiles.update({
            ('workspace', x, y): InventoryTile(
                x=x * (workspace_tile_size + 2.5) + 700,
                y=y * (workspace_tile_size + 2.5) + 32,
                size=workspace_tile_size,
            )
            for x in range(5)
            for y in range(10)
        })
        self.items = [
            InventoryItem.get_grapple_hook(105 * 1.5, 105 * 1.5),
            InventoryItem.get_mushroom(105 * 3.5, 105 * 1.5),
        ]
        self.pointer = Pointer()

    def draw(self):
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT, TEXTURES['bg'],
        )

        for tile in self.tiles.values():
            tile.draw()

        for item in self.items:
            item.draw()

        self.pointer.draw()

    def update(self, dt):
        self.pointer.update(dt)

    def handle_action(self, action):
        if action == PlayerAction.up:
            self.pointer.move_up()
        elif action == PlayerAction.down:
            self.pointer.move_down()
        elif action == PlayerAction.right:
            self.pointer.move_right()
        elif action == PlayerAction.left:
            self.pointer.move_left()


class PlayerAction(enum.Enum):
    right = 'right'
    down = 'down'
    left = 'left'
    up = 'up'
    select = 'select'


key_config = {
    arcade.key.RIGHT: PlayerAction.right,
    arcade.key.LEFT: PlayerAction.left,
    arcade.key.UP: PlayerAction.up,
    arcade.key.DOWN: PlayerAction.down,
    arcade.key.ENTER: PlayerAction.select,
    arcade.key.D: PlayerAction.right,
    arcade.key.A: PlayerAction.left,
    arcade.key.W: PlayerAction.up,
    arcade.key.S: PlayerAction.down,
    arcade.key.SPACE: PlayerAction.select,
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
        self.ui.update(dt)

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
