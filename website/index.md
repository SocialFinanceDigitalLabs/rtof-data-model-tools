---
layout: default
---

This document outlines the Refugee Outcomes Transition Fund (RTOF) Data Specification.

The document outlines the data fields, types, and descriptions for all required data collection during the lifetime of the Refugee Transition Outcome Fund. The description for each field outlines the context, collection frequency and milestone at which it should be collected.

The validation rules that apply for each field are noted in the grey tables for each record. These will be applied on submission of data, if any validation rules are not met, a report will be produced with details of the fields and specified errors for the given fields.  The images below outline the key milestones and data collection points during the program.

# Data Submissions

Within each record page on this site we have included sample data, providing an example of how data submissions should look. We will update this webpage with an additional tab, titled "Sample Submissions" which will provide mulitple downloadable links to sample data in excel - including both examples described below.      

The RTOF datamodel is relational but does include many-to-one relationships that are not easily represented in pure tabular formats without either duplicating rows or columns.

So for tabular formats, records may be provided either one-by-one (separate file / worksheet for each type) or as a long format. All column names are unique, so if column names from multiple record types appear in the same file, then all records will be added / updated. Omitted records will retain their previous values if they already existed.

For many-to-one relationship, columns can contain a suffix, e.g. integration_outcome_type_1. All columns belonging to that record must have the same suffix, i.e.:

*integration_outcome_type_1
*integration_outcome_achieved_date_1
etc.

Alternatively, multiple rows can be provided, one for each record.

![Diagram explaining the different data collections periods and submission frequency][periods]

![Forms][forms]

You can also download the [Word specification]({{ '/assets/spec/specification.docx' | relative_url }}) and
[list of categories]({{ '/assets/spec/specification-dimensions.xlsx' | relative_url }}) in Excel.

[periods]: {{ "assets/src/submission_and_collection.png" | relative_url }}
[forms]: {{ "assets/src/RTOF_program_path.png" | relative_url }}