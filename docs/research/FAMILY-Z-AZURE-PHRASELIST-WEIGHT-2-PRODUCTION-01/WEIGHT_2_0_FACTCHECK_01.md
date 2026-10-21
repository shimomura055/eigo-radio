重み2.0は正式採用済みか: **Yes**(ユーザー正式決定2026-10-20、USER_DECISION_REGISTER #126、OPEN-426=CLOSED・PRODUCTION_WIRED[Fable判定2026-10-21]、配線commit `68725797d` 2026-10-20 10:43 JST)
Productionで実際に動いているか: **Yes(Phrase Listが空でないときのみ発火)**。Family Z=メロス run_e2e_06で実発火(`dgi.bias=2.0`、"Melos")。Family X=paycheck_personality run_pp_01で実発火(2026-10-21 13:09、phrase "unknown")、ただしmanga_ai_chat_byus run_byus_01等はPhrase List空のため未発火(`setWeight`未到達)。

# WEIGHT_2_0_FACTCHECK_01(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02、API 0・コード/SSOT変更なし、2026-10-21)

## 1. 採用判断(SSOT)
- `docs/pm/USER_DECISION_REGISTER_01.md:293` #126 判断済み2026-10-20「Azure Phrase List重み2.0 `APPROVED_FOR_PRODUCTION`」(Trial=FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01のFable判定REJECTEDに対するユーザー裁定。追加Trial・新品質基準なし)。
- `OPEN_ITEMS.md:938` OPEN-426 = CLOSED・PRODUCTION_WIRED(承認2026-10-20+配線+test7+wire evidence dgi.bias=2.0+run_e2e_06 audit記録)。
- `DECISION_LOG.md:21857`(2026-10-20 ユーザー決定+配線)、`:21864`(2026-10-21 PRODUCTION_WIRED確定)。ユーザー原文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_USER.md`。
- `OPEN_ITEMS.md:936` OPEN-424(重み比較Trial)= CLOSED・REJECTED(Fable判定)。ただしユーザー判断で2.0を採用(OPEN-426)。

## 2. 正式Production経路で実際に設定されている重み
- `er006_secondary_asr_01.py:75` `AZURE_PHRASE_LIST_WEIGHT: float = 2.0`(定数。コメントL70-74に「既定ON固定: flag/環境変数/関数引数では切替えない(Family X/Y/Z共通、_AzureShared経由の全Azure呼出に適用)」)。
- `:106-111` `if phrases:` の内側で `PhraseListGrammar` 生成+`setWeight(float(AZURE_PHRASE_LIST_WEIGHT))`。**phrasesが空ならPhrase List自体が作られず重みは送信されない(未指定=SDK既定1.0相当)**。
- 呼出元: `:475`(CS equivalence)、`:708`(`_AzureShared._call`=統一judge経路)。X(`er003_v1_repro01_main_generate.py:355-358`)・Z(`er012_b_family_voices_production_01.py:551-555`)とも `ledger_phrases=[h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]` を渡す同一関数。
- 監査記録: `:923`・`:1019` `azure_phrase_list_weight`=(`AZURE_PHRASE_LIST_WEIGHT if ledger_phrases else None`)。
- test: `er006_azure_phrase_list_weight_test_01.py` 7件、本回再実行 `7 passed`(API 0)。
- 採用前(commit `68725797d^`)の状態: `setWeight`呼出なし(Grep 0件)、`:288`の定数辞書は `"phrase_list_weight": None`(「SDKが重み設定APIを公開していない」とする誤コメント)=Azure SDK既定(1.0)で動作。`git log -S AZURE_PHRASE_LIST_WEIGHT` の初出もこのcommitのみ。

## 3. runtime evidence(重み2.0の発火)
- 配線機構(DEV、Production関数経由): `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/wire_evidence_prod_01.json`: `sdk_prop_weight=["2.000000"]`、送信JSON `speech.context ... "dgi":{...Items:[{"Text":"Melos"}]},"bias":2.000000`、PASS=true(Azure 1回、約JPY1)。
- **Family Z 正式run**: run_e2e_06(2026-10-20 10:37-10:52 JST、メロス Std/Adv全77 clip)。`docs/research/.../MELOS_REGEN_RUN_E2E_06_RECORD_01.md` と `run06_clip_evidence_01.json:2304-2334 weight_records_06`: part1_c9・part3_c1 secondary_1で weight=2.0・phrases=["Melos"]、kp4_en は PL空で weight=null。run_e2e_05では0件。`er011_output/attempt_history.jsonl` 行16089/16090/16097(theme_id=run_e2e_06)に `azure_phrase_list_weight: 2.0, azure_phrase_list:["Melos"]`。
- **Family X 正式run(発火あり)**: `er011_output/attempt_history.jsonl:16198`(2026-10-21 13:09:34、theme paycheck_personality__run_pp_01、a2/in_one_line、secondary_1): `phrase_list_used:true, azure_phrase_list_weight:2.0, azure_phrase_list:["unknown"]`、行16199(post_slowdown_cascade)も同じ。同一内容が `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/a2/narration/attempts/in_one_line_attempt1_custom78daa961.json`。"unknown"の出所=`er006_output/pronunciation_ledger_01/ledger.json:1098`。(注: `attempt_history.jsonl`はgit上未commit差分あり[M]、上記行は作業ツリーの実記録。)
- **Family X 正式run(未発火)**: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md:17-18,25` = usage Azure 12行すべて`phrase_list_size=0`、`setWeight(2.0)`は一度も実行されず(LedgerにEN pronunciation_hintが無く`get_hint_for_text`が空)。attempt_history 行16216-16264(byus_01)・16152(mey_02)も weight=None・list=[]。つまり「発火するかはLedgerに英語hintがある語が記事にあるか次第」。
- er089 Trial(Trial専用、Production関数経由)`er089_output/proper_noun_en_pronunciation_trial_01/phrase_list_evidence.jsonl` で`bias`観測=機構証拠であり正式runの証拠ではない。
- 注: 認識精度への効果自体はAzure内部で直接観測不能。確認できたのは「APIへ渡した設定」まで。

## 4. 過去Trialとの関係(区分)
| 対象 | 区分 | 根拠 |
|---|---|---|
| Phrase List導入(重みなし、既定1.0) | 採用済み(2.0採用前から本番、ledger語を`addPhrase`) | `er006_secondary_asr_01.py:78-` / 旧版`:288` None |
| 重み2.0(定数・全Family共通・既定ON固定) | **採用済み・PRODUCTION_WIRED** | #126、OPEN-426、`:75` |
| 重み1.5 | 未採用(Trial限定) | OPEN-424: Phase Aで`Mellows`→`Melos`だが採用判断は2.0のみ |
| 重み1.0/1.5/2.0比較(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、`er084_azure_phraselist_weight_trial_01_lib.py:113` setWeight) | Trial限定(Fable判定REJECTED、副作用: 有効負例33wavで重み2.0の新規誤PASS+3例Mullos→Melos、w2.0で`onto→unto`) | OPEN-424、`er006_secondary_asr_01.py:70-74`コメント。ユーザーが承知のうえ2.0採用、安全網=PASS_WITH_WARNING+試聴リスト運用 |
| er084 `weight=None`なら`setWeight`非呼出 | Trial専用の比較機構(Production経路は定数2.0固定で別) | er084 lib:89,113 |
| er089 固有名詞EN発音供給Trial | Trial専用(別テーマ、未採用) | OPEN-434 |

## 5. 結論の補足
- 「採用済み」と「全記事で動く」は別: 重み2.0はPhrase Listが空でない呼出のみに効く。Family Zメロス・Family X paycheck_personalityで実発火済み、Family X byusは空で未発火。開いた窓(未生成)は未観測。
