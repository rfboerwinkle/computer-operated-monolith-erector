#!/usr/bin/env python3

# Computer Operated Monolith Erection system

import sys
import math

out_name = None

# NOTE: There are three main non-printing move commands: Z-move commands, moves
# internal to monoliths, and moving between monoliths. Because internal moves
# are so small and it takes time to pressurize / depressurize, the pressure is
# not turned off for internal moves. If you want it turned off for these moves,
# uncomment the things labeled "uncomment for internal depressurization:"

settings = {
  "monoliths": 16, # count
  "monolith-spacing": 25, # millimeters
  "radius": 8, # millimeters
  "angle": 0.125, # revolutions
  "line-spacing": 3, # millimeters
  "layers": 40, # count
  "layer-height": 0.5, # millimeters
  "wait": 500, # seconds
  "tangent": 16, # millimeters
  "circle-resolution": 40, # count
  "move-feedrate": 3000, # millimeters/minute
  "print-feedrate": 200, # millimeters/minute
  "z-feedrate": 3000, # millimeters/minute
  "x-min": 40, # millimeters
  "x-max": 220, # millimeters
  "y-min": 40, # millimeters
  "y-max": 220, # millimeters
}

settingsTypes = {
  "monoliths": int, # count
  "monolith-spacing": float, # millimeters
  "radius": float, # millimeters
  "angle": float, # revolutions
  "line-spacing": float, # millimeters
  "layers": int, # count
  "layer-height": float, # millimeters
  "wait": float, # seconds
  "tangent": float, # millimeters
  "circle-resolution": int, # count
  "move-feedrate": float, # millimeters/minute
  "print-feedrate": float, # millimeters/minute
  "z-feedrate": float, # millimeters/minute
  "x-min": float, # millimeters
  "x-max": float, # millimeters
  "y-min": float, # millimeters
  "y-max": float, # millimeters
}

settingsShort = {
  "m": "monoliths",
  "S": "monolith-spacing",
  "r": "radius",
  "a": "angle",
  "s": "line-spacing",
  "l": "layers",
  "h": "layer-height",
  "w": "wait",
  "t": "tangent",
  "c": "circle-resolution",
  "f": "move-feedrate",
  "p": "print-feedrate",
  "z": "z-feedrate",
  "x": "x-min",
  "X": "x-max",
  "y": "y-min",
  "Y": "y-max",
}

class command:
  def __init__(self, mode, args):
    """ "mode" should be "other", "print", "move", "z", "wait" """
    self.mode = mode
    self.args = args
  def fNum(num):
    s = f"{num:.4f}".strip("0")
    if s[-1] == ".":
      s = s[:-1]
    if s == "":
      s = "0"
    return s
  def timeAndCompile(self, currentInfo):
    # currentInfo is a list which is modified:
    # [x,y,z,mode]
    # returns gcode string, time
    global settings
    if self.mode == "other":
      string = self.args
      time = 0

    elif self.mode == "print":
      time = (math.hypot(self.args[0]-currentInfo[0], self.args[1]-currentInfo[1]) / settings["print-feedrate"]) * 60
      if currentInfo[3] == "print":
        string = f"G1 X{command.fNum(self.args[0])} Y{command.fNum(self.args[1])}"
      else:
        string = f"G1 X{command.fNum(self.args[0])} Y{command.fNum(self.args[1])} F{command.fNum(settings["print-feedrate"])}"
      currentInfo[0] = self.args[0]
      currentInfo[1] = self.args[1]

    elif self.mode == "move":
      time = (math.hypot(self.args[0]-currentInfo[0], self.args[1]-currentInfo[1]) / settings["move-feedrate"]) * 60
      if currentInfo[3] == "move":
        string = f"G0 X{command.fNum(self.args[0])} Y{command.fNum(self.args[1])}"
      else:
        string = f"G0 X{command.fNum(self.args[0])} Y{command.fNum(self.args[1])} F{command.fNum(settings["move-feedrate"])}"
      currentInfo[0] = self.args[0]
      currentInfo[1] = self.args[1]

    elif self.mode == "z":
      time = (self.args / settings["z-feedrate"]) * 60
      if currentInfo[3] == "z":
        string = f"G0 Z{command.fNum(self.args)}"
      else:
        string = f"G0 Z{command.fNum(self.args)} F{command.fNum(settings["z-feedrate"])}"
      currentInfo[2] = self.args

    elif self.mode == "wait":
      string = f"G4 P{int(self.args)}"
      time = int(self.args)/1000

    currentInfo[3] = self.mode
    return string,time

def timeAndCompile(pcode, startInfo):
  # currentInfo is a list which is modified:
  # [x,y,z,mode]
  # returns gcode string, time
  time = 0
  gcodeSegs = []
  for line in pcode:
    dg,dt = line.timeAndCompile(startInfo)
    time += dt
    gcodeSegs.append(dg)
  return "\n".join(gcodeSegs), time

def rotate(vec, angle):
  """ returns vector `vec` rotated by `angle` revolutions """
  theta = angle * 2 * math.pi
  x = vec[0] * math.cos(theta) - vec[1]*math.sin(theta)
  y = vec[0] * math.sin(theta) + vec[1]*math.cos(theta)
  vec[0],vec[1] = x,y

def findIntersect(line1, line2):
  """ returns the intersection between the 2 lines.
  if no intersection, return None. """
  x1,y1 = line1[0]
  x2,y2 = line1[1]
  x3,y3 = line2[0]
  x4,y4 = line2[1]
  denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
  if denom == 0: # parallel
    return None
  ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
  if ua < 0 or ua > 1: # out of range
    return None
  ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
  if ub < 0 or ub > 1: # out of range
    return None
  x = x1 + ua * (x2-x1)
  y = y1 + ua * (y2-y1)
  return (x,y)

def generateLayer(centerX, centerY, totalAngle):
  """ returns pcode """
  global settings

  # generate perimeter
  pcode = [] # for "PseudoCODE" of gcode
  if settings["tangent"] != 0:
    startPoint = (
      centerX + settings["radius"],
      centerY - settings["tangent"],
    )
    if not(settings["y-min"] <= startPoint[1] <= settings["y-max"]):
      print("Tangent goes off the edge!")
      quit()
    pcode.append(command("move", startPoint))
    pcode.append(command("other", "M106 S255"))
    pcode.append(command("print", (centerX+settings["radius"], centerY)))
  else:
    pcode.append(command("other", "M106 S255"))
  perimeter = []
  segmentAngle = 360/settings["circle-resolution"]
  for seg in range(settings["circle-resolution"]):
    theta = (seg+1) / settings["circle-resolution"] * 2 * math.pi
    x = math.cos(theta)*settings["radius"]
    y = math.sin(theta)*settings["radius"]
    perimeter.append((x,y))
    pcode.append(command("print", (x+centerX,y+centerY)))
  # uncomment for internal depressurization:
  #pcode.append(command("other", "M106 S0"))

  # generate hatching
  lines = []
  numLines = int((settings["radius"]*2)//settings["line-spacing"])
  if numLines % 2 == 1:
    lines.append([0,0])
    numLines - 1
    startY = settings["line-spacing"]
  else:
    startY = settings["line-spacing"]/2
  for i in range(numLines//2):
    lines.append([0,startY+(settings["line-spacing"] * i)])
    lines.append([0,-1 * (startY+(settings["line-spacing"] * i))])
  lines.sort(reverse=True)
  # Reverse might make it a little faster? Unsure...
  Llines = [] # arbitrary, not necessarily right and left
  Rlines = []
  for line in lines:
    rotate(line, totalAngle)
    Llines.append([
      [
        line[0],
        line[1],
      ],[
        line[0] + math.cos(totalAngle*2*math.pi)*(settings["radius"]+1),
        line[1] + math.sin(totalAngle*2*math.pi)*(settings["radius"]+1),
      ],
    ])
    Rlines.append([
      [
        line[0],
        line[1],
      ],[
        line[0] - math.cos(totalAngle*2*math.pi)*(settings["radius"]+1),
        line[1] - math.sin(totalAngle*2*math.pi)*(settings["radius"]+1),
      ],
    ])

  # trim hatching to inside circle
  toggle = True
  for i in range(len(lines)):
    lp = None
    for perI in range(len(perimeter)):
      lp = findIntersect(Llines[i], (perimeter[perI], perimeter[perI-1]))
      if lp != None:
        break
    rp = None
    for perI in range(len(perimeter)):
      rp = findIntersect(Rlines[i], (perimeter[perI], perimeter[perI-1]))
      if rp != None:
        break
    if lp != None and rp != None:
      lp = (lp[0]+centerX, lp[1]+centerY)
      rp = (rp[0]+centerX, rp[1]+centerY)
      if toggle:
        pcode.append(command("move", rp))
        # uncomment for internal depressurization:
        #pcode.append(command("other", "M106 S255"))
        pcode.append(command("print", lp))
        # uncomment for internal depressurization:
        #pcode.append(command("other", "M106 S0"))
        toggle = False
      else:
        pcode.append(command("move", lp))
        # uncomment for internal depressurization:
        #pcode.append(command("other", "M106 S255"))
        pcode.append(command("print", rp))
        # uncomment for internal depressurization:
        #pcode.append(command("other", "M106 S0"))
        toggle = True

  pcode.append(command("other", "M106 S0"))
  return pcode

# take command-line arguments
for arg in sys.argv[1:]:
  if len(arg) == 0:
    continue
  if arg[0] == "-":
    if arg.count("=") != 1:
      print(f"There should be 1 '=' per option! ({arg.count('=')} found in '{arg}')")
      quit()
    if len(arg) == 1:
      print(f"No option name given: '-'!")
      quit()
    if arg[1] == "-":
      arg = arg[2:]
      name,value = arg.split("=")
    else:
      arg = arg[1:]
      name,value = arg.split("=")
      if len(name) != 1:
        print(f"Short option names must have length 1! (found '-{name}={value}')")
        quit()
      if name not in settingsShort:
        print(f"Unknown short option: '{name}'!")
        quit()
      name = settingsShort[name]
    if name not in settingsTypes:
      print(f"Unknown option: '{name}'!")
      quit()
    try:
      convertedValue = settingsTypes[name](value)
    except:
      print(f"Option '{name}' only takes arguments of type '{settingsTypes[name]}', but conversion of '{value}' failed!")
      quit()
    settings[name] = convertedValue

  else:
    if out_name == None:
      out_name = arg
    else:
      print(f"Only one file name please! (found '{out_name}' and '{arg}')")
      quit()

if out_name is None:
  out_name = "out.gcode"

try:
  out = open(out_name, "w")
except:
  print(f"File {out_name} could not be opened!")
  quit()

settingPrint = "\n".join(f"; --{setting}={settings[setting]}" for setting in sorted(settings.keys()))

out.write(f"""; Marlin GCODE for the MS&T Chem E Cube team's Creality Ender-3
{settingPrint}
M84 E ; Disable extruder
G28 ; Home all axes
G90 ; Absolute positioning""")

xAmount = int((settings["x-max"] - settings["x-min"]) // (settings["radius"]*2 + settings["monolith-spacing"]))
yAmount = int((settings["y-max"] - settings["y-min"]) // (settings["radius"]*2 + settings["monolith-spacing"]))
if xAmount * yAmount < settings["monoliths"]:
  print("Not enough space for the set amount of monoliths!")
  quit()

time = 0
currentInfo = [0,0,0,"other"]
for layer in range(1, settings["layers"]+1):
  startPcode = [command("z", settings["layer-height"]*layer),]
  startGcode,dt = timeAndCompile(startPcode, currentInfo)
  layerTime = dt

  angle = (settings["angle"]*layer)%0.5
  mono = settings["monoliths"]
  layerPcode = []
  for i in range((mono//yAmount) + 1):
    y = settings["y-min"] + (settings["monolith-spacing"]+(settings["radius"]*2))*(i+0.5)
    xAmt = min(mono, yAmount)
    mono -= yAmount
    for j in range(xAmt):
      x = settings["x-min"] + (settings["monolith-spacing"]+(settings["radius"]*2))*(j+0.5)
      layerPcode += generateLayer(x, y, angle)

  layerGcode,dt = timeAndCompile(layerPcode, currentInfo)
  layerTime += dt

  time += layerTime
  waitTime = settings["wait"] - layerTime
  if waitTime > 0:
    endGcode,dt = command("wait", waitTime*1000).timeAndCompile(currentInfo)
    time += dt
    endGcode = "\n" + endGcode
  else:
    endGcode = ""
    print(f"Warning: The time to print a layer ({command.fNum(layerTime)} s) is longer than the dry wait time ({command.fNum(settings["wait"])} s).")
    print("Non-critical, continuing")
  out.write(f"\n{startGcode}\n{layerGcode}{endGcode}")

endPcode = [
  command("z", (settings["layers"]+1) * settings["layer-height"]),
  command("move", (0,0)),
  command("other", f"; total time (seconds): {int(time)}"),
]

endGcode,_ = timeAndCompile(endPcode, currentInfo)
out.write("\n" + endGcode)
out.write("\n")
out.close()

print(f"Written to: {out_name}")
print(f"Total time (seconds): {time}")
