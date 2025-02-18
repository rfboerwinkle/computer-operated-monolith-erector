#!/usr/bin/env python3

# Blobulator

# Yes, I put less effort into this script, it was way simpler.

import sys
import math

out_name = None

settings = {
  "blobs": 16, # count
  "blob-spacing": 10, # millimeters
  "blob-time": 2000, # milliseconds
  "blob-height": 2, # millimeters
  "move-height": 6, # millimeters
  "move-feedrate": 3000, # millimeters/minute
  "z-feedrate": 3000, # millimeters/minute
  "x-min": 40, # millimeters
  "x-max": 220, # millimeters
  "y-min": 40, # millimeters
  "y-max": 220, # millimeters
}

settingsTypes = {
  "blobs": int, # count
  "blob-spacing": float, # millimeters
  "blob-time": int, # milliseconds
  "blob-height": float, # millimeters
  "move-height": float, # millimeters
  "move-feedrate": float, # millimeters/minute
  "z-feedrate": float, # millimeters/minute
  "x-min": float, # millimeters
  "x-max": float, # millimeters
  "y-min": float, # millimeters
  "y-max": float, # millimeters
}

# "h" and "H" were chosen because they roughly correspond to the min and max
# height.
settingsShort = {
  "b": "blobs",
  "s": "blob-spacing",
  "t": "blob-time",
  "h": "blob-height",
  "H": "move-height",
  "m": "move-feedrate",
  "z": "z-feedrate",
  "x": "x-min",
  "X": "x-max",
  "y": "y-min",
  "Y": "y-max",
}

# format num
def fNum(num):
  s = f"{num:.4f}".strip("0")
  if s[-1] == ".":
    s = s[:-1]
  if s == "":
    s = "0"
  return s

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
G90 ; Absolute positioning
""")

# The ' - 1' is because there is a half spacing on either side.
xAmount = int((settings["x-max"] - settings["x-min"]) // settings["blob-spacing"]) - 1
yAmount = int((settings["y-max"] - settings["y-min"]) // settings["blob-spacing"]) - 1
if xAmount * yAmount < settings["blobs"]:
  print("Not enough space for the set amount of blobs!")
  quit()

# time in seconds
time = 0
# position in millimeters
curPosition = [0,0,0]
nextPosition = [0,0,0]
count = 0
for y in range(yAmount):
  for x in range(xAmount):
    # count
    count += 1
    if count > settings["blobs"]:
      break

    # move up
    nextPosition[2] = settings["move-height"]
    out.write(f"G0 Z{fNum(nextPosition[2])} F{settings["z-feedrate"]}\n")
    time += (abs(nextPosition[2]-curPosition[2]) / settings["z-feedrate"]) * 60

    # move over
    nextPosition[0] = (x + 0.5) * settings["blob-spacing"]
    nextPosition[1] = (y + 0.5) * settings["blob-spacing"]
    out.write(f"G0 X{fNum(nextPosition[0])} Y{fNum(nextPosition[1])} F{settings["move-feedrate"]}\n")
    time += (math.hypot(nextPosition[0]-curPosition[0], nextPosition[1]-curPosition[1]) / settings["move-feedrate"]) * 60

    # move down
    nextPosition[2] = settings["blob-height"]
    out.write(f"G0 Z{fNum(nextPosition[2])} F{settings["z-feedrate"]}\n")
    time += (abs(nextPosition[2]-curPosition[2]) / settings["z-feedrate"]) * 60

    # print on
    out.write("M106 S255\n")

    # wait
    # No fNum because it's an integer
    out.write(f"G4 P{settings["blob-time"]}\n")
    time += settings["blob-time"]/1000

    # print off
    out.write("M106 S0\n")

    curPosition = nextPosition.copy()

# move up
nextPosition[2] = settings["move-height"]
out.write(f"G0 Z{fNum(nextPosition[2])} F{settings["z-feedrate"]}\n")
time += (abs(nextPosition[2]-curPosition[2]) / settings["z-feedrate"]) * 60

nextPosition[0] = 0
nextPosition[1] = 0
out.write(f"G0 X{fNum(nextPosition[0])} Y{fNum(nextPosition[1])} F{settings["move-feedrate"]}\n")
time += (math.hypot(nextPosition[0]-curPosition[0], nextPosition[1]-curPosition[1]) / settings["move-feedrate"]) * 60

out.write(f"; total time (seconds): {int(time)}\n")

out.close()

print(f"Written to: {out_name}")
print(f"Total time (seconds): {time}")
