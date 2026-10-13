# design_diff_01: 最小改善案(1案) P0X = P0 + 1段落 (Trial専用、Production非接続、採用判断なし)
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01 / 2026-10-13

## 1. 方式の選択: 選定Prompt側(1段落追加)。候補供給側は採らない
根拠(DIAG_01の事実とRound 1〜2の知見):
1. 既存gate・canonicalizationは「選定段で display_phrase を候補span超へ拡張し、canonicalizationが無変更にする」経路を既に通す(`push prices up`は候補`prices up`から14/14で拡張、`no way to know`もPASSを実gate経路で確認)。足りないのは**選定LLMへの指示**だけ。
2. 供給側の拡張(`no way to` 等の拡張候補を追加)は、(a)「いつ拡張するか」の新規ヒューリスティック(例: 名詞末尾+to不定詞)が必要、(b)追加候補が既存候補と包含関係になり Tier-H/S・`contains:`注釈・Redundancyに波及、(c)候補ブロックのsha・行数が変わりM2P0対照を再利用できなくなる。Round 1 で `match:` 注釈は効果なし、注釈系は効きにくいと分かっている。
3. M2P0対照のshaを維持できる(候補ブロックは完全に同一。Prompt headの1段落のみ追加。全6セルで`P0X - 追加段落 == P0`をtestで確認)。
4. Round 1〜2で「Promptの全面書き直し」は効きにくく副作用(concierge低下など)が出た。今回は書き直しではなく**既存の「単独で意味が成立する句を選ぶ」原則(数値穴埋め句に限定された文言)を構文断片へ一般化する1段落**で、差分は249文字(約155 token相当)。
補欠案(今回は実装・見積対象外、報告のみ): P0Xが効かない場合の供給側案 = 「候補の本文出現の直後が`to`+語で、候補末尾が名詞の辞書登録2語」に対して拡張候補を同じ行に`ext:`として付す。Round 1の注釈無効の知見から効果は不確実。

## 2. 追加段落(これだけが差分)
挿入位置: P0 head の「ソロ旅行を～％とする…数値を補わないと意味が成立しない句…それ単体で意味が成立する句・グロスを選んでください。」段落の直後。
```
切り出した語句が、本文ではto不定詞・前置詞句・目的語などが続いて初めて意味が成立する構文の一部で、その語句だけでは意味や用法が十分に伝わらない場合は、候補の語句に本文で隣り合う語を加えて、意味が成立する1〜5語の形をdisplay_phraseにしてください(source_candidate_idは元の候補のままで構いません)。is・have・canなどの有限の助動詞はdisplay_phraseに含められないため、含めずに意味が成立する形にできない場合は、その候補を選ばないでください。
```
設計意図:
- 「A(選ばない)」「B(意味が成立する語句へ拡張)」の両方を許容し、機械的強制はしない。
- 「source_candidate_idは元の候補のまま」: 末尾ガイダンスの「候補に無い新しい表現を作らないでください」との衝突を避ける(display_phraseの拡張であり、新候補の創作ではない旨)。
- 「is・have・canなどの有限の助動詞は含められない」: 既存Validator(`er003_key_words_min_unit.py` L260-261)が `have/had/has/is…` を INVALID にするため。P0の既存文言「動詞は基本形へ直せ」に従うと `have no way to know` を出してINVALIDになる危険があり、これを回避する。
- 特定語・特定記事・評価語句なし(`hardcode_check` pass: 禁止語19語・全アンカー12・10記事M2の2語以上候補108句に不一致。`er064_kp_noway_01_test.py` Hardcodeクラスで固定)。

## 3. M2P0との差分(diff)
```
--- P0_head
+++ P0X_head
@@
 「ソロ旅行を～％とする」のように、数値を補わないと意味が成立しない句・日本語グロス(数値の穴埋めを必要とする不完全な表現)は選ばないでください。それ単体で意味が成立する句・グロスを選んでください。
+
+切り出した語句が、本文ではto不定詞・前置詞句・目的語などが続いて初めて意味が成立する構文の一部で、…(上記1段落)…その候補を選ばないでください。
```
- head文字数 1381 → 1630(+249)。推定 +約155 token(tiktoken未導入のためUTF-8 bytes/4近似)。追加入力費用 約JPY0.0025/job。
- 変更しないもの: 候補ブロック(M2 shortlist、rows sha)、末尾ガイダンス(P0のまま)、出力schema、Production gate(選定validator・Rule7・Redundancy)、canonicalization Prompt、モデル(gpt-6-luna)、retry/fallback機構(Trial runnerはretryなし、Production経路と別)。
- 差分全文は `offline_check_01.json` の `prompt.head_unified_diff`。Trial専用コード: `er064_kp_noway_01_prompts.py`(P0X構築)。Production Prompt(`er030` 系の `_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`・static instructions)は読取のみ。

## 4. 案B(`no way to know`)のオフライン検証結果(既存コード・LLM呼出0、`offline_check_01.json`)
| 項目 | 結果 |
|---|---|
| 本文逐語性 | `no way to know` は `S14` に連続して存在(逐語OK)。`have no way to know` は本文が`had`のため逐語ではない |
| 1〜5語 | `no way to know`=4語 PASS、`no way to know whether`=5語 PASS、`…whether they`=6語 INVALID |
| 実選定gate(FakeClientで`run_source_reference_contract_gate`+`validate_min_unit_selection`) | `no way to know`/`no way to`/`no way to know whether`=PASS。`have no way to know`/`had no way to know`/`have no way`=**INVALID(有限助動詞)** |
| canonicalization Rule7 | 選定で拡張済みでcanonが無変更ならPASS。canonicalizationだけで`no way`→`no way to know`へ拡張するとINVALID(Phase2 C0 run1で実観測)。one's一般化: `pump its fist`→`pump one's fist`(1対1置換)PASS、`pumps its fist`→`pump one's fist`(動詞活用を同時変更)は不可 |
| `candidate_mismatch_suspected` | `no way to know` = false(telemetryのみ、非ブロッキング) |
| source_span超え拡張 | gate上は問題なし(`source_span`は候補`no way`のまま復元される。`_verify_source_spans_against_raw_article`で欠落なし) |
| Redundancy QA | LLM判定のためオフライン不可(有料runで測定) |
| display_phraseの逐語検査 | **既存gateに無い**(`no way to tell`のように本文に無い語もgateはPASS)。Trial解析側で語幹許容の逐語率を測る(`er064_kp_noway_01_analyze.py`) |
- 重要: ユーザー例の `have no way to know` はそのままでは既存Validatorを通らない。成立形は`no way to know`(動詞`have`を含まない形)。Validator変更(`have`許可)はProduction変更でありTrial範囲外 = 仕様候補として報告のみ(実装しない)。

## 5. ファイル
- `er064_kp_noway_01_prompts.py`(P0X構築) / `er064_kp_noway_01_offline.py`(本検証) / `er064_kp_noway_01_run.py`(Trial runner雛形。`--mode prep`のみ実行可。`--mode run`は環境変数`KP_NOWAY_PAID_RUN_AUTHORIZED`未設定だと拒否、test済) / `er064_kp_noway_01_analyze.py`(判定指標算出。対照`control_baseline_01.json`作成済) / `er064_kp_noway_01_test.py`(20件PASS、`test_results_01.txt`)。
