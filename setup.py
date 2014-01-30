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
    license='MIT',
    scripts=['scripts/squadron'],
    tests_require=[
        'pytest>=2.5.1',
        'mock>=1.0.1'
        ],
    cmdclass = {'test': PyTest},
    install_requires=[
        'jsonschema>=2.3.0',
        'gitpython>=0.3.2.RC1',
        'quik>=0.2.2',
        'requests>=2.2.0',
        'py>=1.4.19']
)
