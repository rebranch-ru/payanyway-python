from os.path import join, dirname

from setuptools import setup, find_packages


setup(
    name='payanyway',
    version=0.1,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='Rebranch',
    url='https://github.com/rebranch/payanyway_python',
)