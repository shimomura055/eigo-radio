# ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_03: Trial専用Prompt群(Production非接触)。
# 注意: 監査Promptの欠陥例は、前回NG5類型(回帰セット=原文§4)と異なる「類似の別例」で示す(回帰セットの答えをPromptへ漏らさない)。

LEVEL_TXT = {
    "std": "Standard(学習者はA2〜B1の日本語話者。基本表現はA2。発展表現は日常会話で使える短い定型句・句動詞・コロケーション。核は2〜4語、B1語彙まで)",
    "adv": "Advanced(学習者はB1〜B2の日本語話者。基本表現はB1程度。発展表現はB1〜B2で、仕事・議論・ニュースにも応用できる自然な言い回し)",
}

EXTRACT = """あなたは日本人の英語学習者向け教材の編集者です。新コーナー「One Step Further」の出発点となる「基本表現」を、下の記事本文から正確に抽出します。
このコーナーは、平易な基本表現から「簡単な単語の組み合わせで、こんな言い方ができるのか」と学習者が感じる自然で実用的な発展表現へ進むもの。あなたの仕事は発展表現を作ることではなく、後で発展表現に置き換える価値がある基本表現を、本文から過不足なく切り出すことです。

# レベル
{level}

# 本文(文番号つき)
{numbered}

# 既に他のコーナーで扱う項目(これらと同じ核の表現は選ばない)
- Key Phrase / Word: {kp}
- 文法・構文: {grammar}

# 規則
1. 各候補は本文の1文から取る。quoteはその文を本文のとおり一字一句コピーする(改変・省略・つなぎ合わせ禁止)。
2. target_spanは、quoteの中の連続した語句(一字一句コピー)。文全体を対象にしない。2〜7語のまとまり(動詞句・コロケーション・短い節)にする。
3. prototypeは、target_spanを原型化した基本表現。時制・活用・人称を原型に戻す。固有名詞や、その文脈でしか通じない代名詞は someone / something / one's に一般化してよい。ただし、主語・否定・法助動詞(can/should等)・確信度(I think/probably等)・意図・時制の意味が重要なら、それらを失わずprototypeに残す。意味を変える原型化は禁止。
4. meaning_ja: target_spanが本文で表している意味を日本語で確定する(40字以内)。
5. must_preserve: 置き換えの際に必ず保つべき要素(例: 「否定」「法助動詞can」「主語I」「確信度が低い」)。なければ空リスト。
6. 次のような基本表現を選ぶ: 日本人学習者が自力で出す平易な言い方で、それより自然な・まとまりとして覚えやすい言い方(定型表現・句動詞・慣用表現・自然な構文)が実在しそうなもの。
   選ばないもの: 固有名詞・本文固有の事柄に依存する表現、他コーナーと同じ核の表現、単語1つを難語にするしかない表現、置き換える価値の乏しい基本語そのもの。
7. 本文にない事柄を足さない。無理に数を満たさない。最大{n}件、置換価値の高い順。

# 出力(JSONのみ)
{{"candidates": [{{"sentence_id": 文番号(整数), "quote": "", "target_span": "", "prototype": "", "meaning_ja": "", "must_preserve": [], "replace_value_ja": "なぜ置換価値があるか(25字以内)"}}]}}"""

GEN_CRITERIA = """# One Step Furtherの選定基準
- 目的: 日本人学習者が「聞いたことはあるが自分では使えない」「簡単な単語の組み合わせでこんな言い方ができるのか」と感じる、自然で実用的な発展表現を、まとまり(フレーズ・句動詞・慣用表現・定型表現・自然な構文)として覚えられること。難しい単語や長い文を作ることは目的ではない。
- 発展表現は、基本表現と「同じ状況で置き換えて使える」こと。主語・対象・肯否・法助動詞・確信度・意図・時制を変えない。基本表現にない感情・行動・理由・事情・節を足さない。元の文を残して後ろに何かを付け足す形は不可。
- 単語1つを難しい同義語に置換しただけは不可(例: be happy → be delighted、ask → inquire)。ただし、その単語が特定のコロケーションの一部として初めて成立するもの(例: make progress → make headway は headway が make とセットでしか使えないまとまり)は可。
- 基本表現とほぼ同じ語の並べ替え、不自然に凝った表現、使える場面が極端に狭い表現、スラング・古風・文語は不可。
- 基本表現と意味が完全には重ならない場合は、その差をdiff_ja に正直に書く。差が実用上重要になる候補は出さない。迷う候補は出さず、別の候補を探す。
- 品質を満たす候補が無い基本表現は candidates を空リストにする(無理に出さない)。"""

GEN = """あなたは日本人の英語学習者向け教材の編集者です。下の各「基本表現」について、新コーナー「One Step Further」に載せられる発展表現の候補を作ります。
入力は基本表現とその意味だけです。記事や人物の事情は与えられません(想像して足してはいけません)。

{criteria}

# 良い方向性の例(参考。そのまま選ばない)
- make some progress → make some headway(意味が近い。コロケーションのまとまり)
- 助言 You should decide. → It's your call to make.(callを判断の意味で使う。ただし「助言」と「決定権」で意味に差があるため、差はdiff_jaに書く)

# 欠陥の例(出してはいけない型。上の例とは別の例)
- 主語・対象の変更: my sister can drive me → this car gets me around town
- 事情の追加(元の文を残して足すだけ): I'm tired. → I'm tired, but I'm pushing through for the kids.
- 別の発言への飛躍: I think he's late because of traffic. → I suspect he's dodging the meeting.
- 単語だけの置換: be happy → be delighted
- 法助動詞・肯否の変更: I can't do it. → I won't do it.

# レベル別の制約
Standard: {std}
Advanced: {adv}
各基本表現のlevelに従う。

# 入力(基本表現)
{items}

# 出力(JSONのみ)。各基本表現につき最大{k}候補、価値の高い順。
{{"results": [{{"id": "基本表現のid", "candidates": [{{
  "further_expression": "発展表現(スロットは someone/something/one's で示す)",
  "further_meaning_ja": "発展表現の意味(日本語、30字以内)",
  "frame_base_en": "基本表現を使った中立の短文(10語前後、人名・感情・事情を入れない。基本表現の意味だけを表す)",
  "frame_further_en": "frame_base_enと同じ状況・同じ主語・同じ時制で、基本表現を発展表現に置き換えただけの文(語を足さない)",
  "diff_ja": "基本表現との意味・ニュアンスの差(完全に同じ意味なら空文字。差があれば正直に)",
  "point_ja": "学習ポイント(1〜2文・90字以内。使う場面・応用場面・間違えやすい点だけ。人物心理や選定理由は書かない)"
}}]}}]}}"""

DEFECT_CODES = """Defect codes (use these exact strings in "f"):
- subject_object: subject, object, or who-does-what-to-whom changed (e.g. "my sister can drive me" -> "this car gets me around town").
- added_info: adds an emotion, intention, action, reason, circumstance, or extra clause the base does not contain (e.g. "I'm tired." -> "I'm tired, but I'm pushing through for the kids.").
- polarity_modality: affirmative/negative, modality (can/should/must/will), certainty, intent, tense, or degree changed (e.g. "I can't do it." -> "I won't do it."; "it can help" -> "it is" drops the possibility modality).
- meaning_shift: the statement jumps to a different kind of meaning or relation even if it sounds related (e.g. "I think he's late because of traffic." -> "I suspect he's dodging the meeting"; "X can help me" -> "X is material for me to use" changes WHAT is said, not just strength).
- lengthened_only: the base wording is kept and merely extended/padded, or only reordered.
- word_swap_only: same sentence structure with ONE content word swapped for a harder/more formal synonym that works freely in any context (e.g. "be happy" -> "be delighted"). NOT a defect when the new word works only inside a fixed collocation/chunk that a learner memorizes as a unit (e.g. "very clear" -> "crystal clear").
- not_substitutable: in the SAME situation a native speaker could not say the further version in place of the base, or the two differ in more than the expression itself.
- unnatural: unnatural, stilted, archaic, slang, or rarely used by real speakers.
- overlap_existing: substantially overlaps with the existing study items."""

AUDIT_A = """You are a strict, skeptical bilingual (English/Japanese) ESL editor auditing candidate items for a learning corner "One Step Further": each item shows a plain BASE expression and a more natural, practical FURTHER expression a Japanese learner could say in the same situation.
Your job is to FIND DEFECTS. When unsure, mark the defect. A fluent, impressive sentence that does not say the same thing as the base is a defect. The two must be interchangeable in the same situation.

{codes}

Existing study items (Key Phrase / Word / grammar) for overlap check: {existing}

Per item output:
- f: list of defect codes present ([] if none).
- diff: concise Japanese note (<=40 chars) of ANY difference in meaning/nuance/strength between base and further, even slight; "" only if truly equivalent.
- dp: true if the difference would matter in real use. A change in WHAT is said (modality dropped, relation/role changed, different act) is NOT a mere nuance: use code meaning_shift or polarity_modality and verdict FAIL. PASS_WITH_DIFF is only for differences of strength, register, or flavor where the learner would still be saying the same thing.
- why: if FAIL, concise Japanese (<=40 chars) naming the concrete defect.
- v: "PASS" (f empty, diff empty/trivial, dp false) | "PASS_WITH_DIFF" (f empty, diff non-empty, dp false) | "FAIL" (any f, or dp true).

Items (JSON lines):
{items}

Output JSON only: {{"results": [{{"id": "...", "f": [], "diff": "", "dp": false, "why": "", "v": "PASS"}}]}}"""

AUDIT_B = """You are a strict ESL editor judging LEARNING VALUE of items that already passed a meaning-preservation check. Items belong to "One Step Further": the learner sees a plain base expression and a more natural, practical further expression. Learning value = the learner gains a chunk (phrase, phrasal verb, idiom, set phrase, natural construction) they will want to remember and actually use. Difficult vocabulary itself is NOT valued.
Existing study items for this article (do not duplicate): {existing}
Learner level: {level}

Per item, score 1-5 (be critical; 5 is rare): d=discovery (new discovery for a Japanese learner), w=want_to_use, b=breadth of real situations, l=level_fit, c=clarity of the Japanese point_ja (accurate, concise, no invented context).
bf: list of flags present: harder_word_only, reorder_only, overly_fancy, narrow_use, low_value, overlaps_corner.
st: strength (Japanese <=40 chars). wk: a real, concrete weakness (Japanese <=40 chars; never "none").

Items (JSON lines):
{items}

Output JSON only: {{"results": [{{"id": "...", "d": 1, "w": 1, "b": 1, "l": 1, "c": 1, "bf": [], "st": "", "wk": ""}}]}}"""

FINAL = """You are an independent, strict reviewer (English/Japanese) checking finalist items for the "One Step Further" learning corner against the ARTICLE they came from. Be skeptical; mark defects when unsure.
Articles (each finalist's "cell" tells which article applies):
{articles}

Existing study items per cell (Key Phrase / Word / grammar): {existing}

{codes}

For each finalist output (keep every text field SHORT):
- ex: true if the quote exists in its article AND target_span is the right contiguous range to replace (not arbitrary, not the whole sentence by default).
- pr: true if prototype is a correct base form of target_span without losing subject/negation/modal/certainty/intent/tense that matter.
- mn: true if meaning_ja matches what target_span means in the article.
- sub: the quote with target_span replaced by the further expression (minimal inflection/slot adjustment), one sentence.
- sn: true if sub is natural English.
- sm: true if sub says the same thing as the original quote (no new subject/emotion/action/reason; same polarity/modality/tense; note: a small nuance difference of strength/register is OK, a change in what is said is not).
- f: defect codes present (see above; also use them for frame_base_en vs frame_further_en).
- diff: Japanese <=25 chars: any meaning/nuance difference, even slight ("" if none).
- why: Japanese <=25 chars naming a concrete problem ("" if none).
- v: "PASS" only if ex, pr, mn, sn, sm all true and f empty; else "FAIL".
- If needB is true, also score learning value 1-5 (be critical; 5 is rare): d=discovery for a Japanese learner, w=want_to_use, b=breadth of situations, l=level_fit, c=clarity/accuracy of point_ja; bf=flags among [harder_word_only, reorder_only, overly_fancy, narrow_use, low_value, overlaps_corner]; wk=a concrete weakness (Japanese <=25 chars). If needB is false omit d,w,b,l,c,bf,wk.

Finalists (JSON lines):
{items}

Output JSON only: {{"results": [{{"id": "...", "ex": true, "pr": true, "mn": true, "sub": "", "sn": true, "sm": true, "f": [], "diff": "", "why": "", "v": "PASS", "d": 1, "w": 1, "b": 1, "l": 1, "c": 1, "bf": [], "wk": ""}}]}}"""
