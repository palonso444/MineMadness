# This is the setup file necessary to build the cythonised_lights module

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        name="cythonized_lights",
        sources=["cythonized_lights.pyx"],
        include_dirs=[numpy.get_include()]
    )
]

setup(
    ext_modules=cythonize(extensions, language_level=3)
)