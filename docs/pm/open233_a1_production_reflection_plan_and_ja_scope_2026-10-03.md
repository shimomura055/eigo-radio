# OPEN-233 末尾句読点差対策(L5)のProduction反映準備 と 日本語本文を直さないことの実害整理(委任_52、2026-10-03)

性質: read-only調査。コード・Prompt・テスト・SSOT・既存docは未編集。API費用¥0。git操作なし。`PRODUCTION_WIRED`判断なし。
記号: 「確認」=コード・記録を実際に読んで確かめた事実。「推測」=確認できていない見立て。

---

## 0. 全体の結論(先に読む節)

1. **Family X(Entertainment)のProduction正式経路に、L5を入れる「反映先」は無い。** Production側はCheckerの`claim_in_article`を記事内で探さない。指摘は文字列のまま`must_fix`としてWriter(忠実英訳)へ渡し、記事全体を再生成する。位置特定が無いので、句読点差で「対象を外す」こと自体が起きない(確認)。
2. 位置特定をするProduction処理は別にある。`er010_ledger_local_rewrite_09.py::locate_target_sentence`(L68〜86。完全一致→単語重なり0.25以上の文を採用)を、Discovery Focus・N3記事・B-family voicesのLocal Rewriteが使う(確認)。ここは句読点差でも単語重なりで文が拾われるため「失敗」にはならない。Production記録の実測では、句読点だけの差で外れた実例は0件(確認、原因を判定できた11件中。残りは未判定)。
3. したがって、ユーザーの意図(「Trialでは直っていたがProductionへ入れ忘れた」の禁止)を満たす追跡の形は、**「Self-Recovery FlowをProductionへ接続する際の必須項目」としてOPEN_ITEMSに追跡する**ことを提案する(§A-5の案文)。例外として、er010の`locate_target_sentence`へ同等処理を入れるかは**別のユーザー判断事項**(別の承認済み機構の挙動変更になる。§A-3の反映先2)。
4. 日本語本文を直さないことの実害: 後続処理10件を調べ、**実害あり1系統(再生成の再翻訳。無言ではなくChecker再検査で検知される)**、整合だけ2件、影響なし5件、タイトル1件(ユーザー決定により対策なし、事実のみ記載)。
5. Opus条件Cは、Production採用(接続)の実装前に**該当する**(自動Rewrite・自動Recovery・Human Review境界・validatorに触れるため)。

---

## 作業A: 句読点差対策(L5)のProduction反映準備

### A-1. 反映先の特定(Checker引用から書き換え対象・位置を特定する処理の全数)

結論: Production正式経路でCheckerの引用文字列を「記事内で探す」処理は、er010の`locate_target_sentence`系だけ(Local Rewrite系3経路が呼ぶ)。Family Xの正式経路には存在しない。

**表1: Production正式経路**

| # | ファイル:行 | 関数 | 何に使うか | 照合方式 | 句読点差で失敗しうるか |
|---|---|---|---|---|---|
| P1 | `er010_ledger_local_rewrite_09.py:68-86` | `locate_target_sentence` | MAJOR逸脱の書き換え対象文を決める(Local Rewrite) | ①`claim.strip() in article_text`(完全部分一致)→②失敗時、文単位に分割し単語集合(`[a-z']+`)のJaccard重なり最大の文を採用(0.25以上)→③未満は`not_found`(人間確認) | ①は句読点差で外れる。ただし②は句読点を無視する単語集合なので、通常は拾える(失敗ではなく「文単位への拡大」) |
| P1の呼び出し | `er003_discovery_focus_staged_production_01.py:219,252`、`er003_v1_n3_01_articles_generate.py:1178`、`er012_b_family_voices_writer_generic_01.py:1532` | (上記を呼ぶ) | Discovery Focus(CURRENT_SPEC L1003)、N3記事、B-family voicesのLocal Rewrite | 同上 | 同上 |
| P2 | `er010_ledger_local_rewrite_09.py:204-235` | `_role_word_overlap`/`classify_deviation_role` | 書き換え後の再検査で、指摘が対象文・前後文のどれに当たるかの役割判定 | 単語重なり(0.25閾値) | 句読点は単語に影響しない。影響なし |
| P3 | `er010_ledger_local_rewrite_09.py:238-` | `evaluate_target_sentence_status` | 対象文に関する指摘が残存しているかの判定(OPEN-141差分QA) | P2を使用 | 影響なし |
| P4 | `er012_e_family_entertainment_two_level_runner_01.py:282-291`、`:400-404`、`:496-500` | `_must_fix_from_deviations` ほか | Family X Advanced/Standardの must-fix retry。claimを**文字列のまま**WriterのPromptへ渡す(位置特定なし)。再検査は`prior_issues`(Checker自身に「解消したか」を判定させる、`er003_v1_en_direct_vfl_01_generate.py:649-693`) | 照合なし | 失敗する処理が無い |
| P5 | `er019_family_x_ja_writer_o_r1_r2_01.py:128-138,192` | JA差し戻し(案B)用のmust-fix文 | claimを「該当箇所」としてJA Writerへ文字列で渡す | 照合なし | 失敗する処理が無い |

**表2: Production経路ではないもの(参考)**

| ファイル | 内容 | 理由 |
|---|---|---|
| `er052_open233_self_recovery_flow_runner_01.py` `vs_match_levels`/`vs_edge_punct_match`/`resolve_violation_spans`(L2923〜3089) | L0〜L5の受け渡し照合。`VS_MATCH_EXT`(L335、既定False) | Trial/DEV専用。Productionから呼ばれない(委任_49設計書§5-5、`er052_open233`をer003/er01x等からgrepして0件) |
| `er009_n1_full_writer_ledger_integration_08.py:279`、`er011_*_trial_*`、`er012_editorial_b_voices_trial_*` ほか | `locate_target_sentence`のTrial時代の複製・呼び出し | Trial専用 |
| `er020_tts_retry_local_rewrite_01.py:174,204,362`、`er021_en_asr_semantic_equivalence_production_01.py:673,721` | `difflib.SequenceMatcher`によるトークン差分 | **Checker引用ではなく**、正本テキストとASR文字起こしの差分を取る処理。本件の対象外(Production経路だが別の仕組み) |

### A-2. 影響の有無(末尾句読点差のChecker引用が来たとき)

結論: Family Xでは「対象を外す」ことは起きない(位置特定が無い)。Local Rewrite系(P1)は単語重なりで文が拾われ、Rewrite自体は走る。Production記録に句読点だけで外れた実例は見つからなかった。

- **P4/P5(Family X)**: claim文字列は記事に一致するかを問わず`must_fix`としてWriterへ渡る。句読点差は無関係(確認)。
- **P1(Local Rewrite)**: 完全一致失敗→単語重なりで文単位に拡大して書き換える。結果として「引用された句」ではなく「文全体」が書き換え対象になる(確認)。副作用の有無は推測(Rewrite範囲が広がる)。L5を入れるなら、対象がclaimの範囲(文より狭い)になるか、文へ拡大するかを決める必要がある(Trial runnerのL5は文単位スナップはしない、`vs_edge_punct_match`のdocstring)。
- **¥0実測1(Checker引用 vs 記事)**: スクリプト`%TEMP%\o233\count_claim_match.py`(標準ライブラリのみ。リポジトリ外)で、`er0*_output`配下のJSON84件をなめ、`prompt`内の「検証対象の記事」と`parsed.deviations[].claim_in_article`を比較。使えたのは50件(残り34件は形式不一致で除外)。Deviationは計23件。結果: **完全一致20、不一致3、末尾句読点差のみ(edge_punct)0**。不一致3件は日本語のCheck(`family_x_refresh_e2e_01`のja_original_attempt1)で、複数の「」断片を連結した引用であり、句読点差ではない。Production runner配下(`family_x_entertainment_production_runner_01`、`family_x_b3_production_wiring_01`)は計8件すべて完全一致。**標本が小さい(Deviation 23件)ので「発生しない」の証明ではない**。末尾句読点差22件は、すべてTrial(`er052_output`)のGPT系Checker出力・346件由来(委任_41/45)で、Production記録にはまだ現れていない(推測を含む)。
- **¥0実測2(Production Local Rewriteの位置特定の方式別件数)**: `er0*_output`の`"location_method"`記録を集計: `exact_substring` 223、`sentence_fallback(overlap)` 78、`not_found` 4。fallback 78件のうち、同じaudit内に記事本文が残っていて原因を判定できたのは11件(スクリプト`fallback_cause.py`): **edge_punct_only 0、whitespace_only 4、その他(記事が書き換え後で変化/言い換え)7**。スクリプトが走査できたのは78件中26件(`local_rewrite_cycles.json`形式)で、うち記事が同じaudit内に無く判定不能が15件。残り52件は別形式のためスクリプトの走査対象外で、未判定。つまり「sentence_fallbackの26%は何かで完全一致しなかった」ことは確認できたが、その原因が句読点差だったかは**未確認**。

### A-3. 反映計画

結論: 反映先は「Self-Recovery FlowをProductionへ接続するときの新規照合処理」(反映先1)が本命。反映先2(er010の`locate_target_sentence`)は別判断。どちらも今回は実装しない。

**反映先1: Self-Recovery FlowのProduction接続(未接続、Production側に既存処理なし)**

1. **変更内容**: Trial runnerの`vs_match_levels`(L0〜L3、単語境界条件)・`vs_edge_punct_match`(L5)・`resolve_violation_spans`の`label_only`判定を、Production接続時に**まとめて**取り込む。L5だけを取り出して単独で入れることはしない(L5はL0〜L3の単語境界条件と`label_only`と一体の設計で、既存346行の再生の結果「確定不能→確定22、確定→確定不能0」が得られた組み合わせ)。方式は、共有モジュール化(Trial runnerの関数をProduction用モジュールとして切り出し、Trial runnerとProductionの両方がimport)を推奨する。理由: 二重管理すると「Trialでは直っていたがProductionへ入れ忘れた」が再発しやすい(推測)。小関数の複製を選ぶ場合は、同一入力で同一結果になる同値テストを必須にする。
2. **経路の整合**: 初回・Rewrite周回・Recheck・retry/fallback/regenerationのすべてが同じ`resolve_violation_spans`を通ること(経路ごとに別の照合を持たせない)。Family Xの既存retry枠(Advanced/Standard各1回のmust-fix、JA差し戻し1回、`MAX_REWRITE_CYCLES`)を超えない・無効化しない(既存の安全装置を回避しない)。確定不能は従来どおり人間確認(fail-closed)。
3. **runtime evidenceに残すもの**: 各claimごとに`level`(L0〜L5)、`edge_removed`(両端から除いた文字)、`status`(resolved/unverified)、`reason`(`label_only`等)、`switches`(`VS_MATCH_EXT`相当の値)。Trialの`cycle_record`と同じ項目名を使う。実機で「L5で確定した例が1件以上」を見るのが望ましいが、発生は偶然に依存する(実データ上は346行中22行=約6%)ため、無い場合は固定入力(下記テスト)での実行記録で代替し、その旨を明記する(判断はFable/ユーザー)。
4. **必要なテスト**(委任_45の実例): U03 `“Trump’s proposed Hormuz fee vanished overnight.”`(引用符+末尾ピリオド)、U04 `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage.`、U07(同U04の末尾に`, but the chart only pulled back briefly before recovering.`が続く文、20行)。いずれも「記事内で、claimの末尾の句読点だけが異なる/引用符の差がある」ケース。加えて(a)ちょうど1箇所でないときは確定しない(複数箇所一致は`multi`)、(b)語境界でないとき確定しない、(c)英語本文のみで日本語本文には適用しない、(d)`label_only`は確定不能、(e)悪化0の再生(既存346行の再生を回帰として残す)、(f)既存のL0〜L4・retry・Gateのテストが従来どおりPASS。
5. **CURRENT_SPEC.mdに書く仕様文の案**: 追記先は、Family Xの項目5(案B、L1242〜1271)・項目6(新記事構造、L1272〜)の次の新項目(項目7)として、「Checker引用の受け渡し照合(L0〜L5、末尾句読点差対応)」。文案: 「Checkerの`claim_in_article`を記事側の書き換え対象へ確定する照合は、完全一致・引用符除去・空白正規化・大小無視・断片連結(L0〜L4)に加え、両端の`. , ; : ! ?`を除いた文字列が英語本文にちょうど1箇所(両端が単語境界)で一致する場合に確定する(L5)。語は足さない・落とさない・置換しない。構造ラベル行のみに一致した場合、複数箇所に一致する場合、一致しない場合は確定不能として人間確認へ回す。日本語本文には適用しない。」(行番号は現時点の案。実装時にGrepで再確認する。)
6. **DECISION_LOG.md / OPEN_ITEMS.mdの記載案**: DECISION_LOGにはユーザー指示(2026-10-03、4-1)の原文全文を転記(委任_51が記録済みのはず。Gate 2の「原文全文転記」要件)+「Production接続時の必須項目」である旨の1行。OPEN_ITEMSは§A-5。
7. **Gate 3チェックリスト**(PM_GOVERNANCE.md L182〜193、`PRODUCTION_WIRED`を宣言する前の確認): ①Production正式初回経路への実装 ②retry・fallback・regenerationとの整合 ③DEV/Trial-onlyでないこと ④Production runtimeでの実発火 ⑤必要testのPASS ⑥runtime evidence ⑦model_id・routing確認(必要時。本件は決定論的照合のためLLM追加なしの見込み) ⑧コスト影響評価(追加LLM呼び出しなしの見込み、確認要) ⑨CURRENT_SPEC ⑩DECISION_LOG ⑪OPEN_ITEMS ⑫Git反映 ⑬approved specとProduction挙動の一致。さらにGate 4(Dangling Reference Check: Trial-only仕様への参照が残っていないこと)。

**反映先2(任意・別のユーザー判断): `er010_ledger_local_rewrite_09.py::locate_target_sentence`への同等処理**

- 現状は完全一致→単語重なり文。ここへL5を入れると、句読点差の引用を「文全体」ではなく「引用された句」へ確定できる。ただし(i)これは**承認済みLocal Rewrite機構(Discovery/N3/B-family)の挙動変更**で、Family Xとは別の仕様、(ii)ユーザー指示は「OPEN-233のL5」についてのもの、(iii)Production記録に句読点だけの失敗実例は未確認(A-2)。したがって**ユーザーの意図に含まれるかを確認する必要がある**(新しい仕様候補として報告のみ。実装しない)。

### A-4. Opus条件Cの該当判定

結論: **該当する**(Production採用の実装前に、Opus最終レビュー[11-3節 条件C]を入れる)。

- 根拠: PM_GOVERNANCE.md Gate 2(L176〜181)が、ユーザーへProduction正式採用を提案する前に、重要な技術変更[Production初回経路/retry/fallback/regeneration/validator/Human Review/model routing/Safety判定/自動Rewrite/自動Recovery]にOpus最終レビューを入れるとしている。L5を含む受け渡し照合は、(1)自動Rewriteの対象確定、(2)確定不能時の人間確認(Human Review)への分岐、(3)retry/regenerationの周回で同じ照合を通すこと、に関わる(確認)。
- 再利用の可否: Gate 3 L192〜193は「Production採用提案前に実施したOpusレビューは再利用してよい」。委任_49のOpusレビュー#6(Trial実装の評価・記録・照合追補・英語だけ修正)が、L5・単語境界・label_onlyのどこまでを見たかは今回確認していない(未確認)。Production接続時に、**共有モジュール化の設計(反映先1-1)と、retry/regeneration経路が同じ照合を通る設計**はレビュー#6の範囲外の可能性が高い(推測)ため、再レビュー条件に当たるかはFableが11-3節で照合する。
- 本委任(調査・計画のみ)は非該当。

### A-5. 追跡の形(OPEN_ITEMS.mdの案文。編集はしない)

語彙の確認: `OPEN_ITEMS.md`では「`APPROVED_FOR_PRODUCTION`(Gate 3進行中)」「`PRODUCTION_WIRED`未達」「Statusは`APPROVED_FOR_PRODUCTION`のまま」(L134, L268, L290, L296)の表現が使われている。`approved-but-unwired`の語はCLAUDE.md(compact復帰手順)・PM_GOVERNANCE系のdocに出る運用語で、OPEN_ITEMS.md本体では上の表現が主(確認)。

**案文(反映先が無いため「接続時の必須項目」型)**

```
| OPEN-233-A1-PROD | **Self-Recovery Flow Production接続時の必須項目: Checker引用の受け渡し照合(L0〜L5、末尾句読点差L5を含む)(2026-10-03、ユーザー意向、委任_52)**。ユーザー意向(2026-10-03、原文はDECISION_LOG.md記録)により、Trial runner(`er052_open233_self_recovery_flow_runner_01.py`、`VS_MATCH_EXT`)の末尾句読点差対策(既存346件で再生、22件解消、悪化0)は**Trial/DEV専用に残さずProduction正式経路への反映対象**。Status: `APPROVED_FOR_PRODUCTION`(ユーザー意向)・**approved-but-unwired**(Production未配線)。**反映先の現状**: Family Xの正式経路にはCheckerのclaimを記事内で探す処理が無く(must-fixとして文字列のままWriterへ渡し全文再生成、`er012_e_family_entertainment_two_level_runner_01.py:282-291,400-404`)、Self-Recovery Flow自体がProduction未接続のため、現時点で直接の反映先は存在しない。**したがって、Self-Recovery FlowをProductionへ接続する作業には本項目(L0〜L5の照合・単語境界・label_only・runtime evidence・同値テスト・既存346行の再生回帰)を必ず含める。含めずに接続した場合は`PRODUCTION_WIRED`としない**。Local Rewrite系(`er010_ledger_local_rewrite_09.py::locate_target_sentence`)へ同等処理を入れるかは別のユーザー判断(未決)。`PRODUCTION_WIRED`は、Production初回経路への実装・retry/fallback/regenerationとの整合・runtime evidence・必要test PASS・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Git反映まで完了してから判断する(PM_GOVERNANCE.md Gate 3)。「Trialでは直っていたがProductionへ入れ忘れた」状態を禁止する。実装前にOpus条件C(`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md` A-4)。 |
```

---

## 作業B: 日本語本文を直さないことの実害

結論: 「日本語本文を直さない(英語だけ直す)」場合、**実害あり**は1系統だけ(Productionの再生成が`ja_writer/revision2.md`から英語を訳し直し、直した誤りが戻る経路。ただし再生成後は必ずChecker再検査を通るため無言では戻らず、コスト・周回の問題)。日本語タイトルは別扱い(事実のみ)。日英整合を保ちたいだけの理由は数えていない。

### B-1/B-2. 日本語本文を入力にするProduction後続処理と、古いまま残った場合(分類)

| # | 処理 | ファイル:行 | 古い日本語が残ると何が起きるか | 分類 |
|---|---|---|---|---|
| 1 | Advanced生成(忠実英訳)=初回・段落数retry・deviation must-fixのretry・`--regenerate-stage advanced` | `er012_e_family_entertainment_two_level_runner_01.py:361,365,403-404`(確認) | 条件: Self-Recovery Flowが英語を直した**後**に、Productionの再生成がこの経路で走る。`generate_family_x_faithful_translation(ja_text,...)`が古い日本語R2から英語を作り直すので、直した誤りが戻りうる。戻った英語は`run_deviation_check`を必ず通る(L382, L415)ので、無言では戻らない | **実害あり**(コスト・周回。誤りの流出ではない) |
| 2 | R2の再利用(再実行時に`revision2.md`を読む) | `er019_family_x_entertainment_production_runner_01.py:358-363,376,386,397`(確認) | 1と同じ。`stage in (advanced, all)`や`--regenerate-stage`で`revision2.md`が`run_writer_stage`へ渡る | **実害あり**(1と同一経路) |
| 3 | 案B(ja_source MAJORでJAを1回差し戻し、Advanced/Standardを再実行) | `er012_e...:392-399`(STOP)、`:581-666`(差し戻し)(確認) | 英語だけ直して合格すれば、ja_sourceのMAJORは検出されず案Bは発動しない。日本語は誤りのまま残るが、ユーザーに届かない | **整合だけ** |
| 4 | Deviation Checkの`source_article_text`(起源タグ付け専用) | `er012_e...:383,416,479,510`、`er003_v1_en_direct_vfl_01_generate.py:644-675`(確認) | 判定ではなく`origin`(ja_source/translation)を付けるための参考入力。古い日本語が残っても逸脱の判定本体はLedgerとの照合。再指摘の「揺れ」は実測未確認 | **整合だけ**(揺れの懸念は未確認) |
| 5 | Comment1-4・Preview | `er019_family_x_audio_production_runner_01.py:240-300`(委任_43、確認) | 英語本文`parts`から作る。日本語は入力に入らない | 影響なし |
| 6 | Key Phrase | 同`:320-341`(委任_43) | 英語記事から生成 | 影響なし |
| 7 | 音声(本文TTS)・playerの本文行 | 同`:204-228`、`:1582-1780`(委任_43) | `{level}/article.md`の英語 | 影響なし |
| 8 | Standardの生成 | `er012_e...:458-459,471`(委任_43) | 修正済みのAdvanced(`b1b/article.md`)から作る。日本語は入力に入らない | 影響なし |
| 9 | QA/validator・キャッシュ・再利用判定 | `er019_family_x_audio_production_runner_01.py`のキャッシュ(`_generate_or_reuse`、L933-947)ほか | 委任_43で本文は使われないと確認済みの範囲。キャッシュの判定が日本語本文に依存するかは今回**詳細未確認**(`japanese_title`セグメントのみ日本語を扱う) | 影響なし(推測を含む。タイトル以外) |
| 10 | 日本語タイトル(音声・playerの「Japanese title」) | `er019_family_x_audio_production_runner_01.py:133-147,1852,933-947,1423,1605`(確認) | ユーザー決定「タイトル変更なし前提」。事実のみ: `derive_japanese_title`は`source_dir/ja_writer/`の成果物(`runtime_evidence.json`の`title`優先、無ければ`revision2.md`等の1行目)だけを入力にし、**英語記事・英語見出しは入力ではない**(委任_46 C-1)。英語見出しの最小修正がタイトルへ反映されないのは決定どおり | (タイトル。対策案なし) |

件数: 実害あり 2行(表の行1・2。経路は同一のため**1系統**)、整合だけ 2、影響なし 5、タイトル 1(対策なし)。

**実害ありの経路と最小の対策案**
- 経路: `efam.run_writer_stage()`(`er012_e:340-`)が`ja_text`(`ja_writer/revision2.md`)から英語を作り直す。誰がいつ呼ぶか: (a)段落数retry(L364-371)、(b)deviation must-fix retry(L403-407、ja_source以外のMAJOR)、(c)`--regenerate-stage advanced`/`stage in ("advanced","all")`の再実行(er019 entertainment runner L384-399)。
- 古い日本語から何を作るか: 古い日本語R2に含まれる逸脱を持つ英語Advancedを再生成する。
- 最小の対策案: **「既存で足りる」**。再生成後の英語は必ず`run_deviation_check`を通り、MAJORなら既存のmust-fix retry・案B・STOPに入る(CURRENT_SPEC L1951の記述、委任_43)。追加コードは不要。ただし、Self-Recovery FlowをProductionへ接続するとき、「再生成後も必ずSelf-Recovery Flowを通す」ことを接続仕様に明記する(委任_43の案A1)。案A2(英語の修正内容をmust-fixとして再生成へ添える)は、Production変更が必要なのでユーザー判断(今回は提案のみ)。
- 注: Self-Recovery FlowがProductionに接続されるまでは、この経路は発動しない(Production未配線、委任_43)。

### B-3. 承認済み仕様との関係

結論: 「英語だけ修正」をProductionへ入れる場合、**2つの承認済み仕様と衝突する可能性が高い**。今回は判断しない。

| 仕様 | 位置・逐語 | 衝突 |
|---|---|---|
| 忠実英訳 | `CURRENT_SPEC.md` L1272-1278: 「新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1→本文1→…」「見出し生成指示を除いた忠実英訳+段落境界のみでの決定論的3分割」(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`) | 英語だけ直すと、英語はJA R2の「忠実な訳」でなくなる。仕様文自体の変更が必要か、「忠実英訳で作った後の局所修正は例外」と明記するかの判断が必要 |
| 案B | 同L1242-1257: 「English側(Advanced/Standard)のDeviation Checkが`origin=ja_source`のMAJORを検出した場合…その具体的な指摘をJA Writer Oのoriginal段へmust-fixとして差し戻し、JAを…**1回だけ**再生成し、Advanced/Standardを再実行する」「JA差し戻し1回後もMAJORならSTOPする」 | 「日本語へ遡らない」方針と方向が逆。英語だけ修正をProductionで`ja_source`にも適用するなら、案Bの発動条件との優先順位(先に英語だけ修正か、案Bか)の決定が必要 |
| 日本語タイトル | (決定済み。衝突なし) | ユーザー決定により「タイトル変更なし前提」 |
| Local Rewrite | L1010-1014(Main Story固定原則: 英語上のLocal Rewriteは既存安全装置として許容) | 衝突しない(Local Rewriteは英語記事上で動き日本語を入力にしない、委任_43) |

**Production採用時にユーザー判断が必要な点(今回は判断しない)**
1. 「忠実英訳」を、局所修正後の英語については緩めるか(仕様文の変更)。
2. 案B(JA差し戻し1回)と英語だけ修正の優先順位。ja_source指摘を英語だけで直す場合、案Bを残すか廃止するか。
3. 再生成が日本語R2から訳し直す経路(B-2の実害あり)への対応: 「再生成後も必ずSelf-Recovery Flowを通す」(案A1)でよいか。
4. 日本語タイトルは決定済み(対応なし)だが、Meta Muse見出し・hormuzの「原油高」など、実害が実在する例(委任_46 C-3)を、将来記録だけ残すか(`en_title_rewritten`の記録は設計書§5-1)。

### B-4. Trial runnerの`JA_MODE=english_only`は、ユーザー方針3点を満たすか

結論: **3点とも満たす**。ただし、設計・実装に「満たさない」とまでは言えない注意点が2つある(下記)。

| 方針 | 確認(runner、設計書§5) | 判定 |
|---|---|---|
| 日本語へ遡らない | `JA_MODE == JA_MODE_ENGLISH_ONLY`のとき`current_ja_text = None`(runner L5332-5336)。JA Recheck、`ja_pending_deviation`、JA合流、`ja_fail_open_guard`、等価チェックが`current_ja_text is not None`を条件にしているため迂回される(設計書§5-4表、L446-459) | 満たす |
| 日本語側の対応箇所を推測して同時Rewriteしない | `use_pairing`が常にFalse(`current_ja_text is None`、設計書L420)、`paired_rewrite`・`locate_ja_counterpart_by_position`が呼ばれない | 満たす |
| 整合のためだけに処理を複雑化しない | 削除ではなくスイッチで迂回(設計書L463)。既定は`paired`で既存テストを維持。英語だけ修正では、JA由来の指摘も英語単独のRewrite | 概ね満たす(下の注意2) |

注意点(ユーザー方針と矛盾するとまでは言えないが、確認が必要):
1. **ja_sourceの指摘を書き換えた周回は全文Recheckを必須にする**(runner L4447-4459、`english_only_ja_source_requires_full_recheck`)。これは日本語を直すためではなく、英語だけ修正の安全網(英語側の全文再検査)。日本語へ遡らない原則とは矛盾しないが、費用・周回は増えうる(確認、費用影響は今回未測定)。
2. **`source_article_text`(元の日本語)をCheckerとStage 2へ渡し続ける(D1)**(runner L5333-5336、設計書§5-2)。起源タグ(ja_source/translation)のための参考入力で、「日本語を使った判断・書き換え」ではない。ただしユーザー方針の「日本語へ遡らない」を厳密に読むと、日本語を完全に入力から外すD2が方針に近い。D1/D2の選択は設計書が「測定の連続性」のためD1を推奨しており、ユーザー判断が必要な論点として残る(今回は判断しない)。
3. Checkerが日本語記事にしか存在しない文字列を引用した場合(`ja_only_match_english_only`、runner L4249-4254)は確定不能として人間確認へ回る(fail-closed)。これは日本語を直さない設計の自然な帰結。

---

## 確認できたこと / 推測 / 未確認(まとめ)

- 確認: Family Xの正式経路は位置特定をしない(must-fix文字列のまま全文再生成)。`locate_target_sentence`の呼び出し元(3経路)。Production audit内のClaim一致実測(23件中、句読点差のみ0)。location_methodの件数(223/78/4)。再生成の再翻訳経路の行番号。`japanese_title`の入力。runnerの`JA_MODE`実装。
- 推測: 共有モジュール化の方が入れ忘れを防ぐ。Production記録に未だ句読点差が現れていない理由(標本が小さい/Checker世代の違い)。Opus#6の範囲。
- 未確認: sentence_fallback 78件のうち67件の原因。キャッシュ・再利用判定(`_generate_or_reuse`)が日本語本文に依存しないこと(タイトル以外)の直接確認。日本語タイトルがJA Fact Checkの対象かどうか。再生成の頻度。

一覧外のRead/Grep(委任文の事前指定に無いもの): `er012_e...`(L255-345,384-407)、`er019_family_x_entertainment_production_runner_01.py`(L356-399)、`er003_v1_en_direct_vfl_01_generate.py`(L640-710)、`er012_b_family_voices_writer_generic_01.py`(L1525-1550)、`er003_discovery_focus_staged_production_01.py`(L214-226)、`CURRENT_SPEC.md`(L988-1015、L1236-1286)、`PM_GOVERNANCE.md`(L170-193、L478-489)、委任_45結果(U03/U04/U07のGrep)、`er0*_output`のJSON(¥0集計)。
