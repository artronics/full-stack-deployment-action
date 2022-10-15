#!/usr/local/bin/python
import os
import subprocess
import sys


def usage():
    return """Usage:
    NOTE: All options are positional and required
    command --path="" --workspace=default --options="" --dryrun=false --destroy=false --destroy-workspace=false
    
    --path               This is the directory that contains your terraform files. Pass empty string ("") for current working directory
    --workspace          This is the terraform workspace that will be created if necessary. Pass "default" if you don't want to create new one
    --options            This is any extra options that you want to pass to terraform command. For example "-var=foo=bar". Pass empty string ("") for no options
    --dryrun             If true terraform plan will be executed even if destroy option is true
    --destroy            If true terraform destroy will be executed. In case of dryrun terraform plan -destroy will be executed
    --destroy-workspace  If true then it will delete workspace as the final step when destroying. It switches to the "default" workspace before deleting current one
    """


def run(cmd, capture=False):
    cmds = [opt.strip() for opt in cmd.split(" ") if opt.strip() != ""]
    return subprocess.run(cmds, capture_output=capture, check=True)


def get_workspace(path):
    def cmd(opt):
        return f"terraform -chdir={path} {opt}"

    p = run(cmd("workspace show"), capture=True)
    current_ws = p.stdout.decode().strip()

    p = run(cmd("workspace list"), capture=True)
    ws_list = p.stdout.decode().split("\n")
    workspaces = [ws.strip() for ws in ws_list if ws != "" and current_ws not in ws]
    # append current one separately because, the terraform stdout adds an asterix (*) to the selected workspace
    workspaces.append(current_ws)

    return workspaces, current_ws


if __name__ == '__main__':
    if len(sys.argv) < 7:
        sys.exit(usage())


    def parse_arg(key, arg):
        if not arg.startswith(f"--{key}="):
            print("this", key)
            print("this", arg)
            sys.exit(usage())
        return arg.split(f"--{key}=")[-1]


    path_arg = parse_arg("path", sys.argv[1])
    path = path_arg if path_arg else os.getcwd()

    desired_ws = parse_arg("workspace", sys.argv[2])
    has_workspace = not desired_ws == "default"

    extra_opt = parse_arg("options", sys.argv[3])

    # arg4 is dryrun. The result of boolean says if we do apply or plan
    apply = parse_arg("dryrun", sys.argv[4]) == 'false'

    destroy_arg = parse_arg("destroy", sys.argv[5])
    if destroy_arg == 'true':
        destroy = True
    elif destroy_arg == 'false':
        destroy = False
    else:
        sys.exit("destroy options must be set explicitly and correctly. Either \"true\" or \"false\"")

    destroy_ws = parse_arg("destroy-workspace", sys.argv[6]) == "true"
    if (destroy_ws and not destroy) or (destroy_ws and destroy and not apply):
        sys.exit("you can only destroy workspace if operation is also destroy and also not dryrun")


    def cmd(opt):
        return f"terraform -chdir={path} {opt} {extra_opt}"


    run(cmd("init"))

    all_ws, current_ws = get_workspace(path)
    if destroy and desired_ws not in all_ws:
        sys.exit(f"request for destroying a workspace ({desired_ws}) that doesn't exist")

    if has_workspace:
        if desired_ws not in all_ws:
            run(cmd(f"workspace new {desired_ws}"))
        elif desired_ws != current_ws:
            run(cmd(f"workspace select {desired_ws}"))

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

    if destroy_ws and desired_ws != "default":
        run(cmd("workspace select default"))
        run(cmd(f"workspace delete {desired_ws}"))
