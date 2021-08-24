---
layout: default
title: Datatypes
---

|Type  | Description  |
|---|---|
{% for r in site.data.datatypes -%}
| {{r.id}} | {{ r.description }} |
{% endfor %}
