import os
from os import listdir
from os.path import isfile, join
import sys
import subprocess

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line) 
    popen.stdout.close()
    return_code = popen.wait()
    return return_code

def execute_wait(cmd):
    with subprocess.Popen(cmd, stdin=None, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT, universal_newlines=True) as build_tool_process:
        exit_code = build_tool_process.wait()
    return exit_code

def run_default_building_pipeline():
    build_args = []
    
    for i, arg in enumerate(sys.argv):
        if i >= 1:
            build_args.append(arg)

    print("Invoking shell: ", build_args)

    execute(build_args)
    

def get_project_path():
    for i, arg in enumerate(sys.argv):
        if arg.startswith("-Project"):
            words = arg.split("=")
            value = words[1]
            return value
    return None

def get_project_name(project_file_path):
    project_file_name = os.path.basename(project_file_path)
    name = project_file_name.rsplit(".", 1 )[0]
    return name

def get_project_dir(project_file_path):
    return os.path.dirname(project_file_path)

def get_build_configuration():
    return sys.argv[4]

def get_architecture():
    return sys.argv[3]

def get_target_directory_path():
    project_file_path = get_project_path()
    if project_file_path is None:
        return None
    project_dir = get_project_dir(project_file_path)
    arch = get_architecture()
    config = get_build_configuration()
    project_name = get_project_name(project_file_path)
    path = f"{project_dir}\\Intermediate\\Build\\{arch}\\UnrealEditor\\{config}\\{project_name}"
    return path

def get_editor_directory_path():
    project_file_path = get_project_path()
    if project_file_path is None:
        return None
    project_dir = get_project_dir(project_file_path)
    arch = get_architecture()
    config = get_build_configuration()
    project_name = get_project_name(project_file_path)

    path = f"{project_dir}\\Intermediate\\Build\\{arch}\\{project_name}Editor\\{config}\\Engine"
    return path

def fix_file(entry_fullname):
     text = None
     with open(entry_fullname, "r") as target_file:
        text = target_file.read()
     text = text.replace('"Version": "1.2"', '"Version": "1.1"')
     with open(entry_fullname, "w") as target_file:
        target_file.write(text)

def fix_editor_json_versions():
    editor_dir = get_editor_directory_path()
    if editor_dir is None:
        print("Unable to get editor directory")
        sys.exit(-1)

    print(f"Editor directory: {editor_dir}")

    for entry in listdir(editor_dir):
        entry_fullname = os.path.join(editor_dir, entry)
        if not isfile(entry_fullname):
            continue
        if not entry_fullname.endswith(".h.json"):
            #print(f"{entry} does not match the search pattern")
            continue
        print(f"Fixing json file {entry}")
        fix_file(entry_fullname)

    print("Finished fixing target files")

def fix_target_json_versions():
    target_dir = get_target_directory_path()
    if target_dir is None:
        print("Unable to get target directory")
        sys.exit(-1)

    print(f"Target directory: {target_dir}")

    for entry in listdir(target_dir):
        entry_fullname = os.path.join(target_dir, entry)
        #print(f"Checking entry {entry}")
        if not isfile(entry_fullname):
            #print(f"{entry} is not a file")
            continue
        if not entry_fullname.endswith(".cpp.json"):
            #print(f"{entry} does not match the search pattern")
            continue
        print(f"Fixing json file {entry}")
        fix_file(entry_fullname)

    print("Finished fixing editor files")


if __name__ == "__main__":

    fix_target_json_versions()
    fix_editor_json_versions()
    
    run_default_building_pipeline()
		