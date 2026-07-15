---
layout: default
title: Home
permalink: /
nav_order: 0
---

<div class="home">

  <section class="hero">
    <img class="hero__image" src="{{ '/assets/images/home/hero.webp' | relative_url }}" alt="">
    <div class="hero__scrim"></div>
    <div class="hero__text">
      <h1>SOCIAL COMPUTING</h1>
      <p class="hero__subtitle">The meeting point of social sciences and computing.</p>
    </div>
  </section>

  <p>Helsinki Social Computing is an interdisciplinary research group focused on
  computers and social science. Our work spans across political science,
  human-computer interaction, design, and data science. We study both <span class="highlight">the role of computers in our society</span> – the substance – and <span class="highlight">means to conduct digital and computational</span> research in social science – the methods</p>

  <ds-grid ds-container="true" ds-type="grid" ds-columns-desktop="3" ds-columns-tablet="2" ds-columns-mobile="1" class="link-box-list">
    <ds-card ds-heading="Research" ds-url="{{ '/research/' | relative_url }}" ds-link-type="full">
      <img slot="image" src="{{ '/assets/images/home/link-projects.webp' | relative_url }}" alt="">
    </ds-card>
    <ds-card ds-heading="People" ds-url="{{ '/people/' | relative_url }}" ds-link-type="full">
      <img slot="image" src="{{ '/assets/images/home/link-people.webp' | relative_url }}" alt="">
    </ds-card>
    <ds-card ds-heading="Method development" ds-url="{{ '/methods/' | relative_url }}" ds-link-type="full">
      <img slot="image" src="{{ '/assets/images/home/link-methods.webp' | relative_url }}" alt="">
    </ds-card>
  </ds-grid>

  <ds-grid ds-container="true" ds-type="grid" ds-columns-desktop="2" ds-columns-mobile="1" class="home-columns">
    <div class="home-column">
      <h2>Recent blog posts</h2>
      <ol class="blog-list">
      {% assign recent_posts = site.data.blog_posts | slice: 0, 5 %}
      {% for post in recent_posts %}
        <li>
          <ds-link ds-href="{{ post.url }}" ds-text="{{ post.title | escape }}" ds-weight="semibold"></ds-link>
          <br><small>{{ post.date }}</small>
          <p>{{ post.description }}</p>
        </li>
      {% endfor %}
      </ol>
      <p><ds-link ds-href="https://sociallycompute.substack.com" ds-text="All posts" ds-icon="arrow-outward"></ds-link></p>
    </div>

    <div class="home-column">
      <h2>Recent publications</h2>
      <ul class="publication-list">
      {% assign recent_publications = site.data.publications | sort: "date" | reverse | slice: 0, 5 %}
      {% for pub in recent_publications %}
        <li>
          <ds-link ds-href="{{ pub.url }}" ds-text="{{ pub.title | escape }}" ds-weight="semibold"></ds-link>{% if pub.venue %}: {{ pub.venue }}{% endif %}{% if pub.year %} ({{ pub.year }}){% endif %}
          {% if pub.authors %}<span class="badge-row">{% for author in pub.authors %}<ds-badge ds-text="{{ author | escape }}" ds-variant="default"></ds-badge>{% endfor %}</span>{% endif %}
        </li>
      {% endfor %}
      </ul>
      <p><ds-link ds-href="{{ '/publications/' | relative_url }}" ds-text="All publications" ds-icon="arrow-outward"></ds-link></p>
    </div>
  </ds-grid>
</div>
