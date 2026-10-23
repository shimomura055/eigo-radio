# OPUS_REVIEW_REQUEST_01: Key Phrase 一般化・文脈意味・意味説明の包括対策(条件A: 新しい処理構造の設計)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 依頼元: 委任_01(2026-10-23) / 正本: PM_GOVERNANCE 11-3(条件A)
添付: `ROOT_CAUSE_01.md`、`DESIGN_01.md`、`census_items_01.json`・`census_labels_01.json`、`kp_probe_01_result.json`・`kp_probe_02_result.json`、`kp_census_01.py`・`kp_probe_01.py`・`kp_probe_02.py`
ユーザー原文: `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md`

## 依頼の背景(3行)
記事Bの KP `draw that line` が、Std「その線を引く」/Adv『to decide where the limit is between what is acceptable and what is not』となり、ユーザー期待(`draw a line`/「境界線を設ける」/『to establish a clear boundary or limit』)と乖離した。原因は、canonicalizationの許可変換が閉集合で `that→a` を作れず(validatorも却下)、gloss Promptが全語訳出を要求して「その」を訳し、Adv説明が辞書的な下位語義に寄る、という構造。推奨案Aは新規LLM callなしで既存3段の規則を精密化する。

## レビュー論点(依頼事項)
各論点について、**重要度(BLOCKER/MAJOR/MINOR)・QCD影響・採否推奨**を付けて回答してください。

1. **一般化の過不足**
   - 規則5(this/that→a/an、him/her→someone)の対象範囲は適切か。複数形の指示語(these/those)・them/it・主語代名詞は対象外としたが妥当か。
   - 固定表現(that said, at that point, in that case, this time, like that, all that)の過剰一般化を、Promptの例外記述+ネガティブコントロールだけで抑えられるか。validator側で守る決定論ガードが必要か(辞書なしで可能な最小ガード案があるか)。
   - `a/an` の一致(an apple)をvalidatorで見ない判断は許容か。
   - `its`の残り(`turn on its head`)、大文字残り(`Carry the Load`)を本件の範囲外とした判断は妥当か(大文字は現templateが変更を禁止)。
2. **文脈に合った意味の保持**
   - 一般化(置換)後のkey_phraseで、gloss/説明が『本文での語義』を失うリスク。例: `sentence him to death→sentence someone to death` で人物情報が落ちる影響、`draw that line→draw a line` で『本文の語義』と『辞書の別語義』がずれる場合。
   - gloss callは記事全文を受け取るが、Adv説明callは1文のみ。説明callに前後1文または記事要約を渡すarmを設けるべきか(probe-01では文脈不足は主因ではなかった)。
3. **慣用表現の誤解釈リスク**
   - 『慣用句はフレーズ全体の中心義で』という方針が、字義どおりの用法(`pump one's fist`、`pull someone under`=物理動作)を過剰に比喩化しないか。字義/比喩の判定を誰(LLM)に任せ、どう検査するか。
   - 追記案の例示語(break the ice等)が過適合・誘導を起こさないか。
4. **Standard/Advanced間の意味整合**
   - Prompt原則の共有+Adv gloss参照(データ共有なし)で十分か。共有KPは21%と少ないが、不整合率は2/7(n小)。『a2 glossをb1b currentとして渡す』既存機構の追加利用を最初から入れるべきか。
   - Std=日本語意味/Adv=英語説明という既存仕様を維持したままの整合方法として、より単純な代案はあるか。
5. **既存仕様・過去Trialとの整合**
   - Prompt 2逐語固定(OPEN-454)、『一般化は後段』、ER-011-NO18(人称一般化)、Trial-02(一般化専用LLM工程REJECTED)、KPQ ①②(OPEN-458)、JRE委任_02の目的格追記(commit 1d501f74d)との矛盾・取りこぼしはないか。
   - 『Adv説明Promptの追記』はユーザー承認済みTrial-02 B候補仕様の変更に当たる。Trial→VALIDATED→ユーザー採用の経路で扱う方針に誤りはないか。validator表の拡張(コード)は11-7の限定例外の対象外(既存の閾値・辞書・規則の直接編集に当たる)と判断しており、Trial限定(DEV経路)としたが妥当か。
6. **過剰なPrompt制約の副作用**
   - 追記により、(i)外側retry増(validator却下)、(ii)正常KPの不要変更、(iii)出力長・語数上限(15語)への影響、(iv)reasoning長増による費用増、のいずれが懸念か。Prompt追記量の上限目安(入力+300token前後)は妥当か。
   - 規則の優先順位(自問文・規則1・規則5・Meaning Preservation Rule)に矛盾や曖昧さが生じないか。
7. **より単純・低コストな方法**
   - 案A以外に、品質を維持しつつより単純な方法があるか(例: validatorの許可表だけ拡張し、gloss/説明は一般化形入力の効果に任せる『最小案A0』。probe-01では gloss の『その』混入は一般化のみで5/5解消、Adv説明の『acceptable』は3/5残存)。段階導入(A0→A-2→A-3)の順序は妥当か。
   - 案B(canon+gloss統合)を将来の本命とすべきか、今は不要か。
8. **検証計画**
   - 成功基準(§5-3の数値)、検証セット(難例20/正常30/ネガティブ10)、Judge構成(2系統+Opus抜取り)、反復(各3回)は必要十分か。過剰・不足の指摘。
   - 小標本probeの限界(各3〜5回、1記事中心)をどう補うか。

## 既知の限界・開示
- census分類は目視1名(Sonnet)の主観を含む。境界例を区別して提示している。
- probeは gpt-6-luna、各3〜5回、DEV用スクリプトで本番builderをimportして実施(Production無変更、実費約1.4円)。
- 並行中のASR-QUALITY(UKUS/PN)Trial実装とのused_form変更による相互影響は統合時に確認する(今回は両module未編集)。

## 回答形式(希望)
- 判定:GO / 条件付きGO / 要再設計
- 指摘一覧(ID付き、重要度・QCD影響・推奨対応)
- 設計への反映が必須の項目(BLOCKER/MAJOR)と、任意の項目の区別
