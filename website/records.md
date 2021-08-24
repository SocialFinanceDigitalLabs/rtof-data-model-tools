---
layout: default
---

Records are the top-level entities of the RTOF data specification and correspond to tables in relational databases.

Records capture information about a specific step in the programme flow and contains essential information for the outcomes validation and payment metrics.

{% for r in site.data.records %}
  * [{{r.id}}]({{ '/records/' | append: r.id | relative_url  }})
{% endfor %}

{% include dynamic/record-relationships.svg %}
