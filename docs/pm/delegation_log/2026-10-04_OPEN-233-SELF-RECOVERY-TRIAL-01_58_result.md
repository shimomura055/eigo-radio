# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_58 最終報告(逐語)

抽出元: `C:/Users/tensh/.claude/projects/C--Users-tensh-eigo-radio/f9ae115b-0305-437d-ac2d-b452b22a5e2a/subagents/agent-a6d5685b1530a2221.jsonl`(SubagentHandbackのmessageをスクリプトで抽出、改変なし)

---

## 委任_58 報告(OPEN-233-SELF-RECOVERY-TRIAL-01)

設計と整理のみ完了。実装はしていません。コード・Prompt・テストは無変更、LLM/APIも使っておらず費用は¥0です。commit `a1adc439` を origin/main へ push 済みです。

### (1) 結論

- **原因の内訳(8種類)**: 8件すべてで、floorがCheckerのフラグだけを根拠にBLOCKINGへ昇格させていました(裏取りなし)。
  - 列挙の波及の残骸が6種類(K08・K09・K11・K12・K15・K17)です。委任_35(2026-10-01 15:33)で是正済みです。
  - Checkerが直接フラグを立てたのは2種類(K13・K14)で、現行コードでも再発し得ます。K19(`changed_comparison`)も同じ型です。
  - 是正後のrun(rep20〜22)では、floor発火14件のうち、LLMが非BLOCKINGなのにfloorだけでBLOCKINGになったのは1件(rep21の`changed_number`)だけです。
  - K04はfloorが発火していません(LLM判定のみ)。
- **重要な所見**: floorだけが重大な誤りを止めた記録が2件あります。
  - Safety-critical A4-0: 13記録中1件(iter5、LLMはACCEPTABLE)
  - K16: 19記録中1件(rep9、LLMはQUALITY)
  - 役職名詞に絡む `changed_actor` は、K13・K14(軽微以下)とA4-0・K18(重大)を字面で区別できません。
- **推奨案はF4**: F1(3値の裏取り付きfloor)に、決定不能分だけの独立再判定を加えます。
  - 裏取りで不一致が確認できたもの(CONFIRMED)はBLOCKINGを維持します。
  - 整合の証拠があるもの(CLEARED)は解放します。K19が該当します。
  - 決まらないもの(UNDETERMINED)は現行どおりfloor維持が既定です。
  - 独立再判定(Stage 2をフラグを見せずにもう1回呼び、どちらかがBLOCKINGならBLOCKING)は、**Opus承認後にのみ有効化**します。
  - どの案も現行より厳しくなる箇所はありません。
- **F2(階層化)は不採用推奨**です。11件を解放し、重大な2件(A4-0・K16)が止まらなくなります。
- **Safety対照のオフライン再生**(決定論部分のみ、LLMは再実行していません):
  - F1/F4は解放0件です。対象はSafety12のfloorフラグ付き6件、Safety-critical 5件、A4-0、K16です。
  - F2は11件を解放します。
  - Hormuz NG5はStage 2単体の対照でStage 1のフラグが無く、floor変更の影響外です。実flowでの確認は「要実測」です。
- **「動機」の仕様不一致は、整理で解消できます**(`USER_DECISION_REQUIRED`にはしません)。
  - 「動機の帰属=軽微」は、Ledger確認済みの事象に理由づけを添えるだけで、新しい具体的事実を加えないものです。
  - 「動機の創作=重大」は、Ledgerに無い意図・仕組みを新事実として書くものです。
  - ユーザー自身が2026-09-30の同じ指示で両方を述べているので、別の事象です。
  - V7は既存より厳しくなっていません(rubric_diff.mdで逐語確認)。
- **限定flowの費用**: 6 instance×n=2=12 runで¥12〜26(F4採用なら再判定+¥1〜3、上限案¥30)。29件横断は¥35〜60(上限案¥70)です。

### (2) 作業2-1の表の要約

詳細は `docs/pm/design_open233_floor_alignment_01.md` §2-1(原文・Ledger逐語・フラグ・LLM判定・最終判定を含む)です。

| 種類 | 発火した機械判定 | LLM判定→最終 | 正式基準 | 区分 |
|---|---|---|---|---|
| K04 | なし(floor不発) | BLOCKING→BLOCKING(V6時) | 軽微 | floorの問題ではない |
| K08・K09・K11・K12 | `apply_floor`(`changed_actor`)+列挙の波及 | ACCEPTABLE/QUALITY→BLOCKING | 問題なし/軽微 | 是正済み。元フラグはK13型の過剰 |
| K13 | `apply_floor`(直接) | ACCEPTABLE→BLOCKING | 問題なし | (a)+(b)、再発し得る |
| K14 | `apply_floor`(直接) | ACCEPTABLE→BLOCKING | 問題なし | (a)+(b)、再発し得る |
| K15・K17 | `apply_floor`(`changed_time`)+列挙の波及 | ACCEPTABLE/QUALITY→BLOCKING | 問題なし/軽微 | 元の文K16は重大で維持が正しい |
| K19 | `apply_floor`(`changed_comparison`) | BLOCKING→BLOCKING | 軽微(ユーザー決定) | (a)+(b)、F1でCLEARED |

- K13・K14のCheckerのissue文自体が、言い換えや一般化を主体の置換として扱っています。
- K14の原文はHF-002の言い換えです。ただし同じ構造のK18は重大で、フラグだけでは区別できません。
- 件数: 全1,014 claim記録のうち、floorが発火したのは258件です。floor単独は54件(Ledger取得可能な250件中)で、その内訳は列挙複製36件(是正済み)と非列挙18件です。

### (3) 設計案の比較

| 案 | 内容 | 8種類+K19 | Safety対照(決定論部分) | 評価 |
|---|---|---|---|---|
| F1 | 3値の裏取り。決定不能はfloor維持 | K19のみ解消。K13・K14は未解消 | 解放0 | 安全だが限定的 |
| F2 | actor・comparison・timeをLLMへ | 全解消 | 11件解放。A4-0・K16が止まらなくなる | 不採用推奨 |
| F3 | Stage 2へフラグ再提示 | 要実測 | 要実測 | priming再発の恐れ(委任_16の前例) |
| F4 | F1+決定不能分の独立再判定(OR) | K13・K14も解放され得る(要実測) | 決定論部分は解放0 | **推奨**。Safety方針の変更に当たり得る |

- F4は、記録上のLLM判定率(A4-0 12/13、K16 18/19)から、両方が見逃す確率を約0.6%・0.3%と見積もっています。呼び出しが独立でない可能性があるため、目安にとどまります。
- 再較正の計画は約¥8〜10(上限¥15)です。委任_55の実測(26 call、¥4.37)を単価に使っています。

### (4) 作業3の結論と案文

- **結論**: 解消可です。
- **案文(2) V7(1)(イ)**: 「(イ)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値**・仕組み・意図**)を加えている」。書き漏れの補足で、既存のBLOCKING対象は変わりません。
- **案文(1) rubricのQUALITY行**: 「…Ledgerが確認済みの事象同士を結ぶ関係付け(因果接続詞・理由づけ・動機の帰属・強調)が加わっているが、新しい具体的事実(人物・出来事・発言・数値・仕組み・意図)は増えていない。」
- **案文(3) 設計書§0-2**: 「未確認の人物・行動・仕組み・数字の追加(Ledgerに根拠のない人物・組織の意図・動機の断定を含む。…新しい具体的事実を加えない理由づけは含まない)」
- **残る小さな論点(1点)**: B1-cは旧BLOCKINGの根拠がHF-011のnotes_for_writer(因果推論の明示禁止)でした。委任_12でQUALITYに再ラベルされましたが、「notesが禁じた断定=BLOCKING」との整合は文言上未整理です。実害は未確認です。Opusが整理で解消できると判断しなければ、ここだけ`USER_DECISION_REQUIRED`候補になります。

### (5) 作業4の計画

詳細は設計書§5です。

- **対象instance**: `meta_run03_standard`、`hormuz_run03_standard`、`neg3_hormuz_prodrunner_b1b`、`safety_A4`、`safety_A2A3`、`safety_er009_changed_number`。n=2、比較対象はrep22・rep21です。
- **有効にするスイッチ**: `HANDOFF_MODE=violation_span`、`VS_MATCH_EXT=True`、`VS_EXPLAIN_SPLIT=True`、`JA_MODE=english_only`、rubric V7、機械判定修正版。スイッチ名の存在はrunnerで確認しました。
- **合格基準**: false PASS=0、floor単独BLOCKING(非列挙)が0〜1件/run以下、不要Rewriteとstage4(Human Review)がrep22以下、最小Rewrite違反0、JA処理の呼び出し0(日本語本文・タイトルのハッシュ不変)。
- **29件へ進まない条件**: false PASS≥1、Safety-critical誤降格≥1、Human Reviewがrep22超、費用が上限の1.5倍超など。
- **確認できない点**: 「古い日本語から英語を再生成するProduction経路の再検査」はTrial runnerでは再現できません。Production配線時のGate 3で確認する必要があります。

### (6) Opusに見てほしい論点

1. F1の3値設計。CLEARED条件、特に事実側に方向語が両方向あるときの解放が緩すぎないか。
2. F4の独立再判定(OR)はSafety方針の変更か。ユーザー判断事項にすべきか。A4-0・K16の救出率の推定は妥当か。
3. 役職名詞のactor(K13・K14とA4-0・K18)を字面で区別できない前提は正しいか。同時に立つフラグでの区別は有効か(n=1〜13と少ない)。
4. 固有名詞の日英別名表を実装時に入れるか。現状は訳語を「新規」と誤判定して解放されず、過剰判定が残る5件の原因です。A2A3-0のCONFIRMEDも誤判定によるものの可能性があります。
5. V7の文言「比較の差は…明確にBLOCKING」と、例「prices began to fall→QUALITY」の食い違い。文言を直すか、floor側だけで足りるか。
6. 案文(2)が既存より厳しくならないことの確認。
7. B1-cのnotes禁止の扱い(上記の残る小論点)。
8. 列挙複製元の過剰フラグ(K13型)を設計の対象に含めるか。
9. Hormuz NG5(Stage 1フラグなし)の実flow確認を、いつ限定flowに入れるか。
10. 限定flowの合格基準とn=2の妥当性。

### (7) 手続き・確認事項

- **T-0**: PASS(警告のみ。TTS関連の言及と`--budget`未言及で、本委任はTTSを伴いません)。委任文は全文逐語で保存しました。
- **commit**: `a1adc439`(10ファイル)。**push**: 済み(`ec012679..a1adc439`、競合なし)。
- 明示addしたのは次のファイルです。
  - `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`
  - `docs/pm/design_open233_floor_alignment_01.md`
  - `er052_output/open233_floor_alignment_offline_01/`(`replay_01.py`、`replay_01_stdout.txt`、`replay_01_result.json`、`K_rows.csv`)
  - 委任文とその`_check.json`
- `ACTIVE_TASK.md`と`RESULT_PACKET.md`は指示どおりaddしていません。
- SSOT: DECISION_LOG末尾にユーザー決定[3回目]を逐語記録し、Fableの受け止めと分担を追記しました。OPEN-233のStatus(旧Statusは「旧Status参考(委任_57)」として残存)と`OPEN-233-A1-PROD`行を更新しました。REPORT_LEDGERの備考とACTIVE_TASKも更新済みです。
- **一覧外Read**:
  - `er052_open233_element_trial_safety_control_02.py`(Safety12の定義)
  - `er009_ledger_deviation_recalibration_02_test.py`(同上)
  - Ledger実ファイル3つ(`verified_fact_ledger.txt`)
  - `er052_output/open233_safety_control_03/`の`results_01.json`と`budget_state_c233ao_55.json`
  - runnerの`build_target_instances`
  - 設計書§7-0-iter4周辺
- **確認できたこと**(記録・実コードによる): 各種のフラグ・floor_reason・LLM判定・列挙の有無、floorの評価順と各条件、委任_35の日時、post-fixのfloor単独件数、A4-0・K16の救出記録、オフライン再生の決定論結果、V6→V7差分、委任_55の単価。
- **推測**:
  - K12の元フラグの出所
  - 同種のフラグ過剰が今後も出ること
  - F4でK13・K14が解放される確率
  - 再判定の見逃し確率(非独立の可能性あり)
  - rubric文言と設計書§0の承認日(未特定、要確認)
- **要実測**: F3、F4の再判定効果、Hormuz NG5の実flow、日英別名表の効果、Ledger未取得の8記録(bgroup_B1、neg4/neg6_smallbag)。

次Trial(5記事×2レベル)は開始していません。USER_DECISION_REQUIREDは現時点でありません。F4採用可否はOpusレビュー後にFableが判断し、必要ならユーザーへ戻します。

主なファイル:
- `C:\Users\tensh\eigo-radio\docs\pm\design_open233_floor_alignment_01.md`
- `C:\Users\tensh\eigo-radio\er052_output\open233_floor_alignment_offline_01\replay_01.py`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md`

raw URL:
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/design_open233_floor_alignment_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_floor_alignment_offline_01/replay_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_floor_alignment_offline_01/replay_01_stdout.txt
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_floor_alignment_offline_01/replay_01_result.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_floor_alignment_offline_01/K_rows.csv
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/REPORT_LEDGER.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md_check.json
