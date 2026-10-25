# SPEC_LEDGER_01: Family Y 仕様差分台帳(X/Z/共通仕様との差分と追跡)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01(Phase 0) / 2026-10-25(JST) / **API 0・Production変更0・有料run 0**
ユーザー正式決定(逐語): `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`(sha256 e7958343…。原文は取得元jsonlで既に文字化けしており、そのまま無改変で保存。内容は委任文§0の要旨に依拠)。委任文逐語: `..._DELEGATION_01.md`。
機械可読版: `spec_ledger_01.json`(同一データ。将来のCloseout Checkはこちらを参照する)。

## 0. 読み方(先に必ず)

- 本台帳は2026-10-23の棚卸し(`FAMILY-Y-VOICES-DESIGN-01/INVENTORY_X_Z_SPEC_01.md`)を出発点に、**2026-10-24〜25に承認・配線された共通仕様**(KP一般化[OPEN-474]・Part 1[OPEN-512]・KP/文法HR[OPEN-518]・Part 2[OPEN-519]・Chunk TTS・中核数値保持v4/J2・Closing一般化・案B個別採用ほか)を追加して作り直したもの。**出発点の一覧を網羅済みとみなさず**、`CURRENT_SPEC.md`の節見出し・`OPEN_ITEMS.md`(OPEN-415〜519)・`PM_GOVERNANCE.md` 28-1運用7を再照合した。CURRENT_SPECの行番号は10-23時点から移動しているため、本台帳は**節見出し名**で参照する(行番号を併記したものは2026-10-25時点)。
- 事実=SSOT/コードを実際に読んだ内容。**仮説・未確認は明記**する。Status語彙: `APPROVED_FOR_PRODUCTION`(ユーザー承認済み・配線は別)/`WIRED_PENDING_FABLE`/`PRODUCTION_WIRED`(Family別・仕様別。1Familyの成功を他Familyの証拠にしない)/`VALIDATED`(Trial評価。Production仕様ではない)。
- 分類: **A**共通 / **B**X基盤 / **C**Y固有 / **D**X・Z固有 / **E**旧Family B由来 / **F**進行中・Trial中。
- Y適用要否: **適用**(Y Productionへ組込)/ **Y固有実装** / **除外**(理由記録)/ **判断待ち**(下記§3)/ **未承認=先行採用禁止**(承認後に再判定)/ **適用(依存実装後に接続)**(進行中仕様。確定I/Fに依存)。
- Y配線Status(現状)は全行「Y正式Production入口が存在しない」ことに起因して**PRODUCTION_WIREDなし**。DEV Trialで動いている部品は「DEV Trial」と明記し、Production到達とは区別する(`production_reachable=False`、`er110_family_y_audio_trial_01.py:176`)。
- 既存の追跡装置(新設しない): (1) `CURRENT_SPEC.md`「共通仕様のFamily別配線Status表」(Y列が現在は『未着手/未定』) (2) `OPEN_ITEMS.md` OPEN-484(Y Production化時の必須受入条件) (3) PM_GOVERNANCE 28-1運用7・Closeout Mandatory Check。本台帳は(1)(2)の**Y列を埋める作業表**であり、新Gate・新報告工程ではない。

## 1. 件数サマリ

| 区分 | 件数 |
|---|---|
| 台帳行 合計 | **55** |
| 適用 | 26 |
| Y固有実装(Yで新規実装) | 11 |
| 適用(依存実装後に接続: KP HR・文法HR・Part 2) | 3 |
| 除外(理由記録) | 7 |
| 判断待ち | 4(すべて§3に理由。ユーザー判断が必要なのは1件、Fable確認で足りるのは3件) |
| 未承認=先行採用禁止 | 4 |
| 分類別 | A=24 / B=2 / C=12 / D=5 / E=3 / F=9 |

主要な差分(Yだけが持っていない/Yだけが違うもの):
1. **Y正式Production入口が無い**(OPEN-484)。X/Zは全工程が`er019`/`er026`のrunnerに配線済み、YはDEV `er110_family_y_*`のTrial runnerのみ。
2. **共有scope定数がX/Zのみ**(`er103...:42`、`er109_xz_scope_01.py:25`)=PNAP・er109がYで非活性。
3. **routing keyにFAMILY_Y_*が無い**(`er006_model_routing_contract_01.py`をGrepして0件)=未登録modelはfail-closedなのでYのProduction callは起動不能。
4. Xの前提(Research/Ledger/B3/Fact Lock Writer/RF/3分割/Comment4/In One Line)とYの設計(実在意見ベース・5パート・Comment3・In One Line廃止)の**構造差**。Y用splitter・timeline・role文が必要。
5. 進行中の共通仕様(KP/文法HR=er119、Part 2=er120)は**Yの接続点が未確定**(別agent実装中)。接続点として明記し、確定I/Fに依存する。
6. 本セッション内で**新規に追加された共通仕様4件**(Chunk TTS・中核数値v4/J2・KP一般化・Part 1)のうち、Chunk=承認原文X/Zのみ(Yは判断待ち)、中核数値=Y対象外と明記(除外)、KP一般化・Part 1=Yへ適用(OPEN-484等)。

## 2. 差分台帳(各行: 仕様ID・名称/分類/承認Status/承認根拠/X・Z配線/Y適用要否/Y配線Status/残作業/追跡先/完了証拠)

### §2-1 C: Y固有仕様(Yで新規に実装・追跡)(12件)

| ID | 仕様 | 分類 | 承認Status | 承認根拠 | X配線 | Z配線 | Y適用要否 | Y配線Status(現状) | 残作業 | 追跡先 | 完了証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YL-C01 | Y 5パート構成(リード/Voice1/Voice2/Voice3/Tension+Closing)・独立Closing廃止 | C | APPROVED(ユーザー決定) | USER_LAUNCH §2-1(2026-10-25)/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02(基本設計確定)/OPEN-463(OPEN_ITEMS.md:976) | N/A | N/A | **Y固有実装** | DEV Trialのみ(production_reachable=False、er110_family_y_audio_trial_01.py:176) | Y Production runnerのsegment計画・timeline・splitterに実装 | OPEN-520 / OPEN-484 | 正式E2Eで5パートの順序・話者対応検査(mapping_check_revised相当)PASS |
| YL-C02 | 3 Voices固定・3立場・人物像から一人称で主観的に語る(迷い許容、他Voice中心論点を抱え込まない) | C | APPROVED(ユーザー決定) | USER_LAUNCH §2-1 / OPEN-463 確定済み基本方針 | N/A | N/A | **Y固有実装** | DEV Trial(opinion_based_03 runnerでVoice R0生成) | Voice生成stage(Persona Sheet入力→Voice R0→Leakage Gate)のProduction module化 | OPEN-520 | Voice Leakage Gate PASS・一人称検査PASS・正式E2E |
| YL-C03 | 実在意見ベース方式(Theme Package=World frame+Persona Sheet+出典付き意見採録→Voice R0のみ。R1/R2エンタメ性upは不使用) | C | VALIDATED(限定、2テーマ)。Production採用の明示文は委任文要旨内に未確認 | OPEN-463(委任_19〜26)/FABLE_EVAL_03/USER_LAUNCH §2-1,§5『3 Voice生成』 | N/A | N/A | **判断待ち** | DEV Trial(再配達R0 Gate PASS、SNS R0 Gate PASS) | Launch §5が『3 Voice生成』を実装範囲とし§2-1が承認済み設計維持と述べるため、承認範囲内と読む(27-3 B、Fable確認)。VALIDATED(限定)の公開前宿題(c)V1根拠R2+のみ/(d)人手収集約25分/(e)目視1名/(g)V2単一出典例外を引継ぐ 〔委任文要旨に依拠。Launch原文は文字化けのため逐語確認不能〕 | OPEN-520(判断候補B: Fable確認) | Launch原文で『Voice生成方式の採用』文言を確認できれば解消 |
| YL-C04 | Closing一般化方式: Prompt 02(sha4713ceff…)+gpt-6.1-sol effort high+観察→候補3〜5→選定→closing_ja、schema family_y_closing_general | C | APPROVED_FOR_PRODUCTION | USER_LAUNCH §2-2(2026-10-25)。Round 2=CLOSING_GENERAL_01/TRIAL_RESULT_02.md・EVAL_02.md、Prompt=prompt_closing_general_02.txt | N/A | N/A | **Y固有実装** | DEV Trial(er110_family_y_closing_general_trial_01.py)。Production未到達 | Prompt原文byte一致のProduction module移植(DEV runner非import)、入力構造・候補選定処理・出力schema・決定論検査・Gate接続を忠実移植 | OPEN-520 | sha一致test+正式E2Eのgen_meta(model_id/routing/prompt sha)記録 |
| YL-C05 | 『宅配の再配達』のみ人手設計案B『料金は、誰の何を動かせるのか』を固定Closingとして正式採用(案A/C/Round 2生成案へ差替えない) | C | APPROVED_FOR_PRODUCTION(当該記事のみ) | USER_LAUNCH §2-3。本文=REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md パート5案B、closing_final.txt sha e9a853e3… | N/A | N/A | **Y固有実装** | DEV Trial(closing_B Gate PASS) | 一般化方式を迂回する例外として監査可能な固定注入(承認記録・sha照合・当該記事slugのみ)を実装 | OPEN-520 | fixed_closing_record.json(承認ref・sha)がE2E成果物に残る |
| YL-C06 | 人物紹介ナレーション(各Voice冒頭、本人の語りを先取りしない、3本1 call+決定論検査) | C | APPROVED(委任文§2-B指定) | USER_10 §2①(2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_10.md)/委任文§2-B。Production採用はLaunch一括承認に依拠 | N/A | N/A | **Y固有実装** | DEV Trial(REDELIVERY_REVISION_01、check_intro) | intro stageのProduction module化。narrator Voiceは『各levelの既存Full Storyナレーター設定』から導出(Aoede直書き禁止) | OPEN-520 | intro決定論検査PASS・音声でVoice切替確認 |
| YL-C07 | AI編集の音声アナウンス廃止+記事/試聴ページ注意書き掲載+Lead再生成(単純削除禁止) | C | APPROVED(委任文§2-B指定) | USER_10 §2②/PAGE_NOTICE_JA(er110_family_y_redelivery_revision_01.py:39) | N/A | N/A | **Y固有実装** | DEV Trial(試聴ページ注意書きは未実装=次段階) | Lead生成stage(115〜160字)・ページ共通builderへの注意書き枠追加(内部情報非表示規則と両立) | OPEN-520 | 公開ページに注意書き表示・音声にアナウンスなし |
| YL-C08 | In One Line廃止(Yのみ。X/Z不変) | C | APPROVED(委任文§2-B指定) | USER_10 §2③/CURRENT_SPEC 共通仕様表『In One Line / Comment 4』行(Y=未定→本案件でY=廃止へ更新提案) | あり(X固有) | なし | **Y固有実装** | DEV Trial(revision moduleは持たない) | 英訳stageでIn One Lineを生成しない新stage(rr.cmd_englishは生成するため流用不可)、Y style gateの`in_one_line`参照(er110_family_y_audio_trial_01.py:137,261)を除去 | OPEN-520 | 成果物にin_one_line segmentなし・Gateがin_one_lineに依存しない |
| YL-C09 | Comment1〜3(Comment4廃止)・Preview・日本語タイトル(Std)のY版role文 | C | APPROVED(Y既決設計、USER_09 §3・DESIGN_PROPOSAL_02 D1) | USER_09 §3/USER_02/OPEN-463 D1 | Comment1〜4 | Comment3つ | **Y固有実装** | DEV Trial(Y roles) | XのComment3/4はPart3分割前提role(INVENTORY T5)のためY版role文をProduction module化 | OPEN-520 | Comment内に内部ラベルなし・Preview原則(答えを先出ししない) |
| YL-C10 | 3 Voiceの固定TTS Voice割当 Algieba/Zephyr/Schedar(Z正式表`assign_dialogue_voices`結果と一致)・ナレーター=Full Story設定 | C | APPROVED(ユーザー決定) | USER_02(固定割当)/USER_09 §4/USER_10 §2①(ナレーターはlevel別既存設定、Aoede全level固定禁止) | N/A | Z=Dialogue別Voice(PW) | **Y固有実装** | DEV Trial(Y_BODY固定、er110_family_y_audio_trial_01.py:44) | 決定論の割当関数呼出+期待値test(3名固定)、男性2声(V1/V3)の聞き分けは宅配E2Eの聴取宿題 | OPEN-520 | voice_assignment_check相当PASS・聴取 |
| YL-C11 | Y style gate・本文segment ID方式(alias full_story_part3_c2/c3)をProductionでは正式Y segment IDへ | C | 設計課題(承認済み仕様の実装形) | INVENTORY_X_Z_SPEC_01 T8/T11、er110_family_y_audio_trial_01.py:44-50,521 | N/A | Z=`..._c{k}`はDialogue clip | **Y固有実装** | Trial=aliasで共有QAに乗せた暫定 | Zのclip ID意味(`part_c{k}`=Dialogue)と衝突しないY ID方式を設計し`resolve_narrative_role`等へY用ID追加(Opusレビュー対象) | OPEN-520 | Connected Speech/Local Rewrite/Repetition/disfluency QAがY全segmentに掛かるtest |
| YL-C12 | 公開範囲=Family Y限定共有(unlisted・noindex・権利確認前の転載不可注記)・出典権利確認 | C | 既存運用(委任文§3) | 委任文§3/REDELIVERY_AUDIO_01/RIGHTS_CHECK_01.md/FABLE_EVAL_03(c)(d) | N/A | N/A | **適用** | DEV Trial(限定試聴ページ) | 公開は既存運用に従う。V1のR2+根拠は公開前に許諾or置換(OPEN-484/463既記) | OPEN-520 / OPEN-463 | 権利確認記録+出典連続一致0件検査 |

### §2-2 A: 共通仕様(X/Zで配線済み・Yへ組込)(24件)

| ID | 仕様 | 分類 | 承認Status | 承認根拠 | X配線 | Z配線 | Y適用要否 | Y配線Status(現状) | 残作業 | 追跡先 | 完了証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YL-A01 | Style profile(PD06/S3/E1/K2/P8-KP/P7、fx_20261017)・Role Style固定記録・M3 Style gate | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC『共通仕様のFamily別配線Status表』(L1681)/OPEN-412/OPEN-415 | PRODUCTION_WIRED(2026-10-17) | PRODUCTION_WIRED(2026-10-17、定数参照+drift test) | **適用** | DEV Trialはprofile継承+Y style gate(YL-C11) | Y新runのStyle記録+drift testへ`CROSS_FAMILY_COMMON_STYLE_MAP`相当を追加(OPEN-415はZ方式[定数参照]を推奨) | OPEN-415 / OPEN-520 | Y runのaudit/style記録がprofile一致・旧style混在を課金前STOP |
| YL-A02 | Std Full Story 6%減速(Narrator/Voice含むY本文) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC L1681表『Std Full Story 6%減速』/USER_09 §4(既存速度・Style継承) | PRODUCTION_WIRED | Narrator分PW(Dialogueは撤去) | **適用** | DEV Trial(Y_MISSING_MANDATORY_A2_SLOWDOWN検査) | 『人物の語りだけ減速なし』版の採否はTrial併置のみで未決=X準拠既定で配線 | OPEN-466 / OPEN-520 | Y Std全本文segmentでslowdown_applied=True |
| YL-A03 | 統一ASR判定(AUW: Primary/Secondary/Whisper決選・HR Lock・PASS_WITH_WARNING・日本語kana/読み/値比較) | A | APPROVED/PRODUCTION_WIRED(原文に『Yの開発時に正式配線』) | CURRENT_SPEC『統一ASR判定仕様』節(L2848)/L1681表 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | DEV Trialは共通moduleを呼ぶ | Y runnerの全TTS segment経路が共通AUWを通ること(迂回なし)をtestで固定 | OPEN-520 | Y E2E全segmentがAUW判定を通過・HR Lock 0または適正解決 |
| YL-A04 | TTS model=Flash-Lite speech_metadata(正式backend)・routing contract fail-closed | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC Coffee/X節/er006_model_routing_contract_01.py:121,143 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Y用routing keyなし(er006にFAMILY_Y_*なし、grep0件) | Y process key新設(Voice Writer/Closing/判定/Lead/intro)+pricing登録(INVENTORY T17)。er006は別agent編集中=委任_02で最小編集 | OPEN-520 | actual model_id==routing==期待、未登録modelはfail-closed |
| YL-A05 | TTS/ASRの再試行(通算3回・cool-down・KP英語4回)・fallback・Local Rewrite(英語5role)→HR Lock | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC QA/Human Review節(L2125)/INVENTORY §5-6 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | DEV Trial(Y body alias経由) | Y segment ID→role解決(YL-C11)。intro/lead/closingのrole割当 | OPEN-520 | retry/Local Rewrite/HR LockがY IDで発動するtest |
| YL-A06 | 音声品質検査(ratio/ASR/値ガード/否定保護/disfluency/repetition/Connected Speech/Audio Validation Gate) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC QA節/統一ASR節 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | DEV Trial | Y ID追加でQA対象漏れ防止(INVENTORY T8)。OPEN-469(Repetition QA単複偽陽性)はYで実発生済み | OPEN-469 / OPEN-520 | Y全segmentでQAが評価対象に含まれる |
| YL-A07 | ASR値ガード(数値・単位は値で比較、5値) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC 統一ASR節 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | 共通module | 自動継承(Y runnerが共通判定を使う限り) | OPEN-520 | — |
| YL-A08 | TTS記号正規化4層(Prompt予防→Validator→TTS直前Normalizer→未変換でSTOP) | A | APPROVED/PRODUCTION_WIRED(全Family共通) | CURRENT_SPEC『TTS記号正規化(全Family共通)』(L2238) | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | DEV Trial(Voice Prompt/決定論検査に記号禁止) | Y新stage(Lead/intro/Closing/Voice)がNormalizerを通ること | OPEN-520 | symbol gate STOP test |
| YL-A09 | 固有名詞読み解決(Pronunciation Ledger+TTS Pronunciation Hint+Stage1供給)・日本語読み調査 | A | APPROVED/PRODUCTION_WIRED(Stage1は条件付き) | CURRENT_SPEC『固有名詞読み解決』(L2329)/Stage 1節(L3008) | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | 共通module | Voiceに固有名詞(企業/サービス名)が出る場合の読み解決。Web検索付き日本語読み調査はY Trialで見積外22.8円の費用事故実績=見積に含める | OPEN-520 / BUDGET_PLAN_01 | 読み調査の事前見積+Ledger登録 |
| YL-A10 | 固有名詞の発音不一致=アラーム受理(PNAP、OPEN-450) | A | APPROVED_FOR_PRODUCTION(対象=X/Z共通と明記、28-1運用7でYを最初から配線対象) | CURRENT_SPEC L3019節/OPEN-450/PM_GOVERNANCE 28-1運用7 | PRODUCTION_WIRED | WIRED_FIRE_UNOBSERVED | **適用** | Y=scope非活性(er103_proper_noun_alarm_policy_01.py:42 APPROVED_SCOPES={X,Z}) | scopeへ"Y"追加(開示事項。承認原文はX/Z、Yは28-1運用7に基づく)=共有module編集のためOpus条件A範囲に含める | OPEN-450 / OPEN-520 | Y runでscope活性・A/B/C不変test |
| YL-A11 | 表記違い同音包括対策(er109)・多語同音救済・M1複数発音候補 | A | APPROVED_FOR_PRODUCTION(er109はX/Zのみ有効と明記) | CURRENT_SPEC L2883/L2839/OPEN-459/OPEN-439 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Y=scope非活性(er109_xz_scope_01.py:25) | scope追加(YL-A10と同じ編集箇所、最小変更)。多語同音救済はmodule定数でscope限定ではない | OPEN-459 / OPEN-520 | Y runでortho_scope=Y記録 |
| YL-A12 | Key Phrase全文選定(Prompt 2逐語sha a12896f4…・各level最大3件・外側retry通算3・fail-closed)・KP品質(語数/難易度/汎用性/canonicalization/gloss整合/Redundancy QA) | A | APPROVED/PRODUCTION_WIRED(KPFT) | OPEN-454/CURRENT_SPEC『Key Phrase』(L1956) | PRODUCTION_WIRED(2026-10-22) | PRODUCTION_WIRED(2026-10-22) | **適用** | Trial scaffoldは`sc.run_key_phrases`を直呼び(er110_family_y_text_trial_01_run.py:264)=Production入口なし | Y正式KP段が`sc.run_key_phrase_canonicalization`(hook付き)を通る(OPEN-484(a)〜(f)) | OPEN-484 / OPEN-520 | Y正式経路でmodel_id・template sha・before/after見出し語を記録 |
| YL-A13 | KP: 本文実在Gate(key_phrase_source_gate)・CMU辞書登録語のみ(M1/M2)・3-ASR多数決・数値/否定保護解除 | A | APPROVED/PRODUCTION_WIRED | OPEN-458/CURRENT_SPEC L2980,1956 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | 共通module | Y KP段で同じGate群を通る(自動継承+test) | OPEN-484 | KP voteがY runで記録 |
| YL-A14 | KP一般化: 所有格possessor_roles+参照語不定化A-1(OPEN-474) | A | APPROVED_FOR_PRODUCTION | OPEN-474/OPEN-484 | WIRED_PENDING_FABLE | WIRED_PENDING_FABLE | **適用** | Y Trial scaffoldに効く(共通module)が正式入口なし | OPEN-484受入条件(a)〜(f)をY正式runで満たす | OPEN-484 | 条件(c)runtime evidence |
| YL-A15 | KP音声構造(Std英→日本語意味→英/Adv英→英語解説→英、同一音源再利用)・KP Style K2/P8-KP/P7 | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC L1681表/OPEN-412 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Trial scaffold経由で動作 | Y正式KP音声段 | OPEN-520 | KP segment 3 clip×levelの生成 |
| YL-A16 | 英訳: Advanced=日本語忠実英訳(同一段落数・順・追加削除なし)、Standard=Advancedからの英語簡易化(A2語彙・段落維持) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC X節/USER_09 §3(Y継承指定) | PRODUCTION_WIRED(W-1) | Zは別方式 | **適用** | DEV Trial(rr.cmd_english。In One Line生成を含むため流用不可=YL-C08) | Y英訳stage: Voice/紹介/Lead/Closingを含む5パートの段落数一致+Voice個性保持検査(人物性が平板化しないか) | OPEN-520 | mapping_check・新事実なし検査(連続一致) |
| YL-A17 | Part 1「Vocabulary & Expressions」(Advanced、案α+T1専用訳工程) | A | APPROVED_FOR_PRODUCTION | OPEN-512(2026-10-25 委任_17 Fable受入) | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Y未配線(DEV Trialは出さない) | Y runnerにstudy_text相当stageを接続(Adv限定。KP HRのpart1_itemsと整合) | OPEN-512 / OPEN-484(g) / OPEN-520 | Y AdvページにPart 1表示・訳工程call記録 |
| YL-A18 | ポーズ/Gap規則(Comment前後・語り手切替=CHARON_TO_AOEDE_PAUSE相当を再利用、効果音なし) | A | DECIDED(既存値) | CURRENT_SPEC Cross-level仕様表/er110_family_y_audio_trial_01.py:57 | DECIDED | DECIDED | **適用** | DEV Trial(Voice間gapは既存値再利用、Y固有の新値なし) | Production timeline builderで同値を使用 | OPEN-520 | timeline.jsonでgap値確認 |
| YL-A19 | Master Audio Store再利用(固定phrase/KP同一音源)・shell固定segment(Welcome/Intro/Outro/Notification) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC X音声構造節/INVENTORY §3 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Trial=Trial名前空間コピー(Production store非書込) | Production storeを使うか(再利用で費用減)を設計で決定。Voice固定のためY本文のstore再利用率は低い | OPEN-520 | store hit率記録 |
| YL-A20 | 公開試聴ページ標準フォーマット(共通builder・内部情報非表示・PASS_WITH_WARNING折りたたみ・全編再生ボタン) | A | APPROVED(2026-10-18) | CURRENT_SPEC X音声構造節/er_user_listening_page_common_01.py/tools/user_test_page_standard_check_01.py | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | DEV Trial(Adv 10/11検査、Y見出し`One Voice:`regex誤検知1件の既往) | Y用ページscript+注意書き枠+検査toolのY見出し誤検知対応 | OPEN-520 | page検査PASS+公開URL実再生 |
| YL-A21 | STOP/RUN_LOCK/RESTART_STORM(26節)のrunner組込み(Zにあり、X audio runnerになし) | A | 運用安全(PM_GOVERNANCE 26) | PM_GOVERNANCE 26/INVENTORY §6/OPEN-354,355 | Xはrunner未実装(文書規則) | Z=実装 | **適用** | DEV Trialはstop_check外部呼出 | Y新runnerはZ方式(各API呼出前のSTOP確認+RUN_LOCK)を採用 | OPEN-520 | STOP/RUN_LOCK test |
| YL-A22 | retry/fallback/regeneration/resume(stage指定再実行、`--only-segments`、sha不一致で再生成、Gate FAIL後の既存retry上限) | A | APPROVED/PRODUCTION_WIRED | CURRENT_SPEC X節/INVENTORY §6 | PRODUCTION_WIRED | PRODUCTION_WIRED | **適用** | Trialは個別CLI | Y runnerの全stageでregenerate-stage/resume定義。Closing Gate FAIL時は既存`run_gate`(判定最大3・LEAKAGE_RESIDUAL_STOP、er110_family_y_persona_text_trial_01.py:617)を使い独自上限を作らない | OPEN-520 | resume test・Gate STOP test |
| YL-A23 | Validator/Regression(全回帰、隔離test、DefaultOffIsolation、Dangling Reference) | A | 運用(PM_GOVERNANCE Closeout/11-7) | PM_GOVERNANCE 3節・11-7 | — | — | **適用** | Y DEV test約115件 | Y Production moduleのtest(Prompt sha・routing・隔離・Gate・resume)+全回帰 | OPEN-520 | 全回帰で自分起因failed 0 |
| YL-B06 | Spoken-first Number Treatment(2軸分類原則) | A | DECIDED(2026-08-17) | CURRENT_SPEC L1731近傍/INVENTORY §4 | PRODUCTION_WIRED(実質の担い手=B3 producer+丸め判断) | — | **除外** | — | 担い手がX限定。Yは数字を原稿に出さない設計のため実質非適用(Voice規則9) 〔理由記録のみ〕 | — | — |

### §2-3 F: 進行中・Trial中・未承認(依存実装待ちまたは先行採用禁止)(9件)

| ID | 仕様 | 分類 | 承認Status | 承認根拠 | X配線 | Z配線 | Y適用要否 | Y配線Status(現状) | 残作業 | 追跡先 | 完了証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YL-F01 | KP Human Review(TOP 8候補・Human 3KP+KP含む単語解説2件=5件・不在時TOP1〜3/1〜5・NGと未レビューの区別・NG自動採用なし) | F | APPROVED_FOR_PRODUCTION・IMPLEMENTED_PENDING_EVIDENCE(KP側X/Z共通核er119実装済み・単体test 104件PASS、Production run 0。commit d7a5713d4、2026-10-25) | OPEN-518/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_02.md:27,39,62 | IMPLEMENTED_PENDING_EVIDENCE(実API evidence R1〜R4は10/26以降) | IMPLEMENTED_PENDING_EVIDENCE(同左) | **適用(依存実装後に接続)** | Y入口なし(OPEN-484(g))=PRODUCTION_WIREDにしない | er119の確定I/F(`run_kp_with_review`・明示auto宣言dict・`reselect`・`UNREVIEWED_AUTO_ADOPTED`)に依存。Y runnerは『接続点』として結線し、HRあり/なし両経路を実装(er119のReadで確認、改変なし) | OPEN-518 / OPEN-484(g) | Y runでKP HRあり(wait→select)/なし(auto)の両方evidence |
| YL-F02 | 文法Human Review(TOP 2・TOP1既定・TOP2/再選定/省略・不在時TOP1) | F | APPROVED_FOR_PRODUCTION・IMPLEMENTING(grammar層は未実装、核はkind非依存) | OPEN-518/OPEN-519/PART2 DESIGN_02.md:78 | 委任_03で配線予定 | 同左 | **適用(依存実装後に接続)** | Y入口なし | er119(kind=grammar)+er120の確定I/Fに依存 | OPEN-518 / OPEN-519 | Y runで文法HRあり/なし |
| YL-F03 | Part 2「Grammar & Sentence Structure」(Trial-07機能)+Trial-08構文選定(倒置は後順位)・Adv限定 | F | APPROVED_FOR_PRODUCTION・IMPLEMENTING(er120 module完成・runner未接続) | OPEN-519/OPEN-497(VALIDATED限定)/PART2 DESIGN_02.md | module準備済み・未配線 | 同左 | **適用(依存実装後に接続)** | Y入口なし(OPEN-484で追跡) | er120接続点を明記。Adv限定=YのAdvのみ。Y Voiceの一人称英語から適格構文が出るかは未検証(0件許容仕様に依存) | OPEN-519 / OPEN-484 | Y Adv runでPart 2生成(0件許容)または0件記録 |
| YL-F04 | JA ASR誤NG根治(案A: 読み一致の是正、助詞は→わ等)・OPEN-517 | F | Trial中・案Aは承認済み仕様(値/読み一致)からの乖離是正=修正へ進む。配線はユーザー正式採用後 | OPEN-515/OPEN-517/JA-ASR-FALSE-NG-ROOT-CAUSE-01/DESIGN_01.md | 未配線 | 未配線 | **未承認=先行採用禁止** | 共通ASRはXと同時に効く設計 | Phase 3 Trial→VALIDATED→ユーザー正式採用→共通moduleへ配線。YはAUW共通経由で採用時に自動的に効く構造にする(Y側の追加実装を避ける) | OPEN-515 | 採用後にYのJA segmentで確認 |
| YL-F05 | Closing Prompt 03(Round 2課題: Gate FAIL/順序偏り/多様性/単価対応)・Gate文言変更 | F | 未承認(Trial結果=VALIDATED限定、案4=Y Production化計画時にまとめて判断) | CLOSING_GENERAL_01/EVAL_02.md Fable評価/USER_LAUNCH §2-2『Prompt 03化禁止』 | — | — | **未承認=先行採用禁止** | — | Prompt 02で立上げ。Prompt 03・Gate変更はPROMPT_GATE_ALIGNMENT_01の案のとおりユーザー判断(理由・差分・QCD付き) | OPEN-520(判断候補D) | ユーザー判断 |
| YL-F06 | Tier内順位改善(Part 2)・Closing effort medium化(単価-55%)・2段階化 | F | 未承認 | OPEN-497追跡/EVAL_02(mediumは不採用候補) | — | — | **未承認=先行採用禁止** | — | 立上げに含めない。単価改善候補として記録(Charter原則3) | OPEN-520 | — |
| YL-F07 | 会話速度v2をYのVoiceに適用 | F | 未承認(新仕様) | OPEN-484追記(2026-10-24) | — | Z=PW | **未承認=先行採用禁止** | — | 採用する場合は`er063_family_z_audio_01.adv_dialogue_ratio_range`を共通利用(重複実装しない)。本立上げでは採用しない | OPEN-484 | — |
| YL-F08 | Voice M1(世界スコープ事実)とleak_evidence_subjectの衝突(OPEN-470)・Voice背景fact | F | RESOLVED_NO_JUDGE_CHANGE(Writer Prompt側で整合) | OPEN-470/B0_LEAKAGE_CONTROL_01.md | — | — | **適用** | Voice Prompt側で解消済み(判定器変更なし) | 実在意見ベース方式ではResearch/Fact空=事実0件が設計。新規対応なし | OPEN-470 | — |
| YL-F09 | Repetition QAの単複/語形揺れ偽陽性(OPEN-469、Y R2g Advで実発生) | F | OPEN_PENDING_USER_DECISION_CANDIDATE | OPEN-469 | 影響あり(共有QA) | 影響あり | **判断待ち** | Yで再発し得る(共有QA) | Yの宅配E2Eで発生した場合は既存HR Lock→人間承認の既存手順。共有QA検出ロジック修正は受理面変更=ユーザー判断候補(未起票) | OPEN-469 | E2EでHR Lockが出た場合のみ顕在 |

### §2-4 B/D: X基盤・X/Z固有(Yは除外または置換)(7件)

| ID | 仕様 | 分類 | 承認Status | 承認根拠 | X配線 | Z配線 | Y適用要否 | Y配線Status(現状) | 残作業 | 追跡先 | 完了証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YL-B01 | Research(web_search)・Fact Ledger検証・B3 Storyline+Fact選定(Fact下限2件)・決定論B3 producer・Fact Lock Writer R0/R1/R2・AN3-T0 | B | APPROVED/PRODUCTION_WIRED(X) | INVENTORY_X_Z_SPEC_01 §1-2/OPEN-217/218/219/USER_09 §2,§3 | PRODUCTION_WIRED | Z=Seed方式(別) | **除外** | — | Yは実在意見ベース(Research/Fact空、`fact_scopes`空)。X W-1のR1/R2はOPEN-217でLeakage悪化の既往=Y Writerは別Prompt(Voice R0のみ) 〔除外理由=Yの設計(Research is backstage・意見ベース)〕 | — | Y記事のResearch/Ledger成果物が存在しないこと(意図的) |
| YL-B02 | Risk Flagger(完成英文×完全Ledger、非Blocking) | D | APPROVED/PRODUCTION_WIRED(X固有。Z対象外) | CURRENT_SPEC L1681表/L1165節 | PRODUCTION_WIRED | 対象外 | **除外** | CURRENT_SPEC表のY列=『未定』 | Ledger不在のためRFの入力が存在しない。Yの創作リスクはLeakage Gate+出典連続一致検査で担保。表のY列を『対象外(理由)』へ更新する提案 〔判断待ちではなく除外提案(Fable確認)〕 | OPEN-520(SSOT提案) | — |
| YL-B03 | X記事3分割(split_family_x_article_text_v2)・Comment3/4 role・音声segment順(Intro→…→In One Line→Outro) | B | APPROVED/PRODUCTION_WIRED(X) | INVENTORY §2,§3,T3/T5/T11 | PRODUCTION_WIRED | Z別 | **Y固有実装** | — | Y用splitter(5パート)・segment順tuple・timeline builderを新設。X関数は無変更で呼ばない | OPEN-520 | Y splitterが5パートを返す |
| YL-B04 | B3後の中核数値丸め判断(OPEN-437、Xのみ) | D | APPROVED(Xのみ、承認原文) | OPEN-437/CURRENT_SPEC L2896 | PRODUCTION_WIRED | Zは到達しない(Isolation test) | **除外** | — | 承認原文が『Family Xのみ』=Y適用は別判断。YのVoiceは数字を使わない設計 | — | — |
| YL-B05 | 中核数値保持v4+J2波ダッシュ正規化(X Std/Adv) | D | APPROVED_FOR_PRODUCTION(Y/Z対象外と明記) | OPEN-507/OPEN-509/CURRENT_SPEC L2911 | PRODUCTION_WIRED(2026-10-25) | 対象外 | **除外** | — | 承認でY/Z対象外。YのVoice規則は算用数字不使用・数量表現禁止。記号QA/TTS Normalizerは共通で効く(YL-A08) | OPEN-514(X側) | — |
| YL-B07 | Z固有: 外国人名ルール・Seed方式・Dialogue別Voice・Strategy L KP・会話速度v2・極短clip速度Gate | D | Z固有/APPROVED | CURRENT_SPEC L1681表/OPEN-462/OPEN-496 | 対象外 | PRODUCTION_WIRED | **除外** | — | Yの3 VoiceはDialogue clipではなく長文Voiceパート。会話高速化v2採用はOPEN-484追記のとおり未承認の新仕様(YL-F07) | OPEN-484追記 | — |
| YL-B08 | Chunk TTS(X=段落+0.2秒 / Z=B_r1 narrator>100語) | D | APPROVED_FOR_PRODUCTION(承認原文はX/Zのみ) | 2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md:5-32/CURRENT_SPEC L2929 | PRODUCTION_WIRED | PRODUCTION_WIRED | **判断待ち** | — | 承認範囲外。Yは各Voiceパートが1段落でAdv英語134〜172語(宅配R0実測 parts.json)=Z規則(100語超)なら対象になり得るが、Y用の承認・Trial無し。初回は非適用で配線し、Y音声で速度問題を聴取した場合にTrial提案(先行採用しない) 〔27-3: 承認範囲外=未承認の先行採用禁止。Fable確認で足りる(B)〕 | OPEN-520(判断候補B) | 宅配E2E聴取で『速い/詰まる』所見の有無 |

### §2-5 E: 旧Family B由来(3件)

| ID | 仕様 | 分類 | 承認Status | 承認根拠 | X配線 | Z配線 | Y適用要否 | Y配線Status(現状) | 残作業 | 追跡先 | 完了証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YL-E01 | Analytical Leakage Check(旧B承認13項目の日本語移植: Voice 7項目/Tension 6項目)・Acceptance Gate上限3判定+局所書き換え+LEAKAGE_RESIDUAL_STOP | E | 旧B承認済み項目をY設計で継承(ユーザー決定) | OPEN-463確定方針『Leakage Gate継承』/USER_02/DECISION_LOG:8511(旧B) | —(X経路に無い) | — | **適用** | DEV Trial(er110_family_y_persona_text_trial_01.py:344-407,617 run_gate) | Production module化(定義・閾値無変更)。DEV-onlyの『累計22円超でGate SKIPPED_BUDGET』(OPEN-463 委任_22/25記載)は移植禁止(Gate省略不可) | OPEN-520 | Voice Gate+Closing Gate が正式E2Eで必ず実行された記録 |
| YL-E02 | 旧B骨格『共通前提→分岐点→非対称性』をTensionに継承 vs Closing一般化の『新しい見方』 | E | 旧B=承認済み/Closing一般化=APPROVED_FOR_PRODUCTION(矛盾箇所あり) | OPEN-463/CLOSING_GENERAL_01/EXISTING_SPEC_CHECK_01 §1,§2 | — | — | **判断待ち** | DEV Trial(骨格に固定しない運用) | `leak_tension_reverts_to_research`の肯定側文言(『3人がなぜ違う答えに至るのかの掘り下げ』)が旧B骨格由来。Prompt/Gate整合(PROMPT_GATE_ALIGNMENT_01)で扱う 〔Gate文言変更=承認済み品質条件の変更〕 | OPEN-520(判断候補D) | ユーザー判断(Gate文言) |
| YL-E03 | 旧B Writer/Editorial Type経路(er012_b_family_*)・旧B Ledger形式 | E | 旧Family B=Legacy凍結(2026-09-27) | PM_GOVERNANCE 27-7/CURRENT_SPEC『Family体系』 | — | — | **除外** | — | ユーザー指示『Bの経路を転用しない』(INVENTORY §8-2)。判定器の考え方のみ日本語移植済み | — | — |


## 3. 判断待ち4件の理由(27-3仕分け: A既判断/B承認範囲内で自己解決/C独立/D真に新しい判断)

| ID | 論点 | 判断待ちの理由 | 27-3区分 | 推奨 | 立上げを止めるか |
|---|---|---|---|---|---|
| YL-C03 | 実在意見ベースVoice生成方式のProduction採用範囲 | 方式はVALIDATED(限定)。Launch要旨は『3 Voice生成』を実装範囲とし『承認済み設計維持』と書くが、Voice Prompt/Persona Sheet方式の`APPROVED_FOR_PRODUCTION`を明示する一文を要旨内で確認できない。原文が文字化けのため逐語確認不能 | **B**(承認範囲内と読める。Fableが原文または要旨の趣旨で確認) | 承認範囲内として進め、VALIDATED(限定)の宿題[(c)V1根拠がR2+のみ→公開前に許諾or置換 (d)意見収集は現状人手約25分=自動化は別案件 (e)目視1名 (g)V2単一出典例外]をOPEN-520へ引継ぐ | 止めない |
| YL-B08 | Chunk TTS(Y Voice長文パートへの適用) | 承認原文がX/Zのみ。YのAdv Voiceパートは1段落で英語134〜172語(宅配R0実測)=Z規則(100語超)の対象になり得るが、Y用の承認・Trialがない | **B**(承認範囲外は先行採用禁止という既存規則で自己解決。適用要否はY音声の聴取所見に依存) | Y初回は非適用で配線。宅配E2E聴取で『速い/詰まる』所見が出た場合のみ、Y用Trial(既存planner流用)を提案 | 止めない |
| YL-E02 | Gate文言(`leak_tension_reverts_to_research`の肯定側=旧B骨格)とClosing一般化Promptの不整合 | Gate変更は承認済み品質条件の変更=ユーザー承認事項。詳細はPROMPT_GATE_ALIGNMENT_01 | **D**(真に新しい判断。ただし初回の宅配は案B固定でGate PASS済みのため立上げ自体はブロックしない) | PROMPT_GATE_ALIGNMENT_01 §6の案(Prompt 02/Gate無変更で立上げ+FAIL時の既存retryで運用、Gate文言改訂は実績を見て1件の判断として提示) | 止めない |
| YL-F09 | Repetition QA単複偽陽性(OPEN-469) | 共有QAの検出ロジック変更=受理面の変更。Y R2g Advで実発生 | **C**(現タスクと独立。X/Z/Y共通の別案件。発生時は既存HR Lock手順) | 本案件ではHR Lock運用で受ける。Yで再発した場合に判断候補を起票 | 止めない |

## 4. 運用案: X/Z実装時にYの適用要否を確認する仕組み(既存Closeout Mandatory Checkの活用)

`docs/pm/PM_GOVERNANCE.md` 3節「PM Closeout Mandatory Check」には現在項目1〜32がある。**PM_GOVERNANCE自体は本委任では編集しない**(提案文のみ)。Fable承認後に追記する想定の文案:

> 33. **全Family共通仕様の採用・配線時にYを含む3 Familyの状況を確認する**(2026-10-25 FAMILY-Y-PRODUCTION-LAUNCH-01提案、28-1運用2〜7の具体化): ユーザーが共通仕様を`APPROVED_FOR_PRODUCTION`した、またはいずれかのFamilyで配線(`WIRED_PENDING_FABLE`/`PRODUCTION_WIRED`)したタスクのcloseout時に、(a)`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/spec_ledger_01.json`に当該仕様の行があるか(無ければ追加)、(b)X/Z/Yの3列が埋まり、Y列が『適用/除外(理由)/判断待ち/未承認=先行採用禁止』のいずれかか、(c)`CURRENT_SPEC.md`「共通仕様のFamily別配線Status表」のY列と矛盾しないか、(d)Yが『適用』で未配線なら`OPEN-484`(またはY案件のOPEN)へ受入条件を追記したか、を確認する。**新Gate・新報告工程ではなく既存Closeout確認の1項目**であり、Y Production入口の設置後(`PRODUCTION_WIRED`)はledgerのY列を`PRODUCTION_WIRED`へ更新して通常の配線Status表運用へ吸収する。

併せて提案(いずれも既存運用の延長で、新規の仕組みは作らない): ①`PM_GOVERNANCE.md` 28-2運用1の「共通仕様/Family固有仕様」欄に、承認原文の対象Family表記(X/Z/『全Family』)をそのまま転記する(PNAP・ChunkのようにX/Zのみと書かれた仕様をYが見落とさない) ②共有moduleのscopeリテラル(`APPROVED_SCOPES`等)を新設・変更するタスクは、Y追加の要否をledgerで確認する。

## 5. 検証(本委任のAPI 0確認)

- 本台帳の根拠は全て既存ファイルの読取り。API呼出・Production file編集・既存`erXXX_output/`変更はない(Git差分は`docs/`配下とSSOT 2ファイルのみ。報告参照)。
- 追跡の弱点(開示): 承認根拠の一部は、10-23棚卸しのCURRENT_SPEC行番号ではなく**節見出し**で参照した(行番号が移動したため)。Launch原文は文字化けで、委任文§0要旨に依拠した行(YL-C03、YL-C06〜C08)がある。
