---
layout: page
title: Work with us
permalink: /work-with-us
nav_order: 6
---

## Individual research project

{% assign small_projects = site.data.cowork | where_exp: "t", "t.categories contains 'Small project'" %}
{% include cowork-list.html topics=small_projects empty_message="No open small projects at the moment — check back later." %}

## Master thesis supervision

{% assign thesis_topics = site.data.cowork | where_exp: "t", "t.categories contains 'Thesis topic'" %}
{% include cowork-list.html topics=thesis_topics empty_message="No open thesis topics at the moment — check back later." %}

In addition, group members are open for supervisting master students:

* Matti Nelimarkka, computational and digital methods in social science research, politics and human-computer interaction

## Do a PhD

Following group members are open for supervisting PhD students:

* [Matti Nelimarkka](https://me.mante.li/research/phd-studies)