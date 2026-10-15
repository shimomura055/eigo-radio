# A_IN_ONE_LINE_TIMELINE_01 (CFSA 委任_01A、2026-10-15、Read-only・JPY0)

目的: In One Line「2文構成」の提案→(Trial)→承認→Coffee適用指示→完成版作成→受入の時系列と、final_v3(2文)→final_03(1文)で1文に戻った段の特定。証拠が無い段は「未確認」。記録者=U(ユーザー)/F(Fable)/S(Sonnet)。区分=提案・Trial・VALIDATED・承認・適用指示・制作・受入。

## 結論(先出し)
1. 「2文構成」は**Trialで検証されたものではない**。2026-10-12にユーザーが決定し(原文逐語はRepo内に未確認、`IN_ONE_LINE_REWRITE_01.md:5`が最も近い記録)、v3制作時にその場で新原稿を生成して適用した。VALIDATEDの記録なし、仕様化は未承認(OPEN-299 OPEN候補)。
2. 2文版の原稿は、記事ソース(`article.md`/`parts.json`)ではなくTrial付属ファイル(`iol_final_text_01.json`)にだけ存在した。Production runnerは`parts.json`のin_one_line(旧1文)からtextを取る。
3. v3→v4→v5までは2文版が維持された(意図的)。**final_03で1文に戻った決定的な段=FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02(2026-10-13 21:55-21:56)**: Audio Validation Gate対応の「検証状態引継ぎ」処理で、Trial生成のIOL wav(2文版)が、元run(e_tone_01)の検証済み1文版wavに置換された。Advは`_replaced_02/`へ退避した記録あり。
4. 置換は「Styleのsha一致」と「textがparts.jsonと一致」で正当と判定された。**文数が仕様(OPEN-299/CURRENT_SPEC:583)と合うかを見る箇所はどの工程にも無かった**。設計書・CHECKLIST・DECISION_LOGのどれにも、IOLが1文に戻る旨の記述がない。
5. 漏れた段: (a)仕様管理=2文版原稿が記事ソースに入らず、OPEN-299が未仕様化のまま残った(b)制作指示=final_03の委任文に「IOL」「OPEN-299」「必須反映5点」の言及なし(c)設計・実装=FIX2設計は「同一textの別take」と記述し、textが変わることを検討していない(d)Fable受入=CHECKLIST_05にIOL項目なし。

## 時系列表
| # | 日付 | 出来事 | 出典(ファイル:行) | 記録者 | 区分 | 漏れ |
|---|---|---|---|---|---|---|
| 1 | 2026-08-09 | In One Line正式仕様: 中心1文(要約)+英語の短い補足2文程度、補足はFull Story/Points既出情報のみ | `CURRENT_SPEC.md:583`(ER-003-A2-STRUCT-05、DECIDED) | U/F | 承認 | - |
| 2 | 〜2026-10-11 | Coffee完成版Final v2/v4系のIOLは中心1文のみ(Std: "Falling coffee bean prices may take at least nine months to affect US shop prices.")。後に「既存仕様の履行不足」と整理 | `er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md:4,13`(旧文) | S | 制作 | 既存正式仕様(#1)の履行不足が過去から存在 |
| 3 | 2026-10-12 | ユーザー決定: 両レベル2文基本(必要なら3文)、1文目=核心、2文目=意味・示唆。「既存仕様の履行不足の是正とは別の新方針」と区別 | `IN_ONE_LINE_REWRITE_01.md:5`、`DECISION_LOG.md:20591` | U→F記録 | 提案+適用指示 | ユーザー原文の逐語はRepo内に未確認 |
| 4 | 2026-10-12 | v3制作(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01): IOL新原稿をgpt-6-luna各1 callで生成(JPY0.204)、TTS、Std6%減速。成果物はTrial隔離(`iol_final_text_01.json`、`segments/adv_in_one_line_raw.wav`) | `docs/pm/delegation_log/2026-10-12_FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01_01.md:7-9`、`IN_ONE_LINE_REWRITE_01.md:7-13` | S | 制作 | 新原稿が記事ソース(`parts.json`)へ反映されない(Trial隔離の設計上の帰結) |
| 5 | 2026-10-12 | SSOT記録: DECISION_LOG(IOL方針を履行不足と新2文方針に区別)、OPEN-299起票[OPEN候補・未仕様化・未承認]、CURRENT_SPEC「In One Line新2文方針は未仕様化(OPEN-299)」 | `DECISION_LOG.md:20591`、`OPEN_ITEMS.md:802`、`CURRENT_SPEC.md:2620` | S/F | 記録 | 仕様化(Writer/Checker/難易度/Comment4接続)は未。承認フロー未開始 |
| 6 | 2026-10-12 | ユーザー指示: 再Assemblyの必須反映5点の1番目=「確定したIn One Line関連仕様を反映する」。前提=「In One Line関連仕様の確定…確定前は再Assemblyを開始しない」 | `docs/pm/design/2026-10-12_COFFEE-FINAL-REASSEMBLY-PLAN-01.md:8-24`、`DECISION_LOG.md:20644`、`OPEN_ITEMS.md` OPEN-321、UDR #1(`docs/pm/USER_DECISION_REGISTER_01.md:18`) | U→S/F記録 | 適用指示 | UDR #1の対象が「Comment4 Trial-03採否」に寄り、IOL文数(OPEN-299)の仕様化決定が独立した判断依頼になっていない |
| 7 | 2026-10-12 | V5(FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01) PRECHECK: 「正式仕様の文数(1+約2)とv4のIOL(2文)には記録上の不一致…決定A/B/CはIOLの変更を求めておらず…v4のものをそのまま再利用」。OPEN-299は未解決のまま続行 | `er057_output/coffee_final_v5/PRECHECK_V5_01.md:22-24`§5、`OPEN_ITEMS.md:802`(V5更新) | S | 制作 | 2文版維持を明示。ただし「確定仕様の反映」(#6)の前提未達を「ブロックしない」と判断 |
| 8 | 2026-10-13 | M2P0/N01 WIRING_01 委任_01-03: 「IN_ONE_LINE/Preview/Comment1-4/shell等は再利用(M2P0・N01の影響を受けない)」「同一text・同一style」と想定。Trial assembler build(`coffee_build_02`)ではAdv IOLは2文版wav(sha `645cac39…`)を使用 | `er071_output/m2p0_n01_production_wiring_01/WIRING_DESIGN_01.md:116`、`COST_ESTIMATE_01.md:45`、`coffee_build_02/assembly_manifest_m2p0_n01_02.json:534` | S | 設計/制作 | 「再利用=同一text」の前提が検証されていない。OPEN-299/321/316への参照なし(rg 0件) |
| 9 | 2026-10-13 | COMPLETION-01 委任_01 FIX2設計: Adv in_one_line/previewはTrial生成raw(`adv_in_one_line_raw.wav`)でProduction Validation記録なし。選択肢(a)正式経路で再生成「同一textでの再生成」/(b)e_tone_01検証済み別takeを引継ぎ「別take」/(c)現wavの検証のみ。**文面(1文⇔2文)の差は指摘されていない** | `er071_output/m2p0_n01_production_wiring_01/completion_01/FIX2_DESIGN_01.md:9-11,38-40` | S | 設計 | 選択肢(b)がIOL文面を変える点を見落とし |
| 10 | 2026-10-13 21:55-21:56(file mtime) | COMPLETION-01 委任_02: 検証状態引継ぎを実行。Std: topic_intro/in_one_line=e_tone_01 seed。Adv: 「in_one_lineはTrial rawを`_replaced_02/`へ退避しe_tone_01検証済みtakeへ置換」。ADV_STYLE_FACTCHECK_02はIOLを「(i) seed+引継ぎ」(Style sha一致のみで判定)。DECISION_LOG記録にIOL文面変更の記載なし | `DECISION_LOG.md:21007`、`completion_02/ADV_STYLE_FACTCHECK_02.md:17,30`、`b1b/narration/_replaced_02/in_one_line.645cac39.wav`(641,324 byte→現行253,484 byte)、`er019_family_x_validation_inheritance_01.py:17,76-78` | S | 制作 | **決定的な漏れ**: 引継ぎ照合は「style sha」「text=parts.json一致」であり、文数がOPEN-299/CURRENT_SPEC:583と整合するかは見ない。Fable受入(委任_02報告)でも指摘なし(未確認: Fable側の受入メモ) |
| 11 | 2026-10-13 | COMPLETION-01 委任_02報告: CHECKLIST_03、F1_RUNTIME_EVIDENCE_02の表に英語4segment(うちin_one_line a2/b1b)のasr_text「Falling coffee bean prices may take at least nine months to…」(旧1文)が表示されていた | `completion_02/F1_RUNTIME_EVIDENCE_02.md:17,19` | S→F | 受入 | 表に旧1文版の冒頭が出ていたが、2文版との差分として認識された記録なし |
| 12 | 2026-10-14 | COMPLETION-01 委任_04: Std/Adv完成版final_03、CHECKLIST_05(12項目)、`PRODUCTION_WIRED`は付与せず。CHECKLIST_05にIOL/K2/M2/A5/B5照合項目なし | `completion_04/CHECKLIST_05.md:5-18`(In One Line語は0件) | S→F | 受入 | 網羅性確認なし(`A_COMPLETION_CRITERIA_RECONSTRUCTION_01.md`§3) |
| 13 | 2026-10-15 | ユーザーがfinal_03試聴でIOLが1文であることを確認、本監査を指示 | `docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01A.md`「ユーザー指示」§1 | U | 受入 | ユーザー自身が発見(Sonnet/Fableの自己検出なし) |

## 補足(実測)
- final_03のIOL textは両レベル1文(`a2/audit/tts_generation_results.json` segments.in_one_line.text、`b1b/…`同)。Stdの置換前2文版wavの退避(`a2/narration/_replaced_02`)は**存在しない**ため、Std側が置換前に2文版だったかは**未確認**(a2の`pre_inherit`記録はin_one_lineが`SKIPPED_NOT_SELECTED`)。Std v5は2文版だったと文書(PRECHECK_V5_01 §5/OPEN-299 2026-10-13追記)は記録している。
- 1文のままの原因としての主要候補: 「Trial付属原稿・音声(R origin)」→「Production検証済みの元run音声(T/旧版)」への置換を、Gate通過のための技術処理として扱い、仕様(文数)観点のチェックが入らなかったこと。これは区分3(旧artifact/seed再利用)+区分4(網羅性確認の欠落)+区分6(SSOT参照不足)の複合(`A_ROOT_CAUSE_CANDIDATES_01.md`)。

## 未確認事項
- ユーザーが2文基本と決定した2026-10-12のチャット原文(Repo外)。
- Fableが委任_02/委任_04を受入れた際の個別メモ(Fable側セッション記録はRepo内にない)。
- Std IOLの置換前の実態(2文版wavが何secだったか)。01Bまたは委任_02でfile/履歴から確認。
