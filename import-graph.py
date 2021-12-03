import collections
import os
import pprint
import re

import click


@click.command()
def main():
    imports = collections.defaultdict(set)

    for dirpath, dirnames, filenames in os.walk("vigilant_crypto_snatch"):
        filenames = [filename for filename in filenames if filename.endswith(".py")]

        for filename in filenames:
            if filename.startswith("test_") or filename.endswith("_test.py"):
                continue
            with open(os.path.join(dirpath, filename)) as f:
                for line in f:
                    if m := re.match(r"from (.*) import .*", line):
                        module = m.group(1)
                        if filename == "__init__.py":
                            this = f"{dirpath}".replace("/", ".")
                        else:
                            this = f"{dirpath}/{filename[:-3]}".replace("/", ".")
                        if module.startswith("."):
                            parents = f"{dirpath}/{filename[:-3]}".split("/")
                            while module.startswith("."):
                                parents.pop()
                                module = module[1:]
                            if module:
                                parents.append(module)
                            module = ".".join(parents)
                            imports[this].add(module)
                        if module.startswith("vigilant_crypto_snatch"):
                            imports[this].add(module)
    pprint.pprint(imports)

    all_modules = set(imports.keys()) | set(
        elem for values in imports.values() for elem in values
    )

    with open("dependency-graph.puml", "w") as f:
        f.write("@startuml\n")
        for module in all_modules:
            f.write(f"component {module}\n")
        for source, targets in imports.items():
            for target in targets:
                f.write(f"{target} <-- {source}\n")
        f.write("@enduml\n")

    with open("dependency-graph.dot", "w") as f:
        f.write("digraph {\n")
        f.write("overlap = false\n")
        f.write("splines = true\n")
        f.write("node [shape=box]\n")
        for module in all_modules:
            f.write(f'"{module}"\n')
        for source, targets in imports.items():
            for target in targets:
                f.write(f'"{source}" -> "{target}"\n')
        f.write("}\n")


if __name__ == "__main__":
    main()
