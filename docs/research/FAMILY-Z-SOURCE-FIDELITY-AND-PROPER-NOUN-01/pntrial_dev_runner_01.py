# -*- coding: utf-8 -*-
"""FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01B: 固有名詞ルール改定のDEV専用Prompt override runner(Trial専用)。

- Production Prompt file(er062_family_z_writer_01.py)は書き換えない。import後にメモリ上でPrompt定数だけ差替えて
  er062.main() を呼ぶ(runner本体・guardrail・provenance・費用記録はProductionと同一)。
- このfileは docs/research 配下のDEV専用。Production(er0xx_*.py)からのimport参照0(Grepで確認、PROPER_NOUN_TRIAL_01.md)。
- --variant common  : 共通ルールのみ(作品固有名を含まない)
  --variant per_story: 共通ルール + 作品個別メモ STORY_PROPER_NOUN_KEEP[story](共通ルールのみで目標未達のときだけ使用)
- 実行は --stage writer / std_adjust(er062と同じ引数)。--print-prompts は API呼出なしでPromptを標準出力。
"""
import argparse, os, sys, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er062_family_z_writer_01 as w          # noqa: E402  (Production module。import only、file無変更)

# ---- 共通ルール文(作品固有名を含まない) ----
COMMON_NAMING_POLICY = (
    "[Naming policy]\n"
    "Personal names are used for the main character (the protagonist) only, with one exception: a character who is "
    "central to the story, or whose identity matters for understanding how the story develops or ends, also keeps the "
    "name used in the original work, whether that character is the protagonist or a supporting character. "
    "Decide by how much the character matters to the story's events and ending -- not by how often the character "
    "appears. Every other person should be referred to by role or relationship (for example: her mother, his "
    "neighbor, the ruler, the guard) instead of a name. Do not add names for their own sake. If a character's original "
    "name has both a first name and a last name, use only one of them, consistently. "
    "This naming policy takes precedence over any other naming instruction elsewhere in this prompt.")

NEW_R0_BLOCK_COMMON_TAIL = (
    "[Characters -- keep it simple]\n"
    "Use 1 or 2 characters as the core of the story; 3 at the absolute most if truly needed. "
    "Do not add named characters that are not necessary for the story.\n\n" + COMMON_NAMING_POLICY)

NEW_PRESERVATION_LAST = "- Keep the cast small. Follow the naming policy for personal names."

NEW_REVISE_USER_TMPL = (
    "Here is a short story:\n\n{body}\n\n"
    "Without changing the events, the characters, or the cause-and-effect, please revise it into a more engaging story. "
    "Keep it at a natural upper-intermediate level (CEFR B1-B2), about 330-470 words, in third person. "
    "Naming policy: only the main character has a personal name, except that a character who is central to the story, "
    "or important for understanding how it develops or ends, keeps the name already used for that character in the "
    "story above; refer to every other person by role or relationship; use only a first name or a last name, not both; "
    "do not add names for their own sake. Output the title and the story only.")

# ---- 作品個別メモ(共通ルールのみで目標未達のときだけ使用。共通Promptには埋め込まない) ----
STORY_PROPER_NOUN_KEEP = {"the_open_window": ["Framton", "Vera"], "melos": ["Melos"]}


def _per_story_block(keep):
    names = ", ".join(keep)
    return ("\n\n[Names for this story]\nThe characters who have a personal name in this story are exactly: " + names +
            ". Use each of these names (one name per character, consistently) and refer to everyone else by role or relationship.")


def apply_override(variant: str, story: str):
    old_common = w.R0_BLOCK_COMMON
    head = old_common.split("[Characters -- keep it simple]")[0]
    assert head != old_common, "R0_BLOCK_COMMON anchor not found"
    w.R0_BLOCK_COMMON = head + NEW_R0_BLOCK_COMMON_TAIL
    pres = w.R0_BLOCK_PRESERVATION
    old_last = "- Keep the cast small and do not add named people other than the main character."
    assert old_last in pres
    w.R0_BLOCK_PRESERVATION = pres.replace(old_last, NEW_PRESERVATION_LAST)
    extra = _per_story_block(STORY_PROPER_NOUN_KEEP[story]) if variant == "per_story" else ""
    w.R0_BLOCK_LISTENING = w.R0_BLOCK_LISTENING + extra if extra else w.R0_BLOCK_LISTENING
    tmpl = NEW_REVISE_USER_TMPL
    if variant == "per_story":
        tmpl = tmpl.replace(" Output the title and the story only.",
                            " The characters with a personal name must be exactly: " + ", ".join(STORY_PROPER_NOUN_KEEP[story]) +
                            ". Output the title and the story only.")
    w.REVISE_USER_TMPL = tmpl
    w.R0_TEMPLATE = (
        "[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;\n"
        "this is NOT a summary to reproduce, just raw material]\n{seed_bullets}\n\n"
        "[How to convert it]\n{conversion}\n\n"
        + w.R0_BLOCK_PRESERVATION + "\n\n" + w.R0_BLOCK_STORY_TYPE + "\n\n" + w.R0_BLOCK_COMMON + "\n\n"
        + w.R0_BLOCK_LENGTH_ADV + "\n\n" + w.R0_BLOCK_LISTENING + "\n\n" + w.R0_BLOCK_FINAL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("common", "per_story"), required=True)
    ap.add_argument("--print-prompts", action="store_true")
    a, rest = ap.parse_known_args()
    story = rest[rest.index("--story") + 1]
    apply_override(a.variant, story)
    if a.print_prompts:
        seed = w.rj(f"{w.seed_dir_for(story)}/seed.json")
        p, _ = w.build_r0_prompt(seed)
        print(p); print("\n=====REVISE=====\n"); print(w.build_revise_prompt("<BODY>", story))
        return 0
    return w.main(rest)


if __name__ == "__main__":
    sys.exit(main())
