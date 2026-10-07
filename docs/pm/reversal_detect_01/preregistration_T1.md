# 事前登録 T1(OPEN-233-REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01 委任_01)

登録時刻: 2026-10-08 00:40(検出器・runnerコードを書いた後、dev/held-outデータへ一度も適用していない時点)
位置づけ: Trial/検証(DEV)。Production変更なし、APPROVED_FOR_PRODUCTIONなし。API不使用(¥0)、上限¥5。

## 0. 凍結物
- 検出器 `er052_output/open233_reversal_detect_01/tools/reversal_detector_v0.py` sha256=ccd0d4a0bdadf730a71bb7b101e88b80ca147d6d806b987f14c2133f19bfd886
- runner `tools/run_T1.py` sha256=3ee91134c4940fa862d8d557506377502bd16173d6ad6122d649f7531a17fd71
- 流用(読み取りのみ): `er052_output/open233_stage0_01/danger/danger_sentence_rules_v0.py`(文分割・台帳parse・fact link・NEG語)、`run_match.py`(記事読込・既知NG→文の対応 `match_dump.json`)

## 1. 検出器の定義(v0)
対象言語=台帳の言語(JA台帳=meta/hormuz/space_weapons/sewer→JA R2文、EN台帳=ai_control→EN最終文)。EN文×JA台帳の対応は概念辞書が要るため本版は扱わない(限界)。
- (i) neg_absence: 否定語(Stage0のNEG_JA/NEG_EN。「not only」型の対比は除外)があり、かつ台帳の「肯定の出来事fact」(出来事語辞書POS_EVENTに一致するfact)と語が重なる(JA: 否定表現を除いた文のbigram共有5以上、EN: 内容語共有2以上)。
- (ii) subj_class: 文の主語名詞(規則抽出)の役割クラス(human/ai/org/public、辞書の主辞)が、文が結び付くfact(Stage0 link_facts、**一意リンクのみ**。曖昧は候補化しない)の主語クラスと異なる。
- (iii) neg_subject: (i)かつ(ii)(475j-n1型)。
- 除外: 語り枠(I/you/we・問いかけ・JA私/あなた/疑問)の文。**既知NG文が語り枠で除外された場合も「取りこぼし」として数える**(再現率に含める)。
- 「候補」=印。印の付いた文は将来Rewriteせず人間レビューパックへ直送する設計(routing_design_v0.md)。LLM重さ判定は使わない。

## 2. データ
- 負荷の走査集合(dev)=Stage0の100記事(B3 55+CCP 18+RCA 27)のうちheld-out項目を含む27記事を除く**73記事**(項目なし22記事を含む)。held-out走査集合=27記事。(委任文の「33記事」は、Stage2 replay対象のログ33本[ccp18+e2e5+P2版10]を指すがそのうち10本はheld-out側のため使わず、Stage0の記事コーパスで統一した。記事数が違うため合格ラインは比率換算する)
- 再現率の分母=dev既知NG(`known_relation_ng.jsonl`の`record=in_set`、split=dev、severity_final≠pending)のうち sentence_type が「否定・不在」「主語新規出現・置換」の項目。pending(未判定)は分母に入れない。文の特定は `match_dump.json` の対応(score≥0.5、検出言語側の文)。**特定できない項目(JA台帳トピックでEN側のみの項目など)は「特定不能」として別掲し、厳密再現率(分母=全NG項目、特定不能を取りこぼし扱い)も併記**。
- 過去重大(PAST-*)は記事本文が無いため対象外。

## 3. 指標と合格ライン(件数、M3)
- 主指標(再現率): 否定・不在型 と 主体型 の**文レベル再現率がそれぞれ60%以上**(特定できた項目が分母。分母が小さい[n<10想定]ため参考性は低いと事前に明記)。否定・不在型の「検出」=(i)または(iii)の印、主体型の「検出」=(ii)または(iii)の印。
- 負荷(記事): 印が付く記事の件数が走査記事のうち **6.06%相当(委任文の33記事中2件を比率換算)以下、すなわちdev 73記事中4件以下**(held-out 27記事中1件以下)。
- 併記(合否には使わない): 印の付く文/全文、位置別(title/summary/intro/body/closing)、記事あたり印数の分布、型別(tag別)、NGでない文(既知NG・pendingを除く)への誤検出率と実例10件(seed固定乱数)とその型、oracleリンク版(既知fact_id使用)の再現率。
- 総合PASS = 再現率2型とも60%以上 かつ 負荷ライン内。どちらか未達=FAIL(CONDITIONAL無し)。機械適用、読み替えない(M1の精神)。
- 副指標メモ: Opusの事前案「印の付く記事7%以下」とは別に、本委任文の「33記事中2件」を比率換算して使う(73記事で4件=5.5%、27記事で1件=3.7%)。

## 4. 手順・規律
1. devで1回適用。結果が悪い場合のdev調整は**最大2版(v0→v1→v2)**、各版の定義差分・結果を全て記録(版ごとに本ファイルへ追記、sha256付き)。調整はdevの既知NG・devの負荷のみを根拠とし、held-out項目は見ない。
2. 最終版を凍結し、held-outへ**1回のみ**適用(結果を見て調整しない)。runnerは既存のheldout出力があると拒否する。
3. 費用: API呼び出し無し(¥0)。台帳のクラス付与は辞書で行う(LLM不要)。
4. 起動前プロセス確認(M6): `Get-Process python*`で他のpython 2本が稼働中のため、自処理は1プロセス・直列で実行。
5. runner/checkerコードは編集しない。BLOCKING未修正のまま出口へ出す経路は作らない(M4、routing_design_v0.md)。

## 5. 追記(2026-10-08 00:55、devのみ参照・held-out未開示)
### 5-1. v0のdev結果と位置補正(runner側のみ)
- 初回(`dev_v0`): 否定・不在 located 3/7、hit 0。原因の一つは**ai_control項目のEN文が`match_dump`で未特定(score 0)**だったこと。runnerに手動位置補正`EN_OVERRIDE`(jb9k-n3/n4/n5=EN文index 23/24/14、cupe-n1=25、目視。Stage0 OVERRIDEの流儀)を追加(runner sha256=0f396cdd…、検出器v0は不変 ccd0d4a0…)して`dev_v0b`を取得。
- `dev_v0b`: 否定・不在 hit 1/6(located)、主体 hit 0/3(located)。印の付く記事 71/73、印の付く文 176/2053(8.6%)。
### 5-2. v1(調整1回目、dev既知NGのヒット要因とdev負荷のみを根拠)
- 変更: (a)EN主語の前置句(In.../As.../What is more,等)をカンマまでスキップ (b)JA主語の末尾格助詞(に/で/と/から等)除去 (c)否定+重なりの閾値をJA bigram 5→8、EN語 2→3 (d)「〜なしに/without」だけの限定句は否定(不在)扱いしない。
- `reversal_detector_v1.py` sha256=755dccbcc4226b88ead74ba19d1843d90d93eb58e158b10e29d856c13ff2d1c5、runner(`DET_MODULE`環境変数で検出器切替を追加)sha256=02c136351e198de7d50c8d54f9a59c4926cae735968bdcede182117b93e87fc6。
- `dev_v1`: 否定・不在 hit 1/6(同じjb9k-n3)、主体 hit 0/3。印の付く記事 62/73、印の付く文 119/2053(5.8%)。
- v2は作らない(ラインの桁が違う: 印の付く記事 ≤4/73 に対し62/73。再現率も2型とも60%未満。構造要因[既知NGの否定型の多くは台帳が「未提示」と述べる事項を「ない」と書いた型で反転型ではない/主体のfact結び付けが一意にならない]は閾値調整では解けない)。
### 5-3. 凍結規則とheld-out実行
- 凍結: 「dev再現率が高い方、同率ならdev負荷が低い方」→再現率は同率(neg 1/6・主体 0/3)で、負荷が低いv1(62/73、119文)を最終版として凍結。
- held-out(27記事)を**v1(sha256 755dccbc…)で1回のみ**実行する。合否は本ファイル3節のラインを機械適用(PASS/FAIL、読み替えない)。
