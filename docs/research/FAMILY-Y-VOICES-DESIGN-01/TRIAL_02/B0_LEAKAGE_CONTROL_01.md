# B0_LEAKAGE_CONTROL_01: Leakage整合の確認(OPEN-470、OF-Y3-06(a))

Status: 実測完了(DEV/Trial、判定器・Prompt・コードは変更なし)。費用0.725円(gpt-6-luna high × 3 call)。証跡=`er110_output/family_y_persona_trial_01/school_phone_ban/b0/`(run1〜3.json、b0_summary.json)。

## 目的
Opus所見OF-Y3-06: 「判定器を変える前に、変えなくてよいかを確認する」。旧Y Trialでは事実が本文から0件になった(Leakage判定がVoice内の事実文をFAILにし、書換えが削除した)。
Persona→Voice設計では、Persona Sheetが許容する事実(V1=JP-03)を**本人主語の伝聞・印象で1文**だけ述べる。この形が**現行の判定器(許容リストなし、旧B承認13項目の日本語移植、gpt-6-luna high)でPASSするか**を先に確認する。PASSすれば、判定入力の調整(ア': 許容リストの導入)は不要で、区分問題(Y Trial限定の判定入力の調整)も発生しない。

## 方法
- 判定器: 旧Y Trialの`build_leakage_prompt`/`run_leakage_check`をそのまま使用(許容リストなし)。judge=gpt-6-luna、effort=high(M7校正済み)。
- control: 手書きの3つの短いVoice(base A=父親型/B=養護教諭型/C=生徒型、各約120〜150字、事実なし)の4文目に、次の1文を挿入。
  - **P(positive)**: 「俺が聞いた話だと、国も高校は校内で使うのを控えさせる考えらしい。」(本人主語・伝聞・数字/調査名なし。JP-03の許容表現)
  - **N1(negative)**: 「調べた研究では、校内の使用を制限した高校のほうが、授業に集中しやすいという結果が出ている。」(研究が主語・報告調)
  - **N2(negative)**: 「ある研究が、禁止した高校では生徒の集中が上がると示したらしい、と聞いた。」(研究が主語の伝聞形=伝聞に見せかけた漏出)
- 3 runで、(base, 挿入文)の組をラテン方陣で回転(各variantが全baseを1回ずつ通る)。1回の判定に3 Voice+中立的なTension段落(手書き)を渡す。アンカリング対策として各variantが全baseを経由する。

## 結果
| variant | run1 | run2 | run3 | 期待 | 結果 |
|---|---|---|---|---|---|
| P(本人主語の伝聞1文) | PASS(base A) | PASS(B) | PASS(C) | PASS | **3/3 PASS**(FAIL項目0) |
| N1(研究主語・報告調) | FAIL(B: evidence_subject, discovery_syntax) | FAIL(C: 同) | FAIL(A: evidence_subject, numbers_foreground, unknowable_analysis, discovery_syntax) | FAIL | **3/3 FAIL** |
| N2(研究主語の伝聞形) | FAIL(C: evidence_subject, discovery_syntax) | FAIL(A: 同) | FAIL(B: 4項目) | FAIL | **3/3 FAIL** |

## 結論(OPEN-470)
1. **現行の判定器は、本人主語の伝聞1文を誤ってFAILにしない**(P 3/3 PASS)。一方、研究が主語の文(報告調・伝聞形を問わず)は3/3 FAILで検出される。判定器の目的(研究報告調・解説者化・無自覚な漏出の防止)は保たれたまま、Sheetが許容する事実の自然な使い方が通る。
2. 従って**ア'(許容リストを判定入力に追加する案)は不要**。判定器・判定入力・定義は変更しない(区分「Y Trial限定の判定入力の調整」は発生しない)。
3. 旧Trialで事実が0件になった主因は、判定器ではなく(i)Voiceの事実が米国論文の報告文形式だったこと、(ii)書換え規則`:568`が「調査・統計・制度の説明をしない」で伝聞文まで削除させたこと、(iii)事実タグ規則が「〜という」型を誘導したこと、と整理できる。本Trialでは(i)(ii)(iii)に対応するWriter Prompt(伝聞形の例示、禁止の具体化)と書換え規則(`調査・統計・制度を説明する文は書かない(許容事実の伝聞1文は除く)`)のみを改訂した。
4. M7見逃し回帰は、判定器が不変のため省略した(OF-Y3-06(a)成立時の省略、約3円削減)。
5. 本Trialの実運用での事実使用: V1のJP-03は任意としていたが、最終稿it2(および1回目it1)のV1は事実を使わなかった(0件)。Sheetは「0件でも不合格にしない」方針(件数の目的化を避ける)。実Trialでの事実の自然な織込みの実証は未達で、controlでの判定器挙動の確認までが根拠である(範囲の限定)。
6. 限界: controlは手書きの短文で、3 run、1判定器(gpt-6-luna)。実際のVoice生成が伝聞形で事実を書いたときの挙動(例: 「国も〜らしい」型)は上のPのみで確認。条件が変われば再確認が必要。
