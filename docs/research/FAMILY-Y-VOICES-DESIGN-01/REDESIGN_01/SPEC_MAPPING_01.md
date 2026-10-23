# SPEC_MAPPING_01: 既存承認仕様と今回(USER_03)の改善事項の対応表(委任_07 Phase A)

Status: 調査のみ(API 0)。照合元(ファイル:行): `CURRENT_SPEC.md`(B-Family Voices節 :668-690、Family Y言及 :1476/:1646/:1684)、`DESIGN_PROPOSAL_02.md`(:100,:170,:190-217,:289,:343)、`INVENTORY_X_Z_SPEC_01.md`(:36-50,:77,:82,:218)、`INVENTORY_OLD_B_VOICES_01.md`(:25-27,:39-41,:65,:186,:202,:210,:227)、`USER_02.md`(:8-48,:140)、`USER_03.md`全文。
区分: **A**=承認済み仕様の範囲内 / **B**=承認済み仕様の変更が必要(ユーザー判断) / **C**=Family Y固有(Trial設計・未承認だが他Familyに影響なし) / **D**=未承認候補(Trial検証後にユーザー判断)。
重要: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_03.md`が明示した改善事項は、Family YのTrial(DEV経路)について**指示済み**。ただしProduction採用は未承認で、「指示済み」は採用の承認ではない(USER_03 §9)。

## 1. 構成・音声

| # | 改善事項(USER_03) | 既存仕様/先例(根拠) | 区分 | 影響・メモ |
|---|---|---|---|---|
| S1 | Comment 1=テーマ導入(人物説明なし) | Xの正式仕様: Comment1〜4はPRODUCTION_WIRED。C1=「次に聞く焦点(答えを言わない)」、Std=日本語Aoede/Adv=英語Charon、役割文は`er019_family_x_audio_plan_01.py:181-236`(`INVENTORY_X_Z_SPEC_01.md:50`)。DP02はComment1=焦点・Comment2=リード回収+橋・Comment3=聞き終えた視点移動(`DESIGN_PROPOSAL_02.md:204-206`)。 | **C(Y用role新設)+ユーザー指示済み** | Xの`COMMENT_*_ROLE`は無変更。Y専用の`Y_COMMENT_1_ROLE`(テーマ導入)を新設。X C1の「答えを言わない」型とは役割が異なる(背景・問題を提示)。台帳外のFactを足さない規則は維持(X C3/C4の「新しいFactを追加しない」準拠)。**Previewとの重複**(Preview=聞く価値・問い、`CURRENT_SPEC.md:1719`Preview原則)に注意し、重複検査を評価基準に入れる。 |
| S2 | Comment 2=Voiceへの導入(人物紹介繰返しなし・C1と重複なし) | 同上。 | **C+ユーザー指示済み** | `Y_COMMENT_2_ROLE`新設。Comment 3(聞き終えた後)・Comment 4は**置かない**(USER_03の構成にComment3が無い。Comment4廃止はUSER_02で既決、Comment3廃止は今回のUSER_03の構成指示による変更。DP02のComment3案は不採用)。 |
| S3 | 5パート `full_story_part1〜5` との対応(part1導入をComment1/2へ分割するのか) | DP02の5パート=リード/V1/V2/V3/最終(`DESIGN_PROPOSAL_02.md:192-196`、USER_02 §1「本文は5パート固定」)。 | **B寄りだがUSER_03の構成指示で事実上改訂(確認事項UJ-1)** | USER_03の構成(Comment1/Comment2/見出し+Voice×3/Tension+Closing)では、リード段落の役割(導入)をComment1/2が担うため、**本文のリード段落が不要になる**。推奨(案A)=本文4パート(V1/V2/V3/最終=`full_story_part1〜4`)+Comment1/2はscaffold(Xと同型)。代替(案B)=本文5パート維持でpart1を語り手導入とする(ただしComment1/2と二重になる)。USER_03はリード段落に言及しない。 |
| S4 | Voice直前にナレーターが短い見出しを読む(例`One Voice: …`) | 旧B: 「Narrator見出し=Aoede」APPROVED_FOR_PRODUCTION(2026-09-08, `INVENTORY_OLD_B_VOICES_01.md:27`)。`One Voice:`/`Another Voice:`はASR欠落でHR Lock(F11, 同:210、是正済み=独立予算経路`generate_narrator_heading_with_a2_slowdown`、`er012_b_family_voices_a2_production_01.py:740`)。Xは見出し読み上げを廃止(SE-1 CLOSED、`INVENTORY_X_Z_SPEC_01.md:48,218`)。DP02 C13はYでも不採用とした(`DESIGN_PROPOSAL_02.md:170`)。Zは登場人物別Voice(Dialogue clip、`:77`)で見出し無し。 | **A(旧Bの承認済み先例あり)+Xの廃止方針とは相違=ユーザー指示でY Trialに限り上書き。Y固有(C)** | DP02 C13の「見出し読み上げを使わない」はUSER_03で上書き(Trial範囲)。音声RoleはNarrator Aoede(Std/Adv共通のFull Story系narrator。Adv Charonは案内系のため見出しには使わない)。既存の`generate_narrator_heading_with_a2_slowdown`をimportして使う(共有コード無変更)。F11再発防止として接続句(`One Voice:`等)のASR欠落をPhase Bで確認(見出しclip単体TTS/ASR、数円)。 |
| S5 | Std英語の減速 | 標準A2の6% slowdownをVoice A/B本文・Narrator見出しを含む全英語segmentへ適用(`CURRENT_SPEC.md:680` B-A2-9, PRODUCTION_WIRED)。Xは`full_story_part1/2`対象(part3はOPEN-466のガード穴)。Y Trialでは「減速あり/人物の語りだけなし」を併置比較(`TRIAL_SUMMARY_01.md §5`)。UDR #167②が試聴判断待ち。 | **A(既存減速)/ D(Voice partの減速有無)** | USER_03指示で「Std減速の有無は新Trialページで再判断」。**Voice part減速の有無はD(ユーザー試聴で判断)**。本設計は既存どおり全narration segment減速ありを基準とし、Voice partのみ無し版を無料(API 0・再組立)で併置できるようにする案を維持。 |
| S6 | 3 Voice固定(Algieba/Zephyr/Schedar) | USER_02 §1(固定仕様、自動割当不採用)。 | **A(ユーザー決定済み)** | V1=Algieba男性的/V2=Zephyr女性的/V3=Schedar男性的を前提にPersonaの性別・年齢感を設計(PERSONA_CANDIDATES_01.md)。 |
| S7 | Tension+Closingを1パートに、具体的に整理・抽象化しすぎない | USER_02 §1(独立Closing廃止、5パート目=Tension+Closing)。旧BのTension「共通前提→分岐点→非対称性」は承認済み(`INVENTORY_OLD_B_VOICES_01.md:190`)。DP02 D1の締め2〜3型と「再要約なし」規則(`DESIGN_PROPOSAL_02.md:196`)の規則自体は設計案。 | **A(構造)/C(具体化規則=Y設計)+ユーザー指示済み** | 「再要約なし」をそのまま守ると具体的整理と衝突するため、「順番に全員を要約する」ことは避けつつ「違いの軸を具体名詞で対比する」ことは許容へ精緻化(DESIGN_PROPOSAL_03 §4-5)。旧Bの承認済み原則(再要約・時系列反復を避け違いを浮き彫りに)の趣旨は維持。 |
| S8 | In One Line | Xの仕様(基本2文)を維持(USER_02が基盤指定、`DESIGN_PROPOSAL_02.md:208`)。 | **A** | 無変更。Tension+Closing末尾が要約・教訓にならない規則と合わせIn One Lineと役割分担。 |
| S9 | R0のみ・R1/R2は削除/変更しない | USER_02はR0→R1→R2全段Trialを指示、USER_03が「R0のみ」へ再変更。Xの既存R1/R2 Production、Y用R1/R2 DEV runner(`er110_family_y_text_trial_01_run.py`)は維持。 | **ユーザー指示済み** | R1/R2は今回呼ばない(コード無変更)。将来のR工程は未決定。OPEN-217のY方針はこれで確定したわけではない(USER_03:「別目的のRevisionの可能性あり」)。 |

## 2. 本文生成・検査

| # | 改善事項 | 既存仕様/先例 | 区分 | 影響・メモ |
|---|---|---|---|---|
| G1 | Persona→Voice工程(Persona Sheet先行、主張の後付け禁止) | 旧B: Voice Cardを人手作成してWriterに注入、専用ペルソナ生成Promptは存在しない(`INVENTORY_OLD_B_VOICES_01.md:68`)。Y Trial: Cast+Card自動生成(`er110:225-279`、DP02 D2「Voice Card半自動生成」は開示事項)。 | **C(Y固有)+ユーザー指示済み** | Persona Sheet(Card後継)を新設。Card→Sheetの項目拡張。X/B/Zの既存コード無変更。 |
| G2 | 生徒(未成年)・保護者・教師を含め当事者を広く検討 | `er110:242`が「未成年本人は避け」としていた(設計者判断、未承認)。 | **C(設計者判断の撤回)+ユーザー指示済み** | 声は成人TTS固定のため、生徒Personaは成年(18〜20歳、定時制等)で設計する(PERSONA_CANDIDATES_01.md)。高校生本人(16〜17歳)を成人TTSが読むことの違和感は**未検証の品質論点**(D、Opus論点)。 |
| G3 | Voice本文: 約190字→「主張+具体論+主観・感情」、場面固定の冒頭を廃止、本人の要求・願いを許容 | R0 Prompt固定文言は未承認設計(`er110:366-367`)。旧B承認済みの原則: 一人称"I"(2026-09-08)、Voice Card起点、Evidence脇役、迷い許容、他Voice中心論点を抱え込まない(`INVENTORY_OLD_B_VOICES_01.md:227`)。旧BのLeakage定義(`er110:434-441`)の「Writer自身の解決策提案」は**語り手/Writerの提案**を対象とし、Voice本人の要求・願い(「〜してほしい」)の禁止ではない。 | **C+ユーザー指示済み。A(旧B承認原則)は維持** | 「解決策・提案は語らない」(`er110:367,568`)は旧B承認ではなくDP02由来の設計案 → 「本人の願い・要求は可、政策設計や根拠データの論証は不可」へ改訂(撤去/変更規則の一覧=DESIGN_PROPOSAL_03 §9)。数字禁止(M1/DP02開示事項、`er110:377`)は維持。 |
| G4 | 本人が知っていそうな事実を自然に使う(件数の目的化なし) | M1: Voice段落に世界スコープ事実1件まで許容(DP02, Opus M1)、Voice段落の数字は使わない(開示事項)。旧B: 候補C「本人経験の数値のみ・最大1つ」、Evidence脇役。Fact Safety/Writer原則「体験claimの根拠付け」(`CURRENT_SPEC.md` B-Family節、恒久原則)。 | **A(Fact Safety・Evidence脇役は維持)/C(M1改訂)** | 「Persona Sheetに事前登録した台帳Fact(0〜1件/Voice)を、本人が主語・本人の言葉(伝聞・印象)で1文以内」へ精緻化。台帳外の事実・数値・統計の創作禁止(USER_02 :46)は維持。Persona自身の生活場面(Sheet内)は「人物スコープ」で、統計・制度・他者組織の事実ではない(M1(a))。 |
| G5 | Leakage Checkと設計の矛盾解消(OPEN-470) | 旧B承認済みAnalytical Leakage Check 7+6項目・Acceptance Gate・局所書き換え(DP02継承A)。USER_02「対策が強すぎて人物の自由な発言を阻害しないか評価すること」(:48)。 | **C(Y用Gate適用の調整)。旧B検査項目自体は維持(A)。ア/イ/ウの選択は従来『設計変更=ユーザー判断』だがUSER_03 §5が検証を明示指示** | DESIGN_PROPOSAL_03 §5で「アの限定版」を推奨(検査定義は変えず、Sheet許容事実のみ形式条件付きで例外)。旧B(Production)の検査コードは無変更。 |
| G6 | 英語化(忠実英訳/Std簡易化)・RF | X正式経路の再利用(A)。RFは人物の自己紹介文を台帳外としてflag(R0 Adv 2件、`EN_COMPARISON_01.md:33`)。 | **A** | Sheet由来文のRF flagは評価時に「想定内」として別集計(Gate化しない)。本文は4パートになるため、英訳の段落数確認をY wrapperで4に更新(`DESIGN_PROPOSAL_02.md` T4の型を踏襲)。 |
| G7 | 見出しの生成 | 旧Bは固定生成(Writer出力の`###`見出し)。 | **C** | 本文英訳の契約を壊さないため、見出しは本文とは別の小さなLLM call(Luna)で、Gate通過後のVoice段落+Sheetの一行主張から日本語・英語を同時生成(ordinal prefixは決定論)。DESIGN_PROPOSAL_03 §4-3。 |

## 3. segment-id・TTS・ページ(M3/M4)への影響

| 項目 | 現行(Y Trial、DP02 §5) | 新構成での変更 | 区分 |
|---|---|---|---|
| 本文segment | `full_story_part1〜5`(リード/V1/V2/V3/最終) | 案A: `full_story_part1〜4`(V1/V2/V3/最終)。Y用タプル・parity testのpart数を5→4へ。part4(最終)はXのpart1〜3の外なのでresolve_narrative_roleのpart4追加の扱いはDP02 §5-5のまま(加算のみ、Xへ影響なし)。part1〜3はXと同じIDなので共有検査の対象になる(むしろM3リスクは縮小) | C |
| 見出しsegment | なし | 新規`voice_heading_1〜3`(alias ID。旧Bの`point_one_heading`相当)。Y runnerのsegment順タプル・timeline builder・Local Rewrite対象外(`INVENTORY_X_Z_SPEC_01.md:82` Heading Readoutは適用外)・Style(Narrator短文、Std減速)を新設 | C |
| Comment segment | Y版Comment1〜3(DP02) | Comment1/2のみ(命名はXと同じ、Y用role)。Comment3削除 | C |
| reuse key(M4) | Y runner側でTTS Voice名をkeyに含める | 変更なし。見出し・CommentはAoede/Charon固定、Voice partはAlgieba/Zephyr/Schedar固定のため、Voice名照合は継続 | C(既存) |
| TTS/ASR/検査 | Y版audio runner | 見出しは短文(5〜9語)でASR欠落(F11)が起こり得るため、既存`generate_narrator_heading_with_a2_slowdown`(独立予算経路)を呼ぶ。Audio Validation Gate(required_structure)は旧Bの`B_FAMILY_A2`キーに`point_*_heading`あり(`CURRENT_SPEC.md:688`)、Yは自前確認で代替(Xの共有gateへの"Y"登録はProduction変更にあたるため本Trial対象外、INHERITANCE T13と同じ扱い) | C |
| ページ | Y用page script | 全スクリプト表に見出し行を追加(内部IDは非表示、標準ページ形式) | C |

## 4. ユーザー判断が必要な項目(判断候補。ラベル`USER_DECISION_REQUIRED`はFableのみ)
| ID | 内容 | 区分(27-3) | 根拠 |
|---|---|---|---|
| UJ-1 | 本文の「リード段落」を廃止し「5パート固定」(USER_02 §1)を4パートへ(案A)。それとも5パート維持(案B)か | B(承認範囲内で自己解決): USER_03のComment1/2構成が事実上案Aを指示している。Trialは案AでDEV経路のみで検証でき、採用判断は試聴後 | USER_02 :8 vs USER_03 §6。Sonnetは案Aで進行して差し支えないと見る(Fable確認を希望) |
| UJ-2 | Voice part(Std)の減速の有無 | D(試聴判断、UDR #167②を新Trialへ引継ぎ) | USER_03 §0(再判断) |
| UJ-3 | 成人TTSでの高校生(未成年)Personaの採否(本Trialは成年生徒で回避) | C〜D(Trialでは回避可、採用時の方針) | G2 |
| UJ-4 | R1/R2・将来のRevision工程の扱い | ユーザー別途指示待ち(USER_03:「未決定」) | S9 |
| UJ-5 | Trial費用上限(残74.62円)での反復回数。2回目(音声込み)の高位推定とArm G検証まで確保するには+約20〜40円が必要(1回目音声込みは残74.62円に収まる)(DESIGN_PROPOSAL_03 §8) | 7-7: 個別Cap超過=Fable報告対象 | §8 |
