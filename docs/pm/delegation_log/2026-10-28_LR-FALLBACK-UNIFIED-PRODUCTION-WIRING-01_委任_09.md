# 委任_09(Phase B / B5): 最終Human報告用資料 生成器(読取専用CLI、未配線=E2E_STAGESに入れない)+混入防止test(API 0)

共通事項=`…_委任_00_COMMON.md`。設計=`INTEGRATION_01.md`(§1・F-3/F-13/F-14)+`OPUS_REVIEW_01.md`(M-7、R-5、Fable照合)+`W4_FINAL_HUMAN_REPORT_DESIGN_01.md`+`W4_SAMPLE_01.html`。前提module=`er129_lr_display_reflection_01.py`(委任_07、commit済み。読取規則はW4 §3ではなく**er129の`build_lr_ledger`/`resolve_adopted_take`を唯一の入力**とする)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B5_FINAL_HUMAN_REPORT_01.md`。**実装委任**(新module `er131_final_human_report_01.py`+test+成果物のみ。既存Productionコード・公開ページ生成器は編集しない)。

## 要件(ユーザー原文§2・§6、決定済み)
- 1 run=1資料(Std/Adv別)、全Role(本文・topic_intro・comment・in_one_line・Preview・KP英語・KP解説・日本語音声・Z Dialogue)網羅。出力先=`final_human_report/<family>/<slug>/<run>/{standard,advanced}.html`(`user_test/`外。GitHub Pages経路)。TTS・ASR・組立完了後の後処理CLI(`--run <dir> --level a2|b1b --family X|Y|Z`)。
- LR=赤(変更後語句 太字+二重下線、変更前 取消線、前後英文併記、対象区間、変更語句、理由)。Fallback=濃青(対象テキスト全体+注記: 発動の事実・最終採用Style名・切替元Style・区間/Chunk/本文範囲)。重複=青区間内に赤語句。実行履歴(採用されなかった試行)は灰色枠・色の意味なし。全てに文字ラベル(LR/Fallback/発動なし/記録なし)。記録欠落=「記録なし」(推測しない)。時刻・cooldown・pathは非表示(sha先頭8桁のみ可)。
- 採用されなかった試行のFallbackを最終採用Styleとして表示しない(er129の採用take解決に従う)。Styleが変わらない再試行は表示しない。
- A/B/C等既存Family: er129が読取できる範囲で「Fallback有無のみ/記録不足で表示不可」を明記(音声方式は不変)。

## 混入防止(5層、test必須)
(1)双方向AST import禁止(er131⇄公開ページ生成器・TTS・ASR・KP表示・Prompt module) (2)run dirを書き換えない(前後sha一致) (3)出力先制約(`user_test/`配下へ書けない) (4)FHRトークン(`fhr-`class・注記文言・`LR_REWRITTEN`/`LR_APPLIED`/`FALLBACK_APPLIED`/Fallback Style名)が公開HTML・TTS入力・ASR正解・Style Prompt・KP表示・study_textに0件(保存run: AI島/告げ口心臓/Word Gacha/メロス_02/猿の手/Y E-1で実測) (5)`check_page(public)`へ追加する検査仕様を成果物に記載(配線は統合commit)。

## 作業
1. module+test(`er131_final_human_report_01_test_01.py`: 採用attempt判定はer129に委譲・重複・欠落・A/B/C・混入5層)。
2. 保存runから実資料を生成し成果物へ相対パスで列挙: AI島Std/Adv(LR赤、`AI agents`/`AI systems`)、Word Gacha Adv、メロス`_02`(発動なし)、猿の手Std、Y E-1 Std/Adv(人間承認原文復帰の表現)、告げ口心臓Std/Adv(LR 0・**Fallback 1**=Adv kp2_en ENGLISH_LOCK を青)、tru_ev evidence run(LR+Fallback重複・JA短文・Z Dialogue切替)。生成物は`final_human_report/`へ(commit対象。公開はGitHub Pages経路で可、`user_test/`には置かない)。
3. Git: 新規ファイル+生成資料+成果物のみ`git add`、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_09(B5): 最終Human報告生成器(未配線)+混入防止test+保存run資料(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。
4. 最終応答: 成果物パス+要約10行(test件数/混入0の実測/生成資料URL `https://shimomura055.github.io/eigo-radio/final_human_report/...`/未観測)。
