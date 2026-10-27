## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06(ユーザー承認2026-10-27: Std `preview` Take 1をHR PASSとして正式確定→Style `fx_20261017`適用済み音声でStd/Adv完成版を組立→必須検査→**通し再生できる通常の最終試聴ページ**を公開→URL提出。API 0見込み(TTS/ASR再生成禁止)。run=`er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`)。並行Agent: KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(同runを**コピーして**evidence中。実runは触らない取り決め。あなたは実runを更新してよい)、GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(read-only)、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_05(フォーム)。Production Pythonは編集しない(不具合時は報告)。あなたの所有=run dir成果物、`user_test/family_y_production_redelivery_fee_03/`(通し版ページ: 既存`index.html`は先行版として`preview_segments_01.html`へリネームし、新しい`index.html`=通常の最終試聴ページ。`hr_preview_01.html`は残置)、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{HR_APPROVAL_STD_PREVIEW_01,BUILD_04,VERIFY_04,COST_03}.md`、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_04.py`(必要なら、`build_page_03.py`流用)、`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_{USER_03,DELEGATION_06}.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP6.md`。SSOT編集権なし。pathspec付きcommit(公開mp3は`user_test/`のみ追跡、wav/raw_usage_log/STOP/lock不追跡)。

## 性質/禁止

- 性質: 承認済みHR確定手順の実行+完成版組立+公開。到達上限=完成版公開・ユーザー最終試聴待ち(Fable受入を経て提出。記事の最終受入はユーザー試聴承認後)。
- 禁止: Gate緩和・迂回、HR Lock解除(採用toolの正規経路のみ)、TTS/ASR再生成(既存takeのみ。やむを得ず必要なら理由と見積を報告して停止)、本文・Voice・Style・KPの変更、旧Style比較/Voice別S9/Take比較をページに必須項目として置くこと、同一run 5分3回起動・150秒未満の再起動、禁止Git操作。
- 時間見込み: 約1.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー承認原文(下記)を`..._USER_03.md`へ逐語保存(採用toolの`--user-statement-ref`に使う)。T-2: runner起動前に`py tools/stop_scope_check_01.py --managed-id FAMILY-Y-STYLE-PROFILE-FIX-01 --run-dir <run> --out <run>/audit/stop_scope_check_06.json`。T-3: 費用はusage log実測(0円期待)。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_06.md` をN=714から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06」のものを採用。

## ユーザー承認(原文・逐語)

【Claude Code指示｜Family Y「再配達」Human Review承認・完成版制作】

## 1. ユーザー承認

Family Y「宅配の再配達は有料にすべきか？」のStandard Previewについて、**Take 1を承認します。**

対象音声：
`std_hr/std_preview_take1.mp3`

原稿「思いどおりに」とASR「思い通りに」の差異を確認したうえで、ユーザーは当該音声を問題なしと判断しました。

この1 segmentをHuman Review PASSとして正式確定してください。

既存Gateを変更・緩和するのではなく、承認済みのHuman Review確定手順に従って処理してください。

## 2. 完成版制作

承認後、以下を進めてください。

1. Take 1を正式採用し、Human Review結果を記録。
2. Family Xから継承した承認済みStyle `fx_20261017` を適用した音声を使用。
3. Standard／Advancedの正式完成版を組み立てる。
4. 必須の音声・組立・公開検査を実施。
5. **Standard／Advancedを通し再生できる通常の最終試聴ページ**を公開する。
6. 完成版のURLをユーザーに提出する。

## 3. ユーザーへの提出内容

今回必要なのは、完成した記事の最終試聴です。

- Standard／Advancedの通し再生
- 必要に応じたパート別再生
- 最終版の原稿・Key Phrase等の学習内容

旧Styleとの比較、Voice別Style評価、Take 1／2／3の比較は、今回の追加必須判断としないでください。

技術的な確認はClaude/Fable側で完了させてください。

## 4. QCD・完了条件

- 承認済み本文・Voice・Style・Key Phraseを無断変更しない。
- 不必要なTTS・ASR再生成を行わない。
- retry／fallback／resume、Human Review Lockとの整合を確認。
- 既存Validator／Regression／公開検査をPASS。
- 必要なSSOT／Git反映を完了。
- Fableが完成版の独立受入を実施。
- 既存承認予算・STOP条件を遵守。

新たな品質上の問題が発生した場合は、承認範囲内で自律的に解決してください。ユーザー判断が必要な場合だけ、該当箇所を原稿・ASR結果・推奨音声1つとともに提出してください。

**目標：Family Y「再配達」Standard／Advancedの完成版を速やかに提出し、ユーザー最終試聴待ちまで進めること。**

完成版のユーザー試聴承認を得るまでは、記事の最終受入完了としないでください。

(原文ここまで)

## 実施事項

1. **HR確定**: `.venv\Scripts\python.exe docs\research\FAMILY-Y-STYLE-PROFILE-FIX-01\tools\hr_adopt_style_fix_01.py --level a2 --segment preview --take 1 --dry-run`→`--apply --user-statement-ref docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_03.md`(採用toolが`human_approved_segments.json`/HR Lock/preview entry(`SKIPPED_NOT_SELECTED`→復元、OPEN-552)を正規手順で更新することを確認)。y_voice_1 take4(Fable許可再生成、既にPASS)の採用状態も確認。`HR_APPROVAL_STD_PREVIEW_01.md`に記録(承認原文path・対象sha・ASR差分・判定PASS理由=ユーザー承認)。
2. **組立**: `er121_family_y_runner_01.py --help`で引数確認後、`--mode real --slug redelivery_fee --run run_style_fix_01 ... --stages provision_shell,gate,assemble,pages,page_verify`を1起動(REGEN_RESULT_02 §3先例、予算guard引数は累計比較に注意=`--approved-budget-jpy`は既存累計以上を指定し理由記録)。Style Gate(`Y_ROLE_COVERAGE`完全一致、`audit/style_actual_vs_approved.json`)PASS、Audio Validation Gate PASS、clipping/長停止検査、page_verify ok を確認。確定内容保護G1(`stage_kp_post_install`等)が旧run(KP確定はフォーム未使用)でlegacy WARNのみで止まらないことも確認(止まった場合は原因・rcを報告、独断で`EIGO_KP_CONFIRMED_PROTECTION=0`にしない)。
3. **最終試聴ページ(`_03/index.html`=通常構成)**: Std/Advの通し再生(各1本のmp3)+パート別再生(任意)+最終版原稿(Std/Adv本文)+Key Phrase等の学習内容(現行確定KP・訳)+制作情報(Voice表・Style `fx_20261017`・model_id)。旧Style比較・Voice別S9・Take比較の節は置かない(先行版`preview_segments_01.html`へリンク1行のみ可)。`_02`は旧版として残置。公開後HTTP 200(index・Std/Adv mp3)。
4. **受入材料(`VERIFY_04.md`)**: 通し音声の長さ・クリッピング・無音・segment構成がtimelineと一致、Std/Advの原稿sha=承認済み本文sha、Voice表=承認済み(Voice 1=Puck等、run_voice_puck_ev_01/`_02`と同一)、Style=fx_20261017の実測一致表、KP=既存確定と同一、Adv Comment 2なし(`_02`仕様維持)、Gate結果、費用。
5. `COST_03.md`(0円期待。発生時は内訳)。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{REGEN_RESULT_02,HR_REQUEST_STD_02,VERIFY_03,BUILD_03,HR_PACKET_STD_PREVIEW_01}.md`、`tools/hr_adopt_style_fix_01.py`(全体)、`tools/build_page_03.py`(構造)
- `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{BUILD_01,VERIFY_01}.md`(`_02`完成版の構成・検査項目=通常の最終試聴ページの先例)
- `er121_family_y_runner_01.py`: `--help`出力、Grep `approved-budget|stages|page_verify` ±5
- run dir: `a2/audit/`、`b1b/audit/`、`human_approved_segments.json`、HR lock、`timeline*.json`

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_06.md --json-out ...\_check.json`
- 上記1〜2のコマンド(実行前に`--help`/`--dry-run`)
- 公開確認: `Invoke-WebRequest <URL>` → 200
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_YSP6.md`にOPEN-537/539/550/552追記文案(HR PASS確定、完成版公開、ユーザー最終試聴待ち、UDR-YRF-2/3撤回済み)。

## Git

- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06: Std preview Take1 HR PASS確定(ユーザー承認)→fx_20261017適用のStd/Adv完成版組立・検査→通常の最終試聴ページ_03公開(API 0)`。trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/06`。push。

## 報告

`docs/pm/RESULT_PACKET_YSP6.md`: (0)T-0、(1)HR確定記録、(2)組立・Gate結果、(3)公開URL(index・Std mp3・Adv mp3)とページ構成、(4)受入材料(VERIFY_04要点)、(5)費用、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾5行要約。