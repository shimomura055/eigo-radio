# OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 設計 (Phase A / 2026-10-07 / ¥0)
Trial専用(DEV)。Production(`er019_family_x_storyline_b3_fact_selection_01.py`)は無変更。根拠仮説: `docs/pm/b3_brief_structure_hypothesis_01.md`(H1主体・対象省略、H2Storyline連結、H3未提示不記載)。指示文の正本は `er052_open233_b3_variant_dev_01.py`(BLOCK_*。ここは要旨+全文の複製を避けるが、全文はpromptsに出力済み)。

## 1 条件と指示文(全文は `er052_output/open233_b3_trial_01/prompts/<V>_<slug>.txt` 末尾、コード BLOCK_V1/V2/V5_EXTRA/V6)
| 条件 | 内容 | 現行「簡潔に」(指示5の括弧書き) |
|---|---|---|
| V0 | 現行(対照、無変更) | そのまま |
| V1 | 【主体・対象の保持】Selected Factsで台帳文の誰が/誰に・何に/率・数値の掛かる先/方向語を省略・再構成・置換しない。台帳で未明示の主体・対象は補わず未明示のまま | 残す。ただし「この指示は『簡潔に』より優先」と明記 |
| V2 | 【単一因果】Storylineは原因と結果が一つにつながる1文。別factの限定語・条件・範囲を1文内で連結しない。関係づけは各factを分けて書く | 残す+優先明記 |
| V3 | V1+V2の連結 | 残す+優先明記 |
| V5 | V3+(a)各fact `- [fact_id] 「台帳文逐語」 役割: …`(b)主要fact5件以上(目安3〜5件を不適用、fact_testsは正直に記録、不足時のみ追加select、6件以上のrecheck_noteは短く理由)(c)台帳の未提示/不明/確認できない/書かない事項はSelected Facts末尾に「〜は示されていない」 | **置換**: 「必要最小限のFactを簡潔にまとめた文章」→「…Factを、台帳文に忠実に整理した文章」(忠実最優先と明記) |
| V6 | 【最大簡潔】各fact1文以内、細部省略・言い換え・統合自由、忠実さより簡潔さ優先(逆方向対照) | **置換**: →「…Factを、要点のみ短く言い換えてまとめた文章」+強化ブロック |
固有名・個別事例は一切含めない(テスト `test_forbidden_words` で検査)。

## 2 差し込み位置
userプロンプト(`build_user_prompt`出力)の末尾(【重要】段の後)に指示ブロックを追記。V5/V6のみ指示5内の1句を置換(出現1回を厳密検査)。developer(system)メッセージ・JSON schema・Test定義・retry note(`_call_once`が末尾へ追加)は変更しない。理由: 既存patched_b3(nb)と同方式で差分最小、schema整合(fact_tests全id必須)を維持。

## 3 brief書式の期待
Storyline行: `build_selected_brief_markdown`が「## Storyline」に別掲(LLMがfact本文先頭へ同文を含めても既存dedupがある)。V2/V3/V5は単一因果1文。Selected Facts: V0/V6=LLM任せ(散文or箇条書き)、V1/V2/V3=台帳文寄りの箇条書き化を期待、V5=`[fact_id]「逐語」役割:`形式+末尾「〜は示されていない」。`parse_brief_md`互換(「## Storyline」「## Selected Facts」維持)。

## 4 副作用の見込み
V1/V3: brief肥大・読みにくさ。V2: Storyline平板化。V5: fact数増(≥5)でWriterが羅列的になる/逐語引用で台帳の条件・scope文が混入(H4の転記増による軽微増の恐れ)/未提示事項の明記が「示されていない」自体を記事に出す。V6: 主体・対象の欠落が増え重大が増える見込み(逆方向対照)。B3の採用数ルール(6件以上でrecheck_note、soft warning)と衝突し得るがV5は(b)で整合を取った。

## 5 読み方(事前固定)
指標=記事当たりの重大件数・fact誤り軽微件数(EN)、評価基準は既存MXと同一(単独判定台帳)。忠実方向なら誤り量が **V6 > V0 > V1/V2 > V3 > V5** の順に減る。この順に単調でなければ「指示追加の効果は不明/逆効果」。N小(各セル4本、条件当たり12本)のため結論でなく仮説判定。brief副指標: 主体・対象保持率(手作業)、fact数、文字数。

## 6 Opus条件Aレビュー論点(5点)
1. 追記位置(user末尾)とV5/V6の句置換が、B3の4テスト・採用数ルールと内部矛盾しないか(V5(b)の「テストは正直、decisionのみ補足」の整合)。
2. V1〜V3で「簡潔に」を残し優先文で上書きする方式は、置換方式より指示衝突が残らないか。
3. V6を逆方向対照に含める意義(読み方の単調性検定)と、V4欠番(未実施)の扱い。
4. V5の逐語引用+役割形式がH4(転記増による軽微増)を誘発し、仮説検証を汚染しないか。
5. 標本設計(条件×テーマ×B3 2回×Writer 2本、Checkerなし)でB3回差とWriter回差を分離できるか、分散分析の読み方。

## 7 Trial手順・費用見積
手順: B3 36call(6条件×3テーマ×2)→brief目視確認(形式崩れ=parse不能は停止)→Writer72本(各brief×2、既存DEV runner `--brief-md` phase1→phase2 `--no-checker`)→EN。詳細 `er052_output/open233_b3_trial_01/PLAN.md`。
単価(`er052_output/open233_note_transfer_matrix_01/cost.json`実績): B3 brief_gen ¥3.11/3call≈¥1.0/call(V5は出力増で≈¥1.5想定)。JA工程(ja_original〜ja_r2_check_retry合計¥185.47/36run≈¥5.15/run)、EN(advanced ¥66.38/36≈¥1.84/run)。MX全体 runs_total ¥265.36/36run=¥7.37/run(再実行込み)。
| 工程 | 数量 | 見込み |
|---|---|---|
| B3 | 36 | ≈¥40 |
| JA工程 | 72 | ≈¥371 |
| EN | 72 | ≈¥133 |
| 合計(再実行なし) | | **≈¥544**、再実行最大8枠(約¥7.4×8=¥59)込みで≈¥600 |
**¥500超見込み→STOP条件に該当。Fableへ判断依頼(案: Writer 1本/brief=36記事で≈¥40+¥265=≈¥305)。**

## 8 Dangling Reference Check
実在確認済: `er019_family_x_storyline_b3_fact_selection_01.py`(build_user_prompt L148、指示5 L68)、`er052_open233_polysemy_nb_dev_01.py`(patched_b3 L85、--brief-md/--no-checker、out_dir規約: runs_root/<slug>/<variant=nb>/…を満たす `runs/<slug>/nb/<V>/b<i>/w<j>`)、台帳 `er052_output/open233_polysemy_trial_02/ledgers/{meta,hormuz,space_weapons}/control/research_ledger/verified_fact_ledger.txt`+`topic.txt`、`er052_output/open233_note_transfer_matrix_01/cost.json`、`docs/pm/b3_brief_structure_hypothesis_01.md`。新規: `er052_open233_b3_variant_dev_01.py`、`er052_output/open233_b3_trial_01/{tools/run_b3_variant.py,tests/test_b3_variant_dev_01.py,prompts/*.txt(18),PLAN.md}`。
注意: hormuz topic.txtは「代替topic」(元theme未記録)。全条件共通のため比較には影響しないが記録。
