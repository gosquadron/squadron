from setuptools.command.test import test as TestCommand
import sys
import os

#Class that spins up various vagrant instances
#If this gets too large we'll move it out
class FullTestPass(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
    def run(self):
        import vagrant
        import pysftp
        #Figure out how to properly install this
        #Options: pip requires file, or test_requires below
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_dir = os.path.join(current_dir,"ftp")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        print 'creating dir'
        v = vagrant.Vagrant(test_dir)
        print 'turning on'
        v.up(vm_name='avm')
        config_raw = v.ssh_config(vm_name='avm')
        print config_raw
        config = v.conf(vm_name='avm')
        
        srv = pysftp.Connection(host=config['HostName'], username=config['User'],
                port=int(config['Port']), private_key=config['IdentityFile'])
        print srv.execute('ls -al')
        srv.close
        print 'shutting down'
       # v.halt(vm_name='avm')

        pass

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
setup(
    name='squadron',
    version='0.1.1',
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
    cmdclass = {'test': PyTest, 'ftp': FullTestPass},
    install_requires=[
        'jsonschema>=2.3.0',
        'gitpython>=0.3.2.RC1',
        'quik>=0.2.2',
        'requests>=2.2.0',
        'py>=1.4.19']
)
