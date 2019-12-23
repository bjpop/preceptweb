#!/usr/bin/env python

from distutils.core import setup

LONG_DESCRIPTION = \
'''Generate the PRECEPT website'''


setup(
    name='preceptweb',
    version='0.1.0.0',
    author='Bernie Pope',
    author_email='bjpope@unimelb.edu.au',
    packages=['preceptweb'],
    package_dir={'preceptweb': 'preceptweb'},
    entry_points={
        'console_scripts': ['preceptweb = preceptweb.main:main']
    },
    url='https://github.com/bjpop/preceptweb',
    license='LICENSE',
    description=('Generate the PRECEPT website'),
    long_description=(LONG_DESCRIPTION),
    install_requires=["jinja2>=2.10.1", "pyyaml"],
)
