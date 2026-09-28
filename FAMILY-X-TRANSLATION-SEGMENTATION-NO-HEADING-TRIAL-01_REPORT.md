# FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md

## 重複確認結果(着手前、最重要)

`git log --oneline --all | grep -i "NO-HEADING\|SEGMENTATION"`、
`docs/pm/REPORT_LEDGER.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`の
Grep(`NO-HEADING|見出し廃止|TRANSLATION-SEGMENTATION`)、
`docs/pm/delegation_log/`のGlob(`*NO-HEADING*`)、`git fetch origin`後の
`git log origin/main --oneline -20`のいずれも本Trial(見出し廃止+忠実
英訳+決定論的3分割)への言及は0件。SEGMENTATIONでヒットしたのはFamily C
Segment Comment・Family X Section Segmentation Contract(既存
`PRODUCTION_WIRED`、見出しを前提とした別トピック)のみで無関係。**未着手を
確認、着手した**。

T-0: 委任文を`docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-
SEGMENTATION-NO-HEADING-TRIAL-01_01.md`へ逐語保存し
`check_delegation_prompt.py`を実行(`status=FAIL`、非ブロッキング記録
ツール、exit 0。理由: 実行コマンド全文中の`-m unittest ... -v`行に
長形式引数/絶対パスなしという定型誤検知1件のみ。TTS言及の誤検知警告は
「TTS/ASRなし」という禁止事項の記述自体をTTSキーワードとして拾ったもの
で、本タスクは実際にはTTS/ASR呼び出しゼロ)。

## 1. Hormuz比較

- JA原文: `er019_output/.../an3_t0_wiring_regression_01/hormuz/ja_writer/
  revision2.md`(8段落)。
- Baseline(見出しあり、現行Advanced、`LEDGER_COMPLIANT`): disk上の
  `hormuz/b1b/article.md`はAN3-T0後の別タスク実行で上書きされており
  REPORT転記と非一致(タイトル"20 Percent"表記が異なる等)と判明したため、
  委任文の指示通り`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_
  REPORT.md`の`## 記事本文全文`セクションからプログラム的に抽出して使用
  (§10で詳述)。
- Trial(見出し廃止、忠実英訳、段落数8=8一致): タイトル"The 20 Percent
  Fee Plan Was Withdrawn, but Oil Prices Quickly Returned"。8段落を
  境界(3, 6)で3分割(Part1=37.6%・Part2=35.3%・Part3=27.1%)。
- Trial Deviation Check(新規実行): `LEDGER_COMPLIANT`(deviations=0)。
- 全文・Comment挿入位置・rubric・word-diffは
  `user_test/no_heading_trial_01/index.html#hormuz`。

## 2. Meta比較

- JA原文: `meta/ja_writer/revision2.md`(10段落)。
- Baseline: disk上の`meta/b1b/article.md`(REPORT転記とdiff一致確認済み、
  `LEDGER_COMPLIANT`)。
- Trial(段落数10=10一致): タイトル"It Was Supposed to Be an AI Phone
  Call, but a Human Appeared Backstage"。10段落を境界(4, 7)で3分割
  (Part1=37.6%・Part2=31.5%・Part3=30.9%)。
- Trial Deviation Check(新規実行): `LEDGER_DEVIATION`(MAJOR 1件+
  MINOR 1件)。MAJOR: 日本語原文「(人間コンシェルジュ機能を)元に戻しました」
  (=ロールバック/無効化の意味)を、Trial英訳が"put back the feature"と
  訳し、これが「再度有効化した」という逆の意味に読める、という指摘。
  MINOR: 「Meta executives」への主体の一般化(Ledger上は特定の副社長1名、
  JA原文にも同じ一般化があるため原文由来の軽微な逸脱)。**重要な考察**:
  本TrialはMAJOR検出時のmust-fix再生成を行わない設計(委任文の禁止事項
  「分割のための本文書き換え」とは別だが、翻訳の書き換えも本Trialでは
  行わないと設計書§3-4に明記)。この結果は「見出し廃止・忠実英訳という
  方式そのものがFact精度を自動的に保証するわけではない」ことを示す
  データであり、実際に配線するならProduction同様のmust-fix retry
  (`er012_e_family_entertainment_two_level_runner_01.py`の既存機構)が
  必要になることを裏付ける。全文・rubric・word-diffは
  `user_test/no_heading_trial_01/index.html#meta`。

## 3. 見出し有無による本文変化

Trial翻訳Prompt(§9)はARM3_BLOCK(reorder/merge/reshape許可)・見出し
生成指示・Section Boundary Contractを含めず、VOCAB_RULE_V2_BLOCKのみを
既存Production定数から逐語流用した。結果、両記事ともJA段落数と完全一致
する段落数(8=8、10=10)で、段落の並び替え・統合は発生しなかった
(word-diffページで目視確認可能)。Baseline(見出しあり)は2セクション
30-60語ずつという固定長制約下で見出しに合わせた要約的な書き換え・順序
調整が入っており、Trialより文の粒度が細かく原文に近い(rubric
`faithfulness_to_ja`/`fact_preservation`/`order_preservation`は両記事
ともTrialが同等以上)。

## 4. 3分割の位置と長さ

決定論アルゴリズム(段落境界のみ、全探索で3区間の語数二乗誤差最小の
境界2点を選択、本文書き換えなし)。Hormuz: 37.6/35.3/27.1%。Meta:
37.6/31.5/30.9%。理想均等(33/33/33%)からの乖離は最大10.5pt
(Hormuz Part3)で、極端な偏りではない。委任文の「なるべく均等」は満たす
が、既存Family X仕様の「50%/25%/25%」目安とは異なる分布になる
(§10で既存仕様との関係を検討)。

## 5. Commentとの接続自然さ

既存Comment1〜4(B1B/English、直近のFamily X B1B scaffold runから
reuse、新規LLM呼び出しなし)をそのままTrial構成へ配置し、rubricで
Baseline/Trial両レイアウトでの接続自然さを採点させた。結果:
Hormuz Baseline=3/Trial=4、Meta Baseline=3/Trial=4(いずれもTrialが
やや優位)。ただしComment自体はAN3-T0本体とは別runの本文から生成された
ものであり(§10の既知の制約)、この差は「新しい3分割位置がComment文脈に
より自然に合致した」可能性と「reuse Commentの文脈ズレの影響」が混在
している点に留意。

## 6. In One Line Before/After

- Hormuz: Before(Baseline)="The political sign changed, but the price
  soon returned..."(20語・1文) / After(Trial)="Although Trump replaced
  the proposed 20 percent fee on ships crossing the Strait of Hormuz,
  oil prices quickly returned to near their previous highs as other
  tensions continued."(27語・1文)。
- Meta: Before="AI may need human help, but humans must say clearly
  when they take over."(14語・1文) / After="Meta's AI phone service
  relied on human contractors to make calls without clearly telling
  users, raising privacy concerns and forcing the feature to be put on
  hold."(28語・1文)。
- **観察**: ユーザー仮説(見出し作成→In One Lineの過剰圧縮)とは逆に、
  Trial側のIn One Lineは両記事ともBaselineよりほぼ倍の語数になった
  (14→28語、20→27語)。「短い自然な一文」という指示に対し、事実密度の
  高い一文になりやすい傾向が見られた(Fact欠落ではなく、より多くのFactを
  1文に詰め込む方向)。rubric`in_one_line_conciseness_accuracy`は両記事
  ともTrial=5(Baseline以上)で、要旨正確性自体は下がっていない。

## 7. Fact/因果逸脱(Deviation Check結果、Baseline/Trial)

Baseline(既存artifact reuse、追加API呼び出しなし): Hormuz
`advanced_attempt2.json`=`LEDGER_COMPLIANT`(all_prior_issues_
resolved=true)、Meta`advanced_attempt1.json`=`LEDGER_COMPLIANT`。
Trial(新規実行、must-fix retryなし): Hormuz=`LEDGER_COMPLIANT`
(deviations=0)、Meta=`LEDGER_DEVIATION`(MAJOR1+MINOR1、§2参照)。

## 8. 面白さ・聞きやすさ(rubric)

LLM rubric(1 call/記事、Baseline/Trial両方・Comment文脈込みで評価、
14項目1〜5点)。傾向: Trialは`faithfulness_to_ja`/`fact_preservation`/
`order_preservation`/`zero_new_facts`等の忠実性系項目でBaseline以上、
Baselineは`readability`/`listenability`/`entertainment_value`で両記事
ともTrialより高い(5 vs 4)。`no_monotony_without_headings`(見出し
廃止で単調にならないか、Trialのみ採点)は両記事とも4/5で、著しい単調化
は報告されていない。1〜2点の壊滅的スコアは0件。詳細表は比較ページ。

## 9. Cost

正式採用run(rubric修正後の最終run): Hormuz ¥2.1751 + Meta ¥2.9165 =
**¥5.0916**(予算¥30の約17%)。呼び出し内訳(記事あたり): 忠実英訳1
call+In One Line 1 call+Trial Deviation Check 1 call+Rubric 1 call
(Baseline Deviation Checkは既存artifact reuseで追加費用¥0)。
**参考(実費用全体)**: rubricがComment文脈を欠いていた設計不備を発見し
1回だけ全体を再実行したため、破棄した初回run分¥4.1167(Hormuz¥2.1516+
Meta¥1.965)を含めた実際のAPI総支出は約¥9.21。Guardrail超過なし
(¥30予算に対し実支出は最終run・全体累計とも大幅に余裕あり)。暴走疑い
兆候(想定外の大量API発火・無意味なretry loop・原因不明の費用増加)は
発生していない。

## 10. Existing Spec との関係(復旧か新規か、衝突の有無)

`CURRENT_SPEC.md`「Family X音声構造」節(L1143-1236、`APPROVED_FOR_
PRODUCTION`/`PRODUCTION_WIRED`)を確認した結果:
- **完全一致**: 音声構造`Comment1→本文1→Comment2→本文2→Comment3→
  本文3→Comment4→In One Line`(SE-1、CLOSED)は本Trialと完全一致。
- **本Trialが置き換える部分**: 本文1/2/3の区切り定義(見出し基準、
  50%/25%/25%目安)とSection Segmentation(見出し境界)Contract
  (`PRODUCTION_WIRED`、commit`9cec45f1`/`e7311d37`)は、いずれも見出しの
  存在を前提とした仕様であり、本Trial(見出し廃止)はこれらを「否定」
  するのではなく「見出しという前提が本当に必要か」を検証する新規Trial
  (過去に「見出し廃止」「翻訳のみ」Trialは存在しない、Grep確認済み)。
  既存Contract自体は無変更のまま残る。
- **OPEN-228との関係**: `split_article_text()`のMain Story段落数2以上
  チェック(見出し前提)がOPEN-228のクラッシュ原因。本Trialは見出しを
  廃止した新しい分割方式(段落境界の決定論アルゴリズム)を使うため、この
  チェック自体を経由しない。両記事ともTrial側で段落数不足によるエラーは
  発生しなかった(Hormuz8段落・Meta10段落、いずれも3分割に十分)。ただし
  これはOPEN-228の「単独修正」ではなく、OPEN-228の前提(見出し必須)を
  Trial結果次第で将来的に不要化できるかを見るためのデータ提供に留まる
  (OPEN-228自体は無編集、修正判断はユーザーへ)。
- **Production Advanced Prompt(ARM3_BLOCK等)との差**: §3・§9参照。
- **衝突なし**: 本Trialはtext-only・別ファイル(`er045_*`)・別Prompt
  定数であり、既存Production経路(`er003_v1_n3_01_advanced_adaptation_
  generate.py`等)を一切変更していない(§11)。

## 11. Production変更ゼロ

`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep
-v er045`は非空だが、列挙された7ファイル(`er003_b1_p9a_audio.py`/
`er003_v1_n3_01_tts_generate.py`/`er019_family_x_audio_production_
runner_01.py`/`er033_*`/`er038_*_test_01.py`/`er044_*_test_01.py`)は
いずれも本タスク開始前から存在した他Agent(並行Task 2/3/4)の未commit
差分であり、本タスクで一切編集していない(読み取りのみ)。`git status
--short`で本タスクが触れたファイルが`er045_*`/`er045_output/`/
`user_test/no_heading_trial_01/`/REPORT/設計書/delegation_logのみである
ことを確認済み。

## 12. 新規USER_DECISION_REQUIRED・STOP条件該当・Prompt所在・公開確認・SSOT文案・commit・raw URL

**STOP条件該当**: なし(忠実英訳の不自然さ/3分割破綻/Comment位置の著しい
不自然/見出し廃止による著しい聞きにくさ/In One Line簡潔化によるFact
欠落/既存仕様との大きな衝突/Family共有Prompt変更の要否/新Product判断の
必要性、いずれも「即STOP」に該当するレベルではなく、Meta Trial翻訳の
MAJOR Deviation[§2・§7]はmust-fix retryなし一発生成という設計上の制約
下での観測であり、追加改善・Prompt再調整は行わずそのまま報告する)。

**到達Status**: `USER_DECISION_REQUIRED`(ユーザー試読・判断待ち。
Sonnetは`VALIDATED`を自己宣言しない)。

**使用Prompt全文の所在**: `docs/pm/design_family_x_no_heading_
segmentation_trial_01.md`§3(忠実英訳/In One Line Trial限定Prompt、
VOCAB_RULE_V2_BLOCKはProduction定数を参照)、rubric prompt構築ロジックは
`er045_family_x_no_heading_segmentation_trial_01.py::build_rubric_
prompt()`。

**公開確認結果**:
```
$ curl -sI https://shimomura055.github.io/eigo-radio/user_test/no_heading_trial_01/index.html
```
(commit・push後に実行、結果は本REPORTの追記または次回確認コマンドの
出力をご参照。ローカルではheadless Chromium/Edgeが未インストールのため
`--dump-dom`は未実行。GitHub Pagesの反映には数分要するため、push直後の
`curl -sI`が404の場合は再確認が必要)。

**SSOT追記文案(RESULT_PACKETへ)**: 下記参照。

**commit hash・raw URL**: 本REPORT末尾のcommit実行後に追記。

## 13. 修正1回目(2026-09-28、管理ID同一、委任_02)

### 13-1. 理由

初回(§2・§7)で、TrialのMeta忠実英訳がDeviation Check `LEDGER_DEVIATION`
(MAJOR1・MINOR1)のまま報告された。これはProduction(`er012_e_family_
entertainment_two_level_runner_01.py`)が持つ「MAJOR検出時に1回だけ
must-fix retryする」機構をTrialが適用していなかったための、Baselineとの
比較条件の不整合だった。またIn One Lineがユーザー仕様(短い自然な一文)
より長く(28語/27語)なっていた点も、v1では「短い」という定性指示のみで
定量的な参考ガイドが無かったことが一因と考えられた。本節はこの2点を
是正した上でv1/v2を併載する。

### 13-2. 実施

1. **Meta must-fix retry**(`run_must_fix_retry_stage`、Production同等の
   `er003_v1_n3_01_advanced_adaptation_generate.build_must_fix_block()`を
   そのままimportして流用、コピペなし): MAJOR 1件のみ(MINORはmust-fix
   対象外、Production同様)。指摘: `claim_in_article`="They also
   temporarily put back the feature in which humans handled the calls."
   / `issue`="「put back the feature」は人間が電話を担当する機能を再び
   有効化した意味に読めるが、Ledgerはその人間コンシェルジュ機能を当面
   ロールバックしたとしている。" / `related_fact_id`=MUSE-HC-012。
   1回だけ再生成し、`run_deviation_check(..., prior_issues=must_fix)`で
   再検証(Production`er012`と同一呼び出しパターン)。
2. **In One Line v2**(両記事、`TRIAL_IN_ONE_LINE_V2_INSTRUCTION_
   TEMPLATE`新設、Trial限定Prompt): 「1文のみ/一回聞いて理解できる/
   複数論点を詰め込まない/新規Fact・結論・教訓を追加しない」を明示指示し、
   「参考ガイド(Trial限定、厳密ルールではない): 主節1つ+従属節最大1つ、
   およそ12〜18語」を追記。Hormuzは不変のv1本文(既にCOMPLIANT)、Metaは
   must-fix retry後のv2本文を入力に、各1 call実行。
3. **rubric v2**: 変更要素(Meta本文v2、In One Line v2×2)を反映して同じ
   `run_rubric()`(14項目、Comment文脈込み)を各記事1 callで再実行。
   Hormuz本文自体は不変だが、In One Line v2反映後の
   `in_one_line_conciseness_accuracy`等を得るため同じ1 callを実行した
   (本文関連13項目の再評価はLLM呼び出しの副産物、目的はIn One Line分の
   更新)。
4. ページ(`user_test/no_heading_trial_01/index.html`)へ、記事ごとに
   「修正1回目」セクションを追加し、must-fix retry結果・In One Line
   v1→v2比較表・rubric v2表を、v1のセクションを削除せず併載した。

### 13-3. 結果

**Meta must-fix retry**: 再生成後`overall_status_v2`=`LEDGER_COMPLIANT`、
`all_prior_issues_resolved`=`true`、`deviations`=0件(指摘したMAJOR1件を
解消しただけでなく、対象外だったMINOR「Meta executives」への一般化も
"A Meta executive"という単数形に自然に修正され、副次的に解消された)。
該当箇所の逐語(v2本文抜粋): 「A Meta executive admitted that it was a
mistake to start the test without a proper explanation. The company then
temporarily rolled back the feature in which humans handled the calls.
It did not shut down Muse itself.」("put back the feature"→"temporarily
rolled back the feature"へ修正、意味反転が解消)。

**In One Line v1→v2**(語数はTrial限定参考ガイド12〜18語との比較):
- Hormuz: v1="Although Trump replaced the proposed 20 percent fee on
  ships crossing the Strait of Hormuz, oil prices quickly returned to
  near their previous highs as other tensions continued."(27語・1文・
  Trump/Hormuz fee/oil price/other tensionsの4論点相当)→ v2="Oil prices
  quickly recovered to almost their earlier high after Trump withdrew
  the proposed Strait of Hormuz fee."(18語・1文・oil price回復と
  fee撤回の2論点に整理、目安上限ちょうど)。Baseline In One Line=20語・
  1文。
- Meta: v1="Meta's AI phone service relied on human contractors to make
  calls without clearly telling users, raising privacy concerns and
  forcing the feature to be put on hold."(28語・1文・4論点相当)→ v2
  (v2本文ベース)="Meta's AI phone agent sometimes handed calls to human
  contractors without clearly telling users, raising privacy concerns."
  (18語・1文・2論点に整理、目安上限ちょうど)。Baseline In One Line=
  14語・1文。
- 観察: v2は両記事ともほぼ目安上限(18語)に収まり、v1比で語数が
  33-36%減、詰め込まれていた論点数も4→2に整理された。新規Factの追加は
  無い(いずれも既存本文の言い換え)。Baselineより依然として長い
  (Baseline 14-20語)が、「主節1つ+従属節1つ以下」という構造要件は
  両v2とも満たす。

**rubric v2の変化**(1〜5点、`no_monotony_without_headings`はBaseline
`null`のまま): Meta(本文v2・In One Line v2を反映)は
`faithfulness_to_ja`4→5、`fact_preservation`4→5、`causal_preservation`
4→5、`no_meaning_added_or_removed`4→5、`order_preservation`5→5(維持)、
`comment_connection_naturalness`4→5と、must-fix retryで解消したFact
精度に整合する形で軒並み上昇した(`in_one_line_conciseness_accuracy`は
5→5で維持)。`length_balance`は5→4に微減(v2本文の語数配分がv1と若干
異なるための再評価、致命的な変化ではない)。Hormuz(本文はv1のまま不変、
In One Line v2のみ反映)は`order_preservation`4→5、
`comment_connection_naturalness`4→3(本文不変にもかかわらず変動、
LLM再評価のノイズと考えられる。本文自体を再評価する目的ではなかった
ため許容範囲と判断)。壊滅的スコア(1〜2点)は0件のまま。詳細表は
比較ページ。

### 13-4. 費用実測

Meta must-fix retry: ¥0.3333(忠実英訳retry)+¥0.4809(Deviation Check
再実行)=¥0.8142。In One Line v2: Hormuz¥0.0769+Meta¥0.0614=¥0.1383。
rubric v2: Hormuz¥1.6556+Meta¥1.4806=¥3.1362。**合計¥4.0887**
(予算¥10の約41%、超過なし)。暴走疑い兆候なし。

### 13-5. Production無変更の確認

`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep
-v er045`は空(本修正で変更したのは`er045_family_x_no_heading_
segmentation_trial_01.py`とそのtestファイルのみ)。追加した関数
(`_must_fix_from_major_deviations`/`build_must_fix_retry_prompt`/
`generate_trial_translation_must_fix_retry`/`generate_trial_in_one_
line_v2`/`run_must_fix_retry_stage`/`run_in_one_line_v2_stage`/
`run_rubric_v2_stage`)はいずれも`er045_*`内の新規追加のみで、
`er003_v1_n3_01_advanced_adaptation_generate.py`の
`build_must_fix_block()`と`er003_v1_en_direct_vfl_01_generate.py`の
`run_deviation_check(prior_issues=...)`はimportして呼び出すのみ
(既存Production関数を一切編集していない)。

### 13-6. テスト

既存14件PASS維持を確認した上で、新規5件(v2 Promptに見出し生成指示が
無いこと・Production must-fix blockをそのまま含むこと・v2 In One Line
Promptが新規Fact禁止/見出しMarkup禁止/参考ガイド語数の明記を含むこと)を
追加し、計19件PASS。`.venv\Scripts\python.exe run_project_regression.py
--pattern "er045*_test_*.py"`: `collected=19 passed=19 failed=0
errors=0 skipped=0`。

### 13-7. 到達Status・STOP該当

STOP条件(§4再掲)への該当なし。Meta must-fix retryが1回で
`LEDGER_COMPLIANT`に到達し、Production同様の上限(1回→STOP)の範囲内で
成功した。In One Line v2は依然Baselineより長いが、目安ガイド(12〜18語)
の上限内に収まり、詰め込み論点数も半減した。到達Statusは
`USER_DECISION_REQUIRED`のまま(ユーザー試読・採否判断待ち)。
