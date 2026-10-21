# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 委任_01(Family Z登場人物用の共通Voice候補 男性的5+女性的5=10種の同一条件比較音声を生成し、試聴ページを作成・公開する。到達上限=試聴候補の準備完了(USER_DECISION_REQUIRED)。採用・配線はユーザーのVoice選定後に別委任)。並行agentなし。`er026_output/`配下の開いた窓run(`the_open_window/run_e2e_01`等)・メロス完成版・Production Voice設定は**変更しない**。

## 性質/到達上限Status/禁止事項
- 性質: 比較音声の作成(Trial)。到達上限=`USER_DECISION_REQUIRED`(試聴候補準備完了)。**Production経路の話者割当仕様(`STORY_SPEAKER_CONFIG`・`resolve_dialogue_voice`・Z-4)は変更・配線しない**。Voice選定後の割当仕様(ユーザー§4: 男性1〜3/女性1〜3を登場順に独立循環、Narrator=Aoede・Adv補助=Charonは別枠)は「ユーザー決定済み方針(Voice名は未決)」としてSSOTへ記録のみ。
- 費用: 本日2026-10-21(JST)既使用JPY73.47(出典: `daily_dev_cost_01.py --date 2026-10-21`実測、RESULT_PACKET_DWA2)。本委任見積: TTS 10 Voice×2セリフ=20 clip(Family Z Dialogueと同一backend `speech_metadata_flash_lite`、メロスrun_e2e_06の実測clip単価をcost_log/raw_usage_logから算出して見積の出典にする。算出前に数字を断定しない)。承認区分C(ユーザー指示で承認済みScope、案件見積300円以下、日次内)。T-3上限(Guardrail)=見積の約2倍、ただし**¥80**を超える見込みが出たら生成前にSTOPして報告(ユーザー§5「超過前に停止」)。差し替え候補の再生成を含めて上限内。
- 禁止: 本文生成/Research/記事E2E/追加Trial/新しいStyle研究(Styleはfamily Z Dialogueの既存条件を1種類固定)/Aoede・Charonの候補入り/Production音声・Voice設定・`STORY_SPEAKER_CONFIG`の変更/メロス完成版・開いた窓runの変更/`git add -A`/`-u`/`-f`/stash/amend/rebase/force push/branch操作。
- Opus独立技術レビューGate(11-3): 非該当(Production構造変更なし)。
- 最新モデル原則(25節): TTSはFamily Z Production Dialogueと同一backend/model(比較目的なので同一条件が優先。モデル名を報告に明記)。
- 時間見込み: 60〜90分。並列化: 20 clipのTTS呼出は独立なので並列可(rate limitに注意、同時4程度)。ページ生成・検証は生成後に直列。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read基本。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`全文読込禁止。
G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化。
F-1: transcript退避不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「VOICE-SELECTION-TRIAL-01 委任_01」を含む最新index。直前のAgent呼出はDWA 委任_02)。`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行、結果1行(見出し名不一致FAILは既知偽陽性)。
T-1: `TTS_EXECUTION_MODE=STANDARD`(同期)。
T-2: TTSあり(20 clip+差し替え分)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Family Z 共通Voice選定Trial — 男女各5候補・試聴ページ作成

## 1. ユーザー決定・目的

Family Zの登場人物用Voiceを共通仕様として固定するため、男性的なVoice 5種類、女性的なVoice 5種類、合計10種類の候補を用意する。

**AoedeとCharonは候補から除外する。**

理由：
- Aoede：NarratorおよびStandardのPreview／Comment等で使用。
- Charon：AdvancedのPreview／Comment等で使用。

この2種類は、登場人物用Voiceとして選定しない。

最終的にユーザーが試聴して、男性1・2・3、女性1・2・3の合計6種類を決定する。

## 2. 現時点の候補

既存の承認済み候補を優先し、新規候補を補う。

| 男性的Voice候補 | 女性的Voice候補 |
|---|---|
| Algieba（既存） | Erinome（既存） |
| Schedar（既存候補） | Sulafat（既存候補） |
| Fenrir（新規候補） | Kore（新規候補） |
| Orus（新規候補） | Leda（新規候補） |
| Puck（新規候補） | Zephyr（新規候補） |

上記は試聴候補案であり、正式採用済みVoice一覧ではない。

Claude／Fableは、使用するTTSモデルでの利用可能性、声質の印象、既存Voice候補との整合を確認すること。

利用できない候補や、男女の聞こえ方が想定と大きく異なる候補は、同じ目的に適したVoiceへ差し替えてよい。差し替え理由を報告する。

## 3. 試聴ページ作成

10種類を同一条件で比較できるシンプルな試聴ページを作成する。

要件：

- 男性的Voice 5名、女性的Voice 5名を分けて表示。
- 各候補のVoice名を明示する。
- 同じ英語セリフを読み上げさせる。
- 可能であれば、落ち着いた会話文と感情のあるセリフの2種類を用意する。
- それぞれ個別に再生できるようにする。
- 同一TTSモデル・Style・速度条件を使用し、Voice自体の違いを比較できるようにする。
- 聞き取りやすさ、自然さ、声質の違いを判断しやすくする。
- 実際のFamily Zで使用するDialogue音声条件を基本とする。

過剰なUI開発は不要。既存の試聴ページ生成機構を再利用する。

## 4. 今後採用するVoice割当仕様

以下はユーザーが決定したFamily Z共通方針である。

| 登場人物の順番 | 男性 | 女性 |
|---|---|---|
| 1人目 | 男性1 | 女性1 |
| 2人目 | 男性2 | 女性2 |
| 3人目 | 男性3 | 女性3 |
| 4人目 | 男性1 | 女性1 |
| 5人目 | 男性2 | 女性2 |
| 6人目 | 男性3 | 女性3 |

- 男性・女性は独立して順番を管理する。
- 同じ登場人物には作品全体を通して同じVoiceを割り当てる。
- 4人目以降は3種類を循環使用する。
- NarratorのAoedeおよびAdvanced補助音声のCharonは別枠とする。
- 作品ごとに新たなVoiceを選び直す運用を原則不要にする。

**ただし、男性1〜3／女性1〜3に実際にどのVoiceを採用するかは未決定。**

今回のTrialでは正式Production経路の話者割当仕様を変更・配線しない。

## 5. QCD・実行方針

- 既存のTTS生成機構・Voice候補情報を再利用する。
- 10種類の比較に必要な最小限の音声のみ生成する。
- 不要な本文生成、Research、記事E2E、追加Trialを行わない。
- 独立した音声生成は可能な範囲で並列化する。
- 既存の個別承認予算と日次1,000円（JST）を遵守する。
- 予算上限や既存STOP条件に抵触する場合は、超過前に停止する。
- Production音声・Voice設定は変更しない。

本件の到達上限は、**試聴候補の準備完了（USER_DECISION_REQUIRED）**。

ユーザーのVoice選定後に、別途Production採用・配線を判断する。

## 6. Fable評価・報告

Fableは候補と試聴成果物を独立確認する。

評価観点：

1. 男女それぞれ5種類が揃っているか。
2. Aoede／Charonが完全に除外されているか。
3. Voice間に十分な聞き分けやすさがあるか。
4. 同一条件で比較できるか。
5. Family Zの既存Dialogue仕様と整合するか。
6. 試聴ページで全音声を再生できるか。
7. 実費とProductionへの影響が明確か。

最終報告には以下を含める。

- **試聴ページURL**
- 男性5名・女性5名のVoice名
- 既存候補／新規候補の区別
- Fableの推奨する男性3名・女性3名とその理由
- 費用・所要時間
- SSOT／Git反映状況
- ユーザーが決定すべき事項

今回の目的は**Voice選定のための比較音声を作ること**であり、音声スタイルの新規研究や正式Productionへの先行実装ではない。

## 7. 『開いた窓』との関係

『開いた窓』の本文生成など、Voice選定に依存しない工程は継続してよい。

ただし、Mrs. SappletonのVoiceについては、今回の共通Voice選定結果を待つこと。

未承認のSulafat等を、今回の選定前にFamily Zの正式Production音声へ独断で採用しない。

Voice選定後は、新しい共通割当仕様に基づいて『開いた窓』の登場人物へVoiceを割り当て、必要なProduction配線・QAを実施する。

**既存メロス完成版は変更しない。**
--- 原文ここまで ---

## 事前指定Read/Grep一覧
- `er063_family_z_audio_01.py`: `TTS_BACKEND`(L38)、`resolve_dialogue_voice`(L362)、Dialogue clipのTTS呼出箇所(style/prompt/速度/profile/voice指定をGrep: `synthesize|tts_|style|profile|voice_name`)→Family Z DialogueのTTS条件(backend/model/style文言/速度/post-slowdownの有無)を特定し、**そのまま再利用**する(関数import優先、コピー禁止)。Std側の6%減速はDialogue生成後の後処理なので、比較音声は**減速なし(Adv条件=生成そのまま)1条件**で統一し、その旨をページと報告に明記。
- Voice候補の既存情報: `CURRENT_SPEC.md` L261/L297(承認済み候補6種: Algieba/Erinome/Schedar/Sulafat/Aoede/Charon。うちAoede/Charonは今回除外)、`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/voice_samples_review.html`(過去の試聴artifact、生成scriptをGrepで特定し再利用可否を確認)、`er062_family_z_structure_01.py` `STORY_SPEAKER_CONFIG`(L21-110、現行割当の参照のみ)。
- 既存試聴ページ生成機構: `er053_output/tts_voice_tone_brightness_trial_01/build_page_01.py`と`listen_play_verify_01.py`(`user_test/tts_voice_tone_brightness_01/index.html`)、および`er063_family_z_audio_01.build_pages`(L1677)。もっとも単純に流用できるものを選び、理由を1行。
- TTS backendの利用可能Voice一覧: backend実装(`speech_metadata_flash_lite`を提供するmodule)で許可Voice listやvalidationがあればGrep。10候補(Algieba/Schedar/Fenrir/Orus/Puck、Erinome/Sulafat/Kore/Leda/Zephyr)が使用可能か実呼出前に確認(一覧が無ければ1 clip生成で確認)。
- 費用単価: `er026_output/family_z_production_e2e_01/melos/run_e2e_06/`配下のcost_log/raw_usage_logからDialogue clip 1件あたりの実測JPYを算出(出典行を報告)。
- Grep: `OPEN_ITEMS.md`末尾行番号(新規行追記位置)、`docs/pm/USER_DECISION_REGISTER_01.md` L296-299(#129/#130、#129は書き換えず注記追記+#131追加)、`docs/pm/REPORT_LEDGER.md`末尾、`DECISION_LOG.md` L21866(直近書式)。

## 作業手順
S0. `daily_dev_cost_01.py --date 2026-10-21`、`git status --porcelain`(作業前)。T-0・ユーザー原文保存。
S1. 条件固定(生成前にcommit): `docs/research/FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01/TRIAL_DESIGN_01.md`へ、(a)TTS条件(backend/model/style文言/速度=減速なし/profile)、(b)10候補と区分(既存/既存候補/新規)、(c)セリフ2種の英文(Sonnetが作成。①落ち着いた会話文=2文・約25語、②感情のあるセリフ=2文・約25語。固有名・性別を示す語・作品のネタバレを含めない、一般的な会話内容。両セリフは全Voice共通)、(d)clip単価と見積総額(出典)、(e)差し替え規則(利用不可、または男女の聞こえ方がF0で想定と逆の場合に、同backendの他Voiceへ差し替え、理由記録)、(f)聞き分け指標(各clipの平均F0[Hz]・発話時間[s]を算出。librosa/pyworld等が.venvにあれば使い、無ければ既存のpitch推定tool[DECISION_LOG 7826行付近のピッチ推定の経緯をGrepで参照]を再利用。新規install禁止)を記載。
S2. 生成: `er0XX`命名でTrial専用script(`er087_family_z_voice_candidates_trial_01.py`、出力`er087_output/family_z_voice_candidates_trial_01/<voice>/{calm,emotional}.wav`+`cost_log.jsonl`+`manifest.json`)。Production moduleはimportのみ(diff 0)。並列実行(同時4以内)。費用を実測で記録。利用不可Voiceは差し替え。
S3. 計測: 各clipの平均F0・発話時間・ファイルサイズをmanifestに記録。男性群/女性群のF0が想定どおり分かれているか確認。逆転があれば差し替え(S2)。
S4. 試聴ページ: `user_test/family_z_voice_candidates_01/index.html`(+音声ファイル、既存機構流用)。男性5/女性5を分けて表示、Voice名・区分(既存/既存候補/新規)・平均F0・セリフ①②の個別再生ボタン、ページ上部に条件(model/style/速度/減速なし)とセリフ全文。過剰UI不要。
S5. 公開検証: commit/push(`git push origin HEAD:main`)後、GitHub Pages URL `https://shimomura055.github.io/eigo-radio/user_test/family_z_voice_candidates_01/index.html`で全20 clipがHTTP 200かつ再生可能(既存`listen_play_verify`系を流用、evidence JSONを`docs/research/.../pages_play_evidence_01.json`へ)。Pages反映待ちは最大10分、未反映なら時刻と再試行手順を記録。
S6. SSOT: (a)`OPEN_ITEMS.md`末尾に新規行OPEN-430(Status: `VOICE_CANDIDATES_READY_USER_DECISION_REQUIRED`、本委任の要点・URL・費用・候補10名・差し替え有無・割当方針§4は記録のみ未配線)。(b)REGISTER: `### 2026-10-21 FZVS 委任_01追記`節を追加し、#131(UDR-blocking・未回答: Family Z共通Voice 男性1〜3/女性1〜3の選定、試聴URL)を登録。#129行は書き換えず直下に注記1行「2026-10-21ユーザー指示§7により#131の選定結果を待つ(Sulafat等の先行採用禁止)」。(c)DECISION_LOG新規1件(ユーザー決定: 候補10種・Aoede/Charon除外・§4割当方針[Voice名未決]・到達上限UDR・Production未変更・原文path+sha256)。(d)REPORT_LEDGER 1行。(e)ACTIVE_TASK先頭追記(固定ヘッダ。UDR-blocking: #131、#129は#131待ち)。(f)CURRENT_SPEC.mdは変更しない(配線・採用後に別委任)。
S7. secret scan(`tools/secret_scan_01.py --staged` hits=0)→commit→push→`git log origin/main -1 --oneline`。

## Git
- 明示add: delegation_log 2件(+_check.json)、`docs/research/FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01/*`、`er087_family_z_voice_candidates_trial_01.py`、`er087_output/family_z_voice_candidates_trial_01/`(wav含む、合計サイズを報告。10MBを超える場合はwavをmp3/ogg化せず**そのまま**、サイズのみ報告)、`user_test/family_z_voice_candidates_01/`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`。
- Commit: 設計=`FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 委任_01: T-0+ユーザー原文+事前登録設計(生成前)`、成果=`FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 委任_01: 10 Voice×2セリフ比較音声+試聴ページ+OPEN-430/REGISTER #131`。
- Push: `git push origin HEAD:main`(ローカルbranchは`work/post-merge-01`)。

## 報告(docs/pm/RESULT_PACKET_FZVS1.md 上書き。ユーザー§6の順)
1. 試聴ページURL(GitHub Pages)+再生検証結果(20/20)
2. 男性5・女性5のVoice名、既存/既存候補/新規の区分、差し替えがあれば理由
3. 各clipの平均F0・発話時間の表(男女群の分離確認)、Sonnet所見(聞き分けやすさの客観指標のみ。推奨3+3はFableが決めるので、Sonnetは「判断材料」として指標順位を示すに留める)
4. 同一条件の証明(TTS条件、Family Z Dialogue仕様との整合、減速なしの理由)
5. 費用(clip単価の出典、実費、当日累計)・所要時間・Production影響(diff 0の証明)
6. SSOT/Git(commit hash、origin/main到達、secret scan、raw URL一覧)
7. 判断候補(ユーザーが決めるべき事項=#131。Sonnetは「判断候補」表記)
8. T-0 check 1行、ユーザー原文sha256
RESULT_PACKET末尾に4行判定(既存仕様整合/未承認機能のProduction入り/失敗終了時の成果物/撤去・残置)。