# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PLAN-01

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PLAN-01`。
**読み取り専用の影響範囲分析タスク**。コード・Prompt・SSOT(`docs/pm/ACTIVE_
TASK.md`・`docs/pm/RESULT_PACKET.md`・`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`CURRENT_SPEC.md`・`ARTIFACT_REGISTRY.md`)は一切編集していない。API呼び
出し(LLM/TTS)は行っていない(費用¥0)。Git操作も行っていない。書き込みは
本ファイル1件のみ。

## エグゼクティブサマリー

1. 3V方式(B-Family記事の3声Voice構成)は2026-09-10、並列タスク
   `PM-CLOSEOUT-CONSOLIDATION-65`により`APPROVED_FOR_PRODUCTION`(未配線)
   とSSOT反映済み(`DECISION_LOG.md` 10247-10336行、`CURRENT_SPEC.md`
   602行)。本Reportはその配線計画。
2. B-Family 2V(2声Voice構成)のB1 Production経路は既に`PRODUCTION_WIRED`
   (Phase 1スコープ、`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`)、
   A2 Production経路も`PRODUCTION_WIRED`(`EDITORIAL-B-FAMILY-VOICES-A2-
   PRODUCTION-WIRING-01`)。3VはB1のみTrial実装(`er012_editorial_b_voices_
   3v_audio_trial_01.py`、root、Trial専用スクリプト)。
3. 3V Audio Trial Report自身が「Production配線に必要な項目」として5項目
   を明示済み(下記2〜6)。`OPEN_ITEMS.md` OPEN-132行にも同内容が15項目
   チェックリストの11〜15番として登録されている。
4. 主要な差分は5点: (1)registry`build_required_structure()`の2声固定
   シグネチャ、(2)Gate辞書2件への`point_three`系segment未登録、
   (3)Comment 2/3の3V文言が未承認の手動ドラフトのまま、(4)segment命名
   方式(`point_one/two/three` vs `voice_1..N`)未確定、(5)Voice 3
   (Schedar)の「fallback候補→本採用」格上げの正式承認未取得。
5. retry/fallback/regeneration機構自体(TTS retry cascade・Human Review
   Lock・disfluency gate・OPEN-121/122安全機構)はvoice名を引数で受け取る
   汎用primitiveであり、3V Trialでも無改造で機能した(実測確認済み)。
   ただしVoice 3用のfallback声(Voice A/Bのみ`VOICE_FALLBACK`に定義あり、
   Voice 3分は未定義)は新規のUSER_DECISION_REQUIRED候補。
6. Audio structural gate(構造完全性チェック、OPEN-129)は`PRODUCTION_
   WIRED(opt-in)`済みで3V Trialでも実際に機能したが、mandatory化は
   Trigger(b)(次回A-Family Production run実績)未達のため`DEFERRED`の
   まま(本配線でも変更しない)。
7. 残存課題6点(3V長文化・Tension再膨張・Local Rewriteによる人物Voice
   抽象化・Fact Checker A'負荷・Distinctness維持・Audio structural gate
   mandatory化)はいずれも「未解決」であり、本配線計画では大半を「観測
   継続」へ送る(deferred維持)。詳細は7節。
8. Phase分け(Phase 1=経路実装+オフラインtest、Phase 2=runtime発火確認
   1本、Phase 3=SSOT更新→PRODUCTION_WIRED判定)を提案する(10節)。
9. ユーザー判断が必要な項目は6件(11節)。特にsegment命名方式とVoice 3
   格上げの正式承認は、後戻りコストが大きいため先行決定を推奨する。
10. 見込み費用はPhase 2 runtime確認1本あたり¥90〜150(3V Audio Trial実測
    ¥93.82・2V Phase1実測¥27.56〜28.64を根拠、いずれも実測、本Reportでの
    追加費用は¥0)。

---

## 1. 現状の3V実装の所在

- Trial実行結果: `EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01_REPORT.md`
  (実行結果)・`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT_
  REPORT.md`(SSOT整理・Gate 1判定確定)。
- 実装ファイル: `er012_editorial_b_voices_3v_audio_trial_01.py`(root、
  982行、**Trial専用ファイル**)。内部の主要関数(実ファイル確認、行番号
  付き):
  - `split_six_voice_sections()`(208行目): 6区切り(Hook/3 Voices/
    Tension/Closing、`##`/`###`混在見出し)のparser。
  - `build_parts_3v()`(227行目): 記事本文からsection抽出。
  - `build_required_structure_3v(voice_1, voice_2, voice_3)`(261行目):
    16 segment・`point_one`/`point_two`/`point_three`命名の
    required_structure(Trial側正本、**registry正本[`build_required_
    structure()`]とは別定義の二重化状態**)。
  - `build_b1_voices_timeline_3v(parts, voice_1, voice_2, voice_3)`
    (601行目): 3声版Assembly timeline builder。
- Production関数の呼び出し方: Trial Reportの記述どおり、既存Production
  TTS関数(`b1prod.generate_voice_body_wide_margin`・
  `voice01.generate_charon_english`・`point_headings.generate`・
  `news_tail_fix.generate_news_narration_wide_margin`)は**引数で呼ぶだけ**
  (Production側は無変更)であることをTrial Report本文で確認した(実装
  ファイル自体の逐語照合は本タスク範囲では未実施、Trial Reportの記述を
  一次情報とする)。
- 結論: **3V実装は現状すべてTrial harness専用**(root直下のTrialスクリプト
  1本)であり、Lane B正式ファイル(`er012_b_family_editorial_type_registry_
  01.py`・`er012_b_family_voices_production_01.py`・`er012_b_family_
  production_runner_01.py`)への実装は一切ない(`Grep`で3件の正式ファイル
  いずれにも`voice_3`/`point_three`/`3v`系の記述なしを確認)。

## 2. B-Family Production正式初回経路(2V)

- 2V B1: `EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`。
  Status(同Report末尾): `PRODUCTION_WIRED`(Phase 1スコープ、一人称"I"の
  機械保証はPhase 2保留)。`CURRENT_SPEC.md` 580-585行でも同様に
  `PRODUCTION_WIRED`(Phase 1スコープ)と記載。
- 2V A2: `EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01_REPORT.md`。
  `CURRENT_SPEC.md` 591-601行の表で全項目`PRODUCTION_WIRED`。
- 実装ファイル3本(実ファイル確認、`wc -l`で行数取得):
  - `er012_b_family_editorial_type_registry_01.py`(443行) — Editorial
    Type registry。Voice割当(`VOICE_ASSIGNMENT`=45行目、`VOICE_FALLBACK`
    =51行目)、物理構造(`SECTION_LABELS`=59行目、5区切り固定)、Comment
    Contract(`COMMENT_ROLES`=150行目)、`EDITORIAL_TYPES`辞書(364行目)、
    `build_required_structure(level, voice_a, voice_b, editorial_type)`
    (424行目、**voice_a/voice_bの2引数で固定**、voice_cは受け取れない)。
  - `er012_b_family_voices_production_01.py`(500行) — B1用parser・
    Voice可用性チェック・Voice本文TTS(`generate_voice_body_wide_margin`)・
    B1用timeline builder。
  - `er012_b_family_voices_a2_production_01.py`(821行) — A2版。
  - `er012_b_family_production_runner_01.py`(1050行) — resumable stage
    方式のrunner。`main()`(981行目)が`level`文字列(`"b1"`/`"a2"`のみ、
    987行目`if level == "a2":`)で分岐。`run_tts(parts, support_texts,
    voice_a, voice_b)`(303行目)・`run_tts_a2(...)`(752行目)いずれも
    **voice_a/voice_bの2声シグネチャ固定**。
- 共有Gate(`er003_v1_n3_01_assemble.py`): `verify_episode_audio_
  validation_gate(out_dir, level, required_structure=None)`(375行目)、
  `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`辞書(166行目、キー
  `"B1"`/`"A2"`/`"B_FAMILY_A2"`の3種、`"B1"`はA-Family/B-Familyで共有)。
- **結論**: 2VはB1・A2とも`PRODUCTION_WIRED`。ただしいずれもLane B内で
  完結する「Phase 1」スコープであり、Lane A共有Writerへの一人称"I"機械
  保証(Phase 2)は未実装のまま(`OPEN-132`行で追跡中)。3Vの配線対象は
  この「Phase 1と同じ音声Production経路」であり、Phase 2(Writer統合)
  ではない(委任文の背景説明とも整合)。

## 3. 2V正式経路と3V Trialの差分

| 差分項目 | 2V正式経路(現状) | 3V Trial(現状) | Production経路への組み込み方 | 2V互換条件 |
|---|---|---|---|---|
| registry`build_required_structure()` | `(level, voice_a, voice_b, editorial_type)`固定2声(424行目) | Trial内`build_required_structure_3v(voice_1, voice_2, voice_3)`として別関数(261行目)、registryとは二重化 | シグネチャへ`voice_c: str \| None = None`等の後方互換オプション引数を追加し、`voice_c`が渡された場合のみ3声用`_ROLE_TO_VOICE_RESOLVERS["voice_c"]`解決を行う。または`editorial_type`に新規`"b_family_voices_3v"`を追加し独立configとする(design判断が必要、10節Phase 1で提案) | 既存呼び出し元(`voice_c`省略)はバイト単位で不変にする(既定値`None`、単体テストで固定) |
| `B_FAMILY_B1_REQUIRED_SEGMENTS` | 14 segment(`point_one`/`point_two`の2 voice、267行目) | Trial側16 segment(`point_one`/`point_two`/`point_three`、命名は3V Audio Trial Reportの記述どおり) | registryへ`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`(新規定数)を追加し、`EDITORIAL_TYPES`の新規configキーへ登録(既存`B_FAMILY_B1_REQUIRED_SEGMENTS`は無変更) | 既存2V configは無変更のまま温存 |
| `run_tts()`/`run_tts_a2()` | `(parts, support_texts, voice_a, voice_b)`2声固定(303/752行目) | Trialの`build_b1_voices_timeline_3v(parts, voice_1, voice_2, voice_3)`が別関数として存在(601行目) | 新規`run_tts_3v()`(2V版のコピーへ3声目のループを追加)を`er012_b_family_voices_production_01.py`側へ新規追加。既存`run_tts()`は無変更 | 既存`run_tts()`呼び出し元は無変更 |
| `er012_b_family_production_runner_01.py::main()` | `level`文字列で`"b1"`/`"a2"`のみ分岐(987行目) | Trial runnerは別ファイル(`er012_editorial_b_voices_3v_audio_trial_01.py`)として独立実行 | `main()`へ`voice_count`または`level in ("b1_3v",)`等の新規分岐を追加(具体名称は5節・8節参照)。Trialスクリプトを一切importしない構成(Gate 3「DEV/Trial-onlyではないこと」)を2V Phase1と同じ設計で踏襲する | 既存`"b1"`/`"a2"`分岐は無変更 |
| `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`(共有`er003_v1_n3_01_assemble.py` 166行目) | `"B1"`キーに`point_one_heading`/`point_two_heading`のみ登録 | `point_three_heading`は未登録(3V Audio Trial Reportで既知課題として明記) | `"B1"`キーへ`point_three_heading`を追加する場合、**A-Familyと2V B-Familyが同じ`"B1"`キーを共有している**(OPEN-129 Trial-01で判明済みの設計上の既知事象)ため、追加しても既存segment名と衝突しない(新規segment名のため影響なし)ことを単体テストで確認する必要がある | 既存"B1"キーのA-Family/2V B-Family判定には影響しない設計にする(新規segment名の追加のみ) |
| Comment 2/3の3V文言 | `VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_ROLE`はregistry内に確定Contract(2声版、99/117行目) | design.md B-1の3V版ドラフトを`TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED`として無変更のまま使用(LLM再生成せず)、registry未登録 | Comment 2/3の3V版文言をユーザー承認(Contract化)のうえregistryへ`VOICES_COMMENT_2_ROLE_3V`等として正式追加するか、既存2声版Prompt自体を「voice数に依存しない汎用文言」へ書き換えるかの設計判断が必要(`OPEN-132`追記(6)で既に同種の懸念[voice数パラメータ化、定数を増殖させない設計]が記録済み) | 既存2声版Comment 2/3 Contractはbyte単位で不変にする |
| TTS voice設定・Voice 3割当 | `VOICE_ASSIGNMENT`(voice_a/voice_b)・`VOICE_FALLBACK`(voice_a→Schedar、voice_b→Sulafat) | Voice 3=Schedar(Fable決定、3V Audio Trialで技術的availability確認のみ、fallback候補内からの格上げ) | `VOICE_ASSIGNMENT`へ`voice_c: "Schedar"`を追加。**Voice 3自体のfallback声は現状未定義**(Schedarが使えない場合の代替声が無い) | 既存`voice_a`/`voice_b`のfallback関係は無変更 |
| Fact Checker A'(Voice別事実帰属) | `FACT_ATTRIBUTION_MODE_DEFAULT = False`(opt-in、295行目)、`_VOICE_EVIDENCE_LINE_RE`は`VOICE_(\d+)_EVIDENCE`の正規表現で**voice数非依存の設計**(297-300行目のコメントで3V/4Vもタグ名追加のみで対応可能と明記済み) | 3V Audio Trialでは個別に`VOICE_3_EVIDENCE`タグを使用したかは本タスク範囲では未確認(Trial ReportにFact A' 2/2 PASSの記載はあるが、attribution modeの有効/無効はTrial Report記述からは特定不可) | 既存opt-inフラグ・正規表現は3声でも無変更で動作する設計のため追加実装は不要と見込まれる(**未実測、確認は8節runtime evidence計画で行う**) | 既定OFFのまま、2V既定挙動に影響なし |
| Local Rewrite(Ledger Deviation是正の文章書き直し) | 既存Production機構(voice数非依存、記事テキストのみ操作) | 3V Trialで人物Voiceを抽象化しAnalytical Leakageを再導入する失敗モードが2回観測(Trial-01/03、7節参照) | 本配線では対策コード変更を行わない(7節で「観測継続」に分類する提案) | 既存2V挙動に影響なし(この機構自体は無変更のため) |

## 4. retry/fallback/regeneration整合

- TTS retry cascade・Human Review Lock(`guarded_generate`)・disfluency
  gate・OPEN-121(repetition QA)/OPEN-122(connected speech equivalence
  layer)はいずれも`voice_name`を引数として受け取る汎用primitiveであり、
  2V Phase 1配線時点で「呼び出し側のvoice_name以外は全てvoiceに依存しない」
  ことが確認されている(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-
  WIRING-01_REPORT.md` 2節)。3V Audio Trialでも同じprimitiveを3回目の
  声(Schedar)へそのまま適用し、16 segment全て`status=OK`・
  `asr_verified=True`・`repetition_qa_checked=True`を実測確認済み(Trial
  Report)。**したがって、Voice 3追加自体のためにretry/fallback機構本体
  へ変更を加える必要はないと見込まれる**(既存primitiveの追加呼び出しの
  みで足りる)。
- ただし以下2点は未整備:
  1. **Voice 3自体のfallback声が未定義**(`VOICE_FALLBACK`辞書は
     voice_a/voice_bのみ)。Schedar自体が技術的に使えない場合の代替声を
     どうするか(4番目の声を新規定義するか、Voice 3のみfallbackなしで
     即Human Review Lockへ倒すか)は設計判断が必要。
  2. **Voice 3向けrepetition QA/connected speech equivalence layerの
     enable既定値**: 2V Phase1では修正指示1回目でVoice A/Bの本文
     segmentへ`enable_repetition_qa=True`等を明示適用した経緯がある
     (`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`
     9節)。3V配線時も同じ規約をpoint_three(Voice 3本文)へ明示適用する
     必要があり、既定値の取り違え(Falseのまま)によるGate機構の意図しない
     動作(Assembly GATE_BLOCKED)のリスクがあることは、2V Phase1修正
     指示1回目で実際に一度発生した実例(`in_one_line`のdisfluency_qa
     既定値問題)からも見込まれる(見込み、実測なし)。
- OPEN-129(Audio structural gate、opt-in)は既にB-Family 3V Trialで
  `required_structure`(Trial側正本)を通じて実際に機能し、negative
  control 2件(`VOICE_MISMATCH`・`UNEXPECTED_EXTRA_SEGMENT`)を正しく
  検知したことを実測確認済み(Trial Report)。ただしTrial側正本と
  registry正本が二重化しているため(3節)、Production配線では
  registry側`build_required_structure()`を拡張してこちらを唯一の正本
  とする必要がある(Gate自体の挙動変更は不要、呼び出し元の統合のみ)。

## 5. テスト計画

- 既存Regression/Validator/integration testの所在:
  - `run_project_regression.py`(root、唯一の正式回帰入口。2V Phase1
    配線時`collected=2171 passed=2168 failed=3`[既知3件のみ]を実測、
    2V A2配線時も新規19テスト追加以外の差分なしを実測)。
  - `er012_editorial_b_family_production_phase1_test_01.py`(root、
    2V Phase1の単体テスト14件)。
- 3V wiringで追加すべきテスト(¥0のオフラインテスト、見込み):
  1. registry`build_required_structure()`拡張の契約テスト(voice_c
     省略時に既存2V出力とbyte一致することを固定するテスト、および
     voice_c指定時に3声分のsegmentが含まれることを検証するテスト)。
  2. `B_FAMILY_B1_3V_REQUIRED_SEGMENTS`の内容検査(16 segment・
     point_three系命名がTrial側`build_required_structure_3v()`の出力と
     一致することを検証、2重定義の解消を保証)。
  3. `run_tts_3v()`(新規)のmockベース契約テスト(2V Phase1の
     `RunTtsBodySegmentSafetyFeatureContractTests`と同型、Voice 1/2/3
     いずれも`enable_repetition_qa=True`・`enable_connected_speech_
     equivalence_layer=True`で呼ばれることを検証)。
  4. `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`拡張後、既存A-Family
     `"B1"`キー利用箇所への非影響テスト(新規segment名`point_three_
     heading`追加が既存A-Family B1 episodeの判定に影響しないことを
     固定)。
  5. `er012_b_family_production_runner_01.py::main()`の新規分岐
     (level文字列またはvoice_count引数)が、既存`"b1"`/`"a2"`分岐の
     出力へ影響しないことを検証する回帰テスト(2V A2配線時の
     「既存B1経路は無変更」確認パターンを踏襲)。
- runtime発火確認に必要な最小の実行(記事1本分): 3V基準記事(3V Audio
  Trial-02最終版、既に承認済み・費用0で再利用可能な既存article.md)を
  Production正式経路で1本通す。**見込み費用**: 3V Audio Trial実測
  ¥93.82(TTS¥57.69/LLM¥33.41/ASR¥2.72)を上限目安とする(記事は既存の
  ため再利用でKey Phrase生成コストは圧縮できる見込み、実測ではない)。

## 6. runtime evidence計画

- **model_id/routing**: 2V Phase1 Reportの実測パターン(TTS:
  `gemini-2.5-pro-preview-tts`[`p9a.ENGLISH_MODEL_NAME`]、Support:
  `routing.require_model("B1_SUPPORT", ...)`)を踏襲し、Voice 3
  (Schedar)呼び出しでも同一のTTS model_id・`voice=Schedar`が実際に
  使われたことを`tts_generation_results.json`の該当segment(`point_
  three`)で確認する。
- **voice ID発火確認**: `tts_generation_results.json`の`point_three`/
  `point_three_heading`エントリの`voice`フィールド値=`Schedar`である
  ことを機械チェックする(2V Phase1 Reportの`voice_resolution.json`と
  同型のログを新設)。
- **Audio structural gate発火確認**: `verify_episode_audio_validation_
  gate()`呼び出し時に、registry統合後の`build_required_structure()`
  (3声版)が実際に`required_structure`引数へ渡され、16 segment全件が
  `complete=True`で一致することをログ(2V Phase1の`voice_resolution.
  json`・OPEN-129 Trial-01の`complete=True`ログと同型)で確認する。
- **Cost/latency**: 3V Audio Trial実測値(TTS/LLM/ASR内訳)を基準値とし、
  Production経路実行時の実測値と比較する(異常な乖離が無いことの確認)。
- **保存先**: 既存`ER-*_REPORT.md`/`er0XX_output/`構造を踏襲し、新規
  `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-01_REPORT.md`(実装
  タスク側の管理ID、本Reportとは別)と`er012_output/editorial_b_family_
  voices_3v_production_wiring_01/`配下へ格納する想定(実装タスクの命名は
  ユーザー承認後にFableが確定)。

## 7. 残存課題6点の扱い(「全部解決済み」ではない)

| # | 課題 | 提案する扱い | 理由 |
|---|---|---|---|
| 1 | 3V長文化(soft target未達が複数Trialで継続) | **観測項目として2V・3V実運用確認へ送る**(変更しない) | 3V Audio Trial実測尺356.6秒は目標380〜400秒の範囲外のままユーザーが試聴のうえ許容と判断した経緯(`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT_REPORT.md`)があり、Prompt側の追加対策は未検証・未承認。配線作業でPromptを変更すると2V実測値との比較基準が崩れるため、まず観測を優先する提案 |
| 2 | Tension再膨張(圧縮後にLedger Deviation是正で語数が後戻り) | **観測項目として送る**(変更しない) | Ledger Deviation Checker自体はWriter配線(Phase 2)の領域に近く、本タスク(音声Production経路の配線)の範囲外。Phase 2着手時のチェックリスト(`OPEN-132`)で再検討する対象として整理するのが妥当 |
| 3 | Local Rewriteが人物Voiceを抽象化しAnalytical Leakageを再導入する失敗モード(Trial-01/03で計2回観測) | **観測項目として送る**(変更しない) | Local Rewrite自体は記事生成後の是正機構であり、音声Production配線の対象ではない。発生頻度・深刻度を2V/3V実運用確認で追加収集してから対策要否を判断するのが安全 |
| 4 | Fact Checker A'負荷(3V/4Vでweb_search回数増) | **観測項目として送る**(変更しない、cache導入等のコスト最適化はユーザー決定[PM-CLOSEOUT-CONSOLIDATION-47]により未実施のまま) | `OPEN-136`で調査済みだが、「安全性を下げるcost optimizationは禁止」との既存決定があり、8項目の観測継続方針が既に確定している。本配線でもこの方針を維持するのみで変更不要 |
| 5 | Voice Distinctnessの維持 | **観測項目として送る**(Gate化はしない) | 3V Audio Trialでは実測(direction_agreement_rate=1.0、method_agreement_rate=0.933)が良好だったが、これは基準記事1本の実測にすぎない。Production配線で新規Gate(閾値判定の自動ブロック化)を追加することは未承認の仕様拡張にあたるため、本配線では実施しない |
| 6 | Audio structural gate mandatory化(OPEN-129) | **変更しない(deferred維持)** | `OPEN-129`は既に`PRODUCTION_WIRED(opt-in)`/mandatory化`DEFERRED`(Trigger(a)[3V/4V Trial実績]到達済み、Trigger(b)[次回A-Family Production run実績]未達)とSSOT確定済み。3V配線がTrigger(b)を満たすわけではない(Trigger(b)はA-Family側の実績)ため、本配線をもってmandatory化を提示することはPM-CLOSEOUT-CONSOLIDATION-29の規定(両Trigger到達まで提示しない)に反する。opt-in経路(registry統合後の`build_required_structure()`)を使うことのみ提案する |

**注記**: 上記6点はいずれも本配線計画の対象外(deferred維持または観測
継続)とすることを提案しているが、これは「解決済み」を意味しない。特に
3(Local Rewriteの失敗モード)は再発リスクが構造的に残ったままである点を
明記する。

## 8. SSOT更新計画

- `CURRENT_SPEC.md`: 「## B-Family(Voices)Editorial Type」節(580行目
  以降)の3V行(602行目)を、配線完了後に`APPROVED_FOR_PRODUCTION`から
  `PRODUCTION_WIRED`(Phase 1スコープ、音声Productionのみ)へ更新する。
  併せて、2V行と同型の詳細行(Voice割当・required_structure・Comment
  Contract・Production経路ファイル名)を新規追加する想定。**仕様本文の
  追加は配線完了後のみ**(本Reportでは追加しない)。
- `OPEN_ITEMS.md`:
  - OPEN-120行: 配線完了後、「配線に必要な5項目」の各項目にstatus
    (実装済み/deferred)を追記。
  - OPEN-129行: 変更不要(mandatory化Trigger状況は本配線で変化しない、
    7節参照)。ただしregistry側`build_required_structure()`統合後の
    3V required_structureが「正本統合完了」となった旨のみ追記候補。
  - OPEN-132行: 配線完了後、11〜15番(3V配線関連5項目)を「対応済み」
    として更新。1〜10番(Phase 2 Writer関連)は変更不要(本配線はPhase 2
    ではないため)。
  - OPEN-136行: 変更不要(観測継続方針のまま)。
- `DECISION_LOG.md`: 配線タスク完了時のエントリを新規追加(本Reportでは
  作成しない)。
- **Dangling Reference Check(新仕様名・rule名の事前確認)**: 本Reportで
  提案した新規名称(`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`・`run_tts_3v()`・
  `voice_c`引数等)はいずれも既存命名規約(`B_FAMILY_B1_REQUIRED_
  SEGMENTS`・`run_tts()`・`voice_a`/`voice_b`)の延長であり、既存の対の
  概念(2V版)が存在することを確認済み。ただし`point_one/two/three`
  vs `voice_1..N`のsegment命名方式自体は`OPEN-132`(PM-CLOSEOUT-
  CONSOLIDATION-42追記)で**未確定のまま**であり、本Reportの提案名称
  (`point_three`系)は3V Audio Trial実績に合わせた**仮称**である点を
  明記する(11節のユーザー判断事項)。

## 9. 影響範囲・リスク・ロールバック

- **変更ファイル一覧(見込み)**:
  1. `er012_b_family_editorial_type_registry_01.py`(既存、拡張) —
     `voice_c`引数追加・`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`新規定数・
     `EDITORIAL_TYPES`へ新規config追加。
  2. `er012_b_family_voices_production_01.py`(既存、拡張) — 3声版
     parser・timeline builder・`run_tts_3v()`新規追加(Trial側の
     `split_six_voice_sections`/`build_parts_3v`/`build_b1_voices_
     timeline_3v`を正式移設)。
  3. `er012_b_family_production_runner_01.py`(既存、拡張) — 新規分岐
     追加。
  4. `er003_v1_n3_01_assemble.py`(**共有ファイル**、最小限拡張) —
     `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`の`"B1"`キーへ
     `point_three_heading`追加のみ(2V A2配線時の「1エントリ追加のみ」
     パターンを踏襲)。
  5. 新規単体テストファイル(1〜2本、見込み)。
  6. `CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`(配線完了後、
     別タスクでSSOT反映)。
- **2V既存Production挙動への影響**: 上記1〜3はいずれも既存関数を無変更
  のまま新規関数・新規引数(既定値で無効化)を追加する設計を提案してお
  り、2V経路への影響はゼロと見込まれる(2V Phase1/A2配線でも同型の
  「共有ファイルは無変更、新規ファイルのみ追加」実績があるため)。4の
  共有ファイル変更は1エントリ追加のみで、新規segment名(`point_three_
  heading`)は既存A-Family/2V B-Family episodeには存在しないため、
  既存判定への影響は無いと見込まれる(**見込み、実測は8節runtime
  evidence計画で行う**)。
- **ロールバック方法**: (a)設定切替 — 新規引数(`voice_c`等)は既定値で
  無効化されるため、3V呼び出しを行わなければ2V経路は変更前と同一に
  動作する。(b)Git revert — 変更ファイルは全て新規追加または最小差分
  (共有ファイルへの1エントリ追加)のため、単一commitのrevertで復旧可能
  と見込まれる。
- **見込み工数**: Sonnetセッション数の見込みは、2V Phase1配線の実績
  (初回実装1回+修正指示2回、計3セッション)を参考に、3V配線でも
  **2〜3セッション**(Phase 1実装1回、Phase 2 runtime確認1回、必要なら
  修正1回)を見込む(見込み、実測ではない)。
- **見込み費用**: Phase 2 runtime確認1本あたり¥90〜150(5節参照、3V
  Audio Trial実測¥93.82を基準)。Phase 1(オフライン実装・テスト)は
  API呼び出しを伴わないため¥0見込み。

## 10. 実装の段階分け案

- **Phase 1: 経路実装+オフラインtest(API呼び出しなし、¥0)**
  - 内容: registry拡張(`voice_c`引数・3V required_structure・Gate辞書
    1エントリ追加)、`run_tts_3v()`新規追加、runner分岐追加、単体テスト
    追加、既存`run_project_regression.py`実行(既知failureのみで新規
    failureゼロを確認)。
  - STOP条件: (a)既存2V経路のregressionに新規failureが1件でも発生した
    場合、(b)共有ファイル(`er003_v1_n3_01_assemble.py`)への変更が
    1エントリ追加を超える規模になった場合、(c)segment命名方式(11節)
    が未確定のまま実装を進めようとした場合(命名の後戻りコストが最大
    のため、確定前に実装しない)。
- **Phase 2: runtime発火確認1本(実API呼び出し、見込み¥90〜150)**
  - 内容: 3V基準記事(既存承認済みarticle.md)をProduction正式経路
    (Trialスクリプト非経由)で1本通す。model_id/voice ID実発火確認、
    Audio structural gate実発火確認、retry/fallback既存上限の非超過
    確認、完成episode+player.html生成。
  - STOP条件: (a)Assembly GATE_BLOCKEDが既存retry上限内で解消しない
    場合(2V Phase1で実際に発生した`point_two`STOPPED事例と同様の
    パターンが起きた場合は、独自にGate回避・閾値変更をせずSTOPして
    ユーザー判断を仰ぐ)、(b)Voice 3(Schedar)が技術的に使用不可
    だった場合(fallback未定義のため、この場合は即STOP)、(c)費用が
    ¥150を明確に超過する兆候が出た場合。
- **Phase 3: SSOT更新→PRODUCTION_WIRED判定**
  - 内容: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`更新、Git
    反映、Fable/ユーザーによる`PRODUCTION_WIRED`受入判定(Sonnetからは
    宣言しない、2V Phase1/A2と同じ運用)。
  - STOP条件: ユーザー承認内容(3V Audio Trial-02基準記事・Voice
    1/2/3=Algieba/Erinome/Schedar・16 segment構造)とProduction実挙動
    が一致しない場合は、SSOT更新を行わずUSER_DECISION_REQUIREDとして
    報告する。

## 11. ユーザー判断が必要な項目

1. **segment命名方式の確定**(`point_one/two/three` vs `voice_1..N`、
   `OPEN-132`PM-CLOSEOUT-CONSOLIDATION-42で既に未決事項として記録済み)。
   推奨: 3V Audio Trialで実際に使用・検証済みの`point_one/two/three`を
   採用(4Vは別途`voice_1..4`のまま据え置きでも実害はないと見込まれる、
   ただし4Vは`DEFERRED`のため今回は判断不要)。理由: 実績があるほうが
   後戻りコストが低い。
2. **Voice 3(Schedar)の「fallbackから本採用への格上げ」自体の正式承認**
   (3V Audio Trial Report・OPEN-132で継続する既出論点)。推奨: 承認
   (3V自体が`APPROVED_FOR_PRODUCTION`となった以上、Voice 3=Schedarの
   使用も暗黙に前提とされていると解釈できるが、**明示的な承認確認を
   推奨**)。理由: fallback候補からの格上げは既存2V配線の運用ルールに
   影響しうる論点のため。
3. **Voice 3自体のfallback声の要否**(4節)。推奨: 「Voice 3は
   fallbackなし、使用不可時は即Human Review Lockへ倒す」を暫定採用し、
   実運用確認(2件)で発生頻度を見てから追加投資を判断。理由: 現時点で
   4人目の声の候補すら未検討のため、先行してfallback声を決めるのは
   時期尚早。
4. **Comment 2/3の3V文言のContract化方式**(3節)。推奨: 既存2声版
   Prompt自体を「voice数に依存しない汎用文言」へ書き換える案を優先
   検討(定数の増殖を避ける、`OPEN-132`追記(6)の懸念と整合)。理由:
   3V専用定数を追加するとVoice数が増えるたびに定数が増殖し保守コストが
   増す。
5. **`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`の`"B1"`キー拡張方式**
   (共有ファイルへの変更、3節)。推奨: 提案どおり`point_three_heading`
   追加のみ(A-Family/2V B-Familyへの影響なしと見込まれる、Phase 1で
   単体テスト固定)。理由: 2V A2配線時の「1エントリ追加のみ」実績パター
   ンと整合し、影響範囲が最小。
6. **Phase 2 runtime確認記事の選定**(既存3V Audio Trial-02基準記事の
   再利用か、新規テーマでの1本目実行か)。推奨: まずTrial-02基準記事の
   再利用(Writer費用¥0、TTS/Assembly費用のみ)でPhase 2を実施し、
   「2V/3Vそれぞれ別テーマで1本ずつProduction実運用確認」計画
   (`PM-CLOSEOUT-CONSOLIDATION-65`で登録済み)は本配線完了後の別タスク
   として実施。理由: 配線自体の検証(runtime evidence)と、実運用確認
   計画(残存課題の深刻度確認)は目的が異なるため分離するのが安全。

## QCD(品質・費用・納期)見込み

- **品質(Quality)**: 既存2V配線パターン(共有ファイル最小変更・新規
  ファイル追加中心)を踏襲することで、2V既存Production挙動への影響は
  最小化できると見込む。ただし残存課題6点(7節)は本配線では解決しない
  ため、配線完了=品質問題解決ではない点を明記する。
- **費用(Cost)**: Phase 1(オフライン)¥0、Phase 2(runtime確認1本)
  見込み¥90〜150、Phase 3(SSOT更新)¥0。合計見込み¥90〜150(実測は
  Phase 2実施後に確定)。
- **納期(Delivery)**: Sonnetセッション数見込み2〜3回(9節)。Fable
  サンドイッチ運用のループ上限(初回+修正最大3回、合計最大4回)の範囲内
  に収まると見込む。

---

## SSOT上で特定できなかった点

- 3V Audio Trialにおいて`FACT_ATTRIBUTION_MODE_DEFAULT`(Voice別事実
  帰属opt-inフラグ)が実際にON/OFFいずれで実行されたか、Trial Report
  本文からは特定できなかった(Fact A' 2/2 PASSの記載はあるが、
  attribution modeの状態は記載なし)。
- `EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md`
  のComment 1/4文言が3V(3人物構成)でも無変更のまま成立する理由(「人数
  非依存の文言のため」という3V Audio Trial Reportの記述)について、
  Contract本文の逐語確認は本タスク範囲では行っていない(Trial Report
  記述を一次情報として採用)。
- 4V(4声Voice方式)の`voice_1..4`命名との優劣比較実測が、本タスク範囲
  で参照した資料内では完了していない(`OPEN-132`PM-CLOSEOUT-
  CONSOLIDATION-42「両命名方式の優劣比較は今後実測をもって判断」との
  記載どおり、判断材料は不足したまま)。ただし4V自体が`DEFERRED`のため
  本配線の判断には影響しない。

---
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EqG9xnr2dZhshz85bFW4Kt
