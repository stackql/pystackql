# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pystackql',
    version='v3.8.0',
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
        'psycopg[binary]>=3.1.0',  # Added psycopg with binary wheels for all platforms
        'nest-asyncio>=1.5.5',      # For async support in Jupyter
        'termcolor>=1.1.0',         # For colored output in test runner
        'tqdm>=4.61.0',             # For progress bars in download method
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
