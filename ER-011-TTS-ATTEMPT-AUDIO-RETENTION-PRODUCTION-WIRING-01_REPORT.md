# ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01

**管理ID**: ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01(+記録訂正
KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01-CORRECTION)
**Lane**: Lane A / Key Phrase・TTS。種別: Production配線(ユーザー2026-09-06
`APPROVED_FOR_PRODUCTION`)+SSOTの記録訂正。**Production変更範囲は「attempt音声を
上書きせず追加保存する」ことのみ。ASR Cascade/Validator/English lock/retry上限は
無変更**(既存の実挙動・判定結果には一切影響しない)。
**コード基準**: 作業ツリー(直前commit `3fb48c3`から本タスクの変更のみ追加)。

---

## 1. 何が問題だったか

既存のTTS retry cascade(`generate_narration_snippet_verified_strict`等、
`er011_human_review_lock_01.py`が管理する7 guarded関数)は、retryのたびに
同一`out_path`を無条件に上書きする設計だった。このため、Human Review Lockへ
到達したsegmentで「attempt 1〜Nそれぞれで実際に何が発話されたか」を事後に
確認する手段が無かった。実際、`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`で
A2 Key Phrase 2「new normal」を調査した際、attempt 1〜3の音声が上書きにより
消失し、現存したattempt 4のみで判断せざるを得なかった。

## 2. 何を変更したか

`er011_human_review_lock_01.py`へ`save_tts_attempt_audio(out_path, route_label,
metadata)`を新設し、review_lockが管理する既存7 guarded関数のTTS retryループ
本体8箇所(下記)へ配線した。各attemptで`out_path`へ実際に書き込まれた音声を、
**上書きせず**`<narration_dir>/attempts/<segment_id>_attempt<N>_<route_slug>.wav`
+同名`.json`(ASR raw出力・分類・instruction種別・model_id・voice・
`tts_execution_mode`・timestamp等)として個別保存する。attempt番号は
`attempts/`配下の既存ファイルを都度スキャンして最大値+1を採番するグローバル
単調増加方式(追加の永続stateなし)。

**配線箇所(8箇所)**:
1. `er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict`
   (Key Phrase Primary/Fallback両stage・Full Story/Preview/News等の標準経路・
   A2英語/日本語standard経路を含め共通経由。route_labelは`style_prefix_override`
   の有無から自動判定、カスタム時はinstruction文のMD5先頭8桁を含めて多段呼び出し
   同士のファイル名衝突を回避)
2. `er003_v1_sing01_voice01_generate.py::generate_charon_english`
3. `er003_v1_sing01_voice01_generate.py::generate_charon_japanese`(standard loop)
4. 同上(fallback loop)
5. `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`
6. `er003_v1_sing01_point_headings_aoede.py::generate`
7. `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback`
   (fallback loop。standard部分は#1経由で既にカバー)
8. `er003_v1_n3_01_tts_generate.py::generate_a2_japanese_with_fallback`
   (fallback loop。standard部分は#1経由で既にカバー)

いずれもASR結果・分類が確定した直後に`save_tts_attempt_audio()`を呼び、返却
パスを当該`attempts_log`/`fallback_attempts_log`エントリへ`attempt_audio_path`
として追記する。既存の`record_outcome()`(無変更)の`last_attempts_log`永続化
経路を経由して、review_lock台帳(`review_lock_state.json`)へも自動的に
attempt保存パスが引き継がれる。

**最終成果物への影響**: 無し。`save_tts_attempt_audio()`は`out_path`を読み取る
だけで一切書き込まない(`shutil.copy2`でコピー元として使うのみ)。

同時に、new normal事象(A2 Key Phrase 2「new normal」STOPPED)の記録を訂正した
(下記6節)。

## 3. 何が改善されるか

Human Review Lockへ到達したsegmentで、どのattemptがどんな音声を生成しどんな
ASR結果になったかを、音声そのものを含めて事後に確認できるようになる
(診断性の改善)。今回のruntime evidenceでは、従来なら消失していたattempt
1〜3の音声も含め4件すべてが個別ファイルとして保存されることを実証した
(4節参照)。最終成果物(Assembly等が読む`out_path`)自体は一切変更されない。

## 4. リスクや注意点

- ASR Cascade/Validator/English lock/retry上限は無変更。今回の変更は「保存を
  追加しただけ」であり、既存の判定結果・retry挙動には影響しない。
- 保持ポリシー(採用take確定後の削除・cleanup)は今回未導入。1 segmentあたり
  最大3〜4attempt×数秒wav(小容量)で、既存の`*.wav`のgitignore方針・出力dir
  構成と矛盾しない。無期限保持のため、量産が進むと`attempts/`配下が蓄積する
  (cleanupは別途検討事項)。
- **プロジェクト全体回帰は実施していない**。無関係な既存スクリプト
  (`test_writer_api.py`・`tts_style_test.py`・backtest系スクリプト)が
  `unittest discover -p "*test*.py"`のモジュールimport時に実TTS/LLM API呼び出し
  を伴う設計であることが判明し、誤って実行してしまった(下記7節「発生した
  副作用」参照)。以降は本タスクが変更したモジュールに限定したtargeted回帰の
  みを実施した。

---

## 5. 実装詳細(補足)

`save_tts_attempt_audio()`は、out_pathがReview Lockの標準的な
".../<theme>/<level>/narration/<segment>.wav"命名規約に従わない場合(単体
テストのダミーパス等)、既存のReview Lock全体と同じ安全側の判断で保存自体を
スキップする(`_has_valid_narration_layout()`を再利用)。

```python
def save_tts_attempt_audio(out_path: str, route_label: str, metadata: dict = None):
    if not _has_valid_narration_layout(out_path):
        return None
    if not os.path.exists(out_path):
        return None
    ...
    attempt_number = (max(existing_numbers) + 1) if existing_numbers else 1
    ...
    shutil.copy2(out_path, wav_path)
    ...
    return wav_path
```

## 6. runtime evidence(実際の実行結果)

`er011_tts_attempt_audio_retention_wiring_01_runtime_evidence.py`を新設し、
TTS_EXECUTION_MODE=STANDARD(PM_GOVERNANCE 7-1、正式リリース前の既定)で、
Production関数を無変更のまま2件実行した(出力先
`er011_output/tts_attempt_audio_retention_wiring_01/`)。

**(1) 英語Key Phrase Component「new normal」**
(`repro01.generate_key_phrase_component_verified`、ASR不一致を起こしやすい
ことがKEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01で確認済みの実例):

| attempt | route | ASR raw | verified | sha256(先頭16桁) |
|---|---|---|---|---|
| 1 | custom_bd5c8f46(Minimal) | 新常態 | False | f8e22787b39a719b |
| 2 | custom_bd5c8f46(Minimal) | 新常態 | False | 43695d03bb1d8872 |
| 3 | custom_31eb2f72(English Lock) | 新常態 | False | f85f4054ff64ec87 |
| 4 | custom_31eb2f72(English Lock) | 新常態 | False | 387e91d04f3b0a8b |

最終status=`STOPPED`(`HUMAN_REVIEW_REQUIRED`)。**4回とも診断-01の元事象
(「新常態」)を実際に再現し**、かつ**4回のsha256がすべて異なる**(=4つの
異なる音声が実際に個別保存された、単なる複製ではない)ことを確認した。
最終成果物`out_path`のsha256(`387e91d0...`)はattempt 4のsha256と完全一致
(=out_pathには常に最後のattemptの内容が残るという既存挙動どおりで、変更
していない)。model_id=`gemini-2.5-pro-preview-tts`・voice=`Aoede`・
`tts_execution_mode=STANDARD`をJSON側で確認済み。

**(2) 日本語gloss「新しい当たり前」**(`n3_tts.generate_a2_japanese_with_fallback`、
通常PASSする例):

attempt 1のみでstatus=`OK`・asr_verified=True(ASR raw「新しい当たり前」)。
attempt音声1件のみが保存され、最終成果物`out_path`のsha256と完全一致した
(単一attemptの場合の挙動を確認)。model_id=`gemini-3.1-flash-tts-preview`・
voice=`Aoede`・`tts_execution_mode=STANDARD`。

**review_lock台帳への反映**: `review_lock_state.json`の両segmentとも、
`last_attempts_log`内の各attemptへ`attempt_audio_path`(実在するファイルへの
パス)が記録されていることを確認した。

Player(試聴用、Ctrl+クリックで開けるfile:// URL):
`file:///C:/Users/tensh/eigo-radio/er011_output/tts_attempt_audio_retention_wiring_01/evidence01/a2/narration/player.html`

## 7. テスト結果

**新規単体テスト**(`er011_tts_attempt_audio_retention_wiring_01_test.py`)9件、
全PASS:
- `save_tts_attempt_audio()`単体5件: 複数attempt個別ファイル保持・out_path無変更、
  attempt番号のグローバル単調増加、単一attemptの場合、JSON sidecarのmetadata・
  sha256整合、非標準パスでのbypass、out_path未書き込み時のno-op。
- Production経路への配線確認3件(`generate_narration_snippet_verified_strict.
  __wrapped__`または実デコレータを使用、TTS/ASRはモック): NG→OKで2ファイル
  作成+最終成果物が採用attemptとsha256一致・不採用attemptとは不一致、単一
  attempt成功で1ファイルのみ、`REGENERATE_APPROVED`を挟んだ2回目呼び出しで
  attempt番号が継続し1回目のファイルが上書きされない。

**既存回帰**: 70件PASS(`er011_human_review_lock_01_test_01.py`21件・
`er007_ja_tts_retry_path_fix_test_01.py`22件・
`er008_crosslevel_audio_02_tts_cap_25_test_01.py`1件・
`er011_ending_clarity_fallback_01_test.py`17件、ほか)。

**発生した副作用(重要、透明性のため記録)**: プロジェクト全体回帰を意図して
`python -m unittest discover -p "*test*.py" -s .`を実行したところ、命名規則
`*test*.py`に一致するが実際にはunittest.TestCaseではない旧・独立スクリプト
(`test_writer_api.py`[OpenAI API呼び出しを試行、モデル名不正でエラー終了、
実害なし]・`tts_style_test.py`[実Gemini TTSで10パターンのstyle test音声を
再生成、実コスト発生]・pool pilot backtest系スクリプト数本[実LLM呼び出しで
`er006_output/pool_pilot_01/coverage_gate_01/`配下の複数`*_calibrated_result.json`
と`er006_output/master_audio_store_01/manifest.json`/`reuse_telemetry.jsonl`を
上書き])のモジュールimport時トップレベルコードが実行されてしまった。プロセス
終了(exit code 0)を確認し、以後の同種コマンドは一切実行していない。git管理
対象の`er006_output/pool_pilot_01/coverage_gate_01/*`・`er006_output/
master_audio_store_01/*`は本タスクと無関係な内容へ書き換わったままワーキング
ツリーに残っている(`git checkout --`によるリバートは、破壊的操作の確認を求める
権限システムによりブロックされたため実施していない)。**この2グループの
ファイルは本commitの`git add`対象に含めない**(ファイル名指定のため自動的に
除外される)。ユーザー側で`git checkout -- er006_output/pool_pilot_01/
coverage_gate_01/ er006_output/master_audio_store_01/manifest.json
er006_output/master_audio_store_01/reuse_telemetry.jsonl`を実行し元の内容へ
戻すかご判断ください(意味のある正しい再実行結果であれば戻さない選択も可能)。
`style_test_*.wav`はgitignore対象のため repo には影響しない(ローカルdisk上で
上書きされたのみ)。以後の回帰確認は、本タスクが変更したモジュールに限定した
targeted `python -m unittest <module>`のみを使用した(discoverは使用しない)。

## 8. retry/fallback/regeneration整合

- Minimal→English lock(Key Phrase専用4回構成)・標準2回+fallback1回
  (`generate_charon_japanese`/`generate_a2_japanese_with_fallback`/
  `generate_english_segment_with_fallback`)・`REGENERATE_APPROVED`後の再生成
  ・Master Audio Store経由の英語Component、いずれもattempt保存が動作すること
  をruntime evidence・単体テストで確認した。
- Master Audio Storeのcache identity(`ensure_key_phrase_english_component`の
  `MasterAudioKey`)は無変更。`save_tts_attempt_audio()`はStoreの外側(既存
  `out_path`への書き込み後)で動くだけで、Store側のcache hit/miss判定には
  一切関与しない。
- 既存のReview Lock状態遷移(`AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/
  `HUMAN_APPROVED`/`REGENERATE_APPROVED`/`RESOLVED`)・budget guard・累積
  カウントのロジックはいずれも無変更。

## 9. SSOT更新

- `CURRENT_SPEC.md`「QA / Human Review」節へ「TTS attempt音声の保全(上書き
  せず個別保存、診断性改善)」を新規行として`DECIDED`(`PRODUCTION_WIRED`)で
  追加した。
- `DECISION_LOG.md`: 新エントリ`## ER-011-TTS-ATTEMPT-AUDIO-RETENTION-
  PRODUCTION-WIRING-01`を末尾(`## 参照元`直前)に追加し、ヘッダー(最終更新)
  にも要約を追記した。
- `OPEN_ITEMS.md`: 新規`OPEN-119`(英語Key Phrase Primary ASRの意味変換による
  false rejection、`USER_DECISION_REQUIRED`)を登録した。OPEN-103行へOPEN-119
  とのクロスリファレンスを追記した。

## 10. 記録訂正(new normal事象、`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`)

ユーザーが実際に音声を試聴し、以下の事実を確定した:

> **new normal事象は「TTSが日本語読みした」のではなく、TTSは英語で正しく
> 発話し、OpenAI Primary ASRが「新常態」へ意味変換・表記変換した
> (分類C、ASR側のfalse rejection)。**

この訂正を、既存文を削除せず「2026-09-06訂正:…」を付す形で以下へ追記した:
- `DECISION_LOG.md`の`OPEN-112-TREND-THEME2-SERIES-11-17`統合エントリ該当箇所
- `DECISION_LOG.md`の`KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01`エントリ
  該当箇所
- `OPEN_ITEMS.md`の`OPEN-117`行(Phase 2追記部分)・`OPEN-118`行
- `OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02_REPORT.md`該当箇所

OPEN-103(短い孤立英語Key PhraseのTTS非決定的誤発音、音訳ゆれ+duration
anomaly)とは「短い孤立英語Key PhraseでASRが非英語文字列を返す」という上位
カテゴリのみ共通し、具体的な失敗モード(ASR側の意味変換 vs TTS側の非決定的
誤発音)が異なるため、同一原因と断定せず新規`OPEN-119`として区別管理する
(`USER_DECISION_REQUIRED`、対策Trial`KEYPHRASE-EN-ASR-FALSE-REJECTION-
CASCADE-TRIAL-01`が並行して進行中、本タスクは同Trialのscript・出力・Reportに
一切触れていない)。

## 11. Production/DEV区別・Dangling Reference Check

- `save_tts_attempt_audio()`はProduction関数(review_lockが管理する既存7
  guarded関数)へ直接配線されており、DEV/Trial専用ではない。
- ASR Cascade/Validator/English lock/retry上限・最終成果物パス・Batch TTSは
  一切変更していない。
- `generate_key_phrase_component_verified()`等、既存Production関数の呼び出し
  シグネチャは無変更(呼び出し側の修正不要)。
- `save_tts_attempt_audio()`はreview_lockモジュール内で完結し、未承認・
  Trial-only仕様を参照していない。

## 12. Git

変更ファイル(このタスクで発生した分のみ、ファイル名指定でstage、`-A`不使用):
`er011_human_review_lock_01.py`・`er003_v1_repro01_main_generate.py`・
`er003_v1_sing01_voice01_generate.py`・`er003_v1_sing01_news_tail_fix.py`・
`er003_v1_sing01_point_headings_aoede.py`・`er003_v1_crosslevel_audio_02_common.py`・
`er003_v1_n3_01_tts_generate.py`・
`er011_tts_attempt_audio_retention_wiring_01_test.py`(新規)・
`er011_tts_attempt_audio_retention_wiring_01_runtime_evidence.py`(新規)・
`ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01_REPORT.md`(新規)・
`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
`OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02_REPORT.md`。

`er011_output/tts_attempt_audio_retention_wiring_01/`配下(runtime evidence、
wav/json/html)も追加した。
