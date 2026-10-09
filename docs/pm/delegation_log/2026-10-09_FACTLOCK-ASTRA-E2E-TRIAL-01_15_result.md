# 委任_15 結果 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) Status=EVALUATED_PENDING_FABLE(MEASURED、ラベル暫定、判定線の最終判定はFable待ち)。API支出¥0、Production変更なし、VALIDATED/APPROVED_FOR_PRODUCTION未宣言

## 1. 成果物・commit・raw URL
- `er052_output/factlock_astra_e2e_trial_01/eval/`: `labels_merged.jsonl`(553行、重複グループ46、worker間テーマ重複0、`labels_merged_stats.json`)、`merge_labels_01.py`、`judge_table_01.py`/`judge_table_01.json`(機械判定の根拠数値)、`EVAL_E2E_01.md`、`HUMAN_CHECK_E2E_01.md`(+`build_human_check_01.py`)、ラベル原本 `labels_w{1,2,3}.jsonl`/`_summary.md`(未編集)。
- SSOT: REPORT §111、DECISION_LOG末尾1節、`docs/pm/REPORT_LEDGER.md` 1行、ACTIVE_TASK固定ヘッダ(gitignore対象)。`CURRENT_SPEC.md`/`OPEN_ITEMS.md`は未編集。
- 記録: 委任文 `_15.md`、`_15_check.json`、`_14a/b/c_result.md`(commitのみ)、本書、RESULT_PACKET。
- commit: COMMIT_HASH_PLACEHOLDER
- raw URL: 末尾。

## 2. 判定線 機械照合表(n=9、予定run各腕18。Fable最終判定は空欄)
| 指標 | 新 | 旧 | 差 | 判定線 | 機械判定 | 旧4(新/旧) | 新5(新/旧) | Fable最終 |
|---|---|---|---|---|---|---|---|---|
| 2-1 重大(出荷最終本文の残存) | 0 | 0 | 0 | 新0かつ新<旧で良化、総数2以下は判定不能、新>0かつ旧0は要確認フラグ | 判定不能(床効果)、フラグなし | 0/0 | 0/0 | |
| 2-2 軽微 JA列(claim単位、対6テーマ) | 5(平均0.83) | 9(平均1.50) | -4 | 平均比0.75以下かつ新少ない対が過半数かつ6対以上 | 同等(平均比0.56は良化線、新少ない対3/4で6対以上に届かない) | 1/4 | 4/5 | |
| 2-2 軽微 EN Adv列(対4テーマ) | 3 | 3 | 0 | 同上 | 同等 | 1/1 | 2/2 | |
| 2-2 軽微 EN Std列 | 5(4本) | 4(5本) | +1 | 同上 | 判定不能(対のある対が1、総数5以下) | 3/1 | 2/3 | |
| 2-4 EN STOP率 Adv(分母9) | 0.22(2: openai,semi) | 0.00 | +0.22 | 3記事差以上かつ翻訳由来MAJOR/記事の比 | 同等(translation由来MAJORは両腕0) | 0/0 | 2/0 | |
| 2-4 EN STOP率 Std(分母9) | 0.22(2: space,byd) | 0.22(2: small,byd) | 0 | 同上 | 同等(STOP率差0、translation由来MAJOR/記事は新0.22対旧0=片方のみ=記述) | 1/1 | 1/1 | |
| 2-5 Rewrite率(分母18) | 0.111(2) | 0.167(3) | -0.056 | 差0.15以上(3 run差) | 同等 | 1/8対0/8 | 1/10対3/10 | |
| 2-5 Human Review率 | 0 | 0 | 0 | 総イベント2件以下は判定不能 | 判定不能(床効果) | 0/0 | 0/0 | |
| 2-5 人手介入必要率(分母18) | 0.333(6) | 0.333(6) | 0 | 差0.15以上、総イベント4件以下は判定不能 | 同等(感度: Adv STOPでStd runも失う解釈なら8対6=差+0.111でも同等) | 0.125対0.625 | 0.50対0.10 | |
| 2-6 総合(参考) | 良化0・悪化0 | | | 2指標以上良化かつ悪化0で良化、2指標以上悪化または確定フラグで悪化 | 同等/混在 | | | |
| 記述: JA R2 FC MAJOR / (ii)最終 / 初回JA_RECHECK | 0 / 2 / 4(9) | 4 / 15(うち7は案B前) / 3(9) | | 判定外 | 記述 | | | |
| 記述: M1発火(runログ) / M3保護 / B1 | 1(space Adv) / 6 / 3(完走1) | 0 / 影5 / 案B 3(成功1) | | 判定外 | 記述(M1 Std未実装) | | | |
| 費用(判定外) | raw ¥395.12(1記事 ¥43.9) | ¥63.92(¥7.1) | +¥331.2 | 併記 | 差額のみ | | | |
- 符号検定(片側、同点除外): 人手介入 3対4(p=0.77)、Rewrite 3対2(p=0.50)、軽微JA 3対1(p=0.31)。いずれも有意でない。

## 3. ラベル要約(暫定)
- 出荷本文の重大見逃し: 新0 / 旧0(3 worker一致)。重大ラベルは meta旧のrejected本文(STOPで阻止)の境界1件のみ。
- 出荷本文に残る軽微(claim単位): JA 新5/旧9、EN Adv 新3/旧3、EN Std 新5/旧4。
- 境界例11件(B-01〜B-11): 出荷本文に残る4〜5件(space両腕の不在・秘匿の断定[基準(6)字義なら重大寄り]、byd新の見出し無留保[新腕のみ=要確認フラグ候補]、streaming旧の時制[低確信]、space新Advの単複差)、出荷されなかった/最終前6件(meta旧『そこで人間が』、central新R0の2件、openai新B1前のCMI主体、semi新R0/R1)。
- STOP9記事(新5・旧4)の妥当性: 重大(境界)1、軽微起因6、偽陽性2。B1 3発動=軽微2+問題なし1、完走1。案B(旧)3発動=全て軽微、成功1(openai)。Rewrite: 新2イベント(不要1)、旧7イベント(小数点断片起因6、軽微劣化2)。
- B3由来・AMBIGUOUS由来: 真の問題として確定したもの0件。機械候補(B3 新4/旧4、AMBIGUOUS 新2)はラベル上は偽陽性/問題なし。実際のB3由来STOP(semi新EN Adv)は機械候補の母集団外(新腕Checker未実行)。

## 4. Fableメモの検証(一致/不一致)
- 出荷本文の重大見逃し両腕0: **一致**。
- 新腕JA段の台帳外主張が少ない((ii) 2対15、R2 FC MAJOR 0対4): **部分一致**。数字は一致だが、旧(ii)15のうち7は案B前本文、最終JA由来に限ると2対8、ラベル上は旧(ii)の大半が問題なし(semi 4件は台帳内)、旧FC MAJOR4は重大(境界)1・軽微1・偽陽性2、space新JAにも旧腕と同型の不在断定が残り(ii)=0は検出器の注記依存の疑い(未検証)。軽微JA列の差(5対9)は小さい。
- 新腕EN STOP4件・B1 3件は軽微/偽陽性、B1純効果は疑問(¥103): **一致**。
- semiconductor新EN STOPはB3 qualifier由来(AMBIGUOUS由来でない): **一致(確認済み)**。briefの事実1末尾『Ledgerで確認されていない因果関係を付け加えないこと』が、ENの『この発表だけでは両者のつながりは説明されない』の源。
- central_bank新R0 STOPの『30年固定』範囲拡張に注記(周辺扱い)が影響した可能性: **部分的に支持(因果は未検証)**。注記は`name_embedded`=常に周辺とし【周辺数値】タグが付く。注記なしの旧briefと本文は同一でタグの有無だけが差。ただしbrief事実5・6が『固定型』『固定住宅ローン』と総称語を使っており、そこからの拡張の可能性もある。
- Checker小数点文分割: **一致**。旧Std 7 Rewriteのうち6件、軽微劣化2件(w3)。新腕にも断片は出るがQUALITY止まりでRewriteに至らず(理由は未検証)。
- 旧腕(ii)は案B前本文: **一致**(sha不一致で確認、small 3・byd 4)。
- **Fableの暫定所見にない食い違い(要対処)**: (a)`AGGREGATE.md`/`_13_result`は旧腕EN STOP 2件を『Advanced』欄とするが、成果物とrunログでは**Standard STOP**(small_bag旧・byd旧。Advanced本文は出荷済み)。正: 旧 Adv0/Std2、新 Adv2/Std2。(b)集計の『M1発火 新Std 2』は`attempt2`ファイルの存在=must-fix再生成でM1ではない(REPORT §110: M1はAdvanced枝のみ)。runログ`[OPEN243_M1]`は space新Advの1回のみ(B1前の本文で効き、B1後の最終Adv要約に不在断定が再出現)。w2の『byd新StdでM1発火』記述3行は矛盾(`qa_note`で記録、原本不変)。(c)集計の『初回MAJOR』は回復後の最終runのみ。回復前を含むAdv初回MAJORは新4/旧5(translation由来は新1/旧2)。

## 5. 人間確認パックの推奨3記事と理由(HUMAN_CHECK_E2E_01.md)
- **byd_recall**: 新腕JA最終にだけ見出し・冒頭の無留保描写の境界があり(w2が人間確認候補)、旧腕に同型なし。回答が重大なら新腕の要確認フラグが立つ唯一の候補。新腕EN Std STOPの起点JA文(交換の目的表現)も含む。
- **openai_copyright**: B1(Trial 3回目)後にEN Adv STOP。根拠は見出し一般化(軽微判定)。回復前JAにCMI除去の主体取り違えの字面(重大寄りの境界)。STOP妥当性・B1純効果に直結。旧腕に同型の主語省略を対照として提示。
- **central_bank_mortgage**: 新腕R0 STOPの根拠3件が全て軽微/重大の境界(30年固定の範囲拡張、『レンジ』脱落)。重大なら妥当STOP、軽微なら過剰ブロック。人手介入必要率の読みが変わる。旧腕は同じ台帳で完走・指摘0。
- workerの推奨(併記済み): w1=space_weapons・meta旧rejected、w2=byd_recall・central_bank_mortgage新・small_bag旧、w3=openai新Adv・semiconductor新Adv・streaming旧Std。w1のspace_weaponsは『台帳が補わないと指示しただけの事柄を示されていない/秘密と断定』という共通基準質問として1問(S-1/S-2)を追加(両腕に同型なので新旧の差には効かないが『出荷本文の重大0』の前提に効く)。

## 6. OPEN項目候補(起票はFable判断)
OC-1 Checker小数点文分割(不要Rewrite、軽微劣化) / OC-2 B3自動注記(人手注記は上限性能) / OC-3 EN段ja_source・translation MAJORの過剰ブロック(軽微でB1/案B/STOP) / OC-4 B1回復の扱い(純効果疑問、Trial上限の順序依存) / OC-5 B3注記の副作用(周辺扱い、qualifier文) / OC-6 集計scriptの帰属誤り(旧腕EN STOPのレベル、M1発火) / OC-7 FC/EN deviation判定の再現性 / OC-8 不在・非公開の断定と単複差の基準 / OC-9 M1のStandard枝未実装とB1後の再出現 / OC-10 面白さ比較(新931字対旧740字、pairwise未実施)。

## 7. 未確認・Fable判断要
1. 判定線の最終判定(特に、軽微JA列を『同等』とするか、n=9で『6対以上』が事実上達成不能な点の扱い)。2-6の総合は機械上『同等/混在』。
2. 境界例11件、特にB-05(byd新、新腕のみのフラグ候補)とS系(space両腕の不在断定)のユーザー回答。
3. 集計script(`er052_factlock_astra_e2e_final_aggregate_01.py`/`aggregate_01.py`)の帰属誤りの修正要否(runs配下・AGGREGATE.mdは編集していない。別委任)。
4. B1上限(Trial 3回)の順序依存でsemi新が拒否された反実仮想は未実施(cherry-picking禁止のため再実行していない)。
5. central新R0 STOPと注記(周辺扱い)の因果は未検証(アブレーションは再生成となるため行っていない)。
6. 請求ダッシュボード照合未実施(Astra単価はTrial/DEV登録、guardはx1.5)。
7. 旧腕Standard Checkerの小数点断片が新腕でRewriteに至らなかった理由は未検証。
8. Production採用提案を行う場合は、Opus独立技術レビュー(条件C)が必要。本書は採用提案ではない。

## commit・raw URL
COMMIT_URL_PLACEHOLDER
