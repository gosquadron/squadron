from distutils.core import setup
import better

setup(
    name='sphinx-better-theme',
    version=better.__version__,
    author='Steve Johnson',
    author_email='steve@steveasleep.com',
    packages=['better'],
    package_data={
        'better': [
            '*.html',
            '*.conf',
            'static/*.css_t'
        ]
    },
    url='http://github.com/irskep/sphinx-better-theme',
    license='LICENSE',
    description='A nice-looking, customizable Sphinx theme',
    long_description=open('Readme.rst').read(),
)
