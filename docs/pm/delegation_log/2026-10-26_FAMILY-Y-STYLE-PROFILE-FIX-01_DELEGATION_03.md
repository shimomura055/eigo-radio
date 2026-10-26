## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_03(API 0・JPY0: `_03`公開ページの先行構築=Advanced完成版(Gate 15/15 PASS)の公開+Voice 1〜3の旧`_02`比較節+Standardの承認待ち2 segment(y_voice_1/preview)のHR試聴節[候補take個別再生]。Std通し版はユーザー承認後に委任_04で追加)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・leaf)、PM-SSOT-SYNC-15(SSOT)。あなたの所有=`user_test/family_y_production_redelivery_fee_03/**`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{BUILD_03,VERIFY_03,HR_REQUEST_STD_01}.md`、`tools/build_page_03.py`(拡張)、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP3.md`。run dir `run_style_fix_01`は読み取りのみ(組立stageはStd承認後)。ただしAdvの`gate,assemble,pages,page_verify`(API 0)はStdの承認待ちと独立に実行できるなら実行してよい(正式CLIの`--stages`で`b1b`のみ指定可能か`--help`で確認。Std Gate BLOCKで全体rc=2になるならAdvの組立済み成果物が生成されるかを確認し、生成されなければ組立はしない=公開はsegment個別再生+既存timelineのみで構成)。SSOT編集権なし。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。

## 性質/禁止

- 性質: 公開ページ構築+HR依頼資料(API 0)。到達上限=「Adv修正版公開・Std HR承認待ち」(「完成」「PRODUCTION_WIRED」と書かない)。
- 禁止: 有料API、HR Lockの解除・承認の代行(承認は人間のみ)、再生成、旧`_01`/`_02`の改変、Gate/QA条件の変更、禁止Git操作。
- 時間見込み: 約45分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSなし(`TTS_EXECUTION_MODE=STANDARD`は正式CLI起動時に環境変数として明示)。T-3: 費用なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_03.md` をN=683から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_03」のものを採用。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{REGEN_RESULT_01,COMPARISON_01,VERIFY_01}.md`、`tools/build_page_03.py`、`wpm_01.json`(自成果物)
- `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/BUILD_01.md`(前回`_02`の公開手順・ページ構成)
- `user_test/family_y_production_redelivery_fee_02/index.html`(構成の踏襲)
- `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/a2/narration/attempts/`(y_voice_1・previewの候補wav: attempt1/2=通常Style、attempt3=fallback)、同`a2/audit/`のASR結果(転写・NG箇所)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `er121_family_y_runner_01.py --help` で`--stages`/`--only-levels`相当の有無を確認(Advのみ組立可否)。
- 公開ページは`user_test/family_y_production_redelivery_fee_03/index.html`+mp3(公開mp3は`user_test/`のみ追跡)。

## 実施事項

1. **Advanced修正版**: 組立可能なら正式CLIで`gate,assemble,pages,page_verify`(b1b限定、API 0、`TTS_EXECUTION_MODE=STANDARD`明示、起動間隔150秒遵守)→通し音声をmp3化して公開。不可なら各segment個別再生のtimeline表示(順序はY構成どおり、Comment 2なし)で公開し、通し版は委任_04で追加と明記。
2. **Voice 1〜3比較節(Adv)**: 旧`_02`(default Style)と新版(PD06)をsegment単位で並べて個別再生。「S9未評価・ユーザー判断項目(個性を損なっていないか)」と明記。WPM前後表(`wpm_01.json`)。部位別Style前後表(全segment: 旧prefix要約→新prefix要約・再生成/再利用)。
3. **Standard HR試聴節**: 承認待ち2 segment(y_voice_1、preview)について、候補take(attempt1/2=承認Style、attempt3=fallback短文Style)を個別再生+各takeのASR転写とNG箇所(`re-deliveries`ハイフン/`思い通り`⇔`思いどおり`)を表示。Std 16/18通過segmentも個別再生で並べる(通し版は承認後)。**承認の操作方法**(ユーザーが「Std y_voice_1=take N承認、preview=take M承認」と返答→Fableが`er119/er011`の承認コマンドを委任で実行)を`HR_REQUEST_STD_01.md`に記載。run_01で同2 segmentがどう承認されたか(承認record・take)を参考情報として併記。
4. **検査**: HTML/mp3存在・リンク・HTTP 200(push後)・Comment 2不在・Voice割当(Puck/Zephyr/Schedar)を`VERIFY_03.md`に。
5. `BUILD_03.md`: 構成・コマンド全文・成果物一覧。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_03.md --json-out docs\pm\delegation_log\2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_03.md_check.json`
- 正式CLI(Adv組立、可能な場合): `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_style_fix_01 --theme-package <run_01と同じ> --stages gate,assemble,pages,page_verify <Adv限定引数> --tts-execution-mode STANDARD`(実値は`--help`で確認し全文記録)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `user_test/family_y_production_redelivery_fee_03/`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{BUILD_03,VERIFY_03,HR_REQUEST_STD_01}.md`、`tools/build_page_03.py`、delegation_log。pathspec付きcommit。
- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_03: 再配達記事 _03 先行公開(Adv修正版+Voice1〜3旧新比較+Std HR承認待ち2 segmentの試聴節、API 0)`
- trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/03`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_YSP3.md`: (0)T-0、(1)公開URL(index.html絶対URL)と構成、(2)Adv組立の可否と結果、(3)Std HR試聴節の内容(take一覧・ASR転写)、(4)検査結果、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)commit hash・raw URL。末尾5行要約。