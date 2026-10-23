# RULE_CONSISTENCY_01: 承認済みgloss規則「全語反映」・mapping検査と G2/G3 出力の整合(OF-KPGM-BE-06、原則8)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_08 / 2026-10-23 / API 0・Production変更0(read-only照合)
問い: 承認済みgloss規則「目的語・補語・修飾語を含むすべての語」とmapping検査は、G2/G3の出力(例: G3 `reach for someone's wallet`→「財布に手を伸ばす」はsomeone'sを訳さない)と矛盾するか。G2/G3採用で規則文・検査の変更が要るか。

## 0. 結論(先頭)
1. **規則文・検査の変更は不要**(矛盾なし)。G2/G3は「語」ではなく「フレーズ全体の意味」を過不足なく表す点で承認済み規則と同じ向き。
2. 「全語反映」という文言は**新規生成には直接は適用されない**(適用されるのは既存glossの整合判定=指示1。新規生成は`NEW_GENERATION_TEXT`が指示2の『そのまま返す』と合わせて置換し、基準は『最終key_phrase全体の意味に過不足なく』)。
3. **mapping検査(`check_added_word_mappings`)は新規生成itemでは実質空**(必須対象=canonicalizationが候補に追加した内容語のみ。fulltext新規itemはdisplay=keyで0語)かつ**record-only**(Productionは`mapping_gate`を渡さない=既定False)。someone'sを訳さない出力で不合格にならない。
4. 「人の財布」(=盗む読み)を誘発した直接要因は「全語反映」文ではなく、**`PERSON_CONSTRAINT_TEXT`の例示**(『誰かの』『人の』『人を』)と見るのが妥当。ただし同文は「不定の人称を訳出すると不自然になる場合は人称を明示しない自然な表現にしてかまいません」と**省略を許容**しており、G3の出力は規則違反ではない。
5. 残る曖昧さ(`ユーザー判断事項`ではなく**情報**): 「全語反映」の字面は、慣用句の意味単位訳と一見緊張する。採用時に規則文を直す必要はないが、**G3ブロックの『語ごとの直訳は案にしない』が『全語反映』を弱めると誤読されるリスク**はLLM判定(`qa_reflects_all_key_phrase_words`)側の挙動で、Trial_03の出力ではFAIL/誤訳の増加として観測されなかった(Sonnet参考値 FAIL: G0 4/120、G2 3/120、G3 2/120)。

## 1. 照合した規則と検査(file:line)
| 項目 | 内容 | 出典 |
|---|---|---|
| 指示1(全語) | 「current_japanese_glossが、最終的なkey_phrase全体(目的語・補語・修飾語を含むすべての語)の意味と過不足なく一致しているかを判定(current_gloss_consistent)」。**対象は`current_japanese_gloss`(既存gloss)の整合判定** | `er003_key_words_gloss_alignment.py:585-588` |
| 指示2 | 一致していれば返す。不一致なら最終key_phrase全体に一致するglossを返す | 同:589-593 |
| 末尾 | 「key_phrase全体の意味を反映できている場合のみqa_reflects_all_key_phrase_wordsをPASS」 | 同:603-604 |
| 新規生成 | `current_japanese_gloss=null`は`current_gloss_consistent=false`・新規書下ろし。「最終key_phrase全体の意味に過不足なく一致」。指示2の『そのまま返す』は適用されない | 同:315-321(`NEW_GENERATION_TEXT`)、:576 |
| 人称 | 不定の人称は日本語でも不定のまま(『誰かの』『人の』『人を』)。**「不定の人称を訳出すると不自然になる場合は、人称を明示しない自然な表現にしてかまいません」** | 同:301-312(`PERSON_CONSTRAINT_TEXT`)、:575 |
| 決定論検査(人称) | 具体人称(あなた/彼/私…)の混入だけを不整合とする。**省略は検出しない** | 同:205-224(`person_reference_mismatch`) |
| mapping検査 | `added_content_words(display, key)`(候補に追加された内容語、機能語除く)が日本語spanで覆われるか。**record-only(gate化はユーザー承認事項)** | 同:511-、:16-17、:663-666(`mapping_gate`既定False)。Production呼出元は`mapping_gate`未指定(`er003_v1_n3_01_scaffold_generate.py:532`、`er026...:1347`) |
| gloss承認規則(抽出) | 平易・括弧禁止・~可・数字は漢数字・数値穴埋め句は選ばない。**語の全訳を求める文は無い** | 実行時抽出(`load_approved_gloss_rules(include_numeric_rule=True)`、本調査で出力確認) |

実測(本調査): `added_content_words("reach for someone's wallet", "reach for someone's wallet")`=`[]`、`keep someone company`=`[]`。→ 新規生成itemではmapping検査の必須語が0で、someone'sの有無は検査されない。

## 2. 問いへの回答
(a) **規則文は新規生成項目にも適用されるか**: 「全語」の文言は指示1(既存gloss判定)で、新規生成には`NEW_GENERATION_TEXT`の「全体の意味に過不足なく」が適用される。末尾の`qa_reflects_all_key_phrase_words`(全key_phrase語を反映)は新規生成にも適用されるが、これはLLM自己判定(PASS/FAIL)であり、判定基準は「意味の反映」。someone'sを訳さなくてもフレーズ全体の意味が表れていればPASSとなる。決定論の検査はこの観点を持たない。
(b) **G2/G3採用時に規則文・検査の変更は必要か**: 不要。G2/G3のブロックは`【日本語グロスの規則(承認済み選定Promptと同一)】`の**直前に挿入**する(Trial実装と同じ位置、`er112_kp_gm_trial_02.py gloss_call`)ため、承認済み規則文は逐語のまま残り、`rules_sha256`(`load_approved_gloss_rules`の抽出結果)は不変。`mapping_gate`も既定のまま。
(c) **最小変更案(必要な場合)**: 変更不要のため案は置かない。念のため選択肢のみ記録する。
   - 選択肢1(推奨): 変更なし(G2/G3ブロックのみ追加)。
   - 選択肢2: 指示1の括弧「(…すべての語)」を「(…すべての語の意味)」へ明確化 → 承認済み規則文の変更であり、効果は未測定。**現時点では提案しない**(原則1: 磨き込みをしない、原則8: 変更時は影響確認が必要)。
   - 選択肢3: `mapping_gate=True`化 → 新規生成itemでは必須語0で効果なし、かつgate化はユーザー承認事項。不要。

## 3. 観測(Trial_03のsomeone's/one's/oneselfを含むKP)
| KP | G0 | G2 | G3 | 備考 |
|---|---|---|---|---|
| reach for someone's wallet(難例) | 人の財布に手を伸ばす / 誰かが自分の財布に手を伸ばす | 人が自分の財布に手を伸ばす / 人が支払いを覚悟する | 誰かの財布に手を伸ばす / 財布に手を伸ばす | **3 armとも人称を訳出する出力が混在**(省略は G3 rep2のみ)。gold(支払おうと財布に手を伸ばす)に照らし、全armが不安定 |
| lose trust in someone | 人への信頼を失う ×2 | 同 | 同 | 不定人称を『人』で保持 |
| speak against someone | 人を批判する ×2 | 人を批判する ×2 | 人を批判する / 誰かに反対する発言をする | |
| in one's place | 人の代わりに ×2 | 人の代わりに ×2 | 人の代わりに / 誰かの代わりに | |
| room for one's own pace / a place of one's own / change one's surroundings | 自分の… | 自分の…/身の回りの… | 自分の…/周りの… | 再帰one'sは『自分の』(規則どおり) |
→ 「someone'sを訳さない」のはG3に特有の系統的挙動ではなく、**G3 rep2の1出力**のみ。G3が承認済み規則から逸脱する系統的傾向は観測されなかった。

## 4. 残リスク・次の一手
- `reach for someone's wallet`は全armで不安定(Sonnet参考値 G0 F/T、G2 T/F、G3 F/T)。これはStd glossの個別KPの意味決定(支払いの含意)の問題であり、規則整合の問題ではない。個別KP対策(few-shot等)は禁止(委任_08 §3)。Fable盲検で最終判定。
- 規則整合上の追加作業は無い。`WIRING_DESIGN_03.md`ではG2/G3ブロックの挿入位置を現行規則の直前に固定する。
