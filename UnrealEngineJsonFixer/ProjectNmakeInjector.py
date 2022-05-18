import os
import sys
import os.path

import xml.etree
import xml.etree.ElementTree as et

class NMakeCommandLine:
    def __init__(self, build, rebuild, clean):
        self.build = build
        self.rebuild = rebuild
        self.clean = clean

def is_property_group(xml_block):
    return "PropertyGroup" in xml_block.tag

def get_xml_configuiration_blocks(tree, root):
    result = []
    for child in root:
        if not is_property_group(child):
            continue

        condition = child.get("Condition")
        if condition is None:
            continue

        condition = condition.replace(" ", "")
        if "'$(Configuration)|$(Platform)'==" in condition and "Invalid" not in condition:
            result.append(child)

    return result

def get_nmake_from_config(config_xml):
    build = ""
    rebuild = ""
    clean = ""
    for child in config_xml:
        if "NMakeBuildCommandLine" in child.tag:
            build = child.text
        if "NMakeReBuildCommandLine" in child.tag:
            rebuild = child.text
        if "NMakeCleanCommandLine" in child.tag:
            clean = child.text

    return NMakeCommandLine(build, rebuild, clean)

def set_nmake_to_config(config_xml, nmake):
    for child in config_xml:
        if "NMakeBuildCommandLine" in child.tag:
            child.text = nmake.build
        if "NMakeReBuildCommandLine" in child.tag:
            child.text = nmake.rebuild
        if "NMakeCleanCommandLine" in child.tag:
            child.text = nmake.clean

# ProjectNmakeInjector.py path_to_project_file path_to_injected_python_script
if __name__ == "__main__":
    this_script_name = sys.argv[0]
    project_path = sys.argv[1]
    injected_script = sys.argv[2]

    #injected_script = injected_script.replace("\\", "/")
   
    print(f"Project: {project_path}")

    if not os.path.exists(project_path):
        print(f"Project file {project_path} does not exist!")
        quit()

    tree = et.parse(project_path)
    root = tree.getroot()

    configurations = get_xml_configuiration_blocks(tree, root)

    changes = False

    print("Found build configurations:")
    for config in configurations:
        print(config.get("Condition"))
        nmake = get_nmake_from_config(config)
        print(f"\t{nmake.build}")
        print(f"\t{nmake.rebuild}")
        print(f"\t{nmake.clean}")

        if nmake.build.startswith("python"):
            print("Already injected")
            continue

        nmake.build = f"python {injected_script} {nmake.build}"
        nmake.rebuild = f"python {injected_script} {nmake.rebuild}"
        nmake.clean = f"python {injected_script} {nmake.clean}"

        print(f"\t{nmake.build}")
        print(f"\t{nmake.rebuild}")
        print(f"\t{nmake.clean}")

        set_nmake_to_config(config, nmake)

        changes = True

    if changes:
        print("Saving...")
        xml_text_bytes = et.tostring(root, encoding='utf-8', method='xml')

        xml_text = xml_text_bytes.decode("utf-8")

        xml_text = xml_text.replace("ns0:", "").replace(":ns0", "")

        #path = project_path + ".debug.xml"
        path = project_path

        with open(path, "w") as f:
            f.write(xml_text)
    else:
        print("No changes was made")
