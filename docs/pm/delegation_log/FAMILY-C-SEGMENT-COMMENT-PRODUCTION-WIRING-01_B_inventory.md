## 管理ID

`FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`(委任B: ユーザー実検証用記事一覧のRepo再監査、read-only)
並行タスク: 委任A(Family C Production wiring)が同時実行中で、`er013_family_c_production_*.py`・`er013_output/family_c_production/`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・`docs/pm/ACTIVE_TASK.md`を編集しGit操作を行う。**本委任Bは完全read-onlyとし、新規作成するのは`docs/pm/RESULT_PACKET_UT_INVENTORY.md`と`USER-TEST-INVENTORY-01_REPORT.md`(root直下)の2ファイルのみ。Git操作(add/commit/push)・SSOT編集・`ACTIVE_TASK.md`編集・記事修正・音声再生成・API呼び出しを一切行わない。**

## 性質/到達上限Status/禁止事項

- 性質: 「現在ユーザー実検証に回すべき完成記事・音声を、漏れなく・重複なく・正しい最新版player URL付きで確定する」ためのread-only Repo監査。
- 到達上限: 監査報告のみ。各episodeを`USER_LISTENING_DONE`/`USER_LISTENING_REQUIRED`/`NOT_READY`に分類。未完成記事を見つけても修正・再生成を開始しない(残課題を1行で特定するところまで。修正が必要なものは`USER_DECISION_REQUIRED`として列挙)。
- 禁止: 記事修正、音声再生成、API呼び出し(Web到達確認のHTTP GETのみ可)、Git操作、SSOT編集、Opus使用、古いTrial成果物の再検証に時間をかけすぎること、`ARTIFACT_REGISTRY.md`のみへの依存、推測で○を付けること(A2が存在しないテーマを推測で○にしない。完成A2があれば必ず拾う)。
- STOP条件: ユーザー実検証記事の最新版を複数候補から一意に確定できない場合は、そのテーマを`NOT_READY(候補複数: …)`として候補と根拠を列挙し、他テーマの監査は続行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_B_inventory.md`。delegation_logへの保存は本委任で唯一許可される`docs/pm/`配下の追加書き込み。)

## ユーザー指示(原文)

ユーザー原文(2026-09-16)の本委任該当部分を引用:

---
10. ユーザー実検証用記事一覧のRepo再監査: 目的は、「現在ユーザー実検証に回すべき完成記事・音声を、漏れなく・重複なく・正しい最新版player URL付きで確定する」こと。以下の表を出発点とするが、内容を鵜呑みにせずRepoで事実確認すること。

対象表:
| Family | テーマ / 記事 | A2 | B1 | 現在の認識 |
| A / News | AI regulation / AI race — The AI Race Meets the Rulebook / Two Clocks, One AI Race | ○ | ○ | 記事セットあり |
| A / Trend | Smartphone / ambient AI — The Smartphone Screen Is Still Here. It Is Just Sharing the Work 系 | △ | ○ | B1完成、A2要確認 |
| A / Trend | Young travelers / slow travel | ○ | ○ | A2/B1完成候補 |
| A / Discovery | Silence — Why Can Silence Feel Uncomfortable? 系 | ○ | △ | 最新完成状態を再確認 |
| A / Discovery | Towels — Why a Clean Towel Can Still Smell | ○ | ○ | A2/B1+playerあり |
| A / Discovery | Wake Before Alarm | ○ | ○ | A2/B1成果物あり |
| A / Discovery / Household | Refrigerator / crisper — The Small Refrigerator Slider with a Big Job 系 | ○ | ○ | 一本化最終候補 |
| B / Voices 2V | Free-address / assigned desk — One Office, Two Ideas of a Place to Work | ○ | ○ | A2/B1完成候補 |
| B / Voices 2V | Personalized news — Is personalized news good for us? / When Personalized News Feels Helpful — and Narrow 系 | — | ○ | B1 USER TEST READY |
| B / Voices 3V | AI hiring — When AI Sits Between a Job and a Person | — | ○ | 完成episode、試聴済み |
| C / Future | Home Robots | ○ | ○ | 最新完成版あり |
| C / Future | The Future of Memory | ○ | ○ | Trial-11/12最新完成版 |
| C / Future | Digital Twins | ○ | ○ | Trial-12最新完成版 |

11. 表から完全削除するもの: 削除1 CAR-T / immune reset(仕様Trial用記事、ユーザー検証対象外)。削除2 Home Robots / Memory / Digital Twinsの元記事群(最新完成版と重複する旧artifact群、別記事として数えない、fallback / Trial旧版も一覧へ出さない)。

12. Repo監査で確認すること: 各テーマについて: 1. A2本文の有無 2. B1 / B1B本文の有無 3. 完成episode audioの有無 4. Audio Validation結果 5. playerの有無 6. どのplayerが現在の最新版・正式な実検証候補か 7. ユーザーが既に試聴済みか 8. ユーザー試聴がまだなら、その旨 9. 旧Trial / superseded版ではないか 10. 同一テーマの別Trialを別記事として重複カウントしていないか。ARTIFACT_REGISTRY.mdだけに依存せず、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/最新Report/output directory/player/audio validation evidenceを突き合わせる。

13. 特に再確認する項目: A. Smartphone / ambient AI: 最新A2が本当に未完成なのか。Human Review Lock後に後続タスクで完成していないかを確認。完成版があれば表を○へ修正し、player URLを出す。未完成なら具体的な残課題を1行で示す。B. Silence: B1が一時停止後に修正・完成している可能性があるため、最新成果物まで追う。A2/B1双方について最新版player URLを確定する。C. Wake Before Alarm: 「記事・音声系成果物あり」だけでなく、本当にユーザー実検証へそのまま回せる完成episode/playerかを確認。D. Voices: Free-address 2V/Personalized news 2V/AI hiring 3Vをテーマ単位で整理する。同一AI hiringテーマのTrial違いは1記事として扱う。A2が存在しないテーマを推測で○にしない。逆に完成A2がある場合は必ず拾う。E. Family C: 今回ユーザーが試聴OKした最新版を採用。Home Robots A2/B1、Memory A2/B1、Digital Twins A2/B1。旧Trial playerは出さず、現在の最新版のみ。

14. 「未試聴」と「完成済み」を分ける: 各行を`USER_LISTENING_DONE`(ユーザーが最新版を実際に試聴しOKした記録がある)/`USER_LISTENING_REQUIRED`(完成版・Validation PASS・playerありだが、最新版についてユーザー試聴記録がない→必ずplayer URLを貼る)/`NOT_READY`(ユーザー実検証にまだ回せない→playerが古い・不完全なら貼らない→残作業を1行で説明)に分類する。

15. 完成品もリンクを再掲: USER_LISTENING_DONEであっても、現在の正式完成player URLを全件再掲する。最終表に、Family/Theme/A2/B1/Voice structure(Voicesのみ2V/3V)/Status/最新player URL A2/最新player URL B1/ユーザー試聴済みか/備考を入れる。リンクがA2/B1共通playerの場合はその旨明記。

16. 最終的なテーマ数も報告: 旧Trial派生を除き、ユーザー実検証用として独立テーマが何テーマあるかを数える。加えて、USER_LISTENING_DONE: 何テーマ / 何episode、USER_LISTENING_REQUIRED: 何テーマ / 何episode、NOT_READY: 何テーマ / 何episodeを集計する。

17. 勝手に追加修正しない: 今回のRepo監査中に未完成記事を発見しても、ユーザー承認なしに記事修正・音声再生成を開始しない。特に、Smartphone A2/Silence/その他未完成episodeについて、残課題を特定するところまで。修正が必要ならUSER_DECISION_REQUIREDとしてSTOPして報告。

18-B〜E 報告フォーマット: B. ユーザー実検証用記事 — 最終一覧(最新版だけをテーマ単位で表。各完成品についてクリック可能なplayer URLを必ず記載)。C. 未試聴一覧(USER_LISTENING_REQUIREDのepisodeだけ: テーマ/Level/player URL)。D. 未完成一覧(NOT_READYだけ列挙、勝手に修正しない)。E. 集計(独立テーマ総数/完成episode総数/試聴済みepisode数/未試聴完成episode数/未完成episode数)。

QCD注意: Repo監査はread-only中心/古いTrial成果物の再検証に時間をかけすぎない/最新Report / SSOT / player / audio validationを優先/Opus不要。
---

Fable補足(既知の事実、監査で再確認すること): Family Cの最新版=Home robots A2 `er013_output/family_c_episode_trial_09/home_robots_v2/`(VALIDATED、試聴OK)・Home robots B1 `.../home_robots_b1/`(VALIDATED、試聴OK)・Memory A2 `er013_output/family_c_episode_trial_11/memory_a2/`(VALIDATED、試聴OK)・Memory B1 `er013_output/family_c_episode_trial_12/memory_b1/`(試聴OK、2026-09-16)・Twins A2 `er013_output/family_c_episode_trial_12/twins_a2/`(試聴OK)・Twins B1 `er013_output/family_c_episode_trial_12/twins_b1/`(試聴OK)。Trial-10 memory/twins・home_robots(v1)は旧版。Discovery(er014 four_type_observation_01 discovery)はB1標準player未生成・A2は旧604語版playerのみで530語版未公開=NOT_READY(残課題: B1 part2bの表記差[enダッシュ]Gate不合格/A2 full_story_part1・point_twoのTTS不一致、ユーザー判断待ち)。これらはSSOT/成果物で再確認のうえ記載。

## 事前指定Read一覧

- `ARTIFACT_REGISTRY.md`: Grepで`player|episode|USER TEST|VALIDATED|試聴`→該当行(出発点として使うが鵜呑みにしない)
- `OPEN_ITEMS.md`: Bash(python)で各行の先頭300字+`Status`語を抽出し、テーマ名(News/AI race・Trend/Smartphone・Trend/travel・Discovery/Silence・Towel・Wake・Refrigerator・Voices/Free-address・Personalized news・AI hiring・Family C)を含む行を特定(Readツールは単一行長超過でエラーになるため使わない)。特にOPEN-135(Discovery A2)/OPEN-151(Voices 2V)/OPEN-153(Discovery B1)/OPEN-147(Family C)。
- `DECISION_LOG.md`: Grepで`試聴OK|試聴済|USER_LISTENING_DONE|ユーザー試聴|VALIDATED`→ヒット行±3行(ユーザー試聴記録の有無をテーマ別に確定。直近の索引部分は`Grep pattern="^## "`で見出し一覧→必要エントリのみ範囲Read)
- `CURRENT_SPEC.md`: Grepで`USER TEST READY|USER_LISTENING|PARTIAL|Human Review Lock|HUMAN_REVIEW_REQUIRED`→該当行
- 最新REPORT群(Glob `*_REPORT.md`でroot直下一覧を取得し、各テーマの最新REPORTのみ`## `見出しGrep→「試聴URL」「player」「Status」節を範囲Read): 特に`USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03_REPORT.md`0節(試聴URL 6件表)、`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`、`USER-TEST-AUDIO-COMPLETION-01_REPORT.md`、`FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`、Voices系REPORT(Glob `*VOICES*_REPORT.md`)、Discovery/Household系REPORT(Glob `*DISCOVERY*_REPORT.md`・`*HOUSEHOLD*_REPORT.md`・`*REFRIGERATOR*`)、`docs/pm/RESULT_PACKET_UT06_D.md`(Discovery最新状態)
- output directory: Glob `er0*_output/**/player.html`および`er0*_output/**/web_delivery.json`および`er0*_output/**/audio_validation.json`→テーマ別にplayer実在・Audio Validation結果(`status`キー)を確認。`human_review_player.html`・`player_prev_*.html`・`*_before_regeneration_*`・`prev/`配下は旧版/補助として除外。
- `docs/pm/PM_GOVERNANCE.md`: Grepで`9-5|Gate 7`→試聴URL提示ルール(raw.githack/raw.githubusercontent形式)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. テーマ→output directoryマッピング: `Grep pattern="AI Race Meets the Rulebook|Two Clocks|Smartphone Screen Is Still Here|slow travel|Young travelers|Silence Feel Uncomfortable|Clean Towel|Wake Before Alarm|Refrigerator Slider|crisper|One Office, Two Ideas|Personalized News|AI Sits Between|Home Robots|Future of Memory|Digital Twins" path=. glob=**/{web_delivery.json,player.html,*.md} output_mode=files_with_matches -i`→各テーマの成果物ディレクトリを確定(ヒットが多い場合はディレクトリ名で集約)。
2. 各テーマで: (a) A2本文(`article.md`/`reader_facing_article*.txt`等)有無、(b) B1本文有無、(c) episode mp3(`web/*.mp3`)有無、(d) `audio_validation.json`の`status`、(e) `player.html`有無、(f) 同一テーマの複数出力(v1/v2/Trial/fix)がある場合はDECISION_LOG/REPORTの「採用」「superseded」「旧版」記述と`web_delivery.json`の更新日時で最新正式版を一意確定(確定できなければ候補列挙)、(g) ユーザー試聴記録(DECISION_LOG/REPORT/OPEN_ITEMSの「試聴OK」「ユーザー評価」等)有無と日付。
3. 特に: A. Smartphone/ambient AI A2: `Grep pattern="Smartphone|ambient AI" path=DECISION_LOG.md`→Human Review Lock以降の完成記録の有無、`er011_output/`等の該当A2 player/Audio Validationの実在。B. Silence: Discovery系のSilence記事(`er014_output/four_type_observation_01/discovery/`か別ディレクトリか)を特定し、A2/B1の最新状態(RESULT_PACKET_UT06_D.md記載のNOT_READY状態と一致するか)。C. Wake Before Alarm: player/Audio Validation/web_delivery/試聴記録を実在確認。D. Voices: Free-address 2V(A2/B1)・Personalized news 2V(A2の実在を確認、無ければ「—」)・AI hiring 3V(A2の実在を確認、Trial違いは1記事)、CURRENT_SPEC/OPEN-151の`PARTIAL / USER TEST READY`との整合。E. Family C: Fable補足の6 playerを実在確認(旧Trial playerは出さない)。
4. 除外: CAR-T/immune reset記事、Home Robots/Memory/Digital Twinsの旧版(trial_09 home_robots v1・trial_10 memory/twins・fallback・prev)は一覧に出さない(除外した旨のみ報告)。
5. Web到達確認: 最終表に載せる全player URL(raw.githack `https://raw.githack.com/shimomura055/eigo-radio/main/<path>`)をUser-Agent付きHTTP GETで確認(200のみ掲載。404/その他は「未公開」としNOT_READY理由に記載)。CDN遅延時は60秒待ち最大2回。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_B_inventory.md --json-out docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_B_inventory_check.json
```

OPEN_ITEMS行抽出(Readツール不可のため):
```
.venv\Scripts\python.exe -c "import re;[print(l[:300]) for l in open('OPEN_ITEMS.md',encoding='utf-8').read().splitlines() if re.search(r'OPEN-1(35|47|51|53)\b|Smartphone|Silence|Towel|Wake|Refrigerator|crisper|Free-address|Personalized|AI hiring|AI Race|travel', l, re.I)]"
```

Audio Validation一括確認:
```
.venv\Scripts\python.exe -c "import glob,json;[print(p, json.load(open(p,encoding='utf-8')).get('status', json.load(open(p,encoding='utf-8')).get('gate_status','?'))) for p in glob.glob('er0*_output/**/audio_validation.json', recursive=True)]"
```
(キー名は実構造に合わせて調整。)

Web到達確認(掲載候補URL全件、raw.githack、User-Agent付きGET):
```
.venv\Scripts\python.exe -c "import urllib.request as u,sys;urls=sys.argv[1:];[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) if True else None for x in urls]" <URL1> <URL2> ...
```
(実URL全件を引数に展開して実行し、結果表を報告。404はtry/exceptで捕捉して記録。)

## SSOT追記文

なし(本委任はSSOT編集禁止)。監査で判明したSSOT不整合・Open Item漏れ・`USER_DECISION_REQUIRED`候補はRESULT_PACKETに「SSOT反映候補」として列挙のみ(Fableが委任A完了後に別途反映)。

## Git(明示add対象・コミットメッセージ・trailer)

なし(本委任はGit操作禁止。作成した2ファイル+delegation_log 2件はuntrackedのまま残し、Fableが後続でcommit手配)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_INVENTORY.md`と`USER-TEST-INVENTORY-01_REPORT.md`(同内容、REPORTはユーザー向け整形)に、ユーザー指示18-B〜Eの形式で:
1. T-0結果
2. **B. 最終一覧表**(テーマ単位、最新版のみ): Family/Theme/A2/B1/Voice structure(Voicesのみ2V/3V)/Status(`USER_LISTENING_DONE`・`USER_LISTENING_REQUIRED`・`NOT_READY`をA2/B1別に)/最新player URL A2/最新player URL B1(A2/B1共通playerならその旨)/ユーザー試聴済みか(記録の所在: DECISION_LOG行・REPORT名・日付)/備考(Audio Validation結果、superseded除外した旧版、確定根拠)
3. **C. 未試聴一覧**(`USER_LISTENING_REQUIRED`のみ: テーマ/Level/player URL)
4. **D. 未完成一覧**(`NOT_READY`のみ: テーマ/Level/残作業1行/修正要否=`USER_DECISION_REQUIRED`候補)
5. **E. 集計**: 独立テーマ総数/完成episode総数/試聴済みepisode数/未試聴完成episode数/未完成episode数、Status別テーマ数・episode数
6. 特記事項13-A〜E各1〜3行(Smartphone A2の実態、Silence最新状態、Wake Before Alarmの実検証可否、Voices各テーマのA2実在、Family C最新版確認)
7. 除外したもの(CAR-T、Family C旧版群)と除外根拠
8. 一意確定できなかったテーマ(候補と根拠)
9. Web到達確認結果表(URL/status)
10. SSOT反映候補(不整合・Open Item漏れ・USER_DECISION_REQUIRED候補)
11. 確認に使ったソース一覧(REPORT名・SSOT行・ディレクトリ)、事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用、内部識別子`b1b`は備考にのみ可)。
