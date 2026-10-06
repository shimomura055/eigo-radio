# sensor_quality_01 (JPY0、checker関数ローカル再実行。LLM未実行)

結論: Opus指摘は**真**【確認】。HC-012のnegation_polarity_mismatchはLedger行「開示なしに」の「なし」(是正案aのNEGATION_EXTRA_JA)への反応で、向き反転とは無関係。

## A. HC-012反応機構
- fact行: 「適切な開示なしに契約スタッフが…ロールバックした」。legacyマーカー=なし、是正案aマーカー=「なし」(1語)。
- 記事側: 否定語なし(unit_neg=[])。→ `(not u_neg) and all(f_negs)` が成立し発火(L529-535)。
- meta_run03_advanced HC-012根拠文4件、全run HC-012根拠32文で、英語否定語を持たない肯定文は全て是正案aで発火。
  「That was a mistake.」「Meta admits a mistake」「A Meta executive admitted the mistake」「The problem was telling users...」も発火。
- 対照(合成): 忠実な「rolled back」/反転「expanded」/反転「restored」の3文、全て同一に発火(区別なし)。
  逆に否定を含む忠実文「did not disclose」は是正案aで発火せず。

## B. fact_id別反応(negation_polarity_mismatchのみ。number/causalは新9 runで0)
| set | fact | claim数 | 反応 | ラベル | fact行否定(a/legacy) |
|---|---|---|---|---|---|
| new | MUSE-HC-012 | 32 | 13 | 重大1/問題なし12 | あり(なし)/なし |
| new | HF-007 | 17 | 10 | 問題なし10 | なし/なし |
| new | HF-003 | 11 | 8 | 問題なし8 | あり(なかっ)/あり |
| new | MUSE-HC-006 | 17 | 6 | 問題なし6 | なし/あり |
| new | HF-011 / HF-009 | 1 / 28 | 1 / 1 | 問題なし | なし/なし, なし/あり(ほどなく) |
| old | HC-012/HF-003/HF-007/HC-006 | 83/15/22/69 | 19/10/9/9 | 未ラベル | 同上 |
- 新9 run反応39件: ラベル38件=問題なし、真の重大1件(HC-012 restored)=精度1/39。旧9 run=47件。
- 反応39件の内訳(新): fact行に否定語(a)あり21(うち「なし」「なかっ」等aのみ13)、記事側に英語否定語あり+fact行肯定14、その他3。
  → 反応の大半は「fact行の否定語」か「記事の英語否定語」の有無という表層一致で、向きの正誤とは無関係。

## C. gold感度(記事誤文×Ledger行を決定論検査へ直接適用)
| ケース | negation legacy | 是正案a | 数値 | 因果 | 比較 |
|---|---|---|---|---|---|
| A5-0 put back the feature(HC-012) | 不発 | 発火(なし) | 不発 | 不発 | センサー無し |
| HC-012 restored | 不発 | 発火(なし) | 不発 | 不発 | センサー無し |
| K19 HF-009 | 発火(「ほどなく」の「なく」) | 不発 | 不発 | 不発 | センサー無し |
| K16 HF-009 | 発火(同上) | 不発 | 不発 | 不発 | センサー無し |
| D61合成「plan withdrawn, oil prices fell」 | 発火(同上) | 不発 | 不発 | 不発 | センサー無し |
- 発火/不発は全て「fact行の偶発的な否定語」の有無で決まる。HF-009ではlegacyが対比構文語「ほどなく」に偶然反応、aは除外して不発。
- B3の「and」版(HF-007)は正解ラベルがACCEPTABLE(参考。因果センサー不発は正しい)。
- 比較・方向反転用の関数はcheckerに存在しない【確認: grepで該当関数無し】。

## D. 数字floor穴
- 生成: checker L554-555(`numbers_not_in_facts`→`reasons.append("number_not_in_fact")`)。
- 接続: L640-643で候補の`flags`は`_flags_from(it)`=モデルが出したflag(SUPPORTED時は全false)。sub_reasonからchanged_numberへの変換なし。
  runner(`er052_open233_self_recovery_flow_runner_01.py`)に`number_not_in_fact`の出現ゼロ。`apply_floor`(L2544)は`dev[changed_number]`のみ見る(FLOOR_MODE=number_only、L849)。
- 新9 run 123 record中`number_not_in_fact`出現=0件(floor発火0)。穴は構造上存在するが今回実害なし【確認】。
- 修正は未実施(分析のみ)。
