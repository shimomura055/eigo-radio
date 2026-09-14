# B1B Key Phrase 人手選定(manual selection)理由記録

管理ID: USER-TEST-AUDIO-COMPLETION-01-DISCOVERY
selection_mode: `manual_user_decision_2026-09-14`
対象記事: `er014_output/four_type_observation_01/discovery/b1b/article.md`(canonical final text、complete3版)

## 背景

自動選定(方式L選定、`run_key_phrase_selection`)は、この記事に対して
過去4回試行され(`production_set_cost.json`記録)、そのうち有力候補が
必ず"have agency"を含み、既存Validator(`er003_key_words_min_unit._FINITE_AUX_WORDS`)
が語彙動詞haveを有限助動詞として誤検知し、`KEY_WORDS_STRUCTURE_INVALID`と
なって完走できなかった(call1/call3/call4)。call2のみ選定自体は
PASSしたが、canonicalization段階でqa_traceable_contiguous_span不合格
(occupy their thoughts→their→one's正規化)、続くRedundancy QAで
`occupy their thoughts` vs `a mental path to follow`の意味重複が
NGとなり、完走しなかった。

ユーザー判断(2026-09-14): 完成を急ぐため、選定(Selection)段階のみを
人手で行う。以下を厳守する。
- canonical B1B本文に実在する連続spanから選ぶ(捏造しない)。
- 既存Key Phrase仕様(Strategy L=Listening Blocker Ranking)の観点を
  そのまま踏襲する(standalone natural unit、残余文脈語なし、意味保持、
  他文脈で再利用可、5件間で冗長でない)。
- 「have agency」は不採用(本文を書き換えて回避することはしない)。
- 既存Validator(canonicalization/Redundancy QA双方)は無変更のまま、
  選定済み5件を入力として通す(`er003_v1_n3_01_scaffold_generate.
  run_key_phrase_canonicalization`/`run_key_phrase_redundancy_qa`を
  無変更で直接呼び出し、選定[Selection]段階の関数だけをスキップする)。

## 採用した5件

| rank | display_phrase | japanese_gloss | 出典文 | 選定理由 |
|---|---|---|---|---|
| 1 | nothing to do but think | 考えることしかすることがない状態 | "...did not enjoy spending six to fifteen minutes with nothing to do but think." | "nothing to do but+動詞原形"という省略的構文。butが「〜以外」という除外の意味で働く点が初見リスナーには聞き取りにくく、他文脈でも再利用しやすい(nothing to do but wait等)。 |
| 2 | reduced the feeling of connection | つながっている感覚を弱めた | "For strangers, these longer gaps reduced the feeling of connection." | 動詞+長い名詞句目的語という構造。主語・動詞・目的語の境界を聞き取りにくい。人間関係・感情の文脈で再利用可能。 |
| 3 | being in the present moment | 今この瞬間にいる感覚 | "...a stronger feeling of being in the present moment." | 動名詞being+前置詞句。マインドフルネス関連の定型表現として他文脈でも頻出。 |
| 4 | actively choosing solitude | 自分から積極的に孤独を選ぶこと | "In one study, actively choosing solitude was associated with relaxation and lower stress." | 副詞+動名詞+目的語が文の主語として機能。動詞的意味を持つ名詞句の聞き取り負荷が高い。他の名詞へ差し替えて再利用可(actively choosing rest等)。 |
| 5 | complicates any simple cultural story | 単純な文化的な説明を複雑にする | "A staged one-to-one tutorial complicates any simple cultural story." | 動詞complicates(三単現)+目的語。「any simple X」という一般化表現と組み合わさり、記事全体の結論(単純な国別ステレオタイプは通用しない)を担う。 |

## 既存Validator/QA結果(この5件を入力とした実行結果)

- canonicalization: `CANONICALIZATION_PASS`(全5件、全QA項目PASS、
  key_phrase=display_phraseのまま無変更[normalization_reason: "none"]。
  model_id=gpt-5.6-luna)
- Key Phrase Set Redundancy QA: `REDUNDANCY_PASS`(重複ペアなし、
  model_id=gpt-5.6-luna)
- 選定(Selection)段階のLLM呼び出しは行っていない(人手選定のため)。

## 除外した主な候補と除外理由

| 候補 | 出典文 | 除外理由 |
|---|---|---|
| have agency | "Quiet can therefore function differently when people have agency and a mental path to follow." | ユーザー指示により不採用。語彙動詞haveが既存Validatorの有限助動詞ブロックリストに一致しKEY_WORDS_STRUCTURE_INVALIDとなる(過去4回の自動選定試行すべてでこの1件が原因)。本文を書き換えて回避しない。Validator誤検知はOpen Item化する(RESULT_PACKET参照)。 |
| a mental path to follow | 同上 | 構造上は選定可能(有限助動詞を含まない)だが、過去のRedundancy QA試行(call2)で"occupy their thoughts"との意味重複(考える方向性を持つこと)が指摘された概念に近い。本セットの"actively choosing solitude"(孤独を選ぶ主体性)との概念近接リスクを避けるため不採用。 |
| occupy their thoughts | "...students told to occupy their thoughts for a brief period..." | 過去試行(call2)でcanonicalization段階のqa_traceable_contiguous_span不合格(their→one's正規化でspan追跡性が壊れる)歴があり、"a mental path to follow"との重複指摘も受けた。同種のリスクを避けるため不採用。 |
| lasted four seconds | "In one version, a single silence lasted four seconds." | 有限助動詞は含まないが、他4件と比べてListening Blocker価値(意味の抽象度・再利用性)が低いと判断。 |
| mixed picture | "Research on the body shows the same mixed picture." | 2語のみで短く、単独では文脈依存度が高い。 |
| thinking for pleasure | "...an everyday activity was enjoyed more than thinking for pleasure in every country tested." | 良い候補だが、採用した"nothing to do but think"と概念(何もしないで考えること)が近く、重複回避のため不採用。 |

## 過去試行の退避先

- call1(元のrun_discovery_complete.py実行)/call2/call3(retry_key_phrase_b1b.py):
  `key_phrases/b1b_old_attempts/call2_3_mixed/`(ディスク上の最終状態、call2の
  canonicalization/redundancy出力とcall3のselector出力が混在したstale状態を
  そのまま保存。詳細な再構成履歴は`production_set_cost.json`の
  `key_phrase_b1b_status_corrected.reconstructed_history_from_file_mtimes_and_content`
  を参照)。
- call4(本タスク開始前、`b1b_final/`への4回目selector試行、結果は
  KEY_WORDS_STRUCTURE_INVALID、"have agency"が原因):
  `key_phrases/b1b_old_attempts/call4_b1b_final/`。

## 既知の限定事項(記録用、ブロッキングではない)

本タスクの2回のLLM呼び出し(canonicalization 1回、Redundancy QA 1回)は、
`finalize_key_phrases_b1b_manual.py`から`er003_v1_n3_01_scaffold_generate`の
既存関数を直接呼び出したが、`er005_cost_logger.install()`によるmonkeypatch
(`cl.install(LOG_PATH)`)を事前に呼ばなかったため、`raw_usage_log.jsonl`への
自動記録が行われなかった(過去のcall1〜4はいずれも`run_discovery_fix_b1b_kp.py`/
`retry_key_phrase_b1b.py`経由でinstall済みだったため記録されている)。
過去の同種呼び出し(`key_phrase_b1b_jpy: 1.3`、`key_phrase_b1b_retry2_jpy: 5.2`、
`production_set_cost.json`記録)から類推すると、本タスクの2呼び出しは
概算¥1〜6程度と推定される(¥160予算上限に対し無視できる規模)。正確な
実測値が必要な場合は再実行が必要になるが、既にCANONICALIZATION_PASS/
REDUNDANCY_PASSで完走しているため、コスト計測のためだけの再呼び出しは
行わなかった(無駄な追加API支出を避けるため)。
