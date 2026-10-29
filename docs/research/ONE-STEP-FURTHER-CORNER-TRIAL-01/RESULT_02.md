# RESULT_02: One Step Further 品質検証Trial 委任_02(残課題解消、2026-10-30)

Status: Trial完了。Closeout案=**VALIDATED**(Trial専用・Production未配線・未承認・既定OFF以前に配線なし)。新コーナーの正式採否・モデル・表現固定方式・表示=ユーザー判断(UDR #225、Fable提示)。現行ニュアンス解説は廃止決定済み(2026-10-30、DECISION_LOG)=比較参考としてのみ併置。
追加費用: **¥32.23**(呼出16回、本委任通常上限¥30を超過、¥40以内。理由=38案の統合独立監査1回¥12.58を必須としたため。委任文の許容範囲内)。Trial累計 ¥59.93+¥32.23=**¥92.16**。

## 1. 比較ページ(6ケース)
- 学習コンテンツ本体: https://shimomura055.github.io/eigo-radio/user_test/one_step_further_trial_01/index.html
- 開発ログ・内部評価(分離、委任_02の全生成・監査・費用を節A〜Fに追加): 同`dev_log.html`
- index.htmlは6ケース(Y/X/Z×Standard/Advanced)の主候補(基本EN/JA・発展EN/JA・学習ポイント・基本との違い・選定理由・着想元)を全文掲載。折りたたみにluna v3案、Yは3候補方式の見本、現行ニュアンス解説は「廃止決定(比較参考)」と注記。

## 2. 作業結果
### 2-1. luna向けStd難度制御(Prompt v3)
- v3=v2+「Standardは3〜4語以内の短い定型句・句動詞、発展文12語前後、抽象的・論述的表現(come to terms with等)不可」+「発展文は日常で自然な形」。Prompt: `tools/osf02_gen.py`(PROMPTS["v3"])。6セル、gpt-6-luna、¥1.36(1セル平均¥0.23、25.8秒)。
- 独立監査(gpt-6.1-sol、匿名・順序シャッフル、38案1回、各項目1〜5):

| 条件 | n | 学習価値 | 正確性 | 例文自然 | レベル適合 | 3点以下 | 捏造 | KP重複 |
|---|---|---|---|---|---|---|---|---|
| luna v3 Standard | 4 | 4.50 | 4.50 | 4.75 | **4.75** | **0** | 0 | 0 |
| luna v3 Advanced | 5 | 4.40 | 4.40 | 4.60 | 4.20 | 1 | 0 | 0 |
| luna v3 全6セル | 9 | 4.44 | 4.44 | 4.67 | 4.44 | 1 | 0 | 0 |
| (参考)luna v2 Std(委任_01) | 10〜11 | 4.1〜4.4 | 4.5〜4.6 | - | 3.64〜3.70 | - | 0 | 0 |
| (参考)sol v2 主候補 | 9 | 5.00 | 4.67 | 5.00 | 4.89 | 1 | 0 | 0 |
- 判定(合格基準=Stdレベル適合≥4.5・学習価値≥4.5・3点以下0件): **Standardは基準達成**(レベル適合3.7→4.75、学習価値4.5、3点以下0。ただしn=4)。**6セル全体では未達**(学習価値4.44、X Advの`hold up under scrutiny`が学習3・正確3・レベル2で、本文の慎重な因果解釈を「結果への疑い」に変えた=3点以下1件)。
- **「luna採用可/不可」: luna単独で6セル全て(特にAdvanced)は『不可』、Standardのみなら『可』(小標本・条件付き)**。難度規則の効果は確認できた(v2の副作用を解消)。単価の判断材料: 全sol=約¥6.5/セット(70円の9%)、全luna v3=約¥0.37〜0.51/セット(0.5〜0.7%)、Std=luna・Adv=solの混成=約¥3.5/セット(約5%、混成の品質は本Trialで直接は未検証=監査済みの各条件の組合せ)。

### 2-2. Y Advanced例文の自然さ+指摘の改善
- 差替え前: `make their decision about me`(硬い)。sol v2を同一Promptで再生成(1回、¥3.76): **`I'm sad, but I don't want to make this about me.`**(核`make something about someone`)。監査は全項目5(例文自然5)。これを主候補へ差替え。差替え前の案はdev_log.html節Cに保存。
- X Adv「言い過ぎ注意」・Z Std「letの説明が回りくどい」は学習ポイント文のみsolで1回ずつ再生成(各¥1.32)。再採点で X Adv 正確性3→5・指摘なし、Z Std 正確性4→5(「語義説明の反復でやや辞書的」の軽微な指摘のみ)。主候補へ反映(改善前後はdev_log節D)。

### 2-3. 表現固定の方式検証(Y、候補3件→選別)
- 方式: v3の規則で「3候補を価値順に出力(自己採点付き)」、sol1回+luna2回(Std/Adv)。機械検査(核表現のKP/本文との重複、禁止例、字数)は全18候補で指摘0。
- 結果(top3の核表現):
  - Y Std: sol=`run A by someone`/`give someone space`/`could use A`、luna1=`make it all about A`/`give A some space`/`hear A out`、luna2=`talk A through`/`find my place`/`mean a lot`。rank1の一致は0/3。ただし`give (someone) space`はsol・luna1・luna v3単発の3生成に出現。
  - Y Adv: sol=`It's less about A and more about B`/`It's not my place`/`what works for someone`、luna1=`not so much A as B`(同型)/`be mindful of A`/`put someone on the spot`、luna2=`make room for A`/`It dawns on someone`/`have a say in A`。rank1は2/3(solとluna1が同型、luna v3単発も同じ)。
- 品質: sol 3候補×2=6案は全て学習価値4以上・正確性5・3点以下0(平均4.83/5.00)=**3候補のどれを人が選んでも使える**。luna 12案は3点以下4件(33%)=自動選別なしで提示すると質のばらつきが出る。自己採点は機械・自己採点では識別できず(solは全案ほぼ満点、lunaは自己満点でも監査で正確性3の案あり)。
- 結論: 同一表現そのものの固定(機械的な再現)は未達。**「3候補を出し、複数生成で共通して出る表現(consensus)を優先し、最終はHR/Fableが選ぶ」運用が現実的**。3候補方式のsol費用は1セル¥4.6〜5.7(単一案の約1.5倍)。HR(人が複数案から選ぶ)との親和性は高く、sol候補なら選択肢のどれも採用品質。lunaで3候補にするなら独立監査(1案あたり約¥0.33)等のGateが必要。

## 3. 学習価値・再現性の評価(まとめ)
- 学習価値: sol主候補5.00(n=9)、luna v3は4.44(Std 4.50)。現行ニュアンス解説2.3〜2.5(委任_01、廃止決定済み)。
- 正確性: 捏造0(監査・目視)、KP重複0(機械56+38項目、監査のkp_overlapはluna `not so much A as B`の1件=文法練習との重複指摘のみ)。
- 再現性: 品質は再現(solの3点以下は0〜1件)、表現は再現せず→3候補+consensus+HR選択で運用する設計が必要。
- 監査はsol(sol生成物の自己採点バイアスあり)。luna v3のn=9は小標本。

## 4. QCD
| 項目 | 値 |
|---|---|
| sol v2 1記事セット(2Lv) | 約¥6.5(70円の9%)、1セル約25〜37秒(並列48秒) |
| sol 3候補方式(1セル) | ¥4.63(Std)/¥5.67(Adv)、48〜69秒 |
| luna v3 1記事セット | Y¥0.51 / X¥0.37 / Z¥0.49(70円の0.5〜0.7%)、1セル19〜33秒 |
| luna 3候補(1セル) | ¥0.30〜0.50、35〜64秒 |
| 独立監査(38案) | ¥12.58(1案約¥0.33)、49秒 |
| 本委任費用 | ¥32.23(呼出16回)、Trial累計¥92.16 |
(品質・QCD分析: Q=luna単独はAdvで不足、solは基準到達。D=並列で約1分/記事。C=sol全面は+¥6.5/セット、Std=luna混成は+約¥3.5。)

## 5. 受入条件1〜8の再確認
1. 学習価値: sol 6セル全てLV≥4(5.00)○、luna v3 Stdは4.5○/Advは△。2. 発見: `make this about me`、`it's not my decision to make`、`let it show`等○(最終はユーザー)。3. 正確性: 4〜5、指摘事項は修正済み○。4. 日本語の簡潔さ: point_ja≤130字、監査4.5〜4.8○。5. 関連・捏造0○。6. KP/文法重複0○(機械)。7. 他Family・レベルで品質再現○、表現再現△(上記)。8. 時間・費用: 測定済み○。

## 6. 正式採否判断に必要な事項(ユーザー判断候補)
(1) 生成モデル: sol全面(高品質・+¥6.5/セット) / luna単独(基準未達・Std限定なら可) / Std=luna・Adv=sol混成(約¥3.5、要最終確認Trial)。(2) 表現固定方式: 3候補+consensus+HR選択を採るか、単一案+再生成か。(3) 表示位置・分量: 1レベル1〜2件を推奨(本Trialは主候補1〜2件)。(4) HR提示: 候補3件を人が選ぶ単位・事前Gate(捏造/KP重複/レベル適合)。(5) 既存公開記事への遡及適用の可否・費用。(6) ニュアンス廃止との関係=廃止は別仕様変更として管理(UDR #225のユーザー指示に従い、OSF配線の理由にしない)。(7) 採用提案前のFable/Opus独立評価(11-3条件C)。

## 7. Closeout案
**VALIDATED**(Trial専用)。条件=(a)モデル選択(Adv=solが妥当、Std=luna可)(b)表現固定は3候補+HR選択で運用 (c)ユーザーが比較ページを読んで「覚えたい」と判断。Production未配線、APPROVED_FOR_PRODUCTIONではない。次の一手の候補: (i)ユーザー採否 (ii)採用の場合のみ、sol/luna混成の小規模最終確認Trial(別委任・費用承認) (iii)不採用ならTrial資産保管して終了。

## 8. 使用モデル・生成物
使用モデル: 生成=gpt-6.1-sol(最新上位)・gpt-6-luna(現行Production route、費用比較)、監査=gpt-6.1-sol(最新)。ツール=`tools/osf02_gen.py`/`osf02_audit.py`/`osf02_page.py`(Trial専用、Production非import)。生成物=`out/*__v3__l1.json`、`*__c3__{s1,l1,l2}.json`、`y_adv__v2__s2.json`、`*__pointfix__s1.json`、`osf02__AUDIT.json`、`usage_log_02.jsonl`、`dev_log_01_backup.html`(委任_01版dev_log、冪等再生成用)。
