# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_55 最終報告(逐語)

抽出元: `C:/Users/tensh/.claude/projects/C--Users-tensh-eigo-radio/f9ae115b-0305-437d-ac2d-b452b22a5e2a/subagents/agent-af2959cc462bbfd90.jsonl`(SubagentHandbackのmessageをスクリプトで抽出、改変なし)

---

## 委任_55 報告(OPEN-233-SELF-RECOVERY-TRIAL-01)

### (1) 結論
- 作業1〜6を実施し、1回目commit/pushまで完了した(`6776da6b`)。
- **再較正は不合格。** 較正セット(a)のSafety-critical 6claimのうちA4-1が、n=2の両方でACCEPTABLEになった(誤降格2件)。
- 指示どおり、修正を重ねずに止めた。2回目commit/pushは未実施で、Fable判断待ち。
- 較正セット(b)〜(f)は合格基準どおり。
- `PRODUCTION_WIRED`ではない。次Trial・29件横断は開始していない。

### (2) Production非依存の確認
- 編集前の`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`は0件だった。
- 編集は`er052_open233_*`のみ。
- 機械的な安全装置は変更していない。対象は`FLOOR_FLAGS`、precheck、主体置換ガード、`MAX_CYCLES`、Hook専用rubric、`DISCLOSURE_GAP_NEGATION_RE`(否定形限定のまま)。新規テストで確認済み。

### (3) ラベル更新(旧→新)
- **Meta-1/Meta-2(K04):** BLOCKING(Safety-critical)→QUALITY。
  - r3dの`SAFETY_CRITICAL_SUB_IDS`から除外した(8件→6件)。
  - runnerの`SAFETY_CRITICAL_CLAIM_DEFS`には`expected:"QUALITY"`の監視用として残した。
  - `detect_safety_critical_misdowngrades`と`compute_residual_at_pass`の対象外になった(テスト済み)。
  - 監視用に`detect_over_quality_monitor_blocks`を追加した(記録専用)。
- **K10(「They enjoyed…」):** BLOCKING→ACCEPTABLE。
- **K19(`prices began to fall`):** BLOCKING(境界)→QUALITY。
- **K01〜K23(再分類docの表に合わせた更新):**
  - ACCEPTABLE: K01、K08、K09、K12〜K15、K23
  - QUALITY: K02、K03、K05〜K07、K11、K17
  - BLOCKING(変更なし): K16、K18、K20〜K22
- **再分類doc集計:** 重大5、軽微9、問題なし9。真の重大見逃し0/23(旧1/23)、過剰品質18/23。20種類換算は案Aが0/20、案Bが0/18。
- **行番号(設計書):**
  - 1回目commit時点では、§7-0-iter33が3711行、7-1表のMeta行が3748行だった。
  - §4-26追加後の現在は、§7-0-iter33が3754行、§4-26が1646行。

### (4) rubric差分(逐語は`er052_output/open233_safety_control_03/rubric_diff.md`)
- body rubricをV6からV7へ切り替えた。V7はV6へ追記する形で、V4〜V6は残している。
- V7の内容:
  - 3区分の定義(ユーザー原文)。
  - (1)条件つき→断定。核心の主張まで断定する、新しい具体的事実を加える、`notes_for_writer`が禁じる断定をする、のいずれかならBLOCKING。核心に留保が残り帰属が保たれていればQUALITY。
  - (2)自然な推論は、否定形・肯定形とも新しい具体的事実がなければACCEPTABLE。この場合、「内心を断定する記述」のBLOCKING条件は適用しない。
  - (3)迷う場合は「重大な誤解につながるか」で決める。数値・主体・否定・比較・時期の差は対象外で、機械的にBLOCKING。
  - 判定済みの例3行。
- Stage 2 productionには`MATERIALITY_RUBRIC_V7`を追加した。「迷えばBLOCKING」の1行だけを置換し、「動機の帰属=QUALITY」は変更していない。旧版は定数として残している。

### (5) 再較正の集計と合否基準への当てはめ(判定はFable)
Stage 2単体、n=2、26 call。

| 較正セット | 結果 |
|---|---|
| (a) Safety-critical 6claim | **誤降格2件(A4-1が2/2 ACCEPTABLE)。** B3・B4-a・A2A3-0・A4-0・A5-0は2/2 BLOCKING |
| (b) Safety12 | 誤降格0/18 |
| (c) Hormuz許容5/NG5 | 10件とも、V6(委任_33、n=1)と合否が同じ。許容側のラベルはQUALITYからACCEPTABLE寄りに動いた |
| (d) 新しい例3件 | 例1 QUALITY、例2 ACCEPTABLE、K19 QUALITY(各2/2、期待どおり) |
| (e) K16・K20(B4-a型) | 2/2 BLOCKING。A2A3-0とB4-aは(a)と同一claimなので(a)を参照した |
| (f) 負例K11〜K13 | false BLOCK 0(全て2/2 ACCEPTABLE) |

**A4-1の原因切り分け**(診断、n=1×7変種、`ablation_a41/`、rubricの修正ではない):

| 変種 | A4-1 |
|---|---|
| V7全体 | ACCEPTABLE |
| V7から(2)の段落を除く | ACCEPTABLE |
| V7から(2)内の「内心の断定にBLOCKINGを適用しない」一文を除く | ACCEPTABLE |
| V7から例3行を除く | ACCEPTABLE |
| V7から(3)を除く | ACCEPTABLE |
| V6+3区分の定義のみ | BLOCKING |
| V6+(2)のみ | ACCEPTABLE |
| V6+(3)のみ | BLOCKING |

- (2)の段落と例2の行が、それぞれ単独でA4-1をACCEPTABLEへ寄せる。両者は冗長で、片方を除いても解消しない。(3)と3区分の定義は単独では寄せない。以上はn=1なので示唆に留まる。
- A4-1の対象文は`people who thought they were speaking with AI were actually speaking with human staff`と`That was what people thought as they spoke.`。ユーザー決定の例2やK23と同型で、V7が例2どおりに判定した結果とも読める。つまり、A4-1をSafety-criticalとする旧ラベル自体が新しい線引きと食い違っている可能性がある。ただし対象文の後半には事実の主張も含まれる。
- 選択肢(実装していない。Fable/ユーザー判断)は次の3つ。
  - (イ)A4-1のラベルを新しい線引きに合わせて再判定する。
  - (ロ)V7の(2)の範囲を狭める。
  - (ハ)別の機械的な仕組みで守る。
  - いずれもpriming(rubric文の追加が別claimの判定へ波及する現象)に注意して再較正が必要。

**費用**
- 再較正(probe含む): ¥4.3666(26 call)
- 診断: ¥2.1157
- 本委任計: ¥6.4823。Guardrail ¥15の範囲内で、暴走の兆候はなし。
- Phase累計: ¥536.4930(上限¥900、残¥363.5070)

### (6) テスト・回帰
- runner単体: 428件OK。新規10件(Meta監視用移行5件、V7の線引き5件)。既存3テストはMeta文を使うため、合成のSafety-critical定義に差し替えた。
- `er052*_test_*.py`回帰: 472件passed。
- 全体回帰: 4395件で、passed 4384、failed 6、errors 5。
  - これは委任_42・49・54の基準11件と同一で、新規の失敗はない。
  - 回帰で書き換わった`budget_state_c233an_42_rep22.json`は`git checkout`で戻した。
  - 既存のrep19等のM差分には触れていない。

### (7) SSOT更新箇所(未commit、working treeに反映済み)
- `DECISION_LOG.md`: 17610行付近に新エントリ(ユーザー原文を全文逐語、Fableの受け止めと分担)。**commit済み**。
- `CURRENT_SPEC.md`: 2338行〜に新節を追加。既存の該当節がなかったため、Model Routing Contract節の次に新設した。
- `OPEN_ITEMS.md`:
  - OPEN-233の新Statusを662行に追加(旧Status参考(委任_54)として旧Statusを残した)。
  - `OPEN-233-A1-PROD`行は726行(本文更新と、英語だけ修正の接続仕様を次Actionへ追記)。
- `docs/pm/REPORT_LEDGER.md` 115行: 備考に追記。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §39: 4045行〜。
- 設計書の§4-26(1646行)、§7-0-iter33(3754行)。**commit済み**。
- `docs/pm/ACTIVE_TASK.md`と`docs/pm/RESULT_PACKET.md`は更新済み(addしない)。

### (8) ユーザー/Fableへ戻す条件に当たる事実
- **再較正で外れた:** あり。(a)のA4-1が2/2 ACCEPTABLEで不合格。
- **機械的安全装置の変更が必要になった:** 変更はしていないが、次の食い違いが残っている。
  - K19はユーザー決定でQUALITYだが、`changed_comparison`のfloorが不変。Checkerがcomparisonを立てた実行では、LLM判定がQUALITYでもfloorでBLOCKINGになる。
  - floorからK19を外すかどうかは、機械的な安全装置を緩める変更なので、ユーザー判断事項。
- **Production変更の必要:** なし。
- **その他の未解決:**
  - 「動機の帰属=QUALITY」と§0-2・K20〜K22の食い違いが残っている。
  - `DISCLOSURE_GAP_NEGATION_RE`は否定形限定のまま。

### (9) T-0・commit・push・差異・確認区分
- **T-0:** PASS(`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55.md_check.json`)。
- **1回目commit/push:** `6776da6b`。
  - 含めたもの: `DECISION_LOG.md`、runner、runnerテスト、Stage 2 calibration/production、`er052_open233_self_recovery_r3dprime_calibration_01.py`、criteria doc、再分類doc、設計書(§7-0-iter33)、委任ログ`_55.md`と`_check.json`。
  - raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
  - raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_stage2_calibration_01.py
  - raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_self_recovery_flow_runner_01.py
  - raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/open233_materiality_criteria_2026-10-03.md
- **2回目commitは再較正の不合格のため実施していない。** 理由は、指示の「再較正の不合格があれば自動解決せず報告して止まる」と、CLAUDE.mdの「動作確認に失敗したらユーザー確認」。以下は明示addの対象(Fable確認後):
  - `er052_open233_element_trial_safety_control_05.py`
  - `er052_open233_safety_control_03_ablation_a41.py`
  - `er052_output/open233_safety_control_03/`
  - `CURRENT_SPEC.md`
  - `OPEN_ITEMS.md`
  - `docs/pm/REPORT_LEDGER.md`
  - `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`
  - 設計書の§4-26
- **委任文との差異:**
  - 委任文の`er052_open233_element_trial_safety_control_03.py`は既存の別スクリプトがあるため、`_05.py`で作成した。出力先は指定どおり`er052_output/open233_safety_control_03/`。
  - 設計書§4-23は使用済みのため§4-26にした。
  - 委任文のcommit対象に無い`r3dprime_calibration_01.py`は、Safety-critical登録の定義ファイルなので編集した。
- **一覧外Read/確認:**
  - `er052_open233_self_recovery_r3dprime_calibration_01.py`
  - `er052_open233_element_trial_safety_control_04.py`
  - `er052_open233_element_trial_safety_control_04`のV6 summary
  - `build_target_instances()`(¥0)
- **確認できたことと推測:**
  - 確認できたこと: 上記の実測値、テスト結果、`git grep`の0件。
  - 推測: A4-1のラベルが新線引きと食い違う可能性、(2)と例2が冗長に効くという読み取り(診断はn=1)。

### 主要ファイル(絶対パス)
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_calibration_01.py`
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_production_01.py`
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py`
- `C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_05.py`
- `C:\Users\tensh\eigo-radio\er052_output\open233_safety_control_03\results_01.json`
- `C:\Users\tensh\eigo-radio\er052_output\open233_safety_control_03\rubric_diff.md`
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET.md`
