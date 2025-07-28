import os
import frontmatter
from slugify import slugify

MONSTER_DIR = "docs/monster"
SLUG_MAP_FILE = "tag_slug_mapping.txt"

# スラッグ変換辞書を読み込む
slug_map = {}
if os.path.exists(SLUG_MAP_FILE):
    with open(SLUG_MAP_FILE, encoding="utf-8") as f:
        for line in f:
            if "->" in line:
                tag, slug = line.strip().split("->")
                slug_map[tag.strip()] = slug.strip()

def get_slug(tag):
    return slug_map.get(tag, slugify(tag))

# 各モンスター .md ファイルを処理
for filename in os.listdir(MONSTER_DIR):
    if filename.endswith(".md") and filename != "index.md":
        path = os.path.join(MONSTER_DIR, filename)
        post = frontmatter.load(path)

        tags = post.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        elif not isinstance(tags, list):
            tags = []

        # スラグ変換
        tag_slugs = [get_slug(tag) for tag in tags]
        post["tag_slugs"] = tag_slugs

        # 上書き保存
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

print("✅ 全モンスターに tag_slugs を追加・更新しました。")
