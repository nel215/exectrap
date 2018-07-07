#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <termios.h>
#include <sys/ioctl.h>

int main(int argc, char **argv) {
  termios origTermios;
  tcgetattr(STDIN_FILENO, &origTermios);

  winsize origWinsize;
  ioctl(STDIN_FILENO, TIOCGWINSZ, reinterpret_cast<char*>(&origWinsize));

  auto ptyMaster = posix_openpt(O_RDWR);
  grantpt(ptyMaster);
  unlockpt(ptyMaster);

  auto ptsName = ptsname(ptyMaster);

  if (fork() == 0) {
    // parent
    setsid();

    auto ptySlave = open(ptsName, O_RDWR);
    close(ptyMaster);

    tcsetattr(ptySlave, TCSANOW, &origTermios);
    ioctl(ptySlave, TIOCSWINSZ, &origWinsize);

    dup2(ptySlave, STDIN_FILENO);
    dup2(ptySlave, STDOUT_FILENO);
    dup2(ptySlave, STDERR_FILENO);
    close(ptySlave);
    execvp(argv[1], &argv[1]);
  } else {
    // child
    termios newTermios = origTermios;

    newTermios.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    newTermios.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    newTermios.c_cflag &= ~(CSIZE | PARENB);
    newTermios.c_cflag |= CS8;
    newTermios.c_oflag &= ~(OPOST);
    newTermios.c_cc[VMIN]  = 1;
    newTermios.c_cc[VTIME] = 0;

    tcsetattr(STDIN_FILENO, TCSAFLUSH, &newTermios);

    const int bufSize = 512;
    pid_t pid;
    if ((pid = fork()) == 0) {
      // parent
      char buf[bufSize];
      for (;;) {
        auto nread = read(STDIN_FILENO, buf, bufSize);

        if (nread < 0 || nread == 0) break;

        const char codeDLE = 0x10;  // ctrl-p
        if (nread == 1 && buf[0] == codeDLE) {
          nread = 2;
          buf[1] = 16;
        }

        if (write(ptyMaster, buf, nread) != nread) break;
      }
      exit(0);
    } else {
      // child
      char buf[bufSize];
      for (;;) {
        auto nread = read(ptyMaster, buf, bufSize)
        if (nread <= 0) break;

        if (write(STDOUT_FILENO, buf, nread) != nread) break;
      }
      kill(pid, SIGTERM);
    }
  }

  tcsetattr(STDIN_FILENO, TCSAFLUSH, &origTermios);

  return 0;
}
