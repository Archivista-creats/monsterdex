import os
import frontmatter
from collections import defaultdict
import jaconv

# === 設定 ===
MONSTER_DIR = './docs/monster'     # モンスターファイルの格納ディレクトリ
OUTPUT_DIR = './docs/animals'  # 出力先（既存Markdownに追記）

CLASS_FILENAME_MAP = {
    "哺乳類": "mammalia.md",
    "鳥類": "aves.md",
    "爬虫類": "reptilia.md",
    "両生類": "amphibia.md",
    "魚類": "pisces.md",
    "昆虫": "insecta.md",
    "甲殻類": "crustacea.md",
    "軟体動物": "mollusca.md",
    "その他": "others.md"
}

# === 準備：分類ごとのリストを作る ===
animal_index = defaultdict(list)

for filename in os.listdir(MONSTER_DIR):
    if not filename.endswith('.md'):
        continue
    path = os.path.join(MONSTER_DIR, filename)
    post = frontmatter.load(path)
    origin = post.get('origin', {})
    title = post.get('title')
    animal_class = origin.get('class', 'その他')
    animal_name = origin.get('common_ja', '不明動物')

    if not title or animal_class not in CLASS_FILENAME_MAP:
        continue

    animal_index[animal_class].append((animal_name, title, filename))

# === 出力：Markdown を分類別に生成・上書き ===
for animal_class, entries in animal_index.items():
    entries_sorted = sorted(entries, key=lambda x: jaconv.kata2hira(jaconv.alphabet2kana(x[0])))
    lines = [f"# 🧬 {animal_class} に属するモンスター\n"]

    for animal_name, title, filename in entries_sorted:
        lines.append(f"- **{animal_name}**：[ {title} ](../monster/{filename})")

    output_path = os.path.join(OUTPUT_DIR, CLASS_FILENAME_MAP[animal_class])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print("✅ animals インデックス生成完了！")
