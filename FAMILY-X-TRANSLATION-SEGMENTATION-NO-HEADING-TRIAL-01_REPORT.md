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
