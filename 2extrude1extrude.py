import re

with open('Traffic_Cone_Two_Color_Single_Extruder.gcode', 'w') as dst:
	with open('Traffic_Cone_Dual_Extrusion/Traffic_Cone_Rings.amf.gcode', 'r') as src:
		t_appearances = {}
		for line in src:
			words = line.split()
			if len(words) > 0:
				cmd = words[0]
			else:
				cmd = 'foobar'

			if cmd[0] == 'T':
				dst.write('; This is the beginning of a color change\n')
				dst.write('G92 E0\n')
				if cmd[1] not in t_appearances:
					t_appearances[cmd[1]] = 0
				t_appearances[cmd[1]] += 1
				if t_appearances[cmd[1]] > 1:
					if cmd[1] == '0':
						dst.write('G1 E1.00000\n')
					else:
						dst.write('G1 E-1.00000\n')
				dst.write('; This is the end of a color change\n')
			elif (cmd == 'M104' or cmd == 'M109'):
				m = re.search('T0', line)
				if m:
					if 'T0' in words:
						words.remove('T0')
					for word in words:
						dst.write(word)
						dst.write(' ')
					dst.write('\n')
			else:
				dst.write(line)