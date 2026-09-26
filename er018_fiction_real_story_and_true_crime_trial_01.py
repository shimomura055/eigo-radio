# ============================================================
# er018_fiction_real_story_and_true_crime_trial_01.py
# 管理ID: FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01
# ============================================================
# 目的: FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02(VALIDATED)で
# 検証済みのGate(G1一次テキスト直接HTTP GET確認/G2日本+米国双方の権利確認/
# G3短編化可能/G4 Story品質4基準)をそのまま使い、
#   (3-A) Real Story追加1本(Livingstone「The Lion That Rose Again」とは
#         別の実話・回想録・探検記等)
#   (3-B) Historical True Crime 1本(1930年以前の事件・PD史料、事実改変禁止)
# を新規に選定・Story化するTrial。
#
# 候補調査・一次テキスト確認・権利確認(S-1/S-2)はSonnetがrequestsで直接
# HTTP GETし(web_search未使用、$0)、その結果をSEEDS辞書(下記)へ手動で
# 記述している。本スクリプトが担当する範囲はSeed化(S-3)とStory本文生成
# (S-4)のみで、Trial-02のSEED_DEVELOPER_MESSAGE/SEED_USER_TEMPLATE/
# SEED_JSON_SCHEMA/STORY_PROMPT_TEMPLATEをそのまま流用する(委任文の指示
# どおり、体裁・難易度をTrial-02と揃えるため)。
#
# True Crime(3-B)は文学Fiction系の命名規則(主人公のみ固有名可)を適用せず、
# 実在の事件関係者の実名をそのまま保持する(委任文3-B「事実を勝手に改変
# しない(日付・人物名・経緯は資料どおり)」を優先)。これはFiction家族の
# 既定命名規則からの意図的な逸脱であり、Sonnetの判断で正式仕様へ反映する
# ものではない(REPORTで明示、Fable/ユーザー判断待ち)。
#
# Status: Trial専用、未承認draft実装(APPROVED_FOR_PRODUCTIONではない)。
# 到達上限: VALIDATED。Production Fiction仕様への反映は本タスクの対象外。
#
# 実行方法(root直下):
#   .venv/Scripts/python.exe er018_fiction_real_story_and_true_crime_trial_01.py \
#       --out-dir er018_output/fiction_real_story_and_true_crime_trial_01 \
#       --step seed --budget-jpy 200
#   ...--step story --budget-jpy 200
#   ...--step assemble
# ============================================================
from __future__ import annotations

import argparse
import json
import os

from dotenv import load_dotenv

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er003_v1_en_direct_vfl_01_generate as vfl01  # get_client()のみ再利用
import er018_fiction_story_dna_e_axis_redesign_01 as e_axis  # 共通ヘルパー再利用(read-only import)

load_dotenv()

THEME_TAG = "FICTION_REAL_STORY_AND_TRUE_CRIME_TRIAL_01"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
USD_JPY = e_axis.USD_JPY
PRICING_SNAPSHOT_PATH = e_axis.PRICING_SNAPSHOT_PATH

# ------------------------------------------------------------
# 2本のStory Seed対象。source_briefはSonnetが実際に一次テキストをHTTP GET
# (requests)で取得し、自分の言葉で書いたもの(引用の丸写しではない)。
# rights_statusは実際にfetchしたURL・確認文言・確認日付。
# 選定理由・不採用候補との比較はcandidates_real.md/candidates_true_crime.md
# 参照。
# ------------------------------------------------------------
SEEDS = [
    {
        "key": "real_story_nellie_bly",
        "label_en": "Real story / investigative memoir",
        "label_ja": "実話・潜入取材記",
        "title": "Feigning insanity to expose an asylum (Nellie Bly, "
                 "\"Ten Days in a Mad-House\")",
        "source_url": "https://www.gutenberg.org/ebooks/59899.txt.utf-8",
        "rights_status_quote": "Public domain in the USA. (Project Gutenberg ebook "
                                 "#59899, \"Ten Days in a Mad-House; or, Nellie Bly's "
                                 "Experience on Blackwell's Island.\")",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is a real newspaper stunt carried out by journalist Nellie Bly in "
            "1887 (Project Gutenberg #59899, fetched and confirmed directly, plus "
            "Wikipedia confirming her dates 1864-1922). Her editor at the New York "
            "World asked her to get herself committed to the insane asylum on "
            "Blackwell's Island so she could report on conditions there from the "
            "inside. The night before, alone in her boarding-house room, she practices "
            "acting insane in front of a mirror (staring wide-eyed, feeling genuinely "
            "frightened by her own reflection) even though she has never seen an "
            "insane person and doubts she can fool trained doctors. The ruse works "
            "completely: a judge, several doctors, and reporters all pronounce her "
            "insane after only a brief, superficial look at her. Once inside the "
            "asylum, she stops performing and simply acts and speaks normally and "
            "asks to be released -- but discovers, with real dread, that the more "
            "calmly and sanely she talks, the more the doctors are convinced she is "
            "insane (one exchange: she challenges a doctor to actually test her "
            "pulse, her eyes, her reflexes, rather than simply doubt her; he refuses, "
            "certain she is 'raving'). She witnesses the cruelty and neglect around "
            "her (nurses who provoke frightened patients for amusement, cold baths, "
            "spoiled food) and comes to believe that any sane woman placed there would "
            "eventually be driven to become genuinely unwell just from the conditions "
            "themselves. After ten days, a lawyer sent by her newspaper arrives and "
            "she is released -- feeling real, unexpected sorrow at leaving the other "
            "women behind, before the relief of freedom takes over. Her subsequent "
            "reporting and Grand Jury testimony led to a real increase in funding and "
            "oversight for asylum care in New York."
        ),
        "conversion_plan": (
            "Keep this as a faithful, simplified retelling of the real event -- the "
            "newspaper assignment, the asylum setting, and the central irony (acting "
            "sane is read as proof of insanity) are the entire point and must not be "
            "cut or replaced with an unrelated modern premise. Tell it in the first "
            "person as the reporter. Per this family's naming rule, only the "
            "protagonist may have a personal name; use her real name, Nellie (per the "
            "true story she used the assumed name 'Nellie Brown' during the stunt "
            "itself, but you do not need to dwell on that detail if it does not fit "
            "the word count). Refer to other people only by role (the doctor, a "
            "nurse, another patient, the lawyer), not by their real names from the "
            "source (do not invent new proper names either). Keep the core sequence: "
            "rehearsing insanity alone at night, the doctors and judge easily fooled, "
            "the ironic reversal once she tells the truth inside, at least one "
            "concrete detail of the conditions inside, and the release with a moment "
            "of real regret at leaving the other women. Around 300-350 words, first "
            "person."
        ),
    },
    {
        "key": "true_crime_eugene_aram",
        "label_en": "Historical true crime",
        "label_ja": "歴史的犯罪実話",
        "title": "The schoolmaster's buried secret (Eugene Aram case, from Camden "
                 "Pelham, \"The Chronicles of Crime; or, The New Newgate Calendar\", "
                 "1841)",
        "source_url": "https://www.gutenberg.org/ebooks/46585.txt.utf-8",
        "rights_status_quote": "Public domain in the USA. (Project Gutenberg ebook "
                                 "#46585, \"The Chronicles of Crime or The New Newgate "
                                 "Calendar\", vol. 1, by Camden Pelham, 1841)",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is a real, documented 18th-century English murder case (Project "
            "Gutenberg #46585, fetched and confirmed directly; the case is also "
            "independently well documented on Wikipedia, e.g. the discovery date and "
            "trial date match). On the night of 8 February 1745, in Knaresborough, "
            "Yorkshire, a self-taught scholar named Eugene Aram, together with a man "
            "named Richard Houseman, murdered a shoemaker named Daniel Clarke, who had "
            "recently gathered a large quantity of silver and jewels on credit "
            "(claiming he would resell them for profit) and was persuaded to walk out "
            "with them at night to 'discuss how to dispose of the goods.' Clarke was "
            "never seen again; people assumed he had absconded with the goods. Aram "
            "continued working respectably as a schoolmaster/usher in various English "
            "towns for the next fourteen years, apparently untroubled. In 1758, a "
            "labourer digging for stone at St. Robert's Cave near Knaresborough "
            "accidentally uncovered a human skeleton. A coroner's inquest was held; "
            "Aram's own wife (from whom he was by then estranged) said she suspected "
            "her husband and Houseman had murdered Clarke. Houseman, questioned and "
            "asked to handle one of the bones, panicked and blurted out, 'This is no "
            "more Daniel Clarke's bone than it is mine!' -- and under further "
            "questioning confessed that Aram had killed Clarke and that the true "
            "burial spot was slightly different from where the first skeleton was "
            "found; a second skeleton was then found exactly where he said. Aram was "
            "traced to a teaching post in Lynn, Norfolk, arrested, and tried at York "
            "in August 1759. He gave a long, learned, and much-admired written defence "
            "arguing that human bones are commonly found in old hermitages and "
            "battlefields and prove nothing -- but the jury convicted him quickly. "
            "After sentencing he privately confessed his guilt to the clergymen "
            "attending him (though he claimed, when asked, that his motive had been "
            "jealousy over his wife). He was executed at York on 16 August 1759."
        ),
        "conversion_plan": (
            "This is Historical True Crime, not the Fiction family: keep the real "
            "names exactly as in the source (Eugene Aram, Daniel Clarke, Richard "
            "Houseman) rather than reducing everyone but the protagonist to a role "
            "label -- do not invent or change any name, date, or the sequence of "
            "events. Do not invent any dialogue, motive, or psychological detail that "
            "is not in the source brief above (Houseman's line and Aram's claimed "
            "jealousy motive are both from the source and may be used or paraphrased; "
            "do not add new invented lines). You may omit or compress period detail "
            "not essential to the arc (e.g. the full text of Aram's courtroom defence, "
            "or the more graphic detail of his later suicide attempt in his cell, "
            "which is in the original source but is not required for this length and "
            "can be simplified to 'he was executed' without inventing a different "
            "cause). Keep the core shape: the murder and the fourteen years of hiding "
            "in plain sight, the accidental discovery of the bones, Houseman's panic "
            "and confession, Aram's arrest and the contrast between his eloquent "
            "defence and the simple physical evidence against him, and the outcome. "
            "Third person, matter-of-fact and not sensationalized. "
            "IMPORTANT (editorial revision after review): the previous draft flattened "
            "the case's most striking real detail into a vague phrase like 'gives "
            "information that leads to the second burial site,' which loses what "
            "made this case land. When listing seed_elements, keep two things concrete "
            "and specific rather than paraphrased away: (1) Houseman's exact "
            "exclamation as a direct quotation -- 'This is no more Daniel Clarke's "
            "bone than it is mine!' -- and the fact that this single remark is what "
            "first made people suspicious of him (they wondered how he could possibly "
            "know that, unless he had seen the real bones himself); and (2) the "
            "concrete, verifiable detail that Houseman's confession specified exactly "
            "where the true burial spot was (the head lying a little further to the "
            "right than the first skeleton found), and that when people dug there, a "
            "second skeleton was found in exactly that spot -- this precise match "
            "between what Houseman said and what was found is the detail that makes "
            "the case striking, and it must survive into the final story as a "
            "concrete beat, not a summary sentence. Also: the final story should not "
            "end by restating or summarizing the whole case again -- it should close "
            "with one or two sentences that end the story plainly instead of "
            "repeating what has already been told. Aim for about 320-380 words "
            "(never below 300 words, and keep it under 420 words). This word count "
            "is a hard floor, not a soft suggestion: a previous draft came in at "
            "only 263 words and was rejected as too thin. If your draft feels short, "
            "do not pad it with repetition or a restated summary -- instead add more "
            "concrete narrative detail that is already implied by the case (for "
            "example, a beat or two more on the questioning, the digging, or the "
            "trial) without inventing new facts, dialogue, or motives. Two more "
            "firm requirements from editorial review of an earlier draft: (a) the "
            "specific execution date and place must appear explicitly near the end, "
            "in words close to 'executed at York on 16 August 1759' -- do not just "
            "say 'he was executed' without the date and place; (b) the very last "
            "paragraph must be only 1-2 sentences, and it must not repeat any fact "
            "already stated earlier in the piece (for example, do not say again that "
            "he lived as a respected schoolmaster or that fourteen years passed) -- "
            "it should simply close the story, not recap it. FINAL CHECK BEFORE YOU "
            "ANSWER: several earlier drafts came in far too short (245, 259, and 263 "
            "words) and were all rejected for being too thin -- count the words in "
            "your draft before finalizing it, and if it is under 320 words, add 2 to "
            "4 more full sentences of concrete, source-consistent detail (for "
            "example: a little more on the night walk out of town, the coroner's "
            "inquest itself, the moment of digging at the cave, or the courtroom "
            "scene) until you reach at least 320 words -- do not submit a short "
            "draft, and do not reach the target by inventing new facts."
        ),
    },
]


# ------------------------------------------------------------
# S-3 Story Seed化(Trial-02のSEED_DEVELOPER_MESSAGE/SEED_USER_TEMPLATE/
# SEED_JSON_SCHEMAを逐語で再利用。委任文により変更禁止)
# ------------------------------------------------------------
SEED_DEVELOPER_MESSAGE = (
    "You help an English-learning magazine's Fiction team turn a real, rights-cleared "
    "source into a reusable \"Story Seed\": an abstraction that keeps the elements needed "
    "to write a new short-story version of the SAME real event, and explicitly discards "
    "only what does not fit a short A2-level piece (minor subplots, excess names, excess "
    "historical/technical detail). Unlike a from-scratch fictional story, this is not "
    "supposed to be a totally new, unrelated plot -- it should still recognizably be a "
    "retelling of the real source event. This is not a summary for readers -- it is an "
    "internal planning document. Do not quote long passages from the source; describe "
    "things in your own words."
)

SEED_USER_TEMPLATE = """[Source brief -- written by the editor, in their own words, not quoted from
the original]
{source_brief}

[Conversion plan -- written by the editor]
{conversion_plan}

[Task -- produce a Story Seed]
1. original_summary: 3 to 5 sentences, in your own words, summarizing what actually
   happened/what the source is about.
2. seed_elements: up to 6 short bullet-style strings -- the elements that must carry over
   into the new story so that it is still recognizably a retelling of this real event
   (key situation, turning point, emotional core, any detail the conversion plan says must
   not be cut).
3. discarded_elements: short strings -- proper names, minor subplots, or excess period/
   technical detail that should be simplified away or dropped for an A2-level short piece.
4. conversion_plan: 2 to 4 sentences describing how to turn this into an English-learning
   short story: whether to keep or modernize the setting, first-person or third-person,
   and roughly how long/what level (use the editor's conversion plan above as the basis,
   restated in your own words)."""

SEED_JSON_SCHEMA = {
    "name": "fiction_external_story_seed",
    "schema": {
        "type": "object",
        "properties": {
            "original_summary": {"type": "string"},
            "seed_elements": {
                "type": "array", "minItems": 2, "maxItems": 6,
                "items": {"type": "string"},
            },
            "discarded_elements": {
                "type": "array", "minItems": 1, "maxItems": 6,
                "items": {"type": "string"},
            },
            "conversion_plan": {"type": "string"},
        },
        "required": [
            "original_summary", "seed_elements", "discarded_elements",
            "conversion_plan",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def call_seed(client, seed_spec: dict) -> dict:
    stage = f"seed_{seed_spec['key']}"
    user_message = SEED_USER_TEMPLATE.format(
        source_brief=seed_spec["source_brief"],
        conversion_plan=seed_spec["conversion_plan"],
    )
    kwargs = dict(
        model=MODEL_LUNA,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": SEED_DEVELOPER_MESSAGE},
            {"role": "user", "content": user_message},
        ],
        text={"format": {"type": "json_schema", **SEED_JSON_SCHEMA}},
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    if response.model != MODEL_LUNA:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={MODEL_LUNA}, actual={response.model})")
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError(f"{stage}: 応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "user_message": user_message, "model": response.model,
            "response_id": response.id}


def step_seed(out_dir: str, budget_jpy: float, only_key: str | None = None) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_seed", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    seeds = [s for s in SEEDS if s["key"] == only_key] if only_key else SEEDS
    for seed_spec in seeds:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        result = call_seed(client, seed_spec)
        seed = dict(result["parsed"])
        seed["rights_status"] = {
            "url": seed_spec["source_url"],
            "confirmation_quote": seed_spec["rights_status_quote"],
            "confirmed_date": seed_spec["confirmed_date"],
        }
        seed["title"] = seed_spec["title"]
        e_axis.save_json(f"{sys_dir}/seed.json", seed)
        e_axis.save_json(f"{sys_dir}/seed_api_meta.json", {
            "developer_message": SEED_DEVELOPER_MESSAGE,
            "user_message": result["user_message"], "model": result["model"],
            "response_id": result["response_id"],
        })
        print(f"[step_seed][{seed_spec['key']}] DONE.")
        budget_guard(f"after_seed_{seed_spec['key']}", out_dir, log_path, budget_jpy)

    print("[step_seed] ALL DONE.")


# ------------------------------------------------------------
# S-4 Story本文生成(Trial-02のSTORY_PROMPT_TEMPLATEを逐語で再利用)
# ------------------------------------------------------------
STORY_PROMPT_TEMPLATE = """[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;
this is NOT a summary to reproduce, just raw material]
{seed_elements_block}

[How to convert it]
{conversion_plan}

[Common principles for this story family]
{common_principles}

[Your single job]
Write a short story inspired by the Story Seed above. Make a reader genuinely feel \
something, want to keep reading, and feel some excitement and a little tension along \
the way. Do not follow any fixed structure, fixed number of scenes, fixed number of \
emotional turns, or a fixed ending shape -- choose whatever narrative shape makes THIS \
Story Seed land most strongly. Do not just retell the original source with no changes at \
all, but also do not force superficial changes for their own sake -- a faithful, simplified \
retelling of the real event is welcome here.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; {max_characters} at the absolute most \
if truly needed. Only the main character (the protagonist) may be given a personal \
name. Every other person should be referred to through their relationship to the main \
character (for example: her mother, his father, her friend, their daughter, his \
neighbor) instead of a separate name. Do not add named characters that are not \
necessary for the story.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text is about {word_target} words (roughly \
{range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""

# True Crime用: キャラクター/命名ルールの文言を差し替えた版(実名保持を明示)。
STORY_PROMPT_TEMPLATE_TRUE_CRIME = """[Story Seed -- a real, documented historical crime case, faithfully retold; \
this is NOT a summary to reproduce verbatim, but facts/names/dates must not be changed]
{seed_elements_block}

[How to convert it]
{conversion_plan}

[Common principles for this story family]
{common_principles}

[Your single job]
Write a short true-crime story built from the Story Seed above. Make a reader genuinely \
feel some tension and curiosity about how the case unfolds. Do not follow a fixed \
structure -- choose whatever narrative shape makes this real case land most strongly. \
This must be a faithful, simplified retelling of the real historical event: do not \
invent facts, dialogue, motives, or details that are not part of the Story Seed. You may \
compress, omit minor detail, or paraphrase in your own words for length and clarity, and \
you may state plainly where something is uncertain, but do not add invented content \
presented as fact. Do not needlessly sensationalize violence or make victim descriptions \
more graphic than necessary, but also do not sand the story down until it loses what made \
this case genuinely striking.

[Names -- keep the real ones]
Unlike this magazine's usual fiction pieces, this is a historical true-crime account: use \
the real names of the people involved exactly as given in the Story Seed (do not invent \
new names, and do not reduce secondary figures to unnamed roles only, though you may refer \
to people by role in addition to name where that reads more naturally).

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text is about {word_target} words (roughly \
{range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear who is being discussed at each point.

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""

TRUE_CRIME_KEYS = {"true_crime_eugene_aram"}


REQUIRED_SEED_SPEC_KEYS = [
    "key", "label_en", "label_ja", "title", "source_url", "rights_status_quote",
    "confirmed_date", "source_brief", "conversion_plan",
]


def validate_seed_spec(seed_spec: dict) -> list[str]:
    """SEEDSの各エントリが必須キーを備えているかをオフラインで検証する
    (API呼び出し不要、_test_01.py用)。欠落キーのリストを返す(空なら問題なし)。"""
    return [k for k in REQUIRED_SEED_SPEC_KEYS if not seed_spec.get(k)]


def check_word_count_ok(word_count: int) -> bool:
    """委任文の目安(280-420語)を満たすかをオフラインで判定する(_test_01.py用)。"""
    low, high = e_axis.WORD_ACCEPTABLE_RANGE
    return low <= word_count <= high


def build_story_prompt(seed: dict, seed_key: str) -> str:
    seed_elements_block = "\n".join(f"- {e}" for e in seed["seed_elements"])
    template = (
        STORY_PROMPT_TEMPLATE_TRUE_CRIME if seed_key in TRUE_CRIME_KEYS
        else STORY_PROMPT_TEMPLATE
    )
    return template.format(
        seed_elements_block=seed_elements_block,
        conversion_plan=seed["conversion_plan"],
        common_principles=e_axis.COMMON_PRINCIPLES,
        max_characters=e_axis.MAX_CHARACTERS, word_target=e_axis.WORD_TARGET,
        range_low=e_axis.WORD_ACCEPTABLE_RANGE[0],
        range_high=e_axis.WORD_ACCEPTABLE_RANGE[1],
    )


def step_story(out_dir: str, budget_jpy: float, only_key: str | None = None) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_story", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    seeds = [s for s in SEEDS if s["key"] == only_key] if only_key else SEEDS
    for seed_spec in seeds:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story_model = routing.require_model_or_override(
            "A2_WRITER", routing.WRITER_MODEL,
            override_reason="FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01: 外部Public "
                             "Domainソース(実話/歴史的犯罪記録)をprimary-text確認済みで"
                             "Seed化した短編生成にA2_WRITER Approved Model(Luna)を転用"
                             "(新規process未定義、コスト影響なし、DEV/Trial限定)")
        prompt = build_story_prompt(seed, seed_spec["key"])
        e_axis.save_text(f"{sys_dir}/story_prompt.txt", prompt)

        def _call():
            with cl.logging_context(THEME_TAG, f"story_{seed_spec['key']}"):
                return e_axis.generate_story(client, story_model, "high", prompt)

        story_result, attempts = e_axis.call_with_retry(_call, max_attempts=2)
        e_axis.save_text(f"{sys_dir}/story.md", story_result["raw_text"].strip() + "\n")
        e_axis.save_json(f"{sys_dir}/api_meta.json", {
            "model": story_result["model"], "response_id": story_result["response_id"],
            "effort": "high", "attempts": attempts,
        })
        word_count = len(story_result["raw_text"].split())
        print(f"[step_story][{seed_spec['key']}] DONE. word_count={word_count} "
              f"model={story_result['model']}")
        budget_guard(f"after_story_{seed_spec['key']}", out_dir, log_path, budget_jpy)

    print("[step_story] ALL DONE.")


# ------------------------------------------------------------
# 費用計算(Luna token費用のみ。本Trialではweb_search未使用、$0)
# ------------------------------------------------------------
def load_pricing() -> dict:
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    prices = {}
    ws_price = None
    for entry in snapshot["prices"]:
        if entry.get("model") == "gpt-5.6-luna":
            prices[entry["meter"]] = entry["price"]
        if entry.get("meter") == "web_search_call":
            ws_price = entry["price"]
    prices["web_search_call"] = ws_price
    return prices


def compute_cost_jpy(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    pricing = load_pricing()
    total_usd = 0.0
    record_count = 0
    ws_call_total = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("theme") != THEME_TAG:
                continue
            record_count += 1
            if not rec.get("success", True):
                continue
            ws_calls = rec.get("web_search_call_count") or 0
            ws_call_total += ws_calls
            if pricing.get("web_search_call"):
                total_usd += (ws_calls / 1000) * pricing["web_search_call"]
            if rec.get("model_id") != "gpt-5.6-luna":
                continue
            input_tokens = rec.get("input_tokens") or 0
            cached = rec.get("cached_input_tokens") or 0
            output_tokens = rec.get("output_tokens") or 0
            non_cached_input = max(input_tokens - cached, 0)
            total_usd += (non_cached_input / 1_000_000) * pricing["input_tokens"]
            total_usd += (cached / 1_000_000) * pricing["cached_input_tokens"]
            total_usd += (output_tokens / 1_000_000) * pricing["output_tokens"]
    return {
        "total_usd": round(total_usd, 6), "total_jpy": round(total_usd * USD_JPY, 2),
        "record_count": record_count, "web_search_call_total": ws_call_total,
    }


def budget_guard(stage_label: str, out_dir: str, log_path: str, hard_cap_jpy: float) -> dict:
    cost = compute_cost_jpy(log_path)
    print(f"[budget_guard][{stage_label}] 累計={cost['total_jpy']} JPY (上限{hard_cap_jpy})")
    if cost["total_jpy"] > hard_cap_jpy:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] 累計{cost['total_jpy']} JPYが上限"
            f"{hard_cap_jpy} JPYを超過しました。STOP(以降のAPI呼び出しは行わない)。"
            f" これはGuardrail(PM_GOVERNANCE 7-6)であり、超過見込みが判明した時点で"
            f"継続条件を満たさない。")
    return cost


# ------------------------------------------------------------
# Step: assemble
# ------------------------------------------------------------
def step_assemble(out_dir: str) -> None:
    parts = [
        "# FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 -- stories_all.md\n",
        "Trial専用、Production採用ではない。最大Status: VALIDATED。\n",
    ]
    for seed_spec in SEEDS:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story = e_axis.load_text(f"{sys_dir}/story.md")
        parts.append(f"\n## {seed_spec['key']} -- {seed_spec['label_en']} "
                      f"({seed_spec['label_ja']})\n")
        parts.append(f"**Source**: {seed_spec['title']} -- {seed_spec['source_url']}\n")
        parts.append(f"**Rights**: {seed['rights_status']['confirmation_quote']} "
                      f"(confirmed {seed['rights_status']['confirmed_date']})\n")
        parts.append(f"**Seed elements**: {'; '.join(seed['seed_elements'])}\n")
        parts.append("```\n" + story.strip() + "\n```\n")
    e_axis.save_text(f"{out_dir}/stories_all.md", "\n".join(parts))

    log_path = f"{out_dir}/raw_usage_log.jsonl"
    final_cost = compute_cost_jpy(log_path)
    e_axis.save_json(f"{out_dir}/cost.json", final_cost)
    print(f"[step_assemble] DONE -> {out_dir}/stories_all.md, cost={final_cost}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["seed", "story", "assemble"])
    parser.add_argument("--budget-jpy", type=float, default=200.0)
    parser.add_argument("--only-key", default=None,
                         help="指定した場合、SEEDSのうち該当keyのみを処理する"
                              "(修正1回目: True Crimeのみ再生成しReal Story"
                              "[Nellie Bly]は再生成しないため)")
    args = parser.parse_args()

    if args.step == "seed":
        step_seed(args.out_dir, args.budget_jpy, only_key=args.only_key)
    elif args.step == "story":
        step_story(args.out_dir, args.budget_jpy, only_key=args.only_key)
    elif args.step == "assemble":
        step_assemble(args.out_dir)


if __name__ == "__main__":
    main()
