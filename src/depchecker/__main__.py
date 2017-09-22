import os
import glob
import sys

import click
import pkg_resources


def find_site_packages(env_path):
    patterns = [
        'site-packages/',
        '*/site-packages/',
        '*/*/site-packages',
    ]

    result = []
    for pattern in patterns:
        result.extend(glob.glob(os.path.join(env_path, pattern)))

    return result


@click.command()
@click.option('env_path', '--env-path', default=None, help='Path to env to check')
def depchecker_cli(env_path):
    if not env_path:
        working_set = pkg_resources.working_set
    else:
        site_packages_paths = find_site_packages(env_path)
        if not site_packages_paths:
            print('Error: can\'t find site-packages in: %s' % env_path)
            sys.exit(1)

        print('Checking packages in:')
        for path in site_packages_paths:
            print(' ' * 4 + str(path))

        working_set = pkg_resources.WorkingSet(entries=site_packages_paths)

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
