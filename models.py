from util import SpacingTrigger
from math import sqrt

class Model(object):
  def __init__(self):
    self.texture=None
    self.radius=None
  
  def initModel(self,item):
    self.item=item
    pass
  
  def touched(self,object,engine):
    pass
  
  def getSize(self):
    return None

  def changeMap(self,char):
    item=self.item
    x,y=item.xy
    item.map[int(x),int(y)]=char

class Scroll(Model):
  def __init__(self,message):
    Model.__init__(self)
    self.texture=4
    self.message=message
  
  def touched(self,object,engine):
    object.die()
    engine.showMessage(self.message)

class Key(Model):
  def __init__(self,color):
    Model.__init__(self)
    self.texture=5
    self.color=color
  
  def touched(self,object,engine):
    engine.player.add(object)
    object.die()

class Door(Model):
  def __init__(self,color):
    Model.__init__(self)
    self.texture=None
    self.color=color
    self.radius=1.5
  
  def touched(self,object,engine):
    for item in engine.player.inventory:
      if isinstance(item.model,Key):
        if item.model.color==self.color:
          object.die()
          self.changeMap('.')
          engine.mapChanged()
          engine.player.inventory.remove(item)
          return

  def initModel(self,item):
    Model.initModel(self, item)
    self.changeMap('%')
    

class MonsterModel(Model):
  def __init__(self,health=20,wanderRadius=5,texture=6,speed=1.0,damage=15,radius=1.0,finalBoss=False):
    Model.__init__(self)
    self.texture=texture
    self.health=health
    self.canHurt=SpacingTrigger(0.25)
    self.damage=damage
    self.radius=radius
    self.wanderRadius=wanderRadius
    self.speed=speed
    self.finalBoss=finalBoss
    
  def initModel(self,item):
    Model.initModel(self, item)
    
    item.wanderRadiusSquared=self.wanderRadius**2
  
  def getSize(self):
    return 0.5,0.5
  
  def touched(self,object,engine):
    if self.canHurt.attempt():
      engine.player.damage(self.damage)
  
  def update(self,dt):
    self.canHurt.update(dt)

class Stairs(Model):
  def __init__(self,message):
    Model.__init__(self)
    self.texture=None
    self.radius=sqrt(1)
    self.message=message

  def initModel(self,item):
    Model.initModel(self, item)
    self.changeMap('^')
  
  def touched(self,object,engine):
    engine.nextMap(self.message)
  