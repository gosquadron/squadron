from setuptools import setup, find_packages
setup(
    name='squadron',
    version='0.0.1',
    packages=find_packages(),
    license='Proprietary',
    scripts=['scripts/squadron'],
    data_files=[('/etc/squadron',['files/config'])],
    install_requires=['jsonschema','gitpython','quik']
)

#hopefully its been installed now
from git import *
import os
from distutils.sysconfig import get_python_lib
root_dir = os.path.join(get_python_lib(), "squadron")
if not (os.path.exists(root_dir)):
    print "Squadron did not install in site-packages :("
    exit(1)

community_dir = os.path.join(root_dir, "community")
if not (os.path.exists(community_dir)):
    #install only if it already doesn't exist (from previous install)
    Repo.clone_from("https://github.com/guscatalano/squadron-init.git", community_dir)
