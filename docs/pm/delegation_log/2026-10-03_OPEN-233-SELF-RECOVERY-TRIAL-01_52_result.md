<!-- 抽出元: C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\agent-a785a39f4bc460edf.jsonl のSubagentHandback呼び出しのmessage引数。改変なし(スクリプト抽出) -->

委任_52 報告(read-only調査+新規doc1点のみ。コード・SSOT・既存doc未編集、API費用¥0、git操作なし)

## (1) 結論
1. **Family X(Entertainment)のProduction正式経路に、L5を入れる反映先は無い。** Production側はCheckerのclaim_in_articleを記事内で探さない。claimを文字列のままmust_fixとしてWriterへ渡し、記事全体を再生成する(er012_e L282-291, L400-404, L496-500)。位置特定が無いので、句読点差で対象を外すこと自体が起きない(確認)。
2. 位置特定をするProduction処理は別にある。er010_ledger_local_rewrite_09.py L68-86の`locate_target_sentence`(完全一致→単語重なり0.25以上の文)で、Discovery Focus(er003_discovery_focus_staged_production_01 L219,252)、N3記事(er003_v1_n3_01_articles_generate L1178)、B-family voices(er012_b_family_voices_writer_generic_01 L1532)が呼ぶ。句読点差でも単語集合で文が拾われるため「失敗」にならず、文全体へ拡大して書き換わる。
3. 影響の実例数(¥0集計、スクリプトは%TEMP%\o233\配下)。(a)Checker引用と記事の比較: 使えた50ファイルのDeviation 23件のうち、完全一致20、不一致3、**末尾句読点差のみ0**。不一致3件は日本語の複数「」断片連結で句読点差ではない。標本が小さく、発生しない証明ではない。(b)Production Local Rewriteのlocation_method記録: exact_substring 223、sentence_fallback 78、not_found 4。fallback 78件のうち原因を判定できたのは11件で、edge_punct_only 0、whitespace_only 4、その他7。残り67件は未判定。
4. 追跡の形の提案: 「Self-Recovery FlowをProductionへ接続する際の必須項目」としてOPEN_ITEMSに`OPEN-233-A1-PROD`を立てる(案文はdoc A-5)。Statusは`APPROVED_FOR_PRODUCTION`(ユーザー意向)かつ approved-but-unwired。含めずに接続した場合は`PRODUCTION_WIRED`としない旨を明記した。
5. er010の`locate_target_sentence`への同等処理は、別の承認済み機構の挙動変更になる。ユーザー意図に含まれるかの確認が必要(新しい仕様候補として報告のみ。実装していない)。
6. **Opus条件Cは該当する**(自動Rewrite・自動Recovery・Human Review境界・retry/regenerationに関係。PM_GOVERNANCE Gate 2 L176-181)。Opus#6の再利用可否は、共有モジュール化の設計とretry経路の整合がレビュー範囲外の可能性が高い(推測)ためFableが11-3節で照合する。
7. 日本語本文を直さないことの実害(10行): **実害あり1系統**(表の2行、経路は同一)、整合だけ2、影響なし5、タイトル1(対策案なし、事実のみ)。
8. 実害ありの経路: er012_e L361,365,403-404(Advanced再翻訳)と er019_family_x_entertainment_production_runner_01 L358-363,376,386,397(revision2.md再利用)。Self-Recovery Flowが英語を直した後にProductionの再生成が走ると、古い日本語R2から訳し直して誤りが戻りうる。再生成後は必ずrun_deviation_check(er012_e L382,L415)を通るので無言では戻らない。最小対策は「既存で足りる」。接続仕様に「再生成後も必ずSelf-Recovery Flowを通す」を明記する(委任_43の案A1)。
9. JA_MODE=english_onlyは、ユーザー方針3点(遡らない/推測して同時Rewriteしない/整合のためだけに複雑化しない)を満たす。注意点2つは、(i)ja_source指摘を書いた周回の全文Recheck必須(runner L4447-4459、費用影響は未測定)、(ii)元の日本語をCheckerとStage 2へ起源タグ用に渡し続けるD1(厳密にはD2が方針に近い。ユーザー判断事項として残る)。
10. 承認済み仕様との衝突: 「忠実英訳」(CURRENT_SPEC L1272-1278)と「案B」(L1242-1257)に衝突する可能性が高い。判断はしていない。

## (2) 作業Aの要約
- A-1: Production位置特定はP1(`locate_target_sentence`と3つの呼び出し元)だけ。P2・P3(`classify_deviation_role`/`evaluate_target_sentence_status`、単語重なり)は句読点の影響なし。P4・P5(Family XのmustFix受け渡し、案BのJA差し戻し)は照合なし。Trial/DEV専用(runnerのL0〜L5、er009/er011/er012 Trial複製)とCheckerの引用ではないトークン差分(er020/er021のSequenceMatcher)は別表。
- A-3 反映計画の要点: 反映先1=Self-Recovery FlowのProduction接続時に、L0〜L3の単語境界・L5・label_onlyを一体で共有モジュール化して取り込む(L5だけの単独移植はしない)。初回・Rewrite周回・Recheck・retry/fallback/regenerationが同じresolve_violation_spansを通る。既存retry枠は超えない・無効化しない。runtime evidenceはlevel/edge_removed/status/reason/switches。テストはU03・U04・U07+複数一致・語境界・日本語不適用・label_only・既存346行回帰。CURRENT_SPEC案は項目5・6(L1242〜)の次に項目7を追加。Gate 3チェックリスト13項目+Gate 4。反映先2=er010への同等処理は別のユーザー判断。
- A-5: OPEN_ITEMS案文はdoc内に完全版あり。

## (3) 作業Bの表の要約
| 処理 | 分類 |
|---|---|
| Advanced再翻訳(er012_e L361,365,403) | 実害あり(コスト・周回、Checkerで検知) |
| R2再利用(er019 L358-397) | 実害あり(上と同一経路) |
| 案B(er012_e L392-399, L581-666) | 整合だけ |
| source_article_text(起源タグ専用) | 整合だけ(再指摘の揺れは実測未確認) |
| Comment/Preview、Key Phrase、TTS・player本文、Standard生成、QA/キャッシュ(タイトル以外) | 影響なし(キャッシュはタイトル以外で日本語に依存しないことの直接確認は未実施) |
| 日本語タイトル | derive_japanese_title(er019 audio L133-147)は英語記事を入力にしない。タイトル変更なし前提のため対策案なし |

## (4) T-0・作成ファイル・確認と推測
- **T-0結果: FAIL**(記録のみ、作業は継続)。理由は保存版で「事前指定Grep一覧+追記位置・更新位置の手順」と「実行コマンド全文」の見出しを省いたため。委任文の要点保存版であり、全文逐語保存ではない。TTS関連warningは本委任に無関係。
- 作成ファイル(すべて未追跡のまま):
  - C:\Users\tensh\eigo-radio\docs\pm\open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md
  - C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_52.md
  - C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_52.md_check.json
  - リポジトリ外の集計スクリプト: %TEMP%\o233\count_claim_match.py、%TEMP%\o233\fallback_cause.py
- 一覧外のRead/Grep: er012_e L255-345,384-407、er019 entertainment runner L356-399、er003 vfl01 L640-710、er012_b voices L1525-1550、discovery_focus L214-226、CURRENT_SPEC L988-1015,1236-1286、PM_GOVERNANCE L170-193,478-489、委任_45結果のU03/U04/U07 Grep、OPEN_ITEMS.md行のGrep、er0*_output配下JSONの¥0集計。
- 確認できたこと: Family Xに位置特定が無いこと、`locate_target_sentence`の呼び出し元、上記2つの実測数値、再生成経路の行番号、japanese_titleの入力、JA_MODEの実装。
- 推測: 共有モジュール化が入れ忘れ防止に有効、Production記録に句読点差がまだ現れていない理由、Opus#6の範囲。
- 未確認: sentence_fallback 67件の原因、キャッシュ判定が日本語本文に依存しないこと、日本語タイトルがJA Fact Check対象か、english_onlyの追加費用。
- 注: OPEN_ITEMS.md本体では「approved-but-unwired」の語は使われておらず(CLAUDE.mdと各docの運用語)、「`APPROVED_FOR_PRODUCTION`(Gate 3進行中)」「`PRODUCTION_WIRED`未達」が主な表現。案文は両方を併記した。
