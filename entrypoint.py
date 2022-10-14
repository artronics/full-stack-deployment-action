#!/usr/local/bin/python
import os
import subprocess
import sys


def run(cmd, capture=False):
    cmds = [opt.strip() for opt in cmd.split(" ") if opt.strip() != ""]
    return subprocess.run(cmds, capture_output=capture, check=True)


# def terraform(chdir, operation, opt=""):
#     return f"terraform {chdir} {operation} {opt}"


def get_workspace(path):
    def cmd(opt):
        return f"terraform -chdir={path} {opt}"

    p = run(cmd("workspace show"), capture=True)
    current_ws = p.stdout.decode().strip()

    p = run(cmd("workspace list"), capture=True)
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

    workspace = sys.argv[2]
    has_workspace = not workspace == "default"

    extra_opt = sys.argv[3]
    apply = sys.argv[4] == 'false'  # arg4 is dryrun. The result of boolean says if we do apply or plan

    destroy_arg = sys.argv[5]
    if destroy_arg == 'true':
        destroy = True
    elif destroy_arg == 'false':
        destroy = False
    else:
        sys.exit("destroy options must be set explicitly and correctly. Either \"true\" or \"false\"")

    def cmd(opt):
        return f"terraform -chdir={path} {opt} {extra_opt}"

    run(cmd("init"))

    if has_workspace:
        workspaces = get_workspace(path)
        if workspace not in workspaces["workspaces"]:
            run(cmd(f"workspace new {workspace}"))
        elif workspace != workspaces["current"]:
            run(cmd(f"workspace select {workspace}"))

    if apply:
        if destroy:
            run(cmd(f"destroy -auto-approve"))
        else:
            run(cmd(f"apply -auto-approve"))
    else:
        if destroy:
            run(cmd(f"plan -destroy"))
        else:
            run(cmd(f"plan"))


if __name__ == '__main__':
    deploy()
