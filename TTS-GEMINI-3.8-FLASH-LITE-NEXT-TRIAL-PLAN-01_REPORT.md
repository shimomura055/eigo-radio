# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-PLAN-01 REPORT

管理ID: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-PLAN-01`
性質: **計画作成のみ**。Trial実行なし・TTS/LLM API呼び出し0件・Production
変更0件。API実費用: **¥0**。

## §0 要約

前回Trial(TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01、REJECTED方向)の失敗原因を、
公式一次情報(すべてHTTP GET取得、検索API不使用)と突合した結果、
**最重要の技術的発見**が得られた:

Gemini 3.8系TTSモデル(`gemini-3.8-flash-tts`/`gemini-3.8-flash-lite-tts`)は、
公式ドキュメント(`speech-generation`ガイド、逐語)で
「input textを一字一句そのまま読み上げるverbatim transcriptとして扱う」
と明記されており、style/speaker指示は本文に混ぜず`speech_metadata`という
**構造化フィールド**で渡すことを公式に要求している。前回Trialが使った
現行Production方式(Structured Separation、本文内にdelimiterでstyle指示を
埋め込む方式、`er003_b1_p4c_audio.build_tts_prompt`)は、旧世代モデル
(`gemini-2.5-pro-preview-tts`/`gemini-3.1-flash-tts-preview`)向けに検証
された仕組みであり、Gemini 3.8系の設計思想と正面から矛盾する。これは
前回の症状(指示文の読み上げ、長文ほど悪化する無関係内容生成)と整合する
仮説であり、断定ではないが有力である。

副次的発見: Gemini 3.8系はデフォルトでWAV(RIFFヘッダ付き)音声を返す
(旧モデルはヘッダ無し生PCM)。現行`pcm_bytes_to_float_mono`はヘッダ無し
前提のため、これも未対応だった(影響は軽微と推測、前回3segment成功と
整合)。

公式pricing(`https://ai.google.dev/gemini-api/docs/pricing`)で
`gemini-3.8-flash-lite-tts`の正式単価(Standard: 入力$0.50/output$6.00
per 1M tokens、2026年12月31日まで)を確認済み(前回はproxy推定のみ
だった)。Voice名(Charon/Aoede/Algieba/Erinome/Schedar)は引き続き公式
prebuilt voiceとして有効、日本語・英語とも対応言語内。

以上を踏まえ、計画doc(`docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`)
に、次回Trialで(a) style指示を`speech_metadata`へ外出しする、(b)
まず簡潔なstyle(または空)から試す、(c) 音声フォーマットを明示/防御的に
扱う、(d) pricing_snapshot.jsonへ公式単価を登録する、(e) 1→2〜3→1記事の
段階拡大、(f) ¥500 Capを**呼び出し前の事前ガード方式**で実装する、
という方針をまとめた。Voice/ASR検証/retry上限(標準2+fallback1=計3回)/
既存異常長検知は変更しない。

## §1 到達Status

`TRIAL_PLAN_READY`。STOP該当なし。

## §2 主要な未確認事項(推測で埋めていない)

- GenerateContent API経由での`part.speech_metadata`実送信可否(SDK
  `types.Part`に型定義なし、dict代用の可否は未検証)。
- Interactions API経由での`speech_metadata`アノテーション受理可否
  (`AnnotationParam`のUnionに現バージョンでは未列挙)。
- `requirements-ci.txt`(google-genai==2.14.0)と実機`.venv`
  (2.11.0)のバージョン齟齬(本タスクで発見、影響未調査、計画doc §16に記録)。
- モデル別RPM/TPM(rate-limitsページがJS動的レンダリングのため未確認)。
- 実際のlatency改善有無。

詳細は`docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`§16参照。

## §3 代表segment候補(最終選定はユーザー)

対象article: `er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/`
(前回と同一、既存完成音声との比較可能性のため)。

1. `tension_reflection`(英語、Aoede、62.25秒)— 唯一「New York City」という
   固有名詞を含み、かつ前回B側が最も重度に失敗した(3/3attempt無関係内容
   生成)segment。根本原因修正の直接的な回帰チェックとして最有力候補。
2. `full_story_part1`(英語、Aoede、15.01秒)— 名称通り「Full Story」で
   通常品質確認に直接合致、長さ中庸。
3. `point_two_body`(英語、Erinome[Voice B]、44.06秒)— 3 Voices中の
   Narrator以外のvoiceでの代表例。

注記: 対象article全segmentに算用数字は1件も含まれない(CEFR-A2のため)。
「数字を多少含む」の条件は本article内では満たせない。

## §4 詳細

計画doc(全文、§1〜§17): `docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`

## §5 Production非変更・費用確認

- Production対象ファイル(`er003_*`/`er006_*`/`er011_*`/`er012_*`等)への
  変更: **0件**。
- pricing_snapshot.json(`er005_output/cost_baseline_01/pricing_snapshot.json`):
  **未変更**(登録案は計画doc §15に記載のみ、実際の追記はTrial実行時)。
- API呼び出し: **0件**(HTTP GETのみ、`ai.google.dev`静的ドキュメント
  ページの取得。TTS/ASR/LLM課金APIは一切呼んでいない)。
- git: 本REPORTと`docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`
  の2ファイルのみをpath指定でcommit・push予定(`ACTIVE_TASK_TTSP.md`等の
  一時ファイルは対象外)。

## §6 Fable評価(2026-09-27)

- Status `TRIAL_PLAN_READY` を承認(Fable判定)。委任条件(公式一次情報のみ・
  API呼び出し0・段階拡大・segment単位早期STOP・¥500 Capの事前ガード方式)は
  すべて充足。
- 前回失敗原因の仮説(3.8系はverbatim transcript設計、style指示は
  `speech_metadata`へ外出し)は公式docと整合し有力。ただし未検証であり、
  次Trialの最初のステップは「`speech_metadata`が現SDK経由で送れるか」の
  最小API形状確認(¥数円)とする。
- 代表segmentについて: 委任条件「数字を多少含む」は対象article(A2、算用
  数字なし)では満たせないとSonnetが正直に報告。Fable推奨: Stage 1=候補1
  `tension_reflection`(前回最重度失敗の直接回帰チェック、固有名詞あり)。
  Stage 2(2〜3 segment)で数字を含むsegmentを追加する場合は、Family X
  baseline完成後にHormuz/Meta B1B `full_story_part1`(既存OK音声あり、
  数値・固有名詞含む)を候補とする。最終選定はユーザー。
- 環境齟齬(google-genai: requirements-ci 2.14.0 / .venv 2.11.0)は本タスク
  範囲外の発見として記録。`speech_metadata`型定義の有無に関わるため、
  Trial実行前に整合させるかはユーザー判断(Fable推奨: requirements-ci側に
  合わせて.venvを更新し、全体regressionで無影響を確認してからTrial)。
- 実Trialは開始しない(ユーザー判断待ち)。
