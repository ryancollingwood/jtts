from math import sin, cos, radians, pi, sqrt
from random import random, uniform, choice
from models import *  # @UnusedWildImport
from util import distSq, angle_between, circle_segment
import game_config as conf
import entities


class FinalBossKilled(Exception): pass


class GameObject(object):
    def __init__(self, entity_id, pos, rot):
        x, y = pos
        self.pos = [x, y, rot]
        print(self.pos)
        self.vel = [0.0, 0.0]
        self.alive = True
        self.z = 0.5
        self.size = 0.1
        self.texid = None
        self.radius = 0
        self.entity_id = entity_id
        self.pause = True

    def gl(self):
        x, y, rot = self.pos
        return -x, -y, rot

    def move(self, nx, ny):
        self.pos[0:2] = [nx, ny]

    def __repr__(self):
        return 'x=%f,y=%f,rot=%f' % self.gl()

    def rotate(self, r):

        self.pos[2] += r

        # handle over turns
        if self.pos[2] > 360:
            self.pos[2] = self.pos[2] % 360
        elif self.pos[2] < 0:
            self.pos[2] += 360

    def die(self):
        self.alive = False

    def touched(self, engine):
        pass

    def update(self, dt, player):
        pass

    def randomNearby(self, num, minDist=1.0, maxDist=1.0):
        out = []
        x, y = self.xy
        for _ in range(num):
            angle = random() * 2 * pi
            dist = uniform(minDist, maxDist)

            nx, ny = x + sin(angle) * dist, y + cos(angle) * dist
            out.append((nx, ny))
        return out

    def nearbyCardinal(self):
        x, y = self.xy
        rels = ((-1, 0), (+1, 0), (0, +1), (0, -1))
        return [((x + rel[0], y + rel[1]), rel) for rel in rels]

    def collideMap(self, pos, bad=(1, 2)):
        x, y = pos
        if x < 0 or y < 0:
            return True
        else:
            try:
                if self.map.collideMap[int(x * 8), int(y * 8)] in bad:
                    return True
                else:
                    return False
            except IndexError:
                return True

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def rot(self):
        return self.pos[2]

    @property
    def xy(self):
        return self.pos[0:2]


class Player(GameObject):
    def __init__(self, pos, rot, damage_callback):
        GameObject.__init__(self, entities.PLAYER, pos, rot)
        self.inventory = []
        self.health = conf.PLAYER_HEALTH
        self.damage_callback = damage_callback

    def add(self, item):
        self.inventory.append(item)

    def damage(self, dmg):
        self.health = max(0, self.health - dmg)
        self.damage_callback(self)


class Bullet(GameObject):
    def __init__(self, player, map, speed, texid):
        GameObject.__init__(self, entities.SHOOT, (player.x, player.y), player.rot)
        angle = radians(360 - player.rot)
        self.vel = [-sin(angle) * speed, -cos(angle) * speed]
        self.z = 0.4
        self.map = map
        self.update(0.05, None)
        self.texid = texid
        self.damage = 10

    def update(self, dt, player):

        (vx, vy), pos, map = self.vel, self.pos, self.map
        pos[0] += vx * dt
        pos[1] += vy * dt
        if self.collideMap(pos[0:2], (1,)):
            self.die()


class Item(GameObject):
    def __init__(self, entity_type, pos, type, extra, model=None, map=None):
        GameObject.__init__(self, entity_type, pos, 0)
        self.z = 0.3
        self.size = 0.3
        self.radius = 0.5
        self.type = type
        self.map = map
        if extra:
            self.model = eval(extra)
            self.model.initModel(self)
        else:
            self.model = None
        if model is not None:
            self.model = model
        if self.model is not None:
            ret = self.model.getSize()
            if ret is not None:
                self.z, self.size = ret
            if self.model.radius:
                self.radius = self.model.radius

    def touched(self, engine):
        if self.model:
            self.model.touched(self, engine)

    def findTexture(self):
        if self.model:
            texid = self.model.texture
            if texid is not None:
                return texid
        return 3


MOOD_WANDERING = 0
MOOD_MOVING = 1
MOOD_CHASING = 2
MOOD_CHASEIDLE = 3


class MonsterItem(Item):
    def __init__(self, entity_type, pos, type, model, map):
        Item.__init__(self, entity_type, pos, type, None, model)
        self.health = model.health
        self.submood = self.mood = MOOD_WANDERING
        self.startpos = pos
        self.speed = model.speed
        self.wanderRadiusSquared = 25
        self.map = map
        self.lastRel = (0, 0)
        self.chasePlayerRadiusSquared = 25
        self.minAttackDist = 0.25
        self.giveUpDistanceSquared = 100
        self.targetPoint = None
        self.lasttargetPoint = None

    def damage(self, amt):
        self.health -= amt
        if self.health <= 0:
            self.alive = False
            if self.model.finalBoss:
                raise FinalBossKilled()

    def update(self, dt, player):
        if self.pause:
            return

        self.chasePlayerRadiusSquared = 0
        self.model.update(dt)

        mood = self.mood
        if mood == MOOD_WANDERING:
            pos = self.xy

            points = [(point, rel) for (point, rel) in self.nearbyCardinal() if (
                    distSq(point, self.startpos) < self.wanderRadiusSquared
                    and rel != self.lastRel and not self.collideMap(point, (2,))
            )]
            if points:
                if distSq(pos, player.xy) < self.chasePlayerRadiusSquared:
                    self.pushMood(MOOD_CHASEIDLE)
                    self.pushMood(MOOD_CHASING)
                    self.targetPoint, _ = sorted(points, key=lambda p_r: distSq(p_r[0], player.xy))[0]
                    self.lastRel = (0, 0)
                else:
                    self.pushMood(MOOD_MOVING)
                    self.targetPoint, rel = choice(points)
                    self.lastRel = (-rel[0], -rel[1])
            else:
                self.lastRel = (0, 0)
        elif mood in (MOOD_MOVING, MOOD_CHASING):
            pos = self.pos
            speed = self.speed
            x, y = self.xy
            nx, ny = self.targetPoint
            length = sqrt(distSq(self.xy, self.targetPoint))
            if length < 0.1:  # close enough
                self.popMood()
                return
            dx, dy = (nx - x) / length, (ny - y) / length
            pos[0] += dx * dt * speed
            pos[1] += dy * dt * speed
        elif mood == MOOD_CHASEIDLE:
            pos = self.xy
            if distSq(pos, player.xy) > self.giveUpDistanceSquared:
                self.pushMood(MOOD_WANDERING)
                print('gave up chase')
                self.startpos = pos
            points = sorted([point for (point, rel) in self.nearbyCardinal() if (

                    distSq(point, player.xy) >= self.minAttackDist
                    and not self.collideMap(point, (2,))
            )], key=lambda p: distSq(p, player.xy))
            if points:
                self.targetPoint = points[0]
                self.pushMood(MOOD_CHASING)
                self.lastRel = (0.0)

        if self.targetPoint and self.lasttargetPoint != self.targetPoint:
            change = angle_between(self.pos, self.targetPoint)
            # self.pos[2] = change
            self.rotate(change)
            self.lasttargetPoint = self.targetPoint


    def pushMood(self, newMood):
        self.submood = self.mood
        self.mood = newMood

    def popMood(self):
        self.mood = self.submood
