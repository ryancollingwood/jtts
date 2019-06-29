BRICK = 0
BACKGROUND = 1
SHOOT = 2
ITEM = 3
SCROLL = 4
KEY = 5
MONSTER_1 = 6
DOOR = 7
STAIRS = 8
MONSTER_2 = 9
METAL = 10
REPAIR = 11

ENTITY_TYPE_WALL = 0
ENTITY_TYPE_SPRITE = 1
ENTITY_TYPE_DIRECTIONAL_SPRITE = 2

ENTITY_TYPE_MAPPING = {
    BRICK: ENTITY_TYPE_WALL,
    BACKGROUND:  ENTITY_TYPE_SPRITE,
    SHOOT:  ENTITY_TYPE_SPRITE,
    ITEM:  ENTITY_TYPE_SPRITE,
    SCROLL:  ENTITY_TYPE_SPRITE,
    KEY:  ENTITY_TYPE_SPRITE,
    MONSTER_1:  ENTITY_TYPE_DIRECTIONAL_SPRITE,
    DOOR:  ENTITY_TYPE_SPRITE,
    STAIRS:  ENTITY_TYPE_SPRITE,
    MONSTER_2:  ENTITY_TYPE_SPRITE,
    METAL:  ENTITY_TYPE_SPRITE,
    REPAIR:  ENTITY_TYPE_SPRITE,
}

ENTITY_TEXTURES = ['data/brick.png', 'data/background.png', 'data/shoot.png', 'data/item.png',
          'data/scroll.png', 'data/key.png', 'data/monster1', 'data/door.png',
          'data/stairs.png', 'data/monster2.png', 'data/metal.png', 'data/repair.png']
