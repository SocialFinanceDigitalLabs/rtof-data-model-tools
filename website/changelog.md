---
layout: default
title: Changelog
---

|Date  | Version | Message  |
|---|---|
{% for t in site.data.git.git_tagrefs -%}
| {{ t.date | date_to_long_string }} | [{{ t.tag }}][{{ t.tag }}] | {{ t.message | strip }} |
{% endfor %}

{% for t in site.data.git.git_tagrefs -%}
[{{ t.tag }}]: https://github.com/SocialFinanceDigitalLabs/rtof-data-model/releases/tag/{{ t.tag }}
{% endfor %}
