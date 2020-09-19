#!/usr/bin/env python
from setuptools import find_packages, setup
packages = find_packages()

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "2.1.1"
setup(name='bqmail',
      version=VERSION,
      author='Mijian Xu',
      author_email='gomijianxu@gmail.com',
      url='https://github.com/xumi1993/bqmail',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=find_packages(),
      package_dir={'bqmail': 'bqmail'},
      package_data={'': ['data/*']},
      install_requires=['obspy', 'pandas'],
      entry_points={'console_scripts': ['get_stations=bqmail.query:get_stations',
                                        'get_events=bqmail.query:get_events']},
      include_package_data=True,
      zip_safe=False,
      classifiers=['Programming Language :: Python',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8']
      )
