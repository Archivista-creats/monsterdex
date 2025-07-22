---
title: タグテスト
layout: single
tags: [テスト, 土]
---

タグ機能テスト用ページです。


{% if page.tags %}
<div class="tags">
  <strong>タグ:</strong>
  {% for tag in page.tags %}
    <a href="{{ '/tags/' | append: tag | slugify | append: '/' }}">{{ tag }}</a>
  {% endfor %}
</div>
{% endif %}
