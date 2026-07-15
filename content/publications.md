---
layout: page
title: Publications
permalink: /publications/
nav_order: 4
---

{% assign publications = site.data.publications | sort: "date" | reverse %}
{% assign page_size = 25 %}

<ul class="publication-list" id="publication-list">
{% for pub in publications %}
  <li{% if forloop.index0 >= page_size %} class="is-hidden" hidden{% endif %}>
    <ds-link ds-href="{{ pub.url }}" ds-text="{{ pub.title | escape }}" ds-weight="semibold"></ds-link>{% if pub.venue %}: {{ pub.venue }}{% endif %}{% if pub.year %} ({{ pub.year }}){% endif %}
    {% if pub.authors %}<span class="badge-row">{% for author in pub.authors %}<ds-badge ds-text="{{ author | escape }}" ds-variant="default"></ds-badge>{% endfor %}</span>{% endif %}
  </li>
{% endfor %}
</ul>

{% if publications.size > page_size %}
<ds-button id="load-more-publications" ds-text="Load more" ds-variant="secondary" data-page-size="{{ page_size }}"></ds-button>
{% endif %}
