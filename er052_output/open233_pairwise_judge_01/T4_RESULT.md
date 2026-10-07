# T4_RESULT(OPEN-233-PAIRWISE-JUDGE-MODEL-TRIAL-01 委任_01、2026-10-08)

Trial/DEV。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、Writer/Checker/runner/SSOT未編集、git未実施。事前登録=`docs/pm/pairwise_judge_01/preregistration_T4.md`(6節=held-out前の追記)。**実費 ¥26.40**(上限¥30、STOP¥27未到達)。モデル: A=`gpt-6-luna`(現行判定モデル、$0.10/0.50)、B=`gpt-6-sol`($2.00/10.00、1call約¥0.33)。reasoning effort=medium(両条件)。

## 1. 結論(機械適用、dev、主判定=rep1): A・Bとも **FAIL**
| 指標(合格線) | A: luna x狭い対判定 | B: sol x狭い対判定 | 参考: 現行r3保存判定 |
|---|---|---|---|
| 既知NG検出 (>=15/21) | **8/21** FAIL | **8/21** FAIL | 11/21(SUPPORTED以外を検出扱い) |
| 対照誤検出 (<=4/21) | 0/21 PASS | 1/21 PASS | 0/21(構成上自明: 対照をr3 SUPPORTEDから選んだため) |
| 3/3一致 (>=80%) | 32/42=**76.2%** FAIL(検出フラグでは33/42) | 8/8(サブセット8項目のみ)PASS | 未測定 |
| 費用 (<=¥30) | PASS(総額¥26.40) | | |
- A反復の参考値: 3回多数決の検出8/21(変化なし)、いずれか1回でも検出12/21、対照の多数決誤検出2/21。
- 重大2件: jb9k-n3(dev)は**A=contradicts(rep1,2)/asserts_unstated(rep3)、B=contradicts**=両方検出(r3現行は当該文CANDIDATE=現行も検出)。89wf-n1(held-out、major)は**A・Bとも asserts_unstated(検出)**(Aはrep1のみ、Bは本件2件のみ実行)。
- 読み替えない。仮説H(狭い対判定+モデル変更で検出率上昇・誤検出低維持)は、dev検出率ではA/Bとも8/21で現行r3(11/21)を上回らず、合格線15/21に届かなかった。

## 2. 型別検出(dev、n=21、rep1) A / B
限定語消失 0/2・0/2、否定・不在 1/3・2/3、主語新規出現・置換 0/2・0/2、全称 1/1・1/1、因果・時間接続 3/4・2/4、多義語方向(meta MUSE-HC-012方向型) 0/6・1/6、その他 3/3・2/3。
- 見逃しの大半は meta「元に戻した/一時的に戻した」型(MUSE-HC-012、6件)と ai_control の jb9k-n1/n2/n5・cupe-n1・meta-2xhw-n1等。これらの文は1文x1 factで見ると言い換えとして整合と判定された(例: jb9k-n5「標準の保護が無かった」→両モデルとも「faithfulな言い換え」)。
- A∪B(rep1)=10/21、A∪B∪r3=12/21、A反復any∪B∪r3=13/21。どの条件でも検出されなかった8件: ai_control-cupe-n1, jb9k-n1, jb9k-n2, jb9k-n5, meta-2xhw-n1, meta-daju-n2, meta-gj99-n1, meta-n6vy-n1。r3だけが検出しA/Bが見逃した: meta-cz6g-n1, meta-ggp4-n1。
- 「未提示→不在断定」型: asserts_unstated は出る。jb9k-n4(「人間はAIの制御を失っていない、現時点で」)はBが3回とも、Aはrep2/3で asserts_unstated(rep1はconsistent)。89wf-n2(「宇宙戦争ではない」)は両モデルとも asserts_unstated。jb9k-n3は両モデルが、台帳が述べる事実(モデルが外部ネットに到達)との矛盾として contradicts。jb9k-n5は両モデルconsistent。asserts_unstated総数(dev rep1): A=ng 7件(ng検出8件中)、B=ng 4件+対照1件。

## 3. 誤検出実例(5件)
- dev B 1件: ctrl-sewer-qrfc-n1(対照、文に「Fukushima Prefecture」を含む)→ asserts_unstated「台帳は北方市が福島県にあると述べていない」(世界知識由来の事実を台帳外とみなした)。
- held-out A 4件(14対照中): ctrl-ai_control-s9dk-n1(「公開サイトも課題の一部と考えた」→台帳は package registry と表記)、ctrl-meta-jdmu-n1(Muse説明文→台帳は「personal AI agent」のみ)、ctrl-meta-jdmu-n2(「one report and some tests」)、ctrl-space_weapons-89wf-n1(「much wider range」比較表現)。いずれもr3がSUPPORTEDとした対照で、1fact単独に絞ると他factが支える部分を「台帳未記載」と扱う傾向(1文を1 factだけに照らすため、複数fact由来の文が asserts_unstated になる)。

## 4. held-out(1回、方向のみ。T3 oracle_heldout既知NG fact_id既知14+対照14)
- A(luna、rep1、28件全件): 検出 **7/14**(dev 8/21=38%に対し50%、方向同じ側)、対照誤検出 **4/14**(dev 0/21から増。方向は不一致=誤検出が増えた)。現行r3(held-out既知NG): 検出9/14(参考)。
- B(sol): 費用上限のため89wf-n1・n2の2件のみ実行(事前登録6節)。両件とも asserts_unstated(検出)。検出率・誤検出率は未算出(未実施)。

## 5. 限界・交絡(事実)
- N小(dev 21+21、held-out 14+14)。oracle(文↔fact対応、NG判定)はClaudeの目視で人間確認なし。meta方向型8件(MUSE-HC-012)が検出率を押し下げる偏り。対照は「r3がSUPPORTEDにした文」で、真にNGでない保証は無い。対照の型揃えは正規表現(neg/univ/causal/num/plain、plainが大半)で粗く、対照21件のうち型一致18、同記事内21。
- A対Bの差=モデル差(検出は同じ8/21、誤検出はdevでB 1件)。A対現行r3の差=判定形式差(文脈つき広い判定→1文1fact狭判定)であり、同モデルでは形式差単独の検出向上は見えず(8対11)。ただしr3の「検出」はCANDIDATE化であり、文ごとの根拠付き対判定とは粒度が異なる。
- Bは反復非対称(1回+サブセット8項目x3)でBの3/3一致は小標本。held-out BはN=2のみ。Stage2保存判定は対文unit単位でないため参考比較に含めていない。
- 自己判定promptは1種類(DEV_MSG固定、dev中は変更なし)。promptや提示情報(例: 周辺文・記事内の他fact)の変更効果は未測定。

## 6. 証跡
`er052_output/open233_pairwise_judge_01/`: `items_{dev,heldout}.json`、`out/{dev,heldout}/{A,B}_rep*.json`(全verdict・根拠・usage・費用)、`out/cost_log.jsonl`、`summary_{dev,heldout}.json`、`item_table.txt`(全項目の文・r3判定・A/B判定・根拠)、`build_items.py`・`judge.py`・`analyze.py`(再現: `judge.py --cond A|B --set dev --reps 3`、`analyze.py dev`)、`stability_subset_B.json`、`heldout_B_ids.json`、`logs/`。事前登録: `docs/pm/pairwise_judge_01/preregistration_T4.md`。委任文: `docs/pm/delegation_log/2026-10-08_OPEN-233-PAIRWISE-JUDGE-MODEL-TRIAL-01_01.md`(+`_check.json`)。
