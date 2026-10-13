"""KP-OPT-01 委任_02: 改善Prompt短縮版(C2のPromptそのものを差し替え。Trial専用、Production非接続、API呼出なし)。

01版(er064_kp_opt_01_prompt_build.py)からの変更(Fable判断+Opusレビューのうち必須M1/M3):
 M1 注釈ラベルをrows側定数(U.LABEL_*)と同一にする(Promptは`contains:`/`contained_in:`の英語ラベルを参照)。
 M3 短縮: 定着度/既知基本連語を1段落へ統合、出力ルールの区分3行を1文へ、topic段落を縮約、take care例示削除、
    established_or_article_specific欄を削除(schemaはProduction同一)、「同格 vs 区分優先」を『区分優先は質が同程度のときの補充規則』と位置づけ。
    6指標の順序行(LINE_A)は逐語維持。
"""
from __future__ import annotations
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("TIKTOKEN_PATH"):
    sys.path.insert(0, os.environ["TIKTOKEN_PATH"])
import er064_kp_opt_01_prompt_build as B1
import er064_kp_opt_01_upstream_core as U

OUT = "er064_output/kp_extraction_selection_opt_01/phase1_fix"
LABEL_CONTAINS, LABEL_CONTAINED = U.LABEL_CONTAINS, U.LABEL_CONTAINED

LEVEL_RULE = {  # Level差は各1文のみ
    "std": "この記事は初級(A2相当)向けなので、日常で頻出する基本的な句は既知として扱ってください。",
    "adv": "この記事はB1相当向けなので、基本義と異なる意味の句動詞や文脈で意味が変わるコロケーションは、初見で難しいものとして同列に評価してください。",
}

AFTER_HEAD = """以下の英語記事の候補一覧から、初回リスニングで意味を取れず、その後の理解を止める可能性が高い表現を、支援価値の高い順にちょうど5個選んでください。

【判断の基準】
音声で一度だけ聞いたときに意味を処理できるかを最優先してください。優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。

未知単語、題材固有表現、短い複数語パターン、比喩・感情表現を同格の候補として扱ってください。構成語から意味を容易に推測できる透明表現は、記事上重要でも優先度を下げてください。

同程度の候補どうしでは、定着した自然な表現(慣用句、自然なコロケーション、句動詞、本文で基本義と異なる意味の表現)を、構成語どおりの基本連語やこの記事だけの言い回しより優先してください。区分名(idiom等)やevidenceラベルだけでは選ばず、CEFR等級だけでも判断しないでください。{level_rule}

【学ぶ単位】
動詞表現は目的語・補語まで、名詞表現は修飾語まで含めた、用法が成り立つ最小のまとまりを選んでください(例: rateよりinterest rate)。候補行の`{label_contains} Cn`はCnを含む、`{label_contained} Cn`はCnの一部であることを示します。同じ内容を両方選ばず、用法を成り立たせる要素を含む側を選んでください(長い側が主語・時・場所の付け足しだけなら短い側)。
display_phraseは1〜5語にしてください。完全文、主語と有限動詞を持つ節は禁止です。動詞は本文の時制を残さず基本形へ直してください(受動はbe + past participleの見出し形も可)。

【役割】
5個のうち1個は、この記事に特有で、事前に知っていると本文の主張や展開を追いやすくなる語または表現にしてください(key_phrase_role="topic")。汎用性は高くなくてかまいません。人名・企業名・地名、専門用語、比喩という種類だけでは選びません。該当が見当たらなくても空にせず、最も近い候補を選んでください。
残り4個(key_phrase_role="important")は、他の記事でも使える定着した表現にしてください。この記事だけの創作的な言い回しは選ばないでください(topicには選べます)。key_phrase_roleは候補の区分とは独立した、選定後の役割ラベルです。

【日本語グロス】
日本語グロスは、日本人の英語学習者が音声で聞いてすぐ意味を理解できる、自然で平易な現代日本語の一文にしてください。直訳調や、「常態」「是正」のような硬い報道語・漢語は避けてください。括弧（　）で別訳・専門用語・補足を書き添えないでください。「～」「〜」は辞書的に自然な範囲(例: 「～を示す」)でのみ使い、「…」のようなプレースホルダー記号は使わないでください。数字を含める場合は算用数字ではなく漢数字(一、二、三…)で書いてください。「ソロ旅行を～％とする」のように数値を補わないと意味が成立しない句・グロスは選ばず、それ単体で意味が成立するものを選んでください。
"""

AFTER_TAIL = """
【出力のルール】
- 5件は必ず上記の候補一覧から選び、新しい表現を作らないでください。[重要な単語・単語群候補]区分から少なくとも1個、残りは[phrase / idiom / phrasal verb候補]区分を優先し、[word候補]区分は良い候補が不足するときだけ使ってください。この区分の優先は、質が同程度のときの補充規則です。
- 各itemのsource_candidate_idには、選んだ候補のcandidate ID(例: C7)を1つだけ指定してください。本文の文字列(source_sentence/source_span相当)は書かないでください。
- surface_echoには、選んだ候補が表す表現を短く(1〜6語程度)書いてください。内部確認用で、正誤判定には使いません。
- 上記5件とは別に、backup_itemとして、重要語・重要表現(key_phrase_role="important")の予備候補を、異なるcandidate IDで1件、必ず返してください(topicが正しく選べた場合は採用されません)。
"""


def after_static(level: str) -> str:
    return (AFTER_HEAD.replace("{level_rule}", LEVEL_RULE[level]).replace("{label_contains}", LABEL_CONTAINS)
            .replace("{label_contained}", LABEL_CONTAINED))


def after_template() -> str:
    return (AFTER_HEAD.replace("{level_rule}", "{LEVEL_RULE}").replace("{label_contains}", LABEL_CONTAINS)
            .replace("{label_contained}", LABEL_CONTAINED))


def schema_json():
    return B1.contract.build_json_schema(["C1", "C2"])  # Production同一(established_or_article_specific欄は削除)


tokens = B1.tokens
sha = B1.sha
render = B1.render
extract_candidate_block = B1.extract_candidate_block

V5 = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"


def main():
    os.makedirs(OUT, exist_ok=True)
    bs, bg = B1.before_static(), B1.BEFORE_GUIDANCE
    sep = "\n" + "=" * 20 + " "
    props = schema_json()["schema"]["properties"]["items"]["items"]["properties"]
    after_txt = (f"{sep}[1] DEVELOPER MESSAGE (変更なし) =====\n{B1.DEV_MSG}\n"
                 f"{sep}[2] USER MESSAGE 先頭: 静的instructions(Trial専用・短縮版。{{LEVEL_RULE}}はStd/Advで差し替え) =====\n{after_template()}\n"
                 f"{sep}[2a] LEVEL_RULE std =====\n{LEVEL_RULE['std']}\n{sep}[2b] LEVEL_RULE adv =====\n{LEVEL_RULE['adv']}\n"
                 f"{sep}[3] USER MESSAGE 中段: 候補セクション形式(変更なし。注釈は行末に `| {U.LABEL_CONTAINS} Cn` `| {U.LABEL_CONTAINED} Cn` が付く場合がある) =====\n"
                 + "\n".join(B1.CAND_HEADERS) + "\n"
                 f"{sep}[4] USER MESSAGE 末尾: 出力のルール(Trial専用・短縮版) ====={AFTER_TAIL}\n"
                 f"{sep}[5] OUTPUT SCHEMA(Production同一。追加フィールドなし。item properties) =====\n"
                 + json.dumps(props, ensure_ascii=False, indent=1) + "\n")
    open(f"{OUT}/prompt_after_02.txt", "w", encoding="utf-8", newline="\n").write(after_txt)
    meas = {}
    for lv, d in (("std", "a2"), ("adv", "b1b")):
        p = open(f"{V5}/{d}/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt", encoding="utf-8").read()
        cand = extract_candidate_block(p)
        assert p.startswith(bs.rstrip()) and p.rstrip().endswith(bg.strip())
        aft = render(after_static(lv), AFTER_TAIL, cand)
        open(f"{OUT}/specimen_after_{lv}_v5_02.txt", "w", encoding="utf-8", newline="\n").write(aft)
        tb, how = tokens(p)
        ta, _ = tokens(aft)
        t01 = None
        s01 = f"er064_output/kp_extraction_selection_opt_01/phase1_b/specimen_after_{lv}_v5_01.txt"
        if os.path.exists(s01):
            t01 = tokens(open(s01, encoding="utf-8").read())[0]
        meas[lv] = dict(before_total=tb, after_total_02=ta, after_total_01=t01, delta_vs_before=ta - tb, delta_pct=round((ta - tb) / tb * 100, 1),
                        prompt_text_only_before=tokens(bs)[0] + tokens(bg)[0], prompt_text_only_after_02=tokens(after_static(lv))[0] + tokens(AFTER_TAIL)[0],
                        after_head_02=tokens(after_static(lv))[0], after_tail_02=tokens(AFTER_TAIL)[0], candidates_and_sentences=tokens(cand)[0],
                        after_prompt_sha256=sha(aft), before_prompt_sha256=sha(p), chars_after=len(aft), chars_before=len(p))
    meas["schema_tokens"] = dict(before=tokens(json.dumps(B1.schema_json(False)["schema"], ensure_ascii=False))[0],
                                 after_02=tokens(json.dumps(schema_json()["schema"], ensure_ascii=False))[0])
    meas["schema_identical_to_production"] = schema_json() == B1.schema_json(False)
    meas["token_method"] = how
    json.dump(meas, open(f"{OUT}/token_measure_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(meas, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
