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


def get_cmd():
    buf = array.array('h', [0, 0, 0, 0])
    fcntl.ioctl(0, termios.TIOCGWINSZ, buf, True)

    cmd = 'stty rows {} cols {}'.format(buf[0], buf[1])
    return cmd


def handle_sigwinch(master_fd):
    def inner(signum=None, frame=None):
        cmd = get_cmd()
        os.write(master_fd, cmd.encode()+b'\r\x0c')
    return inner


def initialize(master_fd):
    cmd = get_cmd()
    os.write(master_fd, cmd.encode()+b'\r\x0c')
    signal.signal(signal.SIGWINCH, handle_sigwinch(master_fd))


def main():
    argv = sys.argv[1:]
    pty.spawn(argv, master_read, stdin_read, initialize)


if __name__ == '__main__':
    main()
