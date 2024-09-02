#!/usr/bin/env bash

PYTHON_FILES=$(find "." -type f -name "*.py" -printf "%p ")
isort $(echo $PYTHON_FILES);
black $(echo $PYTHON_FILES);
flake8 $(echo $PYTHON_FILES);
