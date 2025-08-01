import os
import frontmatter

MONSTER_DIR = "docs/monster"
INDEX_PATH = os.path.join(MONSTER_DIR, "index.md")

entries = []

for filename in sorted(os.listdir(MONSTER_DIR)):
    if filename.endswith(".md") and filename != "index.md":
        path = os.path.join(MONSTER_DIR, filename)
        try:
            post = frontmatter.load(path)
        except Exception as e:
            print(f"❌ エラー: {filename} の読み込みに失敗しました: {e}")
            continue
        title = post.get("title", filename.replace(".md", ""))
        slug = filename.replace(".md", "")
        # 👉 リンクを /monsterdex/monster/〇〇.html に変更
        entries.append(f"- [{title}](/monsterdex/monster/{slug}.html)")

index_content = """---
title: モンスター一覧
layout: default
permalink: /monster/
---

# 🐾 モンスター一覧

""" + "\n".join(entries)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(index_content)

print("✅ monster/index.md を更新しました。")
