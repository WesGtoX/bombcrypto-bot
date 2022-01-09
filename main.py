#!/usr/bin/python
from subprocess import Popen


def main():
    while True:
        p = Popen("python index.py", shell=True)
        p.wait()


if __name__ == '__main__':
    main()
