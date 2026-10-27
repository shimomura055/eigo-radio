# SURVEY_01 既存成果の照合(AI-ISLAND-FORM-PRODUCTION-01 委任_01、2026-10-27、read-only・API 0)

## 1. 本文(Std/Adv)の最新承認版
- 本文の唯一の出所: `er019_output/ai_island_temple/run_ai_01/{a2,b1b}/article.md`(2026-10-26 text段で生成。以後`run_kpbf_ev_01`/`run_kp75_ev_01`の同名dirへコピー)。
  sha256: a2=`90c66293dfb1d2d2c164ceea993d4664521819bb44a3deb2422ebb99588c5f10` / b1b=`a2951b9bdf7a555b7a9114860973243306c37bcfc56cecd08b56ed88afb89768`。3 run(run_ai_01/run_kpbf_ev_01/run_kp75_ev_01)で**3者逐語一致**(`sha256sum`)。本文の改版は存在しない。
- 承認状態: 本文の専用「承認」記録は無い。ユーザーが**現行R2本文を維持する**と決定済み(OPEN_ITEMS OPEN-526追記「切り口=(1)現行版」、原文=`docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER_02.md` §1: 現行R2本文・Std/Adv英訳維持、再生成不要)。今回指示(2026-10-27 §2)も本文再生成禁止。
- 正式タイトル: 『島はリセット！ でもAIには「攻略メモ」がある』(OPEN-526)。
- **音声は存在しない**: `er019_output/ai_island_temple*` 及び`.../ai_island_temple__run_*`配下に wav/mp3/flac は0件(audio scaffoldまでで、TTS未実行。OPEN-526 BUDGET_LOG: 「audio scaffold 4.01円、TTS未実行」)。再利用できる音声は無い→完成段(委任_02以降)で必要分のみ生成。

## 2. OPEN-526 のHR記録とユーザー明示確定の有無
- 全HR記録を走査(`ai_island_temple__run_ai_01` / `run_kpbf_ev_01` / `run_kp75_ev_01` の`kp_human_review.json` 6件 + `run_ai_01/b1b/study_text/grammar_human_review.json`): **全て `status=PENDING_REVIEW`、`selection={}`、history=runnerの1件のみ**。`approved_by=user`/`op_select --by user`等の操作は0件。`confirmed_selection.json`/`*frozen*`/sidecar は AI島配下に0件。
- 結論: **旧HRでユーザーが明示確定した内容は無い**(破棄・上書きの対象なし)。旧3+5候補の案A/B/C判断(OPEN-526)は、今回のフォーム選び直し指示で実質置換。旧run_ai_01の候補・HR記録は**一切改変していない**(本委任は読取専用)。

## 3. KP 7+5 候補(再利用判定)
- 再利用元: `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/{a2,b1b}/key_phrases/kp_candidates.json`(P7/W5' Prompt=`kp_prompt_p7`/`kp_prompt_w5p`、model=gpt-6-luna、補完ON、2026-10-27 08:2x生成)。
- 本文一致: doc `text_sha256` は a2=`76f80f62…`/b1b=`00f14092…`で、旧`run_ai_01`/`run_kpbf_ev_01` docの`text_sha256`と同一(同じ本文から生成)。本文sha(KP側のcanonical hash)が3 runで一致、article.mdが3 runで逐語一致 → **最新承認本文に対するP7/W5'正式生成結果が既に存在 → 再生成0**(KP API費用0)。
- 内容: 各level 10件(phrase5+word5)、上限12に対し不足2(フレーズ2: AIの返答が5件、Gate除外E=0で補完対象なし。数合わせはしない=承認済み方針)。全候補`reason_ja`あり(≤25字)、`japanese_gloss`のgloss Gate=ALIGNED(official)。`candidates_sha256` a2=`25a7bce9…`/b1b=`5d8c1b12…`。
- 観測(仕様変更ではない・報告のみ): a2 の word `Strategy` は本文ではなくタイトル行『…AI Has “Strategy Notes”』由来の候補(source_sentenceがタイトル)。 b1b は `carry over`/`erase` に他候補との重複可能性フラグ(`redundant_with`)がある(フォームには「他候補と重複の可能性」注記として表示)。

## 4. フォーム登録済みデータの出所(変更前)
- `user_test/selection_form_v3/data/ai_island_temple__{a2,b1b}__prod.json` は run_kp75_ev_01 の同docから`export_form_data_01.py`で出力されたもの(FORM委任_04)で、文法`[]`(要生成)。articles.jsonでは先頭の『AIの仮想の島』枠は`data:null`(候補未登録)、別枠『AIの仮想の島｜Production候補・7+5 evidence』に同データが載る重複状態だった。
- 旧3+5版は`data/legacy/`に退避済みで、articles.jsonから非表示(`form1_selection_form_v3_test_01.py::test_legacy_3plus5_data_retained_and_not_indexed`)。今回変更後もlegacyは不変。

## 5. 既存Part 2文法候補(参考)
- `run_ai_01/b1b/study_text/grammar_candidates.json`: Step A''済み3件(T1: what節主語/関係節を含む長い主語/that節複合主語)、review=PENDING_REVIEW(未提示・未確定)。**Advは同doc(同一本文・同一extract_signature)を再利用**(Step A'' API 0)。Stdは候補docなし→新規抽出。
- 旧Advには解説(Step B)が未生成(現行Production Part 2は選定後生成)。今回、暫定事前生成で全候補の解説を準備(GRAMMAR_PREP_01)。
