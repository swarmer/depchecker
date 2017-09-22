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
    package_count = 0
    for package in working_set:
        package_count += 1
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
        print('Everything is OK (checked %d packages)' % package_count)


if __name__ == '__main__':
    depchecker_cli()
