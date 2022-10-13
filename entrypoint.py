#!/usr/local/bin/python
import sys


def deploy():
    print(f"path {sys.argv[1]}")
    print(f"workspace {sys.argv[2]}")


if __name__ == '__main__':
    deploy()
