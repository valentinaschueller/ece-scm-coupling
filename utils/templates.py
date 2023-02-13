import pathlib as Path

import jinja2
from files import ChangeDirectory


def get_template(template_filename: str) -> jinja2.Template:
    """get Jinja2 template file"""
    search_path = ["."]

    loader = jinja2.FileSystemLoader(search_path)
    environment = jinja2.Environment(loader=loader)
    return environment.get_template(template_filename)


def render_config_xml(
    destination: Path, config_template: jinja2.Template, experiment: dict
) -> None:
    if not destination.is_dir():
        raise TypeError(f"Destination is not a directory! {destination=}")
    with ChangeDirectory(destination):
        with open("./config-run.xml", "w") as config_out:
            config_out.write(
                config_template.render(
                    setup_dict=experiment,
                )
            )
