## 管理ID

USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY(Discovery B1B短文化→音声完成/A2長さ問題の調査+短縮候補)
並行タスク衝突確認: 並行して Family C(er013)、Trend(`.../trend/`)、Voices(`.../voices/`)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FIX02_DISCOVERY.md`(新規)。

## 性質/到達上限Status/禁止事項

### Part 1: B1B短文化→音声完成(ユーザー指定手順)
- 対象文(B1B `discovery/b1b/article.md`): 「In a study of 2,557 college students at 12 sites in 11 countries, an everyday activity was enjoyed more than thinking for pleasure in every country tested.」→ ユーザー指定候補「**In a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed more than thinking for pleasure in every country tested.**」(後半は不変)。
- 手順: (1) Ledger(`research/verified_fact_ledger.txt`の該当fact: 2,557名/12 sites/11 countries)と意味整合を確認(「about 2,500」は丸め、「12 sites」の省略は情報の削減であり矛盾ではないことを記録)。(2) canonical article変更(B1B `b1b/article.md`と`reader_facing_article_b1b.txt`を同期、変更前を`b1b_before_fix02/`へ退避)。(3) 既存正式QA: Fact Checker A'(1回)、Ledger Deviation Checker、必要ならdiff QA(既存`apply_diff_qa_to_resolved_rewrite`相当をこの1文に対して)、Directional Precheck。FAILならSTOP(記事変更の追加は禁止)。(4) TTS再生成: 新canonical text(数字読み整形は前回CONT1の`tts_reading_transforms.json`の方針を同様に適用: about 2,500→about two thousand five hundred 等、置換一覧を更新)で`full_story_part2`を生成(lockキーは別テキストのため新規、`approve_regenerate()`禁止)。(5) 読み飛ばしが解消→Assembly→Audio Validation Gate→WAV+mp3→player(`discovery/audio/b1b/player.html`、相対パス)→article/audio consistency→`web_delivery.json`→費用更新。(6) **まだ読み飛ばす場合のみ**: 意味を変えず該当文を2文へ分割(例: 「In a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed more than thinking for pleasure. This was true in every country tested.」)→(2)(3)(4)を再実行(Fact Checker再実行込み)→(5)。それでも読み飛ばす場合はSTOP(それ以上の構造変更禁止)。(7) A2との Cross-Level Consistency注記(A2は「2,557 college students at 12 sites in 11 countries」のまま。矛盾ではなく解像度差であることを`cross_level_consistency.md`へ追記)。
- 費用上限(Part 1): ¥90(Fact Checker最大2回≈¥50+TTS+ASR)。

### Part 2: Discovery A2の長さ問題(調査中心、API最小)
- ユーザー指摘: A2記事が600語超級なのに「完成」と報告された。(1) 現A2(`discovery/a2/article.md`)の正確なword count(見出し込み/本文のみ、既存の`word_count`関数があればそれで)を算出。(2) Repoで確認: `CURRENT_SPEC.md`(Discovery Focus S2/A2のlength契約、soft target/hard capの有無)、Production Prompt(`er003_discovery_focus_staged_production_01.py`および呼び出す`build_*prompt`のlength指示)、Validator/QA(word countを見る箇所、超過時の警告・報告契約)、level contract。(3) 「なぜ600語超級が完成と報告されたか/どこでword countを見ているか/soft target超過時に警告・報告する契約があるか/既存QAが何を見ていなかったか」を根拠(ファイル・行)付きで記述。(4) 「目安を大幅超過した場合は完成報告時に必ずユーザーへ明示する」運用が既存仕様と整合するか判定(整合するなら、その根拠行。整合しない/未規定なら「未規定」と明記)。(5) 既存仕様内で自然に短縮可能か判断: 既存Discovery S2 Production経路(`run_one_pattern_staged_discovery_focus`)に既定のlength targetが存在し、同一Ledgerで再生成すれば目安内に収まる見込みがあるなら、**短縮候補を1本生成**(既存経路そのまま、同一Ledger、Stage構成無変更。費用≈¥45〜55、`discovery/a2_short_candidate/`へ出力、canonical A2は置き換えない[ユーザー判断用候補])。生成後はword count・Fact Checker等の標準QA結果を記録。新しい長さ仕様(rigid hard cap)を作る必要がある場合は生成せずSTOP(理由と選択肢)。
- 費用上限(Part 2): ¥60。合計上限¥150。
- 禁止(共通): 新Validator/新length仕様の追加/Prompt変更/Validator変更/Gate緩和/`approve_regenerate()`/Production(er003/er006/er011)コード変更/segment分割等の構造変更/`.gitignore`変更/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: Fact Checker FAILで記事の追加変更が必要/2文分割でも読み飛ばし/新length仕様が必要/費用上限超過見込み/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> Discovery B1: まずユーザー指定の短文化を試す。元「In a study of 2,557 college students at 12 sites in 11 countries...」→候補「In a study of about 2,500 college students in 11 countries...」。手順: Ledgerと意味整合確認/canonical article変更/Fact Checker/Ledger Deviation/必要diff QA/TTS再生成/Audio Validation。解消すれば完成。まだ読み飛ばす場合のみ意味を変えず2文へ分割して再度QA→TTS。それ以上の構造変更はSTOP。
> Discovery A2の長さ問題: 現記事の正確なword countを算出。CURRENT_SPEC/Production Prompt/Validator/level contract/soft target・hard capの有無を確認。なぜ600語超級が「完成」と報告されたか/どこでword countを見ているか/soft target超過時に警告・報告する契約があるか/既存QAが何を見ていなかったか。新しいrigid hard capを勝手に作らない。目安を大幅超過した場合は完成報告時に必ずユーザーへ明示する運用が既存仕様と整合するか確認。既存仕様内で自然に短縮可能なら短縮候補を作る。新しい長さ仕様が必要ならSTOP。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_UT_DISCOVERY_2.md` 全文、`er014_output/four_type_observation_01/discovery/run_discovery_audio_completion_2.py` 全文(B1B経路・読み整形・Assembly以降を再利用して`run_discovery_audio_completion_3.py`を派生)。
2. `er014_output/four_type_observation_01/discovery/b1b/article.md`: Grep `2,557|12 sites|11 countries` → 該当行。`research/verified_fact_ledger.txt`: Grep `2,557|2557|11 countries|12 sites` → 該当fact。
3. `er014_output/four_type_observation_01/discovery/run_discovery_complete_2.py`: Grep `^def |fact_checker|ledger_deviation|diff_qa|directional` → 正式QA呼び出し関数(再利用)。
4. `er014_output/four_type_observation_01/discovery/a2/article.md` 全文(word count算出・短縮判断)。
5. `CURRENT_SPEC.md`: Grep `Discovery Focus S2|A2.*語|word|words|語数|soft target|hard cap|length|Length` → A2/Discoveryのlength契約該当行のみ。
6. `er003_discovery_focus_staged_production_01.py`: Grep `word|words|length|Length|語|target|def run_one_pattern_staged_discovery_focus|STAGE` → length指示・入口のみ。呼び出し先prompt builder(Grep結果から特定)の該当length行。
7. `er003_v1_n3_01_articles_generate.py`: Grep `word_count|WORD|length_ok|too_long|soft|hard_cap` → word countを見る箇所のみ。
8. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Part 1出力: `discovery/b1b_before_fix02/`、`b1b/article.md`+`reader_facing_article_b1b.txt`(更新)、`b1b/audit/fix02_*.json`(QA結果)、`rewrite_log.md`(追記: 旧→新、根拠)、`audio/tts_reading_transforms.json`(更新)、`audio/b1b/{narration/full_story_part2.wav, assembled/, audio_validation.json, player.html, web/episode.mp3, web/segments/*.mp3, article_audio_consistency.json}`、`audio/web_delivery.json`(B1B追記)、`cross_level_consistency.md`(追記)、driver `run_discovery_audio_completion_3.py`。
- Part 2出力: `discovery/a2_length_investigation.md`(word count・仕様根拠・原因・整合判定)、必要時`discovery/a2_short_candidate/`(記事・QA結果・word count)。
- `discovery/production_set_cost.json`(Discovery総原価=¥565.10+本タスク実費、Part 1/2内訳、短縮候補分は「候補生成費」として別記)、`progress_log.md`1行。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY_check.json`
2. Part 1: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_audio_completion_3.py --level b1b --sentence-fix`(budget_jpy=90。全文コマンド記録)
3. Part 2: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\investigate_a2_length.py`(word count+根拠収集、API不使用)→ 短縮候補生成時のみ `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_a2_short_candidate.py`(budget_jpy=60)
4. 確認: `Select-String -Path er014_output\four_type_observation_01\discovery\audio\b1b\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er014_output/four_type_observation_01/discovery/audio/b1b/web/episode.mp3`(exit 1)
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(B1B短文化・音声完成/A2長さ調査結果)、OPEN-153追記案(2文分割が必要だったか、読み飛ばし再発有無)、必要ならOpen Item案「A2 length契約の報告義務」を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FIX02_DISCOVERY.md`に: Part 1: 1) 最終Status(B1B)、2) 文の修正前後・Ledger整合根拠、3) QA結果(Fact Checker verdict・Ledger Deviation・diff QA・Directional)、4) TTS(読み飛ばし解消有無、2文分割の要否、attempt数)、5) Audio Validation、6) duration、7) mp3・player・予定URL(`https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/b1b/player.html`)・gitignore、8) Cross-Level注記。Part 2: 9) A2 word count(見出し込み/本文)、10) 仕様根拠(CURRENT_SPEC行・Prompt行・Validator行)、11) なぜ完成と報告できたか(原因・gap)、12) 「大幅超過時にユーザーへ明示」運用の既存仕様との整合判定、13) 短縮候補(生成有無、word count、QA結果、パス)またはSTOP理由。共通: 14) 費用(Part 1/2実費、**Discovery総原価=¥565.10+実費=¥xx.xx**、候補生成費別記)、15) model_id、16) Open Item候補、17) commit対象候補一覧、18) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥90+¥60)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
