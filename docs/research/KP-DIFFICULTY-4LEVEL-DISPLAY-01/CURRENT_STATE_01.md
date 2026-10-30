# KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_01 現状調査(CURRENT_STATE_01、API 0、2026-10-30)

原文=`docs/pm/delegation_log/2026-10-30_KP-DIFFICULTY-4LEVEL-DISPLAY-01_USER.md` §4(Workstream B)。OPEN-622。

## 1. 現行Production候補生成の出力(難易度に関する既存情報)

| 項目 | 場所(file:line) | 難易度に使えるか |
|---|---|---|
| 選定Prompt P7(Phrase最大7)/W5'(Word最大5) | `er119_kp_p7w5_prompts_01.py:44-45`(P7)・`:52-76`(W5')。sha固定(`:49-50`の`P7_SHA256_PINNED`、`:78`の`W5P_SHA256_PINNED`。変更はユーザー承認要) | 条件4「上級者向けの学習価値」・条件5「易しい表現の除外」(`er105_kp_fulltext_selector_01.py:60-61`)は**選定時の定性的フィルタ**で、段階値は出力しない。出力schemaは phrase/reason_ja/word_count のみ(`:38`の注記、`er119_kp_prompt_2v_01.py`のschema) |
| 候補dictのfield | `er119_kp_candidates_01.py:_gate_chain`(`cand = {candidate_id, selection_phrase, used_form, japanese_gloss, source_sentence, source_sentence_id, word_count, reason_ja, origin, raw_rank, item, kind, flags, gates, auto_eligible, human_selectable, ai_rank}`) | 難易度fieldは**無い**(`grep difficulty\|難易度 er119_kp_*.py er128_kp_confirmed_content_01.py`=0件) |
| CEFR/頻度帯/語彙Band | Productionのruntime語彙リソースとしては**存在しない**。`NEWS-*-VOCAB-6000/10000/14000-*REPORT.md`は記事本文の生成制約(Writer側の語彙水準)で、候補単位の頻度表ではない。`wordfreq`等のlibraryも未導入(`import wordfreq`=ModuleNotFoundError) | 使えない(新規リソース導入になる) |
| CMU辞書(`er108_kp_cmu_lexicon_gate_01`) | 発音可否のGate(基本形化後のCMU未登録語を除外) | 語の有無であり難易度ではない |
| pronunciation ledger | 音声化用 | 無関係 |
| 候補のsource_sentence/japanese_gloss | `_gate_chain`で付与済み | 判定の文脈入力として利用可(追加取得0) |

結論: 難易度に直接使える既存情報は無い。判定には新規の判定処理が必要。入力(表現・種類・日本語訳・例文)は既存fieldで足りる。

## 2. データの流れ(kp_candidates.json -> フォーム -> 確定)とfield引き渡し

1. 生成: `er119_kp_wiring_01.py:70`が`kcand.make_generate_fn`を呼ぶ(X=`er019_family_x_audio_production_runner_01.py`、Y=`er121_family_y_runner_01.py`、Z=`er026_family_z_fiction_production_runner_01.py`が共通利用)。`generate_candidates`->`_generate_candidates_impl`。X/Y/Zの差は`src_fn`/`person_repair_fn`(Zのみ)だけで、候補の最終集合を作る位置は共通。
2. 保存: `rv.save_candidates`が`candidates_sha256`(doc全体、`candidates_sha256 key`以外=`er119_kp_human_review_01.py:217-218`)を付与して`kp_candidates.json`へ。**新field追加はshaに自動で含まれる**(生成時に確定するため整合)。
3. フォームdata: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`の`entry()`/`convert()`(`:145-`・`:236-`)。候補の`reason_ja`/`japanese_gloss`/`kind`/`origin`/`ai_rank`をフォーム用entryへ写す。ここに`difficulty`を足せば`phrases[]`/`words[]`に載る。V3ビルダー`LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/build_data_01.py:8`も同exporterを共有。
4. フォーム表示/コピー: `user_test/selection_form_v3/form_logic.js`(`reasonOf` `:94`、`itemRecord` `:205`)。一括選定UIの`restore_batch`は`er128_form_readable_restore_01.py`。**readable/AIF1の照合コードに候補の参考情報は含まれない設計**(`reason_ja`は`reason_for_reference_only`として別枠)。本委任はform_logic.js/index.htmlを編集しない(並行の一括選定UI 02A)。
5. 確定: `er128_kp_confirmed_content_01.py:_item_from_cand`が確定itemを作り、`reference`にAI参考情報(`ai_reason_ja`,`ai_rank`)を保持(`:261`)。

## 3. retry/regeneration/resume/backfill時の扱い

- 外側retry(`while True`、`er119_kp_candidates_01.py`): 失敗周は候補集合が捨てられ、最終周の`cands_final`だけがdocになる。
- 補完(backfill、KP-GATE-DROP-BACKFILL): 同じ関数内で`cands = cands + new_cands`(ai_rank付番後・Redundancy QA前)。補完分も同じ`_gate_chain`の産物。
- 再選定(reselect): CLIが新roundの`generate_candidates`を呼ぶ=新docが作られる(`RESELECT_MAX=2`、`er119_kp_human_review_01.py:56`)。
- resume/再実行: 候補sha一致なら再選定せず保存済みdocを読む(`er119_x_wiring_test_01`のAPI 0 test)。
- したがって「**候補生成の最終段(`cands_final`確定直後)で1回付与**」が、初回/外側retry/補完/再選定を全て覆う唯一の位置。resumeは保存済みの値を使う。旧doc(本変更より前に生成)には難易度が無い->exporterは`unknown`/`not_graded`で扱う(候補は減らさない)。

## 4. Standard/Advancedの差・X/Y/Zの差

- level key: `a2`=Standard、`b1b`=Advanced(`export_form_data_01.py:25`)。processは`A2_SUPPORT`/`B1_SUPPORT`(どちらもSUPPORT_MODEL=gpt-6-luna、`er006_model_routing_contract_01.py:50`)。
- 難易度判定は表現そのものの難しさを基準にし、学習レベル(Standard/Advanced)は境界例の参考として判定messageに渡す(原文4.2「Standard/Advancedの学習レベルとの関係」を総合要素に含める)。
- Family差は候補生成では`src_fn`/`person_repair_fn`のみ。難易度付与は最終候補集合に対して行うため、X/Y/Zで共通。

## 5. 費用の根拠(70円/記事セット比)

- 前回Trial(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01、`RESULT_01.md:18,69-70`)の実測: gpt-6-luna中心の追加工程で1レベル+0.31円(方式A)。本件の難易度判定は入力が約12件の短いlistで、同規模のluna 1 callと見て**1レベル約0.1〜0.3円、記事セット(Std+Adv)約0.2〜0.6円(70円の0.3〜0.9%)**と見積もる(実測は委任_02の実run・cost loggerで確定)。
