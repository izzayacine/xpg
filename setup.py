#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## setup.py
##
##  Created on: April 04, 2021
##      Author: Xuanxiang Huang, Yacine Izza, Alexey Ignatiev, Joao Marques-Silva
##      E-mail: xuanxiang.huang.cs@outlook.com, yacine.izza@gmail.com
##

#
#==============================================================================
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension



#
#==============================================================================
LONG_DESCRIPTION = """
**XpGraph** is a Python3 package for explaining graph-based classifiers:
Binary decision diagrams (BDDs), Multi-valued decision diagrams (MDDs), 
Decision Tree (DTs), Decision Graph (DGs). 
Additionally, it contains an executable `XpG.py`, which can be applied 
for computing one Abductive explanation (`AXp`, or PI-explanation), one Contrastive
explanation (`CXp`) or enumerating all explanations (AXps and CXps) of a given 
`.xpg` file input.

Details can be found at [https://github.com/yizza91/xpg](https://github.com/yizza91/xpg)

"""


# finally, calling standard setuptools.setup() (or distutils.core.setup())
#==============================================================================
setup(name='XpGraph',
    packages=['xpg'],
    package_dir={},
    version='0.0.1',
    description='Explaining Graph-based Classifiers',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown; charset=UTF-8',
    license='GPL',
    author='Xuanxiang Huang, Yacine Izza, Alexey Ignatiev, Joao Marques-Silva',
    author_email='yacine.izza@gmail.com',
    url='https://github.com/yizza91/xpg',
    ext_modules=[],
    scripts=['XpG.py'],
    cmdclass={},
    install_requires=['networkx', 'numpy', 'python-sat'],
    extras_require = {}
)