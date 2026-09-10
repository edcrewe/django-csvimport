import os

from setuptools import find_packages, setup

version = "3.3"

with open("README.rst", "r") as fp:
    csvimport_description = fp.read() + "\n"
for fname in ("HISTORY.txt",):
    with open(os.path.join("docs", fname), "r") as fp:
        csvimport_description += fp.read() + "\n"

setup(
    name="django-csvimport",
    version=version,
    description="Import CSV files to django models",
    long_description_content_type="text/x-rst",
    long_description=csvimport_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="CVS import django fixture",
    author="Ed Crewe",
    author_email="edmundcrewe@gmail.com",
    url="https://github.com/edcrewe/django-csvimport",
    license="Apache",
    packages=find_packages(),
    package_data={
        "csvimport.messytables": ["README.md"],
        "csvimport.tests": ["README.txt", "fixtures/*.csv"],
    },
    # this line always breaks install?
    # package_data = {'csvimport': ['*.csv', '*.rst']},
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=["django>=4.2", "chardet", "dateparser"],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
