import re
import serial
import argparse
import gtk

class HelloWorld:
    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def hello(self, widget, data=None):
        self.serialConn.write("S\n")

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self, serialConn):
        self.serialConn = serialConn

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)

        # Here we connect the "destroy" event to a signal handler.
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)

        # Sets the border width of the window.
        self.window.set_border_width(10)

        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Load")

        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.button.connect("clicked", self.hello, None)

        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
        # self.button.connect_object("clicked", gtk.Widget.destroy, self.window)

        # This packs the button into the window (a GTK container).
        self.window.add(self.button)

        # The final step is to display this newly created widget.
        self.button.show()

        # and the window
        self.window.show()

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

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
    parser.add_argument('--filename', default='Traffic_Cone_Dual_Extrusion\Traffic_Cone_Rings.amf.gcode')
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
