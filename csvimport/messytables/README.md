# Original Code from Open Knowledge Labs MessyTables

A library for dealing with messy tabular data in several formats, guessing types and detecting headers.

See the documentation at: https://messytables.readthedocs.io

Find the package at: https://pypi.python.org/pypi/messytables

**Contact**: Open Knowledge Labs - http://okfnlabs.org/contact/. We especially recommend the forum: http://discuss.okfn.org/category/open-knowledge-labs/

## Why copy messytable core code into csvimport?

Open Knowledge Foundation have stopped maintaining messytables having replaced it with qsv (in Rust)
see:

https://github.com/dathere/datapusher-plus

Hence it no longer works with latest Python 3.12

To retain this simple type guesstimation for model generation in csvimport with latest Python and Django 5, the two core files required from messytables are moved here, with a tweak to make it just use the simple self.csvfile type for rows = [[value, value], [value, value]] that is all that type_quess needs.

Note this means it no longer opens the csvfile again with messytables, and it no longer only uses a sample set of rows, but instead uses all rows. So if the CSV file is very large, inspectcsv may take a long time.
In which case it may be better to just chop out the first few thousand lines as a manual sample file used for generating the Django model.

This removes messytables as a separate dependency.

Thanks to the Open Knowledge Foundation, and all rights reserved by them, for this messytables subfolder.

- Ed Crewe, Dec 2023
