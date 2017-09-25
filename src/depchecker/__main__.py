from __future__ import print_function

import os
import glob
import sys

import click
import pkg_resources
import requests


def find_site_packages(env_path):
    patterns = [
        'site-packages/',
        '*/site-packages/',
        '*/*/site-packages/',
    ]

    result = []
    for pattern in patterns:
        result.extend(glob.glob(os.path.join(env_path, pattern)))

    return result


def get_safety_db():
    print('Downloading safety-db...')
    safety_db_url = 'https://raw.githubusercontent.com/pyupio/safety-db/master/data/insecure_full.json'

    response = requests.get(safety_db_url)
    return response.json()


@click.command()
@click.option('env_path', '--env-path', default=None, help='Path to env to check')
def depchecker_cli(env_path):
    if not env_path:
        print('Checking packages in current virtual environment')
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

    print()

    # check conflicts between installed packages
    print('Checking conflicts between installed packages...')

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

    print()

    # check for vulnerabilities
    safety_db = get_safety_db()

    vulnerabilities = False
    package_count = 0
    for package in working_set:
        package_count += 1

        if package.key not in safety_db:
            continue

        for vulnerability in safety_db[package.key]:
            for spec in vulnerability['specs']:
                requirement = pkg_resources.Requirement.parse(package.key + spec)
                if package in requirement:
                    print('VULNERABILITY: %s: %s' % (package, vulnerability['advisory']))
                    vulnerabilities = True
                    break

    if not vulnerabilities:
        print('Everything is OK (checked %d packages)' % package_count)


if __name__ == '__main__':
    depchecker_cli()
