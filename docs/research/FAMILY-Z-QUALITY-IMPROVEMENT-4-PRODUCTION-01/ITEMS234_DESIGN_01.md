# ITEMS234_DESIGN_01: 改善項目②③④ 現行経路調査・差分設計・テスト設計・再生成計画・費用見積

管理ID: FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_02 / 日付: 2026-10-19(JST) / 性質: Phase 1 read-only調査+設計文書(コード変更0・有料API呼出0・JPY0・Production変更なし)
到達上限Status: `ITEMS234_DESIGN_READY_PENDING_OPUS_A`(②③は新しい処理フロー設計に当たるためOpus条件Aレビュー後に実装)
根拠データ: run_e2e_03 (`er026_output/family_z_production_e2e_01/melos/run_e2e_03/`)の実測。ユーザー指示原文: `docs/pm/delegation_log/2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md`(委任_01が保存済み)。親=OPEN-419、REGISTER #115(委任_01が起票・登録済み、参照のみ)。

## 0. 結論(1画面)

| 項目 | 結論 | 変更規模 | 再生成対象(メロス) | Phase 3費用(期待/上限) |
|---|---|---|---|---|
| ② Std Preview/Comment=Adv方式の日本語適用 | `run_support_std`を`run_support_adv`と同型へ置換。役割文はAdvのb1s役割の日本語対応版である`a2gen.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLE`を**無改変流用**(Advが`b1s.*_ROLE`を無改変流用しているのと同形、新規Prompt作成なし)。**lint(聴取指示検査)がAdv型Comment 1を必ず弾く**(Trial実績3/3 NG)ため、緩和の扱いが唯一の判断論点 | er062 1関数+新定数1個+stage_support2箇所のsha、test約10件 | Std Preview+Comment1〜3(LLM 4呼出)→S3 TTS 4clip | LLM JPY約0.4/0.8、TTS+ASR約2.3/6.8 |
| ③ Std Dialogue=Adv同一Style+後処理6%減速 | `er063`の2箇所(`style_text_for` L702-706と`dialogue()` L790-797)でStd専用`A2_ENGLISH_STYLE_PREFIX_SLOWER`を渡さないだけ(Advと同じ呼出+既存の6%減速外側ループは温存)。Voice割当・`FAMILY_Z_ROLE_STYLE_VERSION`は不変。reuse_keyのstyle shaが変わるため**Std Dialogue 10clipだけが自動で再生成**される | 実装コード数行+定数表記1+test約5件更新 | Std Dialogue 10clip(王のセリフ含む) | JPY約4.6/12.5 |
| ④ 本文語数400±70 | 現行は既に**WARNのみ・再生成/STOPなし**。変更は定数(350→400、280-420→330-470)・Prompt文言5箇所・test更新・SSOT文言。ハードキャップ/自動再生成/STOPの撤去は**不要**(存在しない)。メロス本文はwriter stageのreuse判定が`prev_sha`(親出力sha)基準でPrompt文面に依存しないため**再生成されない**(Std 408/Adv 387を本調査で実測確認、330〜470内) | 定数3+Prompt文言5+test約6件 | なし(本文reuse) | JPY0 |

Phase 3(再生成)総費用(①を除く): **期待 約JPY7.3(②LLM0.4+②TTS2.3+③4.6)、上限見込み約JPY20**(全clipが通算3回まで再試行した最悪ケース)。run_e2e_03 JPY36.38の約20%。日次1,000円枠・本管理IDの承認枠内。
判断候補(詳細は§8): (D-1)Std Preview/Comment のlint `LISTEN_INSTRUCTION`の扱い(= QA blocking条件の変更に当たるためFable判定)。

## 1. 確認した現行事実(ファイル:行)

### 1-1 Advanced正式経路(②の移植元)
- `er062_family_z_writer_01.py:893-927 run_support_adv`: モデル=`B1_SUPPORT`(`gpt-6-luna`、routing.require_model)。生成順=Comment1→Comment2→Comment3→**Preview(最後)**。lint=`lint_support_text(...,"en")`(`er062_family_z_structure_01.py:658-687`: 聴取指示は検査しない。news語/IOL/Point/構造ラベル/ネタバレ/名前/言語のみ)。
- 入力構成(L900-905): C1=`【本文(これから聞く部分)】Part1`+NOT_NEWS_NOTE(L226)/C2=`【すでに聞いた本文(前半)】Part1`+`【これから聞く本文(後半)】Part2`/C3=Part1+Part2+`limit_comment3_part(Part3)`(Part3先頭約25%・最低2段落・到着/結末マーカー以降除外、L816-833)。役割: C1=`b1s.COMMENT_1_ROLE`、C2=C3=`b1s.COMMENT_2_ROLE`(L906)。Comment4・`COMMENT_3_ROLE`(Point橋渡し)は呼ばない。
- Preview(L918-924): `b1s.PREVIEW_ROLE.format(comment_1=,comment_2=)`+コンテキスト`【本文】`物語全文+NOT_NEWS_NOTE。
- Prompt全文の所在(`er003_v1_b1_scaffold_01_generate.py`): `SUPPORT_ENGLISH_PRINCIPLE` L119、`SUPPORT_PROHIBITIONS` L121-130(本文にない新Fact/因果/過度な一般化/推測/**Point One/Twoの答え先出し禁止**/本文の長いparaphrase禁止/Support英語を学習課題にしない/一度に複数論点禁止)、`build_support_prompt` L133-142、`COMMENT_1_ROLE` L146-154、`COMMENT_2_ROLE` L156-165、`PREVIEW_ROLE` L193-212(下記)。
- **構成・役割・情報開示方針の抽出**:

| 要素 | C1(Listening Focus) | C2/C3(Mid-story Recovery+Next Question) | Preview |
|---|---|---|---|
| 役割 | 次に何を聞けばよいか**注目点**を示す | 前半の核心を**1点だけ**短く回収し、後半で何を聞くかの**問い**を提示 | theme/problem/value/questionを短く提示し関心を引く |
| 分量 | 原則**1文**・非常に短い | **1〜2文**・長いsummaryにしない | **2〜3文**程度 |
| 情報開示方針 | 答え・結論を先に言わない | 本文を言い換えて全部説明しない | 答え/重要数字/結論/**turning pointを先出ししない**、**後続Comment1・2と重複させない**(Comment1・2の本文を役割文に埋込) |
| 入力 | これから聞く部分のみ | 聞き終えた部分+これから聞く部分 | 全文+C1+C2 |
| 共通 | 構造ラベル(Part n/Full Story)を出力しない、易しい英語(SUPPORT_ENGLISH_PRINCIPLE)、禁止事項(SUPPORT_PROHIBITIONS) | | |

- 実出力(run_e2e_03 `b1b/support`): C1=「Listen for what Melos promises before he leaves.」(1文)/C2=「Melos promised to return, and his friend chose to trust him. What will happen as Melos makes his way back to the city?」/Preview=「This story follows a young shepherd who speaks out against a ruler and is sentenced to die. As he faces a choice … what will guide him through this moment of great pressure?」(出来事の先取りなし・問いで終わる)。

### 1-2 Standard現行経路(②の移植先)
- `er062:844-890 run_support_std`: Comment1→2→3→Preview。C1〜3は`fam_c.generate_family_c_a2_comment`(`er013_family_c_production_01.py:428-505`)経由。役割文=`FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3`(L391-419)=「**状況説明に徹する**・2〜3文・80〜110字・content_factsのうち必要なもの」+`_BANNED_PHRASES_INSTRUCTION`(L379-385)。content_factsはrunner側で「これから聞く英文に実際に書かれている事実のみ。場所・状況、人物関係、場面の変化、次の行動、選択や対立点…」(`er062:860-862`)。入力は`【これから聞く部分】Part n`+(n>1なら`【すでに聞いた部分】Part n-1`)。Comment3はPart3先頭約25%に限定。
- Preview(L878-890): role=`er026_family_z_fiction_production_runner_01.py:468-477 _FAMILY_Z_PREVIEW_ROLE_JA`(「状況設定(誰が・どんな状況か)を2〜3文・80〜110字」「結末や山場に触れない」+Family C禁止語句)+`【重複回避】直前のComment 1`のみ。入力は物語全文。**Comment 2は重複回避に含まれない**。
- lint=`lint_support_text(...,"ja")`: 聴取指示検査あり(`fam_c`禁止語句+`_LINT_LISTEN_JA` L642「聞いてみ|聞いてください|お聞き|聞き取|聴いて|耳を|注目して|注意して聞」)。NG→retry1→`FamilyZLintStop`(`generate_with_lint` L804-813)=量産STOP。
- 現行実出力(run_e2e_03 `a2/support`、本調査で読取): Preview=「結婚式を終えたメロスは、三日目の夜明け前に町へ戻り始めます。帰り道には、橋のない川と、道をふさぐ男たちがいます。川は雨で茶色くなり…」(Part2以降の障害を先取り=ユーザー指摘どおり)/C1=メロスの抗議・死刑・猶予・身代わりを全説明/C2=川・三人から逃げた・足が血だらけ・選択、「戻らなければ友人が…」/C3=友人の手を思い出す→岩から水を飲んで立ち上がる(あらすじ化)。

### 1-3 Adv方式との差分表(②)

| 項目 | Adv(正) | Std現行 | Std新(提案) |
|---|---|---|---|
| 生成順 | C1→C2→C3→Preview | 同 | 同(不変) |
| C1役割 | Listening Focus(注目点1文) | 状況説明2〜3文80〜110字 | `a2gen.COMMENT_1_ROLE`(=b1s C1の日本語出力版、Trial B'実績あり) |
| C2/C3役割 | Mid-story Recovery+Next Question(1〜2文) | 状況整理2〜3文 | `a2gen.COMMENT_2_ROLE`(C3も同じ、Advと同形) |
| Preview役割 | theme/problem/value/question 2〜3文、ターニングポイント非開示 | 状況設定2〜3文、結末非開示 | `a2gen.PREVIEW_ROLE`(2文程度80〜110字、4要素を律儀に並べない。注: question独立文は任意)※§2-3 P-B代案あり |
| Previewの重複回避入力 | C1+C2本文 | C1のみ | C1+C2(Adv同形) |
| C1入力 | これから聞く部分のみ | Part1(+なし) | Part1のみ |
| C2入力 | Part1+Part2 | Part2(+Part1参考) | Part1+Part2 |
| C3入力 | Part1+Part2+Part3先頭25% | Part3先頭25%(+Part2) | Part1+Part2+`limit_comment3_part(Part3)` |
| 平易さ | `SUPPORT_ENGLISH_PRINCIPLE` | `SUPPORT_JA_PRINCIPLE`(`a2gen.build_support_prompt`が自動付与) | 同左(Std固有として残す) |
| 禁止事項 | `SUPPORT_PROHIBITIONS`(Point先出し等) | `a2gen.SUPPORT_PROHIBITIONS`(同等) | 同左 |
| 文脈注記 | NOT_NEWS_NOTE | なし(fam_c) | NOT_NEWS_NOTE(Advと同じ) |
| lint | en(聴取指示検査なし) | ja(聴取指示検査あり、NGでSTOP) | **要判断(§2-4)** |
| 呼出関数 | `b1s.run_support_text` | `a2gen.run_support_text`+`fam_c.generate_family_c_a2_comment` | `a2gen.run_support_text`直接(Advと同形、fam_c経路は迂回) |

## 2. ②Standard Preview/Comment=Adv方式の日本語適用

### 2-1 現行(§1-2のとおり)。
### 2-2 参考: 既に取得済みのTrial実績(新規Trial不要の根拠)
`er076_output/family_z_preview_comment1_dual_trial_01/PRODUCTION_IMPACT_02.md`のTrial B'(=Adv型 `a2gen.COMMENT_1_ROLE`無改変+Part1のみ入力+NOT_NEWS_NOTE → 現行Production Std Preview)の実測: **現行lintで3/3 NG**(例外設計なしでは採用不能)、Comment1が36〜41字(`check_a2_comment_quality`下限40字を下回る)、注目点の事実ずれ2/3。**今回の指示はA/B Trialの再実施ではなく、Advの日本語適用の実装**であるため、追加Trial・有料実行は設計に含めない(指示「追加Trial不要」は2026-10-17決定。本件は2026-10-19指示の実装)。

### 2-3 設計
**P-A(推奨)**: `run_support_std`を以下に置換。
1. 新関数`run_support_std`の本体を`run_support_adv`と同形に: `fn = ja_support_fn or a2gen.run_support_text`、`model=routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)`(不変)、`ctxs`はAdv同形(`NOT_NEWS_NOTE`付、Part1 / Part1+Part2 / Part1+Part2+`limit_comment3_part`)、`roles={1:a2gen.COMMENT_1_ROLE, 2:a2gen.COMMENT_2_ROLE, 3:a2gen.COMMENT_2_ROLE}`、Preview role=`a2gen.PREVIEW_ROLE.format(comment_1=,comment_2=)`、ctx=`【本文】`全文+NOT_NEWS_NOTE。`fam_c.generate_family_c_a2_comment`と`er026.build_family_z_preview_prompt()`は呼ばない。
2. 根拠: a2genの3役割はb1sの3役割の日本語出力版で、役割・分量(1文/1〜2文)・開示方針が同一(`er003_v1_iran01_a2_generate.py:127-206`、b1s L146-212と対照済み)。Family X Standard(日本語)のProduction既存資産で、新規Prompt文を作らない(ユーザー指示「別の独自方式を含まない」に最も忠実)。2026-10-13 ユーザー判断「Family Z Std PreviewはFamily X Standard `PREVIEW_ROLE`を基準」(OPEN-338記述、`OPEN_ITEMS.md:841`)とも整合。
3. Std固有に残す要素: 出力言語=日本語(`a2gen.build_support_prompt`の`SUPPORT_JA_PRINCIPLE`=平易さ)、`story_key`別名・ネタバレ辞書lint(`spoiler_ja`)、S3 TTS(不変)。
4. 差分: a2gen.PREVIEW_ROLEはAdvのb1s.PREVIEW_ROLEより短く(2文・80〜110字、question独立文は任意)、4要素のうちquestionを「無理に立てない」。Advは「2〜3文・question含む」。**P-B(代案)**=b1s.PREVIEW_ROLEの構成(theme/problem/value/question・2〜3文・同じ「避ける」リスト)をZ専用に日本語化した新定数を`er062`内に作る。P-Bは新Prompt文の作成であり「独自方式」の疑義を生むため非推奨。Opus観点①に含める。

**Comment/Preview間の重複・先取り確認(新Gateではない・WARN記録のみ)**: `run_support_std`の戻り値に`overlap_notes`(list)を追加記録。(a)Preview×C1×C2の相互4-gram(漢字かな連続4字以上)一致数、(b)本文の「結末語」(`COMMENT3_ENDING_MARKER_RE`の語、lint `spoiler_ja`辞書)の出現、(c)Preview/C1/C2にPart3固有語(Part3にのみ現れる名詞)が出ていないか。結果は`support.json`の`overlap_notes`とconsole WARNに出すのみで**raiseしない・retryしない**(新Gate化しない。Advには同等checkが無いためStdのみ記録=最小)。判定は人手試聴/Fableが行う。

### 2-4 lint(聴取指示検査)の扱い = **判断候補D-1**
- 事実: ユーザー指示「リスナーが何に注目して聴けばよいかを示し」とAdv方式C1(Listening Focus)は、Std現行lintの`LISTEN_INSTRUCTION`(「注目して」「耳を」「聞き取」等)と構造的に衝突する。緩和しないと、Trial実績どおりC1がlint NG→retry1→`FamilyZLintStop`=**量産STOP**が高頻度で発生する(Trial B' 3/3)。
- 選択肢: (L-1・推奨)Std JAのlintをAdv(en)と同一にし、`LISTEN_INSTRUCTION`は**blockingをやめWARN記録のみ**(`attempts[*].violations`ではなく`overlap_notes`/`lint_warn`へ)。構造語(news/IOL/Point/構造ラベル)、ネタバレ辞書、禁止名、言語は従来どおりblocking。Advのlintと完全に同じ思想(Advは聴取指示を検査しない)になり、「Adv方式の日本語適用」に最も整合。(L-2)`_LINT_LISTEN_JA`から「注目して|注意して聞|聞き取|耳を」等だけを除外し、Family C空疎誘導語(「聞いてみましょう」「耳を傾け」「耳を澄ま」「どうなるでしょう」)はblocking維持。ただし`どうなるでしょう`はAdv C2の"What will happen…?"の日本語自然訳と衝突し得る。(L-3)lint不変+役割文のコンテキストに「『注目して』等を使わない表現で」を追加。ただしこれは役割文改変(「別方式」疑義)で、かつ高確率でSTOPが残る(Trial 3/3)。
- 分類: 候補**B(承認範囲内で自己解決可)寄りだが、lintはQA blocking条件であり変更は`CLAUDE.md`共通Charter「QA blocking条件の変更」に隣接するため、Fable判定を要請**。根拠: 2026-10-19ユーザー指示②が結果的にC1の役割(注目点提示)を指定しており、その役割とblocking lintは共存できない。新Gate新設ではなく**既存blocking条件1つのWARN化**(Std JAのみ、Z専用関数`er062_family_z_structure_01.lint_support_text`内、Xは無変更)。

### 2-5 retry/regeneration/resumeへの反映点
1. `run_support_std`は`generate_with_lint`(retry1→STOP)を従来どおり使用(回数・STOP条件は不変、blocking項目のみ§2-4)。
2. `stage_support`(`er026:1112-1145`)の`ensure_stage`入力sha=`_sha(text + file_sha(plan_path))`(L1139)。**方式が変わっても入力shaが同一なので、旧方式のcache(`a2_support.json`)がそのまま`reused`になってしまい、新方式が一切発火しない**。→ Std側のみ`STD_SUPPORT_METHOD_VERSION`(例`z_std_support_adv_ja_v1`)を入力shaに混ぜる(`input_sha = _sha(text + plan_sha + "|" + VERSION)`、Advのshaは不変)。旧cacheの場合は`FamilyZProvenanceMismatchStop`(親sha不一致、`er062:508-510`)=自動再生成しない既存仕様どおり、明示`--regenerate-stage support_a2`が必要。同じ計算が`er062`のCLI経路(L1278)にも存在するため、**共通ヘルパ`support_input_sha(lv, text, plan_sha)`をer062に置き、er026(L1139)とer062 CLI(L1278)の2箇所から呼ぶ**。
3. `prior`(明示再生成時のComment1/2/Preview再利用、`er026:1127-1130`の「委任_08 Comment3のみ再生成」機構)は**旧方式の出力を新方式へ再利用してしまう**。→ `support.json`に`"method": VERSION`を記録し、`prior`は`prior.get("method")==VERSION`のときのみ有効、不一致なら`prior=None`(=全4生成)。`_prev_before_c3_limit.json`退避は継続。Advは`method`キー無し・挙動不変。
4. TTS側のreuse(`er063.generate_or_reuse_z`)はreuse_keyに`canonical_text_sha256`を含むため、**テキストが変わったPreview/Comment 1〜3のS3 clipのみ自動再生成**され、Adv側・Std KP/narration/dialogueは再利用(追加実装不要)。
5. 旧経路の残置: `er026._FAMILY_Z_PREVIEW_ROLE_JA`/`build_family_z_preview_prompt`/`generate_family_z_preview`(`run_text_stage` Phase1互換、L619-)は**E2E正式経路ではない**。trial(er067/er070/er072/er076)と`er070_*_test_01`が参照するため**残置(SUPERSEDEDコメントのみ追記)**。
6. fallback: Support生成にfallback経路は無い(lint STOPのみ)。API失敗は`_support_text`が`FamilyZStop`。

### 2-6 test設計(`er062_family_z_writer_01_test_01.py`中心)
新規(約10件): (1)Std役割=`a2gen.COMMENT_1_ROLE`/`COMMENT_2_ROLE`/`COMMENT_2_ROLE`/`PREVIEW_ROLE`で渡る(AdvのL509-522テストと同形)、(2)C1/C2/C3/Previewの入力構成(Part範囲・NOT_NEWS_NOTE・`limit_comment3_part`)、(3)Previewの役割文にC1・C2本文が入る、(4)新経路は`fam_c.generate_family_c_a2_comment`と`er026.build_family_z_preview_prompt`を呼ばない、(5)lint: 構造語・ネタバレ・禁止名・言語NGはretry1→`FamilyZLintStop`のまま、(6)lint(§2-4 L-1の場合): 「…に注目して聞く」はblockingしない・WARN記録される、(7)`overlap_notes`が記録されraiseしない、(8)入力shaにVERSIONが入りAdvのshaは不変(golden値固定)、(9)`prior`はmethod一致時のみ再利用/不一致は全再生成(旧method priorでC1/C2が再利用されない)、(10)旧cache(VERSIONなし)でresumeすると`FamilyZProvenanceMismatchStop`。更新(約3件): `test_std_comment3_receives_only_front_part_and_prior_reused`(fam_cモック前提→新経路)、`test_std_comment_facts_only_from_target_part`(content_facts前提)、`test_std_preview_has_no_listen_instruction`(L-1採用時はWARN確認へ)。`er070_family_z_std_preview_x_alignment_01_test_01`はtrial固有の現行Production事実確認でrun_support_std呼出を含む→新経路の入出力で通るか確認し必要ならtrial test側を`xfail`でなく**期待値更新**(旧実装の事実確認は意味を失うため)。

### 2-7 メロス再生成計画・費用
手順: 新run dir(例`run_e2e_04`)に`run_e2e_03`の承認済み成果物をコピー(既存の`copy_plan`/Phase3慣行どおり)→`--regenerate-stage support_a2`(明示、自動再生成なし)→Std support 4 LLM呼出(C1,C2,C3,Preview; `gpt-6-luna`)→`tts_a2`でreuse_key不一致の4 clip(preview,comment_1〜3)のみS3 TTS(`gemini-3.8-flash-lite-tts`)+ASR→AUW(生成内統合)→`gate`→`assemble`→`pages`。Adv(`b1b`)・Std本文/KP/narration/dialogueは再利用。
費用(出典実測): LLM support=run_e2e_01 10呼出JPY0.8443/run_e2e_02 9呼出JPY0.9269(`cost_log.jsonl`から`er019_..._runner.compute_cost_jpy_so_far`で再計算、1呼出約JPY0.09〜0.10)→Std 4呼出=約JPY0.4、全4でlint retry1回の最悪0.8。TTS+ASR=run_e2e_03の`tts_a2`のpreview/comment_1〜3の4clip実測**JPY2.2718**(Gemini flash-lite 4呼出+OpenAI ASR 4呼出)、最悪ケース(各3回)約JPY6.8。②合計 期待約2.7/上限約7.6。

## 3. ③Standard Dialogue=Adv同一Style+後処理6%減速

### 3-1 現行(ファイル:行)
| 項目 | Adv | Std(現行) |
|---|---|---|
| Role key | `DIALOGUE_ADV`(`er063:172-177`)、`role_key_for` L497-498 | `DIALOGUE_STD`(L178-182) |
| 生成時Style | `style_prefix_override`を渡さない=`bvoices.generate_voice_body_wide_margin`の既定`p9a.ENGLISH_STYLE_PREFIX`(`er012_b_family_voices_production_01.py:519`)。効果sha `add26d27…`(run_e2e_03 `tts_generation_results.json` b1b) | `n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER`(=`ENGLISH_STYLE_PREFIX`+`A2_SLOWER_PACE_INSTRUCTION`、`er003_v1_n3_01_tts_generate.py:78-84`)を`style_prefix_override`で渡す。sha `d51b9f1f…`(a2) |
| 渡し口 | `dialogue()`(`er063:798`) | `dialogue()` L790-797(`generate_with_a2_slowdown_outer_loop`の`gen_fn`内)と、**reuse_key用の`style_text_for`(L702-706)** |
| Voice割当 | `FAMILY_Z_DIALOGUE_VOICE_*`(L342-348)、話者別 | 同一(不変) |
| model | gemini-2.5-pro-preview-tts | 同一 |
| 後処理6% | なし | `generate_with_a2_slowdown_outer_loop`(`n3_tts.py:406-460`)→`apply_a2_slowdown_postprocess`(L182-)で6%減速+減速後ASR再検証(統一judge J7)、最大3回の通算TTS |
- Dialogue clipが減速検査の対象か: **対象**。`verify_std_english_slowdown`(`er063:1292-1316`)は`_CLIP_ID_RE`に一致するStd英語Story clip(narrator・dialogue、`_cN`含む)全てで`slowdown_applied is True`または`_original.wav`比∈[1.03,1.09]を要求。run_e2e_03のStd Dialogue 10clipは全て`slowdown_applied=True`、`slowdown_ratio`1.0559〜1.0581。
- 実測(run_e2e_03、参考値・基準ではない): Std「Your friend must stay here…」(full_story_part1_c8, Charon) 14語/8.645秒(減速後、ratio1.058)。Adv同clip(Advは本文が異なり12語)5.641秒。
- narrator(PD06+6%減速)は別roleで不変(`NARRATOR_FULL_STORY_STD` L168-172)。生成時減速指示はStd narratorには既に無い(2026-10-17 N01→PD06置換、CURRENT_SPEC:2743相当)ため、今回でStd全体が「生成時減速指示なし+後処理6%」に揃う。

### 3-2 設計(最小変更)
1. `er063:702-706 style_text_for`: `if spec.kind == "dialogue": return None`(a2分岐とn3_tts importを削除)。→ Std/Advとも`None`(=既定Dialogue Style)。**reuse_keyの`style_prefix_sha256`がStd Dialogueだけ`sha(SLOWER)`→`None`に変わる**ため、`FAMILY_Z_ROLE_STYLE_VERSION`を上げなくてもStd Dialogue 10clipだけが自動で再生成される(Adv・narrator・preview等のkeyは不変。version bumpは全clip再生成になるため**行わない**。L36-40のコメント方針と整合)。
2. `er063:790-797 dialogue()`: Std分岐は`n3_tts.generate_with_a2_slowdown_outer_loop(spec.clip_id, text, out_path, lambda max_attempts: bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice, max_attempts=max_attempts))`(`style_prefix_override`引数のみ削除)。外側ループ・減速後再検証・通算3回予算・統一judge・`finalize_a2_slowdown_final_ng`は不変。コメント(L790-792)更新。
3. `FAMILY_Z_ROLE_STYLE["DIALOGUE_STD"]`(L178-182): `style_label`を`"existing_dialogue_style(ENGLISH_STYLE_PREFIX)+post6%"`に、`origin`/`path`文言を更新。`text`はNone(従前どおり)・origin_kind=Z。`assert_style_table_integrity`(L262-)はtext=Noneのroleを検査対象外にするため影響なし。
4. `CROSS_FAMILY_COMMON_STYLE_MAP`(L224-239): `DIALOGUE_STD`はEXCEPTIONのまま(Xと共通Style表の対象外、ユーザー§2B)。理由文言のみ「Adv同一Dialogue Style」に更新。drift test `EXPECTED_EXCEPTION_ROLES`(`er063_family_z_common_style_wiring_01_test_01.py:26`)は不変。
5. `style_record.json`(`expected_style_record`)のDIALOGUE_STD: sha null(従前から)・labelのみ変更。`_effective_style_sha`(L998-1010)はStd Dialogueでも`style_text_for`がNoneになり`p9a.ENGLISH_STYLE_PREFIX`のsha(`add26d27…`)を記録=Advと同値になる(検証に利用)。
6. retry/fallback: 唯一`style_prefix_override`を渡すのは`generate_voice_body_wide_margin` L519のprimary prompt。primary失敗時の`generate_voice_body_minimal_fallback`(L535)はそもそも減速指示を持たないStyleで、overrideの影響を受けない=**retry・fallback・外側ループ・resumeのいずれも新Styleに自動で揃う**(分岐が1箇所に集約されている)。
7. 共有定数`n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER`・`A2_SLOWER_PACE_INSTRUCTION`は**Family A/B/C/X・Voices(`er012_b_family_voices_a2_*`、`er019_family_x_*`ほか約25ファイル)が使用中のため削除しない**(Zの呼出のみ撤去)。

### 3-3 test設計
更新(3件): `er063_family_z_audio_01_test_01.py:604-617 test_std_dialogue_a2_slower_and_postprocess_no_pd8`(`style_prefix_override`がkwargsに無いこと/`A2_SLOWER`文言が渡らないこと/`apply_a2_slowdown_postprocess`が呼ばれ`slowdown_applied`がTrueであること/Voice=Algieba不変)、`er078_asr_unified_wiring_05_test_01.py:269`(`kw == {"max_attempts":3}`)、`er078_asr_unified_wiring_06c_test_01.py:601`(`seen`のstyleが`None`)。`er063_..._test_01.py:100-110`(Dialogueのstyleは`None`)はStdも`None`でPASS(assertを`a2`にも拡張)。新規(約3件): (1)`style_text_for(a2 dialogue) is style_text_for(b1b dialogue) is None`、(2)reuse_key golden: Std Dialogue以外の全roleのreuse_keyが変更前と**完全一致**、Std Dialogueのみ`style_prefix_sha256`が変化、(3)`FAMILY_Z_ROLE_STYLE["DIALOGUE_STD"]["text"] is None`かつラベルに`SLOWER`を含まない+`inspect.getsource(er063)`に`A2_ENGLISH_STYLE_PREFIX_SLOWER`が残っていない(撤去Grep test)。`test_changing_x_default_profile_does_not_change_z_resolution`等のnon-dependence testは不変。

### 3-4 検証計画(Phase 3、新たな数値WPM基準・追加Gateなし)
Std Dialogue 10clip(full_story_part1_c2/c4/c6/c8/c10, part3_c2/c4/c6/c8/c10。王のセリフ=part1_c8、Charon)を再生成し以下を**記録のみ**: (a)`style.effective_style_prefix_sha256`がAdvの`add26d27…`と一致、(b)`slowdown_applied=True`・`slowdown_ratio`が既存`[1.03,1.09]`(`verify_std_english_slowdown`が既に強制)内、期待1.046〜1.060、(c)減速後ASR再検証結果(統一judge PASS/WARN)、(d)旧(run_e2e_03)Std/Advの同clip長との比較表(参考値、WPMは換算を併記するだけで基準にしない)、(e)ユーザー試聴ページで王のセリフを再提示(最終品質はユーザー試聴)。

### 3-5 費用(run_e2e_03実測)
Std Dialogue 10clip=Gemini 2.5 pro TTS 11呼出(1clipが2回)JPY4.2646+OpenAI ASR 21呼出JPY0.363=**JPY4.6276**(`cost_log.jsonl` stage=tts_a2・該当segment抽出、`compute_cost_jpy_so_far`で再計算)。単価: Gemini約JPY0.388/呼出、ASR約0.017/呼出。期待 約4.6〜5.5、最悪(全clip通算3回+Azure secondary)約12.5。

## 4. ④Family Z本文語数400±70

### 4-1 現行(所在)
- 定数: `er062:49-52 ADV_WORD_RANGE=(280,420)`、`STD_WORD_RANGE=(280,420)`、`TARGET_WORDS=350`。`er026:214 ACCEPT_WORD_RANGE=(280,420)`(Phase1互換`check_word_count` L237-241・`run_text_stage` L619-)。
- Prompt文言: `er062:97-99 R0_BLOCK_LENGTH_ADV`「about 350 words (roughly 280-420 words is fine)」、L128 `_CONVERSION_SUBSTITUTIONS`「…about 300–350 words」→「about 350 words」、L132-133 `_CONVERSION_OVERRIDE`「about 350 words (roughly 280-420)」、L137-140 `REVISE_USER_TMPL`「about 280-420 words」、L150-165 `STD_PROMPT_TAIL`は`{target_words}/{lo_words}/{hi_words}`プレースホルダでL376-378が定数から供給。コメント/docstring: L10-18等(280-420記述)。
- Guardrail: `check_adv_guardrails` L385-399(`ADV_WORDS_OUT_OF_RANGE`は`warnings`のみ)、`check_std_guardrails` L401-(`STD_WORDS_OUT_OF_RANGE`も`warnings`のみ)。`er026:625-627 FAMILY_Z_WORD_COUNT_OUT_OF_RANGE`は`[WARN]`出力のみ。
- **ハードキャップ・自動再生成・STOP・語数比Guardrailは現行に存在しない**(2026-10-12決定で撤回済み、`failures`は常に空、`auto_regenerated`はFalse固定をintegration testが確認: `er026_family_z_e2e_integration_test_01.py:124-132`)。ユーザー指示(WARNのみ・語数理由の再生成/STOPなし)に合わせるための**挙動変更は不要**。数値の更新のみ。
- 語数定義: `st.body_word_count`(見出し除外・`clean_body_paragraphs`・空白区切り)、`check_word_count`(`body.split()`)。指示の正規表現計測は参考値として併記。
- シード: `seed.json`の`conversion_plan`に「at about 300–350 words」(凍結ファイル、`SEED_PROVENANCE.json`のshaで凍結検査、`er062:544`)。**seed.jsonは編集しない**。コードの正規表現置換(L128)で400へ上書きされる(置換が効かない場合はL132-133のoverride追記が働く既存フォールバック)。

### 4-2 メロス実測(本調査)
`st.body_word_count`でrun_e2e_03 `writer/std.md`=**408語**、`writer/r2.md`=**387語**(指示と一致)。新範囲330〜470内。`ensure_stage`の再利用判定は`entry["input_sha256"]==prev_sha`(親出力sha)と出力shaのみで**Prompt文面は判定に含まれない**(`er062:504-514`、runner内で`prompt_sha`は記録のみ)ため、Prompt文言を400へ変えても本文stage(r0/r1/r2/std_adjust)は`reused`。ただし`wt(f"{wdir}/{stage}_prompt.txt", …)`(L578)は再利用時も**現行Promptで上書きする**ため、旧Promptで生成された本文の証跡(`r0_prompt.txt`等)が新Promptに置き換わる→Phase 3手順に「`writer/*_prompt.txt`を`*_prompt_gen350.txt`として退避してから実行」を入れる(provenanceの`prompt_sha256`は旧値のまま残り、本文が350目標で生成された事実の証跡になる)。

### 4-3 変更点一覧
| 区分 | 場所 | 変更 |
|---|---|---|
| 定数 | `er062:49-52` | `TARGET_WORDS=400`、`ADV_WORD_RANGE=STD_WORD_RANGE=(330,470)`(単一定義`Z_WORD_TARGET=400;Z_WORD_TOLERANCE=70`から導出し3値の不一致を防ぐ) |
| 定数 | `er026:214` | `ACCEPT_WORD_RANGE=(330,470)`(循環import回避のためliteralを維持しtestで`er062`との一致を固定) |
| Prompt | `er062:99,128,132-133,137-140` | 「about 400 words (roughly 330-470 words is fine)」「about 400 words」「about 330-470 words」。コメント/docstring(L10-18,96,127,136,375)も更新 |
| Guardrail | `er062:385-399,401-` | 範囲は定数参照なので文言(`目標 {RANGE}`)のみ追従。WARNのみは不変 |
| 文書 | `CURRENT_SPEC.md:1606`ほか | §7参照 |
| 非変更 | `seed.json`(凍結)、`er018/er055/er059`等のTrial script(Production外) | 変更しない(歴史資料) |
- 「不自然な加筆・削除による語数合わせ禁止」: 現行Promptに語数合わせの加筆削除を促す文言は無い(目標語数のみ)。新規ルール不要。

### 4-4 test設計
更新(約6件): `er062_family_z_writer_01_test_01.py:75`(「about 400 words (roughly 330-470」)、L99(「330-470」)、L148-150(境界: 8段落×40語=320語はWARN、×45語=360語が範囲内)、L173(`_story_text(8,20)`は範囲外のまま)、`er026_family_z_fiction_production_runner_01_test.py:52-59`(280/420境界→330/470)、`er026_family_z_e2e_integration_test_01.py:125`コメント。新規(約3件): (1)定数3箇所(`TARGET_WORDS`,`*_WORD_RANGE`,`er026.ACCEPT_WORD_RANGE`)の一致+中心値±70、(2)境界値329/330/470/471でWARN有無・`failures==[]`・再生成/STOPなし、(3)Z writerのPrompt・コードに`350`・`280-420`・`300–350`の残存が無い(Grep test。seed.jsonの文字列は`_CONVERSION_SUBSTITUTIONS`の被置換対象であり許容リストで除外)。メロス実測(408/387)のWARN無しをfixtureで固定。

### 4-5 Phase 3(本文reuse確認)
1. 退避: `writer/{r0,r1,r2,std_adjust}_prompt.txt`→`*_gen350.txt`。2. 新run dirで`--stage all`(writerは`--regenerate-stage`なし): `r0/r1/r2/std_adjust`が**`reused`**でLLM呼出0・`cost_log`にwriter stage 0行。3. `provenance.json`の`output_sha256`がrun_e2e_03と同一。4. Guardrail再計算で`ADV/STD_WORDS_OUT_OF_RANGE`警告0(387/408)。

### 4-6 【委任_04追記 2026-10-19】実装済み差分とPhase 3用コマンド
- 実装(③④、JPY0): ③=`er063`の`style_text_for`(dialogueは常にNone)・`dialogue()`(Std分岐から`style_prefix_override`撤去)・`FAMILY_Z_ROLE_STYLE["DIALOGUE_STD"]`ラベル/origin・`CROSS_FAMILY_COMMON_STYLE_MAP["DIALOGUE_STD"]`文言。HEAD比較でreuse_key差分は`DIALOGUE_STD`の`style_prefix_sha256`のみ(21 key同一/2 key差、make_plan a2+b1b)。④=`er062`に`Z_WORD_TARGET=400`/`Z_WORD_TOLERANCE=70`から導出(`ADV/STD_WORD_RANGE=(330,470)`、`TARGET_WORDS=400`)、Prompt文言4箇所、`er026.ACCEPT_WORD_RANGE=(330,470)`。
- Phase 3(別委任)前の`*_prompt.txt`退避(`writer/{r0,r1,r2,std_adjust}_prompt.txt`は本文再利用時も現行Promptで上書きされるため)。`<RUN_SRC>`=`er026_output/family_z_production_e2e_01/melos/run_e2e_03/writer`:
  `for s in r0 r1 r2 std_adjust; do cp "<RUN_SRC>/${s}_prompt.txt" "<RUN_SRC>/${s}_prompt_gen350.txt"; done`(新run dirへコピーする運用の場合は、コピー先の`writer/`で同名退避してから`--stage all`)。退避後、`provenance.json`の`prompt_sha256`が旧値のままで本文`output_sha256`が不変(=reused)なことを確認する。

## 5. 実装順序案(並列可能性・ファイル競合)

| 順 | 作業 | ファイル | 依存/競合 | 並列 |
|---|---|---|---|---|
| 0 | Opus条件Aレビュー(②③) | 本書 | 全実装の前提 | - |
| 1a | ④定数・Prompt・test | `er062_family_z_writer_01.py`(定数/Prompt部)、`er026_..._runner_01.py:214`、`er062_..._test_01.py`、`er026_..._test.py` | ②と`er062_family_z_writer_01.py`/同testで**同一ファイル競合**(部位は別) | 1b・1cと並列可、②とは同一worker内で逐次 |
| 1b | ③ Std Dialogue | `er063_family_z_audio_01.py`、`er063_*_test_01.py`、`er078_*_05/06c_test` | ②④と独立(ファイル別) | **並列可(先行可、本文・話者割当は確定済み)** |
| 1c | ① | 委任_01 | 独立 | 並列可 |
| 2 | ② Std Preview/Comment | `er062_family_z_writer_01.py`(`run_support_std`/新ヘルパ)、`er026:1112-1145`、`er062_..._structure_01.py`(lint、D-1決定後)、test | 1aと同一ファイル→1aの後 | 1aの後逐次 |
| 3 | Phase 3再生成(②③④ + ①は別) | 新run dir、Std support/TTS 4clip/Dialogue 10clip、AUW、gate、assemble、pages | 1a〜2全完了後(最終Assemblyは仕様と原稿が整合した状態で1回、ユーザー指示§3) | ②TTSと③TTSは**同一`tts_a2`実行**でreuse_keyにより一括(別プロセスにしない=同一run state競合回避) |

最短経路: 1b(③)を即着手 → 1a→2(②④、同一ファイル) → Phase 3。③は②④と並列で進められる。

## 6. Opusレビュー観点案(条件A、②③各3件以内)

**②**: (O2-1)置換方針P-A(`a2gen`の日本語役割を無改変流用)とP-B(b1s.PREVIEW_ROLEのZ専用日本語版)の選択はユーザー承認範囲「既存Advanced方式の日本語適用、独自方式を含まない」に最も忠実か(PreviewのquestionとAdvとの分量差の許容)。(O2-2)lint緩和D-1のL-1/L-2/L-3の妥当性とQA blocking条件変更に当たらない設計か(Std JA限定・Zファイル内・X不変・STOP頻度の見込み)。(O2-3)`method`/`STD_SUPPORT_METHOD_VERSION`による入力sha・`prior`無効化がresume/regenerate/provenance(`ensure_stage`)と矛盾しないか、Adv不変の担保。
**③**: (O3-1)`style_text_for`のStd分岐削除でreuse_keyのStd Dialogueのみが変わり他roleが不変であることの網羅性(version非bump方針)。(O3-2)primary/minimal fallback/外側ループ/resume/Local Rewriteの全経路でStd Dialogueが新Styleになる(旧SLOWER指示が残る経路が無い)こと。(O3-3)共有定数`A2_ENGLISH_STYLE_PREFIX_SLOWER`を残置し他Family(A/B/C/X/Voices)へ影響しない境界の妥当性、新WPM基準・追加Gateが混入していないこと。
(④は定数・文言のみで条件Aの対象外。ただし単一定義化と`prompt.txt`退避手順は実装時に確認。)

## 7. E-1分類とSSOT差分文案

### 7-1 分類(CURRENT_SPEC.md行番号は本日Grep、編集はPhase 2以降)
| # | 既存記述(CURRENT_SPEC.md) | 分類 | 内容 |
|---|---|---|---|
| a | L1597 Trial記録(採用なし)Preview/Comment1 A/B Trial(OPEN-338/UDR #51) | **上書き更新(2026-10-17ユーザー決定A「現行方式維持・A/B新方式不採用・追加Trialなし」を2026-10-19指示で更新)** | 決定Aの文言は残し「2026-10-19ユーザー指示②により、Std Preview/Commentは『Advanced方式の日本語適用』へ変更。A/B新方式(Trial)の採用ではなく既存Advanced方式の実装。OPEN-338/#48/#51は履歴として維持(CLOSEDのまま)」を追記 |
| b | L1600 「Standard日本語Preview/CommentはR2を基本、Advanced英語…はFamily Xの対応既存方式」 | **更新(Std側)** | 「StdはAdv方式(`b1s`役割)の日本語版(`a2gen`役割)」へ |
| c | L1600/L1611/L1674 Dialogue「既存の別Voice・従来Dialogue Style」「Dialogue別Voice(Z固有)」行 | **精緻化(Voice割当は維持)** | 「Std Dialogueの生成時Styleはadv同一(既定Dialogue Style)、`A2_ENGLISH_STYLE_PREFIX_SLOWER`は使わない。生成後6%減速・ASR/QA/retry/fallbackは維持」を追記。`PRODUCTION_WIRED`行は変更しない(再wiring後にPhase 3証跡で別途判定) |
| d | L1606 ①原稿長「280〜420英語語(Family X共通目標)」 | **上書き更新** | 「**目標400語、目安330〜470語(400±70、センター値±70)**、Adv/Std共通、WARNのみ・語数理由の再生成/STOPなし」へ。「(Family X共通目標)」の括弧は事実と異なる(Xは本変更の対象外)ため削除し、Xの語数は不変と明記 |
| e | 共通仕様Status表 L1664-1682(PD06/S3/E1/K2/P8-KP/P7/6%減速/AUW/D1、Dialogue別Voice行) | **維持(変更なし)** | S3(Std JA Preview/Comment Style)・6%減速・E1等は不変。Preview/Comment生成方式は別行を新設(`APPROVED_FOR_PRODUCTION`・実装前) |
| f | OPEN_ITEMS OPEN-338(L841) | **維持(CLOSED履歴)** | 変更しない(参照のみ)。OPEN-419は委任_01待ち(未起票)。#48/#51(REGISTER)も判断済み履歴として維持 |
| g | L672・L2046-2047 Voice A/B・A2英語ナレーション速度(`A2_ENGLISH_STYLE_PREFIX_SLOWER`) | **無関係(Z対象外)** | Family B/A/X系の既存承認仕様。変更しない |

### 7-2 SSOT差分文案(Phase 2以降で適用)
- CURRENT_SPEC「Family Z」節の追記: 「**2026-10-19追記(ユーザー正式指示、`FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01`、原文=`docs/pm/delegation_log/2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md`)**: (②)Std日本語Preview/Commentの生成方式を、Advanced英語のPreview/Comment方式(Listening Focus/Mid-story Recovery+Next Question/Preview[theme-problem-value-question、Comment1・2との重複回避]、`er062 run_support_adv`)の日本語版へ変更する(2026-10-17ユーザー決定A『現行方式維持』は本指示で上書き)。別の独自方式は含まない。(③)Std Dialogueの生成時Styleはadvと同一の既定Dialogue Styleとし、生成時の減速指示`A2_ENGLISH_STYLE_PREFIX_SLOWER`はZのDialogueで使わない。生成後6%減速・ASR/音声QA/retry/fallbackは維持。narrator PD06・Std本文ナレーション6%減速は不変。(④)Family Z本文語数: 目標400語、目安330〜470語(400±70)、Std/Adv共通、WARNのみ(ハードキャップなし、語数理由の自動再生成・STOPなし、語数合わせの不自然な加筆削除禁止)。Status: `APPROVED_FOR_PRODUCTION`・実装前(`PRODUCTION_WIRED`未付与)。」
- DECISION_LOG末尾: 「2026-10-19 FZQI 委任_02: ②③④の現行経路・差分設計・再生成計画(JPY0)。実装はOpus条件A後」。
- 各項目のStatus管理(ユーザー指示§4): ②③④を個別にStatus管理し、Phase 2実装→Phase 3 runtime証拠(正式初回経路・retry/regeneration/resume・実Prompt/Style/Voice/model_id/routing記録)が揃った項目のみ`PRODUCTION_WIRED`。

## 8. 判断候補(Fable宛、`USER_DECISION_REQUIRED`ではない)
- **D-1: Std JA lintの`LISTEN_INSTRUCTION`の扱い(§2-4)**。分類=**B(承認範囲内で自己解決可、ただしQA blocking条件に隣接するためFable判定要請)**。根拠: ユーザー指示②(`2026-10-19_…_USER.md`の「何に注目して聴けばよいか」)+Trial B'実績(3/3 NG, er076 PRODUCTION_IMPACT_02.md「lint例外なしでは採用不能」)。推奨=L-1(Advと同一思想: blockingをやめWARN記録)。新Gateは作らない。
- P-A/P-B(§2-3): 推奨P-A(新Prompt文を作らない)。Opus観点O2-1で確認。
- いずれも新仕様の創作ではなく、ユーザー指示の実装方式選択。

## 9. 費用まとめ(Phase 3、①を除く)
| 項目 | 期待 | 上限見込み | 出典 |
|---|---|---|---|
| ② LLM(Std support 4呼出) | 約0.4 | 約0.8 | run_e2e_01/02 `cost_log.jsonl` stage=support |
| ② S3 TTS+ASR 4clip | 2.27 | 約6.8 | run_e2e_03 `cost_log.jsonl` stage=tts_a2 preview/comment_1-3 |
| ③ Std Dialogue 10clip(Gemini 2.5 pro TTS+ASR) | 4.63 | 約12.5 | run_e2e_03 同 full_story_part1/3_c2..c10(偶数) |
| ④ 本文 | 0 | 0 | writer reuse |
| AUW/gate/assemble/pages | 0 | 0 | API無し(ASRは生成内に計上済み) |
| **合計** | **約7.3** | **約20** | |
Phase 3の予算ガード提案: `--approved-budget-jpy 20`(委任文で明示承認が必要)。run_e2e_03(JPY36.38/100)実績の約20%。日次1,000円枠(7-9)内。実行は本Phaseでは行わない。

## 10. 自己チェック
有料API呼出0・コード変更0(新規ファイルは本書と委任文保存のみ)・Production変更0。語数実測と費用再計算は既存ログのread-only処理。STOP: `stop_scope_check_01.py --managed-id … --run-dir run_e2e_03` rc=0(`stop:false`)。

## 追記(2026-10-19 委任_06 実装反映、Opus_E GO_WITH_FIXES採用)
- ②はP-Aで実装済み(`er062_family_z_writer_01.py::run_support_std`=`run_support_adv`同形、a2gen役割文無改変、`STD_SUPPORT_METHOD_VERSION="adv_method_ja_v1"`、共通ヘルパ`support_stage_input_sha(level, text, plan_sha)`をer026 `stage_support`とer062 CLIから呼ぶ。priorはmethod一致時のみ)。
- F3-1: 設計2-3の(c)「Part3固有語の出現」(英日跨ぎ)は削除。`overlap_notes`=日本語4-gram一致(カタカナ3字以上の固有名・頻出語除外の参考値)+既存`spoiler_ja`辞書出現+カタカナ固有名。Gate化せずconsole WARN+`support.json`記録のみ。F3-3: 旧`scene_transition`文の不在とfam_c不呼出をtestで固定。F3-2はPhase 3でFableが照合。
- D-1(2-4)=L-1採用(R-E4): `lint_support_text(..., allow_listen_instruction_as_warn=False[既定], warn_out=None)`を追加し、Z Std呼出側のみTrue。結果は`support.json`の`lint_warn`。他blockingは維持、関数既定は不変。
