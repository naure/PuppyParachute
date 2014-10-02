#!/usr/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup

setup(
    name='PuppyParachute',
    version='0.1',
    description='Puppy Parachute tests',
    author='Aurélien Nicolas',
    author_email='au@nau.re',
    url='https://github.com/naure/PuppyParachute',
    packages=['puppyparachute'],
    scripts=['annotate.yp', 'deannotate.yp'],
    entry_points={
         'nose.plugins.0.10': [
            'puppy = puppyparachute.puppynose:PuppyParachute'
         ]
    },
)
