## 管理ID

PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01(ユーザー正式決定2026-09-18: 標準配布経路をGitHub Pages基準へ更新+「GitHub Pagesはユーザー自身の操作により有効化された」事実記録+Dangling Reference Check)。並行Agentなし(Fable確認済み。次のGate実装タスクは本タスク完了後に起動)。音声stageなし、lock不要。`docs/pm/ACTIVE_TASK.md`の固定ヘッダ+要約を本タスク内容で更新してから開始。

## 性質/到達上限Status/禁止事項

- 性質: SSOT/PM文書更新(ユーザー`APPROVED_FOR_PRODUCTION`済み)。到達してよい最大Status: `PRODUCTION_WIRED`(全項目完了時のみ)。
- 禁止: コード・HTML・TSV・canonical artifactの変更禁止(文書更新のみ)。CLAUDE.mdは変更しない(「変更ファイルのraw.githubusercontent.com URLを添える」は開発用ファイルリンクのルールであり、ユーザーテスト配布経路とは別。変更が必要と考えた場合はSTOPして報告)。過去の証跡(DECISION_LOGの過去エントリ本文・delegation_log・RESULT_PACKET・E2E evidence)内の旧URLは書き換えない。外部API支出禁止(¥0)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。
- 「Claude判断で追加仕様を広げない」: 記述の更新は「正式ユーザーテスト配布経路=GitHub Pages」「rawcdn/rawgit/raw/blobをユーザーテスト標準経路として参照しない」「Pages有効化はユーザー操作」の3点に限定。分類に迷う箇所(現在URLか過去証跡か判別できない行、10記事以外の記事の公開URL行の扱い等)は書き換えずに一覧化し`USER_DECISION_REQUIRED`候補として報告(STOPではなく、確定分は完了させ、迷った分だけ報告)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01.md`)

## ユーザー指示(原文)

「2. PM_GOVERNANCE 標準配布経路 → GitHub Pages基準へ更新する。raw / blob / rawcdn を標準配布経路としている古い記述を、現在のProduction実態に合わせて更新する。正式なユーザーテスト配布経路はGitHub Pages。正式Landing URL: https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html ただし、過去証跡として旧rawcdn URLをDecision Log等に残すのは可。新しいProduction仕様としては、rawgit/rawcdnを標準経路として参照しないこと。Dangling Reference Checkを実施し、PM_GOVERNANCEだけでなく CURRENT_SPEC / DECISION_LOG / ARTIFACT_REGISTRY / OPEN_ITEMS等に不整合が残っていないか確認する。」
「3. GitHub Pages有効化の経緯 → ユーザー自身の操作。SSOTには以下の事実として記録する。『GitHub Pagesはユーザー自身の操作により有効化された』推測表現ではなく、ユーザー確認済み事実として記録してよい。」
「Claude判断で追加仕様を広げないこと。新しい問題・新しい仕様候補が出た場合は、USER_DECISION_REQUIREDでSTOPして報告すること。」

## 事前指定Read一覧

1. `docs/pm/PM_GOVERNANCE.md`: Grep `rawcdn\.githack|raw\.githubusercontent|githack|blob/main|標準配布経路|配布経路|Gate 7` → 該当10箇所+各前後10行(9-5節・Gate 7・9-12節等の配布経路記述)
2. `docs/pm/PM_BRIEF.md` L86-95(「標準配布経路はGitHub blob URL・raw URL」記述)
3. `CURRENT_SPEC.md`: Grep `rawcdn|githack|ユーザーテストWeb表示仕様・配信経路|配信経路` → 該当行+前後5行(Phase Eで新設した節の位置と、旧経路記述1箇所)
4. `ARTIFACT_REGISTRY.md`: Grep `rawcdn` → 13箇所すべて+各行全文(どの記事/成果物の行か、「正式URL」として書かれているか「旧/SUPERSEDED/証跡」として書かれているかを判別)
5. `OPEN_ITEMS.md`: Grep `rawcdn|OPEN-173|GitHub Pages|Pages有効化|経緯` → 該当行(OPEN-173本文、Phase Eで記録した「有効化経緯未記録」の記述箇所)
6. `DECISION_LOG.md`: Grep `^## USER-TEST-HOSTING-GITHUB-PAGES-01` → 本体エントリ範囲(末尾に事実追記するため)。過去エントリのURLは変更しない
7. `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv` 全文(10記事20 URLのPages正式値。ARTIFACT_REGISTRYの該当記事行を置換する際の正)

## 事前指定Grep一覧+追記位置・更新位置の手順

- G-1 PM_GOVERNANCE.md: 該当箇所のうち「標準配布経路」「試聴依頼URL」「Gate 7でユーザー環境から開けることを確認する経路」を定義している記述を、「正式ユーザーテスト配布経路=GitHub Pages(`https://shimomura055.github.io/eigo-radio/`配下、正式Landing URL=`https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html`、個別記事=`.../user_test/unified.html?src=&level=&en=&ja=`、固定SHA不要・常に最新main・反映遅延目安=deploy数分+Cache-Control 600秒)。rawcdn.githack.com/raw.githack.com/raw.githubusercontent.com/GitHub blob URLはユーザーテスト配布・試聴依頼の標準経路として使用しない(ユーザー環境でrawgit『One more step』確認画面が出るため、USER-TEST-HOSTING-GITHUB-PAGES-01、2026-09-18ユーザー決定)。開発用ファイル参照(CLAUDE.mdのraw URL添付ルール)は別扱いで変更なし」へ更新。過去の経緯説明(「〜で明確化」等)は残し、末尾に「(2026-09-18、PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01で更新)」を付す。既存の`file:///`・`C:\`禁止記述は維持。
- G-2 PM_BRIEF.md L88-95: 同趣旨で更新(短く)。
- G-3 CURRENT_SPEC.md: Phase E新設節に「GitHub Pagesはユーザー自身の操作により有効化された(ユーザー確認済み事実、2026-09-18)」を追記。旧経路記述1箇所を確認し、「標準経路」として書かれていれば同様に更新(証跡的記述なら注記のみ)。
- G-4 ARTIFACT_REGISTRY.md: 13箇所を分類。(i)TSV掲載10記事の20 URL(またはLanding)を「現在の正式URL」として書いている行→TSVのPages URLへ置換し、旧rawcdn URLは「旧経路(〜2026-09-18、SUPERSEDED)」として括弧併記可。(ii)明確に「旧/SUPERSEDED/証跡/Trial」として書かれている行→無変更。(iii)10記事以外(例: 14記事セットの残り4記事[Space Weapons/AI Control等]・Trialページ・Human Reviewページ)の公開URL行→URLは書き換えず、行末に「(旧rawcdn経路。2026-09-18以降の正式ユーザーテスト配布経路はGitHub Pages、Pages URL未発行)」と注記のみ。分類に迷う行は無変更で報告(USER_DECISION_REQUIRED候補)。
- G-5 OPEN_ITEMS.md: OPEN-173をCLOSE(本タスクで更新済み、証跡参照)。「Pages有効化の経緯未記録」をOPEN Item化していればユーザー確認済み事実を記してCLOSE(していなければPhase EのDECISION_LOGエントリへの追記のみ)。
- G-6 DECISION_LOG.md: `## USER-TEST-HOSTING-GITHUB-PAGES-01`本体エントリ末尾に「### 追記(2026-09-18、PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01): GitHub Pagesはユーザー自身の操作により有効化された(ユーザー確認済み事実)。標準配布経路記述をPM_GOVERNANCE/PM_BRIEF/CURRENT_SPEC/ARTIFACT_REGISTRYで更新、Dangling Reference Check結果…」を追記。索引+本体に`## PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01`エントリを新規追加(決定内容・変更ファイル・Dangling Check結果・Status)。
- G-7 Dangling Reference Check: 更新後、`PM_GOVERNANCE.md`/`PM_BRIEF.md`/`CURRENT_SPEC.md`/`ARTIFACT_REGISTRY.md`/`OPEN_ITEMS.md`/`docs/pm/templates/*.md`/`.claude/agents/*.md`に対しGrep `rawcdn|githack|rawgit|raw\.githubusercontent|blob/main`を再実行し、残存箇所を(a)正式経路として参照(=NG、0件であること)、(b)過去証跡・旧経路注記付き(OK)、(c)開発用ファイルリンク(OK)、(d)判断保留(報告)に分類して`docs/pm/closeout_136_e2e/distribution_path_pages_01/dangling_reference_check.json`に記録。`DECISION_LOG.md`は過去エントリが多数のため、`## USER-TEST-HOSTING-GITHUB-PAGES-01`以降のエントリのみ対象。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01.md --json-out docs\pm\delegation_log\PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01.md_check.json`
- Dangling Check: `.venv\Scripts\python.exe -c "import re,json,pathlib; pats=re.compile(r'rawcdn|githack|rawgit|raw\.githubusercontent|blob/main'); files=['docs/pm/PM_GOVERNANCE.md','docs/pm/PM_BRIEF.md','CURRENT_SPEC.md','ARTIFACT_REGISTRY.md','OPEN_ITEMS.md']+[str(p) for p in pathlib.Path('docs/pm/templates').glob('*.md')]+[str(p) for p in pathlib.Path('.claude/agents').glob('*.md')]; out=[{'file':f,'line':i+1,'text':l.strip()[:200]} for f in files for i,l in enumerate(pathlib.Path(f).read_text(encoding='utf-8').splitlines()) if pats.search(l)]; pathlib.Path('docs/pm/closeout_136_e2e/distribution_path_pages_01').mkdir(parents=True,exist_ok=True); pathlib.Path('docs/pm/closeout_136_e2e/distribution_path_pages_01/dangling_raw_hits.json').write_text(json.dumps(out,ensure_ascii=False,indent=1),encoding='utf-8'); print(len(out))"`(この生ヒット一覧に分類(a)〜(d)を付与した`dangling_reference_check.json`を作成)
- 正式Landing URL到達再確認: `.venv\Scripts\python.exe -c "import urllib.request; r=urllib.request.urlopen('https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html'); print(r.status, r.headers.get('content-type'))"`

## SSOT追記文

上記G-1〜G-6のとおり。「GitHub Pagesはユーザー自身の操作により有効化された(ユーザー確認済み事実、2026-09-18)」は推測表現を使わずこの文言で記録。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `docs/pm/PM_GOVERNANCE.md`、`docs/pm/PM_BRIEF.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`ARTIFACT_REGISTRY.md`、`OPEN_ITEMS.md`、`docs/pm/closeout_136_e2e/distribution_path_pages_01/*.json`、`docs/pm/delegation_log/PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01.md`(+`_check.json`)、`docs/pm/RESULT_PACKET_DISTRIBUTION_PATH_PAGES_01.md`。
- メッセージ: `PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01: 標準配布経路をGitHub Pages基準へ更新+Pages有効化=ユーザー操作を事実記録+Dangling Reference Check+OPEN-173 close`
- trailer: `Task-ID: PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01`
- push前後`git fetch origin`、main=origin/main確認。`git status --porcelain`で混入なし確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DISTRIBUTION_PATH_PAGES_01.md`(新規)に:
1. 最終Status(`PRODUCTION_WIRED`/`USER_DECISION_REQUIRED`残あり)
2. PM_GOVERNANCE.md更新箇所(行番号・旧→新要旨、10箇所の扱い)
3. PM_BRIEF.md更新箇所
4. CURRENT_SPEC.md更新箇所(Pages有効化事実の追記位置、旧経路記述の扱い)
5. ARTIFACT_REGISTRY.md 13箇所の分類結果表((i)置換/(ii)無変更/(iii)注記/迷い)
6. OPEN_ITEMS.md更新(OPEN-173 close、経緯項目の扱い)
7. DECISION_LOG.md更新(HOSTINGエントリ追記+新規エントリ)
8. Dangling Reference Check結果(分類(a)=0件であること、(b)(c)(d)の件数と(d)の一覧)
9. 正式Landing URL到達再確認結果
10. Git commit SHA、main=origin/main
11. USER_DECISION_REQUIRED候補(分類保留行、CLAUDE.md等の扱い)
12. 一覧外Read(理由1行)、check_delegation_prompt結果
