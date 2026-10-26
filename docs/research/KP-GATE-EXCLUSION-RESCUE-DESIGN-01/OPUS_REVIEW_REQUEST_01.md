# OPUS_REVIEW_REQUEST_01 (条件A: 新しい処理フロー「違反検出→修正→再検査→HR登録」をX/Y/Z共通核へ加える設計の独立レビュー依頼文案)

依頼者: Fable(本文書は案。Opusへの依頼は設計受領後にFableが行う)。対象: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/DESIGN_01.md`(段階1を中心に)。
前提: 調査・設計のみ。Production変更なし・API 0。ユーザー原則=「8件に届かないこと」ではなく「適切に修正できる候補まで捨ててしまうこと」を解決する。承認済み品質規則(5語以下・本文対応・Rule7・正規化・数合わせ禁止・最大8・NG復活禁止)は変えない。

## レビューしてほしい重要論点(これ以外は不要)

1. **「本文対応」の定義の保持**: 救済は(a)元span内のtoken置換(再導出)、(b)無変更revert、(c)[段階2c]元句の連続部分列に限る。この3つは「本文との対応関係を失わない」と言えるか。とくに(c)で`too`を落とすと意味が反転する例(`too soon to wave a flag`→`soon to wave a flag`、RESCUE_ANALYSIS_01 §3.1)があり、決定論Gateは区別できない。段階2cを(LLM提案+HR選択+`auto_eligible=False`)に限る歯止めで足りるか。
2. **Rule7との整合**: 段階1は受理面を広げない(revert=『無変更』、再導出=現行validator通過のみ)と主張している。この主張に穴はないか(例: 再導出の候補生成で`_token_pair_ok`の判定をすり抜ける組合せ、`role_ok_poss`未渡しによる所有格の過受理、`_verb_base_candidates`が作る非語の混入をCMUだけで防げるか)。また`er105:575`の設計意図「V+名詞等は基本形化せず表層形のまま」を、revertで『表層形のまま残す』ことは尊重しているか。
3. **重複/順位/NG復活禁止との整合**: 救済候補を元の`raw_rank`位置に戻す設計(AIは順位を付け直さない)、`_containment`/Redundancy QA/finalizeの再適用、NG判定を「元句」と「救済後句」の両方に行う設計、外側retryの条件(`n_auto<3 かつ gate_dropped`)とOPEN-456 F1の累積除外リストの扱い(救済成功は累積しない、失敗は累積する)に矛盾や抜けはないか。救済候補を`n_auto`に数えない(`auto_eligible=False`既定)判断は、外側retryの発動頻度を意図せず上げないか。
4. **LLM修正の必要最小範囲**: 段階1はLLM追加0、段階2cのみ新規1 call(新Prompt)。Prompt 2/2-Vはsha固定のため新Promptが必要になる点、およびcanonicalization LLMの出力を決定論で書き換える際にQA 12項目(`qa_meaning_or_usage_unchanged`等)を「救済前のkeyに対する判定」として残す扱い(`qa_fail`旗に倒すか、`auto_eligible=False`で足りるか)は適切か。LLMを呼ばずに足りる範囲が他にないか。
5. **X/Y/Z共通核での副作用**: 実装位置は`run_canonicalization_gate(postprocess=)`(`fulltext_p2`のみ)。(i)`postprocess_possessor_roles`との順序(roles検証後に再導出を置く)、(ii)A/B/C旧経路が`_is_ft=False`で無影響であること、(iii)Z限定のSRC D1/人称整合が救済後itemに通常どおり適用されること、(iv)Yの正式経路が未存在(DECISION_LOG.md:50のOPEN-484)でも共通moduleとして問題ないか。
6. **見落とし・過剰な制約**: 本設計が見落としている除外パターン(例: 選定段の`call1`側gate失敗は`sc.run_key_phrase_selection`内retryで、`generate_candidates`のitem単位dropとは別経路。ここへの適用要否)、または過剰な制約(例: 救済候補を一律AUTO不可にすること、lexical `have`の扱いを段階2eに回したこと)。

## 参考(実データ)

- 棚卸し: `EXCLUSION_PATTERNS_01.md`・`inventory_01.json`。HR導入後のGate除外11件=S1(機械的救済可)4/S2(新規則要)3/困難4、HR導入前の一意句29=12/2/11(+現行で既に通る4)。
- 机上再検査: `recheck_01.json`(既存validatorを変更せず呼出)。
- 先例: `er105_kp_fulltext_selector_01.py:927 postprocess_possessor_roles`(UDR #173②承認済み・revertのみ後処理)。
- 照合: `SPEC_CHECK_01.md`(特に§2: 活用形→基本形例外はer119経路に適用済みで、`studied separately`は`er105:662 _guard_ok`の次トークン条件で拒否。次トークン条件はCURRENT_SPEC.md:1997未記載)。

## 期待する出力

論点ごとに「問題なし/要修正(修正案)/ユーザー判断要」を付した所見。11-3の条件Aに該当しないと判断する場合はその理由。
