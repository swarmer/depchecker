from __future__ import print_function

import sys

import click
import pkg_resources
import requests

from .packages import InvalidEnvironmentError, InvalidRequirementsListError, PackageEnvironment


def fatal_error(exception):
    print('Error: %s' % exception)
    sys.exit(2)


def get_safety_db():
    print('Downloading safety-db...')
    safety_db_url = 'https://raw.githubusercontent.com/pyupio/safety-db/master/data/insecure_full.json'  # noqa: line-too-long

    response = requests.get(safety_db_url)
    return response.json()


def get_package_environment(env_path, requirements_paths):
    try:
        package_environment = PackageEnvironment(env_path, requirements_paths)
    except (InvalidEnvironmentError, InvalidRequirementsListError) as e:
        fatal_error(e)

    print('Checking packages in:')
    for path in package_environment.package_search_paths:
        if path == '':
            path = '.'

        print(' ' * 2 + str(path))

    return package_environment


def check_conflicts(package_environment):
    print('Checking conflicts between installed packages...')

    requirements = []
    for source in package_environment.requirements_sources:
        requirements.extend((source, requirement) for requirement in source.requires())

    conflicts = False
    package_count = 0
    for package in package_environment.packages:
        package_count += 1

        relevant_requirements = []
        for source, requirement in requirements:
            if package.key == requirement.key:
                relevant_requirements.append((source, requirement))

        for source, requirement in relevant_requirements:
            if package not in requirement:
                conflicts = True
                print(
                    'CONFLICT: package %s doesn\'t conform to %s specified by %s' % (
                        package, requirement, source,
                    )
                )

                for other_source, other_requirement in relevant_requirements:
                    if other_source == source and other_requirement == requirement:
                        continue

                    print(
                        '    Also required as %s by %s' % (
                            other_requirement, other_source,
                        )
                    )

    if not conflicts:
        print('Everything is OK (checked %d packages)' % package_count)


def check_vulnerabilities(package_environment):
    print('Checking installed packages for known vulnerabilities...')
    safety_db = get_safety_db()

    vulnerabilities = False
    package_count = 0
    for package in package_environment.packages:
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


@click.command()
@click.option(
    'env_path', '--env-path', default=None,
    help='Path to a virtual environment to be checked',
)
@click.option(
    'reqs', '--reqs', multiple=True,
    help='Path to a requirements file that packages will be additionally checked against',
)
def depchecker_cli(env_path, reqs):
    package_environment = get_package_environment(env_path, reqs)
    print()
    check_conflicts(package_environment)
    print()
    check_vulnerabilities(package_environment)


if __name__ == '__main__':
    depchecker_cli()
