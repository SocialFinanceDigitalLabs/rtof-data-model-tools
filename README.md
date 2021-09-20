# Data Model Tools for the Refugee Transitions Outcomes Fund (RTOF)

This is the source repository for the RTOF data model tools for generating different outputs from the
[core specification][rtof-spec].

There are a number of different modules involved with parsing and validating the specification,
compiling the documentation website and associated outputs, creating sample data and file validators.

The tools are mostly written in Python, and the [website][rtof-web] is powered by [Jekyll][jekyll]
and [GitHub Pages][ghp].

## Python Documentation Generators

The documentation generator uses [Poetry][poetry] for dependency management. Make sure you have poetry installed,
then install the project dependencies:

```shell
poetry install
```

Once installed, you can either run the generator from the command line by typing:

```shell
poetry run python main.py
```

or you can launch VS Code with:

```shell
poetry shell
code .
```

## Unit Tests

Unit tests can be found in [/test](./tests) and can be run from the project root with

```shell
poetry run python -m unittest discover 
```

Individual tests can also be run by specifying the module:

```shell
 poetry run python -m unittest tests.test_stream_insert
```

## Linting

To check your codestyle, run:

```shell
poetry run flake8
```

### ERD output

The [Entity Relationship Diagram (ERD)][erd] generator ([erd.py](./rtofdata/erd.py)) uses [Graphviz][graphviz]
to produce an ERD showing the relationships between the records.


### Word output

The [word output module](./rtofdata/word.py) uses [docxtpl][docxtpl] to provide a Word version of the
specification, including the ERD.

### Excel output

Whilst the Word documentation is intended for human consumption, the [excel version](./rtofdata/excel.py)
is better for importing
categories into a CMS. Simply using [openpyxl][https://openpyxl.readthedocs.io/en/stable/] to create tables for
import into other data systems.

### Jekyll output

Finally, the [Jekyll][jekyll] [output module](./rtofdata/jekyll.py) generates a set of Jekyll pages
to produce the website. The Jekyll configuration can be found in [website](./website).

## Transfer formats

So far this documentation has discussed the "core" data model but not really discussed representation and
information exchange. To make the transfer of data from providers to the central reporting function as streamlined
as possible, provide a number of transfer formats that can be used for upload and reporting. 

The most commonly used data interchange formats in this sector are Excel (xlsx), CSV, JSON and XML. Excel and CSV
are tabular formats, whilst JSON and XML are hierarchical. We will therefore focus on these two abstract 
representations.

The core datamodel is relational but does include many-to-one relationships that are not easily represented in 
pure tabular formats without either duplicating rows or columns. 

So for tabular formats, records may be provided either one-by-one (separate file / worksheet for each type) or as a
long format. All column names are unique, so if column names from multiple record types appear in the same file, 
then all records will be added / updated. Omitted records will retain their previous values if they already existed. 

For many-to-one relationship, columns can contain a suffix, e.g. `integration_outcome_type_1`. All columns
belonging to that record must have the same suffix, i.e.:

* integration_outcome_type_1
* integration_outcome_achieved_date_1

etc. 

Alternatively, multiple rows can be provided, one for each record. 


[rtof-spec]: https://github.com/SocialFinanceDigitalLabs/rtof-data-model
[rtof-tools]: https://github.com/SocialFinanceDigitalLabs/rtof-data-model-tools
[rtof-web]: https://sfdl.org.uk/RTOF-specification/

[poetry]: https://python-poetry.org/
[yaml]: https://yaml.org/
[vcs]: https://en.wikipedia.org/wiki/Version_control
[git]: https://git-scm.com/
[jsc]: https://json-schema.org/
[csc]: https://digital-preservation.github.io/csv-schema/
[ssot]: https://en.wikipedia.org/wiki/Single_source_of_truth
[erd]: https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model
[graphviz]: http://www.graphviz.org/
[docxtpl]: https://docxtpl.readthedocs.io/en/latest/
[jekyll]: https://jekyllrb.com/
[gha]: https://github.com/features/actions
[ghp]: https://pages.github.com/
