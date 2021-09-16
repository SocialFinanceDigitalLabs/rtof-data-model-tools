---
layout: default
---
# Introduction

This document outlines the Refugee Outcomes Transition Fund (RTOF) Data Specification.

The document outlines the data fields, types, and descriptions for all required data collection during the lifetime of the Refugee Transition Outcome Fund. The description for each field outlines the context, collection frequency and milestone at which it should be collected.

The validation rules that apply are noted under 'validators' for each record. These will be applied on submission of data, if any validation rules are not met, a validation report will be produced with details of the fields and specified errors for the given fields. The images below outline the key milestones and data collection points during the program.

# Data Submissions

Within each record page on this site we have included sample data, providing an example of how data submissions should look. 

The RTOF datamodel is relational but does include many-to-one relationships that are not easily represented 
in pure tabular formats without either duplicating rows or columns. For more information on how to represent 
these, as well as more detailed examples of all the submission formats, see the 
[samples page]({{ '/datasamples' | relative_url }}).

![Diagram explaining the different data collections periods and submission frequency][periods]

![Forms][forms]

You can also download the [Word specification]({{ '/assets/spec/specification.docx' | relative_url }}) and
[list of categories]({{ '/assets/spec/specification-dimensions.xlsx' | relative_url }}) in Excel.

[periods]: {{ "assets/src/submission_and_collection.png" | relative_url }}
[forms]: {{ "assets/src/RTOF_program_path.png" | relative_url }}