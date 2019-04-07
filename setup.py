# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='DepGraph',
    version='0.1.0',
    description='Dependency Graph generator for multiple languages',
    long_description=readme,
    author='Thomas Lacroix',
    author_email='toto.rigolo@free.fr',
    url='https://github.com/totorigolo/DepGraph',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
