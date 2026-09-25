## 管理ID
`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`(修正1回目: REPORT §11〜§13の`[Fable記入]`置換のみ)。**並行タスクあり**: `NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(er003_*/er012_*/SSOT、標準ACTIVE_TASK/RESULT_PACKET)が実行中。本タスクは`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`と自タスクのdelegation_logのみ触る。一時ファイル`docs/pm/ACTIVE_TASK_KP.md`/`RESULT_PACKET_KP.md`。API呼び出し禁止。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer必須。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/KEY-PHRASE-LEVEL-SPEC-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_KPへ1行(FAILでも継続)。

## 作業
REPORT §11/§12/§13 の`[Fable記入]`(Grep `\[Fable記入\]`、3箇所)を以下で置換。他は変更しない。

§11:
```
### 11.1 一致判定(Fable、同義・学習単位を含む)
- Sewer Standard: instead of(一致)/take care of the rest(学習単位は take care of と同じだが不要語付加=切り方×)/joining together・hard to find・grow old(不一致、汎用句としては妥当)。Topic Word(sewer)未選択。→ **2/5 FAIL**。
- Sewer Advanced: replace A with B(完全一致)/take care of the rest(Standard級かつ不要語付加)/hard to find where A is damaged(記事固有の固定化)/come in・move A closer to B(不一致)。main artery / treatment plant / be connected to / septic tank すべて未選択。→ **1/5 FAIL**。
- Meta Standard: 期待の in other words / put ... on hold / raise concerns / there is nothing wrong with … / AI agent はいずれも未選択。not always a bad thing は意味的に近いが別Phrase、contain personal information はAdvanced期待の personal information に近い。→ **0〜1/5 FAIL**。
- Meta Advanced: raise concerns(raise privacy concerns と同一学習単位、切り方は許容)/put A on hold(一致)/on A's behalf(良い汎用句)/fill in・appear to be(不一致)。behind the curtain / personal information / human concierge 未選択。→ **2/5 FAIL**。
- 全体: 5/20(25%)。目安60%を大きく下回る。

### 11.2 構造的な観察
- **Topic Word枠が4回とも未使用**: 「任意」と書いたため、記事の中心テーマ語(sewer / septic tank / AI agent / human concierge)がすべて落ちた。
- **句の種類が動詞句に偏る**: 「1 Phrase=1学習ポイント」「不要語を付けない」の指示が、名詞複合語(treatment plant / personal information / main artery)や談話標識(in other words)を避ける方向に働いた。
- **レベル配分が期待と逆転**: put ... on hold / raise concerns はStandard期待だったがAdvancedで選ばれ、Standardは tell … what you need / feel safe など基本動詞句に寄った。
- **Prompt内の禁止例が守られない**: Advanced Promptで明示した「take care of the rest ではなく take care of」が、Sewer Standard/Advanced両方で take care of the rest として出現。指示の「例」だけでは抑止できていない。
- 費用¥1.13、4 callとも`gpt-5.6-luna`。Production変更ゼロ確認済み。
```

§12:
```
**REJECTED(Trial Prompt v1)**。ユーザーの選定方針そのものではなく、方針をPromptに落とした第1版が狙いのPhraseを再現できなかった(全4セットFAIL、25%)。Production変更なし。
```

§13:
```
1. Prompt v2での再Trial(4 call、¥2以内)を承認するか。v2の変更候補(Fable案、答えの漏洩は避け一般例のみ): (a) Topic Wordを「記事に中心テーマ語があれば通常1個含める」に変更、(b) 句の種類の多様性を要求(談話標識/句動詞/コロケーション/再利用しやすい名詞複合語 から偏らずに選ぶ、他分野の一般例で示す)、(c) 「不要語を付けない」の禁止例を、例示ではなく出力後の自己点検指示(各Phraseから記事固有語・余分な語を削れるか確認)に変更、(d) Standard/Advancedの差を「Advancedは基本句(A2級)を避け、Standardで選びそうな句は除く」と明示、(e) 記事固有の固定化(hard to find where A is damaged型)の禁止を明示。
2. 想定セット自体の妥当性確認: Meta Standard期待の in other words / there is nothing wrong with … は談話・定型表現であり、現Promptの「再利用性」定義に含まれることを明記する必要がある(ユーザーの意図確認)。
3. 既存Production Key Phrase仕様との関係: 現行Production(記事固有の中心語を上位に選ぶ傾向)を置き換える前提か、併存(Topic Word枠)か(方針確認、今回は判断不要)。
```

## Git
明示add: `KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/KEY-PHRASE-LEVEL-SPEC-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `KEY-PHRASE-LEVEL-SPEC-TRIAL-01: REPORT §11-13 Fable参考評価(全4セットFAIL・Topic Word未使用・動詞句偏重)・REJECTED(Prompt v1)・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: KEY-PHRASE-LEVEL-SPEC-TRIAL-01`

## 報告(RESULT_PACKET_KP)
0. T-0 1. 置換箇所と`git diff --stat` 2. commit SHA・push 3. 一覧外Read理由。
