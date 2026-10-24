## 固有名詞発音アラーム(運営責任者向け・一般リスナー非表示)
1箇所。最終状態=**アラーム付き完成**。制作は停止せずHuman Reviewにも回していません。確認・承認操作は完成の条件ではありません。
- **gacha** × 1箇所
  - [X/a2/topic_intro] er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/a2/narration/topic_intro.wav / 文脈 `...ord Hunting Starts with an English Word [[gacha]]....` / 目安7.8秒
    - 検出した不一致: 原稿 `gacha` -> Primary `gotcha` / Secondary `gotcha`
    - 発音の根拠(Ledger/Perplexity調査): 階層=NAME_IN_CITED_PAGE / 確信度=medium / hint=GOT-chuh
    - TTS発音改善: 供給なし(no_ledger_entry_or_not_planned)
    - 最終状態: アラーム付き完成 / 使用モデル: ASR=gpt-4o-mini-transcribe, Secondary=azure-speech-stt, TTS=gemini-3.8-flash-lite-tts

### 発音供給の適用一覧(TTS入力へ綴り置換した語。ASR比較は置換後の綴りが基準)
0件(供給対象なし。A階層の自動供給対象/人承認済みB階層が無い、または該当語が本文に無い)

### Human Review残(受理境界の外): ASR不確実のまま残ったsegment 0件 (うち固有名詞のみ不一致だが境界外=脱落/一般語化等 0件)

注: 日本語音声の固有名詞読みはこのアラーム方針の対象外です(従来の検証・Human Reviewのまま)。

### 実体表(固有名詞と認識した根拠。受理判定用。発音の根拠[Ledger/Perplexity調査]とは別)
- 実体表: 3件(うち証拠として使用可 1件) / NER call=2 / model=gpt-6-luna / table_sha256=55aa58a2e3f7
- 実体表 brand_product/confirmed: 1件
- 実体表 other_named/weak: 2件
- 証拠にならなかった語(weak/一般語等): UR, Jackpot
- 除外された候補: I Checked the Rarity Before Learning the Words: “Rare-Word Hunting” Starts with an English-Word Gacha[long_phrase], I Checked How Rare the Words Were Before Learning Them: “Rare-Word Hunting” Starts with an English Word Gacha[long_phrase]
