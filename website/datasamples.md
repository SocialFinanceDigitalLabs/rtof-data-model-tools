---
layout: default
title: Data Samples
---

# Submission Formats

We support a number of different formats to make data submission easier.

## Single record per CSV

In the "single record per CSV" format, each of the fields associated with a record and only these fields
are present in a CSV file. The files can be named as you like as the record type is derived from the 
column headers, but it is helpful to include the record type in the name:

| Filename |Description|
{% for r in site.data.records -%}
| [sample_record_{{r.id}}.csv][sr_{{r.id}}_csv] | Sample data for the [{{r.id}}][rec_{{r.id}}] record in a single CSV |
{% endfor %}

## Wide format

In the wide format, multiple records can be included in a single row all identified with a single `unique_id` column.
In this format, multiple records for the same person can be specified by using a column suffix.

By using a column suffix, several records for these "many-to-one" relationships can be included , 
e.g. `integration_outcome_type_1`, `integration_outcome_type_2`. 

All columns belonging to that record must have the same suffix, e.g.:

| unique_id | integration_outcome_type_1 | integration_outcome_achieved_date_1 | integration_outcome_type_2 | integration_outcome_achieved_date_2 |
| DP-14 | Creation | 2023-02-15 | | |
| ES-97 | Creation | 2022-11-06 | 6 month | 2023-08-26 |

Download [complete example]({{ '/assets/spec/samples/sample_wide.csv' | relative_url }}).

## Excel

Excel can be provided, either following the same principles as the CSV files, and in addition by providing multiple
records in separate worksheets. Each row in every worksheet must obviously have a `unique_id` linking them together.

Download [Excel example]({{ '/assets/spec/samples/sample.xlsx' | relative_url }}).

## SQLite

Finally, we don't support submissions this way, but if helpful there is also a 
[SQLite database file]({{ '/assets/spec/samples/sample.sqlite' | relative_url }}) which provides a useful view of what
the relational datamodel looks like.


{% for r in site.data.records %}
[sr_{{r.id}}_csv]: {{ '/assets/spec/samples/sample_record_' | append: r.id | append: '.csv' | relative_url }}
[rec_{{r.id}}]: {{ '/records/' | append: r.id | relative_url }}
{% endfor %}
