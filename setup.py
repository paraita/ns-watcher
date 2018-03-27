#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='nswatcher',
      version='0.1',
      description="Simplifies the add and removal of nodesources to ProActive's Resource Manager",
      url='http://github.com/paraita/ns-watcher',
      author='Paraita Wohler',
      author_email='paraita.wohler@gmail.com',
      license='MIT',
      packages=['nswatcher'],
      setup_requires=['pytest-runner'],
      install_requires=[
          'argh',
          'pathtools',
          'PyYAML',
          'watchdog'
      ],
      test_suite='nose.collector',
      tests_require=[
          'mock',
          'pytest',
          'coverage',
          'coveralls'
      ],
      zip_safe=False)
