#!/usr/bin/env python
# Journey to the Surface by Foone <foone2@gmail.com>, 2010. 
# Based on:
# pyglet version of NeHe's OpenGL lesson10
# based on the pygame+PyOpenGL conversion by Paul Furber 2001 - m@verick.co.za
# Philip Bober 2007 pdbober@gmail.com

import game_config as conf
import os, random, time
from math import sin, cos, radians
import pyglet
from pyglet.gl import *  # @UnusedWildImport
from pyglet import image
from pyglet.window import key, FPSDisplay
import world
from itertools import groupby
from objects import *  # @UnusedWildImport
from util import TimeLimitedKeyTester
from models import *  # @UnusedWildImport
from entities import ENTITY_TEXTURES, ENTITY_TYPE_DIRECTIONAL_SPRITE, ENTITY_TYPE_MAPPING
import glob
from util import circle_segment

def loadTexture(path):
    textureSurface = pyglet.resource.image(path)
    texid = textureSurface.image_data.create_texture(image.Texture)
    glBindTexture(GL_TEXTURE_2D, texid.id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    return texid

def loadItemResources(entity, resource_map):

    if entity in resource_map:
        return resource_map

    resource_map[entity] = dict()

    path = ENTITY_TEXTURES[entity]

    for root, dirs, files in os.walk(path):
        state = root.replace(path, "").replace("\\", "").replace("/", "")
        state_resources = dict()
        for file in files:
            if file.endswith('.png'):
                state_resources[file.replace(".png", "")] = loadTexture(f"{root}/{file}".replace("\\", "/"))

        if len(state_resources) > 0:
            resource_map[entity][state] = state_resources

    return resource_map

def loadTextures():
    textures = dict()

    for entity in ENTITY_TYPE_MAPPING:
        entity_type = ENTITY_TYPE_MAPPING[entity]
        path = ENTITY_TEXTURES[entity]

        if entity_type != ENTITY_TYPE_DIRECTIONAL_SPRITE:
            textures[entity] = loadTexture(path)
        else:
            textures = loadItemResources(entity, textures)

    return textures


class MainWindow(pyglet.window.Window):
    def __init__(self):
        super(MainWindow, self).__init__(width=640, height=480, visible=False, caption="Journey to the Surface",
                                         resizable=False)
        keys = self.keys = pyglet.window.key.KeyStateHandler()
        self.size = (640, 480,)
        self.push_handlers(keys)
        self.setupGL()
        self.textures = loadTextures()
        self.player = None

        self.fps_display = FPSDisplay(self)

        self.message = None

        pyglet.font.add_file('fonts/04b_11/04B_11__.TTF')
        self.healthLabel = pyglet.text.Label('??',
                                             font_name='04b11',
                                             font_size=24,
                                             x=564, y=480 - 404,
                                             anchor_x='center', anchor_y='center')

        self.loadMap(0)
        self.set_visible(True)

        pyglet.clock.schedule_interval(self.update, 1.0 / conf.FPS)
        self.fireClock = TimeLimitedKeyTester(conf.SHOOT_KEYS, conf.SHOOT_DELAY)

        h, v = conf.COLORSHIFTS_V
        textures = self.textures
        self.textureMap = {
            '#-': (textures[0].id, h),
            '#|': (textures[0].id, v),

            '%-': (textures[7].id, h),
            '%|': (textures[7].id, v),

            '^-': (textures[8].id, h),
            '^|': (textures[8].id, v),

            '&-': (textures[10].id, h),
            '&|': (textures[10].id, v),
        }

        self.resourceMap = dict()

    def loadMap(self, num):
        self.levelNum = num
        map = self.map = world.loadMap('maps/level%02i.txt' % num)
        self.player = Player(map.playerPos, map.playerRot, self.healthUpdate)
        self.monsters = []
        self.bullets = []
        self.resourceMap = dict()
        self.loadItems()
        self.mapChanged()
        self.healthUpdate(self.player)

    def nextMap(self, message=None):
        if message is None:
            self.loadMap(self.levelNum + 1)
        else:
            self.showMessage(message, lambda: self.loadMap(self.levelNum + 1))

    def mapChanged(self):
        self.vertexes, self.quads = self.map.update()

    def healthUpdate(self, player):
        if player.health <= 0:
            self.showMessage("Your bones are never found.", postMessage=lambda: self.close())
        self.healthLabel.text = '%02i%%' % player.health

    def setupGL(self):
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_FLAT)
        glClearColor(*conf.MESSAGE_BACKGROUND_SCALED)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDisable(GL_DITHER)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
        glAlphaFunc(GL_GREATER, 0.0)

    def on_draw(self):
        textures = self.textures
        xpos, ypos, rot = self.player.gl()

        if self.message:
            return self.drawMessage()

        self.draw2D()
        glClear(GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glRotatef(rot, 0.0, 1.0, 0.0)
        glTranslatef(xpos, -conf.PLAYER_HEIGHT, ypos)

        glInterleavedArrays(GL_T2F_V3F, 0, self.vertexes)

        for rgroup in self.quads:
            texid, color = self.textureMap[rgroup.texture]
            glBindTexture(GL_TEXTURE_2D, texid)
            glColor3ubv(color)
            glDrawArrays(GL_QUADS, rgroup.start, rgroup.length)

        glEnable(GL_ALPHA_TEST)

        matrix = (GLfloat * 16)()
        glColor3ub(255, 255, 255)
        for texid, objs in groupby(self.objects + self.monsters + self.bullets, lambda o: o.texid):
            glBindTexture(GL_TEXTURE_2D, texid)
            for obj in objs:
                x, y, _ = obj.pos
                glPushMatrix()
                glTranslatef(x, 0.0, y)
                glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
                for i in range(0, 3, 2):
                    for j in range(0, 3):
                        matrix[i * 4 + j] = 1.0 if i == j else 0.0
                glLoadMatrixf(matrix)
                glBegin(GL_QUADS)
                z, size = obj.z, obj.size
                glTexCoord2f(0.0, 0.0);
                glVertex3f(-size, z - size, 0.0)
                glTexCoord2f(1.0, 0.0);
                glVertex3f(+size, z - size, 0.0)
                glTexCoord2f(1.0, 1.0);
                glVertex3f(+size, z + size, 0.0)
                glTexCoord2f(0.0, 1.0);
                glVertex3f(-size, z + size, 0.0)
                glEnd()
                glPopMatrix()

        glDisable(GL_ALPHA_TEST)

        self.fps_display.draw()

    def drawMessage(self):
        w, h = self.size
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.label.draw()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

    def draw2D(self):
        w, h = self.size
        x, y, w3, h3 = conf.WINDOW_3D
        ystart = h - h3 - y
        textures = self.textures
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        textures[1].blit(0, 0)

        y = h - 64
        for item in self.player.inventory:
            glBindTexture(GL_TEXTURE_2D, item.texid)

            glBegin(GL_QUADS)
            c = 560
            size = 32
            glTexCoord2f(0.0, 0.0)
            glVertex3f(c - size, y - size, 0.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(c + size, y - size, 0.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(c + size, y + size, 0.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(c - size, y + size, 0.0)
            glEnd()

            y -= 64

        self.healthLabel.draw()

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)

        glBegin(GL_QUADS)
        glColor3ubv(conf.FLOOR_COLOR_V)
        glVertex2i(x, ystart)
        glVertex2i(x + w3, ystart)
        glVertex2i(x + w3, int(ystart + h3 / 2))
        glVertex2i(x, int(ystart + h3 / 2))

        glColor3ubv(conf.CEILING_COLOR_V)
        glVertex2i(x, int(ystart + h3 / 2))
        glVertex2i(x + w3, int(ystart + h3 / 2))
        glVertex2i(x + w3, int(ystart + h3))
        glVertex2i(x, int(ystart + h3))

        glEnd()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glViewport(x, ystart, w3, h3)

    def on_resize(self, w, h):
        self.size = (w, h)
        x, y, w3, h3 = conf.WINDOW_3D
        glViewport(x, h - h3 - y, w3, h3)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        try:
            ratio = float(w) / h
        except ZeroDivisionError:
            ratio = 1.0

        gluPerspective(45, ratio, 0.05, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def on_key_press(self, sym, mod):
        if self.message:
            if sym in (key.ESCAPE, key.SPACE, key.ENTER, key.DOWN):
                self.message = None
                if self.postMessage:
                    self.postMessage()
                return
        if sym == key.ESCAPE:
            self.close()
        elif sym == key.SPACE:
            print(self.player)
        elif sym in (conf.SHOOT_KEYS):
            if self.fireClock.update(0.0, self.keys):
                self.fire()
        elif sym == key.F2:
            self.nextMap()
        elif sym == key.F3:
            self.winGame()

    def update(self, dt):
        if self.message:
            return  # no processing while messing
        keys = self.keys
        player = self.player
        rot = player.rot
        running = keys[conf.RUN_KEY]
        rotdir = keys[conf.TURN_RIGHT] - keys[conf.TURN_LEFT]
        if rotdir:
            rotspeed = conf.RUN_ROTATE_SPEED if running else conf.ROTATE_SPEED
            player.rotate(rotspeed * rotdir * dt)

        move = keys[conf.MOVE_BACKWARDS] - keys[conf.MOVE_FORWARD]
        if move:
            speed = conf.RUN_SPEED if keys[conf.RUN_KEY] else conf.MOVE_SPEED
            move_scale = dt * speed
            angle = radians(360 - rot)
            vx, vy = move * sin(angle) * move_scale, move * cos(angle) * move_scale
            player.vel = [vx / dt, vy / dt]
            moved = self.movePlayer(player.x, player.y, vx, vy)  # @UnusedVariable # for later

        self.collideGeneric(self.objects + self.monsters)
        if self.fireClock.update(dt, keys):
            self.fire()

        if self.bullets:
            self.collideBullets()
        self.objects = self.updateItemCollection(self.objects, dt)
        self.monsters = self.updateItemCollection(self.monsters, dt)
        self.bullets = self.updateItemCollection(self.bullets, dt)

    def updateItemCollection(self, items, dt):
        out = []
        player = self.player
        for obj in items:
            obj.update(dt, player=player)
            if obj.alive:
                out.append(obj)  # thrash my GC, please

                if ENTITY_TYPE_MAPPING[obj.entity_id] == ENTITY_TYPE_DIRECTIONAL_SPRITE:
                    # move this to an update methods

                    side_index = circle_segment(obj.rot)

                    obj.texid = self.textures[obj.entity_id]["stand"][str(side_index)].id

        return out


    def collideBullets(self):
        for monster in self.monsters:
            mx, my = monster.xy
            for bullet in self.bullets:
                bx, by = bullet.xy
                if monster.alive:
                    if (mx - bx) ** 2 + (my - by) ** 2 < monster.radius ** 2:
                        try:
                            monster.damage(bullet.damage)
                        except FinalBossKilled:
                            self.winGame()

                        bullet.die()
                        break  # out of the bullet loop, cause we've been killed

    def collideGeneric(self, objects):
        x, y, _ = self.player.pos
        for obj in objects:
            ox, oy, _ = obj.pos
            if (ox - x) ** 2 + (oy - y) ** 2 < obj.radius ** 2:
                obj.touched(self)

    def movePlayer(self, oxpos, oypos, xrel, yrel):
        for x, y in ((xrel, yrel), (xrel * 0.5, 0.0), (0, yrel * 0.5)):
            if self.movePlayerInternal(oxpos, oypos, x, y):
                return True
        return False

    def movePlayerInternal(self, oxpos, oypos, xrel, yrel):
        nxpos = oxpos + xrel
        nypos = oypos + yrel

        try:
            if nxpos < 0. or nypos < 0.:
                return False
            if self.map.collideMap[int(nxpos * 8.0), int(nypos * 8.0)]:
                return False
        except IndexError:
            return False
        self.player.move(nxpos, nypos)
        return True

    def fire(self):
        self.bullets.append(Bullet(self.player, self.map, conf.BULLET_SPEED, self.textures[2].id))
        self.handleNewItems()

    def handleNewItems(self):
        self.objects.sort(key=lambda o: o.texid)
        self.bullets.sort(key=lambda o: o.texid)
        self.monsters.sort(key=lambda o: o.texid)


    def loadItems(self):
        objs = self.objects = []
        for char, pos, extra in self.map.items:
            item = Item(3, pos, char, extra, map=self.map)
            target = objs
            if isinstance(item.model, MonsterModel):
                item = MonsterItem(item.model.texture, item.xy, item.type, item.model, self.map)
                target = self.monsters
            item_textures = item.findTexture()

            if ENTITY_TYPE_MAPPING[item_textures] != ENTITY_TYPE_DIRECTIONAL_SPRITE:
                item.texid = self.textures[item_textures].id
            else:
                # move this to an update methods
                angle = int(item.rot)
                item.texid = self.textures[item_textures]["stand"][str(angle)].id

            target.append(item)
        self.handleNewItems()

    def winGame(self):
        if not conf.WIN_MESSAGES:
            self.close()
        else:
            msg = conf.WIN_MESSAGES[0]
            self.showMessage(msg, self.winGame)
            del conf.WIN_MESSAGES[0]

    def showMessage(self, msg, postMessage=None):
        self.message = msg
        w, h = self.size
        self.label = pyglet.text.Label(self.message,
                                       font_name='04b11',
                                       font_size=24, multiline=True,
                                       x=16, y=h - 16, width=w - 32, height=h - 32,
                                       anchor_x='left', anchor_y='top', color=conf.MESSAGE_COLOR_4)
        self.postMessage = postMessage

    def run(self):
        pyglet.app.run()


if __name__ == '__main__':
    win = MainWindow()
    win.run()
