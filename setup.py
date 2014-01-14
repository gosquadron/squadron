from setuptools.command.test import test as TestCommand
import sys

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

from setuptools import setup, find_packages
setup(
    name='squadron',
    version='0.0.1',
    packages=find_packages(),
    license='Proprietary',
    scripts=['scripts/squadron'],
    data_files=[('/etc/squadron',['files/config']),
                ('/var/squadron',['files/info.json'])],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
    install_requires=['jsonschema','gitpython','quik','requests', 'py', 'urllib3']
)
