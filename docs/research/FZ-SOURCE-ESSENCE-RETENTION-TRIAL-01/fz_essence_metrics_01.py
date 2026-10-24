# -*- coding: utf-8 -*-
"""FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 決定論指標(DEV/Trial専用。LLM呼出0)。
人称語・you・語数・文長・段落数を、ダイアログ("..."/“...”内)を除いた地の文で数える。Productionからのimport参照0。"""
import re, sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
import er062_family_z_structure_01 as st   # noqa: E402 (read-only import: 語数/文長の既存関数)

FP = re.compile(r"\b(?:I|I'm|I've|I'd|I'll|me|my|mine|myself|we|our|ours|us|ourselves)\b|\b(?:I’m|I’ve|I’d|I’ll)\b", re.I)
FP_I = re.compile(r"\bI(?:'m|'ve|'d|'ll|’m|’ve|’d|’ll)?\b")          # 'I' は大文字のみ(iは語として出ない)
FP_OTHER = re.compile(r"\b(?:me|my|mine|myself|we|our|ours|us|ourselves)\b", re.I)
TP = re.compile(r"\b(?:he|his|him|himself|she|her|hers|herself|they|them|their|theirs|themselves)\b", re.I)
YOU = re.compile(r"\b(?:you|your|yours|yourself|you're|you'd|you'll|you've|you’re|you’d|you’ll|you’ve)\b", re.I)
_QUOTE = re.compile(r'"[^"]*"|“[^”]*”')


def strip_dialogue(body: str) -> str:
    return _QUOTE.sub(" ", body)


def metrics(text: str) -> dict:
    title, body = st.split_title_body(text)
    paras = st.clean_body_paragraphs(body)
    narr = strip_dialogue(" ".join(paras))
    return {
        "words": st.body_word_count(text),
        "paragraphs": len(paras),
        "avg_sentence_len": round(st.avg_sentence_len(paras), 2),
        "fp_narration": len(FP_I.findall(narr)) + len(FP_OTHER.findall(narr)),
        "tp_narration": len(TP.findall(narr)),
        "you_narration": len(YOU.findall(narr)),
        "you_total": len(YOU.findall(" ".join(paras))),
    }


def main(argv):
    out = {p: metrics(open(p, encoding="utf-8").read()) for p in argv}
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
