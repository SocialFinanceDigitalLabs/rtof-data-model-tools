---
layout: default
---

The following categorical lists are referenced throughout the specification.

{% for r in site.data.dimensions %}
  * [{{r.id}}]({{ '/dimensions/' | append: r.id | relative_url  }})
{% endfor %}
