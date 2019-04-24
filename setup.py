import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "2.12"

with open("README.rst", "r") as fp:
    csvimport_description = fp.read() + "\n"
for fname in ("TODO.txt", "HISTORY.txt"):
    with open(os.path.join("docs", fname), "r") as fp:
        csvimport_description += fp.read() + "\n"

setup(
    name="django-csvimport",
    version=version,
    description="Import CSV files to django models",
    long_description=csvimport_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="CVS import django fixture",
    author="Ed Crewe",
    author_email="edmundcrewe@gmail.com",
    url="https://github.com/edcrewe/django-csvimport",
    license="Apache",
    packages=["csvimport"],
    include_package_data=True,
    namespace_packages=["csvimport"],
    # this line always breaks install?
    # package_data = {'csvimport': ['*.csv', '*.rst']},
    zip_safe=False,
    install_requires=["django>=1.7", "chardet"],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
