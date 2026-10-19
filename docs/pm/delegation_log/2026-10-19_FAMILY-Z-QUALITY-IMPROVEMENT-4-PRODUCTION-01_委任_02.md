# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_02(改善項目②Standard Preview/Comment=Advanced方式の日本語適用、③Standard Dialogue=Advanced同一Style+後処理6%減速、④本文語数400±70 の現行経路調査・差分設計・テスト設計・再生成計画・費用見積。**Phase 1=read-only調査+文書、JPY0、Production変更なし**。実装はOpus条件Aレビュー後)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 調査・設計文書。コード変更0、有料API呼出0。
- 到達上限Status: `ITEMS234_DESIGN_READY_PENDING_OPUS_A`。
- 禁止: Production・Prompt・Styleの変更/有料実行/②で「Advanced方式の日本語適用」以外の独自方式の提案採用/③でWPM数値基準・追加品質Gateの新設/④でハードキャップ化・語数理由の自動再生成/`er082_*`への接触。
- 固定ブロック: **E-1**(CURRENT_SPEC「Family Z」節・共通仕様Status表・Preview/Comment仕様行(2026-10-17ユーザー決定A: Preview・Comment1現行方式維持・A/B新方式不採用=**本件②で上書き更新される点を差分として明記**)・Dialogue Style/Voice仕様・6%減速仕様・Z本文語数仕様(350±70)・OPEN-338/#48/#51(Preview関連close済み)をGrepし分類)/**D-1**(本Phaseは不適用)/**G-1**(変更ファイルのみ明示add、禁止操作同前、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agent(委任_01=①調査、ユーザー原文保存・OPEN-419起票・REGISTER登録を担当)あり: SSOTは自分の変更行のみstaged blob、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASK.mdは編集直前に再読し自分のブロックのみ先頭追記。ユーザー原文ファイル・OPEN-419・REGISTERは委任_01が作成するため本委任では作成しない(参照のみ。未作成なら「委任_01待ち」と記録))/**F-1**(JPY0。見積はrun_e2e_03実測単価(`cost_log.jsonl`、`audit/cost_by_stage_17.json`)を出典に)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_02.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI2.md`)。

## ユーザー指示(2026-10-19、本委任に関係する②③④の逐語抜粋。全文は委任_01が`…_USER.md`へ保存)
---
#### ② Standard Preview／Comment生成方式の変更

**Advancedで採用しているPreview／Comment生成方式を、日本語版としてStandardに適用する。**

目的は、事前に物語の展開を説明することではなく、リスナーが何に注目して聴けばよいかを示し、続きへの興味を引き出すこと。

対応内容：

- Advancedの正式Production Prompt・生成経路を確認する。
- その構成・役割・情報開示方針をStandardの日本語生成へ適用する。
- 本文中の出来事・障害・結末を不必要に先取りしない。
- Standardとして理解に必要な平易さは維持するが、旧方式の詳細なあらすじ説明を無条件に残さない。
- PreviewとComment1〜3の重複や情報の先取りを確認する。
- 新仕様をFamily Zの正式生成経路、retry／regenerationへ反映する。

既存Advanced方式の日本語適用がユーザー承認範囲であり、別の独自方式への変更は含まれない。

#### ③ Standard Dialogue音声速度の改善

**Standardの登場人物のセリフは、Advancedと同じDialogue Styleで生成し、生成後に6％減速する。**

現行Standardの「生成時の減速指示＋生成後6％減速」は廃止する。

対応内容：

- `A2_ENGLISH_STYLE_PREFIX_SLOWER` 等、Dialogueに追加されている生成時減速指示を取り除く。
- Advancedと同一のDialogue Styleを使用する。既存の登場人物別Voice割当は維持する。
- Standardの生成後6％減速、既存ASR／音声QA／retry／fallbackは維持する。
- narratorのPD06や、Standard本文ナレーションの6％減速仕様は変更しない。
- 問題が顕著だった王のセリフを含め、変更後の速度・自然さと6％減速の実施を検証する。

対象例：

`Your friend must stay here. Return late, and he will die in your place.`

セリフの速度改善のために、ユーザー未承認の数値WPM基準や追加品質Gateを新設しない。

#### ④ Family Z本文語数の変更

**Family Zの本文語数目標を350語から400語へ変更する。**

- Standard／Advanced共通
- **目標400語、目安範囲330〜470語（400±70）**
- 従来の「センター値±70語」をそのまま踏襲
- ハードキャップではない
- 範囲外はWARNのみ
- 語数だけを理由とした自動再生成・STOPは行わない
- 不自然な加筆・削除による語数合わせは禁止

Writer Prompt、定数、Guardrail、文書、必要なテストを整合させる。

今回のメロスは既存本文がStandard約408語／Advanced約387語で新しい目安範囲内にあるため、**語数変更のみを理由とした本文再生成は不要**。

### 3. 実施順序と効率化
①②④の仕様調査・修正・テストは、依存関係と競合を考慮して可能な限り並列化する。③の音声修正は、必要な本文・話者割当が確定していれば先行可能。既存の承認済み成果物・音声は再利用し、変更が必要なPreview／Comment、該当Key Phrase日本語意味、Standard Dialogueのみを必要に応じて再生成する。ただし、最終Assemblyは変更後の正式仕様と原稿の整合が取れた状態で行う。

### 4. Production反映とGate(抜粋)
正式初回Production経路に反映済み/retry・fallback・regeneration・resumeへの反映/DEV・Trial専用でない/正式runtimeで発火した証拠/必須Validator・Regression・integration test PASS/実際のPrompt・Style・Voice・model_id・routingの記録/X/Z共通仕様との整合/SSOT更新/Git/承認された仕様と実動作が一致。各項目は個別にStatus管理し、条件を満たしたものだけをPRODUCTION_WIREDとする。
---

## Fable指示(調査・設計の要件)
### ②(Preview/Comment)
1. Advanced正式経路: `er062_family_z_writer_01.py` `run_support_adv`(L893-927付近)の`PREVIEW_ROLE`・Comment生成Prompt(`er003_v1_b1_scaffold_01_generate.py` L207-212のネタバレ禁止含む)の構成・役割・情報開示方針を抽出(Prompt全文の所在:行)。
2. Standard現行経路: `run_support_std`(L844-890)とrunner側Prompt(`er026_family_z_fiction_production_runner_01.py` L468-477)の構成。Adv方式との差分表(入力=本文全文+Comment1 vs +Comment1・2/役割/開示方針/平易さ指示/文長/順序)。
3. 設計: 「Adv方式の日本語版」としてStd Prompt・入力構成・生成順序をどう置き換えるか(逐語的な翻訳ではなく構成・役割・開示方針の移植)。Std固有に残す要素(平易さ・日本語)を明示。Comment1〜3との重複・先取りの確認方法(機械的: 本文の出来事キーワード/結末語の出現check案は**新Gateではなく記録・WARN**に留める)。retry/regeneration/resume(`stage_support`のreuse/provenance)への反映点。2026-10-17ユーザー決定A(Preview・Comment1現行維持)を本指示が上書きする旨のSSOT差分文案。
4. メロス再生成計画: Std Preview+Comment1〜3の再生成(LLM費用見積、出典run_e2e_02/03)→S3 TTS再生成(4 clip)→AUW→Assembly。Adv側は再利用。
### ③(Dialogue)
1. 現行: `er063_family_z_audio_01.py`のDialogue Style決定(Grep `A2_ENGLISH_STYLE_PREFIX_SLOWER|DIALOGUE|kind == "dialogue"|dialogue_style`)、Std/Advで何が違うか(生成時減速指示の有無・Style sha・Voice割当・model)、後処理6%減速(`verify_std_english_slowdown`/適用関数)の対象にDialogue clipが含まれるか。
2. 設計: StdのDialogue StyleをAdvと同一にする最小変更(定数差替え/分岐削除)、Voice割当不変、`style_record.json`・`CROSS_FAMILY_COMMON_STYLE_MAP`・drift testへの影響、`FAMILY_Z_ROLE_STYLE_VERSION`/reuse_keyの扱い(Std Dialogue clipのみ再生成されるようにする方法)、retry/fallback経路でも新Styleになること。
3. 検証計画: 王のセリフ(`Your friend must stay here. Return late, and he will die in your place.`)を含むStd Dialogue全clip(10)の再生成→ASR/AUW→6%減速比(1.046〜1.060)の実測→Advの同セリフとの長さ比較(WPM基準は新設しない。参考値として記録のみ)。費用見積(Gemini TTS+ASR、run_e2e_03実測単価)。
### ④(語数)
1. 現行: Z本文語数の定数・Prompt文言・Guardrail(WARN/STOP/再生成条件)・testの所在(Grep `350|WORD_TARGET|word_count|語数` in er062/er026/er063/tests/CURRENT_SPEC)。
2. 設計: 400±70への定数・Prompt・Guardrail(WARNのみ)・文書・testの変更点一覧。ハードキャップ・自動再生成・STOPが現行に存在する場合は、ユーザー指示(WARNのみ)に合わせる変更の要否を明示。メロス本文は再生成不要(Std 408/Adv 387が範囲内)=Phase 3で本文reuseを確認する手順。
### 共通
- 各項目のE-1分類、retry/fallback/regeneration/resumeの反映点、test設計(新規/更新)、Opusレビュー観点案(条件A、②③で各3件以内)、実装順序案(並列可能性、ファイル競合)、Phase 3再生成の総費用見積(①を除く。①は委任_01)。
- 文書: `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/ITEMS234_DESIGN_01.md`(§2/§3/§4各項目に現行・差分・設計・test・再生成計画・費用、§5実装順序、§6 Opus観点、§7 E-1分類とSSOT差分文案)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py` L830-930+語数定数部(Grep結果)
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L440-500(Std Preview Prompt)・`stage_support`(L1112-1145)・`stage_writer`/語数Guardrail
- `C:\Users\tensh\eigo-radio\er003_v1_b1_scaffold_01_generate.py` L190-230
- `C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py` Dialogue Style/減速関連関数(Grep結果の該当関数全体)
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\{segment_style_table_17.json,cost_by_stage_17.json,style_record.json}`と`a2/support/`配下(現行Std Preview/Comment原稿)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\FZ_COMPLETION_PLAN_01.md` §2仕様差分表・§13

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `Preview|Comment 1|E2_UPBEAT|Dialogue|A2_ENGLISH_STYLE_PREFIX_SLOWER|350|語数`(Family Z節)→行番号を§7へ(編集はPhase 2以降)。
- `OPEN_ITEMS.md`: Grep `OPEN-338|OPEN-419`(参照のみ)。
- `DECISION_LOG.md`: 末尾に「2026-10-19 FZQI 委任_02: ②③④ Phase 1調査完了(要旨)」1行。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_02.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_02.md_check.json`
- 語数実測(read-only): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -c "import re,sys;[print(p, len(re.findall(r\"[A-Za-z'’-]+\", open(p,encoding='utf-8').read()))) for p in sys.argv[1:]]" C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\a2\writer\<本文file> C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\b1b\writer\<本文file>`(実在fileに置換。既存の語数計測関数があればそれを使い同じ定義で測る)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- DECISION_LOG: 「2026-10-19 FZQI 委任_02: ②③④の現行経路・差分設計・再生成計画(JPY0)。実装はOpus条件A後」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_02+_check.json、ITEMS234_DESIGN_01.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_02: ②Std Preview/Comment=Adv方式日本語適用・③Std Dialogue=Adv同一Style+後処理6%減速・④本文400±70 の現行経路調査・差分設計・test設計・再生成計画・費用見積(Phase 1、JPY0、Opus条件A前)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI2.md`)
4行: (1)整合(E-1分類、上書きされる既存決定の明示)(2)Production到達経路=変更なし(3)成果物とcommit sha、②③④それぞれの差分要約・変更ファイル候補・test案・再生成対象と費用見積(合計)、実装順序案(4)撤去/残置候補(例: `A2_ENGLISH_STYLE_PREFIX_SLOWER`のDialogue適用分岐、旧Std Preview Prompt、350定数)。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/コード不変)。
