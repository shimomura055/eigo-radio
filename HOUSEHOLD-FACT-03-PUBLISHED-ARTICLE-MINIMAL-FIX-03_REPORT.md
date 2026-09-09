# HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03 実行報告

管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03(OPEN-138、
A-FACT03-4=(a))。並列稼働中: News N-4、Discovery D-3(`er011_output/*stage3*`)。
本タスクはSSOT・Git禁止(後続統合で反映、`docs/pm/ACTIVE_TASK.md`/
`RESULT_PACKET.md`は未編集)。§1〜14の背景・経緯は
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02_REPORT.md`を参照
(重複転記しない)。

**到達Status: USER_FINAL_AUDIO_REVIEW_REQUIRED**

## 背景

ユーザー決定(2026-09-09、正式、A-FACT03-4=(a))。FIX-02継続3回目(§13)で
唯一残っていたブロック要因`topic_intro=STOPPED`(2026-08-17当時ASR 6回試行
FAIL、現行ASR cascadeでは`NORMALIZED_MATCH`で事後PASS、FIX-02 §12.3)を、
kp2_englishと同じ既存人間承認経路(`er003_v1_n3_01_assemble.
record_human_approval()`)で`HUMAN_APPROVED`として記録し、Assembly→Gate
確認→player生成まで進める。

## 1. 承認記録

スクリプト:
`er011_output/open138_household_fact03_b1b_minimal_fix_03/topic_intro_human_approval_and_assemble_03.py`
（既存Production関数の読み取り専用importのみ、TTS/ASR再生成なし）。

`record_human_approval(B1_DIR, "topic_intro", "", approved_by="user_2026-09-09_HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03")`
を実行。canonical_textはkp2_englishと同型(top-level canonical_text/text
フィールド無し)のため空文字列。記録先:
`er003_output/n3_01/household/fact03_fix_02/b1b/audit/human_approved_segments.json`
（kp2_englishの既存記録は保持したまま追記）。noteフィールド:
「2026-09-09 ユーザー判断A-FACT03-4(a)、現行ASR cascadeによる事後再照合
PASS（NORMALIZED_MATCH、§12.3）、当時attempt 1〜6はFAIL、音声byte不変」。
`tts_generation_results.json`の`status`フィールド（`STOPPED`）は書き込み前後
でassertにより不変であることを確認済み（捏造なし）。

## 2. sha256表(narration/*.wav 32件)

original(`er003_output/n3_01/household/b1b/narration/`)との突合、承認記録前後
・Assembly前後の計3回実施し全て同一結果: **31件完全一致、point_one.wav
のみ不一致**(FIX-02継続1のrevision3a、想定どおり)。topic_intro.wavは
一致31件に含まれる(byte不変)。詳細:
`.../topic_intro_human_approval_and_assemble_03_result.json`
(`step1_sha256_precheck`/`step6_post_assemble_sha256_verify`)。

## 3. Gate結果・Assembly結果

- Gate既定経路(`verify_episode_audio_validation_gate(B1_DIR,"B1")`): **PASS**
- Gate opt-in `required_structure`経路(`derive_a_family_required_structure("B1")`): **PASS**
- `stage_assemble_b1(theme)`: **OK**（既存Production関数を無変更で実行）

出力: `er003_output/n3_01/household/fact03_fix_02/b1b/assembled/English_Your_Way_B1B_HOUSEHOLD.wav`
(sha256: `63699bfd7afa4de151d0fbec4929fe58f65b8305979261b0459058b73b280ff5`。
元公開版`er003_output/n3_01/household/b1b/assembled/`のwav
[`e4eb6061a8b351139b915bc3310f92e1698517938c24ae574eae5ead3efd69de`]とは
point_one差分により不一致、想定どおり)。

## 4. Assembly後の整合確認

- **duration**: 284.754秒 / **peak**: 0.8312 / **clipping**: False /
  **headroom safety valve**: 不適用(peak_before=0.8311974、閾値0.98未満、
  cause_piece=Comment 2)。詳細:
  `er003_output/n3_01/household/fact03_fix_02/b1b/run_summary_assemble.json`。
- **timeline段順**: `audit/timeline.json`実測で Intro→Welcome→Topic
  intro→Notification 1→Preview intro→Preview→Notification 2→Key phrases
  intro→Key Phrase 1〜5→Notification 3→Full story intro→Comment
  1→Full Story Part 1→Comment 2→Full Story Part 2→Comment 3→Point
  Notification→Point One heading→Point One→Point Notification→Point
  Two heading→Point Two→Comment 4→In One Line→Outro、の期待順どおり(逸脱
  なし)。
- **記事本文(revision3a)とTTS入力の一致**: `article.md`33行目・
  `parts.json.point_one_body`・`audit/tts_generation_results.json`
  `segments.point_one.text`/`canonical_text`の4箇所を突合し完全一致を
  確認済み(FIX-02継続1で既に確認済みの内容を本タスクでも再確認)。
- **Key Phrase 5件の整合**: `key_phrases/keywords_canonicalized.json`
  で全5件`qa_overall_status: "PASS"`を確認。narration側sha256も全10ファイル
  (英語5+日本語5)がoriginalとbyte完全一致。

## 5. player

生成物: `er011_output/open138_household_fact03_b1b_minimal_fix_03/build_player_03.py`
（既存共通module`audio_review_player.py`のみ使用、標準フォーマット、
Gate 7 (a)〜(l)準拠、rows=29・unresolved=0）。

**player file:///パス**:
`file:///C:/Users/tensh/eigo-radio/er011_output/open138_household_fact03_b1b_minimal_fix_03/player.html`

topic_introの行にHUMAN_APPROVED経緯、kp2_englishの行に既存承認経緯、
point_oneの行にrevision3a差分を、それぞれ注記として明記。

## 6. 費用

全処理がローカル(record_human_approval=ファイルI/O、Gate/Assembly=既存wav
の読み込み・結合・書き出しのみ、TTS/ASR呼び出しなし)。`er011_output/
attempt_history.jsonl`等の共有台帳に本タスク起因の新規エントリなしを確認済み。
**実費¥0**(上限¥10に対し¥0)。

## 7. 副次的観察(実装せず報告のみ)

`assembled/`ディレクトリのmp3(`English_Your_Way_B1B_HOUSEHOLD.mp3`、
タイムスタンプAug 17)は、FIX-02継続1時点の`shutil.copytree`由来の旧版
(修正前original)のまま残存しており、本タスクで新規生成したwav(revision3a
+topic_intro承認を反映)とは対応しない。委任範囲はwav Assembly→Gate→player
までであり、mp3変換は指示されていないため実施していない(推測拡大実装
はしない)。

## 8. OPEN-139判断材料(実装・policy提案はしない、報告のみ)

本タスクで、2026-08-17承認時点でSTOPPED状態のまま公開されていた
topic_introについて、現行Gate導入前は承認記録(`human_approved_segments.json`)
自体が存在しなかったため、当時「STOPPED記録が残っているにもかかわらず
episodeとして公開・配信されていた」という証跡不整合が実際に存在していた
ことを確認した(現行Gateが後から追加されたことで、今回初めて機械的に
検知された)。同種の事例(現行Gate導入前に承認済みのepisodeで、STOPPED/
未検証segmentがそのまま公開されているケース)が他のレガシー記事にも
存在しうるかどうかは未調査であり、遡及QA方針(OPEN-139)はユーザー/Fable
の判断が必要な事項として、ここでは実装せず提示のみ行う。

## 9. 新規/変更ファイル一覧

- 新規: `er011_output/open138_household_fact03_b1b_minimal_fix_03/`
  (`topic_intro_human_approval_and_assemble_03.py`・
  `topic_intro_human_approval_and_assemble_03_result.json`・
  `build_player_03.py`・`player.html`)
- 変更: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/
  human_approved_segments.json`(topic_introの承認記録を追記、kp2_english
  記録は保持)、`assembled/English_Your_Way_B1B_HOUSEHOLD.wav`(新規Assembly
  実行、point_one差分反映)、`audit/gain_report.json`・`audit/timeline.json`・
  `audit/headroom_report.json`・`run_summary_assemble.json`(Assembly実行に
  伴う再生成)。`audit/tts_generation_results.json`の`status`フィールドは
  **無変更**。
- 不変(確認済み): `er003_output/n3_01/household/{a2,b1b}/`(元の公開済み
  Artifact、本タスクでは一切編集していない)。`docs/pm/ACTIVE_TASK.md`・
  `RESULT_PACKET.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`
  ・`HISTORY_INDEX.md`(いずれも本タスクでは編集していない、SSOT/Git禁止
  指示どおり)。

## 10. STOP条件該当性

- topic_intro HUMAN_APPROVED記録: 完了(ユーザー決定どおり)。
- Gate: 既定経路・opt-in構造経路ともPASS。
- Assembly: OK(clipping無し、headroom不要)。
- Human Review Lock: 本ラウンドでは発動せず(承認記録はGate到達前の記録
  行為のみ、TTS再生成を伴わないため)。
- 費用超過: 非該当(¥0 / 上限¥10)。
- **完成音声の置き換え判断はユーザー試聴後**(元artifact
  `er003_output/n3_01/household/b1b/`は無編集のまま保持)、
  **USER_FINAL_AUDIO_REVIEW_REQUIRED**としてここでSTOPする。
