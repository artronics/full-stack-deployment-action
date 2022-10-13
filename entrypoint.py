#!/usr/local/bin/python
import os
import subprocess
import sys


def run(cmd, capture=False):
    cmds = [opt.strip() for opt in cmd.split(" ") if opt.strip() != ""]
    return subprocess.run(cmds, capture_output=capture, check=True)


def terraform(chdir, operation, opt=""):
    return f"terraform {chdir} {operation} {opt}"


def get_workspace(chdir):
    p = run(terraform(chdir, "workspace show"), capture=True)
    current_ws = p.stdout.decode().strip()

    p = run(terraform(chdir, "workspace list"), capture=True)
    ws_list = p.stdout.decode().split("\n")
    workspaces = [ws.strip() for ws in ws_list if ws != "" and current_ws not in ws]
    # append current one separately because output adds an asterix (*) to the selected one
    workspaces.append(current_ws)

    return {
        "workspaces": workspaces,
        "current": current_ws
    }


def deploy():
    path = sys.argv[1] if sys.argv[1] else os.getcwd()
    chdir = f"-chdir={path}"

    workspace = sys.argv[2]
    has_workspace = not workspace == "default"

    opt = sys.argv[3]
    dryrun = sys.argv[4] == 'false'
    print(f"dryrun |{sys.argv[4]}| {dryrun}")

    run(terraform(chdir, "init"))

    if has_workspace:
        workspaces = get_workspace(chdir)
        if workspace not in workspaces["workspaces"]:
            run(terraform(chdir, f"workspace new {workspace}"))
        elif workspace != workspaces["current"]:
            run(terraform(chdir, f"workspace select {workspace}"))

    if dryrun:
        run(terraform(chdir, f"plan"))
    else:
        opt += " -auto-approve"
        run(terraform(chdir, f"apply", opt=opt))


if __name__ == '__main__':
    deploy()
