# WIRING_DESIGN_02: Production配線差分(設計のみ、Production編集0。VALIDATED後・ユーザー採否後の別委任で実施)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_07 / 前版=`WIRING_DESIGN_01.md`(A-1) / 根拠=OF-KPGM-D3-04/05
採否: 下記の変更は**未承認**(Adv側/G3側とも)。採用は人間ユーザーのみ。以下は採用された場合の差分設計。

## 1. 変更候補
- (S) Std gloss: 新規生成(current_japanese_gloss=null)項目にG3 block(candidates→japanese_gloss)を挿入。`er003_key_words_gloss_alignment.py`の`NEW_GENERATION_TEXT`(:315-321付近)直後に1ブロック追加、schemaにcandidates(2〜3案、downstream不使用)を追加。`PROMPT`変更を伴うため承認要。
- (A) Adv説明: E1型(gloss行と参照規則行を外す)またはE4型(+usage_type/core_sense schema)。`er019_family_x_kp_explanation_01.py`のUSER_TEMPLATE_HEADER(:79-80の規則行)・build_explanation_user_message(:174のjapanese_reference_meaning行)・EXPLANATION_JSON_SCHEMA(schema名`..._trial_02`)。

## 2. signature・再生成(OF-D3-04)
- X: `er019_family_x_audio_production_runner_01.py:1077-1095` `_resolve_kp_explanations_text`。`phrases_signature`/`gloss_signature`の他に**説明仕様ID(例`expl_spec_v2`)とPROMPT_SHA256**をbundleへ保存し、reuse条件に加える(現状はPROMPT_SHA256がsignatureに無い=旧仕様の説明が再利用される)。glossを入力から外す場合も`gloss_signature`条件は外してよいが、仕様ID一致は必須。
- Z: `er026_family_z_fiction_production_runner_01.py:1517-1528` sig_payload(dict)に`spec`=仕様ID+PROMPT_SHA256を追加(形が変わるためハッシュ変化=既存の完成記事は次回run時に再生成される。**既存完成記事を次回runで再生成する扱いをユーザーへ明示**)。
- X/Z両方で同一の仕様IDを使い、XとZで挙動が分かれないことをtestで固定。

## 3. 撤去・置換(OF-D3-05)
- 撤去(Aを採用する場合): `er019_family_x_kp_explanation_01.py:79-80`「Do not just translate the Japanese reference meaning…」、:174 japanese_reference_meaning行、:165-167 docstring、schema名`key_phrase_advanced_english_explanation_trial_02`を新仕様名へ。呼び出し側のjapanese_gloss引数: X runner :1089-1091、Z `er026...:1534-1535`(`japanese_gloss`をinput_itemsから外す。`gloss_signature`関連も整理)。
- **編集しない**: `er041_*`(Trial-02履歴module)。
- 逐語一致test: 「Trial-02のPROMPT_SHA256と一致」を撤去し、新仕様IDのhash固定testへ置換(旧testの反転であり、不整合な出力を期待値にしない)。
- 残置: 語数(MAX_WORDS=15)/新規Fact検査、技術retry(parse失敗1回+QA起因1回、合計上限は現行どおり)、A-1全項目、Std gloss承認規則(平易・括弧禁止)。

## 4. 検証要件(採用時)
DefaultOffIsolation型test(flag未設定でAPI 0・出力不変)、X2記事+Z1作品の正式経路text工程、retry発動統計、Store reuse/再生成signatureの実run確認。
