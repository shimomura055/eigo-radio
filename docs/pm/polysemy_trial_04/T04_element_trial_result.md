# T04 要素Trial結果(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04 委任_P4a-2)

作成: Sonnet(実行層)。成立判定・SSOT反映はFable。Production変更なし(Trial/DEVのみ)。各パターン1回実行(再実行・後付け基準変更なし)。
詳細: `er052_output/open233_polysemy_trial_03/eval/t04_eval_table_p04.md` / `t04_funnel.md` / `t04_*_content_label_sheet.md` / `t04_labels.json`(Sonnet仮ラベル、人手確認前) / `runs/cost_t04.json` / `eval/rollback_gate_labels.md`(3値定義、実行前記載)。

## 1. 実装(Opus必須修正1〜9)
1 stage1に`predicate_direction_explicit`+`ambiguous_expression`追加、Rはpolarity最優先列挙、pred=falseかつpolarity採用Rは判定役を素通り(コード`is_bypass`)。2 vague語lint(戻す/元に戻/復元/ロールバック/変更/見直し/改める/調整+当該factの曖昧表記)をR・変化後の状態・r_echo・note(引用符'...'内を除く)へ、違反は`lint_rejected.json`。3 P2直行廃止→P2'(判定役常時、high通過、mediumはstage1 2回通過のみ)。4 stage1は既存notes伏せ、`existing_note_covers`は別の小call(cover_prompt)、covers=trueはstage2へ送らず、stage2へは「繰り返さない一覧(already_prohibited)」のみ。5 判定役を固定基準+blocking_word必須、限定語blockingはlow→medium(コード)。6 Noteは「表記'<曖昧表記>'」形式、英語は台帳実在語のみ(コード照合)。7 stage2はr_echo一致+noteの「Rではない」部分(bigram被覆>=0.5)をコード照合。8 prompt_lintに禁止語・`prompt_hashes.json`追加。9 `eval/rollback_gate_labels.md`。
検証: pytest 45件PASS、衛生PASS(64 file)、lint PASS。コード: `tools/gen_notes_p04.py`(全面改修)、`gen_notes_p03.py`(stage1で既存notes伏せ・cover読込)、`prompt_lint_p04.py`、`eval_notes_p04.py`。旧`P1_gate_hm`/`P2_stable`は未使用の旧版として残置(P1p_gate_hm/P2p_stableが新版)。

## 2. 比較表(コア5台帳。P3は予算上限でai_control未実行=4台帳・対象11件)
| 指標 | P1' | P2' | P3(4台帳) |
|---|---|---|---|
| 捕捉(対象) | 2/14 | 3/14 | 3/11 |
| 付与率(平均) | 21%(meta40%,hormuz33%) | 13%(最大25%) | 19%(meta40%) |
| 対象外付与 妥当V/変質D/誤りH | 11/3/2 | 4/4/0 | 9/1/0 |
| 内容一致 主(生成のみ) Y / (Y+P) | 0/2(0%) / 50% | 2/3(67%) / 67% | 0/3(0%) / 67% |
| 副: 和集合Y(生成+既存notes禁止文転記) | 9/14 | 9/14 | 6/11 |
| holdout over(期待超過) | 6(A02 +3,small_bag +3,A01 0) | 4(A02 +1,small_bag 0,A01 +3) | 未実行(対象外) |
| holdout 誤り(H/X) | 1(A02 PILOT-05) | 1(同) | - |
| 捏造 | 0(目視) | 0 | 0 |
| 字数 平均/最大 | 89/119 | 80/101 | 90/111 |
| 実費 | 43.75円 | 61.97円 | 18.47円 |

## 3. 基準照合(6項目。捕捉>=9/14・付与率<=25%・holdout誤付与<=1・捏造0・内容一致>=70%・迎合なし)
| 項目 | P1' | P2' | P3 |
|---|---|---|---|
| 捕捉>=9/14 | NG(2) | NG(3) | NG(3/11) |
| 付与率<=25% | OK(全体21%、台帳別meta/hormuzはNG) | OK | OK(全体、meta40%はNG) |
| holdout<=1 | NG(6) | NG(4) | 判定対象外 |
| 捏造0 | OK | OK | OK |
| 内容一致>=70% | NG(0%、(Y+P)50%) | NG(67%、n=3) | NG(0%、(Y+P)67%) |
| 迎合なし | OK(台帳別件数が不一致) | OK | OK |

## 4. rollback別枠Gate(MUSE-HC-012)
| | 捕捉 | Note全文 | 機械チェック | 3値仮ラベル |
|---|---|---|---|---|
| P1' | Y | 注意(逆転): 台帳の表記'ロールバック'は、人間コンシェルジュ機能が当面提供されない状態の意味。Metaは人間コンシェルジュ機能を恒久的に廃止したのではない。 | FAIL候補(A取り下げ語なし,B復活否定なし) | 軸ずれ |
| P2' | N(コードr_echo却下) | なし(却下note文はP1'と同型) | FAIL(未捕捉) | 未捕捉 |
| P3 | Y(素通り経路) | 注意(逆転): 台帳の表記'ロールバックした'は、人間コンシェルジュ機能が当面停止している状態の意味。Metaは人間コンシェルジュ機能を恒久的に廃止したのではない。 | FAIL候補(B復活否定なし) | 軸ずれ |
全パターン合格なし(誤禁止型はなし=『復元ではない』『元に戻していない』は不出現)。いずれも「時期軸(恒久廃止ではない)」止まりで、「機能そのものを復活・再提供した意味ではない」を含まない。Fable最終判定要。

## 5. 段別ファネル(詳細は t04_funnel.md)
- stage1が最大の損失: 対象14件中 reversible=false で落ちたのは P1' 8件 / P2' 6件 / P3 4件(11件中)。
- cover(既存notesがRを既に禁止)でstage2へ送られず落ちた対象: P1' 3(F-009,F-011,EVID-006) / P2' 3(F-009,F-007,EVID-006) / P3 1(F-007)。この3〜4件は「生成のみ」の捕捉に入らず、既存notes(禁止文)で補われる。
- 判定役で落ちた対象: P3 2(F-009,F-011=low、いずれも非限定語blocking_word)、P2' 1(F-002=判定役の出力欠落)。mediumを2回通過条件で落としたfactはP2'全体で13件(対象は0)。
- コード照合で落ちた: P1' F-010(stage2 lint: 「市街化調整区域」の「調整」)、P3 F-010(同語でR lint)、P2' HC-012(r_echo末尾「。」有無だけの不一致)。
- HC-012: 全パターンで pred_direction_explicit=false。ただしP1'/P2'は採用Rが interim_final(恒久廃止)でpolarityでないため素通りせず判定役high通過。P3のみpolarity判定で素通り。いずれも「復活・再提供」型のRが列挙されず、Gateの要件(復活・再提供の否定)が書かれない。

## 6. 件数: 素通り / low→medium昇格 / lint却下
P1' 0 / 0 / 10(R1+stage2 9) 、P2' 0 / 0 / 9、P3 1 / 0 / 1。stage2コード却下: P1' 10(英語台帳外8,R非保持1,lint1)、P2' 8(英語台帳外6,r_echo不一致1,字数超過1)。

## 7. 安定性: 未実施(残予算 約5.8円 < 20円)。P2'のstage1 Jaccard(2回): meta .50 / hormuz .17 / space .57 / sewer .67 / ai_control .91 / A02 .50 / small_bag .09 / A01 .00。

## 8. 実費: 124.19円(上限130)。TRIAL-03累計160.13円 + 本件124.19円 = 284.32円。P3のai_controlは約6.5円で上限超過のため未実行(明示的な逸脱)。

## 9. 所見
1. 3パターンとも合格条件を満たさない(捕捉2〜3/14、holdout過付与、Gate不合格)。損失の主因は判定役の閾値ではなくstage1のreversible判定(対象の6〜8/14が脱落)とcover(3件)であり、HC-012は「時期軸」Rしか列挙されず復活・再提供型Rが出ないためGate要件を満たせない。内容一致の最良はP2'(2/3)だがn=3。
2. 既存notes禁止文の機械転記だけで対象Y一致9/14(和集合でも9/14=生成noteの上積みなし)。ハーネス側欠陥として、(a)r_echo照合が末尾「。」で却下(1件)、(b)R lintが「市街化調整区域」の「調整」を誤却下、(c)「<R>ではない」でR文末が過去形だと「〜だったではない」の文法崩れ(P1'のsmall_bag等)、(d)台帳外英語照合がFW25/SS25等の略記を却下、(e)P2'の判定役が1件verdict欠落。基準・promptは再調整せず、Fableの判断材料として記録。
