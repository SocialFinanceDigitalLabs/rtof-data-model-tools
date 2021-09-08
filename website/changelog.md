---
layout: default
title: Changelog
---

|Date  | Version | Message  |
|---|---|
{% for t in site.data.git.git_tagrefs -%}
| {{ t.date | date_to_long_string }} | [{{ t.tag }}][{{ t.tag }}] | {{ t.message | strip }} |
{% endfor %}

For detailed version history, see the full [GIT commit log][gitlog]. For changes to the published
documentation, see the [published specification changelog][speclog].



{% for t in site.data.git.git_tagrefs -%}
[{{ t.tag }}]: https://github.com/SocialFinanceDigitalLabs/rtof-data-model/releases/tag/{{ t.tag }}
{% endfor %}

[gitlog]: https://github.com/SocialFinanceDigitalLabs/rtof-data-model/commits/main
[speclog]: https://github.com/SocialFinanceDigitalLabs/RTOF-specification/commits/main
