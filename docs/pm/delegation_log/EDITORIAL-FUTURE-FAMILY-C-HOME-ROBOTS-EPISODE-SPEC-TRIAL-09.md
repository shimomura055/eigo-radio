## 管理ID

EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09
並行タスク衝突確認: 並行してEDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01(er012_*・`er014_output/.../voices/`・SSOT・Git担当)が走る。本タスクは**新規ファイルは`er013_*`とer013_output/のみ**に作り、既存Production部品(er003_*/er006_*/er008_*/er010_*/er012_*等)は**呼び出して再利用するだけで編集しない**。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)を一切行わない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FC9.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(完成episode仕様の設計+試作)。**最大Status: VALIDATED**(Production採用・配線禁止)。終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。
- 目的(ユーザー): Family C Futureをユーザー検証へ早く進めるため、Trial-08採用のHome robots記事(「便利さが少しずつ人間から好みそのものを奪う」、`er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt`)を代表題材とし、**記事本文以外に必要なFamily C完成episode仕様をまとめて設計・試作**する。ユーザー検証候補はHome robots/The future of memory/Digital twins of ourselvesの3本だが、今回はHome robots 1本を完成候補まで通す。Trial-08自由生成方式のProduction正式採用とはまだ扱わない。
- 基本方針: 仕様を増やしすぎない。既知の弱点(「未来記事というより未来を題材にした小説」「展開のパターン化」)は認識したまま、**今回は改善Trialを繰り返さない**。記事Writer・Core Provocation・Story構造の改善は禁止。
- **記事本文は固定**: 許されるのは意味を変えない完成episode化処理のみ(音声化用format normalization、UI表示文の読み上げ処理、segment分割)。Core Provocation・人物・結末は変更しない。
- 既存仕様の再発明禁止: A-Family/B-FamilyでPRODUCTION_WIRED済みの仕組み(Preview/Key Phrase/日本語gloss/Comment・support/Title読み上げ/TTS/Voice/segment構造/Assembly/Audio Validation Gate/player/A2・B1差分/slowdown/retry・fallback/Human Review/cost logging)を先に確認し、Family Cでそのまま再利用できるものを特定する。「Family Cだから新しい仕組みが必要」と最初から仮定しない。新規Family C専用部品が必要な場合はTrial専用で最小実装(Production配線しない)。
- episode構造: A-FamilyのMain Story/Point One/Point Two/In One Lineを機械的に持ち込まない。記事本文はひと続きのStoryとして扱う(音声segmentに分けてよいが、リスナーに「Point One/Point Two」のような分析構造を聞かせない)。既存部品を最大限再利用した**最小episode構造を1案に絞って提示**(複数案を大量に出さない)。
- Preview: 必要か確認し、必要なら最小仕様。オチ・中心の問いを先に説明しすぎない。「この先を聞きたい」と思わせる短い導入。既存Preview Production仕様を流用できるなら流用。
- Key Phrase: 既存A/B Familyの正式Key Phrase仕様をできるだけ再利用(個数/選定基準/英語phrase/日本語gloss/表示位置/音声位置/本文との一致/No Jargon/redundancy/TTS)。特殊な体系を新設しない。Home robotsで**実際に生成**して完成候補を提示。
- 日本語support/Comment: 小説的な記事の余韻を解説で壊さない。Fact解説・現在技術解説・Current Fact・研究統計を後から付け足さない。既存Comment 1〜4をそのまま全部流用する必要はなく、ユーザー検証用に最低限必要なsupportだけ残す。**具体的なsupport textまで生成**する。
- Voice/TTS: 登場=narrator/Maya/her mother/robot。過剰なmulti-voice化をしない。候補(全文single narrator/narrator+dialogueのみ声変更/narrator+Maya・mother・robot分離)を「誰が話しているか分かる/小説として自然/リスニングで混乱しない/制作コストが大きく増えない/量産できる」で比較し、**最小かつ聞きやすい1方式を推奨・試作**。新しいVoice資産を無制限に増やさない(既存TTS Voiceを再利用)。
- UI表示文(例「CARE HOUSE: more sleep for Maya. / HOME: more time with her mother.」)の音声化: narratorが普通に読む/system・robot voiceとして読む/一部を音声では省く、を比較しHome robotsでは1方式に決めて試作。意味が失われる省略は禁止。新しいUI-reading validatorは作らない。
- 人物名ルール(暫定案の妥当性確認のみ、Validator新設なし): 主人公は固有名可/その他の人間は関係性表現/AI・robotは理解に有益なら固有名可/不要な固有名を増やさない。
- A2/B1: Home robots Trial-08記事が現在どのlevel契約で生成されたかをRepoの事実(`er013_family_c_future_writer_08.py`/trial_08_run.py/word_count.json)で確認し、ユーザー検証に必要なlevel構成をQCD込みで提示(Family Cも最終的にA2/B1の2レベルを持つべきか/まず1レベルで検証するか)。**勝手にA2/B1両方を新規生成しない**。これはUSER_DECISION_REQUIREDにしてよい。
- Fact Safety: Reader-facing本文CURRENT FACT=0件を維持、Current Factを追加しない。CURRENT FACT 0件時に本当に必要なFact Safety(不要なCheckerを形式的に回していないか)を整理してよいが、Production変更はしない(Open Item/Production採用候補として提示)。
- 完成episode試作: Home robotsについて可能な範囲で article/Preview/Key Phrase/日本語support/segment設計/Voice・TTS方式/Audio/Assembly/player まで作成。**ユーザーが実際に聞いて評価できる完成候補**を作る。既存Production部品(TTS生成・Assembly・Audio Validation Gate・標準player)は実際に使用。
- 費用: Family C残額**¥133.99**(ハード上限)。TTSは開発・Trial向けのStandard同期(PM_GOVERNANCE 7-4)。想定: Key Phrase/Preview/support生成≈¥5〜15、TTS+Assembly+Audio Gate≈¥20〜60。超過見込みで停止し報告。**開発・Trial費**と**将来のProduction 1生成セット総原価(推定)**を分離(PM_GOVERNANCE 15-8標準、「1記事単価」と「episode全体原価」を混同しない)。
- 禁止: 記事本文の再生成/Writer・Provocation・Story改善/新Validator/Production配線・既存Production部品の編集/SSOT・Git/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/`er014_output/`の変更。
- STOP条件: 費用上限/既存Production部品の再利用にコード修正(編集)が必要と判明(修正せず、Trial専用ラッパで回避できない場合は報告)/Audio Validation Gateで解消不能なブロック。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 目的: Family C Futureについて、ユーザー検証へ早く進むため、Trial-08で採用された Home robots記事を代表題材として、記事本文以外に必要なFamily C完成episode仕様をまとめて設計・試作する。
> 基本方針: Family Cは仕様を増やしすぎないこと。ユーザーから既に以下の弱点が指摘されている(「Future記事」というより、未来を題材にした小説になっている/小説の展開に一定のパターンが見える)。これらは認識したまま、今回は改善Trialを繰り返さない。ユーザー検証を優先して、完成episodeとして成立させるために必要な最低限の仕様を決める。新しい記事Writer改善・Core Provocation改善・Story構造改善は今回しない。
> 1. まずRepo上の既存仕様を確認。A-Family / B-Familyで既にProduction Wiredされている仕組みを確認し、Family Cでそのまま再利用できるものを特定すること。既存仕様を再発明しない。
> 2. Home robots記事本文は固定。3. Family Cのepisode構造を決める(最小episode構造を1案に絞って提示)。4. Preview仕様。5. Key Phrase仕様(Home robotsで実際に生成して、完成候補を提示)。6. 日本語support / Comment仕様(具体的なsupport textまで生成)。7. Voice / TTS仕様(最小かつ聞きやすい方式を1つ推奨・試作)。8. UI表示文の読み上げ仕様(1方式に決めて試作)。9. 人物名ルール。10. A2 / B1の扱い(USER_DECISION_REQUIREDにしてよい)。11. Fact Safety。12. 完成episode試作(article/Preview/Key Phrase/日本語support/segment設計/Voice・TTS方式/Audio/Assembly/player)。13. コスト(開発・Trial費/将来のProduction 1生成セット総原価)。14. 最終REPORT。
> 最重要: 今回はFamily Cの記事生成をまた改善し始めるタスクではない。「Home robotsの記事は一旦これでよい」として、ユーザー検証できる完成episodeへ持っていくための残り仕様を決める。仕様を増やしすぎず、既存資産を最大限流用し、できるだけ早く聞ける状態にすること。狙いは、Home robotsを1本完成形まで通して「実際にeigo-radioとして聞いたときにどうか」を確認すること。

## 事前指定Read一覧

1. `er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt` 全文(固定本文)と同dirの`word_count.json`・`core_idea.json`。
2. `CURRENT_SPEC.md`: Grep `Preview|Key Phrase|日本語gloss|Comment|Title読み上げ|TTS|Voice|segment|Assembly|Audio Validation|player|slowdown|Human Review|cost logging|A2|B1B` → **各仕組みのProduction仕様の定義範囲のみ**Read(全文禁止。1仕組みあたり該当節の先頭〜表末尾程度)。特にA2 Production経路(`FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01`関連、L763-764付近)とB-Family A2経路(L637-658)。
3. `er003_v1_n3_01_tts_generate.py`: Grep `^def |JAPANESE_TITLES|VOICE|voice` → 関数一覧・Voice定数・A2 segment生成入口のみ。
4. `er003_v1_n3_01_scaffold_generate.py`: Grep `^def |key_phrase|preview|comment` → Key Phrase/Preview/Comment生成関数の入口のみ。
5. Assembly/Audio Validation Gate/player: Grep `^def ` を `er003_*assembl*.py`・`er006_*audio*validation*.py`・`er003_*player*.py`(Globで実ファイル名を特定)→ 入口のみ。
6. `FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`: Grep `^## |^### ` → theme→artifact連続性の手順節のみRead(A2 end-to-endの実行手順の先例)。
7. `er013_family_c_future_writer_08.py`: Grep `level|A2|B1|WORD_COUNT` → level契約の該当範囲のみ。
8. `docs/pm/PM_GOVERNANCE.md`: Grep `7-4|15-8|9-5` → TTS方式・コスト報告・試聴リンク要件の範囲のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 設計文書(先に作る、¥0): `er013_family_c_episode_spec_09.md`(新規root直下ではなく`er013_output/family_c_episode_trial_09/spec/episode_spec.md`)に、既存部品の再利用表(仕組み/Production実装/再利用可否/Family Cでの扱い)、最小episode構造1案(segment一覧: 順序・内容・voice・出典部品)、Preview/Key Phrase/support/Voice・TTS/UI表示文読み上げ/人物名ルール/A2・B1提案(QCD表)/Fact Safety構成、を記載。
- 試作: `er013_family_c_episode_trial_09_run.py`(新規。固定本文の読み込み→format normalization(意味不変)→Preview生成(既存仕様流用)→Key Phrase生成(既存正式関数)→日本語support生成→segment分割→TTS(既存関数・既存Voice)→Assembly→Audio Validation Gate→標準player生成。費用上限¥133.99ガード、目安¥80で警告)。出力`er013_output/family_c_episode_trial_09/home_robots/`(`article_normalized.txt`、`preview.txt`、`key_phrases.json`、`support_ja.md`、`segments.json`、`audio/`、`assembled/`、`player.html`、`audio_validation.json`、`cost_summary.json`、`raw_usage_log.jsonl`)。既存部品が特定ディレクトリ構造を要求する場合はそれに合わせ、完了後に上記dirへコピー(元は残す)。
- 決定的テスト(API不要): `er013_family_c_episode_trial_09_test_01.py`(normalizationが本文の語・順序を変えないこと、UI表示文の変換規則、segment分割の再結合が本文と一致すること)。
- `docs/pm/RESULT_PACKET_FC9.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09.md --json-out docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_check.json`
2. offline検証(生成前): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待: 既存121+新規全PASS)
3. 試作: `.venv\Scripts\python.exe er013_family_c_episode_trial_09_run.py --theme home_robots --budget-jpy 133.99`(CLIフラグ・ガードは本タスクで実装。段階ごとに費用チェックし、次段階の見込み費用を含めて上限判定する)
4. 費用確認: `cost_summary.json`合計が上限内であること。
(既存Production部品の回帰は不要: 編集していないため。)

## SSOT追記文

本タスクではSSOTを編集しない。root REPORT `EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_REPORT.md`末尾に「SSOT追記文案(編集は行っていない)」節として、OPEN-147末尾追記案(ユーザー検証候補3本の記録、Trial-09結果・分類・費用・残額、Open Item候補[A' skipのProduction採用候補、UI表示文読み上げ、人物名ルール等])とDECISION_LOG新エントリ案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない(Fableが後続CONSOLIDATIONで明示addし、playerと音声をGitHub経由で公開する)。RESULT_PACKETに「commit対象候補ファイル一覧(音声ファイルのサイズ込み)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FC9.md`に、ユーザー必須項目を同じ順で: 1) 採用した完成episode構造(segment一覧)/2) 既存A/B仕様から再利用したもの/3) Family C専用で新規に必要だったもの(Trial専用実装)/4) Preview完成文/5) Key Phrase完成候補(英/日本語gloss/位置)/6) 日本語support完成文/7) Voice・TTS方式(比較表+採用理由)/8) UI表示文の読み上げ方法(比較+採用)/9) segment一覧/10) player・audioの相対パス(rootからの相対。commit後にFableがGitHub URLを付ける)/11) A2・B1提案(現在の契約の事実+QCD表、USER_DECISION_REQUIRED可)/12) Fact Safety構成(0件時に必要なもの・不要なCheckerの整理、Production変更なし)/13) 開発・Trial費(API別+5区分、TTS分離)/14) 将来のProduction 1生成セット総原価(推定、内訳、未確定要素明記)/15) 残る問題/16) Gate 1判定材料/17) USER_DECISION_REQUIRED一覧/18) Status・Gate(分類)。加えて: Audio Validation Gate結果、retry/fallback発生有無、commit対象候補一覧(サイズ)、T-0結果、事前指定外Read(理由付き)、STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(spec/run/test/出力dir)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥133.99ハード上限)
- [x] 並行タスク衝突回避あり(er013限定・既存部品無編集・Git操作なし)
