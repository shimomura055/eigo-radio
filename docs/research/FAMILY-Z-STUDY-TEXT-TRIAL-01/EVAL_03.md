# EVAL_03(FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-03、Sonnet所見。Fable独立評価は別途)

評価対象: 最終版PROMPT=03c(Part 1=03c、Part 2=03b)の出力 `OUTPUT_03c_{gift,open_window,ig_nobel}_RAW.md`(主標本)+同Promptの再標本 `OUTPUT_03cR2_*`(安定性確認)。経緯の初版`OUTPUT_03_*`・中間`OUTPUT_03b_*`/`03bR2_*`・Before(Trial-02条件)`OUTPUT_02_RAW.md`(賢者)/`OUTPUT_02B_*`(X・Z新規2作品)。全出力は無編集(自動修正なし)。
モデル: gpt-6-luna(最新世代の推奨系。Trial-01/02と同一model_id・API設定=条件固定のため。旧/下位モデル使用ではない)。

## 1. 作品選定(理由)
| 区分 | 選定 | 理由 | 見送り候補 |
|---|---|---|---|
| 必須Z | 賢者の贈り物 | ユーザー指定 | - |
| X | イグ・ノーベル賞2026解説(ig_nobel_2026、ユーザー最終承認済み) | 英文構造が物語文と異なる(説明文+引用+数値比較+「Compared with what?」型の論の運び)。KPの種類が別: 複合形容詞コロケーション(nutrient-rich crystals)/過去分詞+前置詞の専門表現(bound to the protein)/比喩的イディオム(leap into action)。Part 2に数値比較(`more than three times as much A as B`)という読み誤りが記事の主張に直結する構文がある。正式KP・英語解説・公開本文が揃い、公開ページと本文が一致 | word_gacha(口語・比喩が多くPart 1は面白いがKPが比喩寄りに偏る)、uk_train(KPが後日UDR #169で変更された経緯があり正式KP成果物の一貫性の確認に追加コストがかかるため後回し) |
| Z | 開いた窓(the_open_window、ユーザー最終PASS) | 会話中心(『賢者』は地の文中心)で語順・構文が異なる。KPが句動詞的/副詞句/動詞+目的語+補語の別種(give way=拡張用法が豊富、at a moment's notice=仕事で頻用、keep someone company=社会的場面)。Part 1の「仕事・社会の用法/比喩的拡張」の検証に最適 | 猿の手(KPが名詞句中心で拡張用法の検証力が弱い)、二十年後(KP3個とも名詞句寄り)、メロス(翻訳由来文体) |

## 2. Part 1(実用性)評価 ― 判定: PASS(軽微注記あり)
基準(ユーザー§6): 実用場面が具体的/ニュアンス理解/自然な拡張用法の取りこぼしなし/創作なし/文法との重複なし。

| 作品 / KP | 03c主標本 | 再標本03cR2 | 判定・根拠 |
|---|---|---|---|
| 賢者 hand down | 家宝・家具に加え、伝統・知識・技能を後の世代や後任者へ | 家族の品・伝統・技術・知識+「法廷で判決を言い渡す」+pass onとの使い分け | PASS。ユーザー指定の『技術・知識・経験を後輩/次世代へ』を満たす(03初版: 『経験豊富な社員が若手に専門知識や仕事の勘所を伝える』)。hand down a verdictは実在の自然な用法で創作ではない |
| 賢者 catch sight of | 人混みで知人/看板が目に入る、noticeとの違い | catch a glimpse ofとの違い | PASS。Trial-02の良好な実用性を維持(同僚を見つける場面は03で追加) |
| 賢者 catch one's breath | 運動後+「忙しい時期や大仕事のあとにひと息ついて立て直す」 | 運動後+「忙しい仕事の合間にひと息」+驚いたあと | PASS。**ただし拡張用法(忙しさから一息)の説明は03初版1/1・03b 0/2・03c 2/2**。03bまでの指示では取りこぼしが発生したため03cで「拡張用法が一般に使われているかを確認し、使われていれば必ず説明」に強化した結果、再標本含め2/2で説明された |
| 開いた窓 give way | 物理的崩壊+圧力・感情に負ける比喩+道を譲る | 比喩(圧力に屈する/制度が取って代わられる)+give inとの使い分け | PASS。自然な拡張用法を網羅(Beforeは物理的崩壊のみ)。R2の「人が要求に譲歩する場合はgive inが一般的」はやや断定的だがgive way to pressureも自然なため要注意の程度 |
| 開いた窓 at a moment's notice | 急な依頼・変更への対応(仕事) | 同+immediatelyとの違い(予告・準備がほぼない状況に焦点) | PASS。注記: 03c主標本の「at short noticeは予告が少ないことに、本表現はすぐ動けることに重点」は近似表現の差を強調しすぎる懸念(出典に基づく区別ではない)。創作用法ではなく使い分け説明の過剰解釈リスク(軽微) |
| 開いた窓 keep someone company | 病院の付き添い/待ち時間 | 友人訪問/待ち時間、accompanyとの違い、業務上の付き添いはaccompanyが適切 | PASS。社会的場面と使い分けが具体的 |
| X nutrient-rich crystals | nutrient-richを土壌・環境にも使える、ただし健康的とは限らない | 農業・環境分野で使える、評価語でなく特徴の記述 | PASS。Beforeは本文再説に近かったが、拡張分野を追加。無理な仕事用途は付けていない(適切) |
| X bound to the protein | 物質どうしの結合(attached toとの違い)、他の文脈ではbe bound to=義務(03初版) | 専門的な響き | PASS。無理な比喩はなし |
| X leap into action | 仕事でのチーム対応、take actionより素早さ・意欲 | act quicklyとの違い | PASS |

- 創作用法: 全17出力で明白な創作は検出せず(人手確認)。文法解説への脱線: 検出せず(Part 1長はBeforeと同程度=約1.0〜1.3k字、水増しなし)。Part 2との役割重複: 検出せず。
- 参考例(USER_02 §3)との比較: hand down(技術・伝統の継承)・catch sight of(知人を見かける/ふと視界に入る)・catch one's breath(運動後+忙しさからのひと息)は03c主標本が参考例の方向性を満たす。逐語再現はない(Promptに参考例を入れていないため、一発生成で到達した評価として有効)。

## 3. Part 2(選定の学習価値・構文解説)評価
### 3-1. 賢者の贈り物 ― 判定: PASS(深さは中。倒置への改善は達成)
- 選定: 03/03b/03bR2/03c/03cR2の**全5標本が`Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers.`(倒置)を選択**(Promptに倒置・当該文は書いていない。Grep 0件)。前回NGのwhose解説は、全5標本でwhoseを主題とせず倒置を主題にした(whoseは構成要素の説明にとどまる)。
- §3の4点の充足(03c主標本/R2): (a)なぜ通常と異なる語順か=hereを先に出して場面に視線を向けてから主語を登場させる(○) (b)通常語順=`Two foolish young people sat here with gifts they could not use, and their love made ...`を比較用として明示(○。03b初回標本は関係節を落とした比較文で不完全だったが03c/R2は完全) (c)情報提示順序・焦点=「人物から入る通常語順 vs 場面から入る本文」の差を説明(○) (d)文学的効果=foolishとthe wisestの逆転、直前の「髪も時計も失った二人と使えない贈り物」の場面を受けて結末に二人を登場させる効果(○〜△)。
- 残存(深さ): 直前文`The magi were wise men who brought gifts ...`との呼応(wise men→the wisest)に触れた標本は0/5。文末に`the wisest of all gift-givers`を置く文末焦点(end-focus)の説明も薄い。Fable評価でこの水準が「必要十分」かを判断(私見=学習価値は§3の要求の大半を満たし、Trial-02のwhoseより明確に高い。呼応の指摘は更なる深みだが追加Trialの優先度は低い)。
- 前回との比較: Trial-02(whose=基礎用法・NG)→Trial-03(倒置+仕組み+通常語順との差+焦点+文学的効果)。**「whoseから倒置へ改善され、学習価値が高まったか」=はい**(Trial-02のPart 2は約500字・「whoseは所有の関係代名詞」止まり、03cは約1,650字で4観点を網羅)。

### 3-2. イグ・ノーベル賞解説(X) ― 判定: PASS
- 選定: 03b/03c/再標本とも`The crystals contain more than three times as much energy as the same weight of milk from several kinds of mammals.`を選択(03b以降の4標本で4/4)。初版03は基礎的な`Take that number on its own, and ...`(命令文+and)を単独で選び、基礎文法回避の方針に反したため03bで修正(03b以降の標本では単独選択は0。ただし03bR2・03cR2は2項目目として命令文+andを追加=03b以降4標本中2標本で基礎寄りの項目が混入)。
- 学習価値: 比較の基準(同じ重さ)を読み落とすと数値の意味を誤る点が、直後の段落(「人が飲めば3倍元気になるわけではない」)の主張理解に直結。Before(02B)も同じ文を選んでいたが、理由・難しさ・通常形との比較・焦点の説明がなく約520字。03cは約1,600字で「選定理由・理解しにくい理由・構文の仕組み・通常形との違い・提示順序と焦点」を満たす。
- 注記: 03c主標本の日本語訳「エネルギーを3倍より多く含んでいます」は正確。比較用英文`The crystals contain more than three times the energy found in an equal weight of milk ...`も適切。

### 3-3. 開いた窓(Z) ― 判定: **未達(選定の安定性と学習価値)**
- 5標本の選定: 03=`with them snarling above him`(付帯状況with)、03b/03bR2=動名詞主語`Inventing convincing stories at a moment's notice was Vera's speciality.`、03c=**0個**(「特別な解説が必要な文はありません」)、03cR2=`His doctor had recommended ..., but visiting strangers was hardly peaceful.`(動名詞主語。選定理由自体が「文の形自体は複雑ではありません」と自認)。Before(02B)は過去完了+動名詞主語とBefore節+could(基礎的)。
- 評価: 本文はB1目標で一文が短く、構造的に難しい文が元々ほぼ無い(倒置`Across the quiet garden came a young voice:`はあるが短く透明)。動名詞主語・付帯状況withはAdvanced学習者に基礎的で「基礎的すぎる文法を安易に選んでいない」を満たさない。03cの「0個」はPrompt(「適切な文がなければ0個」)どおりでむしろ妥当な出力だが、標本間で不安定(5標本中0個は1)。
- 原因仮説: (1)作品側の天井(学習価値が高い難文が少ない)。(2)Promptは0個を許容するが、モデルは「1個は選ぶ」方向に傾く(再標本で選定が揺れる)。反証済み: 指示強化(03→03b→03c)では改善せず、基礎文法の例示回避も効かなかった。
- 次の一手の候補(改善見込みの自己評価): (a)現状維持=0個を許容し、作品によってはPart 2が空/短い仕様とする(見込み: 追加費用0・安定性は低いまま)。(b)Prompt追加=「学習価値が高い文がなければ0個を優先し、基礎的な構文は選ばない」と0個側を強める(見込み: 中。1〜2円で検証可能)。(c)Part 2を「難文」から「読解効果の大きい文」にも広げる=仕様変更でありユーザーの§3方針(難しい文を選ぶ)と異なるため独断不可(判断候補、分類B寄りだがFable判断)。

## 4. Part 3・4への副作用 ― 判定: 副作用なし(軽微な重複1件)
- 構成: 全17出力でPart 3は1テーマ、Part 4は質問1問+回答例(英日)の形式を維持。Part 3/4のPromptは不変。
- 長さ(03c主標本vsBefore): Part 3 約300字(Before 275〜365)、Part 4 約360〜500字(Before 420〜555)。変化なし。Part 2のみ約500→約1,600字(最大2,500字)。
- 内容: Part 3の主題は従来同様(prove its worth/worth、The final boss of nutrition?、I almost expect to see them 等)。Part 4も作品内容に即した問い。劣化は検出せず。
- 重複: 03bR2賢者のPart 3が`foolish`と`wisest`の対比(Part 2の項目7と同内容)で重複。Trial-02でもPart 3が同対比でPart 2(whose)と近接していた。03c系の賢者2標本(worth)では重複なし。発生率はAfter賢者5標本中1。
- 4 Part一括生成による全体品質低下は観測されず。

## 5. Trial-02(Before)との比較表
| 項目 | Before(Trial-02条件) | After(03c) |
|---|---|---|
| Part 1 賢者 | 良好(ただし拡張用法の網羅は未指示) | 同等以上+catch one's breathの「忙しさから一息」+hand downの職場継承(2/2) |
| Part 1 開いた窓 | give way=物理的崩壊のみ | 比喩的拡張・道を譲る用法・使い分けを追加 |
| Part 1 X | 本文再説に近い | 分野拡張・近似表現との違いを追加 |
| Part 2 賢者 | whose(基礎・NG) | 倒置(5/5)、4観点+文脈 |
| Part 2 X | 同じ数値比較文を選ぶが説明が約520字で浅い | 選定理由・難しさ・通常形・焦点まで(約1,600字)。ただし03b以降4標本中2標本で基礎項目が追加される |
| Part 2 開いた窓 | 基礎的(過去完了+動名詞主語/Before節) | 基礎的な動名詞主語を繰り返し選択、0個は1/5 → 未達 |
| Part 3/4 | 基準 | 変化なし |
| 費用/call | 0.17〜0.23円 | 0.22〜0.35円(平均約0.31円)、所要20〜38秒 |

## 6. 残存問題
1. 開いた窓Part 2の選定不安定(§3-3)。
2. 賢者Part 2の文学的効果の最深部(magiとの呼応・文末焦点)は未到達。
3. X: Part 2に基礎項目(命令文+and)が03b以降4標本中2標本で混入。
4. Part 1「近似表現の使い分け」記述が過剰に断定的になるリスク(at short notice、give in)は軽微だが残る(Production採用時は対象Part 1の使い分け文に事実確認を入れるか否かは設計判断)。
5. サンプル数: 作品あたり主標本1+再標本1(+初版・中間版)で統計的保証ではない。
