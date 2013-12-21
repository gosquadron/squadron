from setuptools import setup, find_packages
setup(
    name='squadron',
    version='0.0.1',
    packages=find_packages(),
    license='Proprietary',
    scripts=['scripts/squadron'],
    data_files=[('/etc/squadron',['files/config']),
                ('/var/squadron',['files/info.json'])],
    install_requires=['jsonschema','gitpython','quik','requests']
)
