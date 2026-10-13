"""KP-EXTRACTION-SELECTION-OPT-01 委任_01B: Phase 1-B 選定Prompt見直し(Trial専用、Production非接続、API呼出なし)。

Before = Production現行(import元定数を逐語取得)。After = Trial専用の改善Prompt(本ファイル内の定数)。
出力: er064_output/kp_extraction_selection_opt_01/phase1_b/ 配下。
"""
from __future__ import annotations
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("TIKTOKEN_PATH"):
    sys.path.insert(0, os.environ["TIKTOKEN_PATH"])
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract
import er003_key_words_min_unit as p2g

OUT = "er064_output/kp_extraction_selection_opt_01/phase1_b"
TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"
DEV_MSG = p2g.SELECTOR_DEVELOPER_MESSAGE


# ---------------- Before(Production現行、逐語取得) ----------------
def before_static():
    t = open(TEMPLATE_PATH, encoding="utf-8").read()
    return selector01.extract_static_instructions(t)


BEFORE_GUIDANCE = contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE

CAND_HEADERS = ["【Topic】title: {article_title}", "【重要な単語・単語群候補】", "【phrase / idiom / phrasal verb候補】",
                "【word候補】", "【SENTENCE REFERENCE】(文脈参照専用。この表の文字列をそのままitemへ書かないでください)"]

# ---------------- After(Trial専用) ----------------
LEVEL_RULE = {
    "std": "この記事は初級(A2相当)の学習者向けです。日常で頻出する基本的な句は、すでに知っているものとして扱ってください。",
    "adv": "この記事はB1相当の学習者向けです。基本義と異なる意味で使われる句動詞や、文脈で意味が変わるコロケーションは、初見で難しいものとして同列に評価してください。",
}

AFTER_HEAD = """以下の英語記事の候補一覧から、初回リスニングで意味を取れず、その後の理解を止める可能性が高い表現を、支援価値の高い順にちょうど5個選んでください。

【判断の基準】
音声で一度だけ聞いたときに意味を処理できるかを最優先してください。優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。

未知単語、題材固有表現、短い複数語パターン、比喩・感情表現を同格の候補として扱ってください。構成語から意味を容易に推測できる透明表現は、記事上重要でも優先度を下げてください。

優先順位が同程度の候補どうしでは、定着した自然な表現(慣用句、自然なコロケーション、本文で非字義的に使われる表現、聞き取りにくいが他の文脈でも使える表現)を、構成語どおりの連語や、この記事だけの言い回しより優先してください。区分名(idiom等)やevidenceラベルがあるだけでは選ばないでください。

学習者がすでに知っている可能性が高い基本の連語(構成語どおりの意味で使われるもの)は、同程度の他の候補があれば優先度を下げてください。候補が乏しい場合は選んでかまいません。句動詞や、本文で基本義と異なる意味で使われる表現は下げないでください。{level_rule}CEFRなどの語彙表の等級だけでは判断せず、表現の定着度と本文での使われ方で判断してください。

【学ぶ単位】
学ぶ価値のあるまとまりを選んでください。動詞表現は目的語・補語まで、名詞表現は修飾語まで含めた、用法が成り立つ最小のまとまりが望ましいです(例: rateよりinterest rate、take careよりtake care of)。候補の行に「含む:Cn」「含まれる:Cn」とある場合、短い方は長い方の一部です。同じ内容を両方選ばず、動詞の目的語・補語など用法を成り立たせる要素を含む側を選んでください。長い側が主語・時・場所の付け足しだけなら短い側を選んでください。
display_phraseは1〜5語にしてください。完全文、主語と有限動詞を持つ節は禁止です。動詞表現は本文の時制を残さず、原則として基本形へ直してください。受動表現を学ぶ価値がある場合は、be + past participleの見出し形を使用できます。

【役割】
5個のうち1個は、この記事に特有で、事前に意味・用法・音を理解しておくと本文を追いやすくなる語または表現を選んでください(key_phrase_role="topic")。汎用性や一般的な学習重要度は高くなくてかまいません。判断基準は「これを知らないと主要な主張や展開を取り違えるか、知っていると本文を明確に追いやすくなるか」です。人名・企業名・ブランド名・地名だから、専門用語だから、比喩だから、といった種類だけでは選びません。該当が見当たらなくても、topicを空にせず、最も近い候補を選んでください。
残り4個(key_phrase_role="important")には、他の記事でも使える定着した表現を選んでください。この記事だけの創作的な言い回しは、importantに選ばないでください(本文理解への貢献が大きく他の候補より優れる場合に限り、topicには選べます)。key_phrase_roleは、候補の区分とは独立した、選定後の役割ラベルです。
各itemのestablished_or_article_specificには、その表現が他の記事でも通用する定着した表現ならestablished、この記事だけの言い回しならarticle_specific、判断できなければunsureを書いてください(記録用で、選定の可否には使いません)。

【日本語グロス】
日本語グロスは、日本人の英語学習者が音声で聞いてすぐ意味を理解できる、自然で平易な現代日本語の一文にしてください。直訳調や、「常態」「是正」のような硬い報道語・漢語は避けてください。括弧（　）で別訳・専門用語・補足を書き添えないでください。「～」「〜」は辞書的に自然な範囲(例: 「～を示す」)でのみ使い、「…」のようなプレースホルダー記号は使わないでください。数字を含める場合は算用数字ではなく漢数字(一、二、三…)で書いてください。「ソロ旅行を～％とする」のように数値を補わないと意味が成立しない句・グロスは選ばず、それ単体で意味が成立するものを選んでください。
"""

AFTER_TAIL = """
【出力のルール】
- 最終的に選ぶ5件は、必ず上記の候補一覧の中から選んでください。候補に無い新しい表現を作らないでください。
- 5個のうち少なくとも1個は、[重要な単語・単語群候補]区分から選んでください(記事理解・再利用価値の高い重要な名詞・専門用語・複合語)。
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。良い候補が不足する場合(基本的な連語しか無い場合を含む)のみ[word候補]区分で補ってください。
- 各itemのsource_candidate_idには、候補一覧の各行のcandidate ID(例: C7)のうち、実際に選んだ候補のIDを1つだけ指定してください。本文の文字列(source_sentence/source_span相当の自由記述)は一切書かないでください。
- surface_echoには、選んだ候補が表す表現を短く(1〜6語程度)書いてください。これは内部確認用の参考情報であり、正誤判定には使用しません。
- 上記5件とは別に、backup_itemとして、重要語・重要表現(key_phrase_role="important")の予備候補を、上記5件とは異なるcandidate IDで1件選んでください。topicが正しく選べた場合でも、backup_itemは必ず1件返してください(その場合は採用されません)。
"""

AFTER_EXTRA_FIELD = {"established_or_article_specific": {"type": "string", "enum": ["established", "article_specific", "unsure"]}}


def after_static(level: str) -> str:
    return AFTER_HEAD.replace("{level_rule}", LEVEL_RULE[level])


def after_template() -> str:
    return AFTER_HEAD.replace("{level_rule}", "{LEVEL_RULE}")


def render(static, tail, shortlist_text):
    return static.rstrip() + "\n\n" + shortlist_text.strip("\n") + "\n" + tail.rstrip() + "\n"


def extract_candidate_block(prompt_text: str) -> str:
    i = prompt_text.index("【Topic】title:")
    j = prompt_text.index("【選定方針】")
    return prompt_text[i:j]


def schema_json(after: bool):
    s = contract.build_json_schema(["C1", "C2"])
    if after:
        s = json.loads(json.dumps(s))
        item = s["schema"]["properties"]["items"]["items"]
        item["properties"].update(AFTER_EXTRA_FIELD)
        item["required"] = list(item["required"]) + ["established_or_article_specific"]
        s["schema"]["properties"]["backup_item"] = item
    return s


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def tokens(s: str):
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(s)), "tiktoken o200k_base"
    except Exception as e:  # pragma: no cover
        return int(len(s) * 0.9), f"fallback chars*0.9 ({type(e).__name__})"


def main():
    os.makedirs(OUT, exist_ok=True)
    bs, bg = before_static(), BEFORE_GUIDANCE
    sep = "\n" + "=" * 20 + " "
    props_b = schema_json(False)["schema"]["properties"]["items"]["items"]["properties"]
    props_a = schema_json(True)["schema"]["properties"]["items"]["items"]["properties"]
    before_txt = (f"{sep}[1] DEVELOPER MESSAGE (prod.SELECTOR_DEVELOPER_MESSAGE) =====\n{DEV_MSG}\n"
                  f"{sep}[2] USER MESSAGE 先頭: 静的instructions(b1_p2_keywords_l_prompt_template.txt を extract_static_instructions で取得、逐語) =====\n{bs}\n"
                  f"{sep}[3] USER MESSAGE 中段: 候補セクション形式(build_lightweight_user_message、各行 `- id: Cn | candidate: ... | type: ... | occ: n | evidence: ... | sentence: Sn`) =====\n"
                  + "\n".join(CAND_HEADERS) + "\n"
                  f"{sep}[4] USER MESSAGE 末尾: _FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE (逐語) ====={bg}\n"
                  f"{sep}[5] OUTPUT SCHEMA(strict json_schema; items 5件 + backup_item。item properties) =====\n"
                  + json.dumps(props_b, ensure_ascii=False, indent=1) + "\n")
    after_txt = (f"{sep}[1] DEVELOPER MESSAGE (変更なし) =====\n{DEV_MSG}\n"
                 f"{sep}[2] USER MESSAGE 先頭: 静的instructions(Trial専用。{{LEVEL_RULE}}はStd/Advで差し替え) =====\n{after_template()}\n"
                 f"{sep}[2a] LEVEL_RULE std =====\n{LEVEL_RULE['std']}\n{sep}[2b] LEVEL_RULE adv =====\n{LEVEL_RULE['adv']}\n"
                 f"{sep}[3] USER MESSAGE 中段: 候補セクション形式(変更なし。Phase 1-Aが注釈 `| 含む:Cn` `| 含まれる:Cn` `| タグ:..` を行末に付ける場合のみ追加) =====\n"
                 + "\n".join(CAND_HEADERS) + "\n"
                 f"{sep}[4] USER MESSAGE 末尾: 出力のルール(Trial専用) ====={AFTER_TAIL}\n"
                 f"{sep}[5] OUTPUT SCHEMA(item propertiesに1フィールド追加、他は不変) =====\n"
                 + json.dumps(props_a, ensure_ascii=False, indent=1) + "\n")
    open(f"{OUT}/prompt_before_01.txt", "w", encoding="utf-8", newline="\n").write(before_txt)
    open(f"{OUT}/prompt_after_01.txt", "w", encoding="utf-8", newline="\n").write(after_txt)

    V5 = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"
    meas = {}
    for lv, d in (("std", "a2"), ("adv", "b1b")):
        p = open(f"{V5}/{d}/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt", encoding="utf-8").read()
        cand = extract_candidate_block(p)
        assert p.startswith(bs.rstrip()), "v5実run先頭がstatic instructionsと一致しない"
        assert p.rstrip().endswith(bg.strip()), "v5実run末尾がguidanceと一致しない"
        aft = render(after_static(lv), AFTER_TAIL, cand)
        open(f"{OUT}/specimen_after_{lv}_v5_01.txt", "w", encoding="utf-8", newline="\n").write(aft)
        tb, how = tokens(p)
        ta, _ = tokens(aft)
        meas[lv] = dict(before_total=tb, after_total=ta, delta=ta - tb, delta_pct=round((ta - tb) / tb * 100, 1),
                        before_static=tokens(bs)[0], before_guidance=tokens(bg)[0],
                        candidates_and_sentences=tokens(cand)[0],
                        after_head=tokens(after_static(lv))[0], after_tail=tokens(AFTER_TAIL)[0],
                        before_prompt_sha256=sha(p), after_prompt_sha256=sha(aft),
                        chars_before=len(p), chars_after=len(aft))
    meas["schema_tokens"] = dict(before=tokens(json.dumps(schema_json(False)["schema"], ensure_ascii=False))[0],
                                 after=tokens(json.dumps(schema_json(True)["schema"], ensure_ascii=False))[0])
    meas["schema_tokens"]["delta"] = meas["schema_tokens"]["after"] - meas["schema_tokens"]["before"]
    meas["developer_message_tokens"] = tokens(DEV_MSG)[0]
    meas["token_method"] = how
    meas["files"] = {f: hashlib.sha256(open(f"{OUT}/{f}", "rb").read()).hexdigest() for f in
                     ("prompt_before_01.txt", "prompt_after_01.txt", "specimen_after_std_v5_01.txt", "specimen_after_adv_v5_01.txt")}
    json.dump(meas, open(f"{OUT}/token_measure_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(meas, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
