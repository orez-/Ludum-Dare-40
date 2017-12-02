import enum

import arcade
import attr


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

ASSET_TILE_SIZE = 100  # size of a tile as expected by assets
TILE_SIZE_GAP_RATIO = 20


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
    size = attr.ib()

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


class InventoryGrid:
    def __init__(self, tile_size, rows, columns, offset_x, offset_y):
        self.tile_size = tile_size
        self.scale = tile_size / ASSET_TILE_SIZE
        self.gap = tile_size / TILE_SIZE_GAP_RATIO
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.rows = rows
        self.columns = columns
        self.tiles = {
            (x, y): InventoryTile(
                x=x * (self.tile_size + self.gap) + offset_x,
                y=y * (self.tile_size + self.gap) + offset_y,
                size=self.tile_size,
            )
            for x in range(columns)
            for y in range(rows)
        }

    def draw(self):
        for tile in self.tiles.values():
            tile.draw()

    def pointer_coord_at(self, row, col):
        return (
            col * (self.tile_size + self.gap) + self.offset_x,
            row * (self.tile_size + self.gap) + self.offset_y,
            self.scale,
        )


TWEEN_RATE = 5
class Pointer(arcade.sprite.Sprite):
    def __init__(self, left, top, scale):
        super().__init__()

        self.scale = scale  # needs to happen before texture set.

        self.append_texture(TEXTURES['pointer'])
        self.set_texture(0)

        # needs to happen after texture set.
        self.left = left
        self.top = top

        self._tween = {}
        self._tween_progress = 1

    @property
    def can_move(self):
        return self._tween_progress == 1

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
            if getattr(self, key) != value
        }
        self._tween_progress = 0

    def move_to(self, x, y, scale):
        self._set_tween(left=x, top=y, scale=scale)


class InventoryScreen:
    def __init__(self):
        self.inventory = InventoryGrid(
            tile_size=100,
            rows=4,
            columns=5,
            offset_x=55 + 60,  # arbitrary
            offset_y=210,  # arbitrary
        )
        self.workspace = InventoryGrid(
            tile_size=50,
            rows=10,
            columns=5,
            offset_x=750,
            offset_y=32 + 104,  # sorry
        )
        self.grids = {
            'inventory': self.inventory,
            'workspace': self.workspace,
        }
        self.items = [
            InventoryItem.get_grapple_hook(105 * 1.5, 105 * 1.5),
            InventoryItem.get_mushroom(105 * 3.5, 105 * 1.5),
        ]
        self.pointer_location = ['inventory', 0, 0]
        x, y, scale = self.inventory.pointer_coord_at(0, 0)
        self.pointer = Pointer(left=x, top=y, scale=scale)

    def draw(self):
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT, TEXTURES['bg'],
        )

        self.inventory.draw()
        self.workspace.draw()

        for item in self.items:
            item.draw()

        self.pointer.draw()

    def update(self, dt):
        self.pointer.update(dt)

    def handle_action(self, action):
        if action in DIRECTIONS:
            if not self.pointer.can_move:
                return
            grid, c, r = self.pointer_location
            if action == PlayerAction.up:
                if r >= self.grids[grid].rows - 1:
                    return
                self.pointer_location[2] += 1
            elif action == PlayerAction.down:
                if r <= 0:
                    return
                self.pointer_location[2] -= 1
            elif action == PlayerAction.right:
                if c + 1 >= self.grids[grid].columns:
                    if grid != 'inventory':
                        return
                    self.pointer_location = ['workspace', 0, 0]
                else:
                    self.pointer_location[1] += 1
            elif action == PlayerAction.left:
                if not c:
                    if grid != 'workspace':
                        return
                    self.pointer_location = ['inventory', self.inventory.columns - 1, 0]
                else:
                    self.pointer_location[1] -= 1
            grid, c, r = self.pointer_location
            x, y, scale = self.grids[grid].pointer_coord_at(r, c)
            self.pointer.move_to(x, y, scale)


class PlayerAction(enum.Enum):
    right = 'right'
    down = 'down'
    left = 'left'
    up = 'up'
    select = 'select'


DIRECTIONS = {
    PlayerAction.right,
    PlayerAction.down,
    PlayerAction.left,
    PlayerAction.up,
}


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
