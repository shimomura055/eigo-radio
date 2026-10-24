# PROMPT_DIFF_06 (委任_25: Opusレビュー OF-Y8-01〜05 の反映差分。API 0)

作成: 2026-10-24。前回の`PROMPT_DIFF_05.md`の続き。**Voice Prompt(`VOICE_PROMPT_OB2`)・`render_persona_ob2`・`OPENING_GUIDE_02`・反復検出・`er110_family_y_opinion_based_01.py`/`_02.py`は変更0字**(testで固定)。変更はテーマ固有データ(Persona Sheet)、03 runnerのloader(印の名前)、testのみ。

## 1. 変更一覧
| ID | 対象 | 変更 |
|---|---|---|
| OF-Y8-01 | V1 ONE_a〜d(RV-55由来4項目) | RV-55由来を3項目(ONE_a[RV-55+56]・ONE_b・ONE_c)に再要約し、段落の順序・固有の言い回し(眠る準備/落ち込んでいる暇/次から次へ/個人のお客さんに求める/報酬を上げる/経営の問題/すり替え)を除去。RV-55だけを根拠にする項目は2つ(ONE_b・ONE_c)。stake_ja・persona_sketch_jaからも同語を除去 |
| OF-Y8-01 | test追加 | `test_sheet_has_no_long_match_with_r2plus_quotes`(逐語抜粋との8文字以上の共通部分列=0、常時)・`test_sheet_has_no_long_match_with_r2plus_source_pages_if_present`(出典本文全体との照合、sources/がある環境。検査自体が働くことの自己確認付き)・`test_v1_not_structured_after_single_note_article`。属性ラベル/テーマ基本語(現役の宅配ドライバー・宅配ボックス・置き配)のみ照合から除外(表現ではないため) |
| OF-Y8-02 | V1 claim_core / 立場の根拠 | 芯=「きついのは本当。でも、お客さんから料金を取って片づく話ではなく、会社や料金全体の側で考えることだと思う。」(留保型)。ONE_a=RV-55+RV-56(送料無料の見直し)、ONE_d=RV-59(依頼自体は業務の一環・客を責めない)、ONE_g=RV-55+RV-29。矛盾欄=「不在での再配達は減ってくれたら、という気持ちはあり…」(RV-55原文の願いの趣旨。原文の言い回し『なくなってほしい、という願い』は長一致testにより言い換え) |
| OF-Y8-02 | AXIS_ANALYSIS_03 §3/§4・PERSONAS_05 §4/§5 | 3件基準の二重基準を是正し、逆向き選定の理由を書き直し(RV-28=2019年・数字が多い/RV-37=伝聞・別話題の一文/反対・慎重側は経験の声RV-57〜59と組み合わせて人物にできる) |
| OF-Y8-03 | V3 | 芯=「手間をかけて再配達を出さない側からすると、くり返し頼む人と同じ料金なのはおかしい。有料でいいと思う。ただ、自分は受け取り方を選べる、恵まれた側かもしれない。」。THREE_f(整備が先、RV-34・RV-66)を削除。THREE_b(努力を台無しにされる経験)は経験欄に残す。矛盾欄=RV-42の引け目1つ。THREE_i(RV-46、意見欄)を追加。persona_sketch/arc/wishes/values/stakeから『整備が先』を除去 |
| OF-Y8-04 | V2 TWO_h(RV-64) | V2から削除。V3のTHREE_h(RV-09・15・19)に『最初は無料で、くり返す人から』を残す |
| OF-Y8-05 | V2 TWO_e | 「もし家にいる日に、チャイムを鳴らされないまま不在票だけ入れられたら、それでも再配達の料金がかかるのか、と心配になる」(仮定形) |
| OF-Y8-05 | V1 ONE_f | 「一軒の玄関先で何分も待つ」→「玄関先で長く待つ」 |
| OF-Y8-05 | 回数の言い換え | 「最初の不在は大目に見る」→「最初は無料で、くり返す人から」(THREE_h・V3 wishes) |
| OF-Y8-05 | 漢数字の数量表現test | `test_no_kanji_quantity_expressions_in_persona_text`(一軒/二回/三度/二度目/一人 等。括弧内のモデル向けメタ指示は除く) |
| OF-Y8-05 | 公開前Gate | SOURCE_LOG_02 §5 に (e)経験欄の過半が単一出典に依存していないか (f)R2+出典とSheet文の長一致の機械照合 を追記。(e)はtestで固定(V1・V3は満たす。**V2はE全件がRV-08の1出典=既知の例外**として固定、Opus論点1でV2の根拠は問題なしと確認済み) |
| OF-Y8-05 | 印の改名 | 03 loaderの印 `tbs_only` → `r2plus_only`(THEME内の項目)。01の照合は旧名を読むため、`patched_ob_03`のwith内の写しにだけ別名`tbs_only`を付ける(01は無変更、themeそのものに`tbs_only`は付かない。testで固定) |

## 2. 変更していないもの(Grep)
- `git diff` で `er110_family_y_opinion_based_01.py`・`_02.py`・`er110_family_y_text_trial_01.py`・`er110_family_y_persona_*` は無変更(`test_01_02_and_existing_modules_unchanged`)。
- Voice Prompt規則9(数字禁止)の解釈は変更なし(案(a)言い換えで通す)。

## 3. 撤去・残置した規則・検査・testの識別子
- 撤去: V3 `THREE_f`・V2 `TWO_h`(Sheet項目)、03 loaderの`tbs_only`付与。旧testの`all(x["tbs_only"]…)`・`ob.SHEETS is th["sheets"]`は新仕様(`r2plus_only`、with内の写し)に置換。
- 残置: 01/02の`tbs_only`(前テーマ用)は触らない。
- 追加test 7件: no_kanji_quantity_expressions_in_persona_text / sheet_has_no_long_match_with_r2plus_quotes / sheet_has_no_long_match_with_r2plus_source_pages_if_present / no_single_source_dominates_experience_column / v1_not_structured_after_single_note_article / v2_hypothetical_and_no_first_time_item_duplicate / source_log_gate_has_e_and_f_and_tbs_only_renamed。計30件PASS、er110_family_y_*_test_01 全体163件PASS。
