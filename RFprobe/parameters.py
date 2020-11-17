from argparse import ArgumentParser

def input_samplerate_d():
    return 40e6

def output_filename_d():
    return "analysis.json"

def lines_per_frame_d():
    return 525

def vsync_d():
    return 60

class Parameters:
    def __init__(self):
        self.args = self.argparser()

    # ambitious description
    def argparser(self):
        parser = ArgumentParser(description='Analyzes the capture file, removes spin-up, guess the standard and TBC it')
        parser.add_argument('-l', '--lines', nargs='?', default=lines_per_frame_d(), type=int,
                            help='lines per frame (default %d)' % lines_per_frame_d())
        parser.add_argument('-v', '--vsync', nargs='?', default=vsync_d(), type=int,
                            help='vertical sync frequency (default %d)' % vsync_d())
        parser.add_argument('-s', '--samp_rate', nargs='?', default=input_samplerate_d(), type=int,
                            help='capture sample rate (default %d)' % input_samplerate_d())
        parser.add_argument('-t', '--start_at', nargs='?', default=0, type=int,
                            help='start analysis at (default %d seconds)' % 0)
        parser.add_argument('-o', '--output', nargs='?', default=output_filename_d(), type=str,
                            help='write analysis log to file (default, %s)' % output_filename_d())

        return parser.parse_args()

    def output_filename(self):
        if self.args.output is None:
            return output_filename_d()
        else:
            return self.args.output

    def lines_per_frame(self):
        if self.args.lines is None:
            return lines_per_frame_d()
        else:
            return self.args.lines

    def vsync(self):
        if self.args.vsync is None:
            return vsync_d()
        else:
            return self.args.vsync

    def samp_rate(self):
        if self.args.samp_rate is None:
            return input_samplerate_d()
        else:
            return self.args.samp_rate

    def hsync(self):
        return self.vsync() * self.lines_per_frame()/2

    def start_at(self):
        if self.args.start_at is None:
            return 0
        else:
            return self.args.start_at


