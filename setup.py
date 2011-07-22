from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='django-csvimport',
      version=version,
      description="Import CSV files to django models",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='CVS import django fixture',
      author='Ed Crewe',
      author_email='edmundcrewe@gmail.com',
      url='https://github.com/TomDunham/helios-iis',
      license='Apache',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['csvimport'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
