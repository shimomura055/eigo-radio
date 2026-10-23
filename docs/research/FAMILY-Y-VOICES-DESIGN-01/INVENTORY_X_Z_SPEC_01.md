# INVENTORY_X_Z_SPEC_01: Family X/Z 最新承認済み仕様の棚卸し(Family Y設計の継承元)

管理ID: FAMILY-Y-VOICES-DESIGN-01 委任_01A / 2026-10-23(JST) / DESIGN/RESEARCH ONLY(read-only・API費用0・Production/Prompt/SSOT変更なし)
ユーザー指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`(本委任文: `..._委任_01A.md`)
旧Family B Voices仕様の棚卸しは並行する委任_01Bの成果物(`INVENTORY_OLD_B_VOICES_01.md`、本書では扱わない)。X/Y接点の既存記録だけ§8-3に参照として載せる。

## 0. 読み方(先に必ず)

- 事実=SSOT/コードを実際に読んだ内容。出典は`CURRENT_SPEC.md:行`(以下CS)/`OPEN-nnn`/`ファイル:関数`。出典が確認できない数値・状態は「未確認」と明記。仮説は「仮説」と明記して事実と分ける。
- Status語彙: `APPROVED_FOR_PRODUCTION`(ユーザー承認済み・配線は別)/`WIRED_PENDING_FABLE`(配線済み・Fable受入前)/`PRODUCTION_WIRED`(Fable判定またはユーザー宣言済み)/`WIRED_FIRE_UNOBSERVED`(配線済み・自然発火未観測)/`DECIDED`(旧語彙の決定済み)。`VALIDATED`はTrial評価でありProduction仕様ではない。`PRODUCTION_WIRED`はFamily別に判定される(PM_GOVERNANCE 28-1運用4)。
- 本棚卸しの「現行」=2026-10-23時点のSSOT。CURRENT_SPEC内には新旧記述が併存し、旧記述は削除されず履歴として残っている。**§13に「旧と現行を取り違えやすい点」を一覧化した(最重要の読み方ガイド)**。
- Level名: Standard=`a2`(日本語解説+やさしい英語)、Advanced=`b1b`(英語解説)。ディレクトリ・コードは`a2`/`b1b`。
- 名称衝突注意: Xの「Voice」はTTSの声(Aoede/Charon等)、Yの「Voice」は人物(1〜3)。本書では「TTS Voice」と「Voice(人物)」を区別する。

## 1. Research / Fact Ledger / Fact Safety

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| Research(web検索) | テーマ文→`gpt-6-luna`+OpenAI web_search toolでFact候補(claim/scope/conditions/numeric/date/causal等)を収集。Ledger未生成時のみ実行(あれば再利用)。`PRODUCTION_WIRED`(Family X) | CS:1175(経路図)、`er006_model_routing_contract_01.py:47` | `er019_family_x_entertainment_production_runner_01.py:98 run_research_and_ledger` → `er012_e_family_entertainment_two_level_runner_01.py:183 run_researcher_for_topic` | 事実収集の対象は「事実」。Voicesの主観(体験・価値観)はResearch対象外で、旧Bの思想「Research is backstage」と整合。Voice人物の「立場の材料」となる統計・制度をResearchが拾う設計かは未設計(後続) |
| Ledger検証 | 別call(web_search付き)でFactごとにVERIFIED/AMBIGUOUS/REJECTEDを判定。REJECTEDは除外。AMBIGUOUSは`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`として保持。検証結果が無いFactは安全側でAMBIGUOUS | `er003_v1_en_direct_vfl_01_generate.py:279 build_verified_ledger_text`、`er012...:206 run_verification_for_topic`、runner `:98-146` | 同左 | 事実台帳は共通形式を使うのが自然。旧B系Ledger形式は非互換(OPEN-219、§8-3) |
| B3 Storyline+Fact選定 | LLM 1 call(`gpt-6.1-sol`、routing key `FAMILY_X_STORYLINE_B3`)で(1)中心Storylineを1つ決定(2)1行明示(3)全Factに4テスト(削除しても筋が分かるか/因果に使うか/「なぜ」に必要か/面白い・具体的だけで残していないか)(4)採用/除外(5)最小Selected Fact Brief。`PRODUCTION_WIRED`(2026-10-11 Sol統一) | CS:1175,1165-1169(E案更新)、4テスト逐語=`er019_family_x_storyline_b3_fact_selection_01.py:40-44` | 同module `USER_PROMPT_TEMPLATE`、runner `run_storyline_b3`(`:148`) | **衝突し得る点**: B3は「記事として一本化しやすい中心Storylineを1つ」決めて最小Factに絞る。Yは3つの異なる視点(Storylineが1本とは限らない)。Factを「3Voice共通の前提」にするかVoice別の材料にするかが論点(設計は後続) |
| B3採用Fact下限2件 | `[VERIFIED]`のみ算入で2件未満なら再評価1回、なお2件未満はSTOP(`B3MinFactsStop`)。`APPROVED_FOR_PRODUCTION`・コード配線済み(`CODE_WIRED_TESTED`)・PRODUCTION_WIRED判定はFable側(OPEN-420、CS:1179) | CS:1179、runner `:216 assert_b3_min_verified` | 同左 | 共通機構。Yでは3Voiceに対するFact数の下限は別論点(仮説: Voice別にFactを割り当てるなら2件下限では不足し得る) |
| 決定論B3 producer(数値注記) | LLM 0。D-det v2+assemblerでSelected Brief中の数値に【中核数値】【周辺数値】印を付与。`rules_sha256=3b4b7fdf…`(2026-10-21是正後)。入力契約V1〜V10はfail-closed。`PRODUCTION_WIRED` | CS:1175 | `er053_b3_deterministic_producer_01.py`、`er053_b3_annotation_contract_01.py` | 数値の扱いはXの根幹(§4)。Voiceが数値を語るか否かは設計論点 |
| 中核数値の丸め判断 | Family Xのみ。`gpt-6-luna`(effort low)が1記事1callで【中核数値】のEXACT_REQUIRED/APPROXIMATE_OKを判断、決定論V1〜V9を通った概数だけWriterへ。**Zは到達しない**(Isolation test固定)。`PRODUCTION_WIRED`(2026-10-22 Fable、実走=run_pp_02、OPEN-437) | CS:2870節 | `er095_b3_core_number_rounding_01.py`(flag `B3_CORE_NUMBER_ROUNDING_ENABLED`)、runner `:264` | 承認原文が「Family Xのみ」=Y適用は別判断になり得る(**区分D候補、要確認**) |
| 未確定点の扱い | Writer R0のFact Lock規則3・4: ニュース欄に無いことは書かない、「〜かどうかは分かっていない」は可、推測で埋めない、確かさ(提案/決定)・範囲を強めない、「〜しなかった」「初めて」等の断定禁止。ただし未確定点を本文で「明示する」義務は規定されていない(2026-10-22 2記事E2Eで観測: 記事Aは受賞作未決定・審査員未確定を本文で明示せず。誤断定はなし) | `er053_family_x_factlock_ja_writer_01.py:67-100`(FACTLOCK_R0_BLOCK_HEAD)、`docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md` §2-1 | 同左 | Voiceが主観的立場から語る場面で未確定点を断定してしまうリスクと直結(原文§6-5)。Xの規則は「世界を断定する文に事実タグ、主観文は番号不要だが新事実断定は禁止」(規則1・2)。体験談の創作がこの線引きで足りるかは§11-12 |
| Risk Flagger(RF) | 完成英文×完全Ledgerに4条件(Luna A3/A4・Gemini 3.5 flash-lite A3/A4)、OR統合。**非Blocking**(合否判定・書換・RF起点の自動retryなし)。両Levelで実行、Review Queueへ保存。`PRODUCTION_WIRED`(2026-10-11) | CS:1185-1192 | `er053_risk_flagger_production_01.py`、`er053_review_queue_01.py` | **Zは対象外**(2026-10-17ユーザー決定、CS:1677表)。Y列は「未定」。採否は設計で要判断(Yは事実を扱うためZより近い、仮説) |
| 旧Fact Checker/Deviation/案B | **X Productionから撤去済み**(2026-10-10)。W-1 Writer+RFに置換。`vfl01.run_deviation_check`+`DEVIATION_PROMPT`は旧A/B/C用に残置 | CS:1194 | 撤去表 `docs/pm/delegation_log/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_08.md` | **旧B系の「Analytical Leakage Check」(`er012_b_family_voices_writer_generic_01.run_analytical_leakage_check_3v`)はX経路に存在しない**。Yで必要ならBからの継承設計(01B領域) |
| Concreteness Control AN3-T0 | 数字・時刻・固有名詞の定性的抑制。実際にR0へ送られるのは第2文(固有名詞)+Fact Lock数字規則5(承認Trial `er052`と同一)。`PRODUCTION_WIRED`(2026-09-29)。R1/R2のreminderは削除済み | CS:894節、:1181末尾の注記 | `er053_family_x_factlock_ja_writer_01.py:134 build_r0_block` | 「Fact is context, not script」(OPEN-217の記述)と方向が一致。Yの再利用候補 |

## 2. Writer・記事構造・CEFR・語数・時間尺

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| 生成パイプライン | **日本語を先に書く**: B3→Writer R0(Fact Lock)→R1→R2(いずれも`gpt-6.1-sol`、effort high、R2入力=R1 raw)。R1/R2指示は「事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度」。→Advanced英訳(忠実英訳)→Advanced RF→Standard調整→Standard RF。`PRODUCTION_WIRED` | CS:1165-1183、`er053_family_x_factlock_ja_writer_01.py:64`(USER_TMPL)、`:36-44` | `run_w1_writer`(`:321`)、`er019_family_x_entertainment_production_runner_01.py:445 main` | **最大の構造的衝突**: X経路は日本語原稿→英訳→簡易化の三段。Voice人物の独立性が日本語段階で決まり、英訳・簡易化で保たれるかが論点。また既往Trial(OPEN-217)でX流R1→R2(エンタメ性up)はVoice文脈でFact言い直しを悪化させた(§8-3) |
| 日本語原稿の長さ | R1/R2指示で800〜1000字程度(目安・Gateなし)。実測2記事: 876字/837字(【】タグ除去・空白除去後) | `er053...:64`、実測=`er019_output/{prix_pascal_ai_novel_prize,tesla_spacex_merger_talks}/run_nws_01/ja_writer/revision2.md` | — | Yは5パート構成で長さ配分の再設計が必要(後続) |
| 記事構造(X) | Title+本文(見出しなし・段落のみ)+`## In one line`。本文を**段落境界のみで決定論的に3分割**(part1/2/3、語数均等化の全探索)。段落数<3は1回だけmust-fix再生成、なおダメならSTOP。`###`見出しは廃止(2026-09-29 W1)。`PRODUCTION_WIRED` | CS:1405(項目6)、1332(項目1) | `er003_v1_n3_01_scaffold_generate.py:188 split_family_x_article_text_v2`、`er019_family_x_audio_plan_01.py:282` | **Yの5パートに直接使えない**(3分割・In One Line前提)。段落境界での決定論分割+statusによる再生成という方式は流用可。Voice境界を段落で判定するか構造マーカーを持たせるかは設計論点。旧`###`2つ前提のsplit関数は後方互換のみ残置 |
| Advanced(b1b)英訳 | 日本語記事の**忠実英訳**(同一段落数・同順・追加/削除なし・見出しなし)。語彙ルールv2(約12,000位超は原則平易化候補、例外A〜D)併用。長さ指定なし(日本語の長さに従う)。`PRODUCTION_WIRED`(W1) | `er003_v1_n3_01_advanced_adaptation_generate.py:508-540,674 generate_family_x_faithful_translation`、語彙v2=`:120-190` | 同左 | 旧Advanced用の「280〜420 words・`###`2つ・In one lineは1文」(`ADVANCED_CONTRACT_SUFFIX`)は**Xの忠実英訳経路では未使用の旧契約**(§13)。翻訳指示は「editorial rewritingでない」ため、一人称の語り口は日本語段階で決まる(仮説) |
| Standard(a2)調整 | Advanced英文を入力に「CEFR A2向けに書き直し」。平均文長9〜11語目安、1文1アイデア、約6,000語ライン+例外3種(固有名詞/推測容易な派生語/日本語定着語)、Storytelling保持、追加Fact禁止、段落構造維持、In one lineは同文数維持。`PRODUCTION_WIRED` | `er003_v1_n3_01_standard_a2_generate.py:506-530`、語彙=`:107-137` | `generate_family_x_standard_a2_no_heading`(`:541`) | A2簡易化でVoiceの人物らしさ(口調・迷い)が平板化するリスク(仮説)。簡易化指示にVoice別トーン保持の文言はない |
| 英語語数・文長の規定値 | **Xに英語語数の正式規定値はない**(忠実英訳なので日本語長に従う)。文長目安のみ: Std平均9〜11語、In One Line各12〜22語(目安)。実測2記事(2026-10-22 E2E): Std 434語/385語、Adv 446語/416語(parts.json total、In one line含む)、段落8/7。**Z**は目標400語・目安330〜470語(WARNのみ、再生成・STOPなし、2026-10-19ユーザー指示④) | `er019_output/*/run_nws_01/{a2,b1b}/parts.json`、CS:1626、`er062_family_z_writer_01.py:51-53` | — | Yの語数・尺は新規設計が必要。**ユーザー希望の総尺は原文に記載なし(未確認)** |
| 時間尺 | 実測(2記事E2E): Std 299.6秒/278.7秒、Adv 286.0秒/272.6秒(約4.5〜5分)。規定値は無い | RESULT_01.md §1 | — | Yは5パート+Preview/Comment/KP/In One Lineで尺が増える可能性(仮説) |
| Std/Adv関係 | StdはAdvanced最終稿から派生(英訳→簡易化)。`a2_derived_from_advanced_sha_mismatch`警告は常時偽陽性の観測専用(OPEN-253) | CS:1175、`er019_family_x_audio_production_runner_01.py:2489 _derived_sha_warning` | — | Yも同方式継承が原則(分類A) |
| Family Zの記事構成(参考) | Seed(原作)方式。Adv英語を新規作成(`gpt-6.1-sol` R0→R1→R2)→Std調整。Story 3分割+Comment3つ、In One Line/Comment4なし。Std Preview/CommentはAdvanced方式の日本語適用。RFなし。人物名・原作保持Validatorは撤廃、品質はWriter Prompt改善で対応(Checker/Validatorを安易に増設しない=Z全体方針) | CS:1607,1617,1621,1626 | `er062_family_z_writer_01.py`、`er026_family_z_fiction_production_runner_01.py` | Zの「Checker増設を抑えWriter Promptで対応」は、原文§6「新Validatorを増やさない」と同方向=Yの設計方針の先例 |

## 3. Preview・Comment・Key Phrase・In One Line・日本語タイトル

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| 音声順序(X) | Intro→Welcome→Topic intro→(Std:日本語タイトル)→Notification1→Preview intro→Preview→Notification2→Key phrases intro→Key Phrase×N→Notification3→Full story intro→Comment1→本文1→Comment2→本文2→Comment3→本文3→Comment4→In One Line→Outro。Point One/Two・見出し読み上げ・Point通知音は使わない(SE-1 CLOSED) | `er019_family_x_audio_plan_01.py:282-340`(`FAMILY_X_*_SEGMENT_ORDER_V2`)、CS:1332,1405 | 同左、timeline=`er019_family_x_audio_production_runner_01.py:1684,1950` | Yの5パート(Lead/V1/V2/V3/Tension+Closing)を「本文1〜3」にどう対応させるかが最大の接続論点。Comment数・位置はパート数に依存。ユーザーはPreview/Comment/KP/In One LineをXの最新承認仕様基盤と指定済み(原文§2.1) |
| Preview | Std=日本語(Aoede、Style S3)、Adv=英語(Charon、Style E1)。役割文は既存`a2gen.PREVIEW_ROLE`/`b1s.PREVIEW_ROLE`(Comment1・2本文を埋込)。Std A2 Previewは2文程度・80〜110字が目安(Gateなし)。`PRODUCTION_WIRED`(E1/S3: 2026-10-17) | CS:1677表(E1/S3行)、CS:2050、`er019_family_x_audio_production_runner_01.py:273-340` | scaffold: `run_family_x_b1_scaffold`/`run_family_x_a2_scaffold` | Preview原則(後続の答え・詳細数字・結論を先出ししない)はCross-level共通(CS:1716)。Voice 1〜3の立場をPreviewで先出ししすぎない設計が必要(仮説) |
| Comment1〜4 | C1=次に聞く焦点(答えを言わない)、C2=前半回収+次の問い、C3=ここまでの核心整理+第3部への橋(結論は先に言わない)、C4=全体の意味回収+In One Lineへの橋(In One Lineの文数を断定しない)。C1/C2は既存role無改変、C3/C4はX専用role(Point前提除去)。出力に"Part 1"等の内部ラベル禁止。Std=日本語(Aoede)、Adv=英語(Charon)。`PRODUCTION_WIRED` | `er019_family_x_audio_plan_01.py:181-236`(FAMILY_X_*_COMMENT_3/4_ROLE) | `er019_family_x_audio_production_runner_01.py:273-340` | C3の役割文は「第1部・第2部を聞き終わり第3部へ」と**3分割を前提**。Y用にCommentの役割文・context構成を作り直す必要が確実にある(新規Prompt設計=区分D相当、役割の型自体はX準拠) |
| Key Phrase選定 | **全文選定(Prompt 2逐語、sha256 a12896f4…)・各レベル最大3件**(`gpt-6-luna`)。後段: canonicalization(基本形化のみ許容)・gloss再整合・Redundancy QA(2件未満skip)・X/Z共通の外側retry(通算3回、STALE退避)。**M2P0/DB Hybrid/Strategy L fallback/Topic枠(4+1)はX/Zで撤去**、選定失敗はfail-closed。`PRODUCTION_WIRED`(KPFT、2026-10-22 Fable受入、OPEN-454) | CS:1987-1992、`er105_kp_fulltext_selector_01.py` | `er003_v1_n3_01_scaffold_generate.py:351 _run_key_phrase_selection_fulltext`、`:705 run_kp_with_outer_retry` | 構造非依存で丸ごと継承可(分類A)。Voiceの口語・慣用句が多い本文でのKP品質は未検証(仮説) |
| KP: CMU辞書登録語のみ | 構成する全英単語がCMU発音辞書に登録済みであること。M1=選定gate、M2=canonicalization後再確認。最終attemptでCMU未登録だけが原因ならそのitemだけ除外して確定(shortfall)。`PRODUCTION_WIRED`(X/Z、Fable受入2026-10-23、OPEN-458) | CS:1993 | `er108_kp_cmu_lexicon_gate_01.py` | 共通・自動継承 |
| KP音声: 3-ASR多数決 | KP英語phraseのみ: Primary(OpenAI)/Secondary(Azure)/Whisper(local、割れた時だけ)の2/3でPASS。S+WはPASS_WITH_WARNING(事後試聴)。Azure/Whisper障害は技術STOP。値・否定の保護差は票に使わない(OPEN-458①)。`PRODUCTION_WIRED`(X/Z、2026-10-22) | CS:2923節 | `er104_kp_three_asr_vote_01.py`、`er104_kp_vote_reuse_01.py`(rollback `KP_WHISPER_TIEBREAK_ENABLED`) | 共通。blurt(語末t音)のように「ASR 2/3 PASSでも人間には聞こえない」限界が既知 |
| KP音声構造 | Std=英語→日本語意味→英語、Adv=英語→英語解説→英語。最後の英語phraseは最初と同一音源(Store再利用)。Style: KP英語=K2、Std日本語意味=P8-KP、Adv解説=P7。KP英語は`KEY_PHRASE_TOTAL_MAX_ATTEMPTS=4`(MINIMAL2+ENGLISH_LOCK2)の唯一の「TTS3回」例外、KP解説は3回。`PRODUCTION_WIRED` | CS:1995,2029,1677表,2837 | runner `:1117 _generate_key_phrase_segments_b1`、`:1459 ..._a2`、`er019_family_x_kp_en_k2_store_01.py` | 共通。KP日本語意味の人称一般化はX/Z/Y共通module(`er003_key_words_gloss_alignment.py`)としてY名指しで設計済み(CS:1630付近) |
| In One Line | **基本2文、必要時のみ3文**(条件・ヘッジ・第2の本質点がある場合)、各12〜22語を目安、新規Fact・結論追加禁止。Adv/Stdとも同文数。TTS=Aoede。Zには設けない(Z-3はsupersede)。`PRODUCTION_WIRED`(2026-10-16) | `er003_v1_n3_01_advanced_adaptation_generate.py:552-589`、CS:1215-1259(09:00判断)、1266(Fable判定)、1677表末行、1607(Z) | `generate_family_x_in_one_line`(`:752`) | **Y衝突点**: Yの最終パートは「Tension+Closing」(独立Closing廃止)。In One Lineを維持すると結びの重複(原文§6-4「VoiceとTension+Closingの論点重複」と同種)に注意 |
| 日本語タイトル(Std) | Stdのみ`japanese_title` segment(日本語記事のタイトルから導出)。Style=J3(2026-09-28 APPROVED、09-29 Fable Gate 3) | runner `:150 derive_japanese_title`、CS:1842節 | 同左 | 共通 |
| 可変Role Styleの現状 | 既定profile `fx_20261017`が6role(FULL_STORY=PD06/SUPPORT_JA=S3/PREVIEW=E1/KP_EXPLANATION_EN=P7/KP_EN=K2/KP_JA_MEANING=P8-KP)を固定。それ以外(japanese_title=J3、topic_intro/in_one_line/Adv commentはベースrole style)は`FAMILY_X_ROLE_STYLE_EN`定数。J3/E2のうちPreview/Comment/Full Story/KP日本語は後続承認で置換済み | `er019_family_x_style_profile_01.py:102,187`、`er033_tts_flash_lite_family_x_styles_01.py:41-49` | 同左 | Style profile機構はXとZで別(X=profile固定記録、Z=定数参照+drift test)。Y導入時のX/Z/Y横断profileエンジン化の要否はOPEN-415に起票済み |

## 4. 数字処理・自然な音声表現

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| Writer側の数字規則 | 数字は【中核数値】(B3 producerが付与)だけ使用可・書き方はニュース欄の表記のまま・本文では事実番号タグ必須。【周辺数値】は書かない(数字を省いて述べるのは可)。「大きく/急に/多数」等で大きさを言い換えることだけを禁止 | `er053_family_x_factlock_ja_writer_01.py:90-100`(規則5) | 同左 | 主観的語りで数値に触れる場合(例「3人に1人は〜」)に規則5が全面適用か、Voiceは数値を言わない運用かが未定義。原文§2.3「検証可能な数値・制度・他者の具体的行動を創作しない」と整合する方向だが細部は設計 |
| Spoken-first Number Treatment | Ledgerは常にexact fact保持、語りは精度に意味がない数字を丸め/概数化/方向化してよい(2軸分類)。スコア・日付・記録・安全閾値等はEXACT_REQUIRED維持。`DECIDED`(2026-08-17)。現行は決定論B3 producer+丸め判断(Xのみ)が実質的な担い手 | CS:1731、CS:2870節 | — | Y側の担い手は未定(丸め判断はX限定の承認) |
| ASR値ガード | 数値・単位は表記ではなく値で比較(5値NO_VALUES/EQUAL/DIFF/AMBIGUOUS/UNKNOWN)。三人↔3人=同値、三人↔四人=異値。複合序数・`60 %`の表記揃えは2026-10-22不具合是正。`PRODUCTION_WIRED`(AUW、X/Z) | CS:2831 | `er078_asr_value_guard_01.py` | 共通 |
| TTS記号正規化 | 4層(Prompt予防→Writer Validator→TTS直前の決定論Normalizer→未変換記号でSTOP)。波ダッシュ→「なになに」等。canonical本文は変更せずTTS直前のみ処理。`PRODUCTION_WIRED`(全Family共通、2026-09-27) | CS:2214節 | `er003_audio_tts_asr_safety.py` | 共通。W-1にはR0/R2の音声化禁止記号QA(各1回再生成→STOP)が組込み済み |
| 数字・記号読み上げの事故実績 | Flash-Liteで「Act One/Two/Three」のdigit読み(再現)→既存Local Rewriteで自己解決。Azure ITNが`one's`を`1's`と数値整形(OPEN-456 F3。KP投票は保護差を票に使わない仕様に変更済み) | CS:1757(Flash-Lite節)、CS:1987,2933付近 | — | 数詞・序数を含むVoiceの体験談で再発し得る(仮説) |
| 固有名詞の読み | Pronunciation Ledger+TTS Pronunciation Hint(spoken text本文は変更しない)。語境界一致化(surplus/minister誤爆是正)。`PRODUCTION_WIRED`(2026-09-27)。Stage 1(否定記録・統一lookup・一般語は調査省略・HR根拠階層・出典ページ照合[弱い確認]): `PRODUCTION_WIRED`(条件付き、Perplexity枠切れ401、UDR #134) | CS:2305節、2951節 | `er006_pronunciation_ledger_01.py`、`er097_pronunciation_supply_stage1_01.py` | 共通。人物名をVoiceに付ける場合は固有名詞の読み解決対象。**Zの外国人名ルール(First/Last一方のみ)はZ固有でCheckerなし(Writer Prompt側に降格)**。Y人物名の方針は未設計 |
| 固有名詞の発音不一致=アラーム受理(PNAP) | 発音不一致だけではProductionを止めずHRにも回さず、条件(Primary NG・全diffがentity_like・固有名詞根拠・類似度≥0.40等)を満たすとPASS_WITH_PRONUNCIATION_ALARM(追加API0)。先例=Khaite→Kate(X実発火1件)。供給は初期0件。`PRODUCTION_WIRED`(X)・`WIRED_FIRE_UNOBSERVED`(Z、受入時期=UDR #154) | CS:2962節、OPEN-450 | `er103_proper_noun_alarm_policy_01.py`(`APPROVED_SCOPES={"X","Z"}` `:42`)、`er103_pronunciation_tts_supply_01.py` | **コード上のscope限定リテラルがX/Zのみ**(`er103...:42`、`er109_xz_scope_01.py:25`)。Yはscope追加のコード変更が必要(T13)。PM_GOVERNANCE 28-1運用7(新規Familyは既存共通承認仕様を最初から配線)に基づき新承認不要の可能性が高い(Fable判断) |
| M1複数発音候補/多語同音救済/表記違い同音(er109) | M1: `APPROVED_FOR_PRODUCTION`・配線済み・PRODUCTION_WIRED未宣言(CS:2813)。多語同音救済(`byUs`⇔`buy us`): `PRODUCTION_WIRED`(X/Z、2026-10-22、OPEN-439)。**er109(表記違い同音の包括対策): `APPROVED_FOR_PRODUCTION`・X/Zのみ有効・`WIRED_PENDING_FABLE`(2026-10-23、OPEN-459)**=本棚卸し時点でFable受入前 | CS:2813,2857,2967 | `er006_m1_multi_candidate_01.py`、`er094_multiword_homophone_01.py`、`er109_*.py` | er109は当日配線で未受入=Y継承対象に入れる前に最終Statusを確認(未確認事項) |

## 5. TTS・ASR・音声品質検査

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| TTS model | `gemini-3.8-flash-lite-tts`(`speech_metadata`構造化方式、routing key `FAMILY_X_FLASH_LITE_TTS`)。承認済み正式backend=`speech_metadata_flash_lite`(CLI既定)。legacy(structured_separation)は`--allow-legacy-backend`の明示が必要。実行方式のコード既定はBATCH(環境変数`TTS_EXECUTION_MODE`、実運用設定は未確認)。Z Dialogueのみ`gemini-2.5-pro-preview-tts`(run_e2e_03実測) | CS:1757、`er006_model_routing_contract_01.py:119`、runner `build_arg_parser`(`:2337`)、CS:1677表下の委任_17箇条、`er006_batch_tts_wiring_01.py:68-85` | `er033_tts_flash_lite_*` | 共通 |
| TTS Voice(声) | Std=Aoede単独(Narrator、日本語Preview/Commentも同じ)。Adv=Aoede(Full Story/In One Line/KP英語)+Charon(Preview・Comment・Welcome等の案内系)。実測: AdvでAoede 4+Charon 6 segment。固定フレーズ(welcome等)はMaster Audio Store再利用(TTS 0) | `er019_family_x_audio_plan_01.py:246-297`、RESULT_01.md §4、CS:1902 | 同左 | **Y最大の音声論点**: 3人のVoice(人物)を声で区別するか(Narrator一人か)は原文に指定なし。先例=Zの登場人物Voice正式表(男女独立5+5、初出順割当、循環、Narrator=Aoede・Adv補助=Charonは別枠、決定論関数`assign_dialogue_voices`、2026-10-23ユーザー最終決定、CS:1563)。人物別Voiceは技術的に可能だが新設計=区分D |
| Style(role別) | `fx_20261017`: PD06/S3/E1/P7/K2/P8-KP(sha256は`audit/style_profile.json`と`er019_family_x_style_profile_01.py`)。Std英語Narrationは+生成後6%減速(`PRODUCTION_WIRED`)。名称衝突: Coffee限定の旧「P8(Full Story)」とKP日本語意味の「P8-KP」は別物 | CS:1264,1677表,1259(訂正) | 同左 | Y用Styleは未定(1677表のY列「未着手」)。Voice別Style(口調差)を持たせるなら新規設計 |
| ASR構成 | Primary=OpenAI `gpt-4o-mini-transcribe`、Secondary=Azure Speech STT、ローカルWhisper(small int8)はKP英語phraseの決選票のみ(2026-10-22 KP3Vで「Whisper不採用」をKP限定で上書き)。UDR #136(Primary/Secondary維持・Whisper全面導入せず)は本文等で引き続き有効 | CS:2828(追記・上書き注記)、2923 | `er078_asr_unified_judge_01.py`、`er006_asr_provider_routing_01.py` | 共通 |
| 統一ASR判定(AUW) | 基本フロー: TTS→Primary→NGならSecondary→両NGなら再生成(通算最大3回)→Local Rewrite(英語5role)またはHR Lock。Primary NG・Secondary PASSはPASS_WITH_WARNINGで自動採用・事後試聴リスト登録(非ブロッキング)。保護差(数値・否定)はSecondary不呼出で次slot。`PRODUCTION_WIRED`(ユーザー承認2026-10-16、原文に「Family Yは将来の開発対象。Yの開発時に正式配線」と明記) | CS:2822節、2827 | `er078_*`、`er006_secondary_asr_01.py` | Y配線は既決(区分A) |
| 音声品質検査 | ratio/ASR/値ガード/否定保護/disfluency QA/repetition QA(英語本文segment限定)/Connected Speech Eq層/多語同音/PASS_WITH_WARNING registry(事後試聴リスト、非ブロッキング)/HR Lock(再runは`approve_regenerate`まで0 API)/Audio Validation Gate(Assembly前) | CS:2112,2121-2122,2827 | `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate` | 共通。disfluency/repetition QAは「英語本文segment限定(`full_story_part1/2`等のsegment_id固定)」の旧承認範囲(CS:2122)。Y用segment_idを導入するとQA適用範囲から漏れる危険(T8) |
| Local Rewrite(英語5role) | Full Story/Comment/Preview/Topic intro/In One Lineのみ。Heading Readout/KPには適用しない。3NGでRewrite(Natural English QA、Luna 1 call)。採用後は書換え後文面を正解として再判定。Z Dialogue clipは`full_story_part{n}_c{k}`でFULL_STORYに解決 | CS:2838、`er020_tts_retry_local_rewrite_01.py:125 resolve_narrative_role` | 同左 | **segment_id→roleの解決がハードコード**(full_story_part1/2/3、comment_1〜4等)。Yが`voice_1`等の新IDを導入するとConnected Speech・Local Rewrite・QAの対象外になる(要拡張) |

## 6. retry / fallback / regeneration / resume

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| テキスト側のretry | 技術retryのみ(API失敗・JSON不正)。段落数<3は1回だけmust-fix再生成(Advanced/Standard対称)。W-1の音声化禁止記号: R0は検出時1回だけ再生成、R2は同一R1 rawで1回だけ再実行、残ればSTOP。RF結果起点の自動retry/Rewriteなし。**内容を理由にしたretry(旧Fact Check must-fix)は撤去**。B3最低2件は再評価1回 | CS:1179,1181,1194 | `er053_family_x_factlock_ja_writer_01.py` | 原文§6-6「検査や書き直しを反復しても構造起因NGが解消されない」の防止方針と一致(内容NGで反復再生成しない設計)。Y用に内容系ゲートを足す場合はこのfail-closed/回数上限思想との整合が必要 |
| KP選定の外側retry | X/Z共通・通算3回、各周の開始でSTOPセンチネル確認、失敗attemptの成果物は`keywords_canonicalized.STALE_attemptN.json`へ退避。除外句の累積(OPEN-456 F1)、全候補除外は`OUTER_RETRY_EXHAUSTED`でfail-closed | CS:1989,1991 | `er003_v1_n3_01_scaffold_generate.py:705,652` | 共通 |
| TTS/ASRのretry | 同一segment通算最大3回(attempt3の直前のみ固定600秒cool-down)、KP英語4回、KP解説3回、JAはLocal Rewriteなし→HR Lock。減速後判定も通算3回を共有する外側ループ。最終slot NGはHR Lock(再runで0 API) | CS:1837,2837 | `er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS` | 共通 |
| fallback | KP英語: MINIMAL→ENGLISH_LOCK。shell固定segmentのfallbackは短いstyle。Standard JA SUPPORTのminimal fallbackはM3 `JA_FALLBACK_USED_OR_UNKNOWN`でBLOCK。旧5件KP経路へのfallbackは存在しない | CS:1990,1266 | 同左 | 共通 |
| regeneration / resume | `--regenerate-stage storyline_b3|writer|advanced|standard`、audioは`--stage plan|scaffold|tts|assemble|player|all`、`--scaffold-only kp`(KPだけ1レベル1回)、`--only-segments`(tts専用、対象外はSKIPPED_NOT_SELECTED→Gateが組立を止める)。JA再利用はU-1(W-1来歴+注記sha一致がなければSTOP)。Master Audio Storeの完全一致再利用と継承(`try_inherit_from_cached`、再利用6点は共通helperの3-ASR再判定を通す)。style profileは固定記録(`audit/style_profile.json`)で旧style混在を課金前STOP | CS:1175,1198(U-1/U-2),2937 | `er019_family_x_audio_production_runner_01.py:2337-2406` | `--only-segments`の正規表現は`topic_intro|japanese_title|preview|in_one_line|comment_n|full_story_part_n|kpN_*`で固定(`:537`)=Yの新segment名は拒否される。U-1は`chain_method=="W-1"`来歴前提=Y用Writerを別経路にするなら来歴定義の拡張が必要 |
| STOPセンチネル/RUN_LOCK | **Zのrunner**(`er026`/`er062`/`er063`)は各API呼出・各clip前に`<run>/STOP`/`STOP_ALL`を確認(rc=3)し、二重起動防止の`RUN_LOCK.json`(PID生存)を持つ。**Xのaudio/entertainment runnerにはSTOPセンチネル確認コードが無い**(Grep: `er019_family_x_*`に`check_stop_sentinel`/`STOP_ALL`参照なし)。X側はKP外側retryの各周でZのhelper(`er062_family_z_structure_01.check_stop_sentinel`)を呼ぶだけ。XはコードにSTOP_NOTICE確認なしで文書規則(PM_GOVERNANCE 26-2(d))のみ。統一作業はOPEN-354/355で未実装 | CS:2809,Z節『運用安全』箇条(CS:1635)、`er062_family_z_structure_01.py:236-260,375-414`、`er003_v1_n3_01_scaffold_generate.py:662,851` | 同左 | **Y新設時は「Zの方式」を最初から採るか、OPEN-354統一を待つか**の選択肢がある。有料run前の`tools/stop_scope_check_01.py`はPM運用側で必須(26節) |

## 7. QA・Validator・Assembly・試聴ページ

| 項目 | 現在の正式仕様(Status) | 出典 | 実装の所在 | Family Y継承時の注意 |
|---|---|---|---|---|
| Gate群(Assembly前) | `style_profile_gate`(全role Style記録と承認profileの照合、未通過は組立BLOCK)/`key_phrase_source_gate`(KPのsource_span(source_sentence)が現行本文に実在、Assembly直前)/shared narration gate(shell非OKなら拒否)/gloss整合HR gate/Audio Validation Gate(全segmentのstatus)。2記事E2Eで全PASS | runner `:1735 _style_profile_gate_blocked_summary`、`:855`、`:1765`、CS:2112、RESULT_01.md §1 | 同左 | `key_phrase_source_gate`は本文実在を要求=KPFTの全文選定と整合。Yも同様 |
| Assembly | timeline builder(`build_family_x_b1_timeline`/`..._a2_timeline`)でsegment順に合成、scalar RMS基準のgain、最終段headroom安全弁(`apply_headroom_safety_valve`、peak≤0.95、24k→48k後のオーバーシュート対策)、`audit/timeline.json`・`headroom_report.json`・`gain_report.json`出力。実測: 記事AのAdvで発動(scalar 0.9956) | runner `:1684,1792-1846,1950-2062`、CS:2085-2100 | 同左 | timeline builderはsegment列を**コード内に固定**(T11)。Yは別builderが必要 |
| player / 試聴ページ | runner `player` stageは`player.html`を生成(`build_player_html`)。ユーザー向け試聴ページは**標準フォーマット**(X/Z/Y共通、2026-10-18): 1ページにStd/Adv各節、全編通し再生ボタン、再生順の全スクリプト表(Preview/Comment/Full Story Part/KP英+日本語意味)、効果音行・内部ID・Voice/Style等の内部情報は載せない、PASS_WITH_WARNINGは後ろの折りたたみ。共通module `er_user_listening_page_common_01.render_standard_page`+`check_page`、検査tool `tools/user_test_page_standard_check_01.py`。**X側のページ生成はrunner外の記事別script**(例`er019_nws_final_page_01.py`、`er019_bape_page_04.py`)、Zは`er063_family_z_audio_01.py::build_pages`がindex.html生成+check必須。X runnerへのcheck組込みはFable CP待ち。再生検証(Playwright等)は記事別script(例`er019_nws_play_verify_01.py`) | CS:2919、PM_GOVERNANCE Gate 7補足(a)〜(n)、RESULT_01.md §1,§7 | `er_user_listening_page_common_01.py`、`tools/user_test_page_standard_check_01.py` | 標準フォーマットは「Std/Adv各1節+Preview/Comment/Part/KP」前提。Yの5パートとVoice表示(どのVoiceの発言か)を表にどう載せるかは設計論点。表示仕様はユーザー受入済みXページが基準 |
| 最終受入 | 機械QA全合格でも「完成」ではなく、最終はユーザー試聴(`USER_LISTENING_PENDING`→PASS)。PASS_WITH_WARNINGの事後試聴は非ブロッキング | CS:2110,2919 | — | 共通 |

## 8. 共通仕様のFamily間整合

### 8-1. 配線Status表(CS:1677-1705)の読み方
- 「共通」仕様(PD06/S3/E1/K2/P8-KP/P7/Std 6%減速/AUW共通基盤/Source Reference Contract)はX・Zとも仕様別に`PRODUCTION_WIRED`(Zは2026-10-17 Fable受入)。**Family Y列は全行「未着手」または「未定」**。
- X固有: M2P0+優先順位A方式(KPFTで撤去済みのため表は**古い**、§13)・Risk Flagger・In One Line/Comment4。Z固有: Strategy L KP・Dialogue別Voice・Adv Comment E2_UPBEAT。YはX固有のうちRF/IOL/Comment4を採るかが「未定」(表の記載)。ただし原文§2.1がPreview/Comment/KP/In One LineをX基盤と指定済みのため、IOL/CommentのY採用は既決、RFは未決。
- PM_GOVERNANCE 28-1運用7: 新規Family(Y)は既存の共通承認仕様を最初から配線対象に含める。

### 8-2. A/B/C Legacy凍結(PM_GOVERNANCE 27-7、CS:1638節)
- A/B/CはBackup。最新仕様への追従・新規実装・Regression更新をしない。共有module(Layer 1/3/4、KP共有module等)の変更が結果的にA/B/Cへ及ぶのは妨げない(Family固有コードは個別変更しない)。
- 実装上のscope分離は機構ごとに異なる: er109とPNAPは`run_scope("X"|"Z")`の内側だけ有効(A/B/Cは従来コードパスで、前後署名43,033件がバイト一致、CS:2967)。一方で多語同音救済(`er094_multiword_homophone_01.MULTIWORD_HOMOPHONE_ENABLED`)は共有`protected_check`内のmodule定数で、scopeによる限定ではない(A/B/Cにも及び得るか否かの明示承認は本調査では未確認)。
- 旧B(Voices)は`er012_b_family_*`系で独立実装(Leakage Check等)。X/Zの共有Validatorとは別系統。**YはBの経路を転用しない**(原文§1)。
- 運用方針の記録: 17記事ミックス案にFamily Y(Voices) 3記事が含まれる(CS:2797、運用方針のみ)。

### 8-3. Y関連の既存記録(重複回避のため参照のみ、01B領域と接する)
- OPEN-217(2026-09-28、FAMILY-Y-VOICE-STRUCTURE-TRIAL-01): X流のR1→R2(エンタメ性up)をVoice文脈に流用すると既存Leakage Checkのfail-field数が悪化(2→3→11)、LLM rubric単独評価は改善と誤判定。→ **XのWriterチェーン(R1/R2)をYにそのまま流用できない既往根拠**(Trial記録、Production仕様ではない)。
- OPEN-218: Voice系評価でLLM rubric単独はバイアスがあり、決定論チェック併用が論点。
- OPEN-219: X Fact Ledger形式(`[VERIFIED] id:`)と旧B系Ledger形式(`[VOICE_N_EVIDENCE]`)は非互換(Trial内の使い捨てアダプタのみ)。
- OPEN-415: Style profile機構がXとZで別。Y導入時のX/Z/Y横断profileエンジン化の要否を判断する課題。
- 報告: `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md`(repo root)§2,8,10(Trial実測: 1記事9 call、費用¥5.90。これはTrial記録でありProduction仕様ではない)。

## 9. 費用構造(事実と仮説を分ける)

### 9-1. 事実(出典 `docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md` §5、現行Production正式経路、2026-10-22)
| 項目 | 記事A(Prix Pascal) | 記事B(Tesla/SpaceX) |
|---|---|---|
| 記事セット(Std+Adv)合計 | **54.06円** | **131.61円** |
| Research(web_search) | 5.65 | 26.77 |
| Fact Ledger | 5.48 | 16.03 |
| B3+丸め判断 | 6.07 | 7.14 |
| Writer R0-R2 | 16.55 | 17.13 |
| 英訳(Adv/Std) | 0.57 | 0.96 |
| Risk Flagger | 1.27 | 約1.6 |
| 音声scaffold(Preview/Comment/KP選定/gloss/解説) | 1.29 | 2.87 |
| TTS(Gemini) | 11.32 | 12.71 |
| ASR(OpenAI/Azure) | 3.11/2.73 | 3.34/7.95 |
| 日本語読み調査 | 約0.02 | 約35.1(1回限り。Ledger登録後は再発しない) |

- 定常見込み(記事Bの1回限り読み調査を除外): A 54.1 / B 約96.5 / 平均約75.3円(RESULT_01 §5)。目標70円に対し、差の主因はResearch(web_search)費の記事間変動(B 42.8円 vs A 11.1円)。
- 2記事の単純平均92.8円/セット、合計185.67円(案件上限300円内)。
- 旧baseline(CS:2186周辺「Expected Production Cost ¥111.17/pair」)は2026-08の旧設計の推計で**現行Xの実測とは別物**(§13)。
- Zの直近実測(参考): run_e2e_03は別枠JPY100に対し実測JPY36.38(CS:1677表下の委任_17箇条。Seed方式でResearch/RF無し)。

### 9-2. 仮説(事実ではない。後続Trialで実測が必要)
- Voices構造で増える可能性: (a) Writerの出力長・call数(5パート+3視点の設計)、(b) Commentの数と生成call、(c) 英訳・簡易化の文量、(d) 総尺増に比例するTTS/ASR費、(e) 人物別TTS Voiceを導入する場合のMaster Audio Store再利用率の変化、(f) Y専用のFact言い直し防止ゲートを足すと追加call(Trial記録OPEN-217の見積り: must-fix retryで+1〜2 call/記事)。
- 減る可能性: 旧Bの複雑なGate群を使わずX経路のfail-closed・内容retryなしのGateに寄せれば、検査系callは旧B比で減る(仮説、旧B実績は01B領域)。
- 費用の主要変動要因は既存でResearch(web_search)であり、Voices構造に依存しない。Y独自の増加はWriter側とTTS/ASR尺の2点が主候補(仮説)。

## 10. X経路でFamily Yを「構造差分だけ追加」する場合の技術的接続点(列挙のみ、設計は後続)

| # | 接続点 | 所在(ファイル:関数/行) | 現状のX固有性 | 備考 |
|---|---|---|---|---|
| T1 | Writer prompt(日本語原稿) | `er053_family_x_factlock_ja_writer_01.py` `build_r0_prompt`(`:265`)/`USER_TMPL`(`:64`)/R0 Fact Lockブロック(`:67-100`) | 一本の読み物を書く前提(800〜1000字) | Voice人物設計をどこで入れるか(B3後・R0前等)。R1/R2は「エンタメ性up」でOPEN-217の既往悪化あり |
| T2 | B3/Fact選定 | `er019_family_x_storyline_b3_fact_selection_01.py`(Prompt/schema)、`er053_b3_annotation_contract_01.py` V1〜V10 | 中心Storyline1本+最小Fact | Fact→Voice割当層が必要なら新規。契約V1〜V10のfail-closed維持 |
| T3 | 記事構造定義・分割 | `er003_v1_n3_01_scaffold_generate.py:188 split_family_x_article_text_v2`、`er019_family_x_audio_plan_01.py:282-340`、`:238 reconstruct_family_x_article_text_v2` | 3分割・In one line固定 | 5パート用の分割関数とsegment順序tupleが別途必要。旧split関数は後方互換用に残置 |
| T4 | 英訳/簡易化 | `er003_v1_n3_01_advanced_adaptation_generate.py:674`、`er003_v1_n3_01_standard_a2_generate.py:541`、`er012_e_family_entertainment_two_level_runner_01.py` `run_writer_stage`/`_family_x_ensure_split_or_paragraph_retry` | 段落数一致の忠実翻訳 | 段落数一致契約はY構造に転用しやすい。段落≥3の判定は5以上へ |
| T5 | Preview/Comment scaffold | runner `:273,308`(`run_family_x_b1/a2_scaffold`)、roles=`er019_family_x_audio_plan_01.py:181-236` | Comment3/4が3分割前提のX専用role | Y用のC1〜Cn役割文と生成順(context構成)を新規設計 |
| T6 | KP選定 | `er003_v1_n3_01_scaffold_generate.py:351,705` | 構造非依存 | そのまま継承可(分類A) |
| T7 | In One Line | `er003_v1_n3_01_advanced_adaptation_generate.py:552,752` | 2〜3文、新規事実禁止 | Tension+Closing最終パートとの重複防止を設計 |
| T8 | segment ID→role解決 | `er020_tts_retry_local_rewrite_01.py:125 resolve_narrative_role`、runner `:537`(`_VALID_ONLY_SEGMENT_RE`) | `full_story_part1/2/3`等のID固定 | Y用IDだとConnected Speech/Local Rewrite/QA/`--only-segments`から漏れる |
| T9 | TTS segment生成・Voice割当 | runner `:888 generate_family_x_b1_segments`、`:1234 ..._a2_segments` | Narrator=Aoede/Charon固定 | 人物別Voice化はZ先例(`assign_dialogue_voices`、決定論・初出順)を参照 |
| T10 | Style profile | `er019_family_x_style_profile_01.py`(fx_20261017)、`er063_family_z_audio_01.py`の定数参照+drift test | X=profile機構、Z=定数参照 | OPEN-415 |
| T11 | Assembly timeline | runner `:1684,1950`、`:1792-1846` | segment列がコード固定 | Y用timeline builder |
| T12 | 試聴ページ | `er_user_listening_page_common_01.py`、`tools/user_test_page_standard_check_01.py`、記事別page script | Std/Adv・Preview/Comment/Part/KP | Voiceを示す列/ラベルの有無は設計(内部ID非表示ルールは維持) |
| T13 | run-scope限定の共通機構 | `er103_proper_noun_alarm_policy_01.py:42`、`er109_xz_scope_01.py:25`(`APPROVED_SCOPES`) | "X"/"Z"リテラルのみ | Yへのscope追加が必要。28-1運用7に基づく(Fable判断) |
| T14 | Risk Flagger | `er053_risk_flagger_production_01.py` | Xのみ。Zは対象外 | Y採用の可否が「未定」 |
| T15 | STOP/RUN_LOCK | `er062_family_z_structure_01.py:236-414` | Zにあり、Xのrunnerには無い | Y新設時の採用方式 |
| T16 | 来歴契約(U-1) | `er019_family_x_entertainment_production_runner_01.py:298 load_reused_ja_text` | `chain_method=="W-1"`前提 | Y用Writerの来歴定義 |
| T17 | routing/pricing | `er006_model_routing_contract_01.py:119-141`、`er005_output/cost_baseline_01/pricing_snapshot.json` | 未登録modelはfail-closed | Yで新processキーを足す場合は追加必須 |

## 11. Family Y継承時に衝突・注意が要る点(まとめ)

### A. 構造的衝突(X固有の前提とVoices構造)
1. 3分割・In One Line固定の記事構造(T3/T8/T11)。Yは5パート。
2. Comment3/4が3分割前提のrole文(T5)。Yは別の接続数になる。
3. Writerは「日本語で一本の読み物→英訳→簡易化」。Voice人物の独立性が日本語段階で決まり、後段(忠実英訳・A2簡易化)で平板化しないかが未検証(仮説)。
4. B3が「中心Storyline1本+最小Fact」。複数視点のVoicesでは選定単位が合わない可能性(T2)。
5. R1/R2の「エンタメ性up」指示は既往Trial(OPEN-217)でFact言い直しを悪化させた。
6. segment_id固定(`full_story_part1/2/3`、`comment_n`、`in_one_line`)に依存するConnected Speech・Local Rewrite・disfluency/repetition QA・`--only-segments`(T8)。

### B. 承認範囲・Status上の注意
7. er109とPNAPは"X"/"Z"リテラルscope(T13)。YはPM_GOVERNANCE 28-1運用7で配線対象だが、コード上は追加変更が必要。
8. 丸め判断(OPEN-437)の承認原文は「Family Xのみ」(Zは到達しない)。Y適用は別判断になり得る。
9. RFはZ対象外、Yは「未定」(CS:1677表)。
10. er109(OPEN-459)は`WIRED_PENDING_FABLE`、M1(CS:2813)は`PRODUCTION_WIRED`未宣言。継承前に最終Statusの確認が要る。
11. 多語同音救済は共有関数のmodule定数でscope限定ではない(A/B/Cへの影響は未確認)。

### C. 品質リスクとの対応(原文§6との橋渡し。設計は後続)
12. 「主観的体験談の中での事実創作」: X Fact Lock規則2は「主観文は番号不要・新事実断定禁止」と定義するが、一人称の体験談(誰が・いつ・何をした)が「他者の具体的行動の創作」に当たるかはX規則だけでは未定義。Xの決定論ゲートは数字(【中核数値】)中心で、体験談の創作を機械検出する層はX経路に存在しない(RFは非Blocking・事後)。
13. Xは「内容を理由にした再生成」を撤去済み(旧Fact Checker等)。YのVoice別品質検査(旧BのLeakage Check相当)を持つなら、X設計思想(fail-closed・反復再生成しない)と整合する形での設計が要る(区分D候補)。

### D. 運用面
14. XのrunnerにSTOPセンチネル/RUN_LOCKがない(§6)。Y新設時の方式選択。
15. 試聴ページはX側がrunner外の記事別script(§7)。Y用ページ生成の持ち主。
16. Z Std Dialogue 6%減速の撤去版A/B Trial(`FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01`)が進行中(ACTIVE_TASK並行タスク、OPEN-461)。Std英語narrationの6%減速は共通仕様だが、人物の会話(YのVoice別TTS Voiceを採る場合)への適用方針はこのTrial結果次第。

## 12. 未確認事項
- OPEN-459(er109)のFable受入後の最終Status(本書は`WIRED_PENDING_FABLE`の記載時点)。
- `TTS_EXECUTION_MODE`の実運用設定(コード既定=BATCH。E2EがBatchか同期かは未確認)。
- Std 6%減速が及ぶXのsegment範囲の完全な一覧(Full Storyは確認済み。In One Line等は未確認)。
- Xの`topic_intro`/`welcome`等の生成元テキスト定義(固定フレーズChampion対応表はCS:1902、本書では未精査)。
- 多語同音救済のA/B/C影響の明示承認。
- ユーザー希望のY総尺・語数・人物別TTS Voice採否(原文に指定なし)。
- `docs/pm/PM_GOVERNANCE.md` Gate 7補足(a)〜(n)の全文(CS:2919の要約のみ確認)。
- CS:1677のFamily Y列の記載は「未着手/未定」であり、設計判断済みの記録ではない。

## 13. 旧仕様と現行正式仕様の取り違えやすい点(override関係)

| 旧記述(残存場所) | 現行 | 切替日・根拠 |
|---|---|---|
| 「Primary PASSならSecondary不要」(CS:2827基本フロー) | KP英語phraseのみ3-ASR多数決(P/S/W)。UDR #139の『両方PASS必須』は置換済み(同行内に注記あり) | 2026-10-22 KP3V(CS:2923) |
| 「ローカルWhisperのProduction導入は不採用」(UDR #136、CS:2828) | KP英語phraseの決選票に限り上書き。それ以外の音声は不採用のまま | 2026-10-22(同行の上書き注記) |
| KP 5件(4+1)/Strategy L/DB Hybrid/M2P0候補供給+優先順位A方式(CS:1955,1677表のX固有行) | X/Zは全文選定Prompt2・最大3件。M2P0/DB Hybrid/Strategy L fallback/Topic枠は**撤去**(CS:1990)。1677表のX固有行「M2P0+A方式=PRODUCTION_WIRED」は**古い記述** | 2026-10-22 KPFT(OPEN-454) |
| 旧Fact Checker/Ledger Deviation/案B/JA差戻し/JAFactCheckStopError(CS:1361付近) | X Productionから撤去。W-1 Writer+RF(非Blocking) | 2026-10-10(CS:1194) |
| R0=Luna、R1/R2=Astra | B3/R0/R1/R2=gpt-6.1-sol | 2026-10-11(CS:1165-1169) |
| Point One/Two・Point通知音・Heading Readout・`###`見出し(A/B/C仕様と旧X Stage1〜3c) | Xは見出し廃止・段落3分割・Comment1〜4 | 2026-09-29 W1(CS:1405) |
| Full Story Style N01(2026-10-13)、Coffee限定P8/PD8 | Family XはPD06(2026-10-16承認、10-17にXとZで仕様別PRODUCTION_WIRED)。「P8」はKP日本語意味P8-KPと別物 | CS:1259(訂正)、1677表 |
| Std日本語Preview/Comment=R2(J3は更に前) | S3 | 2026-10-17(CS:1270) |
| In One Line=1文(旧Prompt)/中心1文+補足2文程度(A2仕様CS:591) | 基本2文、必要時3文 | 2026-10-16 09:00判断(CS:1215-1259) |
| KP英語解説P3(Coffee限定)・KP日本語意味M2 | P7(Adv)・P8-KP(Std) | 2026-10-16 |
| Advanced契約接尾`Length 280-420 words/### 2つ/In one line 1文`(`ADVANCED_CONTRACT_SUFFIX`) | Xの忠実英訳経路では未使用(旧Advanced生成関数とTrial互換のため残置) | 2026-09-29 W1 |
| CEFR比較表(A2/B1/B2)・B1(Support-based、Charon Support)節(CS:519-666) | HISTORICAL記載を多く含む。現行Xの採用ルールは`standard_a2_generate.py`/`advanced_adaptation_generate.py`が正本 | CS:519節の注意書き |
| Cost定義の「Expected Production Cost ¥111.17/pair」(CS:2186) | 現行Xの実測=A 54.06円/B 131.61円(定常見込み平均約75円) | 2026-10-22 RESULT_01 |
| Z-3(In One Line、Z)・Z語数280〜420・Zの旧原作保持Validator | Z: In One Line/Comment4なし、400±70語(WARN)、Validator撤廃(Writer Prompt改善へ) | 2026-10-12/10-19(CS:1607,1617,1626) |
| 日本語ASR U1暫定(`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=True`)(CS:2822節の「暫定値」行) | U1発効(False)。A3 length是正済み。AUWは`PRODUCTION_WIRED` | 2026-10-16(CS:2844以降の追記) |
| 「Family Yは別Family、着手済み実装なし」(CS:1643) | 2026-10-16以降は開発対象(X・Z・将来Y)。Y関連の既存記録はOPEN-217/218/219/415のみ(Trial記録・課題で、Production実装なし) | PM_GOVERNANCE 27-7 |
