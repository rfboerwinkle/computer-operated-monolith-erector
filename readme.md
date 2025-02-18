# Chem E Cube

Chem E Cube is a competition put on by AIChE. We have a competition team at my university. This is software written for custom hardware they have.

# Hardware

The machine is a modified Creality Ender-3. When I found it, it was in a non-functional state. I believe something was shorting, so I unplugged everything except for the screen and X/Y/Z steppers/limit switches. In place of the part fan (KFAN-2) I have plugged in some custom electronics. The fan wires were soldered to the coil pins of a relay (Ningbo Songle Relay SRD-24VDC-SL-C). The normally open and common contact pins were soldered to the two parts of a mono audio jack (the jack was actually stereo, but the 2 segments furthest from the tip were joined at the end of the wire). This jack is then plugged into the pressure regulator (LOCTITE digital syringe dispenser 98666) in place of the foot pedal. The dispenser has to be in manual mode. The syringe is mounted to the head of the printer with a custom printed part (`syringe-holder.stl`). The firmware is unchanged. There are pictures of the setup in `pictures/`.

# Additional Notes

The python script `gcode-viewer.py` is for looking at gcode. Left and right arrow keys step through the file. Color shows speed, radius shows height. The white circle only shows up for non-movement commands. Fair warning: it's not very user friendly or well written. The image `pictures/very-technical-drawing.png` shows the measurements used in `syringe-holder.scad` (more information on this file format here [https://openscad.org/](https://openscad.org/)). The syringe was a little wobbly, so the paper and rubber bands in the pictures are to shim and clamp it.

# Blob Creation

The python script `blob-slicer.py` generates a gcode file. Use it with `blob-slicer.py [FILE] [OPTION]...` File name defaults to `out.gcode`.

# Monolith Creation

The python script `monolith-slicer.py` generates a gcode file. Use it with `monolith-slicer.py [FILE] [OPTION]...` File name defaults to `out.gcode`. Keep in mind that none of the ranges are enforced, they are mostly recommendations. I'm not sure what the safe range of feedrates is, 6000 is the highest I've seen. The software should mostly keep itself from making any illegal moves, but if you make drastic changes or are otherwise worried about it you might want to look at it with `gcode-viewer.py`.

### `-m, --monoliths=COUNT`

Sets the number of monoliths to print. Must be \[1, +∞) (integer). Defaults to 16.

### `-S, --monolith-spacing=MILLI`

Sets the distance between monoliths, in millimeters. Must be \[0, +∞). Defaults to 20.

### `-r, --radius=MILLI`

Sets the radius of each monolith, in millimeters. The circles are regular polygons. This is the circumscribed, not inscribed radius. This radius does not account for width of the lines drawn. Must be (0, +∞). Defaults to 8.

### `-a, --angle=REV`

Sets the angle offset between layers, in revolutions. Must be \[0, 0.25\]. Defaults to 0.125.

### `-s, --line-spacing=MILLI`

Sets the horizontal distance between each line, in millimeters. Must be (0, radius*2). Defaults to 3.

### `-l, --layers=COUNT`

Sets the number of layers. Must be greater than 0. The total height (layers * layer-height) must be less than 250mm. Must be an integer. Defaults to 40.

### `-h, --layer-height=MILLI`

Sets the height of each layer, in millimeters. Must be greater than 0.04. The total height (layers * layer-height) must be less than 250mm. Defaults to 0.5.

### `-w, --wait=SEC`

Sets the wait time between layers, in seconds. Must be \[0, +∞) (integer). Defaults to 500.

### `-t, --tangent=MILLI`

Sets the length of the tangent line, in millimeters. Must be \[0, +∞). You should ensure that this lines does not intersect with other monoliths. Defaults to 16.

### `-c, --circle-resolution=COUNT`

Sets the number of segments in the outside circle. Must be \[3, +∞) (integer). Defaults to 40.

### `-M, --move-feedrate=MMPM`

Sets the feedrate of non-printing moves, in millimeters per minute. Defaults to 3000.

### `-P, --print-feedrate=MMPM`

Sets the feedrate of printing moves, in millimeters per minute. Defaults to 200.

### `-Z, --z-feedrate=MMPM`

Sets the feedrate of z-axis moves, in millimeters per minute. Defaults to 3000.

## Questionable Zone

You probably shouldn't have to touch any of the commands below here. They are typically reserved for hardware specific settings. i.e. If you adjust the location of the print head, you would have to change the min/max coordinates.

### `-x, --x-min=MILLI`

Sets the minimum printable x coordinate, in millimeters. No restrictions in place, be careful. Defaults to 40.

### `-X, --x-max=MILLI`

Sets the maximum printable x coordinate, in millimeters. No restrictions in place, be careful. Defaults to 220.

### `-y, --y-min=MILLI`

Sets the minimum printable y coordinate, in millimeters. No restrictions in place, be careful. Defaults to 40.

### `-Y, --y-max=MILLI`

Sets the maximum printable y coordinate, in millimeters. No restrictions in place, be careful. Defaults to 220.

# Examples

The default values are probably what you want. The default gcode file has been generated, and the output is `Monos-V2.gcode` (moved to `examples/Monos-V2.gcode`).

`python3 monlith-slicer.py Monos-V2.gcode`

The following 2 commands are identical, they print 4 monoliths with 10mm of spacing between them. They are outputted to a file named `my-monos.gcode`.

`python3 monlith-slicer.py my-monos.gcode --monoliths=4 -S=20`

`python3 monlith-slicer.py my-monos.gcode -m=4 --monolith-spacing=20`
