# exectrap

Convert ctrl-p into ctrl-p + ctrl-@ and send to pts to resolve conflict detach keys of docker.

## Usage

```
$ exectrap docker run --rm -i -t busybox /bin/sh
# echo hello
hello
# echo hello  # type ctrl-p
```

## Build

```
$ mkdir build
$ cd build
$ cmake ..
$ make
```

## Reference

- http://note.hibariya.org/articles/20150628/pty.html
