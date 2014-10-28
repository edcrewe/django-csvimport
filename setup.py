import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '2.2'

with open("README.rst", "r") as fp:
    csvimport_description = fp.read() + "\n" 
for fname in ("TODO.txt", "HISTORY.txt"):
    with open(os.path.join("docs", fname), "r") as fp:
        csvimport_description += fp.read() + "\n" 

setup(name='django-csvimport',
      version=version,
      description="Import CSV files to django models",
      long_description=csvimport_description,
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
      packages=['csvimport', ],
      include_package_data=True,
      namespace_packages=['csvimport', ],
      package_data = {
        # If any package contains *.csv or *.rst files, include them: 
        '': ['*.csv', '*.rst'],
      },
      zip_safe=False,
      install_requires=[
          'django>=1.7',
          'chardet',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
