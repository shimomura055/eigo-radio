管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_14: iteration 6 = ユーザー
新方針10項目の実装+監査2件+29 instance×n=2再実行+Gate分類)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 到達Status・禁止事項

到達Status: `ITER6_DONE_LADDER_IMPROVED_ROOT_CAUSE_REMAINING`。
Gate=REJECTED(継続改善、詳細REPORT§15-15)。禁止事項: 削除・移動・rm・
git clean・git stash・rebase/reset/amend/force push禁止。
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`はcommit対象外。
`git add -A`禁止(パス指定add)。Production正式path(er003/er006/er009/
er010/er012/er019)への無断実装禁止。既存iteration1〜5証跡は無変更
(iteration6は`_iter6/`へ新規保存)。

## 1. 作業内容サマリ

### 作業A(¥0): 監査2件

`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`を新規作成。
Hook-aware再監査(Production HOOK_CLAUSEはchanged_scope/changed_
comparisonの2種のみ緩和、Family X/Trial双方hook_aware=False未配線、
ユーザー指摘のMeta hook実例[neg1]の実際のflagはHook-aware対象外と
机上確認)+Rewrite後QA資産棚卸し(Fact Checker A' web_search・対象文/
隣接文分離は未実装、Phase2課題として記録)。

### 作業B(¥0): 実装

`er052_open233_self_recovery_flow_runner_01.py`へ以下を追加:
- B-1丸め許容: `precheck.is_natural_rounding`+`_sanitize_dev_for_
  rounding`(floor評価直前にchanged_numberの丸め誤検出を除去)。
- B-2 floor-cited variant: `apply_floor_cited`/`floor_cited_eligible`
  (反実仮想並走測定、既存floor-strictのフロー制御は変更しない)。
- B-3最小変更ラダー: `single_text_rewrite`を①単語接続詞(新設
  `E1_MINIMAL_WORD_PROMPT_TEMPLATE`)→③1文(既存E2_GENERIC)→④段落
  (既存E2_PARAGRAPH)の順へ再設計。paired J-1は未ラダー化のまま
  (既知の限界)。
- B-4セクション役割維持: `measure_section_role_violation`
  (In one line長文化・Title/In one line数字追加・Hook縮小・
  Hook/Titleレトリックマーカー消失)、既存品質劣化検出v2の再生成
  トリガへ統合。
- B-5 Hook-aware統合: `detect_claim_section_type`+
  `apply_hook_aware_downgrade`(changed_scope単独発火のみ、
  changed_comparisonは既存floor安全装置のため意図的に対象外)。
- B-6コスト5分割: `compute_cost_breakdown_5way`。

`er052_open233_self_recovery_precheck_01.py`へ`is_natural_rounding`/
`changed_number_is_natural_rounding_only`/`extract_bare_numbers`追加。

unittest 28件新規追加(`er052_open233_self_recovery_flow_runner_01_
test_01.py`)、既存136件+新規28件=**164件全PASS**(regressionなし)。

### 作業C(¥0): iteration5事例の机上分類

iteration5の全Rewrite event(28件)を`method`フィールドで機械確認し、
ほぼ全件が段落単位(`e2_paragraph_rewrite`)から開始していたことを
確認(B-3再設計の直接的な正当化根拠)。

### 作業D(有料、Guardrail¥60): 29 instance×n=2再実行

`--groups safety,b_group,meta,hormuz,negative --n_runs 2`で実行。
累計¥60.226でGuardrail到達しTrialAbort(既存安全装置の正常停止)。
sample1 29/29完走、sample2 26/29完走(negative群3件`neg5_hormuz_
div_a2`/`neg6_smallbag_div_b1b`/`neg7_meta_prodrunner_b1b`が未完走)。
`combine_n2_measures`の自動集計は両sample完走が前提のため、26
instanceのoverlapで手動再集計した。詳細結果はREPORT§15参照。

### 作業E(¥0): 読み比べページ更新

`er052_open233_self_recovery_rewrite_compare_page_iter6_01.py`
(新規)で`user_test/open233_rewrite_compare_01/index.html`を
iteration6版へ更新。iteration5版は`index_iter5.html`として保持
(削除・移動せず)。収録4記事: `neg1_meta_b3prod_a2`(Meta hook、
item2必須指定)・`bgroup_B3`(B3因果、item4必須指定)・
`hormuz_run02_advanced`・`neg2_meta_refresh_a2`。

### 作業F: Gate分類・Closeout前チェック

REPORT§15-14/§15-15参照。Gate=REJECTED(不要Rewrite率44.44%・
real_run Escalation[n=2で2/12]が未達条件、Safety hard gate・
コストCapは達成)。

## 2. SSOT更新

- `docs/pm/design_open233_self_recovery_flow_01.md`§4-12/§4-13/§5-7/
  §6-4/§8-7/§9-1⑪/冒頭Status。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§15。
- `DECISION_LOG.md`(委任_14エントリ、OPEN-233-SELF-RECOVERY-TRIAL-01
  節末尾へ追記)。
- `OPEN_ITEMS.md`(OPEN-233行の履歴セルへ委任_14追記)。

## 3. 費用・Production安全性

作業A/B/C: ¥0。作業D: ¥60.226(smoke test¥4.7041含む、error 0)。
本委任合計¥60.226(Guardrail¥65内)。Phase累計¥222.9756+¥60.226=
**¥283.2016**/総枠¥400、残¥116.7984。

`git diff --stat`で`er003_*`/`er006_*`/`er009_*`/`er010_*`/`er012_*`/
`er019_*`および既存iteration1〜5証跡に差分なし(確認済み)。変更
対象は`er052_open233_self_recovery_flow_runner_01.py`(+test)・
`er052_open233_self_recovery_precheck_01.py`・新規
`er052_open233_self_recovery_rewrite_compare_page_iter6_01.py`・
新規`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`のみ。
API keyは環境変数のみ、保存jsonはprompt_sha256のみ記録。

## 4. USER_DECISION_REQUIRED該当有無

該当なし(6条件いずれも非該当)。Guardrail到達によるsample2部分完走
(26/29)は既存安全装置の設計どおりの正常停止であり「予算超過」には
該当しない。floor-cited/Hook-aware(changed_scope限定)はいずれも
既存安全装置を弱める方向の変更を伴わない。

## 5. 既知の限界・次委任への申し送り

1. paired J-1(JA/EN対訳ペア)は最小変更ラダー未適用のまま。item4の
   flagship例(`bgroup_B3`)自身がJA対訳ペア経由のclaimだったため、
   ラダーの恩恵を受けなかった(item4の目標はB3自身では未達成)。
2. 不要Rewriteの主因4 instance(neg1/neg2/neg3/meta_run03_advanced)は
   両sampleで完全一致し根本解消できていない(Hook-aware対象外flag・
   Stage2較正セット外汎化)。
3. real_run Escalation(n=2)はiter5比で悪化(meta_run03_standardの
   paired J-1既存挙動)。
4. floor-cited variantは`related_fact_id`依存の限界があり(実例:
   `safety_er009_changed_number`)、採用にはより広い測定・引用検出
   ロジック改善が必要。
5. OPEN_ITEMS.mdのOPEN-233行の第3カラム(Status要約セル)は本委任では
   更新していない(iter5時点の要約のまま、詳細はDECISION_LOG/REPORT
   参照)。
