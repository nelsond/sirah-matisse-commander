from setuptools import setup
import os
from sirah_matisse_commander import __version__

current_path = os.path.dirname(os.path.abspath(__file__))

# Get the long description from the README file
with open(os.path.join(current_path, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(current_path, 'requirements', 'common.txt')) as f:
    required = f.read().splitlines()

setup(
    name='sirah-matisse-commander',

    version=__version__,

    description='Simple client for the Sirah Matisse Commander TCP server.',
    long_description=long_description,

    url='https://gitlab.physik.uni-muenchen.de/sqm/devices/'
        'sirah_matisse_commander',

    author='Nelson Darkwah Oppong',
    author_email='n@darkwahoppong.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6'
    ],

    keywords='sirah matisse commander',

    packages=['sirah_matisse_commander'],

    install_requires=required
)
