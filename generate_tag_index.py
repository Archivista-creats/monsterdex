import os
import frontmatter
from collections import defaultdict
from slugify import slugify

# ディレクトリとファイルのパス
MONSTER_DIR = "docs/monster"
TAGS_DIR = "docs/tags"
PLACE_INDEX_PATH = "docs/place/index.md"
INDEX_PATH = os.path.join(TAGS_DIR, "index.md")
SLUG_MAP_FILE = "tag_slug_mapping.txt"

# 分類カテゴリ定義
ATTRIBUTE_TAGS = {"火", "水", "風", "土", "光", "闇", "時", "空間", "無", "雷", "氷", "毒"}
TYPE_TAGS = {"精霊獣", "禁獣", "変生獣"}

# 出現地名の抽出
def load_places():
    place_tags = set()
    if os.path.exists(PLACE_INDEX_PATH):
        with open(PLACE_INDEX_PATH, encoding="utf-8") as f:
            for line in f:
                if line.startswith("| ["):
                    name = line.split("]")[0].split("[")[1].strip()
                    place_tags.add(name)
    return place_tags

PLACE_TAGS = load_places()

# タグ分類関数
def classify_tag(tag):
    if tag in ATTRIBUTE_TAGS:
        return "属性"
    elif tag in TYPE_TAGS:
        return "分類"
    elif tag in PLACE_TAGS:
        return "出現地"
    else:
        return None  # 未分類

# 手動スラグ定義の読み込み
manual_slugs = {}
if os.path.exists(SLUG_MAP_FILE):
    with open(SLUG_MAP_FILE, encoding="utf-8") as f:
        for line in f:
            if "->" in line:
                tag, slug = line.strip().split("->")
                manual_slugs[tag.strip()] = slug.strip()

def get_slug(tag):
    return manual_slugs.get(tag, None)

# タグ別のモンスター記録
tag_map = defaultdict(list)
unknown_tags = set()

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
            tag_map[tag].append((title, slug))
            if get_slug(tag) is None:
                unknown_tags.add(tag)

# タグ個別ページの生成
os.makedirs(TAGS_DIR, exist_ok=True)
for tag, monsters in tag_map.items():
    slug = get_slug(tag)
    if not slug:
        continue  # 未定義タグは出力しない
    filepath = os.path.join(TAGS_DIR, f"{slug}.md")
    lines = [
        "---",
        "layout: default",
        f"title: タグ: {tag}",
        f"permalink: /tags/{slug}/",
        "---",
        f"# 🏷️ タグ「{tag}」に関連するモンスター\n"
    ]
    for title, monster_slug in monsters:
        lines.append(f"- [{title}](/monsterdex/monster/{monster_slug}.html)")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# index.md の生成（分類ごと）
index_lines = [
    "---",
    "layout: default",
    "title: タグ一覧",
    "permalink: /tags/",
    "---",
    "# 🗂️ タグ一覧\n"
]

for section, header in [("属性", "## 🔥 属性タグ"), ("出現地", "## 🌍 出現地タグ"), ("分類", "## 🧬 分類タグ")]:
    index_lines.append(header)
    for tag in sorted(tag for tag in tag_map if classify_tag(tag) == section):
        slug = get_slug(tag)
        if slug:
            index_lines.append(f"- [{tag}](/monsterdex/tags/{slug}.html)")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))

# 未定義スラグの警告出力
if unknown_tags:
    print("⚠️ 以下のタグにスラグ定義がありません（tag_slug_mapping.txt に追加してください）:")
    for tag in sorted(unknown_tags):
        print(f"  - {tag}")
else:
    print("✅ すべてのタグにスラグが定義されています。")
