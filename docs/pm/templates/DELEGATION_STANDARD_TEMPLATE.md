# DELEGATION_STANDARD_TEMPLATE(委任文標準テンプレート)

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01(D-2、
2026-09-13ユーザー正式採用[施策1]、`docs/pm/PM_GOVERNANCE.md` 11節D-2参照)。

Fableは全委任文(Sonnet/Opusへの委任)を本テンプレートの見出し構成に従って
作成する。各見出し文字列は固定(`docs/pm/tools/check_delegation_prompt.py`
が本文字列でセクション検出を行うため、文言を変更しない)。

共通Charter(行動大原則8項目)の正本は`CLAUDE.md`「共通Charter」節(`docs/pm/PM_GOVERNANCE.md` 29節)。委任文の性質欄・並列化判断・費用承認の記載は、Charter原則2(不要な待機・別日化・直列化をしない)・原則6(承認済み個別枠内の少額費用は都度承認を求めない)に従う。本テンプレートは8原則を複製しない。

---

## 管理ID

(例: `PM-XXXX-01`。並行タスクとの衝突がないか確認した結果も1行で記す。)

## 性質/到達上限Status/禁止事項

(Trial/Production/検証等の性質、到達しうる最終Status[VALIDATED/
APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED/USER_DECISION_REQUIRED等]、
禁止事項[対象外ファイル不可・費用上限[Cap]・破壊的操作禁止等]を明記する。
費用上限[Cap]の記載はT-3の定型文(Guardrail文言)に従う。「上限¥X、
超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが
無いもの)は使用しない。**Opus独立技術レビューGate(`docs/pm/PM_GOVERNANCE.md`
11-3節、2026-10-02)の該当判定[条件A/B/C/D/非該当]を1行で記す。**
**修正範囲の線引き[PM_GOVERNANCE 11-8、2026-10-19]: 不具合の修正を含む
委任では、範囲外を「受理面・閾値・方式の新設/拡大」、範囲内を「承認済み仕様・
設計原則との矛盾[仕様文と実装の乖離・論理的に不整合な比較]の是正とその
Regression・検証」と書く。方式や閾値の変更一般を包括的に範囲外とする書き方は
しない[承認済み仕様への是正まで『範囲外』に分類されるため]。実運用では固定ブロックの
D-1欄が方式・適用性の宣言に使われている[2026-10の委任文27件]ため、D-1欄に修正範囲を
書く場合も同じ語で書く。**
**主要タスクでは時間見込み[全体・工程別]と並列化判断[並列実行する作業/
直列化する場合の理由]を1〜2行で記す[PM_GOVERNANCE 8-X、2026-10-06]。**
**再委任・再計画の委任では、前委任のQDC記録[目的/試行/原因仮説と証拠/結果/
改善見込み/費用/次の一手]と受入記録[Gate 7、sandwich-pm.md手順4-2。必須5項目=
当初目的・要求された最終状態/実際に生成・残存した最終成果物(失敗終了時の最終
成果物を含む)/証拠(ファイル:行・観測値)/目的要件との一致・不一致(項目ごと)/
最終受入判定と理由。要求を満たさない成果物が残存、または証拠なしならACCEPTED
不可。2026-10-15決定②、REGISTER #76。直後に判定整合行[重大NG/主因/是正対象/
STOP理由/提示、PM_GOVERNANCE 27-1]を1行]を1ブロックで冒頭に記す
[PM_GOVERNANCE 11-6]。**
**費用/日次: 当日(JST)既使用JPY<y>(出典: RESULT_PACKET|LEDGER|script)/
残JPY<1,000-y>/本委任見積JPY<e>(根拠: call数×単価、上限=Guardrail)/
改善見込み<高|中|低>(11-6)/承認区分: <A:Fable判断可|B:ユーザー承認要|
C:承認済みscope内>(A/C=承認済みScope内かつ案件見積300円以下かつ日次1,000円以内。B=見積300円超・日次超過見込み・個別Cap超過・新仕様/未承認Trial範囲/重要Scope変更。分割・日付分割は合算判定。正本PM_GOVERNANCE 7-7)。JPY0の委任は「JPY0」のみでよい[PM_GOVERNANCE 7-9、
2026-10-15]。T-3の定型文はこの行と別に維持する。**)

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

`docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`の本文をそのまま
貼る(E-1/D-1/G-1/F-1/T-0/T-2は常時、T-1は施策1 Trial対象タスクのみ、
T-3は費用上限[Cap]を伴う委任のみ)。T-0は委任文標準の検証手順(受領した
委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し
`check_delegation_prompt.py`で検証)であり、本文言は
`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が正本。T-2(2026-09-25、
`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`)はTTS Standard同期
明示の再確認であり、本文言も`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が
正本。T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`)は費用上限
[Cap]=暴走防止Guardrail(自動STOP閾値ではない)の明示であり、本文言も
`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が正本。

**固定ブロック追記(2026-10-27、PM-SSOT-SYNC-20、PM_GOVERNANCE違反記録の再発防止)**: (1)禁止Git操作の再掲: `git add -f`(gitignore対象の強制追加)・`git pull --rebase`・`git stash`・`amend`・`-A`は禁止(許可は`git rm --cached <path>`の追跡解除のみ)。(2)同一runの起動間隔は150秒以上、5分に3回起動しない(RESTART_STORM自発動防止)。(3)有料stageを実行する前に『そのstageがevidenceに必要か』を1行記録する(不要なFull Story TTS再生成の防止)。(4)Family別stage名の注意: X/Y/Zのrunner `--stages`一覧は各runner `--help`で確認し、`provision_shell`はZ専用(Y runnerには存在しない)。

## ユーザー指示(原文)

(該当する場合、ユーザーの承認・指示原文をそのまま引用する。)

## KPI provenance欄(KPI・Gate判定を扱う委任のみ必須、PM_GOVERNANCE 24節)

(KPI・合否数値ごとの測定経路を6区分[fresh/frozen/reuse/manual_substitution/
synthetic/production_formal_path]から明記し、混在時は件数内訳を書く。E2E自己確認
[「fresh Production初回pathを含むE2E値か」Yes/No]の欄も置く。該当しない委任は「該当なし」。)

## Opus台帳更新(Opus指摘が関係する委任のみ必須、PM_GOVERNANCE 11-5)

(`docs/pm/OPUS_FINDINGS_LEDGER.md`の関連指摘IDと、本委任での状態遷移
[RAISED→FABLE_DECIDED→IMPLEMENTED/TRIALED→EVIDENCED→CLOSEOUT_CONFIRMED]を書く。
該当しない委任は「該当なし」。)

## 事前指定Read一覧

(「ファイル:行範囲」または「Grepで位置特定→該当範囲Read」の形式で列挙する。
プレースホルダ[TBD/同上/前回と同じ等]禁止。)

## 事前指定Grep一覧+追記位置・更新位置の手順

(Grepパターンと対象パス、検出後の追記位置・更新手順を明記する。)

## 実行コマンド全文

(コマンドは引数の実値[絶対パス・具体的なフラグ値]を含めて全文で書く。
「同上」「前回と同じ」「<引数>」等のプレースホルダは禁止。実行コマンドは
`.venv\Scripts\python.exe`(またはvenv有効化後のpython)を使用する。PATH上の
素の`python`はMicrosoft Store版等の別環境を拾い回帰が誤検知する
(CONSOLIDATION-118で実証)。`run_project_regression.py --pattern`のglobは
必ず`_test`を含める(例`er003*_test_*.py`)。テスト以外のスクリプトが
import実行される事故防止(CONSOLIDATION-124)。)

## SSOT追記文

(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC等への追記文案をそのまま使用できる
形で記す。)

## Git(明示add対象・コミットメッセージ・trailer)

(明示`git add`対象ファイルの一覧、コミットメッセージ文案、末尾trailerを記す。
`-A`/`stash`/`amend`は既定で禁止。)
(SSOT編集権の有無: 本Agentが`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`の
編集権を持つか明記する。持たない場合、SSOT追記文案はRESULT_PACKETへ
記載するのみとし、SSOTファイル自体は編集・addしない。8-Y節[SSOT編集の
直列化ルール]参照。)

## 報告(RESULT_PACKET項目)

(RESULT_PACKETへ記載すべき項目を列挙する。)

Sonnetはユーザー判断の候補を`判断候補`と表記する(`USER_DECISION_REQUIRED`の
ラベルはFableだけが付ける。PM_GOVERNANCE 27-3)。
ユーザー向け最終報告は固定5節順(PM_GOVERNANCE 9-0、2026-10-05): 1結論(完了/
停止/Production反映状況/次へ進める条件)、2ユーザー判断が必要なこと(決めること/
背景/選択肢と影響/推奨と根拠、通常の技術作業は上げない)、3重要な問題・残作業
(作業ミス/仕様上の制約/未確認事項、各々解決済みかblockingかを明示)、4完了・
良好だったこと、5次の行動・費用(最後にユーザーが答える事項のみ)。技術詳細は
5節の後ろの補足へ。費用上限・STOP条件はユーザー承認値を優先し、独自に過度に
厳しい停止条件を追加しない(2026-10-05)。

---

## Fable自己チェック(送信前)

- [ ] Read一覧に行範囲/Grepパターンあり
- [ ] 追記位置手順あり
- [ ] コマンドに引数実値あり
- [ ] 禁止事項・費用上限あり
- [ ] 並行タスク衝突回避あり
- [ ] Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定[A/B/C/D/非該当]あり
- [ ] 時間見込み・並列化判断あり(主要タスク、PM_GOVERNANCE 8-X)
- [ ] 再委任の場合: 前委任のQDC記録(改善見込み・当日費用残・次の一手)あり(PM_GOVERNANCE 11-6)
- [ ] 前委任の受入記録(Gate 7、必須5項目=当初目的/最終成果物[失敗終了時含む]/証拠[ファイル:行・観測値]/一致・不一致/判定と理由。当初目的はユーザー原文から逐語引用、原文未取得は目的適合を確認済みとしない、設計準拠・テストPASSを目的適合の根拠にしない: sandwich-pm.md手順4-2)を冒頭に記載
- [ ] 費用/日次の行あり(当日既使用・残・見積、JPY0は「JPY0」のみ可、PM_GOVERNANCE 7-9)
