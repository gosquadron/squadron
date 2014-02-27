from setuptools.command.test import test as TestCommand
import sys
import os

#Class that spins up various vagrant instances
#If this gets too large we'll move it out
class VMTestPass(TestCommand):
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
        config = v.conf(vm_name='avm')
        print "Connecting via SSH"
        srv = pysftp.Connection(host=config['HostName'], username=config['User'],
                port=int(config['Port']), private_key=config['IdentityFile'])
        print "Installing prerequisites"
        #This is going to be OS specific, for now assume its debian
        package = srv.execute('export DEBIAN_FRONTEND=noninteractive; sudo apt-get -q -y install git python python-pip')
        print "reclonening squadron git repo"
        clone = srv.execute('rm -rf squadron; git clone https://github.com/gosquadron/squadron.git')
        print "executing tests"
        out = srv.execute('cd squadron; python setup.py test > /vagrant/test.out')
        fresult = open(os.path.join(test_dir, 'test.out'), 'r')
        tests = fresult.read()
        fresult.close() 

        package = ', '.join(package).replace(', ', '')
        clone = ', '.join(clone).replace(', ', '')
        out = ', '.join(out).replace(', ', '')

        f = open('vmtest.output', 'w')
        f.write("{0}\n{1}\n{2}\n{3}".format(package, clone, tests, out))
        f.close()
        print "Output file: vmtest.output"
        srv.close
        print 'shutting down (disabled)'
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
    cmdclass = {'test': PyTest, 'vmtest': VMTestPass},
    install_requires=[
        'jsonschema>=2.3.0',
        'gitpython>=0.3.2.RC1',
        'quik>=0.2.2',
        'requests>=2.2.0',
        'py>=1.4.19']
)
