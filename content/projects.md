---
layout: page
title: Research
permalink: /research/
nav_order: 2
---

Our research and impact spans across focus areas.
Below, each focus area is followed by the projects currently underway within it.

{% for area in site.data.focus_areas %}
{% assign area_projects = site.data.projects | where: "focus_area", area.slug %}
{% assign area_researchers = site.data.people | where_exp: "p", "p.focus_areas contains area.slug" | where: "alumni", false %}
<section class="focus-area" id="{{ area.slug }}">
  <div class="focus-area__hero">
    <img class="focus-area__image" src="{{ area.image | relative_url }}" alt="" loading="lazy">
    <div class="focus-area__text">
      <h2>{{ area.name }}</h2>
      <p>{{ area.description }}</p>

      {% if area_researchers.size > 0 %}
      <p class="researcher-row">
        {% for researcher in area_researchers %}
        <span class="researcher-chip">
          {% if researcher.image and researcher.image != "" %}<img src="{{ researcher.image | relative_url }}" alt="">{% else %}<span class="researcher-chip__placeholder"></span>{% endif %}
          {{ researcher.name }}
        </span>
        {% endfor %}
      </p>
      {% endif %}
    </div>
  </div>

  {% for project in area_projects %}
  <article class="project">
    <h3>{{ project.name }}</h3>
    <p class="project-meta">
      {{ project.start_year }}&ndash;{% if project.end_year %}{{ project.end_year }}{% endif %}
      {% if project.funder and project.funder != "" %} &middot; Funded by {{ project.funder }}{% endif %}
    </p>
    <p>{{ project.description }}</p>
  </article>
  {% endfor %}
</section>
{% unless forloop.last %}<ds-divider ds-padding="none"></ds-divider>{% endunless %}
{% endfor %}
