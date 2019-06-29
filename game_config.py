from keybindings import *  # @UnusedWildImport

MOVE_SPEED = 4.0
RUN_SPEED = 7.5

ROTATE_SPEED = 55
RUN_ROTATE_SPEED = 100

FPS = 30

PLAYER_HEIGHT = 0.50
# PLAYER_HEIGHT=1.50

FLOOR_COLOR = (85, 85, 85)
CEILING_COLOR = (15, 15, 15)

WINDOW_3D = (8, 8, 480, 320)

COLORSHIFTS = (255, 255, 255), (192, 192, 192)

SHOOT_DELAY = 0.3

BULLET_SPEED = 5

MESSAGE_BACKGROUND = (233, 166, 106)
MESSAGE_COLOR = (167, 114, 66)

PLAYER_HEALTH = 100

WIN_MESSAGES = [
    ("When the control machine shuts down, all the demons stop in their tracks. " +
     "You head back down to the village, unsure if you should tell anyone of what you saw here... " +
     "or if they'll even let you in, now that you know the secret of the village."
     ),
    ("You find some runes, without your predecessor's gift for translation, it'll take hours to work out. " +
     "You're in no hurry to return to your village, so you sit down and begin studying.\n" +
     "It says that your whole village is on a journey to a distant land, to begin life anew. "
     ),

    ("To keep your village safe from the dangers of the aether, your ancestors moved deep underground. " +
     "To keep the villagers from being harmed by the repair creatures, the commandment to not journey " +
     "to the surface was created. They didn't think the creatures would break over the years.\n"
     ),
    ("The runes say your journey will take 458 years. From the history of your village, you know they've been underground" +
     "for less than half that long. You resign yourself to a life underground, knowing neither you nor your " +
     "children will ever see the end of your journey, and the surface of the new world."
    )
]

# massage some types into more easily usable forms
import ctypes

COLOR3 = (ctypes.c_ubyte * 4)
FLOOR_COLOR_V = COLOR3(*FLOOR_COLOR)
CEILING_COLOR_V = COLOR3(*CEILING_COLOR)

COLORSHIFTS_V = [COLOR3(*rgb) for rgb in COLORSHIFTS]

MESSAGE_BACKGROUND_SCALED = [x / 255.0 for x in MESSAGE_BACKGROUND] + [1.0]
MESSAGE_COLOR_4 = MESSAGE_COLOR + (255,)
