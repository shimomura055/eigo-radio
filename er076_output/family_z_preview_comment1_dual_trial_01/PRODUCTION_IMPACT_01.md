# PRODUCTION_IMPACT_01: A/B方式のProduction影響調査(read-only、Production無変更)

管理ID: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01。ユーザー指示§8の8項目 + 技術リスク・QCD。いずれもTrialであり、Production採用は未承認。

## 1. 現行のPreview・Comment 1生成順序
- Std (`er062_family_z_writer_01.py::run_support_std` L844-890): Comment1→2→3を順に生成(L855、`generate_with_lint`、lint NG→retry1→`FamilyZLintStop`)し、その後にPreviewを生成(L878-890)。Previewは`er026.build_family_z_preview_prompt()`(`_FAMILY_Z_PREVIEW_ROLE_JA`、er026 L468/479)に「【重複回避】直前に流れるComment 1…」ブロックを足してC1だけを参照。
- Adv (`run_support_adv` L893-928): Comment1/2/3→Previewの順。PreviewはC1・C2を`b1s.PREVIEW_ROLE.format(comment_1,comment_2)`で参照。
- 聴取順(Preview→Comment 1→…)と生成順(Comment 1→Preview)は既に別。**現行の依存方向はTrial Bと同じ(Comment 1先行→Preview)**。

## 2. Advanced / Standard の Comment 1 Prompt・役割差分
| | Std | Adv |
|---|---|---|
| role | `fam_c.FAMILY_C_A2_COMMENT_ROLE_JA_1`(er013 L391): 「状況説明に徹する、雰囲気作りの声かけではない」「2〜3文・80〜110字」「結末・最終選択に触れない」+禁止語句(聴取指示) | `b1s.COMMENT_1_ROLE`(er003_v1_b1_scaffold_01_generate.py L146): Listening Focus、「次に何を聞けばよいか注目点を示す」「原則1文の非常に短い」「答え・結論を先に言わない」 |
| 入力 | art=`【これから聞く部分】\n{Part1}`、content_facts固定文(er062 L862-865) | ctx=`【本文(これから聞く部分)】\n{Part1}`+NOT_NEWS_NOTE |
| 性格 | 前提・状況の要約(情報提供型) | 注目点提示(聴取ガイド型) |
| lint | `lint_support_text(…,"ja")`(聴取指示も検査) | `lint_support_text(…,"en")`(聴取指示は検査しない) |
→ Trial Bで「content_factsだけ差替え」ではAdv的な注目点型にならなかった(role本文が優先)。Adv的Comment 1をStdで再現するには、Std Comment 1の**role本文の新設/差替**(新しいPrompt仕様)が必要で、`FAMILY_C_A2_COMMENT_ROLE_JA_1`はFamily C共通定数のためFamily Z専用roleの新設が前提(共通定数の変更はFamily C/Xへ波及)。

## 3. A方式(Preview先行)のPreview先行依存
- Preview生成をComment生成より前へ移す。Preview roleは「Commentを参照しない」版が必要(Trialはer074条件E=統一Prompt[er070 Z_ROLE_TEMPLATE]からComment参照部分を除去した版)。**現行のProduction Preview role(`_FAMILY_Z_PREVIEW_ROLE_JA`)ではなく、E方式のrole(新Prompt)がProduction化対象**になり、OPEN-338/UDR #48のP1-P3(Preview構成指針・Family X共通仕様に触れる可能性)と同じ論点に接続する。
- Comment 1は生成済みPreviewを参照(art末尾にブロック追加。`generate_family_c_a2_comment`の既存引数`extra_instructions`またはart連結で、fam_c変更なしで実装可能)。Comment 2/3はPreviewに依存せず現行のまま。
- 実装差分箇所(想定): `run_support_std` L855-890の順序入替(Preview→Comment1)、新Preview role定数(er026またはer062に新設)、A2ブロック追加(L861付近のart組立)、`prior`分岐(下記6)。Adv側は無変更。

## 4. B方式(Comment 1先行)のComment 1先行依存
- Preview生成がComment 1に依存する点は現行と同一(L878-890)。Trial Bで必要なのは(a)Comment 1のrole/content_facts差替(上記2)、(b)Preview roleをer070統一Prompt(Z_ROLE_TEMPLATE、C1・C2両方参照)へ差替(現行Production roleはC1のみ参照)。(b)はOPEN-338のFamily X準拠Preview Prompt案(未承認)と同一。
- 実装差分箇所(想定): `run_support_std` L862-865(content_facts差替/role新設)、L878-884(Preview role差替、C2も渡すならC2生成後にPreviewを移動)。

## 5. retry / fallback
- `generate_with_lint`(L804): Comment・PreviewともにlintNG→retry1→`FamilyZLintStop`。
  - A方式: A1(Preview)がlint NGでretry後もNG→Stop(Comment 1未着手で止まるため無駄な呼出は無い)。A2(Comment 1)のlint/品質NGはfam_c内部retry(`max_retries=1`)+外側lint retryで最大4呼出。
  - B方式: 現行と同じ。今回のB2 Take2のように`LISTEN_INSTRUCTION`でNGになる確率が無視できない(1/3 take)ので、実運用ではretry消費→FamilyZLintStop率が上がる懸念(Previewが「お聞きください」型に寄りやすい)。
- 既存のfallback・Gate(Audio Validation/Local Rewrite等)は音声段であり、Preview/Comment生成順序の変更は直接触れない。上限回数・安全装置の回避は不要。

## 6. prior再利用 / regeneration
- 現行: `--regenerate-stage support_a2`時、`prior`でComment1/2とPreviewを再利用し、Comment3のみ再生成(L856-858, L885-887、er026 L1126-1136)。
- A方式: Previewを変えるとComment 1が整合しなくなる→「Preview再生成時はComment 1も再生成」の連動規則が必要。priorにPreviewだけ再利用してComment 1を再生成する、またはその逆、を許さない整合チェックが必要(新規ロジック)。
- B方式: Comment 1を変えるとPreviewを再生成要(現行は暗黙にこの規則=priorで両方再利用、片方のみ再生成は未想定)。同様の整合チェックが必要だが、依存方向は現行どおりなので追加ロジックは小さい。
- どちらも、`prior`再利用の既存テスト(`er062_family_z_writer_01_test_01.py::test_std_comment3_receives_only_front_part_and_prior_reused` L385)の呼出順序の想定変更が必要。

## 7. Family Xの共通処理への影響
- Family X Std/Previewの正本は`er003_v1_iran01_a2_generate.py`(`PREVIEW_ROLE` L174、生成L340-350: Comment 1/2→Preview)。A/Bとも**Family Z専用関数(`run_support_std`)内の変更で完結でき、`a2gen`・`fam_c`・Family Xの経路は変更不要**(Trialもこれらを読取のみで実施)。
- ただし(i)Z専用Comment 1 roleを`fam_c.FAMILY_C_A2_COMMENT_ROLE_JA_1`の変更で実装すると、Family C共通のため波及する(禁止、Z専用定数を新設すること)。(ii)Preview roleをFamily X `PREVIEW_ROLE`準拠へ寄せる案(OPEN-338)はFamily X側の共通仕様変更の議論と接続する。

## 8. 旧Phase 1経路のDangling Reference
- `er026_family_z_fiction_production_runner_01.py::run_text_stage`(L619、CLI `--stage text`のlegacy経路、L1669)は、Preview(`generate_family_z_preview` L502)→Comment 1(`generate_family_z_comment_1` L560、Dionysius/Selinuntius等のcontent_facts固定)を**互いに参照せず独立**に生成(L679-680)。新E2E stage経路(`stage_support`→`run_support_std`)は使わない。
- A/B採用してもlegacy経路は変わらず、legacyのPreview/Comment 1が新方式と食い違うまま残る(順序・参照関係が異なる、固有名詞入りcontent_facts)。「Phase 1互換」として残置か、廃止/注記かの判断が必要(コード変更はしていない)。
- 新規ファイルの参照: 本Trialの成果物(`er076_*`)は新規で、SSOT追記でも存在するpathのみを記載(Dangling Reference確認は`state_guard_01.json`とSSOT追記時に実施)。`er062`/`er026`がimportする`er026.build_family_z_preview_prompt`(L479)は現行Production役割のため、Preview role差替時に本関数のみ置換するか新関数を作るかの判断が必要。

## 9. 必要なValidator・Regressionの変更点(想定、未実装)
- Validator: 既存の`lint_support_text`(禁止語句/聴取指示/ネタバレ)は流用可能。新Gateは作らない。意味重複は機械判定できず(4-gram補助は判定ではない)、現行にも重複Validatorは無い。
- Regression追加候補: (A) 生成順(Previewが先、Commentは同一Preview全文をartに含む、C2/C3はPreview非依存)をmockで検証、(B) B用content_facts/roleの注入確認、(共通) prior再利用時の整合(片方のみ再生成の拒否/連動)、legacy `run_text_stage`が影響を受けないこと。既存`er062*_test*.py`(64件)・`er026_family_z_fiction*_test*.py`(21件)は現状PASS(本Trial時点)で、順序入替後は`run_support_std`呼出順を想定するテストの更新が必要。

## 10. 技術リスク・QCD
| | A方式 | B方式(現行の依存方向と同じ) |
|---|---|---|
| 変更量(目安) | 中: `run_support_std`の順序入替+新Preview role+A2ブロック+prior整合(約60〜100行+test約5件) | 小〜中: Comment 1 role/content_facts差替+Preview role差替(約30〜60行+test約3件)。ただしAdv型Comment 1を実現するにはZ専用role新設(新Prompt仕様)が別途必要 |
| 追加API呼出 | 0(生成数は同じ。lint retry時のみ増) | 0 |
| Latency | 変化ほぼなし(C2/C3はPreview非依存だが現行も逐次) | 変化なし |
| 主リスク | Preview roleが現行から変わる(OPEN-338/UDR #48と同じ論点)。Comment 1が前提再話になり聴取ガイドにならない。時系列(Previewが後半場面を述べ、Comment 1が冒頭を再話)。Preview/Comment連動のprior整合 | Previewが抽象化(今回の3/3 take)。Comment 1をAdv型にするには新role仕様が必須。Preview lint NG(`LISTEN_INSTRUCTION`)でretry→Stop増の懸念 |
| 品質(Trial所見) | Preview具体性良好(3/3)、事実誤り0、lint OK 6/6 | Preview抽象的(3/3)、lint NG 1/6 |
| 必須Gate | 新しい処理フロー設計(Opus独立技術レビュー条件A)+ユーザー`APPROVED_FOR_PRODUCTION` | 同左(Comment 1 role新設の場合は新Prompt仕様のUSER_DECISION) |
