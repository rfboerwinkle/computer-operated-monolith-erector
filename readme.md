# Introduction

Hello! If you're familiar with Chem E Cube and python, you can skip to the "Usage" section.

# Chem E Cube

Chem E Cube is a competition put on by AIChE. We have a competition team at my university. This is software written for custom hardware they have (See "Hardware").

# Python

I'll fill this section out later...

# Hardware

The machine is a modified Creality Ender-3. When I found it, it was in a non-functional state. I believe something was shorting, so I unplugged everything except for the screen, X/Y/Z steppers/limit switches, and case fan (KFAN-1). In place of the part fan (KFAN-2) I have plugged in some custom electronics. The electronics consist of a relay (SONGLE SRS-05VDC-SL) that lets the part fan toggle connectivity of the 2 parts of a mono audio jack. This jack is then plugged into the (PART THING HERE TODO) to emulate the foot pedal. The syringe is then mounted to the head of the printer.

The firmware is unchanged.

# Usage

The python script `ChemE_Slicer.py` generates a gcode file. Use it with `ChemE_Slicer.py [FILE] [OPTION]...` File name defaults to `out.gcode`.

### `-m, --monoliths=COUNT`

  Sets the number of monoliths to print. Must be \[1, 9\] (integer). Defaults to 1.

### `-r, --radius=MILI`

  Sets the radius of each monolith, in milimeters. Must be (0,...\]. Defaults to 10. TODO

### `-a, --angle=ROT`

  Sets the angle offset between layers, in rotations. Must be \[0, 0.25\]. Defaults to 0.125.

### `-s, --line-spacing=MILI`

  Sets the horizontal distance between each line, in milimeters. Must be (0, diameter\]. Defaults to 3. TODO

### `-l, --layers=COUNT`

  Sets the number of layers. Must be greater than 0. The total height (layers * layer-height) must be less than . Must be an integer. Defaults to 40. TODO

### `-h, --layer-height=MILI`

  Sets the height of each layer, in milimeters. Must be greater than . The total height (layers * layer-height) must be less than . Defaults to 0.7. TODO

### `-w, --wait=SEC`

  Sets the wait time between layers, in seconds. Must be \[0, \] (integer?). Defaults to 120. TODO

### `-c, --circle-resolution=COUNT`

  Sets the number of segments in the outside circle. Must be \[3, \] (integer). Defaults to . TODO

### `-M, --move-feedrate=MMPM`

  Sets the feedrate of non-printing moves, in milimeters per minute. Must be \[500, 6000\] (integer). Defaults to 6000. TODO

### `-P, --print-feedrate=MMPM`

  Sets the feedrate of printing moves, in milimeters per minute. Must be \[500, 6000\] (integer). Defaults to 1200. TODO

### `-Z, --z-feedrate=MMPM`

  Sets the feedrate of z-axis moves, in milimeters per minute. Must be \[500, 6000\] (integer). Defaults to 3000. TODO

# Examples

`python ChemE_Slicer.py my_monos.gcode -m=4 --wait=60`
