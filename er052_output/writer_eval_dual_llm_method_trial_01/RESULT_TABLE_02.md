# RESULT_TABLE_02: 追加Trial 結果(自動生成 aggregate_02.py、集計対象モデル=gpt-6-luna, gpt-5.6-luna, deepseek-v4-flash)

## 1. 横並び(label rep1/rep2)

| case | human_tier | gpt-6-luna | gpt-5.6-luna | deepseek-v4-flash |
|---|---|---|---|---|
| K01 | ユーザー確認済み(C、2026-10-09) | B/A | A/A | A/A |
| K02 | ユーザー確認済み | B/B | B/B | C/C |
| K03 | ユーザー確認済み(C、2026-10-09) | B/B | C/C | C/C |
| K04 | Sonnet暫定(未ラベル) | B/B | A/A | B/B |
| K06 | Sonnet暫定(ユーザー未裁定) | B/B | B/B | B/B |
| K08 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/A | A/A | A/A |
| K09 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/B | A/A | A/A |
| K10 | Sonnet暫定(因果語を含むため境界へ移動) | A/A | A/A | A/A |
| K11 | ユーザー判断(C寄り・Bの余地あり、2026-10-09) | B/B | B/B | B/B |
| K12 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/A | A/A | B/A |

## 2. モデル別指標

| model | M1判定(K01,K02,K03 x rep1,rep2) | M1 | C数(M1) | M2判定(K08,K09,K12) | M2 | M4自己一致 | K11 | 形式違反 | 実費JPY(登録単価) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna | BABBBB | REJECTED | 0/6 | AAABAA | PASS | 80% | B/B | 0 | 0.65 |
| gpt-5.6-luna | AABBCC | REJECTED | 2/6 | AAAAAA | PASS | 100% | B/B | 0 | 1.11 |
| deepseek-v4-flash | AACCCC | REJECTED | 4/6 | AAAABA | PASS | 90% | B/B | 0 | 6.06 |

## 3. モデル別Status(PREREGISTRATION_02 s6)

- gpt-6-luna: REJECTED
- gpt-5.6-luna: REJECTED
- deepseek-v4-flash: REJECTED

## 4. 状態と機械適用(部分結果: sol未実行)
- **gpt-5.6-sol は実行していない**(dry-run見積がJPY 40上限を超過のためSTOP、RUN_LOG_02.md 2節)。よって sol列・sol×deepseekペアの人間確認対象率・Trial全体のStatusは未確定。上表のgpt-6-luna/gpt-5.6-lunaは前Trialの既存結果(再実行なし)。
- DeepSeek(deepseek-v4-flash、応答model=`deepseek-flash`、実体V4.1-Flash): K01=A/A(**見逃し**)、K02=C/C、K03=C/C、K11=B/B(期待内)。M1: Aあり → **REJECTED**(事前登録式)。ただしC数は4/6で6-luna(0/6)・5.6-luna(2/6)を上回る。M2: K08=A/A, K09=A/A, K12=B/A → B/C 1件でPASS。M4=90%(ただしtemperature=0指定でもthinkingモードで実効性は不明、effective_paramsに'temperature': 0.0 と記録されるのみ)。形式違反0、実費JPY 6.06(rep1 3.90 + rep2 2.16)。
- 「改善」の定義(事前固定: C数が6-lunaを上回るかM1=PASS、かつM2=PASS)の機械適用: DeepSeek=該当(C 4/6 > 0、M2 PASS)。ただし「安定検出(M1全6判定C)」は未達(K01を両repで見逃し)。参考として gpt-5.6-luna も定義上は「改善」(C 2/6)だが、K01=A/Aで同様にM1=REJECTED。
- 解釈規則への適用(部分): DeepSeekは K02(不在断定)・K03 を安定してCにした点で「モデル/vendor依存の改善」の兆候あり。一方、K01(restored vs rolled back、意味の近い言い換えに見える方向反転)を両repでAとしたため、重大を「安定検出」とは言えない。Sol結果が出るまで、「両方でも安定検出できない」(方式の現実性への強い疑義)の判定は保留。
- 揺れる論点: (1) K01はDeepSeekの理由文が「restoredはrolled backの言い換えの範囲」と読んでいる。人間の確認(ユーザー確認済みC)と評価LLMの読みが分かれる型で、これが「プロンプトの3分類定義」の問題かモデル能力の問題かは本Trialでは切り分けられない。(2) DeepSeekはHC-012系(K01,K03,K04,K12)で判定が割れ、同一Fact偏重の限界を引き継ぐ。(3) DeepSeek 2rep間で K12(B/A)がブレた(M2は事前式でPASS)。(4) DeepSeekはモデル名が引退済みの旧名で呼ばれ実体が更新されている点(公式脚注)。
- 成功しても「LLM Checkerが客観的に正しい」とは結論しない。n=10、重大3件(+参考1)の機能確認。
