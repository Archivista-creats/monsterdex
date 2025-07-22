---
title: タグテストV1
layout: single
tags: [テスト, 土, 風]
---

これはタグ機能の動作確認用ページです。  
正しく設定されていれば、このページの下部にタグが表示され、  
各タグからタグ別ページ（例：`/tags/風/`）に遷移できるようになります。

---

{% if page.tags %}
**📌 タグ一覧：**

{% for tag in page.tags %}
- [{{ tag }}](/monsterdex/tags/{{ tag | slugify }}/)
{% endfor %}
{% endif %}
