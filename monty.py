import click
import importlib
import os
import re
import yaml
import subprocess
import sys
import venv

def install_dep(dep_name, dep_type, uninstall=False):
    click.echo(f"Installing {dep_name}... \t", nl=False)

    url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    error = None

    if uninstall:
        subprocess.run(["./venv/bin/pip", "uninstall", dep_name])

    if re.search(url_regex, dep_type):
        error = subprocess.run(["./venv/bin/pip", "install", f"git+{dep_type}"], capture_output=True, text=True)
    elif dep_type == "latest":
        error = subprocess.run(["./venv/bin/pip", "install", dep_name], capture_output=True, text=True)
    else:
        error = subprocess.run(["./venv/bin/pip", "install", f"{dep_name}{dep_type}"], capture_output=True, text=True)

    output = error.stderr.strip("\n") if error.stderr else "done"

    click.echo(output)

@click.group()
def monty():
    pass

@click.command(help="Creates new monty package")
@click.option("--with-git", is_flag=True, help="Initiates a git repository on project creation")
@click.argument("path")
def new(path, with_git):
    try:
        abs_path = os.path.abspath(path)
        os.mkdir(abs_path)

        if with_git:
            subprocess.run(["git", "init", abs_path], capture_output=True)

        builder = venv.EnvBuilder(with_pip=True)
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

        lock_path = os.path.join(abs_path, "monty_lock.yaml")
        with open(lock_path, 'w') as l:
            pass

    except Exception as e:
        click.echo(f"Error creating new project: {e}", file=sys.stderr)

@click.command(help="Install uninstalled packages")
def install():
    # install wheel if not installed already
    if "\nwheel" not in subprocess.run(["./venv/bin/pip", "list"], capture_output=True, text=True).stdout.split(" "):
        subprocess.run(["./venv/bin/pip", "install", "wheel"], capture_output=True)

    with open("monty.yaml", "r") as config_file, open("monty_lock.yaml", "r+") as lock_file:
        deps = yaml.load(config_file, Loader=yaml.SafeLoader)["dependencies"]
        lock = yaml.load(lock_file, Loader=yaml.SafeLoader)

        if deps is None:
            sys.exit(0)

        if lock is None:
            lock = {}

        for dep in deps:
            dep_name = list(dep.keys())[0]

            if dep_name not in lock:
                install_dep(dep_name, dep[dep_name])
                lock[dep_name] = dep[dep_name]
            elif lock[dep_name] == dep[dep_name]:
                click.echo(f"installing {dep_name}...\talready installed")
            else:
                install_dep(dep_name, dep[dep_name], uninstall=True)
                lock[dep_name] = dep[dep_name]

        lock_file.seek(0)
        yaml.dump(lock, lock_file)
        lock_file.truncate()

@click.command(help="Runs the given monty script")
def run():
    with open("monty.yaml", "r") as config_file:
        entry = yaml.load(config_file, Loader=yaml.SafeLoader)["entry"]
        subprocess.run(["./venv/bin/python", entry])

monty.add_command(new)
monty.add_command(install)
monty.add_command(run)

if __name__ == "__main__":
    monty()
