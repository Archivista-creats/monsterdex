import os
import frontmatter
from collections import defaultdict
from slugify import slugify

MONSTER_DIR = "docs/monster"
TAGS_DIR = "docs/tags"
INDEX_PATH = os.path.join(TAGS_DIR, "index.md")
SLUG_MAP_FILE = "tag_slug_mapping.txt"

os.makedirs(TAGS_DIR, exist_ok=True)

tag_map = defaultdict(list)
slug_mapping = {}

# 手動スラグ定義の読み込み
manual_slugs = {}
if os.path.exists(SLUG_MAP_FILE):
    with open(SLUG_MAP_FILE, encoding="utf-8") as f:
        for line in f:
            if "->" in line:
                tag, slug = line.strip().split("->")
                manual_slugs[tag.strip()] = slug.strip()

# スラグ取得関数
def get_slug(tag):
    return manual_slugs.get(tag, slugify(tag))

# モンスターファイルからタグを収集
for filename in os.listdir(MONSTER_DIR):
    if filename.endswith(".md") and filename != "index.md":
        path = os.path.join(MONSTER_DIR, filename)
        post = frontmatter.load(path)
        title = post.get("title", filename.replace(".md", ""))
        raw_tags = post.get("tags", [])
        if isinstance(raw_tags, str):
            tags = [t.strip() for t in raw_tags.split(",")]
        elif isinstance(raw_tags, list):
            tags = raw_tags
        else:
            tags = []
        slug = filename.replace(".md", "")
        for tag in tags:
            tag_slug = get_slug(tag)
            slug_mapping[tag] = tag_slug
            tag_map[tag].append((title, slug))

# タグごとの Markdown ページを生成
for tag, monsters in tag_map.items():
    slug = get_slug(tag)
    filepath = os.path.join(TAGS_DIR, f"{slug}.md")
    lines = [
        "---",
        "layout: default",
        f"title: タグ: {tag}",
        f"permalink: /monsterdex/tags/{slug}.html",
        "---",
        f"# 🏷️ タグ「{tag}」に関連するモンスター\n"
    ]
    for title, monster_slug in monsters:
        lines.append(f"- [{title}](/monsterdex/monster/{monster_slug}.html)")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# index.md を生成または更新
index_lines = [
    "---",
    "layout: default",
    "title: タグ一覧",
    "permalink: /tags/",
    "---",
    "# 🗂️ 全タグ一覧\n"
]
for tag in sorted(tag_map.keys()):
    slug = get_slug(tag)
    index_lines.append(f"- [{tag}](/tags/{slug}/)")
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))

# スラグ変換リストを出力
with open(SLUG_MAP_FILE, "w", encoding="utf-8") as f:
    for tag, slug in sorted(slug_mapping.items()):
        f.write(f"{tag} -> {slug}\n")

print("✅ タグ個別ページ、タグ一覧、スラグ変換マップを生成・更新しました。")
