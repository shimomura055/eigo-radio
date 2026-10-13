# plan_01 (FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01, 生成前)

## 固定
- model: gpt-6-luna / reasoning effort high / developer message=`日本語のListening Support原稿を作成してください。` / `a2gen.run_support_text`経由(er072/er074と同一)。
  使用モデル=Production Preview/Comment生成と同一。最新世代か=現行Production最新(gpt-6-luna)。例外理由=現行Production出力との比較可能性。
- 原稿: `er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer/std.md`、Part境界 boundaries=[8, 15](segment_plan_a2.json)、Part1=`parts[1]`(段落0..7)。
- A1: er074条件Eの`build_roles()["E"]`+ctx(`【エピソード全文(参考、新しいFactの追加禁止)】`+std全文)を逐語使用。Prompt探索なし。
- A2: `fam_c.generate_family_c_a2_comment(n=1)`、content_facts=Production固定文(逐語)、art=`【これから聞く部分】\n{Part1}`+末尾に追加ブロック(下記)。同TakeのA1 Previewを参照。
- B1: 同経路、content_factsのみ固定文へ差替(下記)。art=Part1。
- B2: er070統一Prompt(Z_ROLE_TEMPLATE)に comment_1=同TakeのB1生成物、comment_2=現行Std Comment2(er074条件Aと同じ組立でC1のみ差替)。ctx=std全文。
- lint: `er062_family_z_structure_01.lint_support_text(text,"ja","melos")`を全12生成に適用・記録のみ(NGでも再生成しない)。Comment生成のみ、Production既存の`check_a2_comment_quality`(40〜170字・禁止語句)内部retry(max_retries=1)が働く(Production経路温存)。

## A2追加ブロック(art末尾へ追加、role本文・content_facts不変)
```
【直前に流れるPreview(すでにリスナーが聞いた内容)】
{A1のPreview全文}

【Previewとの役割分担】Previewで述べた事実・状況を説明し直さない。Previewにない背景・理由・条件(なぜその状況になったか、どんな約束や条件があるか等)のうち、これから聞く英文の理解に必要なものを補足する。単なる言い換えや、説明不足にならないようにする。最後は、これから流れる英文へ自然につなぐ。
```
## B1 content_facts固定文
```
これから聞く英文(下の【これから聞く部分】)に実際に書かれている事実のみを使う。Advanced版のComment 1と同じ性格にする: 物語の前提を長々と説明せず、聞くときに注目する具体的な点(誰が・何を・どんな約束や条件か)を、1〜2文の短い聴取ガイドとして示す。先の展開・結末は述べない。抽象的な教訓・評論調にしない。Standardの学習者が分かる平易な日本語にし、理解に必要な前提(人物関係・置かれた状況)は最小限で含める。
```
## role矛盾の報告(固定文のまま実施)
Production Std Comment1 role(`FAMILY_C_A2_COMMENT_ROLE_JA_1`)は「状況説明に徹し、2〜3文・80〜110字程度」。Advanced COMMENT_1_ROLE(`b1s.COMMENT_1_ROLE`)は「注目点を示す原則1文の非常に短いListening Focus、答え・結論を先に言わない」。
B1固定文は「1〜2文の短い聴取ガイド」であり、role本文の「2〜3文・80〜110字」「状況説明に徹する」と部分的に矛盾する(role本文は変更しない指示のため、LLMがどちらを優先するかはTake結果に依存)。

## 費用見積(生成前)
単価 input $0.10/output $0.50 per 1M(er006_model_routing_pricing_coverage_test_01.py L50-52)、USD/JPY=160。
er074実績: 12生成 合計JPY 1.0114(平均 0.0843/生成)。同方式で12生成は約 JPY 1.01。
保守的prompt長ベース上限見積(出力3000tok想定): 名目12生成 JPY 3.414、Comment内部retry最悪(Comment 6件→最大12呼出)含む JPY 5.043。上限JPY20に対し十分小さい。
各Prompt別保守見積(JPY/回): {"A1": 0.2956, "A2": 0.2723, "B1": 0.2707, "B2": 0.2993}
