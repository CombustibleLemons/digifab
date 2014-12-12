import re
import serial
import argparse
from extrusions import calc_lengths

def measure_lengths(serial_fd, channel, color_lengths):
    ser = serial.Serial(4, 115200)
    # hello = HelloWorld(ser)
    # hello.main()

    for length in color_lengths:
        print "Load extruder ", length[0]
        while True:
            # Setup the extruder
            stepOne = ser.readline().rstrip()
            print stepOne
            if (stepOne == "loaded"):
                ser.write("B\n")
            else:
                # This makes sure the switch is in the right start before we actually do anything.
                continue

            # Print the requisite number of millimeters
            ser.write("E%f\n" % length[1])
            result = ser.readline()
            print "Length extruded:", result

            # Change according to the offset
            stepTwo = ser.readline().rstrip()
            print stepTwo
            if (stepTwo == "cut"):
                ser.write("F\n")
            break


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', default='Traffic_Cone_Dual_Extrusion/Traffic_Cone_Rings.amf.gcode')
    parser.add_argument('--serial_port', default=4)
    parser.add_argument('--channel', default=115200)
    args = parser.parse_args()

    # Get the color lengths
    color_lengths = calc_lengths(args.filename)

    # Fix Colors
    # Total Hack, fix for more than 2 colors
    for i in range(0, len(color_lengths)-1, 2):
        first = color_lengths[i]
        second = color_lengths[i+1]
        # Ugh, this is an awful way to do it, fix this later
        if first[1] < 20.0:
            second[1] += first[1]
            first[1] = 0
        elif second[1] < 20.0:
            first[1] += second[1]
            second[1] = 0
        color_lengths[i] = first
        color_lengths[i+1] = second

    # Talk to the Arduino in order to print out the appropriate lengths
    measure_lengths(args.serial_port, args.channel, color_lengths)
