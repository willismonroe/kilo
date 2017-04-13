#! /usr/bin/python3
import sys
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

def setraw(fd, when=termios.TCSAFLUSH):
    """Puts current terminal into raw mode."""

    mode = termios.tcgetattr(fd)

    mode[IFLAG] = mode[IFLAG] & ~(termios.BRKINT | termios.ICRNL | termios.INPCK | termios.ISTRIP | termios.IXON)
    mode[OFLAG] = mode[OFLAG] & ~(termios.OPOST)
    mode[CFLAG] = mode[CFLAG] | termios.CS8
    mode[LFLAG] = mode[LFLAG] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
    mode[CC][termios.VMIN] = 0
    mode[CC][termios.VTIME] = 1

    termios.tcsetattr(fd, when, mode)

if __name__ == '__main__':
    setraw(sys.stdin)
    sys.stdout.write("{}{}".format(CSI, "6n"))
