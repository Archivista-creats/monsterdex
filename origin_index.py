# tools/build_origin_index.py
# 「元動物から探す」の階層インデックスを生成します。
# - ディレクトリ自動検出（docs/monster 優先、なければ monster）
# - 基本は Class → 元動物（2階層）
# - Class 内の元動物が THRESHOLD 以上なら Order を自動挿入（最大3階層）
# - どのページにもパンくず・件数バッジ・五十音ジャンプを付与

import sys
import collections
from pathlib import Path
import frontmatter
from slugify import slugify

def detect_monster_dir() -> tuple[Path, Path, Path]:
    """(MONSTER_DIR, OUT_DIR, SITE_ROOT) を返す。docs/monster 優先。"""
    cand = Path("docs/monster")
    if cand.exists():
        return cand, Path("docs/origin"), Path("docs")
    cand = Path("monster")
    if cand.exists():
        return cand, Path("origin"), Path(".")
    print("ERROR: monster ディレクトリが見つかりません（docs/monster か monster を用意）", file=sys.stderr)
    sys.exit(1)

MONSTER_DIR, OUT_DIR, SITE_ROOT = detect_monster_dir()
THRESHOLD   = 30  # Class 内の元動物がこの数以上なら Order を挿入
ATTR_SET    = {"火","水","土","風","光","闇","時","空間","無","雷","氷","毒"}

KANA_GROUPS = [
    ("あ", set("あいうえおアイウエオ")),
    ("か", set("かきくけこカキクケコ")),
    ("さ", set("さしすせそサシスセソ")),
    ("た", set("たちつてとタチツテト")),
    ("な", set("なにぬねのナニヌネノ")),
    ("は", set("はひふへほハヒフヘホ")),
    ("ま", set("まみむめもマミムメモ")),
    ("や", set("やゆよヤユヨ")),
    ("ら", set("らりるれろラリルレロ")),
    ("わ", set("わをんワヲン")),
    ("英数", set())
]

def head_kana(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "英数"
    ch = s[0]
    for label, chars in KANA_GROUPS[:-1]:
        if ch in chars:
            return label
    return "英数"

def read_entries():
    entries = []
    for p in sorted(MONSTER_DIR.glob("*.md")):
        post = frontmatter.load(p)
        origin = post.get("origin") or {}
        cl = origin.get("class")
        an = origin.get("common_ja")
        if not cl or not an:
            continue
        tags = set(post.get("tags") or [])
        attr_list = [t for t in tags if t in ATTR_SET]
        attr = "・".join(attr_list) if attr_list else None

        title = post.get("title") or p.stem
        entries.append({
            "title": title,
            "path": str(p.relative_to(SITE_ROOT)).replace("\\","/"),
            "attr": attr,
            "origin": {
                "class": cl,
                "order": origin.get("order") or "Unassigned",
                "family": origin.get("family") or "Unassigned",
                "common_ja": an,
                "common_en": origin.get("common_en"),
                "scientific": origin.get("scientific"),
            }
        })
    return entries

def nest_by(entries, key_fn):
    d = collections.defaultdict(list)
    for e in entries:
        d[key_fn(e)].append(e)
    return d

def write(path: Path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    path.write_text(str(text), encoding="utf-8")

def badge(n: int) -> str:
    return f"<sup>**{n}**</sup>"

def breadcrumb(parts):
    return " / ".join(parts)

def header(title, crumbs):
    return f"# {title}\n\n_{breadcrumb(crumbs)}_\n\n---\n"

def animal_list_grouped(entries):
    # 元動物 → [entries...]
    by_animal = nest_by(entries, lambda e: e["origin"]["common_ja"])
    # 五十音ラベル → [(animal_name, [entries...])]
    groups = collections.defaultdict(list)
    for an, ents in by_animal.items():
        groups[head_kana(an)].append((an, ents))

    lines = []
    # ジャンプリンク
    jump = []
    for label, _ in KANA_GROUPS:
        anchor = "#kana-" + ("en" if label == "英数" else label)
        jump.append(f"[{label}]({anchor})")
    lines.append(" ".join(jump) + "\n")

    for label, _ in KANA_GROUPS:
        items = sorted(groups.get(label, []), key=lambda x: x[0])
        if not items:
            continue
        anchor_id = "kana-" + ("en" if label == "英数" else label)
        lines.append(f'<a id="{anchor_id}"></a>\n## {label}\n')
        for an, ents in items:
            links = []
            for e in sorted(ents, key=lambda x: x["title"]):
                attr = f"[{e['attr']}]" if e["attr"] else ""
                links.append(f"{attr} [{e['title']}](/{e['path']})")
            lines.append(f"- **{an}** — " + "、 ".join(links))
        lines.append("")
    return "\n".join(lines)

def write_root(class_map):
    # /origin/index.md
    lines = [
        "# 🧭 元動物から探す\n",
        "大分類（**Class**）から辿って、元動物 → 登録モンスターへ。\n\n---\n"
    ]
    for cl in sorted(class_map.keys()):
        animals = {e["origin"]["common_ja"] for e in class_map[cl]}
        lines.append(f"- [{cl}]({slugify(cl)}/index.md) {badge(len(animals))}")
    write(OUT_DIR / "index.md", "\n".join(lines) + "\n")

def write_class(cl, entries):
    animals = {e["origin"]["common_ja"] for e in entries}
    title = f"{cl}（Class）"
    crumbs = ["元動物", cl]
    if len(animals) < THRESHOLD:
        # 2階層：元動物を直接並べる
        text = [
            header(title, crumbs),
            f"**登録元動物**：{len(animals)}\n\n",
            animal_list_grouped(entries)
        ]
        write(OUT_DIR / slugify(cl) / "index.md", "\n".join(text))
    else:
        # 3階層：Order を挿入
        by_order = nest_by(entries, lambda e: e["origin"]["order"])
        lines = [header(title, crumbs), "## 目（Order）\n"]
        for od in sorted(by_order.keys()):
            count = len({e["origin"]["common_ja"] for e in by_order[od]})
            lines.append(f"- [{od}]({slugify(od)}/index.md) {badge(count)}")
        write(OUT_DIR / slugify(cl) / "index.md", "\n".join(lines) + "\n")
        for od, ents in by_order.items():
            write_order(cl, od, ents)

def write_order(cl, od, entries):
    title = f"{od}（Order）"
    crumbs = ["元動物", cl, od]
    # Family は URL を増やさず、見出しで区切るだけ
    by_family = nest_by(entries, lambda e: e["origin"]["family"])
    lines = [header(title, crumbs)]
    for fa in sorted(by_family.keys()):
        lines.append(f"## {fa}（Family）\n")
        lines.append(animal_list_grouped(by_family[fa]))
    out = OUT_DIR / slugify(cl) / slugify(od) / "index.md"
    write(out, "\n".join(lines))

def main():
    entries = read_entries()
    by_class = nest_by(entries, lambda e: e["origin"]["class"])
    write_root(by_class)
    for cl, ents in by_class.items():
        write_class(cl, ents)
    print(f"generated origin indexes under: {OUT_DIR}")

if __name__ == "__main__":
    sys.exit(main())
