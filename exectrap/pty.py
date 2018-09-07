import os
import tty
from pty import STDIN_FILENO, CHILD, fork, _read, _copy


def spawn(argv, master_read=_read, stdin_read=_read, initialize=None):
    """Create a spawned process."""
    if isinstance(argv, str):
        argv = (argv,)
    pid, master_fd = fork()
    if pid == CHILD:
        os.execlp(argv[0], *argv)
    try:
        mode = tty.tcgetattr(STDIN_FILENO)
        tty.setraw(STDIN_FILENO)
        restore = 1
    except tty.error:    # This is the same as termios.error
        restore = 0
    try:
        if initialize is not None:
            initialize(master_fd)
        _copy(master_fd, master_read, stdin_read)
    except OSError:
        if restore:
            tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)

    os.close(master_fd)
    return os.waitpid(pid, 0)[1]
