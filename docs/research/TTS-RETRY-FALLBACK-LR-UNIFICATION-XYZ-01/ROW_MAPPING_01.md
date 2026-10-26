# ROW_MAPPING_01 — 棚卸し49行 → 新仕様の対応表(機械照合済み)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(設計・read-only)。入力=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/consolidated_01.json` `star_table_1`(49行)。構造化版=`ROW_MAPPING_01.json`。

**漏れ0の機械確認**: 入力49行のIDと本表の対応IDが完全一致(生成スクリプトのassert: `set(入力ID)==set(対応ID) and len==49`。実行結果=PASS)。行数 X=16/Y=19/Z=14。

## 1. policy別の行数(合計49)

| policy | 内容 | 行数 | 最大TTS | 最大待機 | LR |
|---|---|---|---|---|---|
| EN_LR_STD | 英語・LRあり(Std) | 10 | 6 | 2回(360秒) | あり(最大1回) |
| EN_LR_ADV | 英語・LRあり(Adv) | 14 | 6 | 2回(360秒) | あり(最大1回) |
| JA_STD | 日本語(Std) | 8 | 3 | 1回(180秒) | なし |
| KP_EN | Key Phrase英語phrase | 6 | 4 | 1回(180秒) | なし |
| KP_EXPL | Adv KP英語解説 | 3 | 3 | 1回(180秒) | なし(現行どおり。新設しない) |
| Z_DLG_CTX | Zセリフ(ctx方式) | 2 | 3 | 1回(180秒) | なし(今回追加しない) |
| Z_DLG_LEGACY | Zセリフ(legacy方式=ロールバック/既存run) | 2 | 3 | 1回(180秒) | なし |
| SHELL_EN | shell固定英語(表外) | 3 | 3 | 0回(0秒) | なし |
| NO_TTS | TTSなし(固定mp3) | 1 | 0 | 0回(0秒) | — |
| 合計 | | 49 | | | |

LRあり行 = EN_LR_STD(10)+EN_LR_ADV(14)=24行(現行22行+Z topic_intro_en Std/Advの2行=24行)。

## 2. policy定義(全行共通の新仕様。ユーザー原文§2・§3)

| policy | ①② | 待機 | ③ | LR | LR後構成 | 最大TTS/待機 | 最終NG |
|---|---|---|---|---|---|---|---|
| EN_LR_STD | role Style(呼出側指定のまま。Std本文系=6%減速Style)の同一Styleで①② | ②NG後・③直前に180秒 | ③=既存の短文Style(minimal。force_secondary維持) | あり(最大1回) | LR後: ①'②'=同じroleStyle→180秒→③'=短文Style(再入なし) | 6/2回 | LR block最終NG→Lock+英語HRQ(1行)→Gate BLOCK/STOP |
| EN_LR_ADV | role Style(呼出側指定のまま)の同一Styleで①② | ②NG後・③直前に180秒 | ③=既存の短文Style(minimal)【新規適用。旧=Style不変】 | あり(最大1回) | LR後: ①'②'=同じroleStyle→180秒→③'=短文Style(再入なし。旧=role Style脱落/再入) | 6/2回 | LR block最終NG→Lock+英語HRQ(1行)→Gate BLOCK/STOP |
| JA_STD | 日本語Style(呼出側)の同一Styleで①② | ②NG後・③直前に180秒【新規。旧=待機なし】 | ③=既存の日本語短文Style(JA minimal instruction) | なし | — | 3/1回 | ③NG→Lock+日本語HRQ→Gate BLOCK/STOP |
| KP_EN | 前段Style(X/Z=K2、Y=MINIMAL[U-15は別件・不変])で①② | ②NG後・ENGLISH_LOCK段の直前(実TTS直前のみ)に180秒【新規】 | ③④=ENGLISH_LOCK(後段2回。既存どおり) | なし | — | 4/1回 | ④NG→Lock+英語HRQ(slot4)→Gate BLOCK/STOP |
| KP_EXPL | 解説Style(P3系。呼出側指定)の同一Styleで①② | ②NG後・③直前に180秒【新規】 | ③=既存の短文Style(minimal)【新規。適合性確認済み=DESIGN_01 §8】 | なし(現行どおり。新設しない) | — | 3/1回 | ③NG→Lock+英語HRQ→Gate BLOCK |
| Z_DLG_CTX | ctx Style(文脈・感情付き)で①② | ②NG後・③直前に180秒(旧600秒→180秒) | ③=承認済みの従来Dialogue Style(style_prefix_override=None) | なし(今回追加しない) | — | 3/1回 | ③NG→Lock→TERMINAL_NG→HR/STOP(rc=2) |
| Z_DLG_LEGACY | 従来Dialogue Styleで①② | ②NG後・③直前に180秒【新規】 | ③=従来Dialogue Style(同一。Style変更なし) | なし | — | 3/1回 | ③NG→Lock→HR/STOP(rc=2) |
| SHELL_EN | 現行どおり(同一Style①②③・F-Techのみ) | なし(現行維持) | 同一Style(現行維持) | なし | — | 3/0回 | 現行どおり(Lock+HRQ→SharedNarrationBlockedError) |

## 3. 49行の対応(現行→新仕様)

| ID | Family/Lv | 部位 | 現行(総/LR/分類) | policy | 変更種別 | 設計項目 | 備考 |
|---|---|---|---|---|---|---|---|
| X-S01 | X | topic_intro(英語・Aoede) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312) | D1,D2,D4,D5,D6,D12,D14 |  |
| X-S02 | X | 日本語: japanese_title・preview・comment_1〜4・KP日本語意味 | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 |  |
| X-S03 | X | shell固定日本語『ポイント解説』(A2のみ生成) | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 | shell固定日本語(ポイント解説)。JA関数共通 |
| X-S04 | X | full_story_part1〜3(英語・6%減速) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | 減速後再検証NGも通算の「attempt NG」として数え、最終NGはLRへ(旧U-09=LRなしHRを解消。D6) |
| X-S05 | X | full_story chunk _k{j}(段落が2つ以上のpart) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | chunk単位で独立に3回構成+LR(chunk構造・境界は保持。D6) |
| X-S06 | X | in_one_line(英語・6%減速) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | 文数不変Gate維持 |
| X-S07 | X | Key Phrase英語phrase kpN_en | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 |  |
| X-A01 | X | topic_intro(英語・Charon) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| X-A02 | X | preview(英語・Charon) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| X-A03 | X | comment_1〜4(英語・Charon) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | disfluency NGのみ(U-03)はLR適用判定でNO_NG_SPAN→③NG直後に即HR(待機・③は省略しない。D5) |
| X-A04 | X | full_story_part1〜3(単一段落part・PD06) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| X-A05 | X | full_story chunk _k{j} | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | chunk単位 |
| X-A06 | X | in_one_line(英語) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | 文数不変Gate維持 |
| X-A07 | X | Key Phrase英語phrase kpN_en | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 |  |
| X-A08 | X | Key Phrase英語解説 kpN_explanation_en | 総3/LR×/C | KP_EXPL(3回・待機1) | 待機新設(180)、③短文Style新規 | D1,D2,D9,D12,D14 | 正式経路でTTS音声実在(er019:2218 timeline、Y=er121_audio:783、Z=er063:584 ClipSpec) |
| X-A09 | X | shell固定英語9(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five。Adv/Std共通key) | 総3/LR×/C | SHELL_EN(3回・待機0) | 変更なし(表外) | (対象外=表に名指しなし。現行維持。DESIGN_01 §7 A-1) | Master Audio Store再利用で生成0が通常。399 entry失敗0。現行維持(A-1) |
| Y-S-01 | Y | shell固定英語9(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five) | 総3/LR×/C | SHELL_EN(3回・待機0) | 変更なし(表外) | (対象外=表に名指しなし。現行維持。DESIGN_01 §7 A-1) | 同上 |
| Y-S-01b | Y | shell固定日本語 point_explanation『ポイント解説』 | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 | Y a2 timeline未使用(U-17。生成時のみ適用) |
| Y-S-02 | Y | topic_intro(英語) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312) | D1,D2,D4,D5,D6,D12,D14 |  |
| Y-S-03 | Y | japanese_title(日本語タイトル) | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 |  |
| Y-S-04 | Y | 日本語支援文 preview/comment_1/comment_2/comment_3(Stdはcomment_2を維持) | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 |  |
| Y-S-05 | Y | ナレーター本文5(y_lead/y_intro_1〜3/y_closing・6%減速) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | Y Gate: ③/LR採用は現行どおりGate承認要(D13=変更なし) |
| Y-S-06 | Y | Voice本文3(y_voice_1 Puck/y_voice_2 Zephyr/y_voice_3 Schedar・6%減速) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | Voice既定Style不変。Y Gate同上 |
| Y-S-07 | Y | 本文chunk y_<segment>_k<j>(段落2つ以上のときのみ。現行Y契約は各Voice1段落) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | chunk単位 |
| Y-S-08 | Y | Key Phrase英語 kp{rank}_en(3件) | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 | 前段=MINIMAL(U-15=OPEN-537は別途。本件で変更しない) |
| Y-S-09 | Y | Key Phrase日本語意味 meaning_{i}(3件) | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 |  |
| Y-B-00 | Y | Intro/Notification1-3/Outro(固定mp3) | 総-/LR—/— | NO_TTS(0回・待機0) | 変更なし | — | 固定mp3読込のみ。変更なし |
| Y-B-01 | Y | shell固定英語9(Y-S-01と同一key) | 総3/LR×/C | SHELL_EN(3回・待機0) | 変更なし(表外) | (対象外=表に名指しなし。現行維持。DESIGN_01 §7 A-1) | shell固定英語。現行維持(A-1) |
| Y-B-02 | Y | topic_intro(英語) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| Y-B-03 | Y | preview/comment_1/comment_3(Comment 2は2026-10-26承認で削除) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| Y-B-04 | Y | ナレーター本文5(y_lead/y_intro_1〜3/y_closing=Tension+Closing) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | Y Gate: ADV_MINIMAL_FALLBACK等は③採用時に発火(現行Gate不変。D13) |
| Y-B-05 | Y | Voice本文3(y_voice_1/2/3) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | Voice既定Style不変(①②)。U-03が最頻の部位(OPEN-536/533) |
| Y-B-06 | Y | 本文chunk y_<segment>_k<j> | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | chunk単位 |
| Y-B-07 | Y | Key Phrase英語 kp{rank}_en(3件。phrase_repeatは新規生成せず同一entry複製) | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 | 前段=MINIMAL(U-15別件) |
| Y-B-08 | Y | Key Phrase英語解説 kp{rank}_explanation_en(3件) | 総3/LR×/C | KP_EXPL(3回・待機1) | 待機新設(180)、③短文Style新規 | D1,D2,D9,D12,D14 | 正式経路でTTS音声実在(er121_audio:783) |
| Z-A2-NARR | Z | 地の文(narrator) full_story_part{n}_c{k}・100語超はchunk _k{j}(6%減速・PD06) | 総4/LR○/A | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、減速後最終NGもLRへ(旧U-09) | D1,D2,D4,D5,D6,D12,D14 | chunk(100語超)も同一。減速後再検証をattempt内へ(D6) |
| Z-A2-DIALOGUE-CTX | Z | 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定) | 総3/LR×/C | Z_DLG_CTX(3回・待機1) | 待機(旧600→180) | D1,D2,D10,D12,D14 | Std: 減速なし |
| Z-A2-DIALOGUE-LEGACY | Z | 登場人物のセリフ(dialogue) policy=legacy(既存run・ロールバック時) | 総3/LR×/C | Z_DLG_LEGACY(3回・待機1) | 待機新設(180) | D1,D2,D10 |  |
| Z-A2-TOPIC | Z | Topic intro(topic_intro_en・Aoede) | 総3/LR×/B | EN_LR_STD(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、分類是正(U-06)+LR有効化 | D1,D2,D4,D5,D6,D12,D14 | clip_id topic_intro_enの役割解決是正(U-06/OPEN-538)でcooldown+LRが初めて有効。旧=総3・LRなし。D11 |
| Z-A2-JA | Z | 日本語: japanese_title/preview/comment_1〜3 | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 |  |
| Z-A2-KPEN | Z | Key Phrase英語 kp{r}_en | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 |  |
| Z-A2-KPJA | Z | Key Phrase日本語意味 kp{r}_ja | 総3/LR×/A | JA_STD(3回・待機1) | 待機新設(180) | D1,D2,D7,D12,D14 | KP日本語意味。JA関数共通 |
| Z-B1B-NARR | Z | 地の文(narrator) full_story_part{n}_c{k}・100語超はchunk _k{j}(PD06) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 | chunk(100語超)も同一 |
| Z-B1B-DIALOGUE-CTX | Z | 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定) | 総3/LR×/C | Z_DLG_CTX(3回・待機1) | 待機(旧600→180) | D1,D2,D10,D12,D14 | Adv: 約6%高速化→減速後再検証は従来どおり外側ループで通算に数える(U-07据置。D10) |
| Z-B1B-DIALOGUE-LEGACY | Z | 登場人物のセリフ(dialogue) policy=legacy | 総3/LR×/C | Z_DLG_LEGACY(3回・待機1) | 待機新設(180) | D1,D2,D10 | Adv高速化は従来どおり |
| Z-B1B-TOPIC | Z | Topic intro(topic_intro_en・Charon) | 総3/LR×/B | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変)、分類是正(U-06)+LR有効化 | D1,D2,D3,D4,D5,D12,D14 | clip_id役割解決是正(D11)。旧=総3・LRなし |
| Z-B1B-PREVCOM | Z | Preview英語(E1)/Comment 1-3英語(E2_UPBEAT) | 総4/LR○/A | EN_LR_ADV(6回・待機2) | 待機(旧600→180)、LR後構成(旧1回→3構成)、LR再入禁止(OPEN-376)、Style保持(OPEN-312)、③Fallback Style新規(旧=Style不変) | D1,D2,D3,D4,D5,D12,D14 |  |
| Z-B1B-KPEN | Z | Key Phrase英語 kp{r}_en | 総4/LR×/A | KP_EN(4回・待機1) | 待機新設(180・ENGLISH_LOCK段直前) | D1,D2,D8,D12,D14 |  |
| Z-B1B-KPEXPL | Z | Key Phrase英語解説 kp{r}_explanation_en(P7) | 総3/LR×/C | KP_EXPL(3回・待機1) | 待機新設(180)、③短文Style新規 | D1,D2,D9,D12,D14 | 正式経路でTTS音声実在(er063:584 ClipSpec kp_expl_en、er026 kp_explanations) |

## 4. Adv KP英語解説の音声実在・短文Style適合性
DESIGN_01 §8を正とする(本表のKP_EXPL行はその結論を反映)。

