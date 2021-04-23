
Explaining graph-based classifiers (XpG)
=======================================

**XpG** is a Python3 package for explaining graph-based classifiers:

- `Binary decision diagrams <https://en.wikipedia.org/wiki/Binary_decision_diagram>`__ (BDDs).
- `Multi-valued decision diagrams <http://dx.doi.org/10.1109/ICCAD.1990.129849>`__ (MDDs).
- `Decision Tree <https://en.wikipedia.org/wiki/Decision_tree>`__ (DTs).
- `Decision Graph <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.52.1476&rep=rep1&type=pdf>`__ (DGs).

Features:

- Computing one Abductive Explanation (AXp) [1]_ of XpG's.
- Computing one Contrastive Explanation (CXp) [2]_ of XpG's.
- Enumerating all AXps and CXps with `MARCO <https://link.springer.com/article/10.1007%2Fs10601-015-9183-0>`__ algorithm [3]_.

Getting Started
---------------

Before using XpG, make sure you have the following Python packages installed:

- `networkx <https://networkx.org/>`__
- `numpy <https://numpy.org/>`__
- `PySAT <https://pysathq.github.io/>`__

Installation
************
From the `Python Package Index (PyPI) <https://pypi.org>`__ using the package installer ``pip``:
::
   pip install XpGraph

Localy, clone the xpg repository and install it using: 
::
   pip install -e <local project path>

Usage
-----
To see the list of options, run:
::

   $ Xpg.py -h


To find one AXp, run with option ``-x 'AXp'`` (option ``-v`` increases verbosity.):  
::

  $ XpG.py -v -v -x 'AXp' xpg-file

To find one CXp, run with option ``-x 'CXp'``:
::

  $ XpG.py -v -v -x 'CXp' xpg-file

To list all AXps and CXps, run with option ``-a``:
::

  $ XpG.py -v -v -a xpg-file

Input file format (.xpg)
***************
To use XpG scripts to explain graph-based classifiers,
you need to transform the classifiers at hand to a .xpg file.
The transformation can be achieved via graph traversal algorithm.

The format of .xpg file is as follow:
::

  ########### Author: Joao Marques-Silva ###########

  XpG FORMAT:

  NN: <number-nodes>
  Root: <1>
  T: <terminal-node-ids>
  TDef:
  [<node-id> <0|1>]+
  NT: <non-terminal-node-ids>
  NTDef:
  [<parent-id> <child-id> <0|1>]+
  NV: <num-vars>
  VarDef:
  [<node-id> <var>]+


  NOTES:
  - There can be empty lines or lines starting with '#' for comments
  - The root node is 1 by default; this can be changed
  - Nodes or edges marked 1 are "active"
  - Nodes or edges marked 0 are "inactive"
  - There exists exactly one terminal node marked 1 that is connected to
    the root by one or more paths of edges with value 1
  - For every terminal node marked 0, there is not path of edges with
    value 1 connecting that terminal node to the root node
  - For the edges leaving a non-terminal node, exactly one is marked with
    1; all others are marked 0


Be aware that when parsing `VarDef`, for each ``var`` in ``[<node-id> <var>]`` pair, 
we assign a variable index (starting from 0) for each ``var``.
If you compute explanation with only one ``-v`` option, the printed explanation
maybe difficult to understand.

Usage examples
****************
.xpg file sample:
::

  # comment:
  # features: [A0,A1,B0,B1,Irrelevant,Correlated]
  # instance: [0,0,0,0,0,0]

  NN: 7
  Root: 1
  T: 4 7
  TDef:
  4 1
  7 0
  NT: 1 2 3 5 6
  NTDef:
  1 2 1
  1 3 0
  2 4 1
  2 5 0
  3 6 1
  3 7 0
  5 4 1
  5 7 0
  6 4 1
  6 7 0
  NV: 4
  VarDef:
  1 A0
  2 B0
  3 A1
  5 B1
  6 B0
  
For this sample file, running the following command
::
  $ XpG.py -v -v -x 'AXp' examples/corral/corral_0.xpg

will output:
::
  load XpG from  examples/corral/corral_0.xpg
  find an AXp ...
  Encode XpGraph into Horn formulas ...
  AXp: [1, 2] (['B0', 'A1'])
  Runtime: 0.000

where ``['B0', 'A1']`` is the explanation and ``[1, 2]`` is the explanation represented as variable index.

To list all AXps and CXps, the command
::
  $ XpG.py -v -v -a examples/corral/corral_0.xpg

will print:
::
  load XpG from  examples/corral/corral_0.xpg
  list all XPs ...
  AXp: [1, 2] (['B0', 'A1'])
  Runtime: 0.000
  AXp: [0, 3] (['A0', 'B1'])
  Runtime: 0.000
  CXp: [1, 3] (['B0', 'B1'])
  Runtime: 0.000
  CXp: [0, 1] (['A0', 'B0'])
  Runtime: 0.000
  AXp: [0, 1] (['A0', 'B0'])
  Runtime: 0.000
  CXp: [0, 2] (['A0', 'A1'])
  Runtime: 0.000

  Num of AXp: 3
  Num of CXp: 3
  Total Explanation: 6
  Runtime: 0.001


Citation
--------

Please cite the following paper when you use this work:
::
  @article{hiims-corr21,
  author    = {Xuanxiang Huang and
               Yacine Izza and
               Alexey Ignatiev and
               Jo{\~{a}}o Marques{-}Silva},
  title     = {On Efficiently Explaining Graph-Based Classifiers},
  journal   = {CoRR}
  }


.. [1] Alexey Ignatiev, Nina Narodytska, Joao Marques-Silva.
      *Abduction-Based Explanations for Machine Learning Models*. AAAI 2019.
      
.. [2] Alexey Ignatiev, Nina Narodytska, Nicholas Asher, Joao Marques-Silva. 
  *From Contrastive to Abductive Explanations and Back Again*. AI*IA 2020.
  
.. [3] Mark H. Liffiton, Alessandro Previti, Ammar Malik, Joao Marques-Silva.
    *Fast, flexible MUS enumeration*. Constraints An Int. J. 2016.


License
-------
This project is licensed under the `GPL <https://www.gnu.org/licenses/gpl-3.0.en.html>`__ License, see file LICENCE
