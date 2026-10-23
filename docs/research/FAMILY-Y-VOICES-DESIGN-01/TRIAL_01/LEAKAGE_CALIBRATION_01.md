# LEAKAGE_CALIBRATION_01: 日本語版Leakage Checkの事前校正(M7、FAMILY-Y-VOICES-DESIGN-01 委任_04 段階(0))

実行日: 2026-10-23(JST)。run dir: `er110_output/family_y_trial_01/m7_calibration/`。コード: `er110_family_y_m7_calibration_01.py`(実行)・`er110_family_y_m7_aggregate_01.py`(集計)。Check本体: `er110_family_y_text_trial_01.py` の `build_leakage_prompt`/`run_leakage_check`(旧B `er012_b_family_voices_writer_generic_01.py:1028-1062`の7項目[Voice]/6項目[Tension]を日本語へ移植。Closing項目は最終パート規則へ吸収)。

## 方法(事実)
1. 旧B(3 Voices)の英語記事7件(NG 5件=旧英語版Checkがflagした個体[3V汎用化Regression attempt1・n2 attempt3、Person-Voice Trial-02 attempt1、AI hiring A2再評価、Fact Safety attempt1]、OK 2件=旧Checkが0件だった個体[Person-Voice Trial-02 attempt2、AI hiring B1再評価])を、旧Check JSONの`prompt`から本文4セクション(Voice1〜3/Tension)として抽出し、gpt-6-luna(effort low)で日本語に忠実翻訳(校正データ作成用。要約・分析的表現の除去をしない指示)。
2. 日本語版Checkを3条件で判定: (A)日本語化×gpt-6-luna(effort high=旧Gateの構成に最も近い)、(B)日本語化×gpt-6.1-sol(effort medium、最新最上位系との比較)、(C)**英語原文**×gpt-6-luna(同じ新Promptを英語本文に適用し、「日本語化」の影響と「Prompt/判定器」の影響を切り分ける)。
3. 正解ラベル=旧B英語版Checkの判定(承認済みGateの判定)。ユーザー指摘の記録がある個体はAI hiring A2(統計文2件、`INVENTORY_OLD_B_VOICES_01.md`§6)。**限界**: ラベルは旧Check自身(同系統のLLM判定)に由来し、独立した人手正解ではない。n=7(NG5/OK2)・3 Voicesのみ。

## 結果(事実。数字=FAILした項目数/セクション)
| item | 区分 | 旧B(英語)判定 | (A)日本語×Luna high | (B)日本語×Sol medium | (C)英語原文×Luna high |
|---|---|---|---|---|---|
| NG1 3V汎用化Regression a1 | NG | v1:2 v3:3 T:3 | v1:3 v3:4 T:2 | v1:2 v3:3 T:3 | v1:1 v3:2 T:2 |
| NG2 Person-Voice Trial-02 a1 | NG | v1:1 v2:1 v3:2 | v1:4 v2:4 v3:1 | v1:3 v2:3 v3:1 | v1:3 v2:3 v3:3 |
| NG3 AI hiring A2(ユーザー指摘個体) | NG | v2:2 v3:2 T:2 | v1:1 v2:3 v3:1 T:1 | v1:1 v2:1 | v3:2 |
| NG4 Fact Safety a1 | NG | v3:3 | v3:4 T:1 | v1:1 v3:3 | v3:4 |
| NG5 3V汎用化Regression n2 a3(外部統計文) | NG | v1:3 v2:3 | v1:3 v2:4 | v1:2 v2:2 | v1:3 v2:3 |
| OK1 Person-Voice Trial-02 a2 | OK | なし | v1:1 | v1:1 v2:1 | v1:1 v2:2 |
| OK2 AI hiring B1 | OK | なし | v1:1 v2:1 v3:1 T:1 | v1:1 v2:1 | v1:1 v3:1 |

集計(`er110_family_y_m7_aggregate_01.py`の出力): 
- 記事単位(any_flagged): (A)(B)(C)とも **NG 5/5をflag(見逃し0)、OK 2/2もflag(特異度0/2)**。
- セクション単位(旧ラベル有無との一致、4セクション×7件=28): (A)TP12/FN0/FP7/TN9、(B)TP10/FN2/FP6/TN10、(C)TP10/FN2/FP4/TN12。
- 費用(実費、`raw_usage_log.jsonl`): 翻訳0.64円+(A)3.11円(約0.44円/件)+(B)22.69円(約3.2円/件)+(C)2.53円=**合計28.96円**(設計見積5〜20円を超過。主因=Sol medium比較。事前見積は「Sol数件」としていたが、判定器比較の信頼性のため全7件を実施)。

## 所見(Sonnetの読み。事実と区別)
1. **見逃しは0**。外部統計文(NG5「約半数は…」「約90パーセントは…」)・調査が主語の文・ユーザー指摘個体(NG3)の中心文は、日本語版でも(A)(B)両方が検出した。日本語移植で検出力が落ちた兆候はない((C)英語原文より(A)日本語の方がセクション単位のTPが多い)。
2. **OK 2件もflagされたが、日本語化の影響ではない**((C)英語原文でも同じ箇所がflag)。flagされた文は、OK1/OK2のVoice 1が「〜について読んだことがある」と他者の被害事例を長く語る部分(evidence_memorable)、Voice 2の「ある会社の公開通知は、その責務を具体的なものにしている」(evidence_subject、文の主語が資料)など。Y設計の編集意図(本人の経験が主役・他者の具体的行動を語らない・文の主語を資料にしない)に照らすと**真の指摘と読める**ものが多く、旧英語版Checkが当時PASSさせた(見逃し候補、または判定の揺れ)可能性が高い。独立した人手ラベルがないため、特異度は「評価不能」とし、**Phase 1では人がflag箇所を全件確認**する。
3. 判定器の選択: 見逃し0・NG検出の網羅は(A)(B)同等。(A)は旧ラベル付きセクションのTPが最も多く(12/12)、旧Gateの構成(Writerと同系統・effort high)に最も近く、費用は(B)の約1/7。(B)はNG3の旧ラベルvoice_3/tensionを検出できなかった(FN2)。→ **Phase 1のGate判定器はgpt-6-luna(effort high)とする**(承認済みGateの構成の継続。最新最上位系原則[25節]の例外として、費用差と検出網羅の同等性を根拠にここへ明記。Writerは全てgpt-6.1-sol)。
4. 判定のばらつき: 同じ記事でも判定器・言語で件数が揺れる(NG3は(A)6項目/(B)2項目/(C)2項目)。単一回のflag件数は「発生・悪化・改善」の比較に使うが、小さな差は判定ノイズとして扱う(Phase 1ではflag外段落の判定反転を`judgement_noise_unchanged_paragraphs`として記録)。

## 判定定義の調整
**調整なし**。移植時の言語上の変更は、`leak_discovery_syntax`に日本語の例(「〜が明らかになった」「〜という傾向がある」)を加えたこと、「Narrator」を「語り手」、survey等を「調査・研究・データ・割合・報告」とした言い換えのみで、判定基準・閾値・項目数は旧B承認版のまま(7項目/6項目)。見逃しが0であり、調整が必要な悪化(M7の調整条件)は確認されなかった。**定義調整の範囲を超える問題は見つからなかった(ユーザー判断事項なし)**。

## 残る不確実性
- 特異度(過検出)は独立ラベルなしでは測れない。Phase 1の人手確認で補う。過検出が多い場合はGateが書き換えを乱発し、人物の自由な発言を損なう(対策が強すぎる)恐れ → WRITER_COMPARISON_01.mdで評価。
