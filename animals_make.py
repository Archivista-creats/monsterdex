import os
import frontmatter
from collections import defaultdict
import jaconv

# === 設定 ===
MONSTER_DIR = './docs/monster'     # モンスターファイルの格納ディレクトリ
OUTPUT_DIR = './docs/animals'      # 出力先（既存Markdownに上書き）
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
unknown_files = []  # 追加: クラス不明や不備のあるファイルを収集

def to_sort_key(s: str) -> str:
    """かな→ひらがな化＋アルファベット→カナ化して並べ替えの安定性を高める"""
    if not s:
        return ""
    return jaconv.kata2hira(jaconv.alphabet2kana(s))

for filename in os.listdir(MONSTER_DIR):
    if not filename.endswith('.md'):
        continue

    path = os.path.join(MONSTER_DIR, filename)

    # frontmatter 読み込み
    try:
        post = frontmatter.load(path)
    except Exception as e:
        unknown_files.append((filename, "(no title)", f"frontmatter 読み込み失敗: {e.__class__.__name__}"))
        continue

    origin = post.get('origin', {}) or {}
    title = post.get('title')
    animal_class = origin.get('class')  # ★ デフォルトは付けない：不明検出のため
    animal_name = origin.get('common_ja', '不明動物')

    # タイトルが無い場合
    if not title:
        unknown_files.append((filename, "(no title)", "title 未設定"))
        continue

    # クラス未設定 or 未対応クラスは unknown に回す
    if not animal_class:
        unknown_files.append((filename, title, "class 未設定"))
        continue
    if animal_class not in CLASS_FILENAME_MAP:
        unknown_files.append((filename, title, f"class 未対応: {animal_class}"))
        continue

    # ここまで来たら分類に追加
    animal_index[animal_class].append((animal_name, title, filename))

# === 出力：Markdown を分類別に生成・上書き ===
for animal_class, entries in animal_index.items():
    entries_sorted = sorted(entries, key=lambda x: to_sort_key(x[0]))
    lines = [f"# 🧬 {animal_class} に属するモンスター\n"]
    for animal_name, title, filename in entries_sorted:
        lines.append(f"- **{animal_name}**：[ {title} ](../monster/{filename})")

    output_path = os.path.join(OUTPUT_DIR, CLASS_FILENAME_MAP[animal_class])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print("✅ animals インデックス生成完了！")

# === コンソール出力：クラス不明・不備一覧（ファイル出力なし） ===
if unknown_files:
    print("\n⚠️ クラス不明 / 不備のあるモンスターファイル一覧")
    print("------------------------------------------------")
    for filename, title, reason in sorted(unknown_files, key=lambda x: x[0].lower()):
        print(f"- {filename}  |  {title}  |  {reason}")
    print(f"\n合計: {len(unknown_files)} 件")
else:
    print("✅ クラス不明・不備ファイルはありません")
