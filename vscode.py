from minescript import *
import sys
import os
import requests



try:
    os.chdir("minescript")
except:
    pass


URL = "https://raw.githubusercontent.com/n-aoH/Minescript-Class-Explorer/main/ClassList/classes.json"
FOLDER = "VS ClassList"
FILE_PATH = os.path.join(FOLDER, "classes.json")
os.makedirs(FOLDER, exist_ok=True)
classes: list = []
def auto():
    global classes
    classes = [
        "net.minecraft.world.entity.player.Player",
        "net.minecraft.world.phys.Vec3",
        "net.minecraft.world.entity.Entity",
        "net.minecraft.world.entity.LivingEntity",
        "net.minecraft.world.item.ItemStack",
        "net.minecraft.client.Minecraft"
    ]
    with open("classes.json",'w') as file:
        json.dump(classes, file)

lines = []
def review():
    classlist = {}

    for file in os.listdir(FOLDER):

        
        if not file.endswith(".json"):
            continue

        path = os.path.join(FOLDER, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        

        
        classlist.update(data)
        

    def writefile(data_dict,INSERT_ALL,TO_INSERT):
        global lines
                # ============================================================
        # TYPE REGISTRY (IMPORTANT FIX)
        # ============================================================
        lines = []
        EXPOSED_TYPES = set()

        PRIMITIVES = {
            "void", "boolean", "byte", "short", "int",
            "long", "float", "double", "char"
        }

        JAVA_TO_PYTHON = {
            "java.lang.String": "str",
            "java.lang.Boolean": "bool",
            "java.lang.Integer": "int",
            "java.lang.Float": "float",
            "java.lang.Double": "float",
            "java.lang.Object": "object",
            "java.util.List": "list",
            "java.util.Map": "dict",
            "java.util.Set": "set",
        }

        # ============================================================
        # TYPE CONVERSION + TRACKING
        # ============================================================

        def track_type(java_type: str) -> str:
            global lines
        
            if java_type is None:
                return "Any"

            # arrays
            if java_type.endswith("[]"):
                java_type = java_type[:-2]

            # generics strip base
            if "<" in java_type:
                base = java_type[:java_type.index("<")]
            else:
                base = java_type

            # record custom types for aliasing
            if base not in PRIMITIVES and base not in JAVA_TO_PYTHON:
                if "." in base:
                    EXPOSED_TYPES.add(base)

            return java_to_python_type(java_type)


        def java_to_python_type(java_type: str) -> str:
            global lines
        
            if java_type is None:
                return "Any"

            # arrays
            if java_type.endswith("[]"):
                inner = java_to_python_type(java_type[:-2])
                return f"list[{inner}]"

            # direct mapping
            if java_type in JAVA_TO_PYTHON:
                return JAVA_TO_PYTHON[java_type]

            # generics
            if "<" in java_type and ">" in java_type:
            
                base = java_type[:java_type.index("<")]
                inner = java_type[java_type.index("<")+1:-1]

                base_py = JAVA_TO_PYTHON.get(base, base.split(".")[-1])

                inner_parts = [x.strip() for x in inner.split(",")]

                inner_py = ", ".join(
                    java_to_python_type(x)
                    for x in inner_parts
                )

                return f"{base_py}[{inner_py}]"

            return java_type.split(".")[-1]


        # ============================================================
        # BUILD PACKAGE TREE
        # ============================================================

        tree = {}

        dta = {}
        for key, value in data_dict.items():
            if INSERT_ALL or key in TO_INSERT:
                dta[key] = value
                

        for full_name, value in dta.items():
        
            current = tree
            parts = full_name.split(".")

            for part in parts[:-1]:
                current = current.setdefault(part, {})

            current[parts[-1]] = value


        # ============================================================
        # CLASS DETECTION
        # ============================================================

        def is_class_dict(obj):
            global lines
            
        
            if not isinstance(obj, dict):
                return False

            return any(
                isinstance(v, dict) and "_type" in v
                for v in obj.values()
            )


        # ============================================================
        # OUTPUT LINES
        # ============================================================

        lines = []

        lines.append("from typing import Any")
        lines.append("from __future__ import annotations")
        lines.append("")

        # ============================================================
        # 🔥 CRITICAL FIX: FLATTEN TYPE ALIASES
        # ============================================================

        def short_name(path: str) -> str:
            global lines
            return path.split(".")[-1]


        def emit_type_aliases():
            global lines
            for full in sorted(EXPOSED_TYPES):
            
                alias = short_name(full)

                if alias in PRIMITIVES:
                    continue
                
                lines.append(f"{alias} = {full}")

            lines.append("")


        # ============================================================
        # PACKAGE GENERATION
        # ============================================================

        generated_packages = set()

        def ensure_packages(path):
            global lines
        
            current = []

            for depth, part in enumerate(path):
            
                current.append(part)
                key = ".".join(current)

                if key in generated_packages:
                    continue
                
                generated_packages.add(key)

                indent = "    " * depth

                lines.append(f"{indent}class {part}:")
                lines.append(f"{indent}    pass")
                lines.append("")


        # ============================================================
        # CLASS GENERATION
        # ============================================================

        def generate_class(class_name, class_data, indent_level):
            global lines
        
            indent = "    " * indent_level

            lines.append(f"{indent}class {class_name}:")

            has_content = False

            for name, info in class_data.items():
            
                if not isinstance(info, dict):
                    continue
                
                if "_type" not in info:
                    continue
                
                has_content = True

                py_return = track_type(info["return"])

                # FIELD
                if info["_type"] == "field":
                
                    lines.append(
                        f"{indent}    {name}: {py_return} = None"
                    )

                # METHOD
                elif info["_type"] == "method":
                
                    args = info["args"] or []

                    arg_strings = []

                    for i, arg in enumerate(args):
                    
                        arg_type = track_type(arg)

                        arg_strings.append(
                            f"arg{i}: {arg_type}"
                        )

                    signature = ", ".join(arg_strings)

                    lines.append("")
                    lines.append(
                        f"{indent}    def {name}({signature}) -> {py_return}:"
                    )
                    lines.append(
                        f"{indent}        pass"
                    )

            if not has_content:
                lines.append(f"{indent}    pass")

            lines.append("")
            lines.append("")


        # ============================================================
        # TREE WALKER
        # ============================================================

        def walk_tree(node, path=[]):
            global lines
        
            for name, child in node.items():
            
                current_path = path + [name]

                if is_class_dict(child):
                
                    ensure_packages(path)
                    generate_class(name, child, len(path))

                elif isinstance(child, dict):
                    walk_tree(child, current_path)


        # ============================================================
        # RUN
        # ============================================================

        walk_tree(tree)

        # insert aliases BEFORE writing classes
        emit_type_aliases()

        
        source = "from system.lib.minescript import *\n" + "\n".join(lines)

        source = source.replace("$", "_DOLLAR_")

        with open("minescript.pyi", "w", encoding="utf-8") as f:
            f.write(source)

        print("Completed!")

    cnt = 0
    for key in classlist.keys():
        if key in classes:
            cnt += 1

    print("Creating Intellisense docs for "+str(cnt)+" Classes.")
    writefile(classlist,False,classes)

if len(sys.argv) == 1:
    print("VS Code Mapping Settings.")
    print("Usage: vscode <arg>      ")
    print("args: \nadd <JavaClass>  ")
    print("del <JavaClass>          ")
    print("list                     ")
    print("auto                     ")
    print("download                 ")
    exit()

try:
    with open('classes.json', 'r') as file:
        classes = json.load(file)
except:
    
    if sys.argv[1] == "auto":
        auto()
        review()
        exit()
    else:
        print("No class settings. Use \\vscode auto to generate defaults.")
    exit()
    


if sys.argv[1] == "auto":
    auto()
    review()
    exit()
if sys.argv[1] == "list":
    str = ""
    for c in classes:
        
        str += "\n"+c

    print("Loaded Classes: "+str)
    exit()

if sys.argv[1] == "add":
    try:
        classes.append(sys.argv[2])
        with open("classes.json",'w') as file:
            json.dump(classes, file)
        
        print("Added Class: "+sys.argv[2])
        review()

    except:
        print("Requires a second arg: Class. classes can be found on mappings.dev.")
    exit()

if sys.argv[1] == "del":
    try:
        classes.remove(sys.argv[2])
        with open("classes.json",'w') as file:
            json.dump(classes, file)
        review()
        print("Removed Class: "+sys.argv[2])
    except:
        print("Requires a second arg: Class. classes can be found on mappings.dev.")
    exit()

if sys.argv[1] == "download":
    response = requests.get(URL)
    response.raise_for_status()

    # Write file
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Successfully downloaded!")
    exit()


echo("Unkown Arguent: "+sys.argv[1])
