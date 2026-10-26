# -*- coding: utf-8 -*-
"""自ルーブリック(DESIGN_01 §7。Y/B/N)の評価結果を own_rubric_01.json に書き出す。評価はjudge結果を見る前に確定(judge出力は未参照)。
R2自然さ/R3汎用性/R4難易度適合(Std=A2〜B1, Adv=B1〜B2)/R5同一run内非重複。"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))

R = {
    "ai_island_temple:a2": {
        "carry over": ("Y", "句動詞。汎用・適度"),
        "worth paying attention to": ("Y", "定型構文。汎用"),
        "a useful card to play": ("B", "usefulは修飾語。card to play が核(R2過剰)"),
        "take a detour": ("Y", "比喩を含む定番表現"),
        "one step ahead": ("Y", "定番の比喩表現"),
        "make a difference": ("Y", "汎用の定番イディオム"),
        "obstacle": ("Y", "B1語彙。汎用"),
        "separately": ("Y", "副詞。Standardでは適度"),
        "discovery": ("B", "基本寄り(R4やや易)"),
        "strategy": ("B", "基本寄り+見出し由来の大文字表記"),
    },
    "ai_island_temple:b1b": {
        "carry over": ("Y", "句動詞"),
        "call on": ("Y", "句動詞(頼まれる)"),
        "look at separately": ("B", "受動の語尾を落とした切り出しでやや不自然"),
        "one step ahead": ("Y", "定番の比喩"),
        "card to play": ("Y", "最小形のイディオム"),
        "take a detour": ("Y", "比喩を含む"),
        "no use right now": ("N", "基本語のみ+right nowは余剰(数合わせ型)"),
        "a useful card to play": ("B", "usefulは修飾語(R2過剰)"),
        "performance": ("N", "易しい語。glossも文脈依存"),
        "exploration": ("Y", "B2名詞。汎用"),
        "overlook": ("Y", "B2動詞。汎用"),
        "exploration mode": ("B", "mode付きは記事寄り"),
        "technique": ("B", "基本寄り"),
    },
    "uk_train_speaker_playback:a2": {
        "point to current rail rules": ("N", "記事固有で再利用不可(R3)"),
        "written permission": ("Y", "汎用コロケーション"),
        "draw a line": ("Y", "比喩の定番"),
        "put on an unwanted show": ("N", "見出し由来で記事固有・glossも不自然"),
        "sound no one asked for": ("B", "見出し由来でやや記事寄り"),
        "reach for one's wallet": ("Y", "定番表現"),
        "exception": ("Y", "B1名詞。汎用"),
        "masterpiece": ("Y", "B2名詞。汎用"),
        "audience": ("B", "基本寄り(R4やや易)"),
        "carriage": ("B", "基本寄り・英国寄りの意味"),
    },
    "uk_train_speaker_playback:b1b": {
        "blanket ban": ("Y", "コロケーション"),
        "reach for one's wallet": ("Y", "定番表現"),
        "draw a line": ("Y", "比喩の定番"),
        "be covered": ("N", "文脈依存で単独では不明確(R2)"),
        "due to be shared": ("B", "be due toが核。shared付きでやや過剰"),
        "face a fine": ("Y", "コロケーション"),
        "written permission": ("Y", "コロケーション"),
        "up to": ("N", "基本語(R4)"),
        "uninvited": ("Y", "B2形容詞"),
        "automatically": ("B", "基本寄り"),
        "masterpiece": ("Y", "B2名詞"),
    },
    "monkeys_paw:a2": {
        "sergeant-major": ("N", "軍の階級名で汎用性が低い(R3)"),
        "break the silence": ("Y", "定番表現"),
        "take hold of": ("Y", "定番表現"),
        "for someone's loss": ("N", "切り出しが不自然な断片(R2)"),
        "rise into the night": ("B", "描写的で再利用は限定的"),
        "back to life": ("Y", "定番表現"),
        "to blame": ("Y", "be to blame の核"),
        "blame someone for what happens": ("B", "blame someone for が核。節まで含み過剰"),
        "fate": ("Y", "汎用名詞"),
        "twist": ("Y", "多義の汎用動詞"),
        "scrape": ("Y", "B2動詞。汎用"),
    },
    "monkeys_paw:b1b": {
        "interfere with fate": ("B", "interfere withが核。fateは目的語で余剰気味"),
        "wail of loss": ("B", "描写的でやや記事固有"),
        "pay off": ("Y", "句動詞"),
        "compensation": ("Y", "汎用名詞"),
        "snatch": ("Y", "動詞"),
        "rattle": ("Y", "動詞"),
        "sergeant-major": ("N", "軍の階級名で汎用性が低い"),
        "pay off the house": ("B", "pay offが核。目的語が記事固有(R2過剰)"),
        "caught in the machinery": ("B", "記事固有の文脈寄り"),
        "shake one's husband awake": ("N", "記事固有の断片(R3)"),
        "deserted": ("Y", "形容詞。汎用"),
        "burial": ("Y", "B2名詞"),
        "in compensation": ("B", "compensationと重複する学習点(R5)で前置詞付きは弱い"),
        "responsibility": ("B", "基本寄り"),
    },
}

if __name__ == "__main__":
    out = {k: {f: {"verdict": v[0], "note": v[1]} for f, v in d.items()} for k, d in R.items()}
    with open(os.path.join(OUT, "own_rubric_01.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print({k: len(v) for k, v in out.items()})
