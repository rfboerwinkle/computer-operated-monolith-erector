#!/usr/bin/env python3

import sys

if len(sys.argv) < 2:
  print("Please provide a filename!")
  quit()

import pygame
from pygame import gfxdraw
pygame.init()
screenx = 880
screeny = 880
screen = pygame.display.set_mode((screenx, screeny),16)
while not pygame.display.get_active():
  time.sleep(0.1)
pygame.display.set_caption("gcode viewer")
clock = pygame.time.Clock()

print("\nBe aware, the size of the screen and placement of monoliths is offset from the real size / placement.\nProvide \"auto\" after the filename to auto-step!\n")

gcode = open(sys.argv[1], "r").read().split("\n")
if "auto" in sys.argv[2:]:
  increment = 30
else:
  increment = 0
gcodeIndex = 0

def n():
  global gcodeIndex, gcode, update
  gcodeIndex += 1
  if gcodeIndex >= len(gcode):
    gcodeIndex = len(gcode)-1
    print("End")
  else:
    update = True
    print(gcode[gcodeIndex])
def p():
  global gcodeIndex, gcode, update
  gcodeIndex -= 1
  if gcodeIndex < 0:
    gcodeIndex = 0
    print("Start")
  else:
    update = True
    print(gcode[gcodeIndex])

count = 0
while True:
  clock.tick(60)
  update = False
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      quit()
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RIGHT:
        n()
      elif event.key == pygame.K_LEFT:
        p()

  count += increment
  if count >= 100:
    count %= 100
    n()

  colors = {}

  def feedToColor(f):
    c = pygame.color.Color(0)
    c.hsva = ((0.75-(f/8000))*360, 100, 100, 100)
    return c

  if update:
    update = False
    screen.fill((0,0,0))
    x,y,z,f = 0,0,0,0
    for i in range(120):
      c = feedToColor(i*50)
      pygame.gfxdraw.pixel(screen, i, 1, c)

    pygame.gfxdraw.circle(screen, 500,500,10,(255,255,255))

    for lineI in range(gcodeIndex+1):
      line = gcode[lineI].split(";")[0].split(" ")
      if 3 <= len(line):
        if line[0] == "G0" or line[0] == "G1":
          trans = False
          for coord in line[1:]:
            if not coord:
              continue
            if coord[0] == "X":
              x = float(coord[1:])
              trans = True
            elif coord[0] == "Y":
              y = float(coord[1:])
              trans = True
            elif coord[0] == "Z":
              z = float(coord[1:])
              trans = True
            elif coord[0] == "F":
              f = float(coord[1:])
          if not trans:
            continue
          c = feedToColor(f)
          circleThings = (int(x*4), int(y*4), int(z*4), c)
          if lineI == gcodeIndex:
            print("     ",x,y,z,f)
            pygame.gfxdraw.circle(screen, 500,500,10,(0,0,0))
          pygame.gfxdraw.circle(screen, *circleThings)
  pygame.display.flip()
