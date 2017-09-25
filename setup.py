import codecs
import os
import re

from setuptools import find_packages, setup


# utility functions
def slurp(path):
    with codecs.open(path, 'rb', 'utf-8') as f:
        return f.read()


def find_meta(field):
    meta_match = re.search(
        r'^__{field}__ = [\'"]([^\'"]*)[\'"]'.format(field=field),
        META_FILE,
        re.M,
    )

    if not meta_match:
        raise RuntimeError('Unable to find __{field}__ string.'.format(field=field))

    return meta_match.group(1)


# utility constants
HERE = os.path.abspath(os.path.dirname(__file__))
META_FILE = slurp(os.path.join(HERE, 'src', 'depchecker', '__init__.py'))


# metadata
NAME = 'depchecker'

AUTHOR = 'swarmer'
AUTHOR_EMAIL = 'anton@swarmer.me'
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Programming Language :: Python',
    'Topic :: Software Development',
]
DESCRIPTION = 'A tool that checks python project dependencies'
INSTALL_REQUIRES = [
    'click>=6.7,<7.0',
    'requests>=2.18,<3.0',
    'six>=1.11,<2.0',
]
KEYWORDS = ['dependency', 'package', 'vulnerability', 'requirements']
LICENSE = 'MIT'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
PACKAGES = find_packages(where='src')
URL = 'https://github.com/swarmer/depchecker'
VERSION = find_meta('version')


if __name__ == '__main__':
    setup(
        name=NAME,

        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        classifiers=CLASSIFIERS,
        description=DESCRIPTION,
        install_requires=INSTALL_REQUIRES,
        keywords=KEYWORDS,
        license=LICENSE,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        package_dir={'': 'src'},
        packages=PACKAGES,
        url=URL,
        version=VERSION,

        zip_safe=False,
    )
