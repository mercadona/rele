#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

from setuptools import setup, find_packages


def get_version(*file_paths):
    """Retrieves the version from rele/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version('rele', '__init__.py')


if sys.argv[-1] == 'tag':
    print('Tagging the version on git: %s' % version)
    os.system('git tag -a %s -m "version %s"' % (version, version))
    os.system('git push --tags')
    sys.exit()

readme = open('README.md').read()

setup(
    name='rele',
    version=version,
    description="""Relé makes integration with Google PubSub easier.""",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='MercadonaTech',
    author_email='software.online@mercadona.es',
    url='https://github.com/mercadona/rele',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=['django', 'djangorestframework', 'google-cloud-pubsub'],
    license='Apache Software License 2.0',
    zip_safe=False,
    keywords='rele',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
