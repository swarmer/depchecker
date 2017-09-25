import os
import glob

import pkg_resources
import six


class InvalidEnvironmentError(Exception):
    pass


class InvalidRequirementsListError(Exception):
    pass


@six.python_2_unicode_compatible
class RequirementList(object):
    def __init__(self, path, requirements):
        self.path = path
        self.requirements = requirements

    def requires(self):
        return self.requirements[:]

    def __str__(self):
        return self.path

    @classmethod
    def load(cls, path):
        try:
            with open(path) as reqs_file:
                requirements = []

                for line in reqs_file:
                    try:
                        requirements.append(pkg_resources.Requirement.parse(line))
                    except Exception as exc:
                        # TODO: find a better parser
                        # pkg_resources can't handle everything pip can
                        pass

            return cls(path, requirements)
        except Exception as exc:
            print(exc)
            six.raise_from(
                InvalidRequirementsListError('cannot load requirements from %s' % path),
                exc,
            )


class PackageEnvironment(object):
    def __init__(self, env_path=None, requirements_paths=None):
        self._working_set = self._get_working_set(env_path or None)
        self._requirements_lists = [
            RequirementList.load(path)
            for path in (requirements_paths or [])
        ]

    @property
    def package_search_paths(self):
        return self._working_set.entries[:]

    @property
    def packages(self):
        return list(self._working_set)

    @property
    def requirements_sources(self):
        return self.packages + self._requirements_lists[:]

    @classmethod
    def _get_working_set(cls, env_path):
        if env_path:
            site_packages_paths = cls._find_site_packages(env_path)
            if not site_packages_paths:
                raise InvalidEnvironmentError('cannot find site-packages in %s' % env_path)

            return pkg_resources.WorkingSet(entries=site_packages_paths)
        else:
            return pkg_resources.working_set

    @staticmethod
    def _find_site_packages(env_path):
        patterns = [
            'site-packages/',
            '*/site-packages/',
            '*/*/site-packages/',
        ]

        result = []
        for pattern in patterns:
            result.extend(glob.glob(os.path.join(env_path, pattern)))

        return result
