import collections
import enum

import arcade
import attr


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

ASSET_TILE_SIZE = 100  # size of a tile as expected by assets
TILE_SIZE_GAP_RATIO = 20
ASSET_TILE_TOTAL = ASSET_TILE_SIZE + ASSET_TILE_SIZE / TILE_SIZE_GAP_RATIO


TEXTURES = {
    'item_grapple_hook': [arcade.load_texture('assets/grapplehook.png')],
    'item_mushroom': [arcade.load_texture('assets/mushroom.png')],
    'item_battleaxe': [arcade.load_texture('assets/battleaxe.png')],
    'item_gascan': [arcade.load_texture('assets/gascan.png')],
    'pointer': arcade.load_textures(
        'assets/pointer.png',
        [
            (0, 0, 64, 64),
            (64, 0, 64, 64),
            (128, 0, 64, 64),
        ],
    ),
    'bg': [arcade.load_texture('assets/bg.png')],
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


ItemType = collections.namedtuple('ItemType', 'shape textures')
ITEM_TYPES = {
    'grapple_hook': ItemType(
        shape=[(1, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
        textures=TEXTURES['item_grapple_hook'],
    ),
    'mushroom': ItemType(
        shape=[(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
        textures=TEXTURES['item_mushroom'],
    ),
    'battleaxe': ItemType(
        shape=[(1, 0), (1, 1), (0, 1), (0, 2), (0, 3)],
        textures=TEXTURES['item_battleaxe'],
    ),
    'gascan': ItemType(
        shape=[(1, 0), (1, 1), (0, 1), (0, 2), (1, 2)],
        textures=TEXTURES['item_gascan'],
    ),
}

TWEEN_RATE = 5
class TweenableSprite(arcade.sprite.Sprite):
    def __init__(self, scale, left, top, textures):
        super().__init__(scale=scale)

        self._frame = 0
        self.textures = textures
        self.set_texture(self._frame)

        # needs to happen after texture set.
        self.left = left
        self.top = top

        self.offset_x = 0
        self.offset_y = 0

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
            self.set_texture(self._frame)
        if self._tween_progress == 1:
            self.angle %= 360
            self._tween = {}

    def _set_tween(self, **properties):
        self._tween = {
            key: (getattr(self, key), value)
            for key, value in properties.items()
            if getattr(self, key) != value
        }
        self._tween_progress = 0

    def set_offset(self, x, y):
        old_x = self.offset_x * self.scale
        old_y = self.offset_y * self.scale
        self.offset_x = x
        self.offset_y = y
        self.move_to(
            self.left - old_x,
            self.top - old_y,
            self.scale,
        )

    def move_to(self, x, y, scale):
        self._set_tween(
            left=x + self.offset_x * scale,
            top=y + self.offset_y * scale,
            scale=scale,
        )


class InventoryItem(TweenableSprite):
    def __init__(self, *, shape, name, textures, left, top, scale):
        super().__init__(
            scale=scale,
            left=left,
            top=top,
            textures=textures,
        )
        self.shape = list(shape)
        self.center_row = max(y for _, y in self.shape) / 2
        self.center_col = max(x for x, _ in self.shape) / 2
        self.name = name

        self.row = None
        self.col = None

    @classmethod
    def get_item(cls, item_type, left, top, scale):
        shape, textures = ITEM_TYPES[item_type]

        return InventoryItem(
            left=left,
            top=top,
            shape=shape,
            scale=scale,
            name=item_type,
            textures=textures,
        )

    def item_coords(self):
        for x, y in self.shape:
            yield self.col + x, self.row - y

    def rotate_left(self):
        rounding = 0
        left = self.left
        top = self.top
        # if self.center_row % 1 != self.center_col % 1:
        #     rounding = 0.5
        self.shape = [
            (
                y - self.center_row + self.center_col + rounding,
                self.center_col - x + self.center_row + rounding,
            )
            for x, y in self.shape
        ]
        self._set_tween(
            angle=self.angle + 90,
            left=left,
            top=top,
        )

    def rotate_right(self):
        rounding = 0
        left = self.left
        top = self.top
        # if self.center_row % 1 != self.center_col % 1:
        #     rounding = 0.5
        self.shape = [
            (
                self.center_row - y + self.center_col,
                x - self.center_col + self.center_row,
            )
            for x, y in self.shape
        ]
        self._set_tween(angle=self.angle - 90)

    def __repr__(self):
        return self.name


class Pointer(TweenableSprite):
    def __init__(self, left, top, scale):
        super().__init__(
            scale=scale,
            left=left,
            top=top,
            textures=TEXTURES['pointer'],
        )

        self.lifted_item = None

    def point_hand(self):
        self._frame = 0
        self.set_texture(self._frame)

    def open_hand(self):
        self._frame = 1
        self.set_texture(self._frame)

    def grab_hand(self):
        self._frame = 2
        self.set_texture(self._frame)


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
        self.contents = {}

    def place_item(self, item, row, col):
        item.row = row
        item.col = col
        safe = all(
            0 <= x < self.columns and
            0 <= y < self.rows and
            not self.contents.get((x, y))
            for x, y in item.item_coords()
        )
        if not safe:
            return False
        for x, y in item.item_coords():
            assert not (x % 1 or y % 1), (x, y)
            self.contents[x, y] = item
        self.print_grid()
        return True

    def lift_item(self, row, col):
        item = self.contents.get((col, row))
        if not item:
            return None, None, None
        for x, y in item.item_coords():
            item_at = self.contents.pop((x, y))
            assert item_at is item, item_at
        # item.row_offset = row - item.row
        # item.col_offset = col - item.col
        print(item.center_row, row, item.row, item.center_col, col, item.col)
        # item.row = None
        # item.col = None
        return item, item.row - item.center_row, item.col + item.center_col

    def get_item(self, row, col):
        return self.contents.get((col, row))

    def draw(self):
        for tile in self.tiles.values():
            tile.draw()

    def pointer_coord_at(self, row, col):
        return (
            int(col * (self.tile_size + self.gap) + self.offset_x),
            int(row * (self.tile_size + self.gap) + self.offset_y),
            self.scale,
        )

    def item_coord_at(self, row, col):
        """
        Transform a row,col coord to screen x, y, and scale.
        """
        return (
            int(col * (self.tile_size + self.gap) + self.offset_x - self.tile_size / 2 - self.gap),
            int(row * (self.tile_size + self.gap) + self.offset_y + self.tile_size / 2 + self.gap),
            self.scale,
        )

    def print_grid(self):
        for y in range(self.rows)[::-1]:
            for x in range(self.columns):
                item = self.contents.get((x, y))
                if not item:
                    print(end='-')
                else:
                    print(end=item.name[0])
            print()
        print()


class InventoryScreen:
    """
    Main UI controller for inventory game.
    """
    def __init__(self):
        # grids
        inventory = InventoryGrid(
            tile_size=100,
            rows=4,
            columns=5,
            offset_x=55 + 60,  # arbitrary
            offset_y=210,  # arbitrary
        )
        workspace = InventoryGrid(
            tile_size=50,
            rows=10,
            columns=5,
            offset_x=750,
            offset_y=32 + 104,  # sorry
        )
        self.grids = {
            'inventory': inventory,
            'workspace': workspace,
        }

        # items
        self.items = []
        # self.add_new_item('grapple_hook', 'inventory', 3, 0)
        self.add_new_item('gascan', 'inventory', 3, 0)
        # self.add_new_item('mushroom', 'inventory', 3, 2)
        self.add_new_item('battleaxe', 'inventory', 3, 3)

        # pointer
        self.pointer_location = ['inventory', 0, 0]
        x, y, scale = inventory.pointer_coord_at(0, 0)
        self.pointer = Pointer(left=x, top=y, scale=scale)

    def add_new_item(self, item_name, grid_name, row, col):
        """
        Add an entirely new item to the world of the inventory screen.
        """
        grid = self.grids[grid_name]
        x, y, scale = grid.item_coord_at(row, col)
        item = InventoryItem.get_item(item_name, x, y, scale)
        self.items.append(item)
        grid.place_item(item, row, col)

    def draw(self):
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT, TEXTURES['bg'][0],
        )

        for grid in self.grids.values():
            grid.draw()

        for item in self.items:
            item.draw()

        self.pointer.draw()

    def update(self, dt):
        self.pointer.update(dt)
        for item in self.items:
            item.update(dt)

    def _handle_move(self, action):
        if not self.pointer.can_move:
            return
        grid, c, r = self.pointer_location
        if action == PlayerAction.up:
            if r >= self.grids[grid].rows - 1:
                return
            self.pointer_location[2] += 1
        elif action == PlayerAction.down:
            if r < 1:
                return
            self.pointer_location[2] -= 1
        elif action == PlayerAction.right:
            if c + 2 > self.grids[grid].columns:
                if grid != 'inventory':
                    return
                self.pointer_location = ['workspace', 0, 0]
            else:
                self.pointer_location[1] += 1
        elif action == PlayerAction.left:
            if c < 1:
                if grid != 'workspace':
                    return
                self.pointer_location = ['inventory', self.grids['inventory'].columns - 1, 0]
            else:
                self.pointer_location[1] -= 1
        grid_name, c, r = self.pointer_location
        grid = self.grids[grid_name]
        x, y, scale = grid.pointer_coord_at(r, c)
        self.pointer.move_to(x, y, scale)
        if self.pointer.lifted_item:
            item = self.pointer.lifted_item

            cr = item.center_row
            cc = item.center_col
            print(item.angle)
            if item.angle in {90, 270}:
                cr = item.center_col
                cc = item.center_row
            x, y, scale = grid.item_coord_at(
                r + cr,
                c - cc,
            )
            item.move_to(x, y, scale)
        elif grid.get_item(r, c):
            self.pointer.open_hand()
        else:
            self.pointer.point_hand()

    def handle_action(self, action):
        if action in DIRECTIONS:
            self._handle_move(action)
        elif action == PlayerAction.select:
            grid_name, c, r = self.pointer_location
            grid = self.grids[grid_name]
            if self.pointer.lifted_item:  # dropping
                item = self.pointer.lifted_item
                drop_row = r + item.center_row
                drop_col = c - item.center_col
                placed = grid.place_item(self.pointer.lifted_item, drop_row, drop_col)
                if placed:
                    self.pointer.lifted_item = None
                    self.set_pointer_loc(round(r), round(c))
                    if grid.get_item(round(r), round(c)):
                        self.pointer.open_hand()
                    else:
                        self.pointer.point_hand()
            else:  # lifting
                item, dcursor_row, dcursor_col = grid.lift_item(r, c)
                self.pointer.lifted_item = item
                if item:
                    self.pointer.grab_hand()
                    # Fix draw order.
                    self.items.remove(item)
                    self.items.append(item)
                    self.set_pointer_loc(dcursor_row, dcursor_col)
        elif action == PlayerAction.rotate_left:
            item = self.pointer.lifted_item
            if item:
                item.rotate_left()
                print("!", item.center_row, item.center_col)
                # self.set_pointer_loc(
                #     item.row - item.center_row,
                #     item.col + item.center_col,
                # )
        elif action == PlayerAction.rotate_right:
            item = self.pointer.lifted_item
            if item:
                item.rotate_right()

    def set_pointer_loc(self, row, col, grid_name=None):
        if not grid_name:
            grid_name = self.pointer_location[0]
        self.pointer_location = [grid_name, col, row]
        grid = self.grids[grid_name]
        x, y, scale = grid.pointer_coord_at(row, col)
        self.pointer.move_to(x, y, scale)


class PlayerAction(enum.Enum):
    right = 'right'
    down = 'down'
    left = 'left'
    up = 'up'
    select = 'select'
    rotate_left = 'rotate_left'
    rotate_right = 'rotate_right'


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
    arcade.key.BRACKETLEFT: PlayerAction.rotate_left,
    arcade.key.BRACKETRIGHT: PlayerAction.rotate_right,
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
