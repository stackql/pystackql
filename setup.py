# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pystackql',
    version='v3.7.1',
    description='A Python interface for StackQL',
    long_description=readme,
    author='Jeffrey Aven',
    author_email='javen@stackql.io',
    url='https://github.com/stackql/pystackql',
    license=license,
    packages=['pystackql'],
    # include_package_data=True,
    install_requires=[
        'requests', 
        'pandas',
        'IPython',
        ],
    # entry_points={
    #     'console_scripts': [
    #         'stackql = pystackql:setup'
    #     ]
    # },
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
    ]
)
