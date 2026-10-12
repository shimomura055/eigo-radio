# CONFLICT_RESOLUTION_01(FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_02、2026-10-12)

設計のみ・課金0・コード/Prompt/Routing無変更。Phase A(`PHASE_A_SURVEY_01.md`)が列挙した衝突・STOP候補(S1〜S8)と、既存SSOTの関連項目を、2026-10-12ユーザー正式決定(①〜⑤、APPROVED_FOR_PRODUCTION、`DECISION_LOG.md`参照)で解消されたものと、技術的に未解消のものに分けて整理する。既存文言は削除せず、`CURRENT_SPEC.md`には「superseded by 2026-10-12決定」を追記済み。

注: 委任文は「Z-1〜Z-9」と記したが、`CURRENT_SPEC.md`のFamily Z節に存在するのは**Z-1(権利Gate)〜Z-4**のみ(Z-5〜Z-9の記載は検索で0件)。本書はZ-1〜Z-4を対象とした。

## A. ユーザー決定で解消した項目

| # | 衝突/論点(出典) | 旧状態 | 解消内容(決定) | SSOT反映 |
|---|---|---|---|---|
| A1 | Phase A S1: Family Cベース構成の決定原文が無い / 旧Phase A「3分割+Comment4」は未承認案 | 構成未確定 | 決定①: Family C方式基本。Story 3分割+Comment×3。In One Lineなし。Comment4なし。3分割Story(場面区切り)とDialogue音声clip分割(話者区切り)は別概念 | CURRENT_SPEC Z節追記、DECISION_LOG |
| A2 | Z-3(In One Line、APPROVED_FOR_PRODUCTION 2026-09-26) vs Family C構造(IOLなし) | 衝突 | 決定①により**Family ZではZ-3を不採用(superseded)**。`generate_family_z_in_one_line`等は量産経路で呼ばない(コードは削除せず実装フェーズで量産経路から外す) | CURRENT_SPEC Z-3へ注記 |
| A3 | Phase A S2 / 0-3: R2が名前保持(Dionysius/Selinuntius必須)と衝突。`check_character_name_rule`/`restore_character_names`でR2は不合格/RuntimeError | USER_DECISION_REQUIRED | 決定②: 固有名詞の登場を必須条件としない。Melos以外の名前の機械復元をしない。**Family Z一般仕様としてValidatorを改修**(走れメロス個別例外ではない)。意味保持(役割・関係・重要出来事・因果・結末・魅力)を検証。権利Gate・外国人名ルール・原作保持原則は維持 | CURRENT_SPEC Z節項目2へ注記 |
| A4 | Phase A S3 / OPEN-297(c)(e): Advanced原稿が無い、Sol採用/R0→R1→R2のZ Production化が未決 | USER_DECISION_REQUIRED | 決定③: **Advancedを自然な英語で新規作成**(gpt-6.1-sol、R0→R1→R2)。Standardはその最終稿を基に語彙・文構造・難易度を調整(同一本文にしない)。Trial②のStandard R2は**正式採用しない**。B3Zは不採用(OPEN-297(d)=REJECTED) | CURRENT_SPEC、OPEN-297 |
| A5 | Phase A S4 / OPEN-298(Coffee限定Styleの共通化は未承認) / Dialogue×新Style未検証 | USER_DECISION_REQUIRED | 決定④: Family X承認済みStyleを**対応Role**に適用(Full Story Narrator=PD8。Standard日本語Preview/Comment=R2。Advanced英語Preview/Comment等=Family X対応既存方式)。登場人物セリフは既存別Voice・従来Dialogue Style(PD8を無条件適用しない)。Coffee限定承認(OPEN-298/300)とFamily Z採用範囲は**区別して記録**。全記事共通化は未承認のまま | CURRENT_SPEC、OPEN-298へ注記 |
| A6 | Phase A S6 / 予算: BudgetGuard既定¥200(WARN¥150) | 上限未承認 | 決定⑤: 追加API費用上限**¥300**。超過見込みでSTOP。並列化・再利用 | 設計書(i)、実装時に`BudgetGuard`上限を差替 |
| A7 | Phase A 0-4: R2見出し`# `(`strip_markdown_title`は`### `前提)、斜体`*...*`、題名 | 技術論点 | 決定③でStandard R2不採用のため直接影響は消滅。ただし新Writer出力(`# Title`+斜体の可能性)に対する処理が必要 → B表(B6)へ移管 | - |
| A8 | Phase A Dangling #5: `japanese_title_text`(走れメロス(The Three-Day Promise))とR2題名(Before Sunset) | 要確認 | R2不採用。新Advanced/Standardの題名は新Writer出力に従う。`japanese_title_text`は固定語として維持するが、副題(英語題)は新稿の題名と一致させる必要 → B表(B7) | - |

## B. 技術的に未解消の項目(本設計書で方式を提案、Fable/Opus確認事項)

| # | 項目 | 内容 | 本設計での扱い | 判断者 |
|---|---|---|---|---|
| B1 | **S5: Dialogue clipのASR連続NG** | 3〜6語の短いDialogue clipは、ASR/Connected Speech/Local Rewriteが連続NGになりうる(Local Rewrite上限到達でSTOP) | 設計(f)(j): Dialogue clipは既存`generate_voice_body_wide_margin`(従来Dialogue系。内部cascade上限は既存機構のまま、独自に緩和しない)。STOP時は`human_review_queue`行き、上限の回避はしない。実測が必要 | 実装後Fable |
| B2 | **S7: X音声仕様Fix待ちの保留(OPEN-297文言)** | OPEN-297に「Family Z TTS/AssemblyはX音声仕様Fixまで保留」とあるが、決定①〜⑤は**Z Production音声E2Eの実装着手を明示**している | **解釈案(Fableに確認要)**: 本決定(2026-10-12)で保留は**解除された**と解釈する(ユーザーが実装・費用上限を指示したため)。ただし**X側の未解決論点(OPEN-276/279/281)はZへ持ち込まない**ため、下記B3の方法で切り離す。この解釈でよいか要確認 | **Fable確認** |
| B3 | OPEN-276(Std Part2 6%減速未適用/Gateの減速チェック穴)、OPEN-279(Trial限定条件)、OPEN-281(Std topic_intro等の残異常) | X側・Coffee Trial側の論点 | Zは共有moduleを経由するため、Human Review経路で6%減速が走らない構造穴(OPEN-276)はZのStandardにも波及しうる。対策: Z側で「Human Review経由で採択した音声にも、最終段で減速後ASR+Gateを実行する」確認をtestに含める(共有module改変なし)。OPEN-279(resolver省略等)はZ量産経路でresolver/Batch/正規化を適用するため該当しない。OPEN-281はX固有 | Fable |
| B4 | **S8: er020共有編集の競合** | `resolve_narrative_role`(L125-127)は`full_story_part1/2/3`完全一致。Zの複数clip(Part内のDialogue分割)をConnected Speech/Secondary ASR role gatingの対象にするには、IDが解決される必要がある | 設計(e): 後方互換な正規表現1行の追加(`^full_story_part[1-3](_c\d+)?$`)を推奨。既存ID(完全一致3種)の挙動は不変、Xは`_c\d+`付きIDを生成しないため影響なし。`er020`は単一担当で編集し、`run_project_regression.py`で回帰確認 | Opus/Fable |
| B5 | `er006_secondary_asr_01.py`(L611-613)・`er006_preprod_hardening_01_validation.py`もsegment_idから`resolve_narrative_role`でroleを引く | Z側だけでconnected_speech_enabledの真偽値を渡しても、検証層がsegment_idで再解決する | B4の正規表現で一括解決(Z側alias方式は検証層で解決されず不十分、設計(e)で理由記載) | Opus |
| B6 | 新Writer出力の整形(`# Title`、斜体`*...*`、`### `の有無) | `strip_markdown_title`は`### `前提 | `# `を扱えるよう、Z側で整形関数を追加。斜体はTTS記号正規化(`tts_safe_news_en`、PRODUCTION_WIRED)を必須適用 | 実装 |
| B7 | 題名: `STORY_REGISTRY['melos'].japanese_title_text`と新稿題名 | 副題の整合 | 新稿確定後に`topic_title`を稿から取得し、`japanese_title_text`の副題を同期(固定語Master再利用は不可の場合あり=該当clipのみ再生成) | 実装 |
| B8 | KP再選定: 旧`er035_output/kp_4plus1_evidence_01/melos_a2/`は旧Luna本文用 | 新本文では再利用不可 | 両レベルでStrategy L再選定(LLM課金)。Advanced KPは英語解説(Variant B)工程が必要(X既存のW4機構を共有module経由で利用) | 実装 |
| B9 | Std語数ゲート: `ACCEPT_WORD_RANGE=(280,420)`(A2想定)は、Advanced稿には適用不能 | Advanced語数範囲が未決 | **新規OPEN-302**: Advanced語数範囲(提案は設計書(a)) | Fable/ユーザー |
| B10 | Story 3分割の境界決定方法 | Family Xの3分割は段落境界の決定論分割。決定①は「場面・意味の転換点」、固定語数分割なし | 設計(d): LLM境界提案+決定論検証。方式は**新規構造のためOpus条件A対象** | Opus |
| B11 | Comment2/3の `content_facts`/`scene_transition`(Family C関数の入力) | Z側で用意が必要(現状はMelos固有のハードコード文字列が`generate_family_z_comment_1`内にある) | 設計(d): 新稿から生成した「事実リスト」をValidatorの構造化抽出と共用(重複機構を作らない) | 実装 |
| B12 | Dialogue Voice: 王の台詞がnarratorに落ちる / `friend`未登録 | Phase A 2-E | 設計(e): keywords拡張+attribution監査+override表 | 実装 |
| B13 | Family X側 `FAMILY_X_ROLE_STYLE_EN`はEnglishの6 roleのみ(PREVIEW/COMMENTは`calm, conversational`)。Coffee採用Style(PD8、E1、E2_UPBEAT、K2、M2、P2/R2)は**Trial script内定数**で、Production定数には未登録(OPEN-300) | Zが参照できる「Family X承認済みStyle」の正本 | 設計(f): Z専用Production定数表を新設(Coffee限定のX定数は変更しない)。値はCoffee evidence(`STYLE_APPLICATION_EVIDENCE_V3_01.md`、`prompts_pace_02.md`、`prompts_R.md`)から逐語転記しsha256で検証。**これは新定数の追加であり、「Family Z採用」はユーザー決定④で承認済み。ただしE1の逐語text・Adv Comment方式の特定は実装時に原典sha照合要** | 実装/Fable |
| B14 | OPEN-300(Coffee限定wiring方式) | 記事別override層の新設案 | Zは記事別overrideではなく**Family Zのrole style表**として独立に持つため、OPEN-300とは独立(X定数は不変) | 記録 |
| B15 | Std Dialogue clipの6%減速 | 決定④は「Narrator=PD8、Std=6%減速」を述べるが、Dialogue clipの扱いは明示なし | 既定案: Standardの英語Story clip(Dialogue含む)に6%減速を一律適用(速度一貫性、既存A2仕様)。要ユーザー試聴で確認 | ユーザー試聴 |
| B16 | Dialogue voice間の音色差(flash-liteのAoede/PD8 vs 従来経路のErinome/Charon) | 同一Part内で生成backendが混在 | assembleのgain正規化で吸収を試みるが、最終判断はユーザー試聴(決定④) | ユーザー試聴 |

## C. 既存OPEN/SSOTとの関係

| 項目 | 関係 |
|---|---|
| OPEN-185 | 構造論点は解消済み(2026-09-26)。本ID(`FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01`)で実装着手を追記。`PRODUCTION_WIRED`は未達 |
| OPEN-297 | (a)試聴は実施予定・(b)Sol=gpt-6.1-sol・(c)Sol採用=決定・(d)B3Z=REJECTED・(e)R0→R1→R2のZ Production化=決定。残=実装・試聴 |
| OPEN-298 | Coffee限定承認と全記事共通化は区別のまま。Family Zへの採用は決定④(別枠) |
| OPEN-300 | Zは独立(B14) |
| OPEN-276/279/281 | X/Coffee側。ZはB3のとおり切り離し+確認test |
| 新規OPEN-302 | Advanced語数範囲・語彙/文構造Gate(提案を設計書に記載、未承認) |
| 新規OPEN-303 | Z Role Style定数の原典照合結果とZ専用定数表の承認(実装時に確定する未決) |
