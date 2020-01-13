.. TraceClustering documentation master file, created by
   sphinx-quickstart on Fri Jan 10 13:24:19 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TraceClustering's documentation!
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The basis for this project is the method to cluster the traces of an event log proposed by X. Lu. et. al (Trace Clustering on Very Large Event Data in Healthcare Using Frequent Sequence Patterns,
https://arxiv.org/abs/2001.03411) which makes use of frequent sequence patterns discovered in a small set of traces given by an expert. The backend of this project provides an implementation of said method, while the frontend
serves a web application to upload and event log in xes format and the sample list in csv format and upon receiving certain parameters by the user, outputs a clustered log and displays quality measures.
For the mining of closed frequent sequence patterns specifically, the CloFAST algorithm is implemented (https://www.researchgate.net/publication/283534315_CloFAST_closed_sequential_pattern_mining_using_sparse_and_vertical_id-lists).

To search for modules, use the module index below. The main module combines most of the functionality of the backend and is as such the interface to the frontend. The core funtionality for clustering the log can be found in the cluster module.
Moreover, the sequence_mining package for mining specific sets of frequent sequence patterns is self-contained, but depends on the fact that sequences arise from traces of an event log which means item sets of a sequence are always of size 1.
The frontend implementation is in the FlaskImpl package.

To keep the documentation concise, only small examples for the most important functions are included in this document. Please consult the tests folder of the project to see full example usage for the backend. Information on how to operate the front end is found in the user manual.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
