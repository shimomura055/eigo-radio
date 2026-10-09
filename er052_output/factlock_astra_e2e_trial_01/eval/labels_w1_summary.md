# labels_w1 要約(委任_14a、worker1: meta / hormuz / space_weapons、2026-10-09)

- **注意: 全ラベルはSonnetの暫定推測(`label_source=sonnet_w1`)で、人間確認の代替ではなく確定扱いしない。** Fableが突合し、ユーザーが2〜3記事を人間確認する前提。判定線の評価・VALIDATED等の宣言は行っていない。
- 基準: `docs/pm/open233_materiality_criteria_2026-10-03.md`(重大/軽微/問題なしの線引き、正式採用版5節)。単複差(K05〜K07型、5-3 #2)と「不在・非公開の断定」(基準(6)字義なら重大寄り)は**境界**として軽微に寄せ、確信度を下げて記載。
- 明細: `labels_w1.jsonl`(171行。kind=ja_fc/en_dev/ii/checker_stage2/reclassify/rewrite/m1/m3/b1/b3_origin/shadow/residual_miss/residual_check/rejected_body/stop_review/no_body/no_finding)。
- 限界: ① 旧腕のJA original/R1本文と、旧腕・新腕のattempt1の一部本文はrunに保存されておらず、FC引用文のみで判断した行は確信度を下げた(meta old R2 attempt1、hormuz old original attempt1)。② Checkerのstage2は既定「問題なし」でも、全94行を目視(precheck戻しは文型への誤反応、LLM指摘は評価・推論・修辞)で確認した。③ 台帳照合は担当3テーマの台帳(meta/hormuz/space_weapons、新旧同一)のみ。

## 1. テーマ×腕の要約表
ツール指摘(JA FC/EN deviation/(ii)/Checker stage2)に対する私の暫定ラベル件数。「重大」は境界を含む。同一claimの断片重複行も別行として数える(Checker)。

| テーマ | 腕 | 到達 | ツール指摘件数 | 私のラベル: 重大/軽微/問題なし | 出荷本文の重大見逃し | 備考 |
|---|---|---|---|---|---|---|
| meta | new | 完走(Adv/Std Checker=DOWNGRADE) | 12 | 0 / 1 / 11 | 0 | 軽微1=Std「mistake to start a test」条件省略(次文で復元)。M1/B1/M3なし |
| meta | old | JA STOP(R2) | 2 | 1(境界) / 1 / 0 | 本文なし(rejected本文に重大境界1) | 重大境界=「そこで人間が担当」(因果・設計意図の創作)。attempt1のMAJORは軽微寄り |
| hormuz | new | B1後に完走 | 30 | 0 / 4 / 26 | 0 | B1発火理由=Brent→oil prices(軽微)。回復後は解消。Std Checker軽微3 |
| hormuz | old | JA STOP(original) | 2 | 0 / 1 / 1 | 本文なし(rejected本文に重大0) | 最終MAJOR=ガソリンの一般論(問題なし)→不要STOP寄り |
| space_weapons | new | JA B1後、Adv完走(Rewrite) / Std EN STOP | 34 | 0 / 12 / 22 | 0(Adv)。Std本文は出荷なし、rejected本文に重大0 | 軽微=不在・秘匿の断定(JA由来)と単複差(translation)。B1の発火理由は問題なし |
| space_weapons | old | 完走(Adv/Std Checker=DOWNGRADE) | 28 | 0 / 4 / 24 | 0 | 軽微=不在・非公開の断定、Stdの「first public statement」ずれ(Checker取りこぼし) |

## 2. 重大見逃し一覧(最終本文に残った重大Fact)
- **出荷(採用)された本文に残る重大Factは、担当3テーマ・両腕とも0(私の暫定判断)。**
- 境界(重大寄りの軽微): space_weapons new Adv(Rewrite後)の「Special Attack Is Secret / remain secret / have not been given / has not disclosed their capabilities」4箇所と、space_weapons old Adv/Stdの「name/capabilities have not been made public」。台帳は非公開と明記しておらず(F-001 notesは書き手への「補わない」指示)、基準(6)字義なら重大になりうる。私は核心(配備を公に認めた)が保たれるため軽微に寄せた(確信度0.5)。Fableが重大扱いにする場合、両腕とも見逃しが4〜5件で数は大差なし。
- 境界(単複差、K05〜K07型): space_weapons newの「Russia has destroyed satellites… these were tests」(台帳はCOSMOS 1408の1件、JA原文は数を明示せずEN訳で複数化)。Advは機械floorのRewriteで修正(COSMOS 1408、missiles複数形のみ残存)。Stdはこれが原因でEN STOP。5-3 #2(未決)に依存。
- 出荷されなかった本文: meta old(rejected_ja_r2.md)に「そこで人間が電話を担当する」(重大境界、STOPで阻止)。hormuz old・space_weapons new Stdのrejected本文には重大なし。
- 以上のうちChecker最終出口が見逃した(DOWNGRADEで通過した)軽微は: 不在断定(両腕)、space old Stdの「first public statement」(reclassifyのSUPPORTED除外)。いずれも重大ではない。

## 3. STOP・B1・M1・M3の妥当性(暫定)
| 事象 | 私のラベル | 要点 |
|---|---|---|
| meta old JA STOP | 概ね妥当(重大境界) | 「そこで」の因果創作。基準が緩ければ回避も可 |
| hormuz old JA STOP | 不要STOP寄り | 最終MAJORはガソリンの一般論(問題なし) |
| space_weapons new Std EN STOP | 軽微(境界)によるSTOP | 単複差。機械floor(changed_number)の適用結果 |
| hormuz new B1 | 発火理由は軽微 | B1枠を軽微で消費したが、回復後は解消 |
| space_weapons new B1 | 発火理由は問題なし(hook修辞) | B1枠を問題なしで消費。回復後JAは不在断定(軽微)が増え、EN訳の複数化でStd STOP。回復の純効果は疑問 |
| space_weapons new M1(Adv) | 発火1回、有効 | 要約の不在断定が削除された(本文の同型は残る)。他テーマは発火なし |
| M3保護 | 担当3テーマはすべて0 | 保護で拾えた/拾えなかったclaimは観察不能。旧腕の影も0 |

## 4. 追加所見(Fable判断用)
1. EN deviation checkの再現性: space_weapons newで同一本文に対しactual=COMPLIANT / shadow alt=MAJOR(複数形)。Advはdeviation通過、Checkerが機械floorで検出と、ツール間の不一致がある。
2. (ii)検出の腕間比較可能性: 同型の不在断定が旧腕では(ii)で検出され(space old 2件)、新腕では(ii)=0。新腕R0の事実タグ付けの影響の可能性があり、(ii)差の解釈に注意(要確認)。
3. precheck(決定論)の誤反応: Checker stage2の94行中、私が「問題あり」と見たのは15行のみ(軽微)で、残りは否定・譲歩・比喩の文型や関連fact割当違い(例: 20%がHF-009に紐づく)への誤反応。Rewrite・STOPには至らないが、stage2のコスト源。

---
注: 本書は暫定ラベルの要約であり、判定線の評価・採用推奨は含まない。ラベルのconfidence(0.35〜0.8)を参照して扱うこと。
