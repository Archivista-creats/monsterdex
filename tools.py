# tools/backfill_origin.py
# 既存の monster MD に origin フロントマターを安全に追記・補完します。
# - ディレクトリ自動検出（docs/monster 優先、なければ monster）
# - frontmatter.dumps() → write_text() で bytes 書き込み問題を回避
# - 既存の origin は上書きせず、欠けているキーだけ補完
# - 「## 元動物」節の直後行から日本語名を推定。括弧内があれば優先

import re
import sys
from pathlib import Path
import frontmatter

def detect_monster_dir() -> tuple[Path, Path]:
    """(MONSTER_DIR, SITE_ROOT) を返す。docs/monster があればそれを優先。"""
    cand = Path("docs/monster")
    if cand.exists():
        return cand, Path("docs")
    cand = Path("monster")
    if cand.exists():
        return cand, Path(".")
    print("ERROR: monster ディレクトリが見つかりません（docs/monster か monster を用意）", file=sys.stderr)
    sys.exit(1)

MONSTER_DIR, SITE_ROOT = detect_monster_dir()

# 既知の元動物 → 系統 初期辞書（必要に応じて拡張してください）
KNOWN = {
    "オオアリクイ": {
        "class": "Mammalia", "order": "Pilosa", "family": "Myrmecophagidae",
        "common_en": "Giant Anteater", "scientific": "Myrmecophaga tridactyla"
    },
    "リス": {
        "class": "Mammalia", "order": "Rodentia", "family": "Sciuridae",
        "common_en": "Squirrel", "scientific": None
    },
    "カメレオン": {
        "class": "Reptilia", "order": "Squamata", "family": "Chamaeleonidae",
        "common_en": "Chameleon", "scientific": None
    },
    "タコ": {
        "class": "Cephalopoda", "order": "Octopoda", "family": "Octopodidae",
        "common_en": "Octopus", "scientific": None
    },
    "コウモリ": {
        "class": "Mammalia", "order": "Chiroptera", "family": None,
        "common_en": "Bat", "scientific": None
    },
    "カモノハシ": {
        "class": "Mammalia", "order": "Monotremata", "family": "Ornithorhynchidae",
        "common_en": "Platypus", "scientific": "Ornithorhynchus anatinus"
    },
    "犬": {
        "class": "Mammalia", "order": "Carnivora", "family": "Canidae",
        "common_en": "Dog", "scientific": "Canis familiaris"
    },
}

RE_ORIGIN_H2     = re.compile(r"^##\s*元動物\s*$", re.M)
RE_FIRST_CONTENT = re.compile(r"^[>\*\-\s]*([^\n]+)")
RE_PARENS_J      = re.compile(r"(.+?)（(.+?)）")   # 全角カッコ
RE_PARENS_E      = re.compile(r"(.+?)\((.+?)\)")   # 半角カッコ

def pick_preferred_name(line: str) -> str:
    """括弧内があればそれを優先。なければ行全体の先頭語を返す。"""
    line = line.strip()
    for pat in (RE_PARENS_J, RE_PARENS_E):
        m = pat.match(line)
        if m:
            inner = m.group(2).strip()
            if inner:
                return inner
    return line.split()[0] if line else ""

def infer_common_ja_from_body(body: str) -> str | None:
    """本文の『## 元動物』見出し直後の有効行から日本語名を推定。"""
    m = RE_ORIGIN_H2.search(body)
    if not m:
        return None
    lines = body[m.end():].strip().splitlines()
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("---") or ln.startswith("##"):
            break
        m2 = RE_FIRST_CONTENT.match(ln)
        if m2:
            return pick_preferred_name(m2.group(1))
    return None

def merge_missing(dst: dict, src: dict):
    """dst に対し、src の値を『欠けているキーのみ』補完。"""
    for k, v in src.items():
        if (dst.get(k) is None or dst.get(k) == "") and v is not None:
            dst[k] = v

def main():
    updated, patched, skipped = 0, 0, 0
    files = sorted(MONSTER_DIR.glob("*.md"))
    if not files:
        print(f"WARNING: {MONSTER_DIR} に .md が見つかりません")
    for p in files:
        post = frontmatter.load(p)
        origin = post.get("origin")

        inferred = infer_common_ja_from_body(post.content)
        if origin is None:
            # 新規追加
            common_ja = inferred or "TODO_元動物名"
            base = KNOWN.get(common_ja, {})
            origin = {
                "common_ja": common_ja,
                "common_en": base.get("common_en"),
                "scientific": base.get("scientific"),
                "class": base.get("class", "TODO_Class"),
                "order": base.get("order"),
                "family": base.get("family"),
            }
            post["origin"] = origin
            updated += 1
            print(f"[add ] origin → {p.name}  ({common_ja})")
        else:
            before = dict(origin)
            # KNOWN は common_ja をキーにする。なければ推定値で引く。
            base = KNOWN.get(origin.get("common_ja") or inferred or "", {})
            merge_missing(origin, {
                "common_ja": inferred,                 # 推定を優先補完
                "common_en": base.get("common_en"),
                "scientific": base.get("scientific"),
                "class": base.get("class"),
                "order": base.get("order"),
                "family": base.get("family"),
            })
            if origin != before:
                post["origin"] = origin
                patched += 1
                print(f"[patch] origin → {p.name}")
            else:
                skipped += 1
                # 既に埋まっている
                # print(f"[skip] {p.name}（変更なし）")

        data = frontmatter.dumps(post)  # str を得る
        p.write_text(data, encoding="utf-8")

    print(f"done. added={updated}, patched={patched}, unchanged={skipped}")

if __name__ == "__main__":
    sys.exit(main())
