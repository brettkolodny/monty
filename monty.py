import click
import importlib
import os
import yaml
import subprocess
import sys
import venv

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
    except Exception as e:
        click.echo(f"Error creating new project: {e}", file=sys.stderr)

@click.command(help="Install uninstalled packages")
def install():
    # install wheel if not installed already
    if "\nwheel" not in subprocess.run(["./venv/bin/pip", "list"], capture_output=True, text=True).stdout.split(" "):
        subprocess.run(["./venv/bin/pip", "install", "wheel"], capture_output=True)

    with open("monty.yaml", "r") as config_file, open("monty_lock.yaml", "w+") as lock_file:
        deps = yaml.load(config_file, Loader=yaml.SafeLoader)["dependencies"]

        if deps is None:
            sys.exit(0)
    
        for dep in deps:
            if type(dep) is dict:
                dep_name = list(dep.keys())[0]
                click.echo(f"Installing {dep_name}... \t", nl=False)

                if "version" in dep[dep_name]:
                    version = dep[dep_name]["version"]
                    pip_output = subprocess.run(["./venv/bin/pip", "install", f"{dep_name}{version}"], capture_output=True)

                    if pip_output.stderr:
                        click.echo(pip_output.stderr, nl=False)
                    else:
                        click.echo("done")
                    
                elif "url" in dep[dep_name]:
                    url = dep[dep_name]["url"]
                    pip_output = subprocess.run(["./venv/bin/pip", "install", f"git+{url}"], capture_output=True)

                    if pip_output.stderr:
                        click.echo(pip_output.stderr, nl=False)
                    else:
                        click.echo("done")
                    
            else:
                click.echo(f"Installing {dep}... \t", nl=False)
                pip_output = subprocess.run(["./venv/bin/python3", "-m", "pip", "install", dep], capture_output=True)

                if pip_output.stderr:
                    click.echo(pip_output.stderr, nl=False)
                else:
                    click.echo("done")

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
