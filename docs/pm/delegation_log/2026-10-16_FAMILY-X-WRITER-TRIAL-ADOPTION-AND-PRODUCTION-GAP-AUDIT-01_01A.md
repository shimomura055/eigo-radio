# 委任文(全文保存) FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 委任_01A

## 管理ID

`FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01` 委任_01A(**read-only監査 Part A**: B3→R2 Sol統一の実装・runtime照合+ユーザー指示原文の保存)。並行: 同監査の委任_01B(Writer関連Trial棚卸し、read-only)・委任_01C(Prompt本文/retry・fallback経路/Dangling、read-only)、およびAUW 委任_13(専用worktree `C:\Users\tensh\eigo-radio-a3`で実装中。main dirの`er078_*`/`er003_*`/`er006/007`等を編集しない)。**本委任はファイル編集・Git操作・有料API・Production変更を一切行わない。** 新規作成=監査文書Part A、RESULT_PACKET_FXWA1A.md、委任文保存、ユーザー指示原文保存のみ。

## 性質/到達上限Status/禁止事項
- 性質: 監査(read-only、JPY0)。到達上限Status: `PART_A_COMPLETE`(全体は委任_02でAUDIT_COMPLETE)。
- 禁止: 有料Trial、新Prompt/仕様候補の検証、Production code/Prompt変更、CoffeeのResearch/記事/音声生成、未承認仕様の採用、Open Itemの独断close、**未確認事項を推測でPASS扱いすること**(GitHubから確認できない実行証拠は「未確認」)、既存runtime evidenceの無駄な再取得(API呼出禁止)、Git操作(commitは委任_02)。
- Opus独立技術レビューGate(11-3): 本委任は非該当(Fableが全体に対し任意レビューを検討)。
- 時間見込み: 60〜90分。並列化: Part A/B/Cは独立・並列。
- 費用/日次: JPY0。承認区分: C(ユーザー2026-10-16指示によりAudit承認済み)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`check_delegation_prompt.py`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。保存先=本ファイル(全文)+`..._USER.md`(ユーザー指示原文、冒頭1行「2026-10-16 ユーザー指示原文(Fable受領)」)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示(本委任はTTSなし)。
T-3: 費用上限[Cap]なし(JPY0)。

## 事前指定Read一覧(Part A: B3→R2 Sol統一)
- CURRENT_SPEC.md: Grep `FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01`/`gpt-6.1-sol`/`B3`/`R0`/`R1`/`R2`/`Luna`/`Astra`(現行と履歴記載を区別して行番号記録)。
- DECISION_LOG.md: Grep `SOL61`/`2026-10-11`かつ`Sol`(ユーザー承認原文、逐語・行番号)。
- er053_output/sol61_production_wiring_01/runtime_evidence_01.md 全文。
- git show --stat adb15c30 と git log --oneline -S"gpt-6.1-sol" -- <Writer関連py>。
- Production code: Grep全repo *.py `gpt-6.1-sol`/`model_id`/`WRITER_MODEL`/`B3_MODEL`/`R1_MODEL`/`R2_MODEL`/`resolve_model`/`luna`/`astra` → B3/R0/R1/R2各工程のモデル決定関数(ファイル:行)、既定値、env/flag上書き経路、regeneration/retry/fallback/resume(Local Rewrite・self recovery・precheck retry・resume再実行を含む)で別既定へ戻る経路の有無。
- 入出力契約: Grep `r1_raw`/`R1 raw`/`r2_input`/`notes_for_writer`/`fact_lock`。
- 既存記事の実証跡: er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/等の audit/raw_usage_log.jsonl / writer_result.json 等、10月以降のFamily X run(Glob er0*_output/**/writer_result.json、新しい順3件まで)。

## 追記位置/実行コマンド/SSOT/Git
- 新規作成のみ: docs/research/FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01/PART_A_SOL_ROUTING_01.md。既存ファイルへの追記なし。
- Python実行はread-only集計のみ(.venv\Scripts\python.exe -I)。LLM/TTS/ASR呼出なし。
- SSOT編集権なし。Git操作なし(委任_02で一括commit)。

## 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET_FXWA1A.md。Part A文書構成: §1 承認原文(逐語・出典行)/§2 CURRENT_SPEC現行記載と履歴記載の区別/§3 工程別routing表(B3/R0/R1/R2 × 初回/retry/fallback/regeneration/resume/Local Rewrite/self recovery)/§4 入出力契約の実装確認/§5 runtime evidence(確認済み(出典)/未確認)/§6 Writer品質改善Prompt欠落の予備確認/§7 判定と未確認事項/§8 Fable確認要の箇所/§9 T-0結果・所要・受入記録5項目。

## ユーザー指示(原文)

# Claude Code／Fableへの指示
## Family X：B3・Writer改善仕様の採用漏れ／Production反映漏れ監査

**管理ID：FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01**

**現在Status：AUDIT_REQUIRED**

**今回の到達点：AUDIT_COMPLETE／必要事項のUSER_DECISION_REQUIRED提示**

**Production変更・追加Trial・Coffee再生成：禁止**

## 1. 目的

2026年10月以降を中心に、Family XのResearch・Fact Ledger・B3・日本語Writer・英語化・Standard難易度調整について、過去のTrial結果と正式Production仕様を突合する。

特に、以下の問題がないか確認する。

1. 良好なTrial結果が出たのに、ユーザーへ採否を確認せずOpen Itemに放置されている。
2. ユーザーが正式採用したのに、Production初回経路へ反映されていない。
3. Production初回経路にはあるが、retry／fallback／regenerationで旧仕様に戻る。
4. Promptの改善成果がTrial用コードにだけ存在する。
5. 新しい仕様が承認済み仕様と競合・矛盾している。
6. 過去のユーザー決定が、後続の別仕様・モデル変更によって意図せず失われている。

目的は単なるOpen Item整理ではない。

**良いTrial成果がFamily Xの実際の記事品質に反映されているかを確認すること。**

## 2. 最重点確認：B3→R2

2026年10月11日の承認済み構成は以下。

- B3：gpt-6.1-sol
- W-1 R0：gpt-6.1-sol
- R1：gpt-6.1-sol
- R2：gpt-6.1-sol

CURRENT_SPECでは`PRODUCTION_WIRED`と記録されている。

既存証跡：
- `FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01`
- merge `adb15c30`
- `er053_output/sol61_production_wiring_01/runtime_evidence_01.md`

これを起点に以下を確認する。

- 現在のmainでも正式初回経路がSolを使用するか。
- 実際のB3／R0／R1／R2それぞれのrouting・model_id証跡。
- R2入力がR1 rawである等、承認済み入出力契約の維持。
- regeneration／retry／fallback／resumeで旧モデルに戻らないか。
- 旧CURRENT_SPECに残るLuna／Astraの履歴記載を、誤って現行仕様として読んでいないか。
- モデル変更に伴って従来のWriter品質改善Promptが欠落していないか。

既に確認済みのruntime evidenceを無駄に再取得しない。GitHubから確認できない実行証拠は「未確認」とする。

## 3. Writer関連Trialの全件棚卸し

対象は10月1日〜16日のTrialを中心とし、それ以前でも現在のFamily X正式仕様に関係する承認済み改善を含める。

少なくとも以下を確認する。

- B3 Storyline／Fact Selection／Brief構造改善
- Fact台帳・notes_for_writer・Writerへの情報引き渡し
- B3 deterministic producer・Fact Lock入力契約
- W-1 R0 Writer Prompt
- R1／R2 Entertainment Revision
- Writerの具体性・自然さ・エンターテイメント性改善
- AN3 Concreteness Control
- Fact誤読・意味反転・曖昧表現対策（OPEN-233関連）
- Self Recovery・Rewrite改善
- Precheck誤検出対策（OPEN-238）
- Writerモデル配置・Luna／Astra／Sol比較
- Fact Lock／Astra E2E Trial
- 英語Advanced生成・Standard難易度調整
- Writer品質評価・QA・Risk Flaggerへの連携

上記にない関連Trialも、Git履歴・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・REPORT_LEDGER・委任ログから拾う。

名称に「TRIAL」が付いていない検証や、ユーザー個別指示による改善も対象とする。

## 4. Trialごとの判定

各Trialについて以下を記録する。

| 項目 | 必須内容 |
|---|---|
| 管理ID | Trial／仕様の識別子 |
| 目的 | 何の品質問題を改善したか |
| Trial結果 | 成果・制約・不合格要素 |
| Trial判定 | REJECTED／VALIDATED／USER_DECISION_REQUIRED |
| ユーザー判断 | 正式採用／不採用／明示的defer／未提示 |
| 正式仕様 | CURRENT_SPECの該当箇所 |
| Production実装 | 初回・retry・fallback・regeneration |
| runtime evidence | 実行済みか、どの工程を確認したか |
| 現在Status | APPROVED_FOR_PRODUCTION／PRODUCTION_WIRED等 |
| 問題 | 判断漏れ／配線漏れ／仕様競合／問題なし |
| 必要対応 | 開発側是正／ユーザー判断／対応不要 |

**Open Itemに載っていること自体を、ユーザーが意図的に保留した証拠として扱わない。**

必ず元のユーザー判断を確認する。Repoに逐語記録がなければ「判断証拠なし」とし、勝手に正式採用・不採用を決めない。

## 5. 重点的に発見する問題

### A. VALIDATEDの放置

Trial成果が良好だったのに、採否判断を依頼していないもの。

### B. APPROVEDの未配線

ユーザーが採用したが、Production正式経路に存在しない、またはDEV／Trialにしかないもの。

### C. 部分配線

初回のみ反映され、retry・fallback・再生成時に旧仕様へ戻るもの。

### D. 仕様の上書き・消失

新しいモデル配置やWriter改修で、過去の承認済み改善が失われたもの。

### E. Dangling Reference

後段Prompt・Validatorが、初回Writerに存在しない原則や未承認仕様を参照しているもの。

### F. 承認済み仕様と完成品の不一致

10月15日のCoffee監査で発見されたIn One Line・K2・M2のような、技術テストPASSでも仕様が抜け落ちる問題。

特にWriterについても、**承認済みPrompt要素と現在の実際のPrompt本文・runtime入力を比較すること。**

## 6. 既存の決定事項

以下は今回再判断を要求しない。

- Family XのB3／R0／R1／R2のSol統一。
- Family X正式Writerの承認済みFact Lock構造。
- CoffeeをResearchから全面再制作すること。
- Coffeeを代表記事としてFamily X共通Production仕様を完成させること。
- KP候補供給M2P0、選定優先順位A。
- Full Story PD06、KP英語K2、Standard日本語意味P8、Advanced英語解説P7。
- In One Lineは基本2文、必要な場合のみ3文。

これらは採用済み仕様として監査表に含め、実際の配線状況を確認する。

## 7. 今回実施してよいこと・禁止事項

**実施してよいこと**
- Repo／SSOT／Git履歴のread-only調査
- 過去Trial結果の整理
- 承認済み仕様と実装の差分分析
- 反映マトリクス・監査報告書の作成
- 根拠を伴う是正案・優先順位の提示

**実施禁止**
- 新たな有料Trial
- 新しいPromptや仕様候補の検証
- Productionコード／Promptの変更
- CoffeeのResearch／記事／音声生成
- 未承認仕様の採用
- Open Itemの独断によるclose
- 未確認事項を推測でPASS扱いすること

費用は原則JPY0。調査目的の有料LLM呼出も行わない。

## 8. 最終報告・STOP条件

非エンジニアのPMが判断できるよう、次の順で報告する。

1. **結論：Family XのWriter仕様は本当に最新か。**
2. **承認済みなのにProduction未反映の一覧。**
3. **VALIDATEDなのに採否判断が未提示の一覧。**
4. **採用済みだが部分配線・旧経路残存の一覧。**
5. **B3→R2 Sol統一の実装・runtime照合結果。**
6. **過去Trialから正式仕様への追跡マトリクス。**
7. **優先順位付き是正対象と、その影響範囲。**
8. **ユーザー判断が本当に必要な事項。**
9. **CoffeeをResearchから再制作する前に解消すべきBlocking事項。**
10. **残存するOpen Item・未報告Trial・未配線APPROVED事項。**

問題なしと判断する項目についても、参照ファイル・該当箇所・実装証拠を示す。

**監査結果を提出した時点でSTOPする。**

新たなUSER_DECISION_REQUIREDがあれば明示し、ユーザー判断なしにTrial・実装・Coffee再制作へ進まない。

FableはClaudeの「完了」報告をそのまま受け入れず、CURRENT_SPEC・ユーザー承認・Production実装・runtime evidenceと照合して独立評価すること。

(ユーザー指示原文ここまで)

## KPI provenance欄
該当なし。

## Opus台帳更新
該当なし。
