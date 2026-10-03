# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_57 最終報告(逐語)

抽出元: `C:/Users/tensh/.claude/projects/C--Users-tensh-eigo-radio/f9ae115b-0305-437d-ac2d-b452b22a5e2a/subagents/agent-a32da2286eb7c3907.jsonl`(SubagentHandbackのmessageをスクリプトで抽出、改変なし)

---

## 委任_57 最終報告(OPEN-233-SELF-RECOVERY-TRIAL-01、Status=USER_DECISION_REQUIRED、費用¥0)

### (1) 結論
- A4-1を正式採用基準の適用でACCEPTABLEへ再ラベルした。Safety-critical登録は6件から5件になった。再較正の最終判定は「合格(ラベル修正後)」。
- Opus#7とPM評価、委任_55・56の最終報告を保存した。
- P-strict-closedの事前確認はFable基準を全て満たした。
  - 346行で確定→確定不能0、範囲変化0。
  - 13行中10行採用。U06・U11・U12は確定不能のまま。
  - 合成24件が期待どおり。
- Trial実装(`VS_EXPLAIN_SPLIT`、既定OFF)を入れた。有効化・採用はユーザー承認待ち。
- **エコーの有無は既存記録では検証不能(観測0件)。**
- テスト: runner単体440件OK、er052回帰484件OK、全体回帰4407件中11件失敗は基準の11件と同じで新規なし。
- 次Trial・29件横断は未開始。

### (2) 作業1
- 変更
  - `SAFETY_CRITICAL_SUB_IDS`から A4-1 を外した。
  - `CORRECT_LABEL_OVERRIDES_R3DPRIME["A4-1"]="ACCEPTABLE"`を追加した。
  - runnerの`SAFETY_CRITICAL_CLAIM_DEFS`では`expected:"ACCEPTABLE"`の監視用として残した。
  - 設計書の正解ラベル表(§7-1付近)、再分類doc、criteria docに追記した。
  - `er052_output/open233_safety_control_03/relabel_note_a41.md`を別ファイルで追加した。`results_01.json`は不変で、再実行もしていない。
- 残り5件の確認は机上確認(LLM呼び出しなし)。例2と同型のものは無く、変更なし。

| sub_id | 当てはめ | 結論 |
|---|---|---|
| B3 | 因果の創作 | 重大のまま |
| B4-a | 未確認の仕組み・設計意図の追加 | 重大のまま |
| A2A3-0 | 主体の取り違え | 重大のまま |
| A4-0 | やり取りの相手の取り違え | 重大のまま |
| A5-0 | 時期・経過の創作 | 重大のまま |

- 再較正の最終判定は合格(ラベル修正後)。
  - (a)Safety-critical 5claim 誤降格0
  - (b)Safety12 0/18
  - (c)Hormuz V6と同じ
  - (d)例3件期待どおり
  - (e)K16・K20 BLOCKING
  - (f)false BLOCK 0
- テスト: `TestA41MovedToMonitor57`(3件)を追加した。既存の登録集合テストも5件へ更新した。

### (3) 作業2
- `docs/pm/opus_l2_review_open233_self_recovery_07.md`に`_06.md`と同じ構成で保存した。(1)位置づけ、(2)依頼文逐語、(3)Opus全文逐語、(4)PM評価。
- `docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55_result.md`と`_56_result.md`を保存した。保存場所は既存の`_result.md`の慣習に合わせて`delegation_log/`にした。

### (4) 作業3
**エコー確認(`echo_check_01.py`)**
- 実記録の`claim_span_text`は10件で、全て単一範囲だった。
- そこで`annotate_claim_span_identity`と同じ再構成を行った。BLOCKING指摘136件のうち複数範囲は2件で、どちらも最終周回のため次周回がなかった。
- 結論は「エコーの有無は検証不能(観測0件)」。`claim_span_text`は変更していない。

**再生(`check_02.py`、結果`results_02.json`・`cases_02.csv`)**
- 自己検証として、現行照合のコピーが委任_49の再生と346行で不一致0であることを確認した。

| 346行の遷移 | 件数 |
|---|---|
| 確定→確定(同じ範囲) | 320 |
| 確定→確定不能 | 0 |
| 範囲変化 | 0 |
| 確定不能→確定 | 10 |
| 理由変化 | 0 |
| 確定不能→確定不能 | 16 |

- 確定不能→確定の10行は、U01、U02×5、U08、U09、U10、U13。
- 確定不能のままの16は、数値検査12、U05、U06、U11、U12。
- 13行のうち、U06は`remainder_too_long`(英語14語)で拒否された。U11は`dangling_position:headline,one_line`、U12は`dangling_position:headline`で拒否された。
- 委任_53対照腕62件は全て確定済みのままで、同じ範囲だった。
- 非BLOCKING K1の確定不能6行は、1行のみ確定した(P-strictでは4行)。3行は長い説明文で拒否された。安全側に倒れており、有効化時に注意する点として報告する。
- `same_fact_id_locations`14件は、確定不能→確定が1件(P-strictでは5件)、確定不能のまま11件、確定済み不変2件。
- 合成24件は全て期待どおり。
  - 採用の対照: 3件。
  - 確定不能: 対比の引用(S1、S1b、S1c)、記事内発言引用(S2)、日本語「」(S3a、S3b)、paragraph 5・closing・elsewhere(S4a〜c)、断片の直前・直後に連続(S5a、S5b)、英語6語以上(S6)、日本語11文字以上(S7)、宙に浮いた見出し名指し(S8)など。
- 判定3-3は合格で、作業4へ進んだ。

### (5) 作業4
**実装の要点**(`er052_open233_self_recovery_flow_runner_01.py`)
- `VS_EXPLAIN_SPLIT`(既定False、CLI `--vs-explain-split`)、`vs_explain_split_resolve`、`_resolve_claim_string`(照合の入口、1箇所)を追加した。
- 既存の照合は`_resolve_claim_string_base`へ改名した(中身は不変)。
- ONのときだけ、既存照合で確定不能(explanatory_mixed/mismatch/label_only)の場合に試す。multi_match・empty・no_textは試さない。
- 英語本文のみ。拒否時も`reason`は既存の値のままにして、下流の分岐を変えない。拒否理由コード`explain_split_rejected:<理由>`は`explain_split.reason`へ記録する。
  - これは委任文の「理由コード」の置き場について私が選んだ設計。変更が必要なら指示してほしい。
- 採用時は`level="P:<断片数>"`とし、`explain_split`に採用した断片と`dropped_remainders`(捨てた残り)を記録する。
- `handoff["resolution"]`へ`explain_split`を記録する(ONで存在するときのみ)。
- `switches`記録へ`VS_EXPLAIN_SPLIT`を追加する(ONのときのみ)。
- 複数範囲の`claim_span_text`は変更していない。

**定数(逐語)**
- `VS_EXPLAIN_CONTRAST_REF_EN_RE = \b(ledger|source|but|instead|not|should|however|rather|whereas|contrary|versus)\b|n't`(大文字小文字無視)
- `VS_EXPLAIN_CONTRAST_REF_JA_RE = 台帳|原文|ではなく|ではない|しかし|べき|一方|対して|ところが`
- `VS_EXPLAIN_POSITION_REJECT_RE = \b(paragraph|closing|elsewhere|section|ending|conclusion)\b|段落|末尾|結び`
- 長さ制限: 残り1区間が英語6語以上、または日本語(CJK含む)11文字以上で拒否。記事の逐語として拒否するのは3語以上(日本語は8文字以上)。
- 見出し・In one line・冒頭を名指しする残りは、どの断片もその要素と重ならなければ拒否する(P-strictの拒否を維持)。

**テストと回帰**
- 新規は`TestExplainSplitStrictClosed57`の9件。U01〜U13の実文字列(採用10・確定不能3)、合成24件、OFFで346行が`_resolve_claim_string_base`と同一、ONで確定済みの範囲不変・新規確定10、legacy無影響などを含む。
- runner単体は440件OK(委任_55時点の431件から増加)。
- er052回帰は484件OK。
- 全体回帰は4407件中11件失敗で、基準の11件と同じ。er052は全てOK。
  - 失敗した基準11件のファイル: er003_test_bad、er003_test_p2j_investigate、er011_open112、er015_standard_a2_6000、er025_b1b、er040、er043。
- `budget_state_c233an_42_rep22.json`の書き換えは`git checkout`で戻した。rep19のM表示は開始時から存在しており、触っていない。

### (6) SSOT更新箇所
- `DECISION_LOG.md`末尾に委任_55〜57のエントリを追加した。
- `OPEN_ITEMS.md`のOPEN-233行Statusを更新した。旧Statusは「旧Status参考(委任_55)」として残した。
- `OPEN_ITEMS.md`のOPEN-233-A1-PROD行に必須確認とP-strict-closedの扱いを追記した。
- `docs/pm/REPORT_LEDGER.md`のOPEN-233行の備考と、Opus発火列(L2 条件A #7)を更新した。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`に§40を追加した。
- `docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`に§5を追加した。
- `docs/pm/ACTIVE_TASK.md`をUSER_DECISION_REQUIREDに更新した(addしていない)。
- `docs/pm/RESULT_PACKET.md`に短い要約を書いた(addしていない)。

### (7) ユーザーへ戻す条件に当たる事実
- 判断A: P-strict-closedを次Trialで有効化し、Production配線時の構成要素に含めるか。Fable推奨は有効化。
  - 材料: エコーが検証不能で、非BLOCKING K1の採用が減っている。
- 判断B: K19が`changed_comparison`のfloorでBLOCKINGになる残りを受容するか。Fable推奨は受容。
- 判断C: 次Trial(5記事×2レベル)の前に行う限定flow確認と29件横断(1回)の実施可否。
- 上記以外の「前提が外れた」事実はなかった。例2と同型の2件目のSafety-critical登録も無かった。

### (8) T-0・commit・push・raw URL・その他
- T-0: 保存先は`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_57.md`。`check_delegation_prompt.py`の結果は**FAIL**(「実行コマンド全文」節が見つからない)。
  - 原因: 保存時に実行コマンド節を要旨化したため。委任文を全文そのまま保存するというT-0の指示を満たしていない。FAILでも作業は継続する取り決めのため記録のみ。
- 1回目commit: `8057cf72`(push済み)。委任_55の未commit分、作業1・2、委任_56の成果物を含む。
- 2回目commit: `ec012679`(push済み)。
- 一覧外のRead/確認
  - `check_01.py`の補助関数一式。
  - `er052_output`のinstance JSON構造(エコー確認用)。
  - 全体回帰の出力。
  - REPORT_LEDGERのOPEN-233行。
  - DECISION_LOGの末尾。
- 確認できたこと(実行結果あり): 上記の件数・テスト結果は全て実行して得た値。
- 推測: 残りSafety-critical 5件の「重大のまま」は、設計書・較正コードの対象文要旨に基づく机上確認。エコーの有無は検証不能で、有効化時のrun実測で確認する余地がある。

raw URL
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_flow_runner_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_flow_runner_01_test_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_r3dprime_calibration_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_explanatory_mixed_offline_check_01/check_02.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_explanatory_mixed_offline_check_01/echo_check_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_explanatory_mixed_offline_check_01/results_02.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_safety_control_03/relabel_note_a41.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/opus_l2_review_open233_self_recovery_07.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/REPORT_LEDGER.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/design_open233_explanatory_mixed_countermeasures_01.md
