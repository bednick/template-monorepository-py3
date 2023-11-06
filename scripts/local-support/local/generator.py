import os
import pathlib
import sys

import jinja2

from local import utils


def gen_module(project_name: str, module_type: str, template_type: str) -> bool:
    if any(
        path.exists()
        for path in (
            pathlib.Path(os.getcwd()) / "libraries" / project_name,
            pathlib.Path(os.getcwd()) / "services" / project_name,
        )
    ):
        print(f'module "{project_name}" already exist! Stop gen.', file=sys.stderr)
        return False

    new_dir = pathlib.Path(os.getcwd()) / module_type / project_name
    template_root = pathlib.Path(__file__).parent / "templates" / template_type

    module_name = utils.gen_module_name(project_name)
    new_dir.mkdir(parents=True)

    for path, subdirs, files in os.walk(template_root):
        relpath = os.path.relpath(path, start=template_root)
        for subdir in subdirs:
            new_subdir_absolute = str((new_dir / relpath / subdir).absolute())
            render_new_subdir_absolute = jinja2.Template(new_subdir_absolute).render(
                project_name=project_name,
                module_name=module_name,
            )
            pathlib.Path(render_new_subdir_absolute).mkdir()

        for file in files:
            new_filename = file[:-7] if file.endswith(".jinja2") else file
            new_file_absolute = str((new_dir / relpath / new_filename).absolute())
            render_new_file_absolute = jinja2.Template(new_file_absolute).render(
                project_name=project_name,
                module_name=module_name,
            )
            with open(f"{path}/{file}", "r") as template_fr:
                render_file_data = jinja2.Template(template_fr.read()).render(
                    project_name=project_name,
                    module_name=module_name,
                )
            if render_file_data:
                render_file_data += "\n"
            with open(render_new_file_absolute, "w") as template_fr:
                template_fr.write(render_file_data)
    return True
