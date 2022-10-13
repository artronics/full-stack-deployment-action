#!/usr/local/bin/python
import os
import subprocess
import sys


def run(cmd, capture=False):
    return subprocess.run(cmd.split(" "), capture_output=capture, check=True)


def terraform(chdir, op):
    return f"terraform {chdir} {op}"


def get_workspace(chdir):
    p = run(terraform(chdir, "workspace show"), capture=True)
    current_ws = p.stdout.decode().strip()

    p = run(terraform(chdir, "workspace list"), capture=True)
    ws_list = p.stdout.decode().split("\n")
    workspaces = [ws.strip() for ws in ws_list if ws != "" and current_ws not in ws]
    workspaces.append(current_ws)

    return {
        "workspaces": workspaces,
        "current": current_ws
    }


def deploy():
    path = sys.argv[1]
    chdir = f"-chdir={path}" if path else ""

    workspace = sys.argv[2]
    has_workspace = not workspace == "default"
    print(f"cwd: {os.getcwd()}")

    run(terraform(chdir, "init"))

    if has_workspace:
        workspaces = get_workspace(chdir)
        if workspace not in workspaces["workspaces"]:
            run(terraform(chdir, f"workspace new {workspace}"))
        elif workspace != workspaces["current"]:
            run(terraform(chdir, f"workspace select {workspace}"))


if __name__ == '__main__':
    deploy()
