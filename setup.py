from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='django-csvimport',
      version=version,
      description="Import CSV files to django models",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "TODO.rst")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: Apache Software License"
        ],
      keywords='CVS import django fixture',
      author='Ed Crewe',
      author_email='edmundcrewe@gmail.com',
      url='https://github.com/edcrewe/django-csvimport',
      license='Apache',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['csvimport'],
      include_package_data=True,
      package_data = {
        # If any package contains *.csv or *.rst files, include them:
        '': ['*.csv', '*.rst'],
      },
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'chardet'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
