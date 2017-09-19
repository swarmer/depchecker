import os

import click
import pkg_resources


@click.command()
@click.option('env_path', '--env-path', default=None, help='Path to env to check')
def depchecker_cli(env_path):
    if not env_path:
        working_set = pkg_resources.working_set
    else:
        working_set = pkg_resources.WorkingSet(
            entries=[
                os.path.join(env_path, 'lib/python2.7/site-packages'),
            ]
        )

    requirements = []
    for package in working_set:
        requirements.extend((package, requirement) for requirement in package.requires())

    conflicts = False
    for package in working_set:
        for source_package, requirement in requirements:
            if package.key != requirement.key:
                continue

            if package not in requirement:
                conflicts = True
                print(
                    'CONFLICT: package %s doesn\'t conform to %s specified in %s' % (
                        package, requirement, source_package,
                    )
                )

    if not conflicts:
        print('Everything is OK')


if __name__ == '__main__':
    depchecker_cli()
