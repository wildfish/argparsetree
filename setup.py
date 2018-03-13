import os
import re
import shutil
import sys
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
        return readme.read()


def get_version():
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(os.path.dirname(__file__), 'argparsetree', '__init__.py')) as init_py:
        return re.search('__version__ = [\'"]([^\'"]+)[\'"]', init_py.read()).group(1)


version = get_version()

if sys.argv[-1] == 'publish':
    if os.system('pip freeze | grep wheel'):
        print('wheel not installed.\nUse `pip install wheel`.\nExiting.')
        sys.exit()
    if os.system('pip freeze | grep twine'):
        print('twine not installed.\nUse `pip install twine`.\nExiting.')
        sys.exit()
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    print('You probably want to also tag the version now:')
    print('  git tag -a {v} -m \'version {v}\''.format(v=version))
    print('  git push --tags')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('argparsetree.egg-info')
    sys.exit()

setup(
    name='argparsetree',
    version=version,
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    package_data={
        '': [
            'requirements-package.in',
            'LICENSE',
        ],
    },
    exclude_package_data={
        '': ['__pycache__', '*.py[co]'],
    },
    license='MIT',
    description='Package for creating complex command line argument trees using argparse',
    long_description=get_readme(),
    url='https://github.com/wildfish/argparsetree',
    author='Wildfish',
    author_email='developers@wildfish.com',
    keywords='class based argparse',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
