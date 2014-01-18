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

#Handle other dirs
default_conf_dir = '/etc/squadron'
default_tmp_dir = '/var/squadron'

if '--conf_dir' in sys.argv:
	#actually read it
	conf_dir = sys.argv[sys.argv.index('--conf_dir')+1]
	print conf_dir
	sys.argv.remove('--conf_dir')
	exit()

if '--tmp_dir' in sys.argv:
	#actually read it
	sys.argv.remove('--tmp_dir')

conf_dir = default_conf_dir
tmp_dir = default_tmp_dir

from setuptools import setup, find_packages
setup(
    name='squadron',
    version='0.0.1',
    packages=find_packages(),
    license='Proprietary',
    scripts=['scripts/squadron'],
    data_files=[(conf_dir,['files/config']),
                (tmp_dir,['files/info.json'])],
    tests_require=['pytest>=2.5.1'],
    cmdclass = {'test': PyTest},
    install_requires=[
        'jsonschema>=2.3.0',
        'gitpython>=0.3.2.RC1',
        'quik>=0.2.2',
        'requests>=2.2.0',
        'py>=1.4.19']
)
