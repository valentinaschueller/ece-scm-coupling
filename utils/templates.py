from pathlib import Path

import jinja2


def get_template(template_path: Path) -> jinja2.Template:
    """get Jinja2 template file"""
    loader = jinja2.FileSystemLoader(template_path.parent)
    environment = jinja2.Environment(loader=loader)
    return environment.get_template(template_path.name)


def render_config_xml(
    destination: Path, config_run_template: Path, experiment: dict
) -> None:
    jinja_template = get_template(config_run_template)
    with open(destination / "config-run.xml", "w") as config_run_xml:
        config_run_xml.write(
            jinja_template.render(
                setup_dict=experiment,
            )
        )
