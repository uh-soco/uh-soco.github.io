---
layout: page
title: People
permalink: /people/
description: Members of the Helsinki Social Computing Group, current and alumni.
nav_order: 1
---

{% assign current_members = site.data.people | where: "alumni", false | sort: "name" %}
{% assign alumni_members = site.data.people | where: "alumni", true | sort: "name" %}

## Current members

<ds-grid ds-container="true" ds-type="grid" ds-columns-desktop="3" ds-columns-tablet="2" ds-columns-mobile="1" class="people-grid">
{% for person in current_members %}
  <ds-card ds-heading="{{ person.name | escape }}" ds-description="{{ person.description | strip_html | strip_newlines | escape }}" ds-link-type="none" ds-variant="outlined">
    {% if person.image and person.image != "" %}<img slot="image" src="{{ person.image | relative_url }}" alt="{{ person.name }}" loading="lazy">{% endif %}
  </ds-card>
{% endfor %}
</ds-grid>

## Alumni

<ds-grid ds-container="true" ds-type="grid" ds-columns-desktop="3" ds-columns-tablet="2" ds-columns-mobile="1" class="people-grid">
{% for person in alumni_members %}
  <ds-card ds-heading="{{ person.name | escape }}" ds-description="{{ person.description | strip_html | strip_newlines | escape }}" ds-link-type="none" ds-variant="outlined">
    {% if person.image and person.image != "" %}<img slot="image" src="{{ person.image | relative_url }}" alt="{{ person.name }}" loading="lazy">{% endif %}
  </ds-card>
{% endfor %}
</ds-grid>
