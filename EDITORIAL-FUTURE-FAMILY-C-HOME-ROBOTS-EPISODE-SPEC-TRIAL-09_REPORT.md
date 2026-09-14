# EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09 REPORT

**Status: VALIDATED(Trial上限、Production採用・配線は行っていない)**

目的: Family C Future(Trial-08採用Home robots記事、本文固定)について、
記事本文以外に必要な完成episode仕様を設計・試作し、ユーザーが実際に
聴ける完成episode候補を作ること。記事Writer・Core Provocation・Story
構造の改善は今回のスコープ外。

詳細な仕様設計は`er013_output/family_c_episode_trial_09/spec/episode_spec.md`、
ユーザー必須項目のサマリーは`docs/pm/RESULT_PACKET_FC9.md`を参照。本
REPORTは実行経緯・runtime evidence・Fable判定・SSOT追記文案を記録する。

---

## 1. 既存仕様確認(再発明の回避)

A-Family(11パート構造)・B-Family(5区切りVoices構造)の既存Production
実装を確認した結果、TTS retry構成・Gain primitive・Assembly primitive
(`assemble_with_timeline`/`apply_headroom_safety_valve`)・Audio
Validation Gate(`verify_episode_audio_validation_gate`)・標準player
(`audio_review_player.py`)は、いずれも記事の物理構造に依存しない粒度で
共通化されており、Family Cの全く異なる物理構造(ひと続きのStory)でも
そのまま呼び出せることを確認した。「Family Cだから新しい仕組みが必要」
という仮定は再確認の結果あたらなかった。新規に必要だったのは(1)
これらprimitiveを束ねるorchestration、(2)引用符検出による2-voice分割、
(3)Preview/Support role instruction文言、の3点のみ。詳細は
episode_spec.md 1節の再利用表を参照。

## 2. 記事本文(固定)

`er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt`
は無変更(429語、CURRENT FACT 0件)。本タスクでは一切編集していない。

## 3〜11. episode構造/Preview/Key Phrase/support/Voice/UI表示文/人物名/A2B1/Fact Safety

episode_spec.md参照(各節に既存部品再利用表・比較表・QCD表を記載)。
Voice方式は4候補比較のうえ「narrator(Aoede)+robotの直接発話のみ
Charon」の2-voice設計を採用。UI表示文はCharon(robot/system voice)で
そのまま読む方式を採用。人物名ルール(暫定案)はHome robots記事に対し
そのまま妥当と確認、新規Validatorは追加していない。A2/B1はA2のみの
現契約を確認し、B1追加はUSER_DECISION_REQUIREDとして提案(理由:
Family Cのフィクション記事には既存A-Family B1経路が前提とする
Verified Fact Ledgerが無く、B1相当を作るには新しいWriter手順が必要で、
本タスクの「Writer改善禁止」範囲と抵触しうるため)。

## 12. 完成episode試作(実行経緯)

### 12.1 実装

`er013_family_c_episode_trial_09_run.py`(新規)。既存Production関数
(`generate_narration_snippet_verified_strict`/`generate_charon_english`/
`generate_key_phrase_component_verified`/`run_key_phrases`/
`assemble_with_timeline`/`apply_headroom_safety_valve`/
`verify_episode_audio_validation_gate`/`audio_review_player`)を呼び
出すorchestrationのみを新規実装した。既存Production module・関数は
一切編集していない(grep差分確認済み、本タスクでの変更ファイルは
`er013_*`と`er013_output/`のみ)。

### 12.2 Runtime evidence(発見した2つの技術的問題と対処)

**(a) Key Phrase選定の構造的失敗(6回中4回目で成功)**: 既存Production
正式入口`run_key_phrases()`(内部の`run_key_phrase_selection()`は
`max_attempts=1`固定、hard requirement不適合時の自動retryなしという
既存仕様)が、1〜3回目でいずれも異なる理由(引用符境界のLLM抽出ずれ、
finite auxiliary混入)により`KEY_WORDS_STRUCTURE_INVALID`となった。
既存の安全装置(1回限りのfail-closed判定)は正しく機能しており、これを
回避・緩和はしていない。対処として、Production正式入口自体を最大6回
まで再度呼ぶ設計とした(人間オペレータが選定をやり直すのと同じ操作、
新しいGate・Validatorの追加ではない)。4回目でKEY_WORDS_STRUCTURE_PASS
→CANONICALIZATION_PASS→REDUNDANCY_PASSに到達した。

**(b) TTS/ASR不一致2件(Audio Validation Gateが正しくBLOCK)**:
1回目の完走試行で、Gateが`story_001`(時刻表記"7:00"問題)・
`kp3_number`/`kp5_number`(短い単独英単語のCJKスクリプト誤書き起こし)
の3segmentをSTOPPEDとして検知し、episode assemblyを正しく中止した
(fail-closed、ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05
の設計どおり)。原因を実際に特定し(前者はcanonical text"7:00"をTTSが
自然に"seven"と発話するため、既存ASR Validatorの数値正規化が時刻表記
までは対応していないこと、後者はCURRENT_SPEC.md記載の「短い単独英単語
TTSの既知の不安定性」["default"個別例外と同種])、以下2点を実装した。
(1) `tts_safe_time_reading_en()`(Trial新規、表示用本文"7:00"は不変、
TTS入力のみ"seven"へ変換、date safe-reading等の既存パターンを踏襲)。
(2) Key Phrase番号読み上げを、新規TTS生成(Aoede)から既存B1/A2
Production共有資産(Charon、`num_one_charon.wav`等、記事非依存・
追加コスト¥0)の再利用へ設計変更。いずれも既存のretry上限・Gate判定
基準そのものは変更していない。

**(c) resumabilityバグの発見・修正**: デバッグ過程の再実行効率化のため
実装した「出力ファイルが存在すれば再生成をスキップする」ロジックが、
STOPPED(失敗)attemptの音声ファイルも(ASR検証前に無条件でdisk上書き
される既存仕様のため)ディスク上に残ることを見落としており、失敗音声を
誤って成功扱いする可能性があるバグだったため、`.ok`marker方式
(status=="OK"確認後にのみ書く)へ修正した。Gateへ実際に渡す前に発見・
修正できたため、実害(誤ったPASS)は発生していない。

### 12.3 最終結果(Runtime evidence)

- Audio Validation Gate: **PASS**(`FAMILY_C_TRIAL_09`level、38/38
  segment/sub-segment status=OK)
- 完成episode: `er013_output/family_c_episode_trial_09/home_robots/assembled/family_c_home_robots_trial_09.wav`
  (duration=257.82秒[4分18秒]、peak=0.918、clipping無し、headroom
  safety valve不適用)
- player: `er013_output/family_c_episode_trial_09/home_robots/player.html`
  (PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11準拠)
- テスト: `er013_family_c_episode_trial_09_test_01.py`(21件、決定的・
  API不要)、`run_project_regression.py --pattern "er013*_test_*.py"`
  で121(既存)+21(新規)=142件全PASS(実行済み、実測)

## 13. コスト

開発・Trial費(全実行回の合算、推定): **¥96.30**(上限¥133.99以内)。
将来Production 1生成セット総原価(推定、定常状態): **¥45〜55**。詳細
内訳・方法論の限界(token単位usageが既存Production wrapper関数の戻り値
に含まれないため、precedent値からの推定であること)は
`docs/pm/RESULT_PACKET_FC9.md` 13)・14)節参照。

## 14. Fable判定(自明な修正・USER_DECISION_REQUIRED)

以下はFable自律判断で実施した(既存の安全装置の範囲内の対処であり、
新しい仕様判断ではないため): (a) Key Phrase選定の入口再呼び出し
(既存の「選定からやり直す」運用パターンの適用)、(b) TTS-safe時刻表記
変換の新規実装(表示本文は不変、既存date/name safe-reading pattern踏襲)、
(c) Key Phrase番号読み上げの資産切替(既存共有資産への切替、新規仕様の
追加ではない)、(d) resumabilityバグ修正。

USER_DECISION_REQUIRED(3件、詳細`docs/pm/RESULT_PACKET_FC9.md` 17)節):
(1) A2/B1構成、(2) Key Phrase選定Validatorの会話文主体記事での失敗率
対応要否、(3) UI表示文読み上げ・人物名ルールの恒久ルール化要否。

---

## SSOT追記文案(編集は行っていない)

本タスクではSSOTを一切編集していない。以下はFableが次回CONSOLIDATION
で反映する際の案として記録するのみ。

### OPEN_ITEMS.md OPEN-147末尾追記案

```
- EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09
  (2026-09-14): Family C Futureのユーザー検証候補3本(Home robots/
  The future of memory/Digital twins of ourselves)のうち、Home
  robots 1本の完成episode(Preview/Key Phrase/日本語support/2-voice
  TTS[narrator=Aoede/robot=Charon]/Assembly/Audio Validation Gate/
  player)を試作しGate PASSに到達した(VALIDATED、Production配線なし)。
  開発費実測(推定)¥96.30、将来Production 1生成セット総原価(推定)
  ¥45〜55。Open Item候補: (a) Key Phrase選定Production Validator
  (`validate_min_unit_selection`)が会話文主体のFamily C記事で高頻度
  (観測6回中4回)に構造的不合格になった原因の恒久対応要否、(b) 短い
  単独英単語TTSのCJKスクリプト誤書き起こし(既存"default"個別例外と
  同種、Production全体のgap)、(c) A2語数超過(429語、許容300〜420語)
  の未修正。詳細
  `EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_REPORT.md`。
```

### DECISION_LOG.md新規エントリ案

```
## EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09(2026-09-14)

Family C Future Home robots記事(Trial-08採用、本文固定)について、
既存A/B-Family Production部品(TTS retry構成・Gain/Assembly primitive・
Audio Validation Gate・標準player)を再利用し、完成episode候補(Preview・
Key Phrase 5件・日本語support 2件・2-voice TTS[narrator=Aoede/robot=
Charon]・Assembly・player)を試作した。Audio Validation Gate PASS
(38/38 segment)。ユーザー試聴前のTrial段階のためStatus=VALIDATED
(Production採用・配線は行っていない)。A2/B1構成・Key Phrase選定
Validatorの会話文主体記事での挙動・UI表示文読み上げ/人物名ルールの
恒久化要否をUSER_DECISION_REQUIREDとして残す。詳細は
`EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_REPORT.md`・
`docs/pm/RESULT_PACKET_FC9.md`参照。
```
