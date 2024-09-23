# Introduction

Hello! If you're familiar with Chem E Cube and python, you can skip to the "Usage" section.

# Chem E Cube

Chem E Cube is a competition put on by AIChE. We have a competition team at my university. This is software written for custom hardware they have (See "Hardware").

# Python

I'll fill this section out later...

# Hardware

The machine is a modified Creality Ender-3. When I found it, it was in a non-functional state. I believe something was shorting, so I unplugged everything except for the screen, X/Y/Z steppers/limit switches, and case fan (KFAN-1). In place of the part fan (KFAN-2) I have plugged in some custom electronics.

The firmware is unchanged.

# Usage

The python script `ChemE_Slicer.py` generates a gcode file. Use it with `ChemE_Slicer.py [FILE] [OPTION]...` File name defaults to `out.gcode`.

### `-m, --monoliths=COUNT`

  Sets the number of monoliths to print. Must be \[1, 9\] (integer). Defaults to 1.

### `-d, --diameter=MILI`

  Sets the diamter of each monolith, in milimeters. Must be (0,...\]. Defaults to 20. TODO

### `-a, --angle=DEGR`

  Sets the angle offset between layers, in degrees. Must be \[0, 90\]. Defaults to 45.

### `-l, --layers=COUNT`

  Sets the number of layers. Must be greater than 0. The total height (layers * layer-height) must be less than . Must be an integer. Defaults to 40. TODO

### `-h, --layer-height=MILI`

  Sets the height of each layer, in milimeters. Must be greater than . The total height (layers * layer-height) must be less than . Defaults to 0.7. TODO

### `-w, --wait=SEC`

  Sets the wait time between layers, in seconds. Must be \[0, \] (integer?). Defaults to 120. TODO

### `-s, --spacing=MILI`

  Sets the horizontal distance between each line, in milimeters. Must be (0, diameter\]. Defaults to . TODO

### `-r, --circle-resolution=COUNT`

  Sets the number of segments in the outside circle. Must be \[3, \] (integer). Defaults to . TODO

# Examples

`python ChemE_Slicer.py my_monos.gcode -m=4 --wait=60`
