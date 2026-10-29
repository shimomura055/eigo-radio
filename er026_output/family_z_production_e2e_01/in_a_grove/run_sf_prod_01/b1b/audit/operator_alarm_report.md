## 固有名詞発音アラーム(運営責任者向け・一般リスナー非表示)
2箇所。最終状態=**アラーム付き完成**。制作は停止せずHuman Reviewにも回していません。確認・承認操作は完成の条件ではありません。
- **tajomaru** × 1箇所
  - [Z/b1b/comment_3] er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/b1b/narration/comment_3.wav / 文脈 `...[[tajomaru]] says he freed Takehiro, and they fought...` / 目安0.0秒
    - 検出した不一致: 原稿 `tajomaru` -> Primary `tanjuromaru` / Secondary `taj mahal`
    - 発音の根拠(Ledger/Perplexity調査): 階層=PRON_IN_CITED_PAGE / 確信度=low / hint=tah-joh-MAH-roo
    - TTS発音改善: 供給なし(no_ledger_entry_or_not_planned)
    - 最終状態: アラーム付き完成 / 使用モデル: ASR=gpt-4o-mini-transcribe, Secondary=azure-speech-stt, TTS=None
- **takehiro** × 1箇所
  - [Z/b1b/comment_3] er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/b1b/narration/comment_3.wav / 文脈 `...Tajomaru says he freed [[takehiro]], and they fought with swords. What does...` / 目安1.3秒
    - 検出した不一致: 原稿 `takehiro` -> Primary `takahiro` / Secondary `takahiro`
    - 発音の根拠(Ledger/Perplexity調査): 階層=NAME_IN_CITED_PAGE / 確信度=medium / hint=tah-KEH-hee-roh
    - TTS発音改善: 供給なし(no_ledger_entry_or_not_planned)
    - 最終状態: アラーム付き完成 / 使用モデル: ASR=gpt-4o-mini-transcribe, Secondary=azure-speech-stt, TTS=None

### 発音供給の適用一覧(TTS入力へ綴り置換した語。ASR比較は置換後の綴りが基準)
0件(供給対象なし。A階層の自動供給対象/人承認済みB階層が無い、または該当語が本文に無い)

### Human Review残(受理境界の外): ASR不確実のまま残ったsegment 0件 (うち固有名詞のみ不一致だが境界外=脱落/一般語化等 0件)

注: 日本語音声の固有名詞読みはこのアラーム方針の対象外です(従来の検証・Human Reviewのまま)。

### 実体表(固有名詞と認識した根拠。受理判定用。発音の根拠[Ledger/Perplexity調査]とは別)
- 実体表: 4件(うち証拠として使用可 3件) / NER call=1 / model=gpt-6-luna / table_sha256=5de0d58efc39
- 実体表 person/confirmed: 3件
- 実体表 work_title/weak: 1件
- 証拠にならなかった語(weak/一般語等): In a Grove
