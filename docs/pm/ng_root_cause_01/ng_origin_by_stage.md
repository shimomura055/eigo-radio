# NG発生工程・機序の分解(OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_B2、2026-10-07、¥0・read-only)

位置づけ: 既存の評価成果物の再集計のみ。API・記事生成・Production変更・SSOT編集なし。重大/軽微の判定は既存の単独評価(人間確認なし)に従い、再判定していない。**機序ラベルは本書で付与した分類である。B3側は評価JSONの`kind`をそのまま使い、前回側は`kind`が無いため該当文から本書が分類した。境界例がある。**

## 0. 出典・定義
- 前回=E2E_02 従来版(control)5本+P2版10本。出典は`er052_output/open233_allfact_note_e2e_02/eval/stagewise/{STAGEWISE_SUMMARY.md,stagewise_*.json,NG_*.md,notes_to_error_trace.md}`(REPORT §95)。84件(重大6/軽微78)のng_itemsを全件使用した。
- 今回=B3 Trial V0/V1/V3/V5/V6の記事55本(Gate STOP 5本を除く)。出典は`er052_output/open233_b3_trial_01/eval/articles/*.json`(44件、全て軽微、重大0)と`_private/MAP_stage2.json`(条件対応、開封済み)。
- 工程の対応(重要):
  - 前回の工程列は、**JA**=JA最終稿(R2、`revision2.md`)で存在、**EN新規**=JAに対応文が無くEN化で発生、**Rewrite新規**=EN Rewrite(Checker起動)が生んだ。前回は**R0(Writer初稿)単独の評価をしていない**(`original.md`は`runs/**/ja_writer/`に保存あり)。そのため前回のR0対R2の分離は、`notes_to_error_trace.md`のmeta/hormuz P2 28件と、本書のgrep確認(重大4件)のみ。
  - 今回の工程列は評価JSONの`stage.s0/s1/s2`=R0/R2(JA)/EN。**R0**=初稿から存在、**R2**=R0に無くR2で発生、**EN**=JAに無くENのみ。今回は`--no-checker`のため**Checker/Rewriteループが存在しない**(R2はWriter内部の改稿)。
- 機序: added=台帳外の追加(比喩・装飾・評価語・具体化を含む)/causal=因果の断定/subject=主体・対象の取り違え・特定/scope=範囲・限定語の脱落・連結・拡張(単数化・「約」脱落を含む)/time=時間・数量/undisclosed=未提示事項の断定(「確認されていない」「実証されなかった」型)/other=その他。B3の`kind`は scope・added_fact・causal・subject・time のみ。

## 1. 表A 前回(件数)
工程×機序。JAはR0とR2の区別なし(R2最終稿時点で存在)。

### 1-1. 従来版(control、5本、重大0)軽微
| 機序 | JA | EN新規 | Rewrite新規 | 計 |
|---|---|---|---|---|
| added | 7 | 0 | 0 | 7 |
| causal | 4 | 1 | 0 | 5 |
| scope | 4 | 0 | 0 | 4 |
| subject | 1 | 1 | 0 | 2 |
| undisclosed | 2 | 1 | 0 | 3 |
| 計 | 18 | 3 | 0 | 21 |

### 1-2. P2版(10本)重大/軽微
| 機序 | JA | EN新規 | Rewrite新規 | 計 |
|---|---|---|---|---|
| added | 1/23 | 0/2 | 0/0 | 1/25 |
| causal | 0/7 | 0/3 | 0/0 | 0/10 |
| scope | 1/10 | 0/1 | 0/0 | 1/11 |
| subject | 2/5 | 1/0 | 0/0 | 3/5 |
| time | 0/2 | 0/0 | 0/0 | 0/2 |
| undisclosed | 0/2 | 0/0 | 0/0 | 0/2 |
| other(Rewrite無関係置換/EN欠落/用語不統一) | 0/0 | 0/1 | 1/1 | 1/2 |
| 計 | 4/49 | 1/7 | 1/1 | 6/57 |
- STAGEWISE主表と一致(①JA 4/49・従来0/18。①→②のEN新規は従来0/3・P2 1/7。Rewrite新規はP2 1/1)。
- **JAに最終まで残った重大4件**(meta-p2r2-02、ai-p2r1-01、sw-p2r2-01、sw-p2r2-02)の問題文は、`original.md`/`revision1.md`にその文言が無く`revision2.md`で初めて出現した(本書grep。ai/swは確認語が全て0件。metaは「主役になった人間が知らされていなかった」の1文のみR2で追加、同記事の「相手に十分知らせないまま」はR0から存在)。**JA R2改稿工程での発生と読めるが、文言一致の確認であり、言い換えでR0に存在した可能性は否定できない(限界)**。
- 重大6件のRewrite関与: ENでRewriteにより修正4、Rewrite自体が生んだものがloop内で修正1(ai-p2r2-07)、Rewrite後も残存1(meta-p2r2-02)。JA側は修正されず残存3(OPEN-239)。

### 1-3. 前回meta/hormuz P2 28件のR0/R2/EN(`notes_to_error_trace.md` §1、意味上のR0存在を含む)
- R0に意味上存在14/R1・R2で出現12/JAに対応なし(EN新規)2。重大1(meta-p2r2-02)は「R0に目的語欠落が存在、R2で『主役になった人間』が追加」。
- 同ファイル§4: Note転記が具体化・断定に変換された直接証拠(A)0件、Noteと無関係(B)23、判定不能(C)5。

## 2. 表B 今回 B3 Trial(軽微のみ、重大0)
### 2-1. 工程×機序(全44件。R0〜ENのどこかで存在した軽微。うち36件がEN最終に残存、8件はR0のみで消滅)
| 機序 | R0から | R2で発生 | ENで発生 | 計 |
|---|---|---|---|---|
| added_fact | 9 | 5 | 3 | 17 |
| scope | 12 | 2 | 4 | 18 |
| causal | 3 | 1 | 0 | 4 |
| subject | 1 | 1 | 2 | 4 |
| time | 1 | 0 | 0 | 1 |
| 計 | 26 | 9 | 9 | 44 |
- 条件別の工程内訳(R0/R2/EN): V0 6/1/2、V1 11/1/1、V3 3/1/4、V5 3/1/1、V6 3/5/1。条件別の機序: V0 added4/scope2/subject2/time1、V1 added6/scope5/causal1/subject1、V3 scope5/added2/subject1、V5 scope3/added1/causal1、V6 added4/scope3/causal2。
- EN最終36件(SUMMARY_STAGE2の軽微合計と一致)の工程内訳はR0 18/R2 9/EN 9、機序はscope16/added13/subject4/causal2/time1。
- R0→R2の退行(`regression`)付きは9件(うちV6 5件)。
- 評価JSONにundisclosed/otherのkindが無い(該当がscope/added_factに含まれる可能性があるが未確認)。

## 3. 並べた事実
### (a) 工程別の比率
- 前回(軽微78): JA 67(86%)/EN新規10(13%)/Rewrite新規1(1%)。今回(軽微44): R0 26(59%)/R2 9(20%)/EN 9(20%)。
- R0/R2を分けられる範囲(前回meta/hormuz P2 28件、今回meta+hormuz 26件): 前回はR0 50%・R1/R2 43%・EN 7%、今回はR0 58%・R2 19%・EN 23%。**前回はR2由来の比率が高く、ENのみ発生の比率が低い**。ただし前回のR0判定は「意味上存在」を含む基準、今回は評価者のstageフラグで、基準が同一ではない。
- 前回のENのみ発生の軽微10件(従来3+P2 7)のうち6件は、JAに対応文が無いEN専用の一行要約(In one line)。今回のEN発生9件で一行要約由来は少なくとも2件(V3)。
- 重大: 前回6件はJA(R2)4/EN新規1/Rewrite新規1。今回は0。
### (b) 機序別の比率(1記事当たり)
| 機序 | 前回control(5本) | 前回P2(10本) | 今回B3全体(55本、EN最終36件) |
|---|---|---|---|
| added | 1.40 | 2.50(重大+0.1) | 0.24 |
| causal | 1.00 | 1.00 | 0.04 |
| scope | 0.80 | 1.10(重大+0.1) | 0.29 |
| subject | 0.40 | 0.50(重大+0.3) | 0.07 |
| time | 0 | 0.20 | 0.02 |
| undisclosed | 0.60 | 0.20 | 区分なし |
| other | 0 | 0.20(重大+0.1) | 区分なし |
| 計(軽微) | 4.2 | 5.7 | 0.65 |
- 前回の構成比(軽微): control added 33%/causal 24%/scope 19%/undisclosed 14%/subject 10%、P2 added 44%/scope 19%/causal 18%/subject 9%。今回EN最終はscope 44%/added 36%/subject 11%/causal 6%/time 3%。**今回はcausalの比率が低く(前回18〜24%対6%)、scopeの比率が高い**。
- 件数の水準差: 軽微1記事当たり、前回4.2〜5.7に対し今回0.65〜0.80(全44件基準は0.80)。重大は前回P2で0.6件/記事、今回0/55記事。条件は同一でない(5節)。
- 共通3テーマのP2軽微(STAGEWISE §4、⑤b)は1記事当たり meta 5.5/hormuz 8.0/space_weapons 3.0。今回B3(全工程の軽微)は meta 0.94/hormuz 0.56/space_weapons 0.90。**差が最大なのはhormuz(8.0対0.56)**。前回hormuz P2(2本・16件)の機序はscope 7、subject 3、causal 2、time 2、added 2。
### (c) P2で増えた機序(従来→P2、1記事当たり軽微、前回内)
1. **added(台帳外の追加・具体化)**: 1.40→2.50(+1.10)。meta 8(従来0)、ai_control 7(従来2)、sewer 6(従来3)、hormuz 2(従来0)。
2. **scope(範囲・限定語)**: 0.80→1.10(+0.30)。hormuz 7(従来1。貨物・徴収方法・単数化・制度規模の特定)。
3. **time・other**: 各0→0.20(+0.20)。timeはhormuzの「約24時間48分」を「一日」へ丸める2件、otherはsewerの用語不統一とai_controlのRewrite由来EN欠落。
- causalは不変(1.00→1.00)、undisclosedは減少(0.60→0.20)。
- 「全fact Note由来」かの検証: `notes_to_error_trace.md`(meta/hormuz P2 28件)ではNote由来の直接証拠A=0、無関係B=23、判定不能C=5。上記の増加が全fact Note転記によるとは**言えない(推測もしない)**。hormuzはHF-003(支払義務者は未提示)自体がbriefに非選定で、Note転記が原因になり得ない。同ファイルは、P2でhormuzの具体化が増えた原因がNoteラベルかbrief素材量・構造かは未切り分けと記載している。sewer/ai_control/space_weaponsには同様の追跡が無い(限界)。
### (d) Checker→Rewriteループ由来と判定できる件数
- Rewriteが**新規に生んだ**NG: 2件(ai-p2r2-07 重大=OPEN-238の無関係文置換、loop内で修正済・一時発生/ai-p2r2-08 軽微=Rewriteで必要なEN文が欠落、最終ENに残存)。全84件中2件(2.4%)。従来版は0件。
- Rewriteを経ても同種の誤りが形を変えて残った: meta-p2r2-02(重大、集計上は新規に数えない)。Rewriteの指示語曖昧文(meta-p2r1 "That")は判定保留で集計外。
- Rewrite(②→③)で修正されたもの: 従来0/2、P2 4/5(重大4)。JAはRewrite対象外のため、**EN修正済・JA残存**が重大3/軽微5(P2)・軽微2(従来)(OPEN-239)。
- 今回B3は`--no-checker`のためRewrite由来は0(比較不能)。

## 4. 重大NGカード(前回P2の⑤b残存4件+NTM 1件。参考に前回の一時重大2件)
- **meta-p2r2-02**(meta P2 r2、HC-012、subject): 工程=JA R2(R0に目的語欠落「相手に十分知らせない」、R2で「主役になった人間が知らされていなかった」が追加)、ENにも残存(Rewrite後も「the person on the other end」と対象断定が残る)。briefに両Note(「サービス全体を停止したと書かない」+多義)あり。ただしNoteに開示対象の語は無く、trace判定B(目的語欠落をWriterが補完)。Rewrite=経た(形を変えて残存)。B3 V0〜V6で同種の重大=なし(metaのsubject軽微4件はV0 2/V1 1/V3 1)。
- **ai-p2r1-01**(ai_control P2 r1、EVID-008、added=比喩で状況を逆に描く): 工程=JA R2(R0/R1に「厳重な監獄」「裏口の鍵」なし)、ENへそのまま、Rewrite cycle1でEN削除・JAに残存。briefに誤設定環境と自律的乗っ取りの区別を述べるNoteあり。Noteは比喩を誘導する内容ではなく、原因はWriterの比喩と思われる(推測)。Rewrite=経た(ENのみ修正)。B3にai_controlは無く比較不能。
- **sw-p2r2-01**(space_weapons P2 r2、F-001、subject=発表内容の取り違え): 工程=JA R2(R0/R1に無し)、ENでも発生、Rewrite cycle1-3でEN修正・JA残存。briefにF-001 Note(「軌道上兵器の配備を公式に認めた」までは可、名称・能力・標的は補わない)とF-011 Note(counterspaceは兵器に限らず地上・リンク等を含み得る)があり、F-011の広義定義がF-001の説明へ流入した可能性がある(推測、未検証、space_weaponsのNote追跡なし)。Rewrite=経た。B3 space_weaponsの重大=0。
- **sw-p2r2-02**(space_weapons P2 r2、F-001、scope=「初めて」の対象を兵器配備から防衛の備えへ拡張): 工程=JA R2(R0/R1に無し)、ENでも発生、Rewrite cycle1でEN修正・JA残存。Noteは上と同じ。Rewrite=経た。B3の重大=0。
- **hormuz-T0M0r2-01**(NTM、HF-002、subject/object=20%の対象が全貨物から安全確保費用へ入れ替わり): 工程=ENのみ(JAは正しい)=翻訳由来。T0=Note転記なし、Checkerなし、Rewriteなし、brief固定。つまりNoteなしで発生(Note由来ではない)。B3 V0〜V6で同種(hormuz EN、支払を義務確定的に書く形)の軽微が2件(V0・V5、ENのみ)。重大は0。
- 参考(前回P2の一時重大): ai-p2r1-02(EN新規、CONTROL-002「使われる」で主体入替、Rewrite cycle1で修正)/ai-p2r2-07(Rewriteが無関係文を置換、OPEN-238、precheck偽陽性が原因=DIAG-01で、Note・briefではない)。

## 5. 限界・データ欠落
- **前回のR0(初稿)単独評価が無い**。JAは最終稿(R2)のみ評価。R0/R1/R2の分離は、meta/hormuz P2 28件(`notes_to_error_trace.md`、意味上の判定)と本書の重大4件のgrepのみ。sewer/ai_control/space_weapons/従来版のR0由来比率は不明。`original.md`は保存されているが未評価。
- 前回の機序ラベルは本書の分類(台帳に`kind`なし)で、境界例あり(causalとadded、scopeとundisclosedなど)。STAGEWISE自身にも判定保留1・境界4がある。重大/軽微判定は前回・今回とも単独評価で人間確認なし、評価者が異なる。軽微の境界判断のぶれが条件差と同オーダーとREPORT §100-5にもある。
- 前回と今回は条件が揃っていない: テーマ(前回5、今回3)、記事数(15対55)、Checker/Rewriteの有無(今回なし)、briefの作り方(前回=P2全fact Note転記でbrief約2倍、今回=V0〜V6のbrief構造操作)、評価者・基準。水準差(4〜6件/記事対0.65〜0.8件/記事)を同一条件の改善と読むことはできない。
- 前回の従来版(control)は「notesなし」ではなくnotesを本文に畳んだ形(`notes_to_error_trace.md` §0-3)。Note由来の切り分けは弱い。N=テーマ別1〜2本。
- 前回の重大件数は§94の3件から§95で6件に再ラベルされたもの(sw 2件は§95作業で再ラベル)。
- 今回B3の重大0は床効果(REPORT §100-4)。B3記事55本はGate STOP 5本(V5 4/V3 1)を除く集合で、選択バイアスの可能性がある。
- 今回の評価JSONにundisclosed/otherのkindが無く、前回との機序の完全対応は取れていない。
- grepは文言一致のみで、言い換えによるR0存在は検出できない。
