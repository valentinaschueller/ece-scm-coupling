from pathlib import Path

import jinja2

from context import Context


def get_template(template_path: Path) -> jinja2.Template:
    """get Jinja2 template file"""
    loader = jinja2.FileSystemLoader(template_path.parent)
    environment = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)
    return environment.get_template(template_path.name)


def render_config_xml(context: Context, experiment: dict) -> None:
    jinja_template = get_template(context.config_run_template)
    with open(context.runscript_dir / "config-run.xml", "w") as config_run_xml:
        config_run_xml.write(
            jinja_template.render(
                context=context,
                setup_dict=experiment,
            )
        )
