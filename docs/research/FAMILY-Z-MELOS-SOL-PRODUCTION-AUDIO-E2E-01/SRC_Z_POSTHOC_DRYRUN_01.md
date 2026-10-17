# SRC D1強化版「z_sentence_id_posthoc_v1」オフライン解決dry-run (FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15 W7)

- 性質: JPY0・API呼出0・Production code非接続(実装はしない)。実装は USER_DECISION #109(D1強化版を「ZへのSRC正式適用」と認めるか)の回答後。
- script: `src_z_posthoc_dryrun_01.py` / 結果JSON: `src_z_posthoc_dryrun_01.json`(対象=run_e2e_02の A2=std.md 5 item + B1B=r2.md 5 item = 10 item)。
- 実行: `.venv\Scripts\python.exe docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/src_z_posthoc_dryrun_01.py --run-dir er026_output/family_z_production_e2e_01/melos/run_e2e_02 --out docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/src_z_posthoc_dryrun_01.json`

## 方式(Opus R-C3 (d))
1. `er030_key_phrase_db_hybrid_core_01.build_sentence_units`(X Production使用中の既存関数)で本文をS1..Snに分割(A2=46文、B1B=57文)。
2. 各itemの(source_sentence, source_span)を (i)正規化完全一致 (ii)唯一の包含(文がsource_sentenceに含まれ、かつspanを含む) (iii)spanを含む文が唯一、の順で文IDへ解決。曖昧/該当なしはSTOP(自動採用しない)。
3. `restore_source_fields`(同 source_reference_contract_01:416)でPythonが source_sentence/source_span を復元。`context_sentence_id`がNoneのときspanで代用するfallback(:463-464)は本方式では禁止(STOP)。
4. ラベル案 `z_sentence_id_posthoc_v1`(承認済み `candidate_id_v1` ではない。「LLMに元英文を自由記述させない出力契約」部分は非適用=Strategy L維持のため)。`SUPPORTED_FAMILY_PROFILES`へ"family_z"は追加しない。

## 結果(10 item)
- 解決可否: 10/10解決(方法はすべて `unique_containment`)。曖昧0・該当なし0。`restore_source_fields`のunresolved=0・mismatch=0。
- 復元値と既存値の関係(正規化比較): 完全一致0 / 句読点・引用符差のみ7 / 境界差(復元値が既存の部分=1文)3 / 内容差0。span(source_span)は10件すべて保存。
  - 句読点差7: `build_sentence_units`が終端句読点(.!?)を落とし、引用符を直引用符に正規化し外側の引用符を剥がすため(例: `...the light.` -> `...the light`)。意味・spanは同一。
  - 境界差3: (a) a2 rank2「The ruler smiled and said, “Your friend must stay here. Return late, and he will die in your place.”」(1つの引用符内が2文)-> 復元は S8 `Return late, and he will die in your place`(**引用符内の分割境界ずれの実例**。前半文脈が落ちる)。(b) b1b rank1/rank4 `Silence followed. Then the guards seized ... to death.`(LLMのsource_sentenceが2文にまたがる)-> 復元は S5 のみ(spanを含む1文に絞られる=より厳密)。
- 引用符を含む文(分割後): A2 S1,S5,S7,S40,S41,S44,S45 / B1B S6,S50,S51,S54,S56。うち実item(span)に関わるのは a2 rank2(S8)・rank3(S41)・b1b rank5(S50)。引用符内の複数文(`”` が次の文に続く)でずれる。
- 結論: 文ID解決自体は決定論的に成立する(曖昧0)。ただし D1を実装する場合、次を設計に含める必要がある。
  1. 復元後の source_sentence は終端句読点・引用符が正規化済みになる(既存値との文字列一致は要求しない)。受入判定は「source_span保存+spanが復元文に含まれる」を正とし、文字列差はtelemetryに記録。
  2. 引用符内で文が分割される場合の扱い(a2 rank2型)。案: 復元文が引用符を跨ぐときは前後のunitを連結した「引用段落単位」を許容するか、spanを含む1文のみを採用して前半文脈欠落をtelemetryに記録するか、のどちらかをFableが決める(推奨=後者。KP解説は日本語gloss+display_phraseが主で文脈欠落の影響は小さい見込み)。
  3. 既存値が複数文(b1b rank1/4)の場合は復元値(1文)が既存より厳密。採用すると kp_expl の入力 source_sentence が変わる。

## 配線位置案(実装時。今回は設計文書のみ)
- gate挿入位置: `er026_family_z_fiction_production_runner_01.py:1252-1262` の `ensure_stage(...kp_{lv}...)` 直後・`install_kp_assets` 直前。**再利用経路(ensure_stageが既存結果を返す場合)にも必ず適用**する(OF-KGCPW-08と同型)。復元結果が既存と異なる場合は keywords_canonicalized.json を書き換えず別ファイル(audit)へ記録し、STOP/採用はFable方針に従う。
- kp_expl sig修正: `:1273-1279` の `sig_payload` に source_sentence(または解決した文ID+復元文)を追加する(現状 display_phrase のみ、gloss整合時のみglossを含む)。新runなので互換問題なし。復元で source_sentence が変わると解説の入力が変わるのに、現sigは変化を検出しないため。
- 共有Prompt(`er003_v1_translator_briefs/*`、Strategy L)は変更しない(D2は共有Prompt変更=承認事項のため不採用)。

## 判定
- D1強化版は技術的に成立(10/10解決・曖昧0)。ユーザー確認点は #109(D1を「ZへのSRC正式適用」と認めるか。承認済み`candidate_id_v1`の「LLMに自由記述させない契約」部分は非適用)。Production code実装・`candidate_id_v1`ラベル付与は行っていない。
