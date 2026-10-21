# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_05(Standard試聴ページ改善: ユーザーがFallback音声[Std Full Story第2部]の採用可否を「前後との話し方の違和感」で判断できるよう、Std全体の通し再生+第2部ハイライト+単独再生+平易な説明のページを作る。**API 0、TTS/ASR新規実行なし、原稿・音声・Production Style・品質判定・M3 Gate・assemble経路は変更しない、採用判断・Production組込みはしない**)。最終Status=`USER_DECISION_REQUIRED`(#132)のまま。並行agent: 記事B 委任_06(固有名詞調査、read-only、SSOT未編集)。本委任もSSOT編集はOPEN-432行末1文+REPORT_LEDGER 1行+ACTIVE_TASKのみ(共有プロトコル)。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_05.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_05」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_STD-PREVIEW-PAGE_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_05(Std試聴ページ改善)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X 記事A「収入と性格」— Standard試聴ページ改善

### 1. 目的

現在のHuman Reviewページは、ASR転写・不一致箇所・Take比較が中心で、ユーザーが何を判断すべきか分かりにくい。

**ユーザーに技術的な処理過程を見せることが目的ではない。**

今回の判断は、Standard Full Story第2部で使用されたFallback音声について、前後の音声と比べて話し方に違和感がないか、採用してよい品質かを試聴で評価することである。

この目的に合わせてページを改善する。

### 2. 試聴ページの必須要件

**① Standard全体の通し再生**

ページの冒頭に、Standard完成候補の全体再生ボタンを設置する。

- 第2部には現在のFallback採用候補を組み込む。
- 第1部・第3部など他の音声は既存の承認済みTakeを使用する。
- 第2部以外を再生成しない。
- 正式採用前の確認用プレビューであり、Production完成版として確定しない。

**② Fallback使用箇所を明確にする**

Full Story第2部が今回の確認対象であることを、音声構成またはスクリプト上でハイライトする。

該当箇所を単独再生する手段も設ける。

**③ ユーザーに確認してほしいことを簡潔に記載**

ページには以下の趣旨を表示する。

「Full Story第2部のみ、通常と異なる音声生成Styleを使用しています。全体を聴いて、第1部・第3部と比べて声の調子・話し方に違和感がないか確認してください。」

技術用語は必要最小限にし、専門知識がなくても目的が分かる説明とする。

**④ 技術情報はユーザー向け画面から外す**

次の情報は通常の試聴画面には表示しない。

- ASR転写全文
- ASR差分のハイライト
- 各TakeのNG理由
- M3 Gate等の内部管理情報
- Fallbackの技術的発動経緯
- Style SHA・モデルID等

これらは既存の監査ログ・技術報告に保存し、必要な場合のみ参照できればよい。

### 3. 既存成果物の再利用・QCD

- 既存音声・スクリプト・公開ページ生成機構を再利用する。
- TTS／ASRの新規API実行は不要。
- 原稿・音声・Production Style・品質判定条件は変更しない。
- 無駄な新規UI開発や別Trialは行わない。
- Fableは全体再生、Fallback箇所の表示、音声の取り違えがないことを確認する。

### 4. 完了報告

次の3点のみ簡潔に報告する。

1. 改善した試聴ページURL
2. Standard通し再生とFallback箇所の単独再生が正常に機能すること
3. ユーザーに確認してほしい内容が明確になっていること

**今回の作業はページ改善のみ。Fallback音声の採用判断、Productionへの正式組込み、共通Fallback仕様の変更は行わない。**

最終Statusは引き続き `USER_DECISION_REQUIRED` とする。
--- 原文ここまで ---

## 設計方針(Fable指定)
- **Production assembleは使わない**(M3 Gate BLOCK中のStdを組み立てる経路の新設・迂回は禁止)。代わりに、Std(a2)の全segment音声(`a2/narration/*.wav`等、status=OKの承認済みTake+第2部=fallback採用候補wav)を**Std組立順**(順序の正本=`a2/parts.json`/plan/assemble順序を定義するコードをGrepで特定し、同じ順序)に並べた**プレビュー専用の連結音声**を、Production外の小script(`er019_pp_std_preview_01.py`、ffmpeg/pydub等既存依存のみ)で生成する。segment間の無音は、Production assembleが使う既定値をコードから読み取って同じ秒数にする(読み取れなければ0.6秒とし、その旨記載)。出力は`user_test/paycheck_personality_e2e_01/std_preview/`配下のmp3(wavはgitignore)。ファイル名に`PREVIEW`を含め、ページ上も「正式採用前の確認用プレビュー(Production完成版ではない)」と明記。Production run dir・state・wavは一切変更しない。
- JS側は、通し再生ボタン(プレビューmp3)+「第2部だけ再生」ボタン(fallback候補のmp3単独)+第1部/第3部の単独ボタン(比較用)。スクリプト全文を掲載し、**第2部の段落を背景色でハイライト**し「ここが確認対象」とラベル。
- 冒頭に平易な説明(ユーザー§2③の文言をそのまま使う)+「確認のポイント: 第1部→第2部→第3部と聴いたとき、声の調子・話す速さ・落ち着きが揃って聞こえるか」。
- 技術情報(ASR転写・差分・NG理由・Gate・Style sha・モデルID・発動経緯)は**載せない**。ページ末尾に小さく「技術詳細(監査用)」として既存HRページ(`hr_full_story_part2/index.html`)への1リンクのみ可。
- 既存HRページは残す(削除しない)。新ページpath=`user_test/paycheck_personality_e2e_01/std_preview/index.html`。
- 音声取り違え防止: プレビューに使った各segmentのsha256と、run dirの採用wav(`tts_generation_results.json`のOK entry/`full_story_part2`のfallback候補)のsha256一致表を`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/std_preview_manifest_01.json`に記録(ページには出さない)。Adv完成音声は本ページには載せない(別物の混入防止。必要ならHRページに既存)。

## 手順
S1. T-0・原文保存。S2. Std組立順・無音秒数の特定(file:行)。S3. 連結script作成・実行(API 0)、manifest記録。S4. ページ生成(既存`er019_pp_hr_page_01.py`の構造を流用した`er019_pp_std_preview_page_01.py`)。S5. commit/push(`git push origin HEAD:main`)→Pages反映(最大10分)→Playwright再生verify(通し再生の開始・seek・終了まで、第2部単独、第1部/第3部単独。evidence `docs/research/.../std_preview_play_evidence_01.json`)。S6. OPEN-432行末に「委任_05: Std通し再生プレビューページ公開(採用保留継続)」、REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。secret scan→明示add→commit→push→到達確認。

## 報告(docs/pm/RESULT_PACKET_FXPP5.md 上書き)
ユーザー§4の3点のみ簡潔に(1.URL 2.通し再生・第2部単独再生の検証結果[再生秒数、ファイル数、sha一致表の要約] 3.ページ冒頭の説明文の引用)+補足としてcommit hash・raw URL・無音秒数の出典・4行判定。