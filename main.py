import os
import sys
import pty


def stdin_read(fd):
    data = os.read(fd, 1024)
    if data == b'\x10':
        data += b' \x7f'
    return data


def main():
    argv = sys.argv[1:]
    pty.spawn(argv, stdin_read=stdin_read)


if __name__ == '__main__':
    main()
