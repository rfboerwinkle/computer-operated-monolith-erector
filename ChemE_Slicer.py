import sys
import math

out_name = None

settings = {
  "monoliths": 1, # count
  "radius": 10, # milimeters
  "angle": 0.125, # rotations
  "line-spacing": 3, # milimeters
  "layers": 40, # count
  "layer-height": 0.7, # milimeters
  "wait": 120, # seconds
  "circle-resolution": 20, # count
  "move-feedrate": 6000, # milimeters/minute
  "print-feedrate": 1200, # milimeters/minute
  "z-feedrate": 3000, # milimeters/minute
}

settingsTypes = {
  "monoliths": int, # count
  "radius": float, # milimeters
  "angle": float, # rotations
  "line-spacing": float, # milimeters
  "layers": int, # count
  "layer-height": float, # milimeters
  "wait": float, # seconds
  "circle-resolution": int, # count
  "move-feedrate": float, # milimeters/minute
  "print-feedrate": float, # milimeters/minute
  "z-feedrate": float, # milimeters/minute
}

settingsShort = {
  "m": "monoliths",
  "r": "radius",
  "a": "angle",
  "s": "line-spacing",
  "l": "layers",
  "h": "layer-height",
  "w": "wait",
  "c": "circle-resolution",
  "M": "move-feedrate",
  "P": "print-feedrate",
  "Z": "z-feedrate",
}

class command:
  def __init__(self, mode, args):
    # "mode" should be "other", "print", "move", "z"
    self.mode = mode
    self.args = args
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
        string = f"G1 X{self.args[0]:.4f} Y{self.args[1]:.4f}"
      else:
        string = f"G1 X{self.args[0]:.4f} Y{self.args[1]:.4f} F{settings["print-feedrate"]:.4f}"
      currentInfo[0] = self.args[0]
      currentInfo[1] = self.args[1]

    elif self.mode == "move":
      time = (math.hypot(self.args[0]-currentInfo[0], self.args[1]-currentInfo[1]) / settings["move-feedrate"]) * 60
      if currentInfo[3] == "move":
        string = f"G0 X{self.args[0]:.4f} Y{self.args[1]:.4f}"
      else:
        string = f"G0 X{self.args[0]:.4f} Y{self.args[1]:.4f} F{settings["move-feedrate"]:.4f}"
      currentInfo[0] = self.args[0]
      currentInfo[1] = self.args[1]

    elif self.mode == "z":
      time = (self.args / settings["z-feedrate"]) * 60
      if currentInfo[3] == "z":
        string = f"G0 Z{self.args:.4f}"
      else:
        string = f"G0 Z{self.args:.4f} F{settings["z-feedrate"]:.4f}"
      currentInfo[2] = self.args

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
  theta = angle * 2 * math.pi
  x = vec[0] * math.cos(theta) - vec[1]*math.sin(theta)
  y = vec[0] * math.sin(theta) + vec[1]*math.cos(theta)
  vec[0],vec[1] = x,y

def findIntersect(line1, line2):
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
  """ returns (pcode, starting position) """
  global settings
  pcode = [command("other", "M106 S255")] # for "PseudoCODE" of gcode
  perimeter = []
  segmentAngle = 360/settings["circle-resolution"]
  for seg in range(settings["circle-resolution"]):
    theta = (seg+1) / settings["circle-resolution"] * 2 * math.pi
    x = math.cos(theta)*settings["radius"]
    y = math.sin(theta)*settings["radius"]
    perimeter.append((x,y))
    pcode.append(command("print", (x+centerX,y+centerY)))
  pcode.append(command("other", "M106 S0"))

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
  Llines = [] # arbitrary, not necissarily right and left
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
        pcode.append(command("other", "M106 S255"))
        pcode.append(command("print", lp))
        pcode.append(command("other", "M106 S0"))
        toggle = False
      else:
        pcode.append(command("move", lp))
        pcode.append(command("other", "M106 S255"))
        pcode.append(command("print", rp))
        pcode.append(command("other", "M106 S0"))
        toggle = True

  return (pcode, (perimeter[-1][0]+centerX, perimeter[-1][1]+centerY))



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

out.write(f"""; Marlin GCODE for the MS&T Chem E Cube team's Creality Ender-3
M84 E ; Disable extruder
G28 ; Home all axes
G90 ; Absolute positioning""")

time = 0
currentInfo = [0,0,0,"other"]
for layer in range(1, settings["layers"]+1):
  layerPcode,startPoint = generateLayer(settings["radius"]+10, settings["radius"]+10, (settings["angle"]*layer)%0.5)
  startPcode = [
    command("z", settings["layer-height"]*layer),
    command("move", startPoint),
  ]
  startGcode,dt = timeAndCompile(startPcode, currentInfo)
  time += dt
  layerGcode,dt = timeAndCompile(layerPcode, currentInfo)
  time += dt
  out.write(f"\n{startGcode}\n{layerGcode}")

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
