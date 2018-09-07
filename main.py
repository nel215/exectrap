import os
import sys
import array
import fcntl
import signal
import termios
from exectrap import pty


def stdin_read(fd):
    data = os.read(fd, 1024)
    if data == b'\x10':
        data += b' \x7f'
    return data


def master_read(fd):
    data = os.read(fd, 1024)
    return data


def handle_sigwinch(signum=None, frame=None):
    buf = array.array('h', [0, 0, 0, 0])
    fcntl.ioctl(0, termios.TIOCGWINSZ, buf, True)

    cmd = 'stty rows {} cols {}'.format(buf[0], buf[1])
    sys.stdin.write(cmd)


def main():
    signal.signal(signal.SIGWINCH, handle_sigwinch)
    argv = sys.argv[1:]
    pty.spawn(argv, master_read, stdin_read, handle_sigwinch)


if __name__ == '__main__':
    main()
