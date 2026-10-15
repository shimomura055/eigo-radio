# A_COMPLETION_CRITERIA_RECONSTRUCTION_01 (FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01A、2026-10-15、Read-only・JPY0)

性質: 仕様側の再構成のみ。「実際の完成版」「判定」「原因」列は**空欄**(01B[成果物側]と委任_02で埋める)。ただし仕様側調査中に偶然確認できた実測断片は§2末尾の「暫定観測」に分けて記録した(判定ではない)。SSOT・コード・音声は無変更。`VALIDATED`と`APPROVED_FOR_PRODUCTION`は混同していない。

## §0 超サマリ(非エンジニアPM向け、10行)

1. ユーザーが求めた完成条件は、最も明確なものが2026-10-12の「必須反映5点」(In One Line確定仕様/P3/R2/変更対象音声の更新[既存流用だけ禁止]/最終Assembly後のruntime evidence+試聴ページ確認)で、これはSSOT(DECISION_LOG L20644、OPEN-321、計画書)に残っていた。
2. In One Lineは2系統ある。(a)正式仕様(CURRENT_SPEC L583、2026-08-09 DECIDED)は「中心1文+補足2文程度」=**1文のままでも既存の正式仕様の履行不足**。(b)「2文基本」は2026-10-12のユーザー決定をv3で試したもので、仕様化は未(OPEN-299)。
3. 2文版のIn One Line原稿は、記事の原稿ファイル(parts.json等)には入らず、Trialの付属ファイル(`iol_final_text_01.json`)にだけあった。これが後工程で消える構造的な弱点だった。
4. final_03の制作工程(M2P0/N01の委任文・設計書・CHECKLIST_05・Fable受入)には、OPEN-299・OPEN-316・OPEN-321・REASSEMBLY計画への参照が**1件もない**(rg確認)。「必要仕様の一覧照合」は制作・受入のどこにも組み込まれていなかった。
5. CHECKLIST_05は12項目の「Production配線チェックリスト」で、In One Line・K2・M2・Intro A5/B5・Adv Commentの照合項目は無い。#11は「Std Preview/Comment=R2、Std KP=既存、Adv=E1/P3/N01」しか照合していない。
6. 仕様側の整理では、完成版に関わる仕様を6区分で計46行(正式採用済み13/Coffee限定採用10/VALIDATED未採用・保留6/個別指示8/不採用・保留・対象外6/完成後承認3)に列挙した(件数は§2末尾)。
7. 暫定観測(判定は01B): final_03のIn One Lineは両レベル1文(旧文面)。Std KPの日本語意味はJ3(=M2ではない)、Adv KP英語は既定Style(=K2ではない)。profile定義(`er019_family_x_style_profile_01.py`)にK2/M2/A5/B5は存在しない。
8. 旧gloss再整合(legacy)で作られたCoffee完成版と、2026-10-15正式採用のcorrected版は別物。final_03はlegacy由来(Opus条件C所見どおり、`keywords_canonicalized.json:145-146`)。
9. 技術テスト全PASS(Playwright 51/51、Regression失敗0)は「承認済み仕様の網羅」を保証していない。網羅性確認が無かったことが主因の候補。
10. 本委任は監査のみ。コード・音声・SSOT無変更、有料API 0、JPY0。

## §1 ユーザーがCoffee完成版を依頼した目的・要求(原文逐語+出典)

注記: **ユーザーが最初にCoffee完成版(Final v2/v3)を依頼した2026-10-11/12のチャット原文はRepo内に逐語では残っていない**(未確認)。残っているのは(1)DECISION_LOG/CURRENT_SPECへの「ユーザー決定(逐語要旨)」記録、(2)委任ログ内の転記。以下はRepoで逐語確認できる範囲のみ。

### 1-1. v3時点(2026-10-12) 最終版の依頼と決定
- `DECISION_LOG.md:20569`(FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_03)ユーザー選択(逐語要旨): 「共通Intro A=A5、B=B5 / Advanced Preview=E1 / Full Story=F5(Standardは+既存6%減速)/ KP英語=K2 / KP日本語意味=M2 / Standard日本語Preview・Comment1〜4=P2」「Standard part1/2/3・Advanced part1/2/3をF5で再生成」。
- `DECISION_LOG.md:20591`(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01+02): 「Coffee記事に限りStyle選択=`APPROVED_FOR_PRODUCTION`(Intro A5/B5、Adv Preview E1、Std日本語Preview/Comment P2、KP英語K2、KP日本語意味M2、Full Story PD8[Stdのみ生成後6%減速]、IN_ONE_LINEは既存承認Style不変)。全記事共通Styleは未承認。**In One Line方針**: 既存仕様『中心1文+補足2文程度』の履行不足の是正と、新2文方針(中心1文+補足1文)は区別する。」
- `er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md:4-5`: 「現行完成版は中心1文のみで、**この既存仕様の履行不足**だった」「今回のユーザー決定(2026-10-12): 両レベル**2文基本(必要なら3文)**。1文目=記事の核心、2文目=意味・示唆で自然に締める。」(ユーザー原文の逐語は未確認。このファイルが最も近い記録)

### 1-2. 再Assemblyの必須条件(2026-10-12、ユーザー指示逐語要旨)
- `docs/pm/design/2026-10-12_COFFEE-FINAL-REASSEMBLY-PLAN-01.md:8-16`(DECISION_LOG L20644にも同旨): 「In One Line関連仕様が確定した後、Coffee最終版を再Assemblyする際には必ず次をすべて行う。1.確定したIn One Line関連仕様を反映する。2.**Advanced Key Phrase英英解説の正式選択済みP3音声Styleを必ず反映する。**3.Standard Preview/Commentの承認済み**R2**も反映する。4.既存音声の流用だけで済ませず、変更対象の音声を更新する。5.最終Assembly後、対象Styleの適用を**runtime evidenceと試聴ページで確認**する。」
- 同 計画書§2(`:20-24`): 前提=「In One Line関連仕様の確定(=Comment4 Trial-03採否、OPEN-316)**USER_DECISION_REQUIRED(未確定)**。全体の前提。確定前は再Assemblyを開始しない。OPEN-299(IOL 2文方針の仕様化)も関連」。

### 1-3. final_03直前の指示(2026-10-13、FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01、逐語)
- `docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_01.md:158-181`: 「是正①〜③の後、Coffee Standard・Advancedについて、正式Production経路を使用して完成版を作成すること。…Standard: M2P0 Key Phrase生成・検証PASS/N01 Full Story全対象part生成/Standard 6%減速およびASR再検証PASS/Audio Validation / M3等の必要Gate PASS/正式assemble完了。Advanced: M2P0 KPの正式反映/N01 Full Story各partの正式反映/再利用segmentのValidation状態を正しく検証・引継ぎ/正式assemble完了。試聴ページ: 現在のCoffee試聴ページは途中段階の品質確認用であり、Production完成版の証拠ではない。是正後は、**正式完成版の音声を用いた試聴ページを改めて提示すること。**ユーザーが旧版と新版を混同しないよう、対象音声・生成日時・適用仕様を識別可能にする。」
- 同ファイル`:26-58`: 「M2P0・N01のProduction配線が進んだこと、品質Gateを迂回せずSTOPしたことは適切」「今回の作業は追加Trialではなく、承認済み仕様を正常にProductionで動かすための是正・完成作業とする」。
- 同ファイル`:7節`: 「N01の適用範囲・Coffee原稿v5・既存再生成範囲等については、CURRENT_SPECと過去のユーザー決定を照合し、承認済み範囲で進めること。」(**この指示にIn One Lineの文数は明記されていない**。「CURRENT_SPECと過去のユーザー決定を照合」は求められていたが、照合対象一覧はIn One Line/K2/M2/A5/B5を列挙していない)

### 1-4. 2026-10-14 委任_04(逐語)
- `docs/pm/delegation_log/2026-10-14_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_委任_04.md:2-6`: 「最終英語KPと日本語glossの意味的整合は、当然満たすべき基本品質要件である」「Advanced Comment 1〜4のE0: 今回`main E0`で生成できたことだけを理由に正式採用判断を求めない…今回、E0の新規採用を承認したわけではない」「Coffee Standard/Advancedの聴感判断は完成版試聴ページ提示時に行う。その際、Standardの6%減速後のWPM、AdvancedのWPM、文末ポーズ、実際の聴きやすさを確認できるようにすること」「Production作業の受入条件: 正式Production初回経路、retry/fallback/regeneration、必要Regression、実runtime evidence、model_id/routing、CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、Gitを確認する。未完了項目があれば`PRODUCTION_WIRED`と報告しない。」

### 1-5. 本監査(2026-10-15)のユーザー指示
- `docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01A.md`「ユーザー指示(原文)」節: 「ユーザーはCoffee記事について、これまでのTrial成果・承認済み改善を可能な限り織り込んだ完成版を依頼していた」「仕様が承認されていても完成品に反映されていなければ、完成とはいえない」。

### 1-6. 「依頼時の目的」の再構成(要約、推測を含まない範囲)
(i)Trial成果・承認済み改善の網羅的な反映(上記1-5)、(ii)必須反映5点(1-2)、(iii)正式Production経路での完成と、旧版と区別できる試聴ページ(1-3)、(iv)基本品質要件(KP/gloss整合)と聴感判断材料の提示(1-4)。**(iii)(iv)はfinal_03で満たされたと記録されている。(i)(ii)の一覧照合は記録がない**(§3)。

## §2 完成版が満たすべき仕様(仕様マトリクス・仕様側列)

凡例: 列=# / 仕様名・管理ID / 出典(file:line) / 対象(S=Standard,A=Advanced,両) / Trial結果 / ユーザー判断(日付) / 適用要否 / 期待動作(本来どうあるべきか) / 判断日とfinal_03作成(2026-10-14)の前後。末尾3列「実際の完成版/判定/原因」は**空欄=【01B/委任_02】**。判断日がfinal_03より前=「前」、後=「後」。v3作成=2026-10-12、v5=2026-10-12〜13。

### 区分1: 正式採用済み(Family X共通、当然反映すべき) 13行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 1-1 | In One Line構成(中心1文+補足2文程度)ER-003-A2-STRUCT-05 | `CURRENT_SPEC.md:583` | 両 | -(DECIDED仕様) | 採用(DECIDED、2026-08-09) | 必須 | In One Line節は中心1文+英語の短い補足2文程度(計約3文)。補足はFull Story/Points既出情報のみ、新規fact追加なし。「In One Line」は中心1文を指す語で節全体を1文に限定しない | 前(約2か月前) | 【01B】 |
| 1-2 | M2P0 KP候補供給(M2+P0) FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 | `DECISION_LOG.md:20941` | 両(X) | VALIDATED(Trial)→採用 | `APPROVED_FOR_PRODUCTION`(2026-10-13) | 必須 | M2供給(phrase_cap=20等)+P0選定(prompt sha無変更)。M2例外はStrategy L fallback+通知 | 前 | 【01B】 |
| 1-3 | N01 Full Story narration style | `DECISION_LOG.md:20941`、`er019_family_x_style_profile_01.py` N01_TEXT/N01_SHA256 | 両 | VALIDATED→採用 | `APPROVED_FOR_PRODUCTION`(2026-10-13、Family X/Z) | 必須 | Full Story part1-3は全てsha `d1956c91…`(202文字)。Stdは逐語使用(A2減速指示を追記しない)+生成後6%減速+減速後再検証。fallback takeはN01ではない(Gate/M3でBLOCK・人間承認) | 前 | 【01B】 |
| 1-4 | Std Full Story 6%減速+減速後ASR再検証 | `CURRENT_SPEC.md:2625`(N01節)、`DECISION_LOG.md:20941` | S | 既存承認 | 採用(既存) | 必須 | 英語本文4role(Part1-3+IOL)に生成後約6%減速。duration比≈1.06。減速後も再ASR | 前 | 【01B】 |
| 1-5 | Std Comment 4 Prompt(Bridge「最後に」2文追加) | `CURRENT_SPEC.md:2624`(V5委任_01 (A))、`er057_output/coffee_comment4_trial_03/prompt_diff_03.md` | S | VALIDATED(Trial-03) | `APPROVED_FOR_PRODUCTION`(2026-10-12、共通定数を変更済み) | 必須 | Comment 4に「In One Lineは番組最後の英語による要点整理」「『続いて』より『最後に』」が反映され、本文末→In One Lineの橋渡しになる | 前 | 【01B】 |
| 1-6 | Rule7/Source span/canonicalization(+是正①②③、案A'、候補ID方式) | `CURRENT_SPEC.md:2627-2631`(COMPLETION-01追記)、`DECISION_LOG.md`COMPLETION-01_01〜03 | 両 | -(既存承認+是正) | 採用(「承認済み範囲」2026-10-13) | 必須 | KPは原文にspan根拠があり、Rule7判定は既存式。Rule7 INVALID時の自動処理は既存retry/fallback。KPの語数・難易度は既存基準 | 前 | 【01B】 |
| 1-7 | 最終英語KPと日本語glossの意味整合(基本品質要件) | `…委任_04.md:2`、UDR #57 | S(中心)/A | -(要求) | 採用(2026-10-14ユーザー指示「当然満たすべき基本品質要件」) | 必須 | 英語KPと日本語glossが意味的に一致(例: `based on interviews`⇔gloss)。TTS読みも整合 | 前(同日) | 【01B】 |
| 1-8 | Audio Validation Gate/M3 Style Gate/retry・fallback・regeneration整合 | `CHECKLIST_05.md:7-12`、PM_GOVERNANCE Gate 3 | 両 | -(既存) | 採用(既存) | 必須 | 全segmentがstatus=OK+ASR検証済み。再利用segmentは検証を引継ぎ(`REUSED_VALIDATED`)。fallback takeは人間承認なしに組立不可 | 前 | 【01B】 |
| 1-9 | 可変segment Role Style(E2値): TOPIC_INTRO/IN_ONE_LINE | `er033_tts_flash_lite_family_x_styles_01.py:36-48`、`CURRENT_SPEC.md:2620` | 両 | VALIDATED→採用 | `APPROVED_FOR_PRODUCTION`(2026-09-28) | 必須 | TOPIC_INTRO=`brief, clear, engaging…`、IN_ONE_LINE=`concise, clear, landing naturally…`。Stdのみ減速指示付与 | 前 | 【01B】 |
| 1-10 | Std japanese_title等の日本語Style=J3 | `ADV_STYLE_FACTCHECK_02.md:25`(J3正本)、er033 | S | VALIDATED→採用 | 採用(J3、日付はSSOT行未特定=要確認) | 必須 | japanese_title=J3 sha `ae68e3e6ac8e` | 前 | 【01B】 |
| 1-11 | Fact Lock/Risk Flagger(Lane A、RISK-FLAGGER-PRODUCTION-WIRING-01) | `docs/pm/REPORT_LEDGER.md:243` | 両 | -(PRODUCTION_WIRED) | 採用(2026-10-11) | 必須(原稿生成経路) | 原稿にFact Lock/Risk guardを通す。Coffee v4/v5原稿はToneブランチ由来で、通過有無は要確認(`rf_tts_guard.json`あり) | 前 | 【01B】 |
| 1-12 | JA記事モデル配分(E案、Sol61)/Writer・Entertainment関連 | `docs/pm/REPORT_LEDGER.md:245-246` | S(JA部分) | VALIDATED→採用 | `APPROVED_FOR_PRODUCTION`(2026-10-11、PRODUCTION_WIRED) | 要判断(Coffeeの原稿正本がToneブランチ原稿かProduction L3原稿かで適用有無が変わる=OPEN-326) | 日本語Preview/Comment/title生成がE案配分で作られる | 前 | 【01B】 |
| 1-13 | Family X記事構成(Full Story 3分割+Comment 1-4+Key Phrase 5+IOL、Welcome/Preview intro等の固定音声、Outro) | `docs/pm/design_family_x_section_segmentation_spec_01.md`、CURRENT_SPEC Family X構成節 | 両 | -(DECIDED) | 採用(既存) | 必須 | segment順序・分割数が正式構成と一致。Outro/終端の有無は仕様上の記述を01Bで確認(未確認) | 前 | 【01B】 |

### 区分2: Coffee限定で採用された仕様(2026-10-12ユーザー決定、全記事共通は未承認=OPEN-298) 10行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 2-1 | Intro: Welcome=A5、Preview intro=B5(固定Master phrase) | `DECISION_LOG.md:20569/20591`、`CURRENT_SPEC.md:2620` | 両 | VALIDATED(Trial) | Coffee限定`APPROVED_FOR_PRODUCTION`(2026-10-12) | 必須 | welcome=A5、preview_intro=B5のStyleで生成された音声(sha provenance付きseedなら元Styleの由来を一対一で確認) | 前 | 【01B】 |
| 2-2 | Adv Preview=E1(`calm, composed news anchor…`、sha `8862317ff766`) | `CURRENT_SPEC.md:2620`、`OPEN_ITEMS.md` OPEN-350、`er019_family_x_style_profile_01.py` E1_TEXT | A | VALIDATED | Coffee限定採用(2026-10-12) | 必須 | Adv previewのstyle sha=`8862317ff766`。引継ぎ元e_tone_01の「warm, upbeat」やmain既定「calm, conversational」ではない | 前 | 【01B】 |
| 2-3 | Std日本語Preview/Comment1-4=R2(sha `625826c1187b…`、168文字) | `CURRENT_SPEC.md:2624`(V5 (C))、`DECISION_LOG.md:20585`、`docs/pm/delegation_log/2026-10-12_PM-COFFEE-REASSEMBLY…01_01.md` | S | VALIDATED(R2選択、Q1〜Q8 REJECTED) | Coffee限定採用(2026-10-12、再質問禁止)。**SSOT注記**: `CURRENT_SPEC.md:2620`はP2、後段:2624がR2(R2が後勝ち) | 必須 | preview/comment_1-4のstyle sha=`625826c1187b`。v4のP2(sha `4ade8738…`)ではない | 前 | 【01B】 |
| 2-4 | KP英語=K2(`Say the phrase as one single, smoothly connected chunk of meaning…`) | `DECISION_LOG.md:20569`、`er057_output/coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_B.md:25-31`、OPEN-280 | 両(Adv=OPEN-280 CLOSE[委任_04でK2適用]) | VALIDATED | Coffee限定採用(2026-10-12) | 必須(KPが変わるM2P0版でも要再生成) | 各KP英語音声がK2 Promptで生成されている | 前 | 【01B】 |
| 2-5 | KP日本語意味=M2(`一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください…`) | `DECISION_LOG.md:20569`、`prompts_C.md:21-27` | S | VALIDATED | Coffee限定採用(2026-10-12) | 必須 | 各KP日本語意味音声がM2 Promptで生成されている | 前 | 【01B】 |
| 2-6 | Adv KP英英解説=P3(`…Let the sentence flow from its first word to its last…`、sha `a8aaec59…`) | `CURRENT_SPEC.md:2624`(V5 (B))、OPEN-317、REASSEMBLY計画§1 | A | VALIDATED | 判断済み(2026-10-12、再質問禁止) | 必須(必須反映2) | 全KP解説音声がP3 sha | 前 | 【01B】 |
| 2-7 | Full Story Style: PD8→P8→**N01**(上書き履歴) | `DECISION_LOG.md:20591`(PD8)、:20598(P8)、:20941(N01)、`CURRENT_SPEC.md:2620/2621/2625` | 両 | PD8/P8=VALIDATED(Trial)、N01=VALIDATED | PD8(2026-10-12)→P8置換(2026-10-12)→N01置換(2026-10-13、`APPROVED_FOR_PRODUCTION`) | 必須(最新=N01。区分1-3と同一事項の沿革行) | final_03のFull StoryはN01のみ。PD8/P8は無効 | 前 | 【01B】 |
| 2-8 | Std逐語使用+6%減速(Coffee限定例外COFFEE-P8-STD-VERBATIM-EXCEPTION-01→N01でも踏襲) | `er019_family_x_style_profile_01.py:19-27`、`DECISION_LOG.md:20599` | S | 既存 | 採用 | 必須 | Stdに減速指示を重ねない。生成後6%減速 | 前 | 【01B】 |
| 2-9 | In One Line Style=既存承認(E2)で不変 | `DECISION_LOG.md:20591`、`CURRENT_SPEC.md:2620` | 両 | -(既存) | Coffee限定で「不変」と明記 | 必須 | IN_ONE_LINEのstyle sha: S=`10e21170b1b1`(減速指示付き)/A=`63495557ec82` | 前 | 【01B】 |
| 2-10 | Coffee限定Style profile機構(`coffee_n01_r2_p3`+E1 `coffee_n01_r2_p3_e1`) | `er019_family_x_style_profile_01.py`、`DECISION_LOG.md:20941` | 両 | -(実装) | 採用(配線側、Opus条件A済み) | 必須(実装前提) | 「profileに存在するroleだけ」がrunnerで解決される。profile外のrole(K2/M2/A5/B5/IOL)は共通定数のまま | 前 | 【01B】 |

### 区分3: VALIDATED(Trial)だが正式採用されていない/保留(完成版への反映は不可) 6行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 3-1 | 文末ポーズ緩和(新ポーズ基準/後処理/Prompt)OPEN-332 | `OPEN_ITEMS.md` OPEN-332、UDR #27/#31 | 両 | 8way/H-speed/TRIAL-03〜04: VALIDATED(Trial到達上限) | UDR(未採用) | 対象外(採用されていないため完成版に入れてはいけない) | 現行Productionに自動ポーズ基準なし。参考値のみ表示 | 前 | 【01B】 |
| 3-2 | H-speed/8way Voice Prompt候補(K06/K01 NG含む) | `DECISION_LOG.md:20787-20884`、UDR #28/#29/#39 | 両 | VALIDATED(Trial)、K06/K01=ユーザー試聴NG | 未採用(候補選定UDR継続) | 対象外 | 完成版にこれらのPromptを使ってはいけない(N01のまま) | 前 | 【01B】 |
| 3-3 | 異音検知のProduction組込み OPEN-278 | `DECISION_LOG.md:20569` | 両 | -(DEFERRED) | DEFERRED | 対象外 | 組込まない。試聴での確認 | 前 | 【01B】 |
| 3-4 | KP候補選定品質 設計A〜J、KP Idiom/DB Hybrid追加改善 | UDR #9/#26/#30/#32 | 両 | 設計案提出済み/UDR | 未採用 | 対象外 | M2P0(区分1-2)の範囲のみ | 前 | 【01B】 |
| 3-5 | 異音/連結発音: M1(未配線)、OOV(UDR #52判断済み)、F1(WIRED_PENDING_RUNTIME_EVIDENCE) | UDR #52-55、`REPORT_LEDGER.md:289` | 両 | F1: 実装済み | F1/M1は別評価(2026-10-14) | F1=今回対象(自然発生evidence取得対象)/M1=対象外 | F1再判定が英語4segmentに記録される(`F1_RUNTIME_EVIDENCE_02.md`)。M1は配線なし | 前 | 【01B】 |
| 3-6 | Coffee原稿正本 U1/U2(v5 Tone原稿 vs Production L3原稿) OPEN-326 | `OPEN_ITEMS.md:829`、UDR #4 | 両 | - | UDR(暫定、SSOT根拠行特定不可)。X-1「v5原稿維持を推奨」(WIRING_DESIGN_01:114/229)で進行 | 要判断 | どちらの原稿を完成版に使うかがユーザー承認済みか。final_03はv5(Tone)原稿 | 前 | 【01B】 |

### 区分4: ユーザーが今回の完成品への反映を個別に指示した仕様 8行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 4-1 | **In One Line 2文基本(必要なら3文)**(新方針、OPEN-299) | `IN_ONE_LINE_REWRITE_01.md:5`、`OPEN_ITEMS.md:802`、`DECISION_LOG.md:20591` | 両 | 「Trial」ではなく**v3制作時の個別指示**(IOL新原稿gpt-6-luna各1 call、`iol_final_text_01.json`)。VALIDATEDの記録なし | ユーザー決定(2026-10-12)=v3へ適用。**仕様化は未承認・未起票の承認(OPEN-299 OPEN候補)** | 今回対象(必須反映5点の1番目「確定したIn One Line関連仕様」。ただし仕様が未確定のまま) | S: 2文(例 `Coffee bean prices fell, but…`/`Other costs also matter…`)、A: 2文。1文目=核心、2文目=意味・示唆。新fact・新数値なし。Comment 4の2論点(時期・他の費用)を回収 | 前 | 【01B】 |
| 4-2 | 必須反映5点(IOL確定仕様/P3/R2/変更対象音声の更新/runtime evidence+試聴ページ確認) | `docs/pm/design/…REASSEMBLY-PLAN-01.md:8-16`、`DECISION_LOG.md:20644`、OPEN-321 | 両 | - | ユーザー指示(2026-10-12) | 今回対象(必須) | 5点がfinal_03で全て満たされること。特に4「既存音声の流用だけで済ませず」 | 前 | 【01B】 |
| 4-3 | 正式経路で完成版を作成/旧版と区別できる試聴ページ(対象音声・生成日時・適用仕様) | `COMPLETION-01_01.md:158-181` | 両 | - | ユーザー指示(2026-10-13) | 今回対象 | ページに生成日時・適用仕様が識別可能。旧ページに「途中段階」注記 | 前 | 【01B】 |
| 4-4 | 聴感判断材料の掲載(Std 6%減速後WPM、Adv WPM、文末ポーズ、聴きやすさ) | `…委任_04.md:6`、UDR #49 | 両 | 参考値のみ(Trial値は合否基準ではない) | Deferred(タイミング合意済み) | 今回対象 | 試聴ページに数値掲載。新Gateは作らない | 前 | 【01B】 |
| 4-5 | Adv Comment 1-4のE0は新規採用を承認していない(既存承認Styleか確認) | `…委任_04.md:3`、OPEN-350 | A | - | 「新規採用は承認していない」(2026-10-14) | 要判断(既存承認の整理) | Adv Comment Styleの正本(CURRENT_SPEC:2620はE0、e_tone_01は「warm, upbeat」)が決まっていること | 前 | 【01B】 |
| 4-6 | Fragment候補はC4「当面変更なし・A′の結果を確認」を選択済み | UDR #58、`…委任_04.md:2` | 両(X) | - | 判断済み(2026-10-14) | 今回対象 | 原文窓の拡張が原文外に出ない。不自然・長すぎるKPを採用しない | 前 | 【01B】 |
| 4-7 | 「Production作業の受入条件」(正式初回経路/retry/fallback/regen/Regression/runtime evidence/model_id/SSOT/Git) | `…委任_04.md:6` | 両 | - | ユーザー指示(2026-10-14) | 今回対象 | 未完了があれば`PRODUCTION_WIRED`と報告しない | 前 | 【01B】 |
| 4-8 | 「承認済み範囲を照合して進めよ」(CURRENT_SPEC・過去ユーザー決定との照合) | `COMPLETION-01_01.md:7節` | 両 | - | ユーザー指示(2026-10-13) | 今回対象 | 完成版作成時にSSOTの承認済み事項を照合する | 前 | 【01B】 |

### 区分5: Trialしたが不採用・保留・対象外 6行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 5-1 | Comment 4 Trial-01(C0〜C4)・Trial-02(長すぎ/67字条件) | `OPEN_ITEMS.md:819`(OPEN-316)、`DECISION_LOG.md:20623-20631` | S | REJECTED(Trial-01全候補) | 不採用(2026-10-12)。採用は5-1ではなくTrial-03(区分1-5) | 対象外 | 完成版のComment 4はTrial-03採用Promptであり、C1/C2文面ではない | 前 | 【01B】 |
| 5-2 | Std日本語 Q1〜Q8 | `REPORT_LEDGER.md:269` | S | REJECTED | 不採用(2026-10-12) | 対象外 | R2のみ使用 | 前 | 【01B】 |
| 5-3 | P2(Std Preview/Comment旧採用)、PD8、P8、Adv KP解説P5/P8推薦 | `DECISION_LOG.md:20569/20591/20598`、OPEN-317 | 両 | (置換済み) | 後続決定で無効(R2/N01/P3) | 対象外 | 旧Style音声が残っていない | 前 | 【01B】 |
| 5-4 | `raw-bean`等ハイフン修飾語の一律除外 | `…委任_04.md:2` | 両 | - | 認めていない(2026-10-14) | 対象外 | 導入されていない | 前 | 【01B】 |
| 5-5 | G1/G2/G3(gloss再整合の選択肢提示) | UDR #57 | S | - | 判断不要(基本品質要件)。G2「拡張KPを自動でHuman Reviewへ」を標準対策として推奨しない | 対象外 | Human Reviewに戻さない | 前 | 【01B】 |
| 5-6 | Family Z側のIn One Line(Z-3)/N01の「true story」文言 | `DECISION_LOG.md:20593`、UDR #46 | Z | - | Z-3不採用(superseded)、N-2判断済み | 対象外(Coffeeには無関係) | Coffeeの判断材料にしない | 前 | 【01B】 |

### 区分6: Coffee完成後(final_03: 2026-10-14)に承認/変化した仕様 3行
| # | 仕様 | 出典 | 対象 | Trial | ユーザー判断 | 適用要否 | 期待動作 | 前後 | 実際/判定/原因 |
|---|---|---|---|---|---|---|---|---|---|
| 6-1 | **corrected gloss再整合工程**(`APPROVED_FOR_PRODUCTION`、付随事項3件)。旧legacyは撤去(共存させない) | `OPEN_ITEMS.md` OPEN-356、`CURRENT_SPEC.md`KGCPW 委任_01追記、`REPORT_LEDGER.md:302` | 両(X/Z) | KGDC: VALIDATED | 正式採用(2026-10-15) | final_03には含まれない(後)。再生成要否は委任_02で判断(Std KP #4等) | 当時のCoffee final_03はlegacy工程で作成。corrected版は配線中(KGCPW 委任_02) | **後** | 【01B】 |
| 6-2 | gloss再整合 flag既定OFFの安全措置(2026-10-15)・Z実LLM evidence | `REPORT_LEDGER.md:298-300` | 両 | - | ユーザー承認の安全措置(後続で撤去対象) | 対象外 | final_03(2026-10-14)はflag既定ON時代の挙動 | **後** | 【01B】 |
| 6-3 | Day2運営モデル(UDR #59 U1〜U4、F3独立受入等) | UDR #59、`REPORT_LEDGER.md:293` | - | Research | USER_DECISION_REQUIRED | 対象外(Coffee完成版の仕様ではない。再発防止の検討事項のみ=`A_ROOT_CAUSE_CANDIDATES_01.md`) | - | 後 | - |

### 区分D: 音声品質・完成状態の期待(参考値と正式基準の区別) 追加7行(区分外・観点別)
| # | 観点 | 出典 | 期待(正式 or 参考の別を明記) | 実際/判定/原因 |
|---|---|---|---|---|
| D-1 | WPM | `CHECKLIST_05.md:21`、UDR #49 | **参考値のみ**(Std 157±6、Adv 167±6はTrial値。Production合否基準なし) | 【01B】 |
| D-2 | 文末ポーズ・長い無音 | 同上 | **参考値のみ**(Std ref<=498ms、Adv ref<=593ms、800ms以上の無音の件数も参考) | 【01B】 |
| D-3 | ASR検証(減速後含む) | `CHECKLIST_05.md:11` | **正式基準**(既存ASR判定、減速後再検証) | 【01B】 |
| D-4 | Audio Validation Gate/M3 Style Gateの走査範囲 | `CHECKLIST_05.md:9`(#3の限界) | **正式基準**。ただし固定Master phrase(welcome/preview_intro等)はseed(sha provenance)で`tts_generation_results.json`外=Gate走査対象外(既知の限界) | 【01B】 |
| D-5 | 再利用音声のValidation継承(`REUSED_VALIDATED`) | `er019_family_x_validation_inheritance_01.py`、`FIX2_DESIGN_01.md` | **正式基準**。継承時にtext一致を確認(`expected_text`)。ただしstyle shaは見るがspec上の文面(文数)は見ない | 【01B】 |
| D-6 | 完成MP3と試聴ページの内容一致 | `CHECKLIST_05.md:31` | 試聴ページのaudio参照51件が全て実在/再生可(Playwright 51/51)。内容(原稿)一致は別 | 【01B】 |
| D-7 | 不自然な日本語読み | UDR #12、JA-ASR #24 | 正式基準未整備(UDR)。聴感で確認 | 【01B】 |

### 件数(46行+D 7行)
区分1=13、区分2=10、区分3=6、区分4=8、区分5=6、区分6=3(合計46)。D=7(区分外)。判定列は未記入(01B/委任_02)。

### 暫定観測(仕様側調査中に偶然確認。**判定ではない**、01Bで再確認が必要)
- final_03のIn One Line: `a2/audit/tts_generation_results.json` segments.in_one_line.text=「Falling coffee bean prices may take at least 9 months to affect US shop prices.」(1文、6.225秒)、`b1b/…`=「…US retail prices.」(1文)。ASR済み。
- Adv In One Line: v3の2文版wav(sha先頭`645cac39d8a6`、641,324 byte)は`b1b/narration/_replaced_02/in_one_line.645cac39.wav`へ退避され、現在の`b1b/narration/in_one_line.wav`(sha先頭`897ca8bf983e`、253,484 byte)に置換されている。
- Style sha(実測、`tts_generation_results.json`): Std KP日本語意味=`ae68e3e6ac8e`(J3、M2ではない)、Std KP英語=style_prefix空(既定、K2ではない)、Adv KP英語=`2b0c7505f48e`(`Speak the following short phrase aloud naturally… warm podcast announcer voice`、K2ではない)、Adv KP解説=`a8aaec591ef6`(P3一致)、Adv Preview=`8862317ff766`(E1一致)、Std Preview/Comment1-4=`625826c1187b`(R2一致)、Full Story全6=`d1956c91c925`(N01一致)、Adv Comment1-4=`57c3fda67c1d`(`calm, conversational`=E0)。
- profile定義: `er019_family_x_style_profile_01.py` `STYLE_PROFILES`/`ROLE_SEGMENTS`/`ROLE_LEVELS`にK2/M2/A5/B5/IN_ONE_LINE用overrideは存在しない(L16の注記「他Role(K2/M2/A5/B5/E1/R2等)は後続Phase」)。
- Std KP #4: `keywords_canonicalized.json:116,147`: key_phrase=`based on interviews`、gloss `インタビューをもとにした`(legacy再整合で`～をもとにした`から書換え、`status=GLOSS_REALIGNED`)。

## §3 Gate 7・Closeout Checkの観点: final_03完成宣言時(CHECKLIST_05)に「必要仕様の網羅性確認」があったか

出典: `er071_output/m2p0_n01_production_wiring_01/completion_04/CHECKLIST_05.md`(全33行、逐語)。

**あった項目(逐語)**
- #1 正式初回経路 / #2 「retry/fallback/regen整合」/ #3 「Trial専用実装に依存しない」(限界として「Std/Advの固定Master phrase(welcome=A5/preview_intro=B5ほか)はsha256 provenance付きseed(再生成なし)で、`tts_generation_results.json`に載らずAudio Validation Gateの走査対象外」)/ #4 Regression/ #5 「正式経路でのruntime発火」/ #6 「actual model_id/routing」/ #7 「CURRENT_SPEC更新」「充足(今回追記)」/ #8 DECISION_LOG更新 / #9 OPEN_ITEMS更新・整理 / #10 commit/push / #12 Dangling Reference。
- #11 「承認内容とProduction挙動の一致」: 「**未充足**: (a)gloss再整合工程は新Production処理フロー…ユーザー承認・Opus条件A・Fable判定が未実施。(b)Std Preview/Comment=R2・Std KP=既存・Adv=E1/P3/N01は承認内容と一致。(c)E0は既存承認済みと一致(`E0_RECONCILIATION_04.md`…)」。
- 「未充足一覧」4件: ①#11 gloss工程の採用位置づけ ②UDR #49(聴感) ③「固定Master phrase seedがAudio Validation Gate走査対象外」④OPEN-350のClose可否。

**なかった項目**
- In One Lineの文数・内容(CURRENT_SPEC:583の正式仕様、OPEN-299の2文方針のいずれも)。CHECKLIST_05内に「In One Line」の語は0件(rg確認)。
- KP英語K2/KP日本語意味M2の照合。#11(b)は「Std KP=既存」としており、K2/M2の承認(2026-10-12 Coffee限定)に対する照合ではない。
- Intro A5/B5の一対一照合(#3は「seedでGate対象外」と書くのみで、承認Styleとの照合は未実施)。
- Adv Comment 1-4のStyle(E0 vs e_tone「warm, upbeat」)は(c)で整理したが、OPEN-350の判断待ち。
- 必須反映5点(REASSEMBLY計画)・OPEN-321・OPEN-316・OPEN-299への参照: 0件(`er071_output/m2p0_n01_production_wiring_01`と`docs/pm/delegation_log/2026-10-1[34]_FAMILY-XZ*.md`をrg、いずれも0件)。
- 「承認済み仕様の全件照合表」(仕様マトリクス相当)。#11が最も近いが、照合範囲が上記(a)(b)(c)のみ。

**PM_GOVERNANCE上の位置づけ**: CHECKLIST_05は「Production Wiring Checklist 1-12」(Gate 3系)で、`docs/pm/PM_GOVERNANCE.md:243-246`のGate 7(「approved specとの一致」を受入判定に含める)の具体化にあたるが、Gate 7補足(a)〜(m)(`:248-`)は音声artifactの「見える項目」確認(Preview/Comment全件/本文/KP英語+日本語gloss/…)であり、承認済み仕様の網羅照合を要求する項目は無い。Closeout Mandatory Check(`:476-`)も項目3「正式採用項目が追跡済みであること」・項目7「CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSとの整合」は「SSOT記載の整合」であり、「ユーザー要求項目が完成物に反映されたことの照合」を直接は求めない(既存機構の解釈ギャップ。新Validator提案ではない)。
