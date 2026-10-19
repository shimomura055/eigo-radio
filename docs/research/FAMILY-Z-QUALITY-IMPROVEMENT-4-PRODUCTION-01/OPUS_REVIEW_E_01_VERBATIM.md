# Opus独立技術レビュー_E (FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01、条件A、read-only)

## 総合判定
- ①KP日本語意味: **GO_WITH_FIXES**。診断と案IIIは妥当。実装前に直す点はF1-1〜F1-6
- ②Std Preview/Comment: **GO_WITH_FIXES**。P-AとD-1(L-1)を承認範囲内として進めてよい。直す点はF3-1〜F3-3
- ③Std Dialogue: **GO**(コード差分は妥当)。ただしPhase 3の再利用計画はR-E6のとおり成立しない
- ④語数400±70: **GO**
- Phase 3統合計画(R-E6): **NO_GO(このままでは実行不可)**。下記の修正計画へ差し替えが必要

---

## R-E1 ①の診断・方式・語彙・承認境界

**所見1(妥当、Low)**: 「誤訳ではなく、英語を一般化した後に日本語意味が追従しない(stale)」という診断は、コードで裏付けが取れた。
- `er003_key_words_canonicalization.py:726,742`は選定時のglossを無改変で引き継いでいる。
- `er003_key_words_gloss_alignment.py:119,138`は`_GENERIC_TOKENS`を追加語から外している。
- `:147-150`の対象選定では、人称の一般化が永久に対象外になる。

OPEN-352と同じ原因クラスという整理も正しい。案IVは工程順と承認済みPromptの適用位置を変え、案Vは承認済みcanonicalization Promptを直接編集することになる。どちらも承認範囲を超える恐れがあり、退けてよい。

**所見2(High: 実装時の罠)**: `collect_unevaluated`(`:629-640`)は`select_alignment_targets`をそのまま使っている。
- 新規生成用に`select_alignment_targets`を拡張すると、そのまま`collect_unevaluated`の定義も広がる。
- その結果、status無しの人称一般化item(Coffeeの`shock someone's wallet`等、健全なもの)が、Z `stage_kp`:1273、`load_level_inputs`:1335、X runner関所で一斉にSTOPする。
- **F1-1**: 関数を明示的に2つへ分けること。(a)生成用の対象 = 従来の対象 ∪ 人称一般化item ∪ 決定論checkで不整合のitem。(b)消費側(未評価判定)の対象 = 従来の定義 ∪ 決定論checkで不整合のitem。(b)に人称一般化item全件を入れない。この分離をtestで固定する(Coffee実artifactのfixtureでSTOP 0件)。

**所見3(Med)**: 消費側の決定論checkが`not gloss_alignment_status`のitemだけに掛かると、取りこぼしが出る。旧版で`ALIGNED`(追加語が理由)になったが人称語が残っているitemは素通りする。
- **F1-2**: 不整合判定は、statusにかかわらず全itemに適用する。
- 例外は`HUMAN_RESOLVED`(`:251`)のみ。人間の確定値を再びSTOPさせると無限ループになるため。ただしWARNとしては記録する。

**所見4(Med)**: `validate_item_corrected`(`:443-447`)は、`current_gloss_consistent=true`かつ同一文字列のとき、`adopt=cur`を採用する。
- **F1-3**: 決定論checkは`proposed_gloss`ではなく、採用値`adopt_gloss`に対して掛ける。
- 既存の指示文2(`:385-387`「既に表している場合は書き換えず…書き換えるのは欠けている・誤っている場合だけ」)はLLMを現状維持へ強く寄せる。このため追加の制約文に「不定の人称を具体的な人称で訳すことは『誤っている』に当たる」と明記する。
- さらに、retryのuser messageに前回のINVALID理由(人称語の残存)を項目単位で渡す。現状のretryは同じmessageを再構築するだけ(`:479`)なので、同じ応答が返ってHRになる確率が高い。

**所見5(Med: 語彙の過検出)**: 日本語の閉じた語彙を部分文字列でそのまま照合すると、次の語で過検出する。
- 「暴君」「主君」「君主」(君)
- 「下僕」「公僕」(僕)
- 「私的」「私立」「公私」(私)
- 「彼方」「彼岸」(彼)

メロスは王(暴君)が登場する物語であり、`serve one's lord`→「主君に仕える」型で実害が出得る。
- **F1-4**: 境界付きで照合する。直前が漢字でないこと、かつ直後が助詞・接尾(の/が/は/を/に/と/も/へ/たち/ら/自身/方)か文字列の末尾であること。
- 再帰の規則は「KPのどこかにone's/oneselfがあれば自分/自身を許容」とする。`put oneself in someone's shoes`のような混在型を誤検出しないため。
- 「相手」「その人」「人」を検出しない設計は、someoneの自然な訳として正当なので維持してよい。

発火条件は「KPに一般形トークンがあり、かつKPに具体人称語(`_PERSON_DEPENDENT_TO_GENERIC`のkeyとme/him/us/them)が無い」で妥当。数値基準や新Gateは増えず、既存のvalidate→retry(2回)→HRの中に収まっている。

**所見6(Med: 語義選択)**: 既存の指示文`:398`「key_phrase単体で他の文脈でも再利用できる自然な訳…文脈の追加はしない」は、ユーザー要件「文脈による立場／代わりの選択」と緊張関係にある。設計の制約文(source_sentenceは語義の選択にだけ使い、指示対象の決定には使わない)で解消できる。ただし語義の選択はLLM任せで、mockでは担保できない。
- **F1-5**: ユーザー原文「同種の誤訳を使ったRegression」を満たすため、少額の実LLM Regressionを受入に含める。内容は記事に依存しない合成itemで、同じ英語KPを代わり義・立場義の2文脈に置くペアなど約8〜12item。1回JPY0.06程度なので合計JPY1未満。
- 使用モデルはProduction経路と同一(検証対象が本番経路のため)と明記する。これは新Trialではなく、承認済み①の受入evidenceである。

**所見7(承認境界)**: 決定論的な不整合理由の追加は、形式上は新しいblocking理由になる。ただし以下の理由から、**承認範囲内の改善**と判断する(ユーザー判断に戻す必要はない)。
- ユーザー原文①が「人称・所有格・指示対象…が不当に変わらない」という品質要件そのものと、「検査・retryの改善」を明示している。
- 既存のKGCPW(`APPROVED_FOR_PRODUCTION`)のvalidate/HR機構の中に収まっている。
- **F1-6**: CURRENT_SPECに「新しいvalidate理由+HR経路+kill switch(`GLOSS_ALIGNMENT_ENABLED`)OFF時は無効」を明記し、最終報告①で付随変更として明示する。

## R-E2 ①のメロス適用(stage_kpの人称整合関所)

**所見1(High)**: 設計§5-2は、再利用経路で`key_phrases/a2_result.json`(canonicalization.merged)を更新する。しかしこれは`ensure_stage(kp_a2)`の出力ファイル(`er026:1266`)である。
- `ensure_stage`(`er062:511-513`)は、再利用時に出力ファイルのshaとentryを照合する。
- そのため、関所が書き換えた次の実行で`FamilyZProvenanceMismatchStop("出力ファイルsha不一致")`になる。
- **F2-1**: 関所での修復は次のどちらかにする。(a)`a2_result.json`を更新するなら、同じ処理の中で`prov.set_entry`により`output_sha256`を更新し、修復記録(理由・対象rank・旧/新gloss・version)を付けて`prov.save()`する。(b)`keywords_canonicalized.json`のみを更新し、`a2_result.json`は不変にして別のaudit fileへ記録する(`_load_gloss_hr_resume`:1186と同じく「artifactを正」とする思想)。推奨は(a)で、来歴が一本化される。

**所見2(Low)**: `mark_stale_descendants("kp_a2")`は空振りする。`DEPENDENTS`(`er062:61-64`)にkp_a2の子が無いため。TTSは`ensure_stage`で管理されていないので害はないが、「下流がstale化される」という前提で設計しないこと。

**所見3(Med: 発火位置)**: 関所の置き場所は、`ensure_stage`の後かつ`collect_unevaluated`(:1273)の前にする。この位置なら初回・再利用・regenerate・HR resumeの全経路で1箇所を通る。
- 修復が成立しなかった場合は、既存の`_gloss_hr_gate`と同じHR報告→STOPの経路に乗せる(新しいSTOP経路を作らない)。
- 修復は有料呼出なので、`_guard(ctx, ...)`の予算guardを通す。
- `load_level_inputs`(:1335)と`--stage tts_*`単独起動は、F1-1の(b)で不整合を検出してSTOPする(fail-closed)。これで十分。

**所見4(波及の見立ては正しい)**:
- SRC D1は選定結果が不変なので同一結果になる。
- kp_expl(b1b)は、b1bのglossが不変なので署名(:1290-1301)も不変。
- P8-KPのreuse_keyはtext shaを含む(`er063:708-715`)ので、同じrun dir内ならkp2_jaだけが変わる。ただしR-E6のとおり、Phase 3は新run dirで全clipを再生成する前提になるため、実害はない。

**X**: X runner関所は`collect_unevaluated`をSTOPで使うだけで、修復経路は無い。census上、X側で不整合となるartifactは0件。fail-closedで許容できるが、「X: 修復経路なし・STOPのみ」をOPEN_ITEMSに記録すること(ユーザー原文§4)。

## R-E3 ②の方式(P-A)・sha・prior・WARN

**所見1(妥当)**: P-Aは「Advanced方式の日本語適用」に該当し、「別の独自方式」には当たらないと判断する。根拠は次のとおり。
- `a2gen.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLE`(`er003_v1_iran01_a2_generate.py:127-204`)は、b1sの3役割(`er003_v1_b1_scaffold_01_generate.py:146-213`)と役割・分量・開示方針が同一である。
- これはX Stdの既存Production資産であり、2026-10-13のユーザー判断(Z Std PreviewはX Std `PREVIEW_ROLE`基準)とも整合する。
- P-Bは新しいPrompt文の創作になるので、P-Aより不適。
- 差分(a2genのPreviewは80〜110字で、questionの独立文が任意)は許容範囲。試聴でPreviewの引きが弱いと判断された場合のP-Bは、将来候補(ユーザー判断事項)とする。

**所見2(妥当、Low)**: `STD_SUPPORT_METHOD_VERSION`を入力shaへ混ぜる対策は正しい。
- 旧cacheが`reused`で通ってしまうのを防ぎ、明示regenerateが無ければ`ProvenanceMismatchStop`になる(fail-closed)。
- Advのshaは不変。support_a2には子stageが無いので波及しない。
- `prior`をmethodが一致するときだけ使う規則も正しい。
- 共通ヘルパを`er026:1139`と`er062` CLIの2箇所から呼ぶ方針でよい。他storyの旧方式runは、resume時にSTOPして明示regenerateを要求する。これは意図どおりの挙動として記録する。

**所見3(Low: WARN記録の実効性)**:
- (a)日本語の4-gram一致は、人名(「メロスは」等)でノイズになる。物語の固有名や頻出語を除外するか、参考値と明記すること。
- (c)「Part3固有語の出現」は、英語本文と日本語出力を言語をまたいで照合することになり、設計どおりには機能しない。
- **F3-1**: (c)は削除するか、spoiler辞書(既存の`spoiler_ja`)とカタカナ固有名に限定する。いずれもGate化しない方針は妥当。

**所見4(Med: 品質リスクの開示)**: Trial B'では、Comment1の注目点が事実からずれたケースが2/3あった(`er076.../SETS_02.md:88`)。方式上、決定論checkは作れない。
- **F3-2**: Phase 3の出力をFableが本文と照合し、最終報告②に修正前後と併せて明記する。最終判断はユーザー試聴に委ねる。

**所見5(Low)**: 旧`scene_transition`文(`er062:855-856`)は、新方式で入力から消える。Advにも無いので問題はない。test(4)で、fam_c経路を呼ばないことに加えてこの点も固定すること(F3-3)。

## R-E4 ②のStd JA lint(D-1)

**判断: L-1は承認範囲内の不可避な付随変更として妥当。ユーザー判断に戻す必要はない。** 根拠は次のとおり。
1. ユーザー原文②は、目的を「何に注目して聴けばよいかを示す」と明記している。Adv型のListening Focusの自然な日本語(「〜に注目してください」)は、`_LINT_LISTEN_JA`(`er062_family_z_structure_01.py:642`)と、`fam_c`禁止語句(`er013:368-374`。「注目して」「どうなるでしょう」を含む)に構造的に衝突する。
2. 適用元であるAdv方式のlintは、聴取指示を検査しない(`:660-662`)。このblocking条件は、置き換えられる旧Family C方式に付属していたもの。
3. Trial B'の時点で「lint例外設計が必要=Gate仕様変更に当たる」と記録されており(`PRODUCTION_IMPACT_02.md:8`)、OPEN-338(`OPEN_ITEMS.md:841`)にも「lint例外設計等が未解決」と記載された状態で、ユーザーに提示済みである。ユーザーはそれを踏まえ、10-19にAdv方式の適用を明示指示した。Charterの判断前確認(1)「判断済みでないか」に照らし、判断済みの帰結と扱える。

L-2は、「耳を傾け」「どうなるでしょう」がListening Focus/Next Questionの自然な形であり、STOPリスクが残るので劣る。L-3は役割文の改変(独自方式の疑義)になり、Trial結果(3/3 NG)から見てSTOPも残るので不可。

実装条件:
- WARN化するのは、Z Std JAの`LISTEN_INSTRUCTION`のみ。
- NEWS/IOL/Point/構造ラベル/ネタバレ/禁止名/言語はblockingのまま。
- WARNは`support.json`に記録する。
- 関数の既定挙動を変えるのではなく、Z Stdの呼出側から明示する(trial/他の呼出元への無言の波及を避ける)。
- CURRENT_SPECと最終報告に「②付随: Std JA lint LISTEN_INSTRUCTION blocking→WARN(Adv lintと同一思想)」と明記する。

## R-E5 ③④の設計

**③(コードは妥当)**:
- `style_text_for`(`er063:700-705`)と`dialogue()`(:785-795)の変更は実装済みで正しい。
- primary/minimal fallback/外側ループ(`n3_tts:406-451`)は単一の生成関数を経由しており、SLOWERが残る経路は無い。
- `_effective_style_sha`(:999-1007)はStdでも`add26d27…`を記録するので、Adv同一の証跡に使える。
- 新しいWPM基準やGateは混入していない。共有定数を残置する判断も正しい。

**所見(High、R-E6に直結)**: `DIALOGUE_STD.style_label`が、旧記録`existing_dialogue_style+A2_SLOWER(...)`(run_e2e_03 `a2/audit/style_record.json:21`)から`...+post6%`(:179)へ変わる。
- `inspect_run_style_record`(:589-603)は、全roleの`style_label`を比較する。
- そのため、run_e2e_03系のrun dirで実行すると、a2だけでなくb1bも`RECORD_MISMATCH`→`FamilyZRunStyleMismatchStop`になる。`expected_style_record`(:576-582)は全roleを含むため。
- 設計§3-2の「version非bumpでStd Dialogue 10clipのみ自動再生成」は同じrun dir内でしか成立せず、そのrun dirはこのguardで止まる。
- labelを据え置く回避は、記録の虚偽になるので不可。

**④(GO)**:
- 定数の単一定義化、Prompt5箇所、test、Grep testで問題ない。
- 新run dirでも`writer/`は許可リストでコピーされ(`er063:634`)、reuseされる。
- `*_prompt.txt`の退避手順は妥当。将来候補として、再利用時にprompt.txtを上書きしないコード修正もあり得る。
- `er026:214`をliteralのまま維持し、testで一致を固定する方針でよい。

## R-E6 統合・費用

**所見(High)**: Phase 3計画(新run dirへコピー→4+10+1 clipだけ再生成、期待JPY7.3、上限20)は、既存の安全設計と矛盾しており実行できない。
- 公式のコピー機構`REUSE_*`(`er063:629-641`、委任_15 Opus R-C4)は、wav・`tts_generation_results`・audit・承認を持ち込まない(「新runで全Roleを再生成する。取り込み機構は作らない」)。run_e2e_03自体もreuse 0件で生成されている。
- 同じrun dirで実行すると、上記のstyle_record guardでSTOPする。
- 加えて、同じrun dirの`human_approved_segments.json`は、Gateで再生成clipの不採択を覆い得る(`er063:1273-1274`)。

**推奨(F6-1)**: 新run dirを公式のコピー機構(テキスト系のみ)で作り、Std・AdvともTTSを全再生成する。根拠は次のとおり。
- 前例(run_e2e_02→03)、R-C4、Style混在guardのいずれとも整合する。
- ユーザー原文の「可能な限り再利用」は、安全設計上再利用できない場合を許容する文言である。

予算は、run_e2e_03の`cost_by_stage`(tts_a2がJPY22.45、全体JPY36.38)から再見積りする。期待は約JPY35〜40、上限は個別にcapを再設定する(目安JPY60〜80)。これは日次1,000円枠内の少額なので、Fableの権限で設定してよい。

代償は、Adv音声も再生成されることで、試聴対象が全編に広がること。最終報告で明示する。

代替案として、run dirを丸ごと複製し、role単位でStyle記録を移行する(変更roleのclipを必ず再生成し、該当承認を失効させる)方法もある。ただしこれはR-C4の決定とStyle混在guardを変える新しい処理フローなので、採るなら別途、条件Aのレビューが必要。今回は非推奨。

**最終Assemblyの成立条件(F6-2)**:
- ①〜④の実装とtestがすべてPASSし、commitした後に、新run dirで1回だけ通しで実行する。
- 実行順は、kp(人称関所の発火とprov更新)→`--regenerate-stage support_a2`→tts_a2/tts_b1b→gate→assemble→pages。
- 以下を確認する。
  - kp2のglossが不定人称・代わり義になり、`gloss_alignment_status=ALIGNED`
  - support.jsonに`method=VERSION`とWARN記録がある
  - Std Dialogueの`effective_style_prefix_sha256`がAdvと同一(`add26d27…`)で、`slowdown_applied=True`、比率が[1.03,1.09]
  - writerが`reused`で、語数WARNが0(408/387)
  - 新しいstyle_recordがNEW_RUNとして記録される
  - ページのKP、Preview/Comment、Dialogueが新しい原稿と一致する
- 技術PASSとユーザー試聴PASSは分けて扱う。

---

## 将来候補(今回のScope外)
- Std Previewのquestionを必須化するP-B(新Prompt文になるためユーザー判断事項)
- 選定Promptへ人称規則を追加する保険策(承認済みPromptの改変)
- `meaning_general`/`usage_in_text`の2フィールド化
- writer再利用時のprompt.txt上書き停止
- role単位のStyle記録移行機構(音声の部分再利用用、要条件A)
- X runnerへの人称修復経路の配線

## 関連ファイル
- C:\Users\tensh\eigo-radio\er003_key_words_gloss_alignment.py (119-150, 364-455, 619-640)
- C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py (1112-1143, 1173-1188, 1239-1316, 1321-1339)
- C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py (61-66, 492-522, 806-930)
- C:\Users\tensh\eigo-radio\er062_family_z_structure_01.py (634-687)
- C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py (163-189, 576-641, 700-795, 999-1007, 1265-1274)
- C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\a2\audit\style_record.json (20-24)
- C:\Users\tensh\eigo-radio\er076_output\family_z_preview_comment1_dual_trial_01\PRODUCTION_IMPACT_02.md, SETS_02.md
