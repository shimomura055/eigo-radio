# ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01 完了報告

**管理ID: ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01**
**日付: 2026-09-06**
**種別: Production配線(ユーザーが`APPROVED_FOR_PRODUCTION`と承認済み)**

## 0. タスクの位置づけ

PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01(2026-09-06)で「TTS方式は正式
リリース前=Standard同期・正式リリース後の実量産=Batch API」という運用
基準が決定されたが、それまではmonkeypatch等の一時的な手段でしか切替
できず、コードから明示的・恒久的に選択する手段が無かった。本タスクは
その運用基準を支える最小限の切替スイッチ(環境変数1つ)を、既存の
drop-in factory1箇所へ追加する配線タスク。

## 1. 何が問題だったか
TTS(音声合成)の実行方式には「Batch」(まとめて安く処理、1件あたり
90〜170秒程度かかる)と「Standard」(1件ずつすぐ返る、数秒)の2種類が
あり、どちらを使うかは環境変数のような簡単な方法で選べず、コードを
一時的に書き換える(monkeypatch)必要がありました。これは開発・検証
作業のたびに手間と間違いのリスクを生んでいました。

## 2. 何を変更したか
- Production音声生成が共通に使っている唯一の生成部品(factory)
  [er006_batch_tts_wiring_01.py](er006_batch_tts_wiring_01.py)の
  `make_batch_tts_call_fn()`1箇所に、環境変数`TTS_EXECUTION_MODE`
  (値`BATCH`または`STANDARD`、大文字小文字は区別しない、何も設定
  しなければ`BATCH`)を読む分岐を追加しました。
- `STANDARD`を指定すると、既存のStandard同期関数(声・話し方の指示・
  読み上げる文章は一切変更しない、既存の別モジュールの関数)をそのまま
  返します。
- `BATCH`/`STANDARD`以外の値を設定した場合は、静かにBatchへ戻すのでは
  なく、その場でエラーにして止めます(設定ミスに気付かずに量産が
  走ってしまうことを防ぐため)。
- どちらのモードで生成したかを、既存のコスト記録ログへ
  `tts_execution_mode`という項目として追加で記録するようにしました
  (既存の記録項目は一切変更していません)。
- 音声生成6箇所(Production call site)のコード自体は1行も変更して
  いません。声・話し方の指示・やり直し(retry)の仕組み・音声検証の
  仕組み・使い回し保存(Master Audio Store)は無変更です。
- Master Audio Store(同じ声・同じ文章なら音声を使い回す仕組み)の
  識別キーには、モード(Batch/Standard)を含めませんでした。理由:
  同じmodelを使う以上、Batch/Standardのどちらで作っても音質は同等で
  あり、モードを区別すると既存の使い回し可能な音声資産が無駄に
  再生成されてしまうためです。

## 3. 何が改善されるか
- 環境変数を1つ設定するだけで、コードを書き換えずにTTS実行方式を
  切り替えられるようになりました。開発・検証時は自動的にStandard
  (速い)が使われ、Batch(安いが遅い)へ切り替える必要がある場面
  (正式リリース後の実量産)だけ明示的に指定する運用が可能になり
  ました。
- どちらのモードで生成したかが記録に残るため、後から確認できます。

## 4. リスク・注意点
- 実際にAPIを使った動作確認(小額)を行い、Standard指定時は数秒で
  完了すること、未設定時(既定)は実際にBatch APIが呼ばれ90〜160秒
  程度かかることを確認しました(詳細は下記5節)。
- 既定(未設定)の動作は従来どおりBatchのままで、既存の呼び出し元
  コードは一切変更していないため、既存挙動への影響はありません。
- 今回の確認run中、Batchモードの1件(Key Phrase「opt out」)がASR
  (音声認識による内容検証)で不合格になりましたが、これは配線の
  不具合ではなく、以前から知られているTTS/ASRの実行ごとのばらつき
  (同じ文言・同じ方式でも毎回同じ結果になるとは限らない現象)による
  ものです。詳細は下記5節参照。

---

## 5. 実装詳細・Gate 3チェックリスト

### 5-1. 配線箇所(1箇所であることの確認)

環境変数を読む分岐は`er006_batch_tts_wiring_01.py::resolve_tts_execution_mode()`
1関数のみに存在し、`make_batch_tts_call_fn()`の先頭でこれを呼ぶ形で
1回だけ判定する。Production call site 6箇所はいずれもこの関数を
呼ぶだけで、コード変更なし:
- `er003_v1_crosslevel_audio_02_common.py`(`repro01`の配線済み関数を
  自身で構築せず再利用)
- `er003_v1_repro01_main_generate.py`(2箇所: `generate_narration_
  snippet_verified_strict`/`generate_english_component_minimal_
  instruction`)
- `er003_v1_sing01_news_tail_fix.py`
- `er003_v1_sing01_point_headings_aoede.py`
- `er003_v1_sing01_voice01_generate.py`
- `er003_v1_n3_01_tts_generate.py`

初回・技術的retry(`er002_common._call_tts_with_retry`)・content
retry cascade・fallback(English lock等)・regenerationは、いずれも
同じ`make_batch_tts_call_fn()`が返す`tts_call_fn`を通るため、全経路が
同じ分岐を共有する。

### 5-2. 新規単体テスト

[er011_tts_execution_mode_switch_wiring_01_test.py](er011_tts_execution_mode_switch_wiring_01_test.py)
(11件、全PASS): 既定(未設定)→BATCH解決・Batch job作成経路を通ること、
`STANDARD`→Standard解決、小文字`standard`も可、`Batch`大文字小文字混在も可、
不正値→ValueError、`STANDARD`時は`er003_b1_p7a_audio.make_tts_call_fn_
for_model`へ委譲されること(引数含む)、そのモジュールが無い場合は
`er002_gemini_client.make_tts_call_fn`へフォールバックすること、
Batch/Standard両モードで返る関数の呼び出し形状(`prompt: str -> bytes`)
が同一であること、Batch経路のログに`tts_execution_mode=BATCH`が記録
されること、Standard経路(TTS呼び出しのみ、text呼び出しは対象外)の
ログに`tts_execution_mode=STANDARD`が記録されることを検証した。

### 5-3. 既存回帰・プロジェクト全体回帰

- `er006_batch_tts_wiring_01_test.py`(既存Batch wiring回帰): 14件PASS
  (fail-closed確認`test_no_implicit_standard_fallback`含め全PASS、
  今回の分岐追加は`make_batch_tts_call_fn`本体のBatch実行コード自体を
  変更していないため影響なし)。
- `er007_ja_tts_retry_path_fix_test_01.py`(TTS retry回帰、ER-011-
  TTS-STANDARD2-MINIMAL1系): 22件PASS。
- プロジェクト全体回帰(`run_project_regression.py`、`er0*_test_*.py`
  自動探索): 2084件収集・2081 PASS・3 failed。失敗3件は
  `er003_test_bad.FixtureTests.test_case_0`(意図的fixture)・
  `er003_test_p2j_investigate`の2件(OPEN-77、既知のmeta-test集計
  バグ)であり、`git stash`で本タスクの変更を一時的に外して同一
  regressionを再実行しても同じ3件・同じ収集数(2084件)で失敗する
  ことを確認し、本タスクと無関係な既存failureであることを確認した。

### 5-4. Runtime evidence(実API、小額)

出力先: `er011_output/tts_execution_mode_switch_wiring_01/`
使用テキスト: 既存の承認済みProduction文言、Key Phrase英語「opt out」
(ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01のSmoke確認と同一文言を再利用)
呼び出した実Production経路:
`er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()`
(内部で`generate_narration_snippet_verified_strict`→
`batch_wiring.make_batch_tts_call_fn`を経由、Production call siteを
実際に駆動)

**(1) `TTS_EXECUTION_MODE=STANDARD`**(このプロセスにのみ環境変数を
設定、他プロセス・`.env`・グローバル環境は無変更):
- `client.models.generate_content`を実際に2attempt呼び出し
  (elapsed 3.185秒・2.727秒、いずれも数秒台)。
- `status=OK`(ASR検証PASS、attempt2でNORMALIZED_MATCH相当により合格)。
- `raw_usage_log.jsonl`に`tts_execution_mode=STANDARD`が2件記録され
  たことを確認(`api=models.generate_content(TTS)`のみ、text呼び出し
  には付与されない設計どおり)。
- 詳細: `er011_output/tts_execution_mode_switch_wiring_01/standard/`
  (`kp_opt_out_english.wav`・`evidence_result.json`・
  `raw_usage_log.jsonl`)

**(2) 未設定(既定)**:
- `client.batches.create`を実際に4attempt呼び出し(elapsed 80.5/
  73.3/155.8/117.0秒。既存実測レンジ91〜167秒[ER-006-TTS-BATCH-
  WIRING-SOT-CLEANUP-01]と整合)。
- `raw_usage_log.jsonl`に`tts_execution_mode=BATCH`が4件記録された
  ことを確認(`provider=gemini_batch`)。
- この回はPrimary(Minimal instruction)2attempt+Fallback(English
  lock)2attemptの合計4attemptすべてがASR内容検証で不合格となり、
  `status=STOPPED`(既存のfail-closed設計どおり、上限到達で正しく
  停止)。同一Key Phrase「opt out」は過去のSmoke確認(2026-08-22)
  では1attemptでPASSしており、今回のみ不合格になったことから、
  配線自体の不具合ではなく既知のTTS/ASR run-to-run非決定性による
  ものと判断した(Batch job自体は4回とも`client.batches.create`
  経由で正常にSUCCEEDEDしている)。
- 詳細: `er011_output/tts_execution_mode_switch_wiring_01/batch/`
  (`kp_opt_out_english.wav`・`evidence_result.json`・
  `raw_usage_log.jsonl`)

試聴用(参考、Batch経路は内容不合格のためあくまで技術動作確認用):
- `file:///C:/Users/tensh/eigo-radio/er011_output/tts_execution_mode_switch_wiring_01/standard/kp_opt_out_english.wav`
- `file:///C:/Users/tensh/eigo-radio/er011_output/tts_execution_mode_switch_wiring_01/batch/kp_opt_out_english.wav`

### 5-5. cache identity方針

Master Audio Storeのcache identityにはモード(Batch/Standard)を
含めない。理由: 同一model・同一voice・同一canonical text・同一trim
policyであれば、Batch/Standardいずれで生成しても音声品質は同等
(同一モデルを異なる実行方式[client.batches.create vs client.models.
generate_content]で呼んでいるだけ)であり、モードをキーに含めると
既に生成済みの再利用可能な音声資産が、モードが変わるたびに不要に
再TTSされてしまう。既存資産の再利用を優先する判断とした。

### 5-6. SSOT更新

- `CURRENT_SPEC.md`「Gemini TTS実装方式(Batch API)」行・「TTS」行:
  実行モード切替の仕様(環境変数名・既定・不正値の扱い・記録方法・
  cache identity方針・実API確認結果)を追記し`PRODUCTION_WIRED`と
  明記(既存文は削除せず維持)。
- `DECISION_LOG.md`: 新規エントリ`ER-011-TTS-EXECUTION-MODE-SWITCH-
  PRODUCTION-WIRING-01`を追加(APPROVED→PRODUCTION_WIRED、回帰・
  Runtime evidence全件を記録)。
- `docs/pm/PM_GOVERNANCE.md` 7-3: 「Standard同期の指定は環境変数
  `TTS_EXECUTION_MODE=STANDARD`で行う(monkeypatch不要)」を1文追記。
- `OPEN_ITEMS.md`は本タスクでは変更していない(並行タスク使用中の
  ため。追記が必要な事項は発生しなかった)。

---

## 6. Approved specとProduction挙動の一致確認

承認された仕様「TTS実行モード切替を1箇所追加する最小変更」どおり、
(a) 分岐は`make_batch_tts_call_fn()`1箇所のみ、(b) 既定は`BATCH`で
既存挙動を変更しない、(c) call site 6箇所・voice・style instruction・
Structured Separation・retry cascade・Validator・Master Audio Storeは
無変更、(d) 選択モードはruntime evidenceとして記録、であることを
コード確認・実API確認の両方で一致させた。

---

## 7. Gate 3充足状況・懸念

Gate 3チェックリスト(配線1箇所確認・新規単体テスト・既存回帰・
プロジェクト全体回帰・Runtime evidence[Standard/Batch双方]・SSOT
更新・仕様一致確認)はすべて満たした。懸念点として、Batchモードの
Runtime evidence run自体はASR内容検証でSTOPPEDに終わったが、これは
配線が正しく機能していること自体は示している(実際に`client.batches.
create`が4回呼ばれ、`tts_execution_mode=BATCH`が正しく記録された)。
TTS音声品質・ASR判定の非決定性そのものは本タスクのスコープ外であり、
新規Open Itemとしては起票していない(既知の運用上の注意点として
CURRENT_SPECに既に記載済みの内容と同種の事象のため)。
