import numpy
from pyglet.gl import * #@UnusedWildImport
from collections import defaultdict 
ITEM_LETTERS='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Map(object):
  def __init__(self,lines):
    lines,specialLines=tuple([line for line in lines if (line[0:1]==['?'])==value] for value in (False,True))
    self.lines=lines
    self.size=(max(len(x) for x in lines),len(lines))
    self.playerPos=(0,0)
    self.playerRot=0
    self.items=[]
    self.buildCollideMap()
    self.handleSpecialLines(specialLines)
    self.clean=True
  def __getitem__(self,k):
    x,y=k
    try:
      return self.lines[y][x]
    except IndexError:
      return '\0'
  
  def __setitem__(self,k,v):
    x,y=k
    try:
      self.lines[y][x]=v
      self.clean=False
    except IndexError:
      pass
  
  def update(self):
    self.buildCollideMap()
    ret=buildWalls(self)
    self.clean=True
    return ret
    
  
  def neighbours(self,x,y):
    return self[x-1,y],self[x+1,y],self[x,y-1],self[x,y+1]
  
  def buildCollideMap(self):
    w,h,=self.size
    col=self.collideMap=numpy.zeros((w*8,h*8),numpy.int8)
    for y in range(h):
      for x in range(w):
        if self[x,y] in '#%&^':
          col[max(0,x*8-1):x*8+9,max(0,y*8-1):y*8+9].fill(1)
          col[x*8:x*8+8,y*8:y*8+8].fill(2)
        elif self[x,y]=='@':
          self.playerPos=(x+0.5,y+0.5)
          self[x,y]='.'
        elif self[x,y] in ITEM_LETTERS:
          self.items.append([self[x,y],(x+0.5,y+0.5),''])
          self[x,y]='.'
          
  def handleSpecialLines(self,lines):
    for line in (''.join(line[1:]) for line in lines):
      parts=line.split('=',1)
      if len(parts)==2:
        self.handleSpecial(*parts)
      else:
        self.handleSpecial(parts[0],True)
  
  def handleSpecial(self,key,value):
    if key=='dir':
      self.playerRot=float(value)
    if key.startswith('item'):
      num=key[4:]
      for item in self.items:
        if item[0]==num:
          item[2]=value


def loadMap(path):
  with open(path,'r') as f: 
    return Map([list(x.rstrip('\r\n')) for x in f])


class RenderGroup(object):
  def __init__(self,start,length,texture):
    self.start=start
    self.length=length
    self.texture=texture

TEXCOORDS=([0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0])
VERT_SIZE=5 #GL_T2F_V3F
QUAD_SIZE=4*VERT_SIZE 


def buildArrays(*groups):
  quads=sum((verts for (tex,verts) in groups),[])
  size=len(quads)*QUAD_SIZE
  verts=[0.0 for _ in range(size)]
  for qi,quad in enumerate(quads):
    for vi,vert in enumerate(quad):
      off=qi*QUAD_SIZE+vi*VERT_SIZE
      verts[off:off+VERT_SIZE]=TEXCOORDS[vi]+list(vert)
  array=(GLfloat*len(verts))(*verts)
  offset=0
  out=[]
  for tex,group in groups:
    size=len(group)*4
    out.append(RenderGroup(offset,size,tex))
    offset+=size
  return array,out


def buildWalls(map):
  def addVerticalWall(x,y,offset,target):
    target.append((
      (x+0,0.,y+offset+0),
      (x+1,0.,y+offset+0),
      (x+1,1.,y+offset+0),
      (x+0,1.,y+offset+0),
    ))
  def addHorizontalWall(x,y,offset,target):
    target.append((
      (x+offset,0.,y+1),
      (x+offset,0.,y+0),
      (x+offset,1.,y+0),
      (x+offset,1.,y+1),
    ))
  groups=defaultdict(list)
  w,h=map.size
  for y in range(h):
    for x in range(w):
      me=map[x,y]
      if me not in '#%^&':
        continue
      left,right,up,down=map.neighbours(x,y)
      if me!=down:
        addVerticalWall(x,y,+1,groups[me+'|'])
      if me!=up:
        addVerticalWall(x,y,+0,groups[me+'|'])
      if me!=left:
        addHorizontalWall(x,y,0,groups[me+'-'])
      if me!=right:
        addHorizontalWall(x,y,1,groups[me+'-'])
  return buildArrays(*groups.items())
  
if __name__=='__main__':
  print loadMap('maps/level01.txt')