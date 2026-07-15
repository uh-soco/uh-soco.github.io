---
layout: page
title: Teaching
permalink: /teaching/
description: Courses taught by the Helsinki Social Computing Group, at the University of Helsinki and Aalto University.
nav_order: 5
---

We teach both at University of Helsinki and Aalto University on various
courses focused on digital society and its substantial questions and
computational and digital research methods.

{% for section in site.data.teaching %}
<section class="course-section">
  <h2>{{ section.header }}</h2>
  <ul class="course-list">
  {% for course in section.courses %}
    <li>
      {% if course.url %}<ds-link ds-href="{{ course.url }}" ds-text="{{ course.name | escape }}" ds-weight="semibold"></ds-link>{% else %}{{ course.name }}{% endif %}
      {% if course.start_date %}&nbsp;(last teaching time: {{ course.start_date }} &ndash; {{ course.end_date }}){% endif %}
    </li>
  {% endfor %}
  </ul>
</section>
{% endfor %}

<!-- The two sections below are copied as plain text from
     https://www.helsinki.fi/en/researchgroups/social-computing/teaching —
     edit freely, they are not pulled from any data file. -->

## Impact beyond Helsinki area

Since 2018, our group has been organizing [Summer Institute in Computational
Social Science (SICSS)](https://sicss.io/) in Helsinki, together with other
SICSSs around the world. It is a two-week intensive introduction to
computational social sciences, bringing together graduate students,
postdoctoral researchers, and junior faculty.

Matti's introduction-level book for computational social science:
Computational Thinking and Social Science is published by [SAGE
Publishing](https://uk.sagepub.com/en-gb/eur/computational-thinking-and-social-science/book268542).
The book delves into the tools and techniques used to build familiarity with
programming and gain context into how, why and when they aid to make social
science happen.

## Learning materials

For computational methods, materials we have developed are always
up-to-date in [GitHub](https://github.com/uh-dcm) and most are suitable for
personal study as well.

In addition to courses listed above, our group organises a set of tools
courses for qualitative researchers under the umbrella name [Qualitative
Research and Computers](https://uh-dcm.github.io/qualitative-research-and-computers/).
