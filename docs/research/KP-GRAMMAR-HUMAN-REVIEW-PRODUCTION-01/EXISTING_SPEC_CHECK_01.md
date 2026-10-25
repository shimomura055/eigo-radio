# EXISTING_SPEC_CHECK_01(KP・単語解説・文法 Human Review 正式導入: 既存仕様の事実確認)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_01 / 日付: 2026-10-25 / API 0・Production file変更0(読取のみ)
ユーザー指示原文: `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`(Status=APPROVED_FOR_PRODUCTION、目標PRODUCTION_WIRED)
委任文逐語: `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_01.md`
表記: 事実=ファイル:行で確認済み / 推定=未確認(その旨明記)。行番号は2026-10-25時点(並行agentが他ファイルを編集中のため、実装時に再確認する)。

## 0. 結論(先に)
1. **KP(Key Phrase)は現在、全文選定(Prompt 2)=最大3件。順位付き候補(TOP 8)・Human確認工程は存在しない。** 選定はレベルごと(Std=a2 / Adv=b1b)に、各レベル本文から別々に行う。
2. **単語解説コーナー=Part 1 は「確定KP(最大3件)の各件」を5項目で描画しており、Advancedのみ**(Standard・A/B/C・Yへは拡張しない、と承認済み)。新仕様の「KP3件を含む5件」は、**KP音声に使わない追加2件を新たに確定(used_form・本文中の意味・引用文・T1訳)する必要がある**。Part 1の入力を `keywords_canonicalized.json` からそのまま取る現配線では実現できない(§4)。
3. **文法(Part 2)はProductionに存在しない。** Trial-07/08(VALIDATED(限定))のDEV専用コードのみで、ユーザーが明示的に配線を禁止している。「既存の文法選定」の実体はTrial規則であり、**Part 2のProduction採用の明示承認が別途必要か**はFable/ユーザー判断(§5、選択肢A/B)。
4. Family Yは正式Production入口が無い(OPEN-484)。KP選定コード自体はX/Zと共通moduleをTrial scaffoldが呼ぶ形で、**Y用のHuman Review配線は「Y正式入口の新設」と同時**になる。未整備として追跡する。
5. 既存のHR機構(er011 HR Lock=音声ASR不合格の人間確認、gloss HR=gloss再整合不成立の人間確認、`REVIEW_REQUIRED`=canonicalization QA FAIL)は、**いずれも「選定候補をHumanが選ぶ」機構ではない**。新工程と重複せず併存する(§3)。

## 1. KP選定(X/Z共通の現行仕様)
| 項目 | 事実 | 根拠 |
|---|---|---|
| 正式backend | `fulltext_p2`(全文選定・Prompt 2・GPT-6 Luna・最大3件)。A/B/C(`strategy_l`)は無変更(27-7) | `er003_v1_n3_01_scaffold_generate.py:296-330,348`、`CURRENT_SPEC.md:1995`(PRODUCTION_WIRED、OPEN-454) |
| 件数 | `KP_COUNT_MAX=3`、`KP_COUNT_MIN=1`(0件は失敗。1〜2件は「適切な候補不足」で許容、数合わせ禁止)、語数1〜5 | `er105_kp_fulltext_selector_01.py:33-35` |
| Prompt | Prompt 2は**一字一句固定**(変更はユーザー明示承認、sha256 `a12896f4…3dc9a`をtestで固定)。「3つ選んでください」「6. 3件選定」「英語上級者が学ぶ価値」。**Std/Adv別のPromptは無い**(各レベル本文に同じPromptを適用) | `er105…:51-67`、`er105_kp_fulltext_selector_01_test_01.py`、`er003_test_kp_fulltext_wiring_01.py` |
| 出力schema | `items[{phrase, word_count}]`。件数制約はschemaに置かずローカル検査(strict JSON) | `er105…:74-96` |
| 順位 | **LLMの出力順=`rank` 1..n**(`build_original_items`)。明示的な順位付け指示・理由出力は無い | `er105…:266-291` |
| 決定論Validator | 連続一致/語数1〜5/件数/重複/旧形式precheck(`validate_and_resolve`)、CMU発音辞書登録語のみ(`er108`)、外側retryでの除外語(`apply_exclusions`) | `er105…:225-263,381-420`、`er108_kp_cmu_lexicon_gate_01.py` |
| 後段 | canonicalization(基本形化・人称一般化。`CANONICALIZATION_PASS/REVIEW_REQUIRED/INVALID`の3状態)→ gloss再整合(既定ON・無条件)→ Redundancy QA(2件未満はskip)→ 記号検出 | `er003_v1_n3_01_scaffold_generate.py:475-640` |
| 採用規則 | 採用は`CANONICALIZATION_PASS`のみ。`REVIEW_REQUIRED`は外側retryで再選定→上限後`OUTER_RETRY_EXHAUSTED`でSTOP(承認済み3状態モデル「REVIEW_REQUIREDは自動採用しない・人間確認後に採用可」への整合是正=OPEN-504) | `…scaffold_generate.py`(`run_kp_with_outer_retry`内コメント、729〜) |
| 外側retry | 通算`KP_OUTER_RETRY_MAX=3`(選定失敗・canon INVALID・CMU post-canon NG・REVIEW_REQUIRED)+Redundancy/記号NG再選定(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)。不適合語は累積`excluded`で次周の選定noteと`apply_exclusions`へ渡る。最終失敗時は旧attemptを`keywords_canonicalized.STALE_attemptN.json`へ退避 | `…scaffold_generate.py:631-872` |
| 入口 | X: `run_theme_scaffold`→`sc.run_key_phrases(..., kp_backend="fulltext_p2")`(`er019_family_x_audio_production_runner_01.py:608-664`)。Z: `stage_kp`→`w62.run_kp_stage`→`run_kp_with_outer_retry_fulltext`(`er026_family_z_fiction_production_runner_01.py:1486-1493,1693-1722`、`er062_family_z_writer_01.py:1309-1366`) | 左記 |
| 「KP vote」(er104) | **ASR 3票多数決=KP英語音声の合否判定**であり、選定の順位付け/投票ではない。本タスクの対象外(音声Gateとして無変更) | `er104_kp_three_asr_vote_01.py:1-30` |
| KP音声構成 | Std: 英語Phrase→日本語意味(J3)→英語Phrase。Adv: 英語Phrase→英語解説(Variant B)→英語Phrase。segment=`kp{rank}_english / japanese_meaning / explanation`(rank駆動で1〜3件可変) | `CURRENT_SPEC.md:2021-2030`、`er019…runner_01.py:1498-1515,1836-1856` |
| 公開ページ | KPは`used_form`(英語)・`japanese_gloss`を表示。`keywords_canonicalized.json`のrank駆動 | `er019…runner_01.py:2595-2600` |
| 制作順序 | X: plan→scaffold(support生成→KP→Part 1[Advのみ])→tts→assemble→player。Z: …plan→support→**kp**(b1b→a2、続けてAdv解説`kp_expl_b1b`→Part 1`kp_part1_b1b`→T1訳`kp_part1_ja_b1b`)→tts_b1b/tts_a2→provision_shell→gate→assemble→pages→page_verify | `er019…runner_01.py:3118-3238`、`er026…:1130-1135,1693-1790` |
| レベル別差異 | KPは**Std/Advで別選定**(本文が異なる)。英語Phrase共通化は両レベル本文が同一のときのみ許可 | `er062_family_z_writer_01.py:1309-1311,1371`(`english_phrase_sharing_allowed`) |

## 2. 来歴・再生成・resume・signature(新工程が合わせるべき既存機構)
- **Z**: `w62.ensure_stage(prov, "kp_<lv>", input_sha=_sha(text), out_path=key_phrases/<lv>_result.json, runner, regenerate=…)`。出力+来歴entryがあり`input_sha`/`output_sha`一致→reuse、不一致→`FamilyZProvenanceMismatchStop`、stale指定は明示`--regenerate-stage`が必要、regenerateで子孫をstale化(`er062_family_z_writer_01.py:690-717`)。下流の署名: Adv解説`kp_expl_b1b`のsigは「used_form(+gloss+source_sentence)」(`er026…:1735-1748`)、Part 1は`phrases_signature`(rank昇順の表現+Prompt sha+model、`er003_kp_general_explanation_01.py:206`)、T1訳は引用英文+Prompt sha+model。**KP表現が変わると下流は自動で古くなる**(Z=STOP→`--regenerate-stage`、X=自動再生成)。
- **X**: `--scaffold-only kp`は**KP再生成を1レベル1回に制限**(`_kp_already_generated`が`keywords_runtime_metadata.json`等を「生成済み」と数えSTOP、`er019…runner_01.py:396-407,632-647`)。Part 1は`_part1_kp_items`が`keywords_canonicalized.json`を読む(`:441-450`)。`--stage study_text`はKP再選定なしでPart 1だけ再生成(`:584-598`)。
- **gloss HR(既存の人間確認)**: gloss再整合が不成立のitemは`emit_human_review_notice`で報告書+snapshotを書き、Z=`FamilyZE2EStop`で停止、`resolve_gloss`後に同じstageを再実行すると**選定は再実行されず**snapshotから復元される(`er026…:1499-1556`、`er003_key_words_gloss_alignment.py:1068,1200,1255`)。**新工程の「Human確定後に再選定せず続行」は、この既存パターン(snapshot復元)と同型で実現できる。**
- 停止の運用: RESTART_STORM=同一runを5分に3回起動で自動STOP(`PM_GOVERNANCE.md:3496`)。Human待ちで止まる→確定後に再実行、は通常2起動で収まるが、再選定の往復で近接起動が増える場合に注意(Opus論点)。

## 3. 既存のHuman Review機構(新工程との関係)
| 機構 | 目的 | 位置 | 新工程との重複 |
|---|---|---|---|
| er011 HR Lock / `approve_regenerate` / `asm.record_human_approval` | 音声のASR不合格segmentの再生成/承認(コスト暴走防止) | TTS・Assembly | 重複なし(音声品質。新工程はTTS前の選定) |
| gloss HR(`emit_human_review_notice`/`resolve_gloss`) | gloss再整合が不成立のKP itemの日本語意味を人間が確定 | KP段内 | **候補段階で発生しうる**。新工程では「候補のgloss HR」を`GLOSS_HR_PENDING`扱い(AUTO対象外、Humanは`resolve_gloss`後に選択可) |
| canonicalization `REVIEW_REQUIRED` | QA FAILのitemは自動採用しない・人間確認後に採用可(承認済み3状態) | KP段内 | 新工程では候補に`qa_fail`旗を付け、AUTO対象外・Human選択は可(「人間確認後に採用可」の実装) |
| 過去の個別KP再選定tool | `er019_family_x_stage3e_small_bag_b1b_kp_reselect_01.py` | 個別対応 | 先例のみ。新工程は一般化 |
- **Humanが候補から3件/5件を選ぶ機構は既存に無い**(Grep: `kp_candidates`/`kp_human_review`該当0。`kp_review`は`REVIEW_REQUIRED`再試行系のtest名・関数名のみ)。ファイル名は混同を避け`kp_human_review.json`とする。

## 4. 単語解説コーナー=Part 1(影響整理)
- 仕様: Advancedのみ、確定KPの`used_form`だけを別LLMへ渡す解説(1 call/set)+引用英文だけを渡すT1訳(1 call/set)、表示は`<section class='study'>`(英語表現/本文中の意味/本文引用英文/日本語訳/解説の5項)。`PRODUCTION_WIRED`(X/Z、OPEN-512、`CURRENT_SPEC.md:2039-2052`)。`MAX_PHRASES=5`(旧5件artifactも許容、`er003_kp_general_explanation_01.py:68,125`)=**5件入力そのものは受理できる**。
- **現配線の入力=`keywords_canonicalized.json`(=KP音声のitems)**: X `_part1_kp_items`(`er019…:441`)、Z `_kp_items_b1b`(`er026…:1810`)。新仕様の追加2件はKP音声に使わないため、`keywords_canonicalized.json`へ入れると**KP音声segmentが5件生成される(誤り)**。→ 別ファイル(`vocab_confirmed.json`)を作りPart 1の入力だけを切替える(DESIGN_01 §c)。
- 追加2件に必要な処理: used_form(基本形化・人称一般化=canonicalization)・本文中の意味(gloss再整合)・source_sentence逐語確認(SRC D1 / Part 1の逐語照合)。候補段階で全候補に一括適用するので追加2件も同一Gateを通る。
- 影響: Xの公開ページ=`study_html_for_audio_dir`が`study_text/`を描画(件数可変、`<section>`構造は不変)。Z pages=`stage_pages`が`_require_part1_fresh`後に同一builder。解説call・T1 call=1 call/setのまま入力件数3→5(出力トークン増)。費用見積はBUDGET_PLAN_01(推定)。
- **Standardには単語解説コーナーが無い**(Part 1はAdvのみ)。新仕様「単語解説5件」はAdvにのみ適用できる。Stdで「5件」を実現するにはPart 1のStd拡張=新仕様が必要で、本指示に明記が無い(判断候補I-1)。

## 5. 文法(Part 2)の事実
- **Status**: Trial-07=事前登録基準で8作品中7合格→USER_DECISION_REQUIRED候補(`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/ADOPTION_NOTE_07.md` §1)、Trial-08(倒置の優先順位を下げる)=**VALIDATED(限定)**、Fable受入2026-10-25 委任_19、**Production未配線**(同`ADOPTION_NOTE_08.md`末尾、`OPEN_ITEMS.md` OPEN-497、`CURRENT_SPEC.md:2041`「Part 2〜4は未配線(Trial-07 VALIDATED(限定))」)。
- **配線禁止の原文**: `docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_06.md:12`「Production変更は禁止。正式採用は別途ユーザー判断とする。」、`:110-112`「合格:VALIDATED(Production採用は未承認)」「Production配線・公開は禁止」、`..._USER_08.md:122`「本件は新しい選定優先順位を検証するTrialであり、Production採用・配線は禁止。」
- **「既存の文法選定・難易度・品質基準」の実体(候補)**:
  (a) Step A'': LLMが本文の構文を**数の上限なしで列挙・分類**(INV/CLEFT/CMP/FRONT/HEAVY/POSTMOD/SPEC/ELL/APPOS/OTHER)し、`teaching_value`=HIGH+`teaching_value_ja`・`front_kind`・`omitted_words`・`misread_*`・`basic_only=false`・単一span逐語検証で`eligible7`を判定(`FAMILY-Z-STUDY-TEXT-TRIAL-01/run_trial_07.py:180-194`)。
  (b) Trial-07の選定=コード側の固定優先順位(INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS、段落、出現順)で**最大1件・適格0なら0件**(2件目ロジックは意図的に廃止)。
  (c) Trial-08の選定=Tier1(INV以外の適格)→Tier2(適格なINV)→Tier3(0件)(`run_trial_08.py:24 select_tiered`)。
  (d) Step B: 選定1件の解説執筆(Trial-04同一Prompt)。(e) 基礎項目の除外=`basic_only`・FRONTの基礎/適格区分。対象はAdvanced(学習テキスト)。
- **含意**:
  (1) TOP 2は新たな選定ロジックではなく、(b)/(c)の順序で**適格集合の先頭2件**として自然に得られる(追加LLM callなし。Step A''の既存出力から決定論的に導出可能。ただし「2位の定義」[同一文の除外・同一クラス可否]は新仕様の細部=判断候補G-2)。
  (2) 「適格が無ければ0件=Part 2を出さない」は**Trial-07で既に仕様化された挙動**だが、Trial止まりでProduction承認は無い。ユーザー指示§3は「基準を満たす候補が無い場合は既存承認仕様を確認、未規定の自動省略ルールを独断で追加しない」と書く。**「承認済み」の根拠は現状Trial段階の規則のみ**。
  (3) Part 2のProduction codeは存在しない(`DESIGN_04.md:17`「Productionに存在しない」)。Step A''/Step B/Tier選定/Part 2描画/公開ページ組込みの新設を伴う=実質**Part 2のProduction配線そのもの**。
- **Part 2のProduction採用の明示承認が別途必要か(Fableが判断する材料)**:
  - 選択肢A「本指示がPart 2採用を包含する」: §3は「既存の文法選定・難易度・品質基準を維持」とだけ書き、Part 2の採用・配線を明言しない。ユーザーは同日の別指示でPart 2の配線を明示的に禁止しており、**その禁止を解除する明示文が本指示に無い**。包含と読むのは「承認範囲を要約で広げる」危険(CLAUDE.md禁止(1))。
  - 選択肢B「Part 2採用は別途明示承認が必要(推奨)」: Part 2の採用可否(学習価値閾値TV=HIGH・OTHER扱い・Tier内順位=`ADOPTION_NOTE_08.md` §3(a)(b)(c)は品質基準変更にあたりうるため承認要)をユーザーに確認し、確認後に文法部分を実装する。KP/単語解説部分は独立に先行実装する。
  - 設計は**B前提で文法部分を分離**する(DESIGN_01 §k)。

## 6. Family Y
- 正式Production入口なし。`er110_family_y_*`はDEV/Trial、`y_entry_point.json`に`production_reachable=False`(`er110_family_y_audio_trial_01.py:176`)、KP選定は共通module(`run_key_phrases(kp_backend="fulltext_p2")`)をTrial scaffoldが呼ぶ(`er110_family_y_text_trial_01_run.py:264`、`er110_family_y_persona_text_trial_01_run.py:281`)。OPEN-484に既に「Y Production化時の必須受入条件(a)〜(f)」を記録済み。→ **Y用Human Review配線は(g)としてOPEN-484の受入条件へ追記**(未実装をPRODUCTION_WIREDとしない)。
- 設計制約: **共有関数`sc.run_key_phrases`の既定動作を変えない**(Y Trialが既存どおり3件で動くこと・A/B/C無影響=27-7)。新工程は新module(opt-in)で入る。

## 7. Production到達経路と既定値(Grep)
- `kp_backend`既定は`strategy_l`(A/B/C)、X/Zは`fulltext_p2`を明示渡し(`run_theme_scaffold(kp_backend="fulltext_p2")` `er019…:608`)。新工程のflag/既定値: 承認済みのため既定ONだが、「Human不在の自動確定」は**明示指定時のみ**(DESIGN_01 §b)。
- 旧ルール候補: 固定「最大3件」の定数`KP_COUNT_MAX=3`(`er105:33`)は「確定数」として残し、候補数=`KP_CANDIDATE_MAX=8`を別定数にする。`er003_test_kp_fulltext_wiring_01.py:845-851`・`er105_kp_fulltext_selector_01_test_01.py:68,267`の`KP_COUNT_MAX==3`assertは確定数の意味で維持(改訂は最小)。

## 8. 判断候補・確認事項(Fable向け。USER_DECISION_REQUIREDの付与はFableのみ)
| ID | 内容 | 仕分け(27-3) |
|---|---|---|
| I-1 | 単語解説5件はPart 1(Advのみ)が対象。Standardは単語解説コーナー無し→KP3件のHRのみ。Part 1のStd拡張は新仕様 | D(解釈確認)。既存Part 1承認(`USER_05.md`)はAdvのみ・Std非拡張を明記 |
| I-2 | Prompt 2は一字一句固定(変更は明示承認)。TOP 8順位付けには文言変更(「3つ」→「8つまで順位付き」+理由)が必須 | B寄り(ユーザー指示がTOP 8を承認済み=文言は目的に必要な最小差分)。ただし「Prompt固定」規則上、最小差分の新Prompt(2-R)+sha固定+上位3件の品質同等性確認(小規模paid check)をFableが了承する形を推奨 |
| G-1 | Part 2のProduction採用の明示承認が別途必要か(選択肢A/B、§5) | D |
| G-2 | 文法TOP 2の「2位」定義(同一文を除く次の適格/同一クラス可否) | B(適格順序の機械的延長を既定) |
| G-3 | 適格0件時の「文法コーナー省略」はTrial規則のみ。Production化の承認 | G-1に含む |
| K-1 | 候補段階のGate適用範囲(canonicalization/gloss/CMUは候補ごと、Redundancy QAは候補全体で1回+選択集合の機械検査) | B(DESIGN_01 §a、Opus論点) |
