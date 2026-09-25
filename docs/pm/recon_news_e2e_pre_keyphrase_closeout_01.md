# recon_news_e2e_pre_keyphrase_closeout_01.md

管理ID: `NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01` / Phase A(read-only調査)
実行者: Sonnet(サンドイッチ委任)
日付: 2026-09-25
API呼び出し: 0件(¥0、read-onlyのみ)

凡例: 「事実」=ファイル内容から直接確認。「推測」=コード構造からの妥当な推論(未実行検証)。「未確認」=調査したが特定できず。

---

## A-1 未知読み解決の既存機構

### er006_pronunciation_research_01.py(事実)
- 入力: `entities: list[{"surface","entity_type","risk_reason"}]`。`research_pronunciations(entities, model="sonar")`でPerplexity APIへ**1リクエストで全件まとめて**問い合わせる(L96〜)。
- 出力(`RESEARCH_JSON_SCHEMA`、L21-52): 項目ごとに`entity_type`/`language_origin`/`canonical_spelling`/`expected_pronunciation_ipa`/`pronunciation_hint`(英語style instructionへ渡せるカタカナ的近似、例"oh-TOH-nee")/`alternate_pronunciations`/`confidence`(high/medium/low)/`ambiguity_note`。**日本語カタカナ表記は出力形式に含まれない**(pronunciation_hintは英語話者向けの近似表記)。
- 一次情報優先: Prompt(L56-89)で「本人・公式サイト・所属組織・公式インタビュー等の一次情報源を最優先、無ければ辞書等の二次情報源」と明記。confidence="high"は本人の発話音声が情報源の場合のみ(テキスト書き起こしのみの場合はmedium以下)。
- Web Search使用: Perplexity API自体(`https://api.perplexity.ai/chat/completions`、model="sonar")が検索機能を内包。OpenAI Web Searchとは別課金経路。
- コスト目安: OPEN-47実績で新規API支出¥27.89(複数固有名詞分)。CURRENT_SPEC.mdに「1topic 1requestへまとめると品質劣化(confidence low・hint空欄)が実測されている」との注記あり(個別クエリ推奨)。
- **Production配線状態(CURRENT_SPEC.md L1284-1285)**: Ledger→Secondary ASR Phrase Listへの配線のみ`DECIDED(配線済み)`。TTS Pronunciation Hint注入(英語TTSのstyle instruction)は`NOT_WIRED`(Ottoni検証でmixed/負の結果のため見送り中、OPEN-47)。**この経路はいずれも英語TTS向けであり、日本語ER-009 Gateとは無関係**。

### er006_pronunciation_ledger_01.py / ledger.json(事実)
- `LedgerKey(surface, entity_type, source_context)`のsha256先頭16桁をkeyにcache(`er006_output/pronunciation_ledger_01/ledger.json`)。`lookup()`でcache hit判定、`upsert()`で登録、`get_hint_for_text(text, min_confidence)`でtext中の既登録surfaceをconfidence順に返す。
- エントリ例(実データ): `Ottoni`(person、confidence=medium、pronunciation_hint="oh-TOH-nee")、`Malmö`(place、confidence=high)。**カタカナ表記フィールドは存在しない**(IPA+英語近似表記のみ)。
- 誰が書き込むか: `er006_pronunciation_ab_01_run.py`等のA/Bテスト用scriptからのみ実績あり。Production TTS生成6箇所への自動書き込みは配線されていない(上記CURRENT_SPEC L1285)。

### ER-009-JA-FOREIGN-TOKEN-GATE-01 検出ロジック(事実、`er003_audio_tts_asr_safety.py` L640-844)
- 実体モジュールは`er003_audio_tts_asr_safety.py`(`er009_ja_foreign_token_gate_01_test_01.py`はテストのみ、L14-16でこのモジュールをimport)。
- `classify_foreign_tokens_in_japanese_text(text, known_key_phrase_terms=None, reading_dictionary=None)`(L702-779)が4分類:
  1. `NEEDS_JAPANESE_PARAPHRASE`(制作内部ラベル「Part 1」等、`_INTERNAL_LABEL_RE` L669-671)
  2. `ENGLISH_PRONUNCIATION`(その記事のKey Phrase英語表現[`known_key_phrase_terms`]そのもの)
  3. `READING_DICTIONARY`(`DEFAULT_JA_READING_DICTIONARY`、L681-694に機械的固定登録: cm/kg/km/kcal/ceo/wi-fi/cafe/ai/it/ev/iot/dx/gps/sns/pc/gdp/eu/nasa/ar/vr/esg/nft、計21語)
  4. `HUMAN_REVIEW`(上記いずれにも該当しない残りのLatin文字トークン)
- `foreign_token_gate_requires_stop(findings)`(L782-785): カテゴリ4が1件でもあればTTS呼び出し自体をブロック(カテゴリ1〜3はブロックしない)。
- 検出対象はentity_typeを区別しない汎用ロジック(`_LATIN_TOKEN_RE = r"[A-Za-z][A-Za-z0-9\-\.']*"`)。person/organization/product/place/loanword/abbreviation/Latin tokenいずれも同じ扱いで、辞書に無ければ機械的にHUMAN_REVIEWへ回る(entity_type別の特別処理は無い)。
- 配線先: `er003_v1_n3_01_tts_generate.py`の`generate_charon_japanese_with_reading_safety()`(L293-323)・`generate_a2_japanese_with_reading_safety()`(L475-506、minimal fallback経路も内包)。**いずれも`reading_dictionary`引数を受け付けない**(関数シグネチャは`known_key_phrase_terms`のみ)。`classify_foreign_tokens_in_japanese_text()`自体はreading_dictionary引数を持つが、呼び出し元2箇所とも渡していない(L311-312、L497-498で`reading_dictionary=`を省略)。
- **Human Review記録**: `log_foreign_token_human_review()`(L833-843)が`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`へ追記のみ(**ステートフルなlockファイルは無い**)。同じtextを再度渡せば毎回同じ判定を返す**純粋関数**であり、「解除」という概念自体が存在しない。解決方法は(a)そのtextを言い換える、(b)`DEFAULT_JA_READING_DICTIONARY`(コード内定数)へ追加する、(c)`known_key_phrase_terms`に含める、のいずれかのみ。**「承認して解除するコマンド」は存在しない**(ユーザーが依頼した「Human Review Lockの解除正式手順」は、この4分類Gateには該当しない設計)。

### er011_human_review_lock_01.py(別機構、事実)
- **ER-009 Foreign Token Gateとは別モジュール**。TTS/ASR retry自体の暴走防止用(`review_lock_state.json`、segment単位でstate管理: `AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/`HUMAN_APPROVED`/`REGENERATE_APPROVED`/`RESOLVED`)。
- 正式解除手順: `approve_regenerate(out_path, text, approved_by="user")`(L357-)でREGENERATE_APPROVEDへ遷移、次の1回のみ再生成許可。
- **重要**: Meta a2のcomment_1/2/3は、ER-009 Gateが**TTS呼び出し自体より前**にSTOPPEDを返すため(`generate_a2_japanese_with_reading_safety`内、L499-505)、er011のReview Lock(`check_before_generation`/`guarded_generate`)には到達していない。実際`review_lock_state.json`にcomment_1/2/3のエントリは存在しない(grep確認済み)。**したがって`approve_regenerate()`は不要**、Meta「メタ」の場合はテキストを言い換えるか辞書へ登録すれば足り、追加の「unlock」操作は無い。

### Meta run GATE_BLOCKED状態の記録位置(事実)
- `er012_output/e_family_two_level_wiring_01/meta/a2/audit/tts_generation_results.json`: `comment_1`/`comment_2`/`comment_3`が`status: "STOPPED"`、`foreign_token_findings`に`{"token": "Meta", "category": "HUMAN_REVIEW", ...}`を記録(L192-247)。
- `er012_output/e_family_two_level_wiring_01/meta/a2/run_summary_assemble.json`: `{"status": "GATE_BLOCKED", "error": "EPISODE_BLOCKED_BY_AUDIO_VALIDATION: ... ['comment_1=STOPPED', 'comment_2=STOPPED', 'comment_3=STOPPED']"}`(全文確認済み)。
- `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(340行、テストのダミーデータ"Gloobargaxxx"も同一ファイルに混在——本番/テストでログパスが共有されている点に注意、本タスクでは変更しない)に実際の"Meta" HUMAN_REVIEW検出3件を記録(comment_1/2/3、L327-331相当)。
- **最小再開手順(推測、未実行)**: (1)「meta」→「メタ」を`DEFAULT_JA_READING_DICTIONARY`へ追加(コード変更=Production正式仕様、ユーザー承認要)、または呼び出し元2箇所へ`reading_dictionary`引数を新設して配線(コード変更、同様に承認要)。(2) `er012_e_family_entertainment_two_level_runner_01.py --stage tts`を再実行(`parts.json`のtext hashが変わらない限り既存RESOLVED segmentは再生成されない設計のため、comment_1/2/3のみ再生成される見込み)。(3) `--stage assemble`を再実行しGATE_BLOCKED解消を確認。

### SSOT該当管理ID(要約1行ずつ)
- `ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01`(CURRENT_SPEC.md L1284-1285): Pronunciation Ledger基盤、ASR側のみ配線済み、TTS Hint注入は未配線。
- `OPEN-47`(OPEN_ITEMS.md L184): Ottoni A/B検証で確実な改善効果を実証できず、対応方針`TBD`。
- `OPEN-50`(OPEN_ITEMS.md L190): TTS Batch配線は完了、TTS Pronunciation Hint配線は継続TBD。
- `ER-009-JA-FOREIGN-TOKEN-GATE-01`(CURRENT_SPEC.md L1090, L1244): 4分類Gate新設の経緯・設計・配線先、`DECIDED(PRODUCTION_WIRED)`。
- `ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01`(2026-09-12、CURRENT_SPEC L1244内追記): 辞書へAI/IT/EV等15略語追加、ユーザー承認済み前例(今回の「メタ」追加もこの前例と同型の変更になる見込み)。
- `OPEN-177`(OPEN_ITEMS.md L326)サブ項目(10): Meta a2のHuman Review待ちを起票。

### 欠けている部品(まとめ)
1. **er006 Research/Ledger出力(IPA+英語近似表記)→ER-009 Gate入力(`DEFAULT_JA_READING_DICTIONARY`のカタカナ表記)への変換ステップが存在しない**。データ形式が異なる(英語話者向け近似 vs 日本語カタカナ)。
2. **「当該run自動採用」と「恒久登録」を分離する仕組みが無い**。現状はコード定数`DEFAULT_JA_READING_DICTIONARY`への直接追加(=恒久・Production変更)以外に手段が無く、`classify_foreign_tokens_in_japanese_text`が受け付ける`reading_dictionary`引数は2つの呼び出し元(B1/A2の日本語TTS入口)まで配線されていない。ここへ引数を1つ追加すれば「当該run限定辞書」を実現する土台にはなる(実装するかはProduction変更のため要ユーザー承認)。
3. **confidence閾値によって「自動採用可否」を判定するロジックが無い**(research結果のconfidence high/medium/lowを、ER-009 Gateの採用判断に接続する処理が未実装)。
4. **entity_type別の特別扱いは元々存在しない**(person/organization/product/place/loanword/abbreviation/Latin tokenいずれも同一のLatin-token正規表現で検出されるため、種類による対応の欠落は無い。欠けているのは辞書充足度そのもの)。

---

## A-2 Meta "some parts of the calls"

### 存在するartifact(事実、grep確認)
`er012_output/e_family_two_level_wiring_01/meta/`配下:
- `b1b/article.md`(L9)、`a2/article.md`(該当箇所)
- `b1b/parts.json`、`a2/parts.json`(`part2`フィールド)
- `b1b/audit/b1_support_generation.json`、`a2/audit/a2_support_generation.json`(Comment生成時のcontext echo)
- `b1b/audit/review_lock_state.json`、`a2/audit/review_lock_state.json`(`full_story_part2`のcanonical_text_sha256・last_attempts_log.asr_text)
- `b1b/audit/tts_generation_results.json`、`a2/audit/tts_generation_results.json`
- `b1b/key_phrases/*.txt`、`a2/key_phrases/*.txt`(Key Phrase選定promptのcontext echo、3ファイルずつ)
- `b1b/narration/attempts/full_story_part2_attempt1_englishstyleprefixwidemargin.json`、`a2/narration/attempts/full_story_part2_attempt1_custom35d6860b.json`(TTS attempt記録)
- `scaffold_run_summary.json`、`player.html`(表示用echo)

**該当箇所はb1b/a2とも`full_story_part2`セグメントのみ**(comment_1/2/3や他segmentには出現しない、grep確認済み)。

### 再TTSが必要なsegment
- `full_story_part2`(b1b・a2の両方)。他segment(comment_1-4等)は無関係。
- b1bはTTS完了済み(`run_summary_tts.json`全OK、`full_story_part2`は既にRESOLVED状態で音声化・player.htmlへ収録済み)。a2の`full_story_part2`もOK(comment_1/2/3のみSTOPPED、`full_story_part2`自体は別問題で既にTTS完了)。

### 再TTS手段(事実+推測)
- `er003_v1_n3_01_tts_generate.py`の`generate_b1_segments()`/`generate_a2_segments()`(L673, L796)は**`parts.json`を`load_json()`で都度読み込む**(article.mdから毎回再分割するのではない、事実、L679/L802)。
- `er012_e_family_entertainment_two_level_runner_01.py --stage tts`(writerを再実行せず、`tts_gen.run_theme(theme)`のみ呼ぶ、L697/L373-380)。
- **手順(推測、未実行)**: `parts.json`の`part2`フィールドと`article.md`本文の該当文を"some parts of the calls"→"some of the calls"へ手動修正(b1b/a2両方)→`--stage tts`再実行。er011 Human Review Lockはtext変更時にsha256不一致で自動的に旧lockを無効化する設計(`er011_human_review_lock_01.py`docstring L44-46)のため、`full_story_part2`のみが再生成され、他の既にRESOLVEDなsegmentは再生成されない見込み(未実行のため確定ではない)。

### a2側のGATE_BLOCKED確認
事実確認済み(A-1参照): `run_summary_assemble.json`が`GATE_BLOCKED`、comment_1/2/3が`STOPPED`(Meta読み未確定)。`full_story_part2`自体はGATE_BLOCKEDの直接原因ではない(comment_1/2/3が原因)。

---

## A-3 Entertainment新Family(Family X)

### 既存の所在(事実)
- Family A(News)本来のcontract: `er003_v1_n3_01_articles_generate.py`(`### `x2 + `## In one line`、L166周辺に言及)。
- 現在Sewer/Metaで使われている**別runner**(News Entertainment専用、2026-09-25新設): `er012_e_family_entertainment_two_level_runner_01.py`。Advanced(B1)/Standard(A2)生成のcontract(`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01_REPORT.md` §2-3): `# Title` + 本文 + `### `x2(各30-60語)+ `## In one line`。**Family Aの`split_article_text`をそのまま再利用**している(`er003_v1_n3_01_scaffold_generate.py` L104-159、B1/A2共通)。
- `split_article_text()`(L104-159、事実): タイトル・本文(段落単位で語数バランス分割→part1/part2)・2つの`### `見出し(`point_one_heading`/`point_two_heading`)+本文(`point_one_body`/`point_two_body`)・`in_one_line`を機械的に抽出。**「自然な物語の切れ目」ではなく「語数の均等さ」でpart1/part2を分割**(L140-152、段落境界のうち合計語数差が最小になる位置を選ぶ)。
- Assembly順序(事実、`er003_v1_n3_01_assemble.py` `build_b1_timeline()` L677-733): Intro→Welcome→Topic intro→Notification→Preview→Notification→Key Phrases→Notification→Full story intro→**Comment 1**→**Full Story Part 1**→**Comment 2**→**Full Story Part 2**→**Comment 3**(bridge)→**Point Notification(SE)**→Point One heading→Point One body→**Point Notification(SE)**→Point Two heading→Point Two body→Comment 4→In One Line→Outro。
  - 既存の「SE」相当は`POINT_NOTIFICATION_MP3_PATH`(`parts["point_notification"]`、L717/L722)。Family Xで要求される「休憩点のSE」は、この既存音源をそのまま再利用できる可能性が高い(推測、未検証)。
  - ただし現行構造は「Part1→Comment→Part2→Comment(bridge)→**別建てのPoint 2区画(SE+見出し+本文)**」であり、ユーザー要求の「1つのStoryを連続保持しつつ3分割・各切れ目にSE+見出し」とは異なる(現行はStory 2分割+独立Point 2区画=計4本の音声ブロック、Family Xは連続Story 3分割=計3本)。

### 変更が必要なモジュール/関数 vs 継承可能なもの(表)

| 項目 | Family Xで変更必要か | 理由 |
|---|---|---|
| `split_article_text()`(scaffold_generate.py) | **要変更/要フォーク**(新関数として) | 現在は「2 Point見出し+本文」を抽出する専用ロジック。Family Xは「3 Story part+2つの非ネタバレ見出し」の抽出が必要で、契約(`### `の意味)自体が異なる |
| `build_b1_timeline()`/`build_a2_timeline()`(assemble.py) | **要変更/要フォーク** | Comment 1-3の挿入位置・Point区画の有無が異なる |
| Advanced/Standard Writer Prompt(`er003_v1_n3_01_advanced_adaptation_generate.py`等) | **要変更**(contract suffix行) | `### `の意味(Point見出し→Story区切り見出し)・語数制約(30-60語のPoint本文→Story Part3の語数)を変更する必要 |
| Ledger構築(`vfl01.build_researcher_prompt`/`build_verification_prompt`/`build_verified_ledger_text`) | **継承可能** | Fact/Ledger機構自体はStory構造と無関係 |
| `run_deviation_check`(Ledger整合性チェック) | **継承可能** | 同上(ただしA-4の懸念[逆方向使用パターンの適否]は共通課題) |
| Rewrite(vfl01.run_writer_with_technical_retry、構造Gate付きretry) | **継承可能**(構造Gateの中身[`### `x2の期待]だけ更新要) | retry primitive自体は汎用 |
| TTS(`generate_charon_japanese_with_reading_safety`等、ER-009 Gate含む) | **継承可能** | segment名が変わるだけで、TTS関数自体はtext+out_pathを受け取る汎用設計 |
| Audio Validation Gate / Human Review Lock(er011) | **継承可能** | segment単位の汎用機構 |
| Key Phrase選定(`run_key_phrases`) | **継承可能** | 記事本文から独立に選定する設計(REPORT §10参照) |
| Point Notification SE音源 | **継承可能**(用途を「Point区切り」→「Story区切り」へ転用) | 既存mp3をそのまま再利用できる見込み |

### 現行Meta B1版の重複/ネタバレ実例(`meta/b1b/article.md`から引用、3件以内)
1. **見出しの先出しネタバレ**: 本文L9「In internal tests, some parts of the calls were handled not by AI, but by human contract workers.」で既に「人間が担当していた」という核心が明かされているにもかかわらず、直後のPoint One見出し(L11)「### The hidden performer inside the phone call」が同じ「隠れた人間」を指し示す見出しになっており、見出しとしての驚き・先出し防止の役割を果たせていない。
2. **本文とPointの内容重複**: Point One本文(L13)「The call looked like a one-person performance, but another performer was hidden inside the piano.」は、本文L9の「a human was making the call. The AI only appeared to be performing alone.」と同じ事実(AIが1人で対応していたように見えて実は人間がいた)を比喩を変えて反復しているのみで、新規情報の追加が薄い。
3. **見出し自体のネタバレ**: Point Two見出し(L15)「### Privacy concerns led Meta to pause the feature」は、本文を聞く前に「Metaが機能を一時停止した」という結末情報を見出しの時点で開示してしまっている。

### 元R2所在パス(事実)
`docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md`(AI電話代行テーマ=Meta記事のR2)。Sewerの元R2は`sewer_revision2.md`(同ディレクトリ、詳細はA-4参照)。

### Trial実装の最小案(未実装、提案のみ)
- 新runner名案: `er0XX_e_family_x_entertainment_three_part_trial_01.py`(Production非接続、独立ファイル。既存`er012_e_family_entertainment_two_level_runner_01.py`をコピー・改変する形が最も安全[Family A/既存Entertainment runnerを直接改変しない])。
- 対象: Meta 1本のみ(既存Ledger[MUSE-001〜018]を`--ledger-file`で再利用、Sewerは事実性未解決のため対象外推奨)。
- Advanced(B1)のみで比較可能(3者比較=元R2[日本語]/現行Family A適用Production版[既存meta/b1b]/新Family X版、いずれもB1レベルで意味の比較は可能。Standard[A2]は日本語版ER-009 Gate問題と無関係な独立検証のため、コスト優先ならAdvancedのみで初回比較し、採否確定後にStandardへ展開する案を推奨)。
- 概算コスト(推測、実測ではない): text生成のみ(Advanced 1本、Ledger再利用)は前例(REPORT §14「Meta Advanced+deviation ¥1.01」)からの類推で**¥1〜2程度**。TTSあり(B1フル、13segment相当)は前例「Meta TTS(b1b+a2)¥4.08」の概ね半分(B1のみ)として**¥2〜3程度**、合計**¥5前後**。

---

## A-4 Sewer元Source

### Sewer R2作成経緯(事実、重要な発見)
`docs/evidence/news_iterative_r2_adoption_2026-09-24/README.md`および`comparison_and_decision.md`により判明:
- Sewer(下水道テーマ)は`NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01`(`er015_news_iterative_entertainment_trial_01.py`)で作成。
- **Original Promptには[ニュース]欄(Source Note)が無く、「老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討」というテーマ文1行のみが入力**(`NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01_REPORT.md` L10、L164、L184)。
- `comparison_and_decision.md` L93「下水道(Trial-01): Original Promptは[ニュース]欄なし(テーマ1行のみ)。**素材なしでLunaが自由に内容を構成**。」/ L94「Article A/B(Trial-02、AI電話代行[Meta]・旅行荷物)は実在の元記事[HTTP取得確認済み]に基づく中立的な素材文2〜3文を挿入」と明記。
- Fact維持確認(同ファイル L86)「下水道: Original自体が素材なし(テーマ文のみ)で生成されたため『Original創作』の判定対象が存在しない」。
- web_search使用: 4回すべて`web_search_call_count: 0`(L184)。

**結論(事実、推測ではない)**: **Sewer記事に「元Source URL」は存在しない**。Meta/旅行荷物(実在記事に基づく)とは異なり、Sewer記事はテーマ文1行からLLM(Luna)が自由に内容を創作したものであり、探すべき一次情報源自体が最初から無い。今回`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`でSewerのAdvanced生成がLEDGER_DEVIATION(MAJOR)で2回ともSTOPしたのは、事後的に構築したLedger(実在情報に基づく20 facts)と、素材なしで創作された記事本文の間に整合性が無いのは**構造的に当然**であり、Ledger構築方法やdeviation checkの不具合ではない可能性が高い。

### 現行runnerのSource URL明示入力可否(事実)
- `er012_e_family_entertainment_two_level_runner_01.py`の`load_or_build_ledger()`(L231-)は`--ledger-file <既存Ledger再利用path>`のみ受け付け、Source URLを直接渡す引数は無い。Ledger新規構築は`vfl01.build_researcher_prompt`等(内部でweb_search、テーマ文のみから調査)に委ねる設計。
- 最小の追加方法(推測、未実装): `--source-urls`のような引数を新設し、Researcher promptへ「この記事のみを情報源として使う」という制約文を追加する改修が考えられるが、**Sewerには元々そのようなURLが存在しない**ため、この改修自体は今回のSewer問題の解決にはならない。

### 現在のSewer run状態(事実)
`er012_output/e_family_two_level_wiring_01/sewer/b1b/audit/rejected_advanced_attempt2.md`に不採用の2回目生成全文を保存。Advanced段でSTOP(LEDGER_DEVIATION MAJOR×2件)、Standard(A2)段は未実行(入力が無いため到達せず)。TTS/Assembly/player.htmlも未生成。

---

## A-5 TTS mode

- `er012_e_family_entertainment_two_level_runner_01.py`(L37, L632, L649、事実): `--tts-mode`既定値`STANDARD`、`TTS_EXECUTION_MODE`環境変数へ設定。`BATCH`指定時は`--batch-reason`必須(未指定はエラー)。**今回の経路(Sewer/Meta/将来のFamily X trial runnerも同型で作る前提)は既定STANDARD**。
- 前回audit(`docs/pm/tts_mode_audit_2026-09-25.md`)で「要判断」だった2項目:
  - `er013_family_c_production_runner_01.py`: **非該当**(今回のNews Entertainment[Sewer/Meta]・Key Phrase作業の経路には含まれない、別Family C専用runner)。
  - voices modules importers(`er012_b_family_voices_a2_production_01.py`/`er012_b_family_voices_production_01.py`を import する未確認の呼び出し元群): **非該当**(今回の経路は`er012_e_family_entertainment_two_level_runner_01.py`→`er003_v1_n3_01_tts_generate.py`が直接使う構成で、Family B voicesモジュール経由ではない)。
- segment再TTS(A-2の手動修正後の再実行)は同じrunnerの`--stage tts`を使う想定のため、STANDARD既定を継承する(A-2参照)。

---

## Fableへの推奨作業順序(1案)

1. **A-4(Sewer)を先にFable/ユーザーへ報告し方針決定**(実装作業なし、¥0)。「Sourceが存在しない創作記事」という事実確認の結果であり、実装的な解決策(Ledger再構築等)では直らない。「別テーマへ差し替え」「観測記録として保留」等の判断が先に必要で、これを後回しにすると他の作業と並行して無駄なLedger再構築コストが発生しうる。
2. **A-2(Meta "some parts of the calls"修正+再TTS)を次に実施**(推定コスト¥1〜3、TTS再生成1segment×2レベル分のみ)。手順は本ドキュメントA-2節のとおり単純(parts.json+article.mdの手動修正→`--stage tts`→`--stage assemble`)。Sewerと独立に進められ、コストも小さい。
3. **A-1(未知読み"メタ"個別登録+包括フローの最小Trial)を実施**。まず「メタ」個別解決(`DEFAULT_JA_READING_DICTIONARY`へ追加、ユーザー承認要、前例[ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01]と同型)でMeta a2のGATE_BLOCKEDを解消(推定コスト¥1未満、TTS再生成3segment)。包括フロー(検出→辞書→Research→自動採用→Human Review)の最小Trialは、個別解決より設計・実装コストが高いため、個別解決で急場をしのいでから別枠で着手する方が「1記事ずつ完結原則」に沿う。
4. **A-3(Family X Trial)は最後**。他の3項目より設計変更範囲が大きく(新runner・新contract・新Assembly timeline)、コストも相対的に高い(¥5前後、B1のみの場合)。A-1〜A-4の決着(特にSewerの扱い、Metaの読み)がついてから、Meta 1本で独立Trialを行う方が手戻りが少ない。

合計概算(実装・API実行を伴う2〜4のみ、text生成+最小TTS想定): 約¥7〜10程度(A-1個別解決+A-2修正+A-3 Trial Advancedのみの場合)。A-3をTTSまで含めると+¥2〜3程度。

---

## 付記(Phase Aで発見したが本タスク範囲外の事実)

- `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`に、unit testのダミーデータ("Gloobargaxxx"、複数回重複)と実際のProduction run記録("Meta")が同一ファイルへ混在している。テスト実行時に本番ログファイルへ書き込まれている可能性があり(ログパスがテスト・本番で共有)、実務上ログの可読性を下げている。本タスクでは変更していない(範囲外、報告のみ)。
