# T3_RESULT(OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01 委任_01、2026-10-08)

位置づけ: Trial/検証(DEV)。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、runner/checker/SSOT未編集、git未実施。事前登録=`docs/pm/link_precision_01/preregistration_T3.md`(追記6・7節に実行中の記録)。**実費 ¥25.00**(dev 22 run + 反復6 + B3 3記事 = ¥18.51、held-out 10 run = ¥6.48。上限¥40/STOP¥35未到達。Stage1 r3のみ、1call約¥0.5〜0.7)。

## 1. 結論(機械適用、dev): **FAIL**((a)と(d)が未達)
| ライン(事前登録3節) | 結果 | 判定 |
|---|---|---|
| (a) 既知NG文のsupport_fact_ids(strict)がoracle fact_idを含む率 >= 15/21 | **9/21(42.9%)** | FAIL |
| (d) 3記事x3回で3回とも同一集合の率 >= 80% | **74/93(79.6%)**(80%線=74.4件、1件不足) | FAIL |
| 費用 <= ¥40 | ¥25.00 | PASS |
読み替えない。(b)(c)は合否外の記述指標。
- 補足(事前登録した補助指標、合否に使わない): post-hoc正規化版(r3の略記ID`E009`等を台帳IDへ読み替え) (a)=10/21、(d)=74/93(変化なし)。(a2)=support_fact_ids∪Stage1候補の`related_fact_ids`=**19/21**。

## 2. 指標の詳細(dev、`dev_summary.json`)
- **(a)型別(strict/正規化/a2)**: 限定語消失 2/2/2(n=2)、否定・不在 0/1/3(n=3)、多義語方向 4/4/6(n=6)、因果・時間接続 2/2/4(n=4)、主語新規出現 1/1/2(n=2)、全称 0/0/0(n=1)、その他 0/0/2(n=3)。MUSE-HC-012(meta方向型)が21件中8件を占める偏り。
- **(a)をr3判定別に分けた事実**: 既知NG21件のうちr3がSUPPORTEDにしたのは10件で、そのsupport_fact_idsはoracleと一致(strict 9、略記ID`E009`の1件を正規化すると10/10)。r3がCANDIDATEにした11件は`support_fact_ids`が空(11/11)で、oracleとの照合はa2(`related_fact_id`)でのみ可能: 9/11一致、2件不一致(sewer-qrfc-n1全称: F-012に対しF-007/F-010、hormuz-j7gv-n1: HF-003に対しHF-002)。
- **(b) 妥当性**(非空のunit 326): 完全一致でselected_fact_idsの部分集合=**248/326(76.1%)**。台帳IDが完全一致で存在=308/326(94.5%、ID文字列19/372が台帳に無い表記で、`E009`x14、`E011`x3、`E008`x2=すべてai_control記事)。正規化後は台帳ID実在326/326、selected部分集合264/326(81.0%)、selected外の台帳factを参照するunit=62(内訳の原因は未調査)。
- **(c) リンクなし**: judged 645 unitのうち空=**319(49.5%)**。**空はr3 CANDIDATE 319/319、SUPPORTEDで空は0/326**(devの22 run。B3追加では、model_verdict=CANDIDATEでsupportが非空のunitが1件=hormuz-cf8v-n2)。既知NG located 29件のうち空=16: 否定・不在 3/4、その他 5/5、全称 1/1、因果・時間接続 3/6、主語新規出現・置換 1/2、多義語方向 2/6、数値 0/2、限定語消失 1/3。「新しい世界主張(対応factなし)」型6件のうち空は5件、「台帳factの組のズレ」型23件のうち空は11件。
- **(d) 反復**: ai_control 29/35、hormuz 20/29、meta 25/29(strict、正規化後も同じ)。model_verdictが3回同じunit=77/93。3回ともSUPPORTEDだったunit 35件のうち集合が同一だったもの(正規化後)32件。

## 3. held-out(1回、10 run、既知NG located 16、fact_id既知14、`heldout_summary.json`)。方向のみ確認
| 指標 | dev | held-out | 方向 |
|---|---|---|---|
| (a) strict | 9/21 (42.9%) | 6/14 (42.9%) | 一致 |
| (a2) support∪related | 19/21 | 14/14 | 一致(a2は高い) |
| (b) selected部分集合(完全一致) | 76.1% | 76.3% | 一致 |
| (b) 台帳ID完全一致で実在 | 94.5% | 100%(非ledger表記0/171) | held-outではID略記が出ていない |
| (c) 空の割合 | 49.5% | 47.9%(140/292、CANDIDATE 140/140、SUPPORTED空0/152) | 一致 |
| (c) 既知NG located のうち空 | 16/29 | 9/16 | 一致 |
(dの反復はheld-outでは行っていない。)

## 4. 作業3: 「未提示→不在断定」規則R(¥0、`step3_dev.json`・`step3_heldout.json`、`analyze.py`/`step3.py`)
規則R=(リンクなし ∧ 否定語 ∧ 台帳に未提示マーカーを持つfactと実体語を共有)。R1=(iii)を「台帳に未提示マーカーのfactが1件以上」に緩めた版、R2=本来の(iii)。
- **事実1(構造)**: devでは「リンクなし」=r3 CANDIDATEとほぼ同値(319/319)なので、規則Rは既にStage1が候補にしている文の中から選別するもので、新規の検出ではない。
- **再現率**(T1が見逃した否定型、dev 5件): **R1=2/5**(jb9k-n4、space_weapons-637f-n2)、**R2=0/5**。参考としてjb9k-n3(T1で当たり)はR1・R2とも印あり。見逃し: jb9k-n5(r3 SUPPORTED、support=E009)、hormuz-cdwb-n1(SUPPORTED、HF-003)、hormuz-cf8v-n2(CANDIDATEだがsupport=HF-003で非空)。B3 3記事はStage1ログが無いためこの目的のためだけに同条件で追加replay。
- **負荷**(dev 25記事、judged 730 unit): R1=印の付く文**91件(12.5%)**、印の付く記事21/25、記事あたり平均3.6(中央4、最大9)。R2=**15件(2.1%)**、記事10/25(40%)、平均0.6(中央0、最大3)。T1の検出器v1(5.8%、記事85%)と比べ、R1は文率が約2倍・記事率は同程度、R2は文率が約1/3・記事率が半分以下。
- **R2の限界(構造)**: 非ai_control記事は台帳がJA(例: hormuz/meta/sewer/space)で、EN文とのラテン文字語・数値の共有でしか照合できず、R2が印を付けたunitはai_controlと一部の固有名詞・数値を含む文に偏る(jb9k-n3が当たったのはai_controlのEN台帳のため)。
- **held-out**(475j-n1: R1印あり・R2印なし、89wf-n2(否定・不在型): R1印あり・R2印なし)=R1 2/2、R2 0/2。負荷: R1 32/292 unit(11.0%)、記事9/10。R2 6/292(2.1%)、記事5/10。

## 5. リンク供給源としての可否(事実のみ、判断はFable/ユーザー)
- 現行の`support_fact_ids`は**r3がSUPPORTEDにしたunitにしか入らない**(devで非空326/326がSUPPORTED、空319/319がCANDIDATE)。つまり、NGの疑いがあるとr3が見たunit(検出対象になる側)にはこのフィールドで文→factリンクは得られない。CANDIDATE側のリンクは別フィールド`related_fact_id`にあり、既知NGとの一致は dev 9/11、held-out もa2で14/14(分母は同じ14件内)。ただし事前登録した合否指標ではない。
- support_fact_idsが入るSUPPORTED側のNGでは、oracleと一致(dev 10/10(正規化後)、held-out 6/6)。これは「リンクは正しいがr3の判定がNGを見逃した」文であり、リンクの精度とr3の判定漏れは別の問題。
- ID表記: devで`E009`等の略記が19/372ID(5.1%)出た(ai_control記事のみ。held-outは0/171)。r3 verify_supportedは台帳ID完全一致でblocksを引くため、略記は決定論検査から外れる可能性がある(未確認、本委任では検証していない)。
- 反復一致は79.6%(1件不足)。r3の判定(SUPPORTED/CANDIDATE)自体が3回で同じなのは77/93(82.8%)で、判定の揺れがリンクの揺れ(空↔非空)の主因。

## 6. 次の設計への含意(事実のみ、実装・採用ではない)
- Writer自己注釈案④や決定論検出器のリンク供給源として使うなら、(i)r3プロンプトに「CANDIDATEでもsupport_fact_idsまたは最も近いfactを必ず返す」変更が要る(未実施、本委任はr3 prompt不変)か、(ii)Stage1候補のrelated_fact_idを供給源にする設計になる。後者はdevで9/11(CANDIDATE側既知NG)・全体で19/21の一致が既に取れている。
- 否定型の「未提示→不在断定」をリンクなし文の規則で拾う案は、R2では0/5、R1(緩い版)は2/5だが12%の文に印が付く。いずれも既にr3 CANDIDATEの文の中で選ぶ処理であり、見逃し3件はr3がリンクを付けた文(SUPPORTED/非空)だった。
- 限界: oracleの文対応はClaude(人手相当)の目視で人間確認なし。MUSE-HC-012が21件中8件。dev/held-outとも分母が小さい(21/14)。B3追加3記事は(a)の分母に含めていない。(d)は3記事のみ。

## 7. 証跡
- `er052_output/open233_link_precision_01/`: `r3/{dev,devreps,b3x,heldout}/*.json`(r3出力: 全unit・support_fact_ids・model_verdict・候補・call費用)、`dev_summary.json`、`heldout_summary.json`、`step3_dev.json`、`step3_heldout.json`、`cost_*.json`、`logs/`、`oracle_dev.py`・`oracle_heldout.py`(oracle対応付け)、`replay_r3.py`・`analyze.py`・`step3.py`(再現コマンド: `.venv/Scripts/python.exe er052_output/open233_link_precision_01/analyze.py --oracle oracle_dev --tags dev --reps devreps --b3x b3x --out dev_summary`、heldoutは`--oracle oracle_heldout --tags heldout --out heldout_summary`)、`worksheet_{dev,heldout}.txt`。
- 事前登録: `docs/pm/link_precision_01/preregistration_T3.md`。委任文: `docs/pm/delegation_log/2026-10-08_OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01_01.md`(+`_check.json`はFABLE委任文の転記のためテンプレ必須項目欠落でFAILと記録された)。
- 作業中の注意: 集計スクリプト`analyze.py`をimportして一度`dev_summary.json`を上書きしたが、同コマンドの再実行で復元済み(値は同一、決定論)。
