#! /usr/bin/python3
import sys
import os
import termios

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

def setraw(fd, when=termios.TCSAFLUSH, min=1, time=0):
    """Puts current terminal into raw mode."""

    mode = termios.tcgetattr(fd)

    mode[IFLAG] = mode[IFLAG] & ~(termios.BRKINT | termios.ICRNL | termios.INPCK | termios.ISTRIP | termios.IXON)
    mode[OFLAG] = mode[OFLAG] & ~(termios.OPOST)
    mode[CFLAG] = mode[CFLAG] | termios.CS8
    mode[LFLAG] = mode[LFLAG] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
    mode[CC][termios.VMIN] = 0
    mode[CC][termios.VTIME] = 1

    termios.tcsetattr(fd, when, mode)

class rawmode(object):
    """Context manager for raw mode"""

    def __init__(self, fd, when=termios.TCSAFLUSH, min=1, time=0):
        self.fd = fd
        self.when = when
        self.min = min
        self.time = time

    def __enter__(self):
        self.savedmode = termios.tcgetattr(self.fd)
        setraw(self.fd, self.when, self.min, self.time)

    def __exit__(self, *ignored):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.savedmode)

def _opentty(device, bufsize):
    """Open a tty for reading and writing"""
    fd = os.open(device, os.O_RDWR | os.O_NOCTTY)

    if sys.version_info[0] >= 3:

        try:
            os.lseek(fd, 0, os.SEEK_CUR)
        except OSError:
            bufsize = 0
        return open(fd, 'rb+', bufsize)

    return os.fdopen(fd, 'r+', bufsize)

class opentty(object):
    """Context manager for opening a tty safely"""

    device = '/dev/tty'

    def __init__(self, bufsize=1):
        self.bufsize = bufsize

    def __enter__(self):
        self.tty = None

        try:
            self.tty = _opentty(self.device, self.bufsize)
        except EnvironmentError:
            pass
        return self.tty

    def __exit__(self, *ignored):
        if self.tty is not None:
            self.tty.close()

def _readyx(stream):
    """Read a CSI """
    output = b''
    # read one byte from the stream
    c = stream.read(1)

    while c:
        output += c
        if c == b'R':
            break
        c = stream.read(1)

    if output:
        print('output: {}'.format(output))
        line, col = map(int, output[2:-1].decode('ascii').split(';'))
        return (line, col)

if __name__ == '__main__':
    with opentty() as tty:
        with rawmode(tty, min=0, time=30):
            tty.write(b'\033[6n')
            print(_readyx(tty))

