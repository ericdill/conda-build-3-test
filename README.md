# conda build 3 test

To figure out where conda-build 3 might have some issues, this repo contains
the (imperfect) results of running conda-build 3 on all recipes on conda-forge.
This is the "feedstocks" repo located [on
github](https://github.com/conda-forge/feedstocks).

## What's in this repo

- ``build-feedstocks.py``: Python script that will build feedstocks. It times
  how long it takes to build each recipe using a "-1" sentinel for recipes that
  fail to build. The stack trace from those recipes is captured in the "err"
  directory in this repo
- ``err/*``: The stack traces that were raised within conda-build that caused a
  recipe to fail. Each file in this folder is the name of the recipe that
  failed to build
- ``package_build.txt``: Text log where each line is a comment that says when
  an execution began or a line that contains the path to the recipe that was
  build and the time it took to build that recipe, separated by a comma. -1 is
  used a sentinel to indicate that the recipe failed to build

## System information

The system that was used to build these recipes has the following hardware:

- Intel Xeon E5-2695
- Ubuntu 14.04.5 LTS
- conda 4.3.22
- conda-build 3.0.6
- gcc 4.8.4
- Python 3.6.1

