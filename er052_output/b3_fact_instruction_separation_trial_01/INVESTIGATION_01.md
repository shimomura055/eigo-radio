# 注: 本書は委任_03でOpus是正R3を反映済み(『Ledger段は文を追加していない』を訂正、space F-017は推定、semiconductor B3新規の理由は仮説と明記、『notes由来7件確定+1件推定』)。

# INVESTIGATION_01: B3「Selected Facts」へ指示・制約文が混ざった原因の調査(Phase 1、read-only)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 / 委任_01 / 2026-10-10
範囲: 読み取りと既存artifactの再解析のみ。課金API 0件、Production code/Prompt/CURRENT_SPEC変更なし、git操作なし。
再現: 本ディレクトリの `analyze_ledgers_01.py` `verify_ledger_provenance_01.py` `build_trace_5themes_01.py` `preview_armD_01.py` を repo root で `py -I` 実行(いずれもAPI不使用)。

## 0. 結論(先に)

1. 混ざった直接の原因は **B3生成Promptが「Factを簡潔にまとめた文章を自由に書け」と言うだけで、台帳の`notes_for_writer`(Writer向け注意書き)をどう扱うか一切指示していない**こと(er019 L68)。Writerは台帳を直接読まずB3 briefだけを読む(OPEN-237 (b)で確認済み)ため、B3 LLMが自己判断で一部のnotesを命令文のまま本文へ取り込み、一部は落とし、一部は自分で新しい注意文を作った。
2. 5問題テーマの指示・制約文は10件(Writer向け命令文)。内訳: `notes_for_writer`由来 7件確定(逐語3・言い換え4)+1件推定(space_weapons F-016付近の『適法性を断定しない』は未選定F-017のnotes転用と**推定**。逐語一致なし)、Verifierの曖昧メモ(`ambiguity_note`)由来 1件、Ledgerに対応文がなくB3 LLMが新規に作ったもの 1件。**[委任_03で是正]** `notes_for_writer`はResearcher draftからLedgerへ**無加工**(Stage R新規6テーマで100%一致)。ただしLedger段は決定論で、AMBIGUOUS factに`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`という**指示タグ**と、Verifier由来文(`ambiguity_note`)を付与する(`build_verified_ledger_text` L292-309)。したがって『Ledger段は文を追加していない』とは言えない。正常系(meta/byd/openai/streaming)の命令文は0件。
3. バグか意図された設計かの判定: **仕様化された設計ではなく、B3導入(2026-09-26)による経路切断の副作用**。B3導入前はWriterが台帳全文(notes込み)を直接読んでいた。B3導入後はWriterの唯一の入力がB3 briefになり、notesの受け渡し経路が仕様から抜け落ちた。ただしその後のFact Lock R0規則4とB3注記仕様v2は「限定文がニュース欄に混在する」ことを前提に書かれており、下流は現状の混在を吸収する形で承認されている(= 混在が既成事実化している)。
4. 台帳には既に欄が分かれている(`claim/scope/conditions/ambiguity/notes_for_writer`)。B3の自由記述が欄を混ぜ直しているだけなので、**LLM追加callなしの上流修正が可能**(DESIGN_01.md)。

## 1. B3生成経路の完全再構成

### 1-1 工程表(ファイル:関数:行 / モデル / 入出力)

| # | 工程 | 実装(ファイル:関数:行) | モデル(実測) | 入力 | 出力 |
|---|---|---|---|---|---|
| 1 | Researcher | `er019_family_x_entertainment_production_runner_01.py:run_research_and_ledger`(L91) → `er012_e_family_entertainment_two_level_runner_01.py:run_researcher_for_topic`(L179) → `er003_v1_en_direct_vfl_01_generate.py` `RESEARCHER_PROMPT_TEMPLATE`(L137)・`FACT_LEDGER_JSON_SCHEMA`(L82) | `vfl01.MODEL`(=`routing.WRITER_MODEL`、`er006_model_routing_contract_01.py` L48)。実測 `gpt-6-luna`(`stage_r/cost_by_theme.json`)。web_search有 | topic文 | `research_ledger/fact_ledger_draft.json`(各factに claim/scope/conditions/numeric_value/numeric_scope/date_or_period/causal_strength/ambiguity/**notes_for_writer**) |
| 2 | Verification | 同 `run_verification_for_topic`(L202) → `VERIFICATION_PROMPT_TEMPLATE`(L228) | 同上(web_search有) | draft JSON | `fact_ledger_verification.json`(fact_id/verdict VERIFIED・AMBIGUOUS・REJECTED/verification_notes) |
| 3 | Ledger text化 | `er003_v1_en_direct_vfl_01_generate.py:build_verified_ledger_text`(L279、欄の出力規則 L292-309) | なし(決定論) | draft+verification | `verified_fact_ledger.txt`。REJECTEDを除外。AMBIGUOUSのみ `ambiguity_note: {draft.ambiguity or verification_notes}`(L305)。`notes_for_writer`はdraftそのまま(L306-307) |
| 4 | B3 Storyline+Fact選定 | `er019_family_x_storyline_b3_fact_selection_01.py`: Prompt `USER_PROMPT_TEMPLATE`(L51)、schema(L90)、`run_storyline_b3_selection`(L209)、brief組立 `build_selected_brief_markdown`(L252)。runner側 `run_storyline_b3`(runner L141) | `vfl01.MODEL`。実測 `gpt-6-luna`、1 call、約50秒、¥0.38〜0.60(10テーマ平均¥0.50、`stage_r/cost_by_theme.json`) | topic + 台帳txt全文(全fact・全欄、notes込み) | `storyline_b3/selected_brief.md`(`## Storyline`+`## Selected Facts`)、`fact_selection_evidence.json`、`full_ledger.json` |
| 5 | (W-1)B3注記 | 別管理ID B3-ANNOTATION-AUTOMATION-TRIAL-01(Sonnet 5.5約¥15.7/記事)。仕様 `B3_ANNOTATION_SPEC_v2*.md` | LLM | brief+台帳 | `【事実N】`・`【中核/周辺数値】`付与版 |
| 6 | Writer R0(Fact Lock) | `er052_factlock_astra_e2e_runner_01.py:parse_brief_md`(L212)でStorylineとFactsに分割 → `er019_family_x_ja_writer_o_r1_r2_01.py:build_original_prompt`(L148)が `R0_PROMPT`(L52)の「テーマ：」行をStorylineに差替え、末尾に `"[ニュース]\n" + facts`(L161)を付加。Fact Lock規則は `er052_factlock_writer_trial_01_run.py:FACTLOCK_R0_BLOCK_HEAD`(L53) | `gpt-6-luna` | Storyline+Facts文字列のみ(**台帳は渡らない**。台帳が渡るのはJA Fact Check/must-fix時のみ) | R0本文 |
| 7 | R1/R2 | 同 runner `worker_new_astra`(L700) | `gpt-6-astra` | **前段の本文のみ**(briefも台帳も渡らない)。Fact Checkは台帳全文(notes込み)で実施 | R1/R2本文 |

重要な構造的事実:
- Ledgerの`notes_for_writer`は**欄としては既に分離**されている。混ざるのはB3 LLMが「簡潔な文章」を自由記述する工程4だけ。
- Writer R0が読むのはB3 briefのみ(工程6)。R1/R2はbriefを見ない。つまり briefの扱いが変わって影響するWriter側入力は **R0の「ニュース欄」だけ**。
- 工程4の出力schema `selected_fact_ids`(採用ID)は構造化されているが、briefの中身は自由記述の1文字列 `selected_fact_brief`(L117)で、fact_idとの対応は保持されない。

### 1-2 Prompt該当文の逐語引用

B3 USER_PROMPT_TEMPLATE(`er019_family_x_storyline_b3_fact_selection_01.py`):
- L68: 「5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章。冒頭にStorylineの1行を含める)を作成してください。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。」
- L78: 「- selected_fact_brief: Writerへ渡すSelected Fact Brief本文(Storylineの1行を含む)」
- L44-48 DEVELOPER_MESSAGE: 「…記事本文そのものは書きません。」
- **台帳のnotes_for_writer / ambiguity_note / scope / conditionsの扱いについての指示は、Prompt全体に1文もない。** Factと注意文を分けて出す指示も、混ぜてよいという指示もない。
- 「冒頭にStorylineの1行を含める」(L68)が、small_bag/openaiで `Selected Facts` 節の先頭に `Storyline：…` 重複行が残る原因(`build_selected_brief_markdown` L252-277は先頭が接頭辞なしでStorylineと完全一致の場合だけ除去)。

Researcher RESEARCHER_PROMPT_TEMPLATE(`er003_v1_en_direct_vfl_01_generate.py` L161、観点4):
- 「Sourceより強い因果表現(caused/produced/proved等)を**後工程のwriterが使わないよう**、causal_strengthとnotes_for_writerで明示する」
- L166: 「各Factについて…ambiguity・notes_for_writerを埋めてください」
→ `notes_for_writer`は設計上「Writerへの注意書き」として生成される欄(欄名もその意味)。

Fact Lock R0規則4(`er052_factlock_writer_trial_01_run.py` L67-71):
- 「ニュース欄に「〜ではない」「断定しない」とあることは守ってください。」

B3注記仕様v2 §2(`B3_ANNOTATION_SPEC_v2_ANNOTATOR.md`):
- 「限定する文(「ただし〜」「これは〜を意味しない」「〜とは書かない」「〜ではない」など)は、直前の主張の文と同じ事実に入れます」
- 「Selected Facts 節の中の `Storyline：` で始まる重複行、`素材:` で始まる行には、`【事実N】`を付けません」

### 1-3 SSOT上の該当仕様(Grep引用)

- `DECISION_LOG.md` L9573-9574 (NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01、2026-09-26): ユーザー確定事項(7)「LLM出力はJSON Evidence必須(…最終Selected Fact Brief)」(5)「B3の4テスト定義」(6)「Fact数目安3〜5」。**briefにnotes・注意文を含めるか否かの規定はない。**
- `DECISION_LOG.md` L20123 (OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01、2026-10-06) (b)「notesはtxtに常時出る/JA初回R0はB3 briefのみを読み台帳notesを直接見ない/**B3 promptはnotes転記指示なし**/must_fix・Checker後Rewrite・deviation checkには届く/EN生成・retryは台帳を見ない」(c)「notesだけでは確実にWriterへ届かない」。
- `docs/pm/b3_brief_structure_hypothesis_01.md` (OPEN-233-B3-BRIEF-STRUCTURE-HYPOTHESIS-01): 「fact_id記載・主体/対象/方向語の保持・notes折り込み規則・書式の指示は**なし**…言い換え・統合・Storyline行混入・書式は全てLLM任せ」。
- `CURRENT_SPEC.md`: B3の入出力形式(notes欄の扱い)を定める行は見つからず(Grep: `notes_for_writer` 0件、B3関連はL828 Entertainment生成方式行の概要のみ)。

## 2. 5テーマの混入文の逆追跡(1件ずつ)

詳細表は `trace_5themes.json`(各行にbriefファイル・行、台帳ファイル・行、台帳逐語、共通部分長、判定)。要約:

対象artifact: `er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01/<slug>/shared/{brief_original.md,ledger.txt,fact_selection_evidence_original.json}`(= stage_r出力と同一shaを確認。hormuz/streamingのbriefは `stage_r/<slug>/storyline_b3_v2`=B3再生成版と同一)。

| テーマ | 命令文(件) | 由来の内訳 | 備考 |
|---|---|---|---|
| semiconductor_earnings | 2 | ①B3新規 1(「因果関係を付け加えないこと」。Ledgerに対応文なし。B3自身の`fact_tests[].reason`(F2/F3/F6)に「因果関係の確認はない」旨あり=推論メモがbriefへ漏出した、という**仮説**。確認はしていない)②Verifier由来 1(F1の`ambiguity_note`=Verifierの`verification_notes`。Researcher draftのambiguityはnull) | 5 factが1段落(後に単一`【事実1】`)へ統合され、命令文2件がその中に入る。Storyline行にも「ただし…Ledger上確定できない」 |
| small_bag | 1 | MB-06 notes逐語(「「mini」と「micro」を混同しないこと。」15字一致) | `Storyline：`重複行が`Selected Facts`先頭に残存(Prompt L68由来)。記述文の限定1件(MB-01 conditions+notesの言い換え) |
| space_weapons | 4 (+Storyline内1) | F-001/F-003/F-015のnotesの言い換え3、F-016付近の「適法性を断定しない」は未選定F-017のnotes転用と**推定**1(逐語一致なし)。Storyline内「誇張せず整理する」はB3新規 | 22 fact中18がnotes命令形。採用5件に対し命令文4+1 |
| hormuz | 2 | HF-006 notes言い換え1、HF-009 notes逐語(24字)1 | 選定4件 |
| central_bank_mortgage | 1 (+記述文2) | F007 notes逐語(20字)1。記述文「政策の目的・見込みであり…確認ではない」はF003 notes逐語(19字、**欄は`notes_for_writer`だが内容は事実の確かさの限定=境界例**)、「全借り手の支払額ではない」はF007 scope | 6件採用、recheck_noteあり |
| (正常系)meta / byd_recall / openai_copyright / streaming_price | 0 | meta: HC-012 notes「「サービス全体を停止した」とは書かない」をB3が**記述文**へ変換して取り込んだ(命令文0)。byd: 台帳notesに命令形が約7件(推定)あるが**briefには1件も届いていない**(落とされた)。openai/streaming: 限定はFact本文(claim)由来 | |

5つの調査観点への回答(10件の命令文):
- (1) Research段階の原文に存在: 該当notesは存在する(8件)。semiconductor/central_bankはdraft JSONで逐語確認。旧凍結4テーマ(hormuz/space/small_bag/meta)はdraft JSON未保存だが、`build_verified_ledger_text`がnotesを無加工で出す規則(L306-307)であり、Stage R新規6テーマ(semiconductor/central_bank/byd/openai/streaming/inbound)で台帳notes==draft notesが100%一致(`ledger_provenance_check_01.json`: 52/52)。
- (2) Ledgerで追加された: `notes_for_writer`は**無加工**。ただしLedger段(決定論コード)が、AMBIGUOUS factに`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`の指示タグとVerifier由来の`ambiguity_note`(Researcher draftのambiguityが空ならVerifierの`verification_notes`、semiconductor F1)を付与する。文を作るのはVerifierのLLMだが、Ledger段が欄として出力する。[委任_03で是正]
- (3) notes_for_writer由来: 7/10確定(逐語3、言い換え4)+1件推定(未選定factのnotes転用)。
- (4) B3が新規に追加: 1/10(+Storyline内1件、+`Storyline：`重複行の構造問題)。
- (5) B3 Promptが要求: **要求していない**。ただし「簡潔にまとめた文章」「必要最小限のFactだけ」の自由記述指示が、台帳の欄区別を保持させる仕組みを持たない。

副次的な観察(命令文の混入以外の同根の症状。仕様変更ではなく事実の記録):
- notesは**選別なく確率的に取り込まれる**: BYDのnotes(命令形は正規表現推定で約7件)は命令文としては1件も届かなかった(例「「ブレーキが効かなくなる」とは言い換えない」)=Writerに届いていない。逆にspaceは採用5件に対しnotes言い換え3件が届く。「Writerに必要な制約が届く/届かない」は現状LLM次第。
- ledger txtは`VERIFIED`factのResearcher`ambiguity`を印字しない(`verify_ledger_provenance_01.py`: byd 6件、inbound 3件などdraftにambiguityがあるのにtxtに出ない)。これは今回の範囲外の別観察(新仕様候補として報告のみ)。
- B3 briefは台帳より短い(例: space 596字 vs 台帳claim 1,366字)。**B3が圧縮する過程で主体・対象の言い換えが起きる**(`b3_brief_structure_hypothesis_01.md`のhormuz「20%の掛かる先」ずれ)=混入と別に起きる品質リスクで、案Dはこれも解消する。

## 3. 設計意図の確認(旧設計か、副作用か)

証拠:
1. **Researcherの意図**: notes_for_writerは「後工程のwriterが使わないよう」明示するための欄(RESEARCHER_PROMPT L161)。当時(`er003_v1_en_direct_vfl_01_generate.py` `WRITER_PROMPT_TEMPLATE` L317-)は**Writerが台帳全文を直接読んでいた**ため、notes→Writerは台帳経由で直接届く設計だった。
2. **B3導入での変化**(2026-09-26、DECISION_LOG L9573-9575): Writer入力が「Selected Fact Brief」に置換され、台帳はWriterに渡らなくなった(Fact Check/must-fixのみ)。ユーザー確定事項(1)〜(13)にnotesの扱いはなく、Production実装者が書いたB3 Prompt(L68)もnotesに触れない。→ notesの経路は**仕様上未定義のまま切断**された。
3. **その後の吸収**: OPEN-233系(2026-10-06)が「B3 promptはnotes転記指示なし」「notesだけでは確実にWriterへ届かない」を事実確認し、転記を試す案(T0/T1/T2、「既存notes昇格+B3転記」)を未承認の新仕様候補として検討した。Fact Lock R0規則4とB3注記仕様v2は、混在した限定文を前提に規則化された(= 下流が副作用を既成事実として吸収)。
4. **判定**: 「Storytelling制御/Fact逸脱防止/数値制御/因果追加禁止」といった目的でFact欄に指示を同居させる、という**設計意図を示す記述はどこにも見つからない**(DECISION_LOG/CURRENT_SPEC/REPORT/B3 diversity trial記録をGrep)。したがって「意図された旧設計」ではなく「B3導入時の仕様の穴」。ただし**目的そのもの(Writerへ因果・範囲の注意を届ける)は正当で、Fact Lock規則4が依存している**ため、注意文を消すのではなく**別の欄・別の経路で確実に届ける**のが元の目的を保つ修正。

元の目的を失わずに欄だけ分離できるか: できる。台帳が既に「事実本文(claim/scope/conditions/ambiguity)」と「Writer向け注意(notes_for_writer)」を別欄で持つため、欄名による決定論分離が成立する。境界例(notesの中に事実の確かさの限定が入る: central_bank F003、small_bag MB-01、Ledger内部向け文言「Ledger上では必ず…」: hormuz HF-007)は存在する。→ 分離後もFact Lock規則4が読めるようWriter入力(ニュース欄)には制約ブロックを残す(DESIGN_01.md)。

## 4. 限界・未確認

- 旧凍結4テーマ(hormuz/space/small_bag/meta)のResearcher draft JSONは現存せず、「notesがResearcher出力そのもの」は規則と他6テーマの100%一致からの推定。
- briefはB3のサンプリング結果(同一台帳でも再生成で変わる: hormuz v1とv2で書式が異なる)。10件という件数は特定のB3 1回分であり、発生率の統計ではない。再現率はPREREGISTRATION_01.mdのControl再生成(各2回)で測る。
- 命令文の判定は手作業(brief文を台帳と目視で突き合わせ)。正規表現による自動検出は評価補助にとどまり、正本は`trace_5themes.json`。
