import click
import importlib
import os
import yaml
import sys
import venv

@click.group()
def monty():
    pass

@click.command(help="Creates new monty package")
@click.argument("path")
def new(path):
    try:
        abs_path = os.path.abspath(path)
        os.mkdir(abs_path)

        builder = venv.EnvBuilder()
        venv_path = os.path.join(abs_path, "venv")
        builder.create(venv_path)

        src_path = os.path.join(abs_path, "src")
        os.mkdir(src_path)

        yaml_path = os.path.join(abs_path, "monty.yaml")
        with open(yaml_path, 'w') as m_yaml:
            m_yaml.write(
f"""---
package: {path}
version: 0.1.0
authors: []
entry: src/main.py
dependencies: ~
"""
            )
    except Exception as e:
        print(f"Error creating new project: {e}", file=sys.stderr)

@click.command(help="Install uninstalled packages")
def install():
    click.echo("Install packages")

@click.command(help="Runs the given monty script")
def run():
    with open("monty.yaml", "r") as config_file:
        entry = yaml.load(config_file, Loader=yaml.SafeLoader)["entry"]
        os.system(f"./venv/bin/python {entry}")

monty.add_command(new)
monty.add_command(install)
monty.add_command(run)

if __name__ == "__main__":
    monty()
