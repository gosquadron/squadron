from setuptools.command.test import test as TestCommand
import sys
import os

#Runs unit tests
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

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from setuptools import setup, find_packages
import squadron
setup(
    name='squadron',
    version=squadron.__version__,
    author='Squadron',
    author_email='info@gosquadron.com',
    description='Easy-to-use configuration and release management tool',
    long_description=read('README.md'),
    license='MIT',
    url='http://www.gosquadron.com',
    keywords='configuration management release deployment tool',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
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
        'py>=1.4.19',
        'simplejson>=0']
)
