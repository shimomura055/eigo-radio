# design_family_z_melos_production_e2e_and_latest_spec_wiring_01.md

管理ID: `FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01`
作成: Sonnet(Phase A、設計のみ)。本Phaseではコード・Prompt・SSOT・Master
Store・出力ディレクトリを一切変更していない(read-onlyの調査結果のみ)。
API支出¥0(実行はGrep/Read/ローカルPython計算のみ)。

## §0 ユーザー指示(原文要旨、逐語)

目的: Family Zの既存「走れメロス」記事を再利用し、Family Xで正式採用した
記事構造・音声仕様のうちFamily共通として使えるものをFamily Zにも正式
採用・Production配線し、MelosをFamily Z最初の正式な完成E2Eとして
Production正式経路だけで完成音声・試聴まで通す(項目1〜15、Closeout
13項目の詳細は`docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-
PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md`に逐語保存済み、本書では
重複転記しない)。

---

## §1 Existing Spec/Repo 対応表

| # | 項目 | 所在(Production file:関数) | 現行仕様(CURRENT_SPEC該当行) | Melos run_01のartifact | 今回の扱い |
|---|---|---|---|---|---|
| 1 | Family Z専用runner | `er026_family_z_fiction_production_runner_01.py`(commit `42b43772`) | CURRENT_SPEC L1239-1387(Family Z(Fiction)節)、L1326-1328(Z-2) | `er026_output/family_z_production_e2e_01/melos/run_01/` | **既存reuse**。Phase 1=text工程のみ実装済み。`stage_tts()`/`stage_assemble()`は明示的に`NotImplementedError`スタブ(L741-757)。本タスクではこのrunnerへTTS/Assembly stageを追加実装する(runner自体は作り直さない) |
| 2 | article.md(本文) | `resolve_canonical_text()`(L291-327) | CURRENT_SPEC L1267-1272(Story内容基本方針)、L1292-1302(外国人名ルール) | `article.md`(2138 bytes) | **再利用(§2で詳細判定)** |
| 3 | story_type/rights block | `build_story_type_metadata()`(L560-566)、`check_rights_gate()`(L114-124)、`MELOS_RIGHTS_BLOCK`(L125-167) | CURRENT_SPEC L1273-1291(Seed必須条件)、L1303-1309(Story Type metadata) | `article_config.json`の`rights_block`/`story_type_metadata` | **既存reuse**、無変更 |
| 4 | Preview | `generate_family_z_preview()`(L460-470)、`_FAMILY_Z_PREVIEW_ROLE_JA`(L426-434) | Cross-level仕様節「Preview原則」(L1437) | `preview.txt`+`article_config.json`の`preview` | **既存reuse**(Family C禁止語句Contractを参照した新規JA prompt、Family Z所有) |
| 5 | Comment(1のみ実装) | `generate_family_z_comment_1()`(L518-541)、内部で`fam_c.generate_family_c_a2_comment(comment_num=1)`を呼ぶ | CURRENT_SPEC L1038-1176(Family C A2 Comment理解ガイド型Contract) | `article_config.json`の`comment_1`(`contract: FAMILY_C_A2_COMMENT_ROLE_JA_1`) | **Comment1は既存reuse**。Comment2/3は`er013_family_c_production_01.generate_family_c_a2_comment(comment_num=2 or 3)`をそのまま呼べば生成可能(§3bで詳細)。**Comment4は新規**(Family Cは1〜3のみ対応、§3bでSTOP非該当の理由を記載) |
| 6 | In One Line | `generate_family_z_in_one_line()`(L481-515) | CURRENT_SPEC Z-3(L1329-1330、APPROVED_FOR_PRODUCTION) | `in_one_line.txt`+`article_config.json`の`in_one_line` | **既存reuse**、無変更(Z-3で「新しい独立機構を追加で作らない」と既承認) |
| 7 | Key Phrase | `run_keyphrase_stage()`(L712-736)、`scaffold.run_key_phrases(..., "A2", ...)` | CURRENT_SPEC「Key Phrase」節(L1644-1682)、4+1構成(L1673) | `key_phrases/`(run_01、4+1構成**なし**の旧schema) | **要再確認**。run_01のKPは4+1導入前のschema(§3g)。互換artifactは`er035_output/kp_4plus1_evidence_01/melos_a2/`に別途存在(4+1構成PASS済み、§3g) |
| 8 | segment plan(voice分割) | `build_segment_plan()`(L333-400)、`fam_c.build_flat_voice_chunks()`/`split_into_paragraphs()`(Family C由来、read-only参照) | CURRENT_SPEC Z-2(L1326-1328、APPROVED_FOR_PRODUCTION) | `segment_plan.json`(8 voice-boundary segments、§3a) | **既存reuse**(voice分割自体は変更不要。3分割Contractをこの上に追加設計、§3a) |
| 9 | Family C由来Dialogue Voice機構 | `classify_quote_voice_window()`(`er013_family_c_production_01.py` L66-95)、`build_flat_voice_chunks()`(L122-) | CURRENT_SPEC Z-4(L1331-1346、APPROVED_FOR_PRODUCTION) | `segment_plan.json`の`voice`列(narrator/dionysius/selinuntius)、`dialogue_voice_plan`(voice_tts_names_plan: narrator=Aoede/selinuntius=Erinome/dionysius=Charon) | **既存reuse**、無変更(Family C本体は編集しない、Family移行方針どおりread-only参照) |
| 10 | pronunciation resolver | `resolve_and_augment_en_style_prefix`/`seed_work_canon_reading`(`er025_entity_pronunciation_resolver_core_01.py`) | CURRENT_SPEC L1993-2055(`APPROVED_FOR_PRODUCTION`、Phase 2実装中) | CURRENT_SPEC L2020-2023にMelos実測記録あり(`source_context="family_z_melos"`、JA "work_canon"読みは解決するがGemini TTSには未反映という既知の別Phase課題) | **既存reuse前提だが、TTS stage未実装のため実配線はこれから**。`enable_pronunciation_resolver=True`を渡す(Family Xと同じopt-in方式)必要あり |
| 11 | TTS symbol normalization | `er003_audio_tts_asr_safety.py` Layer1/3/4 | CURRENT_SPEC L1863「Family C Layer 2は例外」、L1937-1939「Family Z Writer実装時の必須適用」 | 未生成(TTS未実行) | **必須適用**(未着手、Phase B実装対象) |
| 12 | retry/fallback/Local Rewrite | `er020_tts_retry_local_rewrite_01.py`(`resolve_narrative_role`/`connected_speech_enabled_for`等) | CURRENT_SPEC Family Z項目6(L1310-1316) | 未生成 | **既存共有module reuse**。ただし`resolve_narrative_role()`はsegment_id完全一致判定のため、Family Zの実際のsegment_id命名と整合させる設計が必要(§3a/§3f、known_gap) |
| 13 | Connected Speech | 上記12と同一module、`CONNECTED_SPEECH_SEGMENT_IDS`(L95-111) | CURRENT_SPEC Family Z項目6(5role: Full Story/Comment/Preview/Topic intro/In One Line) | `segment_plan.json`の`known_gap`(L132、既知の未解決点) | **設計要**(§3a/§3f) |

---

## §2 Melos本文の再利用判定

**結論: 再利用可(再生成禁止)。STOP非該当。**

- **正式Family Z生成物か**: `resolve_canonical_text('melos')`を実際にimport・
  実行して再現した(API呼び出しなし、決定論的処理のみ)。`trial_sha256=
  ff93d8a5767ae48b232245ea5aa047df2062fd0bb55894c9eca5e009842ff146`、
  `final_sha256=bd40ab4dd5012218b811c5653974e7b87f05d526b0392e46d24623ea
  0145ce07`、`word_count=383`、`word_count_ok=True`、
  `character_name_rule_ok=True`。いずれも`article_config.json`の記録値と
  完全一致。
- **article.mdとの一致確認**: ディスク上の`article.md`をテキストモードで
  読み込み、`resolve_canonical_text('melos')['body']`と文字列完全一致
  (差分0、sha256一致)を実際に確認した(2138文字)。**由来commit**:
  `42b43772`(`FICTION-FAMILY-Z-PRODUCTION-E2E-01 Phase 1: Family Z
  text工程Production runner新設`)。
- **story_type=literature**: `article_config.json.story_type_metadata.
  story_type == "literature"`、`fixed_audio_intro_text: null`、
  `ui_label: null`(REAL STORY/TRUE CRIME表示なしの仕様と整合)。
- **rights記録**: `rights_block`に著者没年・日本国内PD根拠(1999年確定)・
  出典URL(青空文庫)・米国status記録事項・ユーザー正式決定引用(5条件)・
  `gate_reference`まで完全記載。CURRENT_SPEC L1273-1291のSeed必須条件
  (a)〜(d)を満たす。
- **承認済みFamily Z Story仕様との整合**: 外国人名ルール(項目4)により
  `Dionysius`/`Selinuntius`をフルネームのまま使用しているが、これは
  「同姓人物が複数」ではなく例外(iii)「固有名称としてフルネーム自体が
  重要」に該当するかは微妙。`article_config.json.canonical_text.edits`に
  よれば、これは逆方向の編集(Trial版が名前を欠落させていたためフルネーム
  へ**復元**した)であり、ルールの意図(冗長なフルネーム使用を避ける)とは
  別の問題(固有名詞そのものの欠落補完)。**この点は新しいProduct判断を
  要する論点ではなく、既存article_config.jsonの記録どおりの事実**として
  報告する(西洋文学の登場人物名は日本語文学と異なりFirst/Last統一ルールの
  対象外という解釈も成り立つが、本Phaseでは判断しない)。
- **Story本文に新たなProduct判断が必要な問題**: 発見なし。**STOP非該当**。

---

## §3 Family Z構造設計

### §3(a) 3分割Contract(Story適用)

**入力**: `segment_plan.json`の8 voice-boundary segments(`story_001`〜
`story_008`、語数`[61,4,33,5,5,7,133,135]`、合計383語)。この分割は
既にDialogue境界(引用符境界=speaker切替点)で行われているため、
**この8境界のいずれかを3分割の境界点として選べば、Dialogue途中を
切ることは原理的に発生しない**(Quote境界を跨ぐ分割候補が存在しない
設計)。

**機械的試算**(API呼び出しなし、scratchpad一時スクリプトで実施、
target=383/3=127.67語、`design_family_x_no_heading_segmentation_
trial_01.md` §3-3と同一思想の二乗誤差最小化探索を8境界へ適用):

| 候補(i, j) | body1語数 | body2語数 | body3語数 | 二乗誤差 |
|---|---|---|---|---|
| **(6, 7)** ※最良 | **115** | **133** | **135** | 242.7 |
| (5, 7) | 108 | 140 | 135 | 592.7 |
| (4, 7) | 103 | 145 | 135 | 962.7 |
| (3, 7) | 98 | 150 | 135 | 1432.7 |

**採用候補**: `body1 = story_001〜story_006`(115語、統治者Dionysius登場
→死刑宣告→妹の結婚式の猶予→Selinuntiusが人質を申し出るまで)、
`body2 = story_007`(133語、川を渡り結婚式に出て、帰路で襲われるまで)、
`body3 = story_008`(135語、フォースの逡巡→引き返す決意→間に合う→赦し
の結末)。**Dialogueを跨がない分割が存在することを確認した(STOP非該当)**。
3部の語数バランスは115/133/135(目標127.67との最大乖離約10%)で、
News既存Contractの「50%/25%/25%は理想目安」よりむしろ均等に近い。
物語の緊張構造(設定確立→試練→決着)とも自然に一致する。

**設計上の論点(STOP非該当、実装確認事項として報告)**: body1は内部に
narrator→dionysius→narrator→dionysius→narrator→selinuntiusという
3回のvoice切替を含む(story_001〜006の6 TTS segment)。body2/body3は
それぞれ単一narrator segmentのみ。したがって「3分割」は**TTS呼び出し
単位ではなく、Comment挿入位置を決めるための論理的グループ**であり、
音声Assembly順序は`Comment1→[story_001..006の6 TTS clip連結]→Comment2→
[story_007]→Comment3→[story_008]→Comment4→In One Line`となる。News
(Family X)の3分割は1 body=1 TTS clip(または見出し込み1〜2 clip)である
のに対し、Family Zは1 body=複数voice-clipの連結になりうる点が構造上の
違い(Comment役割の共通化自体は妨げない)。

### §3(b) Comment 1〜4

**Comment1**: 既存`generate_family_z_comment_1()`をそのままreuse
(無変更)。

**Comment2/3**: `er013_family_c_production_01.generate_family_c_a2_
comment(client, comment_num=2 or 3, article_text, content_facts,
scene_transition=..., ...)`を**そのまま呼び出せば生成可能**(Family C
本体は無変更、呼び出しのみ)。role文言は既に用意済み(`FAMILY_C_A2_
COMMENT_ROLE_JA_2`/`_3`、L401-419): 「物語の途中に挿入する短い日本語
コメント」「雰囲気作りではなく状況整理に徹する」「結末には触れない」。
Family Z用のcontent_factsは、body1終端(Comment2の直前=Selinuntiusが
人質を申し出た場面)、body2終端(Comment3の直前=帰路で襲われ倒れる場面)
の事実要約をFamily Z runner側で新規に書く(LLMではなく人手/deterministic
文言、Comment1のcontent_factsと同じ形式)。

**Comment4**: Family Cは`comment_num`を1〜3のみ許可(`ValueError`、
L435-436、「Comment 4なしはTrial-10から無変更」)。**これはSTOPには
しない**。理由: (1)Family移行方針(CURRENT_SPEC L1401-1407)は「Family
A/B/C向けに新規実装を行わない」と定めており、Family C本体(`er013_
family_c_production_01.py`)へComment4を追加することは禁止されている。
(2)一方、Family Z(`er026`)は既にPreview/In One Lineでも同様のパターン
(Family Cのcontent/contract思想を参照しつつ、Family Z所有の新規prompt
定数を`er026`内に定義)を採用済み(L426-434、L445-453)。Comment4も同じ
パターンで、Family Z所有の新規prompt(`FAMILY_C_A2_COMMENT_ROLE_JA_3`を
下敷きに、「結末には触れない」制約を「全体を軽く回収しIn One Lineへ
接続する」制約へ置き換えたもの)を`er026`内に追加すれば実装できる。
これは委任文項目4が明示的に許容する「既存Family Z/Family C Promptを
最大限reuse、最小限のFamily Z適応のみ」の範囲内であり、新しいProduct
判断(新しいVoice仕様・新しい評価基準等)を要しない**実装上の是正**。

Comment役割の共通化案(委任文原文どおり):
1. Comment1=入口(既存`FAMILY_C_A2_COMMENT_ROLE_JA_1`そのまま、変更なし)
2. Comment2=body1→body2 Bridge(`ROLE_JA_2`+scene_transition、reuse)
3. Comment3=body2→body3 Bridge(`ROLE_JA_3`+scene_transition、reuse)
4. Comment4=全体を軽く回収しIn One Lineへ(新規、Family Z所有prompt。
   ネタバレ禁止/内部用語禁止/雰囲気だけの抽象的誘導禁止は既存
   `_BANNED_PHRASES_INSTRUCTION`をそのまま継承)

**Melos run_01のComment artifact再利用可否**: run_01には`comment_1`
のみ存在(1件)。4 Comment構造には不足しており、**Comment2/3/4は新規
生成が必要**(§5コスト概算に反映)。

### §3(c) In One Line

既存`generate_family_z_in_one_line()`は既にZ-3(Fiction向け最小変更
reuse、APPROVED_FOR_PRODUCTION)を実装済みであり、無変更で3分割構造と
共存できる(In One Lineは音声構造全体の末尾に位置するのみで、3分割の
有無に依存しない)。run_01の`in_one_line.txt`(既存)をそのままreuse可能
(新規Product判断不要)。

### §3(d) Preview/Title/Topic intro等のsegment一覧とJ3/E2適用可否

| segment | 言語 | Voice(想定) | Role | J3/E2適用可否 |
|---|---|---|---|---|
| topic_intro | EN | Charon(Family X同様の想定、Melosでは未実装) | TOPIC_INTRO | **reuse可**(E2はRole定数がlevel非依存、CURRENT_SPEC「適用範囲」節: 「EN=FAMILY_X_ROLE_STYLE_ENのTOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3role...Role定数はlevel非依存のためStandard/Advanced両方のENsegmentへ適用される」。level非依存とはA2/B1B間の意味であり、Family非依存とまでは明記されていないため、Family Z側runnerで同じ共有関数[`voice01.generate_charon_english`等]を`style_prefix_override=E2`で呼べば技術的にreuse可能。CURRENT_SPEC「適用範囲」の文言をFamily Zにも及ぶよう更新することを§7で提案) |
| preview | JA | Aoede(既存Melos前提) | PREVIEW | **不可(E2/J3の対象外)**。J3の確定適用範囲は「Family X Standard(A2)のpreview/comment_1〜4のみ」。CURRENT_SPEC本文にも「PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため不変[E0のまま]」とある。**ただしJ3(JA)は逆にpreview/comment_1〜4が対象**(J3はJA全体の話であり、EN E2とは別軸)。すなわちFamily Z PreviewはJ3適用対象**である**(Family X Standard A2のpreview/comment_1〜4と同一のJA関数を同一のstyle定数で呼ぶだけ) |
| comment_1〜4 | JA | Aoede | COMMENT | **J3適用可**(上記と同一理由、Family X Standard A2と同じ関数・定数のreuse) |
| full_story_part1/2/3(body1/2/3、内部は複数voice-clip) | EN | narrator=Aoede/dialogue=Erinome,Charon | FULL_STORY | **E2適用可**(TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3roleに含まれる。ただし§3(a)の内部voice切替clip全てにFULL_STORY roleを解決させる必要があり、§3(f)のresolver拡張が前提) |
| in_one_line | EN | Aoede(A2)またはCharon | IN_ONE_LINE | **E2適用可** |

**Title(japanese_title)への注意**: 委任文項目7「Titleだけ旧Styleの
再発禁止」は、CURRENT_SPEC「適用範囲」節に明記の除外
(`japanese_title・Key Phrase JA・固定Master phraseは対象外`)と一見
矛盾するように見えるが、これは「除外」であって「旧Style使用の許容」
ではない。TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01の実装ノート
(`docs/pm/ACTIVE_TASK.md`該当タスク記録)によれば、japanese_titleは
既に独立した固定style経路を持つため、変数Role Style(J3)の対象外という
設計上の区別であり、意図的な現状維持である。**Melos runでは
japanese_title="走れメロス(The Three-Day Promise)"がFamily Z runnerに
既定義済み**(`STORY_REGISTRY['melos']['japanese_title_text']`、L186)。
本Phaseでは「Titleが誤って古いRole Style経路に落ちないか」を、実装時に
runtime evidenceで確認する項目として記録する(STOP非該当、確認項目)。

**backendゲート**: J3/E2はいずれも`--tts-backend speech_metadata_
flash_lite`明示時のみ有効(既定backend=`structured_separation`では
従来のJA長文prefix/E0のまま)。Family Z TTS stage実装時は、この
backendを既定として使うか明示指定するかをFable/ユーザーに確認する
必要がある(委任文はChampion phraseがFlash-Lite backend前提のため、
Flash-Lite backend明示が前提と解釈するのが自然。STOP非該当、実装時の
確認事項として記録)。

### §3(e) 固定Master(Champion)phrase一覧

Family Zが実際に使う可能性のあるMaster固定phrase(音声構造上必要な
もののみ、無理に追加しない):

| phrase | Family Zで必要か | Champion(delegation記載値) | CURRENT_SPEC記載値(L1616-1638) |
|---|---|---|---|
| welcome | 要(番組冒頭は全Family共通) | A(現行Master継続) | 一致 |
| preview_intro | 要(Preview前の導入) | C | 一致 |
| key_phrases_intro | 要(Key Phrase前の導入、§3(g)適用可否に依存) | C | 一致 |
| full_story_intro | 要(Full Story前の導入) | C | 一致 |
| num_one | 要(Key Phrase番号読み上げ、5件なら1〜5全部使用) | C | 一致 |
| num_two | 要 | B | 一致 |
| num_three | 要 | **B take1**(delegation記載) | CURRENT_SPEC「未確定」(`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01`で継続Trial中、L1636) |
| num_four | 要 | C | 一致 |
| num_five | 要 | **B take1**(delegation記載) | CURRENT_SPEC「未確定」(同上) |
| point_explanation(JA) | **不要**(Family ZはPoint One/Two構造を持たない、Family A固有機構) | B | 一致(だが適用対象外) |

**SSOT差異(STOP非該当、報告事項)**: num_three/num_fiveはCURRENT_SPEC
上ではまだ「未確定」(2026-09-28時点でRetrial継続中)だが、本委任文は
「B take1」を既定値として明記している。これはFable/ユーザーが本委任
発出までに追加決定した可能性が高いが、CURRENT_SPEC自体はまだ未反映
(Retrial-01の結果が別途Production反映されるまでの間)。**本タスクの
実装時(Phase B)には、実装直前に`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-
RETRIAL-01`の最新Status/CURRENT_SPECを再確認することを推奨**(既存
Guardrail: 実装前SSOT再照合)。

Master Store自体(`er006_output/master_audio_store_01/manifest.json`)は
sha256/content-hashキーの汎用cacheであり、Family固有の登録は不要
(呼び出し関数が同じphraseテキスト・同じstyleでlookupすれば自動的に
reuseされる設計、346エントリ確認済み)。

### §3(f) Dialogue Voice

- **Quote境界・speaker判定**: `segment_plan.json`は既にDialogue単位で
  8 segmentへ分割済み(§3a)。3分割Contractの境界点(6,7)はいずれも
  segment境界と一致するため、**3分割後もQuote境界は保持される
  (テスト設計は§4)**。
- **body境界をまたぐDialogue**: 存在しない(境界点(6,7)は共にnarrator
  segmentの終端であり、Dialogue segmentの途中ではない)。
- **retry/fallback/Local Rewrite時のVoice assignment保持**: `er020_tts_
  retry_local_rewrite_01.py`のLocal Rewrite機構はsegment単位(1 TTS
  clip=1 segment_id)で動作するため、各voice-clip(story_001〜008)が
  個別にLocal Rewrite対象になっても、そのclip固有のvoice(narrator/
  dionysius/selinuntius)は変わらない設計(Local Rewriteはtext差し替え
  のみで、呼び出し元が指定するvoice/speaker自体は不変)。**確認要
  (実装時のruntime evidenceで検証、STOP非該当)**。
- **既知課題(known_gap、再掲)**: `resolve_narrative_role()`は
  `"full_story_part1"`/`"full_story_part2"`/`"full_story_part3"`の
  3つの完全一致文字列しかFULL_STORYと判定しない(L125-127)。Melosは
  実際には8 voice-clipに分割されるため、そのままでは大半のclipが
  Connected Speech対象外になる。**推奨設計(選択肢b寄り、STOP非該当だが
  Fable/ユーザー確認推奨)**: `resolve_narrative_role()`へ正規表現
  パターン(例: `^full_story_part\d+$`または`^full_story_seg\d+$`)を
  追加する。これはCURRENT_SPEC「共有moduleの扱い」節(L1411-1414、
  「共有module側の変更自体は妨げない」)の範囲内であり、既存の3つの
  完全一致は不変のまま(後方互換)追加のみ行う設計にできる。Family
  Zのsegment_id命名規約を`full_story_part01`..`full_story_part08`の
  ように拡張し、このresolverパターンで拾う想定(§8で優先順位を整理)。

### §3(g) Key Phrase schema互換性とAdvanced英語解説の対象可否

- **run_01のKP artifact(`key_phrases/`)**: `key_phrase_role`フィールド
  なし(4+1導入前のschema、commit `42b43772`時点)。**現行4+1契約
  (CURRENT_SPEC L1673、2026-09-28 APPROVED_FOR_PRODUCTION)とは非互換**。
- **既に4+1で再検証済みのMelos KP**: `er035_output/kp_4plus1_evidence_
  01/melos_a2/`(commit `0e6744e0`、`KEY-PHRASE-4PLUS1-TOPIC-PHRASE-
  PRODUCTION-01`)。`role_counts: {important: 4, topic: 1}`、
  `selection_status: KEY_WORDS_STRUCTURE_PASS`、
  `canonicalization_status: CANONICALIZATION_PASS`、
  `redundancy_qa_status: REDUNDANCY_PASS`。**この artifact をKey
  Phrase正式値としてreuseすることを推奨**(run_01の旧schema KPを
  そのまま使わない。再選定不要、新候補Trialも不要)。
- **Advanced(B1B)英語解説の対象可否**: `run_keyphrase_stage()`は
  `scaffold.run_key_phrases(article_text, kp_dir, article_id, "A2",
  process=None)`と、level引数を`"A2"`に固定している(L732)。Family
  Z Melosは**現状A2(Standard)のみ**で、B1B(Advanced)track自体が
  存在しない。したがって「Advanced Key Phrase英語解説」(CURRENT_SPEC
  L1677-1683、2026-09-28承認、B1B限定仕様)は**Family Z Melosには
  適用対象外**(B1Bが存在しないため機構自体が無関係、STOP非該当、
  「対象外なら適用しない理由」として上記を記録する)。OPEN-221
  (「Advanced Key Phrase音声に既存の英語解説トラックが存在しない」)も
  B1B文脈の既知課題であり、A2のみのFamily Z Melosには適用されない。

### §3(h) story_type分岐の維持箇所

`build_story_type_metadata()`(L560-566)がstory_type→
`fixed_audio_intro_text`/`ui_label`を機械的に決定する仕組みは既存
実装済み。Melosは`literature`のため両方`null`(UI表示なし・音声冒頭
追加なし)。この分岐自体は変更不要、TTS/Assembly実装時にこのmetadataを
正しく参照する(音声冒頭へ余計な文言を挿入しない)ことをGate確認項目に
含める。

### §3(i) Assembly/Audio Validation/playerのFamily Z構造対応

`er003_v1_n3_01_assemble.py`が複数Family(crosslevel/iran01 a2/
Family X)から共通利用されている汎用assembler(§1対応表#1参照根拠、
`grep -rl`結果)。Family Zの`stage_assemble()`はこの共有assemblerを
呼ぶ設計にする想定(Heading読み上げが存在しないFamily Z構造[今回の
3分割Contractは見出し新設をしない]と、Comment配置順序[Comment1→
body1(6clip)→Comment2→body2→Comment3→body3→Comment4→In One Line]を
音声順序リストとして渡す形)。既存Audio Validation Gate(既定OFF/opt-in
ON)もFamily非依存の共有機構のはずだが、本Phaseでは実際のAssembly実装
コードには着手していないため、Phase B着手時に該当関数のFamily非依存性
を実装直前に再確認することを推奨する(STOP非該当、確認事項)。

---

## §4 Regression/integration計画

1. **Dialogue境界テスト**: 3分割の境界点(6,7)がいずれも
   `segment_plan.json`のsegment境界(Quote境界)と一致し、Dialogue
   segmentの内部を切らないことをunit testで固定する(境界点計算
   ロジック自体をtest化し、将来別Storyでも同じ制約[Quote span除外]を
   守ることを保証)。
2. **story_type分岐テスト**: `literature`/`real_story`/`true_crime`の
   3値で`build_story_type_metadata()`が正しい`fixed_audio_intro_text`/
   `ui_label`を返すことを確認する既存test(存在すれば拡張、なければ
   新規)。
3. **resolve_narrative_role()拡張のregression**: §3(f)で正規表現
   パターンを追加する場合、既存の3完全一致(`full_story_part1/2/3`)・
   `point_one`/`point_two`・Family X既存挙動が変わらないことを
   `run_project_regression.py`で確認する(既存Family X/Family C testの
   PASS維持)。
4. **Dangling Reference Check対象**: 新規追加するComment4 prompt定数・
   segment_id命名変更(もしあれば)・CURRENT_SPEC追記箇所のクロス
   リファレンスを対象に含める。
5. **Connected Speech配線のtest**: 8 voice-clip全てに正しくrole/
   connected_speech_enabledが解決されることを、Melos実データ
   (`segment_plan.json`)を使ったintegration testで確認する。

---

## §5 E2E計画と費用概算(A/B分離)

### 5-A(一回限り: wiring/runtime evidence/E2E確認TTS/regression用生成)

**reuse可能(追加API呼び出し0)**:
- article.md(本文、既存)
- Comment1・In One Line(既存)
- Key Phrase(`kp_4plus1_evidence_01/melos_a2/`を正式採用すれば追加
  選定不要。役割整合性確認[topic該当語がFULL_STORY文脈で自然か]は
  read-onlyで完了可能)

**新規生成が必要**:
- Comment2/3(Family C既存関数呼び出し、1 call×2、Trial実績¥3/call
  換算で約¥6)
- Comment4(新規prompt、1 call、約¥3)
- Topic intro(未実装、生成方式次第だがテンプレート的短文なら¥3未満)
- TTS: Full Story 8 voice-clip + Preview + Comment1〜4(5件) +
  Topic intro + In One Line = 合計約15 TTS segment。Key Phrase音声
  (EN5+JA5=10 TTS segment、既存4+1 artifactのtext再利用、音声は
  新規)。**概算**: 直近実測(TTS-VARIABLE-ROLE-STYLE-PRODUCTION-
  WIRING-01確認regen、¥0.86/segment、Flash-Lite backend)を基準に、
  25 segment × ¥0.86 ≈ **¥21.5**(attempt2即時retry込み、fallback
  1回まで発生した場合は追加数円)。
- ASR validation: TTS Production仕様に内包済み(追加費用は上記
  TTS概算に含む想定)。
- Deviation Check等: 本文は既存reuseのため新規Deviation Check不要
  (article.mdが既に承認済みのため)。

**5-A概算合計**: **約¥30〜40**(Comment2/3/4のLLM call約¥9+TTS約
¥21.5+予備)。Guardrail案: **¥60**(実測乖離・fallback発生を見込んだ
安全マージン)。

### 5-B(量産継続: Family Z記事1本あたりの恒常差分)

- **3分割によるTTS call差**: News(Family X)は3 body=3 TTS clip程度
  だが、Family Zは1 body内に複数voice-clipを含みうる(Melosはbody1が
  6 clip)。1記事あたりのTTS call数はStory内のDialogue量に依存し、
  Newsより変動が大きい(短いDialogue往復が多いStoryほどcall数増加)。
- **Comment数差**: Family C(3 Comment)からFamily Z(4 Comment)への
  変更により、1記事あたり+1 LLM call(約+¥3)が恒常的に発生する。
- **Validator/retry恒常差**: pronunciation resolver・symbol
  normalization・ASR validationはFamily X既存実装と同一コード経路を
  想定しており、追加の恒常費用は基本的に発生しない(Family Xと同水準)。
  Dialogue Voice切替によりTTS segment数がNewsより多くなる分、
  attempt/fallback発生確率が比例して上がる可能性がある点のみ注記。

---

## §6 Gate証拠計画・Opus L2論点候補・STOP該当有無

**STOP該当**: **なし**(本Phaseで発見した論点はいずれも「既存承認仕様
から一意に決まる実装上の是正」の範囲内と判断した)。

**Gate 22項目の証拠計画(概要)**: initial path/retry/fallback/
regeneration/Local Rewrite/cache reuse整合は、Family X既存TTS Production
仕様(`er020_tts_retry_local_rewrite_01.py`)をFamily Z runnerから呼ぶ
実装で満たす想定。Dialogue Voice/story_type分岐/pronunciation resolver/
symbol normalization/Connected Speech/Master Store/runtime evidenceは
上記§3の設計どおり実装しruntime evidenceを取得する。actual model・
voice・style/integration・regression/Melos E2E完走/Audio Validation
PASS/SSOT反映/commit・push/Dangling Reference Checkは、Phase B/C実装
完了後にまとめて証跡化する(§4のtest計画を含む)。

**Opus L2論点候補(Mandatory、実装後1回)**:
1. Comment4の新規prompt設計(Family C本体を変更せずFamily Z所有で
   実装する方針)が、既存Family移行方針(「Family A/B/C向けに新規実装を
   行わない」)の趣旨に照らして適切か。
2. `resolve_narrative_role()`への正規表現パターン追加(§3f)の設計が、
   既存Family X/C挙動への影響なしに実装できているか。
3. §3(a)のbody1(6 voice-clip)構造が、News既存の「1body=1clip」前提と
   異なる点をAssembly/Audio Validationが正しく扱えているか。
4. num_three/num_fiveのChampion値(delegation記載のB take1)と
   CURRENT_SPEC上の「未確定」表記との整合(§3e)。
5. J3/E2のCURRENT_SPEC「適用範囲」記述をFamily Zにも及ぶよう更新する
   ことの妥当性(§3d)。

---

## §7 SSOT文案骨子

- **CURRENT_SPEC.md「Family Z(Fiction)」節**: 実装完了後、
  `PRODUCTION_WIRED`条件(L1317-1323)の充足状況を追記。3分割
  Contract・Comment4新設・Dialogue Voice確認結果・pronunciation
  resolver/symbol normalization適用結果を反映。
- **CURRENT_SPEC.md「可変segment Role Style(J3/E2)」節の「適用範囲」**:
  「Family X Standard(A2)」という限定表現を、Family Z Standard(A2)にも
  及ぶよう更新(§3d、§6論点候補5)。
- **CURRENT_SPEC.md「Key Phrase」節**: Family ZのKP artifact reuse方針
  (`kp_4plus1_evidence_01/melos_a2/`採用、run_01旧schemaは非採用)を
  明記。
- **DECISION_LOG.md**: 本Phase Aの調査結果・3分割試算・STOP非該当判定を
  1エントリとして記録(実装Phase B/Cでも追記継続)。
- **OPEN_ITEMS.md**: OPEN-185へ「Phase Aで構造論点を整理、実装はPhase
  B/Cへ」を追記。§3(f)のresolver拡張要否は新規OPEN登録候補(実装時に
  Fable判断)。
- **REPORT_LEDGER.md**: `FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-
  WIRING-01`行を新設、Phase A完了・Feedback待ちとして記録。

---

## §8 REFRESH-01との依存関係と実装順序

- **共通層(REFRESH-01が担当予定)**: 固定Master Champion(§3e)のMaster
  Store正式登録、J3/E2定数のCURRENT_SPEC「適用範囲」更新(Family X外への
  拡張)、3分割Contract自体のProduction実装(段落境界決定論分割の共有
  関数化)、Japanese Title J3対応、cache version管理。**本設計書
  執筆時点でREFRESH-01の設計書(`docs/pm/design_family_x_refresh_e2e_
  production_wiring_01.md`)はまだ存在しない(並行作業中)**。
- **Family Z固有(本タスクが担当)**: Comment4新設(Family Z所有prompt)、
  `resolve_narrative_role()`のFamily Z向けパターン拡張(§3f、共有layer
  への追加的変更のため技術的にはREFRESH-01と競合しうる。**同一ファイル
  `er020_tts_retry_local_rewrite_01.py`を両タスクが触る可能性がある
  ため、Phase B着手前に競合有無をFableに確認すること**)、Family Z
  TTS/Assembly stage実装(`er026`内)、Melos個別のcontent_facts
  (Comment2/3/4用)。
- **推奨実装順序**: (1) REFRESH-01が共通層(Master Champion登録・
  J3/E2適用範囲拡張・3分割共有関数)を完了させる、(2) その後Family Z
  側が共通層をreuseしつつ、Family Z固有部分(Comment4・
  resolve_narrative_role拡張・TTS/Assembly stage)を実装する。**もし
  並列実装が必要な場合は、共有ファイル(`er020_tts_retry_local_rewrite_
  01.py`、Master Store関連)の同時編集を避けるため、Fableが両タスクの
  差分所有権を明示的に調整する必要がある**(STOP候補ではなく、PM上の
  スケジューリング論点として報告)。

---

## Closeout証拠計画(13項目、概要)

実装Phase(B/C)着手時に、本設計書§3〜§6の設計に基づき: (1)runtime
evidence(TTS実行ログ・ASR結果)、(2)test結果(§4のregression計画)、
(3)Melos E2E完走音声・試聴ページ、(4)Audio Validation PASS記録、
(5)CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER反映、(6)commit・
push、(7)Dangling Reference Check結果、(8)Opus L2レビュー記録(§6
論点候補への回答)、(9)費用実測(§5概算との比較)、を`FAMILY-Z-MELOS-
PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_REPORT.md`として作成する
予定(本Phase Aでは未作成、Phase B/Cの成果物)。
