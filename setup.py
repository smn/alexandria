from setuptools import setup, find_packages

setup(
    name = "smn-alexandria",
    version = "0.1",
    url = 'http://github.com/smn/alexandria',
    license = 'BSD',
    description = "A DSL for interactive, linear, text based menus.",
    author = 'Simon de Haan',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'generator_tools'],
)

