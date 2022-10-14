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

    desire_ws = sys.argv[2]
    has_workspace = not desire_ws == "default"

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

    workspaces = get_workspace(path)
    all_ws = workspaces["workspaces"]
    current_ws = workspaces["current"]
    if destroy and desire_ws not in all_ws:
        sys.exit(f"request for destroying a workspace ({desire_ws}) that doesn't exist")

    if has_workspace:
        if desire_ws not in all_ws:
            run(cmd(f"workspace new {desire_ws}"))
        elif desire_ws != current_ws:
            run(cmd(f"workspace select {desire_ws}"))

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
