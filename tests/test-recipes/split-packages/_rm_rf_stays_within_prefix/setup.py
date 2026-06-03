from os.path import join

from setuptools import setup

setup(name='lsfm',
      version="1.0",
      py_modules=['lsfm'],
      scripts=[join('bin', 'lsfm')],
      )
