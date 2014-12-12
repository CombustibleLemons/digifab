import re

active_color = -1
color_lengths = []
coordinates = 'absolute'
extruder = 'absolute'
units = 'mm'
extruded = 0
last_extruded = 0
last_negative = []
prev_extruded = 0
inc = 0

with open('color.amf.gcode', 'r') as f:
	for line in f:
		inc += 1
		words = line.split()
		if len(words) > 0:
			cmd = words[0]
		else:
			cmd = 'foobar'
		if cmd == 'G1':
			m = re.search('E(-?\d+\.?\d*)\D', line)
			if m:
				if extruder == 'absolute':
					increment = float(m.group(1)) - prev_extruded
					prev_extruded = float(m.group(1))
				elif extruder == 'relative':
					increment = float(m.group(1))

				if increment < 0:
					last_negative[active_color] += increment
				elif increment > 0:
					if round(increment, 5) != round((-1 * last_negative[active_color]), 5):
						extruded += increment
					else:
						last_negative[active_color] = 0
		elif cmd == 'G92':
			m = re.search('E(-?\d+\.?\d*)\D', line)
			if m:
				last_extruded += extruded
				extruded = 0
				prev_extruded = float(m.group(1))
		elif cmd[0] == 'T':
			if active_color != -1:
				color_lengths.append([active_color, last_extruded+extruded])
			active_color = int(cmd[1:])
			if len(last_negative) < (active_color + 1):
				last_negative.append(0)
			extruded = 0
			last_extruded = 0
			prev_extruded = 0
		elif cmd == 'G20':
			units = 'in'
		elif cmd == 'G21':
			units = 'mm'
		elif cmd == 'G90':
			coordinates = 'absolute'
		elif cmd ==	'G91':
			coordinates = 'relative'
		elif cmd == 'M82':
			extruder = 'absolute'
		elif cmd == 'M83':
			extruder = 'relative'
	color_lengths.append([active_color, last_extruded+extruded])

inc = 0
for lneg in last_negative:
	last_negative[inc] += 1
	inc += 1
last_negative[active_color] = 0.0
for color_length in reversed(color_lengths):
	color_length[1] += last_negative[color_length[0]]
	last_negative[color_length[0]] = 0

print color_lengths
color0 = color1 = 0
for length in color_lengths:
	if length[0] == 0:
		color0 += float("{0:.5f}".format(length[1]))
	elif length[0] == 1:
		color1 += float("{0:.5f}".format(length[1]))
print (0, color0)
print (1, color1)

def calc_lengths(filename):
    active_color = -1
    color_lengths = []
    coordinates = 'absolute'
    extruder = 'absolute'
    units = 'mm'
    extruded = 0
    last_extruded = 0
    last_negative = []
    prev_extruded = 0
    inc = 0

    with open(filename, 'r') as f:
        for line in f:
            inc += 1
            words = line.split()
            if len(words) > 0:
                cmd = words[0]
            else:
                cmd = 'foobar'
            if cmd == 'G1':
                m = re.search('E(-?\d+\.?\d*)\D', line)
                if m:
                    if extruder == 'absolute':
                        increment = float(m.group(1)) - prev_extruded
                        prev_extruded = float(m.group(1))
                    elif extruder == 'relative':
                        increment = float(m.group(1))

                    if increment < 0:
                        last_negative[active_color] += increment
                    elif increment > 0:
                        if round(increment, 5) != round((-1 * last_negative[active_color]), 5):
                            extruded += increment
                        else:
                            last_negative[active_color] = 0
            elif cmd == 'G92':
                m = re.search('E(-?\d+\.?\d*)\D', line)
                if m:
                    last_extruded += extruded
                    extruded = 0
                    prev_extruded = float(m.group(1))
            elif cmd[0] == 'T':
                if active_color != -1:
                    color_lengths.append([active_color, last_extruded+extruded])
                active_color = int(cmd[1:])
                if len(last_negative) < (active_color + 1):
                    last_negative.append(0)
                extruded = 0
                last_extruded = 0
                prev_extruded = 0
            elif cmd == 'G20':
                units = 'in'
            elif cmd == 'G21':
                units = 'mm'
            elif cmd == 'G90':
                coordinates = 'absolute'
            elif cmd ==	'G91':
                coordinates = 'relative'
            elif cmd == 'M82':
                extruder = 'absolute'
            elif cmd == 'M83':
                extruder = 'relative'
        color_lengths.append([active_color, last_extruded+extruded])

    inc = 0
    for lneg in last_negative:
        last_negative[inc] += 1
        inc += 1
    last_negative[active_color] = 0.0
    for color_length in reversed(color_lengths):
        color_length[1] += last_negative[color_length[0]]
        last_negative[color_length[0]] = 0

    print color_lengths
    color0 = color1 = 0
    for length in color_lengths:
        if length[0] == 0:
            color0 += float("{0:.5f}".format(length[1]))
        elif length[0] == 1:
            color1 += float("{0:.5f}".format(length[1]))
    print (0, color0)
    print (1, color1)
    return color_lengths
