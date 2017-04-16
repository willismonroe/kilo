#! /usr/bin/python3
import sys
import os
import termios

import time

# helpful module: https://github.com/stefanholek/term/blob/master/term/__init__.py

# Helper prefixes
ESC = "\x1b"
CSI = ESC + "["

# Indexes for termios list

IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6

class Terminal():
    """Class dealing with all aspects of writing and reading a tty connection."""

    def __init__(self, bufsize=1):
        self.bufsize = bufsize
        self.tty = self.open_tty(bufsize=self.bufsize)

    def open_tty(self, device='/dev/tty', bufsize=1):
        fd = os.open(device, os.O_RDWR | os.O_NOCTTY)

        if sys.version_info[0] >= 3:

            try:
                os.lseek(fd, 0, os.SEEK_CUR)
            except OSError:
                bufsize = 0
            return open(fd, 'rb+', bufsize)

        return os.fdopen(fd, 'r+', bufsize)

    def close_tty(self):
        self.tty.close()

    def set_raw(self, when=termios.TCSAFLUSH, min=1, time=0):
        """Puts current terminal into raw mode."""
        self.savedmode = termios.tcgetattr(self.tty)

        mode = termios.tcgetattr(self.tty)

        mode[IFLAG] = mode[IFLAG] & ~(termios.BRKINT | termios.ICRNL | termios.INPCK | termios.ISTRIP | termios.IXON)
        mode[OFLAG] = mode[OFLAG] & ~(termios.OPOST)
        mode[CFLAG] = mode[CFLAG] | termios.CS8
        mode[LFLAG] = mode[LFLAG] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
        mode[CC][termios.VMIN] = 0
        mode[CC][termios.VTIME] = 1

        termios.tcsetattr(self.tty, when, mode)

    def exit_raw(self):
        termios.tcsetattr(self.tty, termios.TCSAFLUSH, self.savedmode)

    def send_sequence(self, sequence, response=False):
        command = str.encode('\033[' + sequence)
        self.tty.write(command)
        if response:
            return self.read_response()

    def read_response(self):
        """Read a CSI """
        output = b''
        # read one byte from the stream
        c = self.tty.read(1)

        while c:
            output += c
            if c == b'R':
                break
            c = self.tty.read(1)

        if output:
            return output.decode('ascii')


class Screen():

    def __init__(self):
        self.term = Terminal()
        self.term.set_raw()
        self.buffer = ''

    def get_window_size(self):
        self.term.send_sequence('999C')
        self.term.send_sequence('999B')
        self.get_cursor_pos()

    def get_cursor_pos(self):
        output = self.term.send_sequence('6n', True)[2:-1].split(';')
        self.max_row, self.max_col = map(int, output)

    def move_cursor(self, row, col):
        # <ESC>[{ROW};{COLUMN}H
        self.term.send_sequence('{};{}H'.format(row, col))

    def write_status_msg(self, msg):
        self.move_cursor(self.max_row-1, 0)
        self.term.tty.write(str.encode(">>>--- STATUS BAR msg: {}".format(msg)))

    def read_input(self):
        pass

    def refresh(self):
        self.write_status_msg('AAAA')

    def write_buffer(self):
        self.move_cursor(1, 1)
        self.term.tty.write(str.encode(self.buffer))

class Editor():

    def __init__(self):
        self.screen = Screen()
        self.screen.get_window_size()

    def main_loop(self):
        # refresh screen, write buffer
        while True:

            self.screen.write_buffer()
            self.screen.refresh()

            ch = self.screen.term.tty.read(1)
            i = 0
            self.screen.move_cursor(i, i)
            i += 1
            self.screen.term.tty.write(ch)



if __name__ == '__main__':
    editor = Editor()
    editor.main_loop()