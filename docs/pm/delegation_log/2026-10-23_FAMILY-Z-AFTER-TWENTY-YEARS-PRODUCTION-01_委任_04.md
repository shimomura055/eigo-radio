MARKER: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_04 (2026-10-23, Fable→sonnet-worker)

# 管理ID: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_04
# 目的: OPEN-482 第2層(ASR最終ゲート value_guard の時刻atom不整合)を影響分析gate付きで修正し、Std c8 を原稿不変で再生成→完成段1起動→試聴ページ→SSOT→Git→報告まで完遂する。

## 0. 前提(必読・短時間で)
- 前委任_03の報告 `docs/pm/RESULT_PACKET_FZ20Y3.md`、影響分析 `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/OPEN_482_IMPACT_01.md`、候補diff `.../OPEN_482_VALUE_GUARD_CANDIDATE_01.diff`、委任_03原文 `docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_委任_03.md`(禁止事項・Git作法・1起動ルールは全て継承)。
- ユーザー原指示 `docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER.md` §8報告8項目。
- `docs/pm/ACTIVE_TASK.md` は自分の行(委任_04行を新設、委任_03行の直下)のみ編集。「有料run(TTS)進行中」flagをTTS前に立て、終了後に「終了(JST時刻・実費・再起動回数)」へ更新。他agent(Family Y 委任_14)がTTSを並走している可能性があるので、TTS直列化ルールに従い、ACTIVE_TASK内の他行の「有料run(TTS)進行中」flagを確認してから開始する(最大待機30分、待機中は他作業を進める)。

## 1. Fable判断(本委任の方針)
- 前委任_03の提示A/B/C のうち **A(第2層の根本修正)を採用**。B(人間試聴承認)は最終手段、C(原稿改変 `half past ten`)は不採用(ユーザーが個別回避を否定しているため)。
- 第1層(er006 `_convert_cardinal_words`、commit b5138e452)と同じ不具合(隣接数詞語の単純合算)が第2層にも存在するので、**同一不具合の第2症状として、同じ影響分析gate方式で修正する**。Opus必須レビュー条件A/Bには該当しない(新構造でなく、同一問題への3回目パッチでもない)とFableが判定した。
- 「Production codeの変更は当該箇所のみ」の枠を以下に再定義する:
  (a) `er078_asr_value_guard_01.py::_guard_en`(または `_compare_pair`)への時刻分岐: 「時0-24・分00-59の数値2atom(例 `10`,`30`)と、反対側の1 time atom(例 `1030`)が hour×100+minute で一致すれば EQUAL」。候補diff(約9行)を基礎にしてよいが、am/pm・`10:13`/`10:15`/`11:30`/`2:03`/`20:1`/`40`/`30`/`ten` 単独 等は非EQUALのまま維持すること(前委任_03の合成負例を全部再利用)。
  (b) `er021_en_asr_semantic_equivalence_production_01.py::_tier1_atoms` の隣接数詞語合算(純語形 `ten thirty`→40): 第1層と同じ分割規則(一の位/10-19語の直後に十の位/10-19語が来る境界で分割)を適用する。**ただし(b)は同じgateを単独で通過した場合のみ採用**。gateが通らない、または影響が広い(PASS→NGが1件でも出る)場合は(b)を見送り、OPEN-482の残存項目として記録する(c8完成には(a)だけで足りる見込みのため)。
  (c) 上記(a)(b)以外のProduction変更は禁止(Prompt/閾値/flag/Gate構造/他module)。
  (d) 副次の既存の穴(`ten thirty`↔`1030` 桁連結がEQUAL)は今回修正せず、OPEN-482に残存事項として明記する。

## 2. 影響分析gate(前委任_03と同一基準。通過しなければ修正をcommitしない)
 (i) replay: 既存の canonical/ASR 判定対(前回の14対+走査で見つかる時刻/数値パターン)を修正前後で再計算し、**PASS→NG = 0件** を確認。NG→PASSは件数と内訳(全て隣接数詞語/時刻atom起因であること)を示す。『開いた窓』run_sf_prod_01・melos・X記事群・pool backtest・golden に判定変化がないことを再確認。
 (ii) 合成負例(前回21件+am/pm・`10:03`・`1:30` vs `13:00`・`twelve thirty` vs `12:03` 等、最低25件)が全てNGのまま。正例(`ten thirty`↔`10:30`/`ten-thirty`/`10 thirty`、`two thirty`↔`2:30`、`one thirty`↔`1:30`、`10 thirty`↔`1030`[既存挙動])がPASS。
 (iii) 差分は(a)(b)それぞれ1関数1ブロック以内。新規test(例 `er078_time_atom_test_01.py`、`er021_time_numeral_test_01.py`)を追加し、既存 `er006_time_numeral_test_01.py`・`er006_cardinal_and_conjunction_test_01.py`・er078/er021の既存testがPASS。
 - gate結果は `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/OPEN_482_IMPACT_02.md` に保存(修正前後の判定表・負例表・差分行数・(b)採否と理由)。
 - gate不通過(PASS→NGが出る/負例が通る)なら、修正を入れずSTOPしてFableへ手戻り(その場合は(a)の縮小案と案Bを併記)。

## 3. 修正後の手順(gate通過時)
 1) 全回帰(`py -m pytest -q` 相当、前回と同じ範囲)。自分起因の失敗0を確認(既存3件[er019/er020/er003_test_bad]は既知として記載、er064のtracked-py検査はcommit後に再実行して解消を確認)。
 2) commit(`git add` は変更ファイル明示、`git diff --cached --name-status` 確認、`git commit --only -- <paths>`、secret pattern grep 0件)→ `git push origin HEAD:main`。
 3) c8: `approve_regenerate` を**原稿不変**で実行(auditファイルを `audit_hr_lock_release_fz20y04.json` として記録、理由=OPEN-482第2層修正後の再生成)→ `--only-clips full_story_part2_c8` で再生成。テイク上限2(標準)+fallback 1(runner既定どおり)。**有料run起動はこの再生成1回+完成段1起動の計2回のみ**。cool-downはハングではないので自PIDを終了しない(26-6)。再起動が必要になった場合は起動せずSTOPしてFableへ。
 4) c8が合格したら `provision_shell,gate,assemble,pages,page_verify` を**1起動**で実行。試聴ページ `user_test/family_z_after_twenty_years_01/`(Std/Adv切替・通し・パート別・全スクリプト・KP・開発者情報なし=『開いた窓』ページと同形式)。page_verify PASSと実再生確認(通し音声の長さ・無音/切断なし)を記録。
 5) c8が再びHR Lockになった場合: それ以上再生成せず、Lock理由(判定ログ原文)を保存してSTOP→Fableへ(案B提示用に、ASR転記・音声長・該当テイクのパスを添える)。
- 費用上限: 本委任 **15円**(作品累計 約46.5円→≤65円)。当日(10-23 JST)上限1,400円の残を開始時にACTIVE_TASK/費用台帳から確認し、超過見込みなら開始前にSTOP。

## 4. SSOT・記録(完成後)
- `OPEN_ITEMS.md`: OPEN-482 を更新(第1層+第2層(a)[+(b)採否]、gate結果、残存穴(d)、X/Z共通、Production変更の範囲、PRODUCTION変更=不具合修正でありGate閾値・仕様の変更ではない旨)。新規OPEN: 『二十年後』完成版提出・ユーザー最終試聴待ち(Std/Adv構成・時間・費用・ページURL)。OPEN-472: 本runでRET/PNAPが会話経路で発火・受理に寄与した証跡があれば追認材料として追記(なければ「本runでは該当なし」と1行)。
- `DECISION_LOG.md`: 委任_04の決定(案A採用・個別回避不採用・gate基準)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 新規UDR「『二十年後』最終試聴PASS可否」(判断待ち)。
- `CURRENT_SPEC.md`: 仕様変更はないので原則不要。Z作品登録表に『二十年後』を既存書式で1行追加する必要があるかを確認し、既存の『開いた窓』記載と同形式でのみ追記(新規節は作らない)。
- 本委任文を逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_委任_04.md`(先頭MARKER行一致で N を確定、要約保存は不可)。
- 報告 `docs/pm/RESULT_PACKET_FZ20Y4.md`。
- 最終commit/push(wav・raw_usage_log・STOP関連ファイルは追跡しない。`git add -A/-u/-f` 禁止)。

## 5. 報告(ユーザー§8の8項目に沿って。Fableが照合するので自己申告だけでなく証跡パスを付す)
 1. 完成版試聴URL(GitHub Pages)とページ検証結果
 2. 両レベルの構成(part数/clip数)・再生時間(Std/Adv通し秒)・Voice配役(ナレーター Aoede/Bob Algieba/警官 Schedar/刑事 Fenrir の固定割当遵守)
 3. 原作忠実性(SOURCE_CHECK_01.md)と品質検査結果(Gate PASS一覧、軽微所見=到着時刻30分 vs 原作約20分、因果・結末影響なし)
 4. 固有名詞・Key Phrase(PNAP/RET/UKUS発火有無、KP現行仕様A-1のみ・未承認G3/②未使用の明示)
 5. retry/再生成/Human Reviewの有無(c8の全テイク履歴 attempt 1〜最終、HR Lock→approve_regenerate 2回の記録、人間承認で通した音声=0件であること)
 6. 実際の制作費用(作品累計、内訳: Writer/TTS/ASR/その他)・制作時間・量産単価70円への示唆(登録負担≈45分 data追加のみ、時刻検査不具合2層の発見)
 7. Production経路・runtime evidence・SSOT/Git反映(commit hash、raw URL)
 8. 未解決Open Item(OPEN-482残存(d)・(b)見送り時はその旨、OPEN-472追認状況)とユーザー判断事項(最終試聴PASS)
- RESULT_PACKET末尾に4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)と判定整合行(重大NG/主因/是正対象/STOP理由/提示可否)、使用モデル名(最新か・理由)を付す。
- 途中で判断が必要になったら(gate不通過・c8再Lock・予算・再起動要)はそこでSTOPし、Fableへ現状・原因・選択肢を返す(自分で案B/Cを実行しない)。