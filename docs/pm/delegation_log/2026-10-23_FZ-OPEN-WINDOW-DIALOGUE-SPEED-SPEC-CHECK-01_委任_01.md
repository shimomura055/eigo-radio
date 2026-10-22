FABLE-DELEGATION-MARKER: FZ-OPEN-WINDOW-DIALOGUE-SPEED-SPEC-CHECK-01-委任_01-20261023

# 委任_01: Family Z『開いた窓』会話音声の低速化指示が正式Productionから撤去されているかの確認(read-only・API費用0・変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FZ-OPEN-WINDOW-DIALOGUE-SPEED-SPEC-CHECK-01_委任_01.md`(N≈317〜327、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FZ-OPEN-WINDOW-DIALOGUE-SPEED-SPEC-CHECK-01_USER.md` に逐語保存。
3. `docs/pm/ACTIVE_TASK.md`: 別agent2本(ASR-HOMOPHONE 委任_04、FX-KP-JA-GLOSS-VOICE-MISMATCH-FIX-01)が並行中。編集直前に再読込し、「並行タスク」として本管理IDの1行を追加するだけ。

## 1. ユーザー指示原文(逐語)
```
## Claude Codeへの指示:Family Z『開いた窓』会話音声の速度仕様確認

### 1. 背景・目的

ユーザー試聴により、『開いた窓』Standard/Advancedの会話部分がゆっくり聞こえるとの指摘がありました。

以前、会話部分をゆっくり読み上げる指示が存在していましたが、ユーザーはその指示を削除する方針です。

**現在の正式Productionで、この低速化指示が確実に撤去されているか確認してください。**

### 2. 調査事項

1. 過去の「会話をゆっくり話す」仕様・Promptと、その撤去に関する決定・変更履歴を確認。
2. Family Zの正式Production経路で使用するTTS Prompt・Style Profile・速度パラメータ・後処理に、会話を遅くする指示や設定が残っていないか確認。
3. 初回生成だけでなく、retry/fallback/regeneration/resumeでも旧指示が使われないか確認。
4. 『開いた窓』の実際の音声生成ログから、使用したPrompt・Voice・model_id・速度設定を確認。
5. 会話が遅く聞こえる原因が、明示的な速度指定なのか、TTSモデル・Voice・演技指示等によるものなのか、証拠に基づいて切り分ける。

特に、**コード上から旧指示が消えていても、実際の生成時に旧Promptが使用されていないか**確認してください。

### 3. 作業範囲

- 今回はread-only調査のみ。コード・Prompt・音声を変更しない。
- 新しいTrialや音声再生成は行わない。
- API費用を発生させない。
- Family Z『開いた窓』を対象とし、既存の承認済み共通速度仕様との整合も確認する。
- 過去に削除が承認されていたにもかかわらず残存している場合は、仕様不整合として報告する。今回の調査段階では修正しない。

### 4. 報告事項

以下を簡潔に報告してください。

1. **旧低速化指示は削除済みか、残存しているか。**
2. 削除済みなら、その証拠(正式経路・実際の使用Prompt)。
3. 残存しているなら、場所・理由・影響範囲。
4. 『開いた窓』の会話が遅く聞こえる原因の推定。
5. 対応が必要な場合の最小限の是正案とQCD影響。

Fableによる事実確認も実施してください。

ユーザーが求めているのは、まず**既存の低速化指示が本当に撤去されているかの確認**です。新たな速度改善Trialや品質基準の追加には進まないでください。
```

## 2. 既知情報(Fable)
- 対象run: `er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`(a2/b1b、2026-10-23生成、runner `er026_family_z_fiction_production_runner_01.py`、TTS `er063_family_z_audio_01.py`、構造 `er062_family_z_structure_01.py`、`--tts-execution-mode STANDARD`)。dialogue Voice: Zephyr/Kore/Algieba/Schedar、Narrator Aoede、Adv補助Charon。試聴ページ `user_test/family_z_open_window_01/`。
- 比較対象: melos `run_jre_01`(受入済み)。X側の共通TTS backend `er033_tts_flash_lite_backend_wiring_01.py`、style_profile(`fx_20261017`等)、speech_metadata。
- 調査の出発点(Grep語の例): `slow`, `slowly`, `ゆっくり`, `pace`, `speaking_rate`, `rate`, `speed`, `tempo`, `calm`, `deliberate`, `unhurried`, `dialogue_style`, `style_profile`, `speech_metadata`, `DIALOGUE_` を、er062/er063/er026/er033/er003 TTS関連・`er003_v1_translator_briefs/`・`docs/`・CURRENT_SPEC(「速度」「話速」「ゆっくり」「会話」節)・DECISION_LOG/DECISION_LOG_HISTORY・OPEN_ITEMS/OPEN_ITEMS_HISTORY・UDRでGrep。全文読込は禁止(該当節のみ)。

## 3. 調査手順(read-only)
1. **履歴**: 旧「会話をゆっくり」指示の仕様・Prompt(原文・所在・導入日)と、撤去を決めた決定(ユーザー原文・DECISION_LOG・commit hash・差分)。撤去が「決定済みだが未実施」「一部経路のみ実施」でないかを区別。
2. **現行Production経路の静的確認**: Z TTS経路でGeminiへ渡す全テキスト(system/style指示、speech_metadata、話者ごとの演技指示、Narrator/dialogue別の指示、後処理[時間伸縮・無音挿入・gap])を関数単位で列挙し、速度に影響する語句・パラメータの有無を引用付きで示す。共通速度仕様(承認済み)との整合も確認。
3. **retry/fallback/regen/resume経路**: 各経路が同じPrompt builderを通るか、別のテンプレート/キャッシュ/保存済みPromptを使うか(例: run dir内に保存されたprompt/plan JSONをresumeで再読込する経路)を確認。
4. **実際の生成ログ**: run_e2e_01のaudit(plan、tts_generation_results、speech_metadata、raw_usage_log、prompt dump/sha)から、dialogue clipで実際に使われたPrompt本文(またはsha→本文の対応)・voice・model_id・速度関連設定を抽出し、静的確認の結果と一致するか照合。**旧Promptの痕跡(旧語句・旧sha)が実使用にないか**を明示。
5. **原因切り分け(証拠ベース)**: 明示的速度指定がない場合、代替仮説を既存データだけで検証: (a)dialogue clipの発話速度(文字数/秒 または 語数/秒)をNarrator clipおよびmelos run_jre_01のdialogue clipと比較、(b)Voice別(Zephyr/Kore/Algieba/Schedar vs melosのAlgieba/Erinome/Charon)の速度差、(c)演技指示(感情・間)の有無、(d)clip前後の無音・gap設定(組立時のpause)。推測と事実を分け、数値は出典付き。
6. **是正案(実施しない)**: 残存していれば最小限の撤去案と影響範囲(再生成要否・費用)。残存していなければ、原因推定に応じた選択肢(例: 現状維持/演技指示の調整=仕様変更/Voice差)をQCD影響付きで列挙(新Trial・新基準は提案段階に留め、起票しない)。

## 4. 禁止
- コード・Prompt・音声・SSOT仕様の変更、API呼出、再生成、新Trial、調査範囲の他作品への拡大(melosは比較参照のみ)。

## 5. 報告(docs/pm/RESULT_PACKET_FZSPD.md、同内容を最終報告で; OPEN_ITEMSに1 item起票[Status=INVESTIGATED_PENDING_USER]、REPORT_LEDGER 1行、commit/push・secret_scan hits=0)
(1)結論: 旧低速化指示は削除済み/残存(確度) (2)削除の証拠(決定・commit・現行経路の引用・実使用Promptの照合) (3)残存していれば場所・理由・影響範囲 (4)遅く聞こえる原因の推定(数値比較表) (5)最小限の是正案とQCD影響 (6)commit・raw URL + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。