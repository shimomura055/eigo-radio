# 結果: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_01(2026-10-09、Sonnet実行層、API支出¥0)

Status: DESIGN_READY(実行Go未)。Production変更なし、既存コード・Prompt・CURRENT_SPEC.md・OPEN_ITEMS.md無編集。check_delegation_prompt.py=FAIL(記録のみ、委任文末尾に記載)。

## 1. 成果物パス・commit・raw URL
- 設計書 `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md`
- 事前登録 `er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md`
- 新テーマ候補10件 `er052_output/factlock_astra_e2e_trial_01/NEW_THEME_CANDIDATES_01.md`
- SSOT追記: `DECISION_LOG.md`末尾(ユーザー決定1〜5)、`docs/pm/REPORT_LEDGER.md`1行。`docs/pm/ACTIVE_TASK.md`固定ヘッダ更新(.gitignore対象のためcommitされない一時ファイル)
- 委任記録 `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_01.md`、本ファイル
- commit hash / raw URLは末尾「Git」節。

## 2. 設計の要点
1. 10記事(旧4+新6)×2腕(旧=現Production経路 / 新=Fact Lock R0[Luna]+Astra R1→R2+M1+M3)。台帳・B3は腕で共有、新腕だけ注記版brief(人手注記)を使う。
2. 新腕はAstraのR2を`ja_writer/revision2.md`として置くだけでer019 runnerの既存「R2再利用」分岐に乗り、EN以降は既存Production経路を再利用できる(コードで確認)。
3. 新腕はJA再確認(案B)を無効化(`storyline_line=None`)。理由=案BがProductionのLuna Writerで本文を再生成し、新腕に旧Writerが混入するため。代償として旧腕との非対称(Opus論点2)。
4. M1/M3はWriter効果と交絡する。別runを増やさず、M1初回/再生成の前後ログ・M1の影の対照(旧入力の要約+同検査)・M3保護claimの下流判定(+影の再分類)で分離。Arm C(旧JA×M1/M3、約¥36見積)は任意。
5. 実行は単層3並列(W1:4テーマ/W2・W3:3テーマ)、旧腕→新腕、ゲートG0(¥0実装・dry-run)→G1(METAの新腕のみカナリア)→G2本番。
6. 停止条件は前回計画書を踏襲(provenance違反/API失敗/単価未登録は即停止、品質起因は止めない)。累計¥1,000でhard stop、¥800でソフトアラート。再開はstage完了マーカーと追記専用の費用台帳。
7. 事前登録: 重大は非対称(新腕に1件でも残れば悪化)、軽微は±25%+6対、Rewrite率/Human Review率の線、n=10の符号検定限界(9/10でp=0.011、7/10でp=0.17)。
8. 評価は自動集計→Sonnetラベル(3 worker)→Fable突合→ユーザー確認2〜3記事(元記事+X/YのR2のみ)→Opus条件C。

## 3. 前提作業一覧(a〜g+追加)
- (a) astra単価登録: `er005_output/cost_baseline_01/pricing_snapshot.json`+coverage test、約51行、Production単価表編集(別commit・Fable承認)、キャッシュ割引は未計上で過大側。
- (b) R0復唱(OPEN-175): Fact Lock R0 24本中1本(ホルムズ b2 r1=Astra matrixのR0そのもの)、all6/baseline 44本中4本。推奨=検出のみ約15行(修正はR0_PROMPT変更=Production変更のため未承認仕様)。
- (c) phase2タグ残存: 案B無効化で新腕では発生しない(0行)。有効化するなら`er052_factlock_writer_trial_01_run.py`で約30〜50行。
- (d) M1のStandard(A2)分岐: 推奨=今回は実装しない(新A2用プロンプトが要り未承認仕様)。実装なら約60〜90行+新プロンプト。
- (e) 記号後変換+Markdown除去: 既存部品を再利用(`strip_markdown`/`dash_to_comma`/`normalize_ellipsis_pause_ja`)、新runner内約40行、R2直後・FC前。
- (f) 2腕並走runner(新規ファイル): 約450〜600行+テスト約250行、動的fixture(`er050...py` L133-151形式)、subprocess分離、書込はtmp→rename。最大リスク。
- (g) web_search未計上: OPEN-242(commit 0110d6f1)で是正済み。残る穴=astra単価未登録(→a)、Checker runnerの別budget stateの横断集計。実行前に¥0で再確認(約20行)。
- (h) 新6テーマの注記版brief: 現状は人手(`annotate_briefs.py`のSPEC)。Sonnet workerが固定ルールで作成しFable確認を提案。Production化できない再現性の限界。
- (h2) TTS入口: 既存のDEV TTS Standard同期スクリプトが未特定(er019 runnerはTTS stageなし)。(i) 影の対照ログ等約150行。

## 4. 費用・時間見積(すべて見積。出典は設計書6節)
- 新腕 約¥42/記事(Astra Standard R1+R2 約¥31.3が主。委任_18結果§5の実測トークン由来、範囲27〜34)、旧腕 約¥9.2/記事、新6テーマresearch共有 約¥100(run_02実測¥16.95等)、TTS+ASR 約¥40(Fable見積、根拠未確認)。
- 合計 約¥650(範囲約¥560〜780)。Fable見積約¥700と整合。上限¥1,000に対し中央値で約¥350の余裕。
- 時間: Checker平均345.5秒/run(§81実測)×40 runを3並列、W1が約130分、全体約2〜2.5時間(見積)。

## 5. Opus条件Aに出す論点(設計書8節)
1) 交絡(Writer×M1/M3)と影の対照/Arm Cの要否 2) 案B無効化の非対称 3) 新腕のProduction等価性(FC MAJOR・記号Gateを記録のみにする是非) 4) 注記briefの人手依存 5) M1のStandard未実装 6) n=10の統計限界と判定線(床効果・符号検定) 7) コスト/停止設計(astra単価の単一出典・カナリア)

## 6. 未確認事項・判断が必要な点(Fable向け)
- 委任文の(b)「R0プロンプト漏れ」と(c)「タグ残存」が一文に混在。(b)=OPEN-175復唱、(c)=phase2タグ残存と解釈した(要確認)。(b)はProductionプロンプト修正を要するため検出のみを推奨、修正するならユーザー承認(新仕様候補として報告のみ)。
- 案B無効化(新腕のja_source MAJORはSTOP記録)で良いか。Production等価(FC MAJOR→must-fix・記号Gate)にするか。いずれも新仕様に近い判断。
- Standard(A2)のM1を実装するか(推奨せず)。Arm C・影の対照のAPI追加(約¥6+約¥36の見積)を許可するか。
- TTS: 2記事の選定時期、入口スクリプト(未特定)、費用約¥40の根拠は未確認。
- 宇宙兵器の台帳が`open233_b3_trial_01`側と一致するか(META/ホルムズは一致を確認)は実行前に照合。旧腕B3の原本(注記なし)と新腕の注記版は別ファイル(sha256は設計書2節)。
- 追加発見: run JSONのM3保護claim一覧の記録有無は未確認(件数`n_protected_keys`のみ確認)。wrapperで補う想定。
- astra単価は`extracted_pricing.json`の単一出典で、ダッシュボード請求との突合は未実施。
- 新テーマ候補10件は「現在のニュース性」を未確認(web検索不使用)。ユーザーに6件+補欠2件を依頼。
- 新しい仕様候補: なし(いずれも「推奨」または「要判断」として報告に留め、実装・変更していない)。

## 7. 所要時間・API支出
- 所要: 約1時間(読込・設計・文書作成・commit)。API生成支出=¥0(OpenAI/Gemini呼び出しなし、web検索なし、HTTP取得なし)。
