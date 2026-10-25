FAMILY-Y-VOICES-DESIGN-01 委任_27(『宅配の再配達は有料にすべきか?』音声化Trial: 英訳Std/Adv→Voice割当→TTS→品質検査→限定試聴ページ→Closeout)。あなたはsonnet-worker。Fable(PM)からの委任。ユーザー指示原文は§9に逐語(保存必須)。

## 0. 位置づけ・境界
- 現状Status=VALIDATED(日本語R0限定、FABLE_EVAL_03)。今回到達可能=VALIDATED(音声化Trial)。**Production正式採用・配線は行わない**(Y正式Production入口は存在しない=OPEN-484。Trial経路のまま、`production_reachable=False`を記録)。
- 日本語R0(Research・視点・人物・本文)はやり直さない。音声化に必要でTrialに存在しない要素(リード、Tension+Closing、Preview/Comment/Key Phrase/In One Line等の既決設計分)のみ補完。承認済み3 Voiceの立場・人物像・主張を変更しない。
- 予算: 案件見積が300円を超える場合は有料前にSTOP(7-7)。日次1,000円(JST): **有料開始前にraw usage log等から本日(JST)の累計を集計し、本件見積を足して1,000円を超える見込みならSTOPして報告**(本日は他案件で約440〜750円の支出・進行があるため厳守)。使い切り不要。
- 有料runは`.venv\Scripts\python.exe`、無料処理は`py`。並行agent: FX-CORE-NUMERIC(er115、Writer系API)、FZ-NARRATION-CHUNK(Z TTS)、FZ-SOURCE-ESSENCE(Z Production run_sf_prod_02、Z TTS)。**TTSは直列化flagを尊重**し、他のTTS稼働中は待機(他processを終了しない)。Production run dir・store・公開ページへ書き込まない。

## 1. Phase 0(API 0): 既存仕様照合・設計・見積(有料前にcommit)
読むもの(必要箇所のみ、SSOT全文読込禁止):
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/{EVAL_SET_04,FABLE_EVAL_03,PERSONAS_05,VOICES_02.json,PROVENANCE_04,SOURCE_LOG_02,THEME_DEFINITION_02,BUDGET_LOG_OB_05}.md|json`(R0確定本文の所在=EVAL_SET_04/VOICES_02.jsonで確認)
- Family Y既決設計: `er110_family_y_persona_pipeline_01.py`(+`_run.py`, test)、`er110_family_y_persona_audio_trial_01.py`、`er110_family_y_audio_trial_01.py`(`y_entry_point.json`/`production_reachable`)、`er110_family_y_persona_audio_page_03.py`(試聴ページ)、過去のY音声Trial結果(`er110_output/`配下の該当run、RESULT_PACKET_FYT*)。
- SSOT: `OPEN_ITEMS.md`はOPEN-463/OPEN-484行のみ、`USER_DECISION_REGISTER_01.md`のFamily Y項(#170/#172/#175/#176と、Voice方式・5パート構成・Preview/Comment/KP/In One Line適用の決定)、`CURRENT_SPEC.md`はFamily Y節とA2(Standard)仕様・Dialogue/ナレーターVoice・速度/Style・音声検査(TTS/ASR Gate、KP音声検査、発音Ledger、Connected Speech、速度・ポーズ、局所Rewrite、retry/fallback、安全上限)の該当節をGrep。`DECISION_LOG.md`はFamily Yの決定(Voice方式=Family Z正式Voice候補表+既定割当、5パート固定構成、ナレーター方式)をGrep。
成果物 `docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/{EXISTING_SPEC_CHECK_01,DESIGN_01,BUDGET_PLAN_01,RIGHTS_CHECK_01}.md`:
- EXISTING_SPEC_CHECK_01: 既決設計の正本(Voice割当方式、5パート、ナレーター方式、Preview/Comment/KP/In One Lineの適用、A2簡易化仕様、英訳方式=Family X承認方式、音声検査一覧)を節番号・ファイル:行で列挙。**既存Y音声Trial経路で今回の5パート(リード/V1/V2/V3/Tension+Closing)がそのまま処理できるか**、できない差分(例: リード・Tension+Closingの生成、話者ラベル、パート順検査)を列挙。
- DESIGN_01: 処理フロー(英訳Adv=忠実英訳、Std=A2仕様簡易化; 3人の人物像・主観性・一人称・葛藤・立場保持; 新事実追加禁止 → Voice割当: Family Z正式Voice候補表+既定割当、性別はVoice Cardの明示情報、V1/V3は男性で聞き分け可能な別Voice、リード/Tension+Closingはナレーター方式 → TTS: 既存の正式速度・Style・設定を継承 → 検査: TTS/ASR承認済み検査、KP音声検査、発音Ledger、Connected Speech、速度・ポーズ、不自然さ、retry/fallback/局所Rewrite(発動時は一人称・立場・口調保持を確認)、安全上限・STOP → 組立 → ページ)。パート順・話者対応の機械検査(日本語/Std/Advの5パート対応)。Production隔離(sink付替え・sha比較・`production_reachable=False`)。
- **Go判定基準(Fable事前設定)**: 次のすべてを満たす場合のみPhase 1(有料)へ自律的に進んでよい。(i)有料工程がすべて既存のY persona音声Trial経路+Family X承認済み英訳/検査関数の再利用で、新しい処理フロー(新Validator・新組立方式・新Voice選定方式・Style変更)を伴わない(リード/Tension+Closing・ラベル等のデータ追加と薄いglueのみ) (ii)案件見積≤300円かつ日次1,000円内 (iii)RIGHTS_CHECK_01で下記の権利条件を満たす。**1つでも満たさない場合は有料前に停止し、Phase 0成果物(必要ならOpus条件Aレビュー依頼書`OPUS_REVIEW_REQUEST_01.md`を含む)を報告して終了**。
- RIGHTS_CHECK_01: V1根拠にR2+(個人ブログ・note、再利用許諾なし)が含まれる(FABLE_EVAL_03 (c))。確認事項=日本語R0本文および英訳が出典の表現を逐語転載していないこと(出典文との連続一致を機械チェック: 例えば日本語20文字以上/英語8語以上の連続一致0件)、出典URL・引用文を試聴ページに載せないこと。満たす場合=**限定共有**(既存`user_test/`配下のunlisted path、`<meta name="robots" content="noindex,nofollow">`、index/一覧からリンクしない、ページ冒頭に「Trial・限定試聴・権利確認前のため転載不可」注記)で公開可。満たさない場合=ローカル成果物(mp3+HTML、絶対path)の提示に留める。
- BUDGET_PLAN_01: 工程別見積(英訳Std/Adv、リード/Closing等の補完生成、KP/gloss、TTS clip数×単価、ASR検査、retry予備)と、本日JST累計の実測・残額。
- commit(有料前固定)。

## 2. Phase 1(有料、Go判定を満たす場合のみ)
- 英訳(Adv忠実/Std A2)→補完要素生成→KP等→Voice割当→TTS(直列化flag尊重)→検査→組立→ページ。独立作業は並列化(Std/Advの英訳は並列可、TTSは直列化規則内)。再生成は既存retry/fallback/局所Rewrite枠内のみ。磨き込みTrial禁止(既存基準を満たした時点で完成)。
- 有料run起動回数・同一run再起動間隔150秒以上・RESTART_STORM規則を守る。実費はraw usage logで確定。
- 試聴ページ(既存標準形式=`er110_family_y_persona_audio_page_03.py`系を再利用): Std/Adv切替、各レベル通し再生、パート別再生、本文・Preview・Comment・In One Line全スクリプト、Key Phrase(英語・意味/解説)、3人の人物ラベル、限定共有注記。公開mp3は`user_test/`配下のみ。公開後HTTP 200確認(デプロイ待ちは再試行)。
- Fable受入用に、英訳Std/Adv本文全文(5パート、話者ラベル付き)と日本語R0本文の対応表を`COMPARISON_01.md`に無編集で置く。

## 3. 記録・Closeout
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/{TRIAL_RESULT_01,QA_RESULT_01,COMPARISON_01,BUDGET_LOG_01,ISOLATION_EVIDENCE_01}.md`。TRIAL_RESULT_01にユーザー§9の7項目(完成状態と試聴方法/人物像・主観性の保持/Voice聞き分けと音声品質/検査結果と残存問題/実費・所要時間・量産単価示唆/Status候補/Production化時の未完了事項=OPEN-484受入条件との対応)。
- SSOT: OPEN-463(またはY音声Trialの該当Open)にStatus・要点追記、OPEN-484に「Production化時の未完了事項」追記、DECISION_LOG 1件。新規UDRは登録しない(Fableが付ける)。編集直前に再Read・scratchpadバックアップ・最小Edit・`git diff --stat`(並行agentとの衝突時は再適用、OPEN_ITEMS.mdはCRLF/LF混在注意)。
- `docs/pm/RESULT_PACKET_FYT27.md`、`docs/pm/ACTIVE_TASK.md`自行(gitignore)。
- 原文・委任文の逐語保存: ユーザー原文=§9の内容を`docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_<既存の次番号>.md`へ(既存の`*_FAMILY-Y-VOICES-DESIGN-01_USER_*.md`をGlobして次番号)。委任文=`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 527 --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_27.md`(冒頭「FAMILY-Y-VOICES-DESIGN-01 委任_27」で照合、不一致なら±5)。`check_delegation_prompt.py`はFAIL想定(非blocking)。
- Git: `git status`→対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡。amend/rebase/force push/stash/reset --hard/checkout -f禁止。commitは最低2回(Phase 0・結果)。
- 注意: `OPINION_BASED_01/`配下に未commitの変更6ファイル(BLIND_SET_05等)がgit statusにある。**本委任では触らず、commitにも含めない**。原因が分かれば報告のみ。

## 4. STOP条件(整理して報告、自動続行なし)
Go判定不成立 / 案件300円超・日次1,000円超の見込み / 既存承認仕様で解決できない重大品質問題 / 新仕様・品質基準・重要モデル変更が必要 / 権利・安全上の問題 / 明示STOP・安全上限到達 / Production採用・配線が必要になる場合。

## 5. 報告(Fableへ)
(1)Go判定の結果と根拠(i)(ii)(iii) (2)ユーザー§9の1〜7(Status候補まで、APPROVED_FOR_PRODUCTIONは書かない) (3)試聴URL(限定共有)またはローカルpath (4)有料run起動回数・実費・日次累計 (5)変更ファイル・commit hash・raw.githubusercontent.com URL (6)RESULT_PACKET 4行(既存仕様整合/Production到達経路に入る未承認機能/失敗終了時の成果物/撤去・残置)+「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」1行。

## 9. ユーザー指示原文(逐語)
# Claude Codeへの指示｜Family Y「宅配の再配達は有料にすべきか？」音声化Trial

## 1. 目的・Scope

Family Y「宅配の再配達は有料にすべきか？」を、既存の日本語R0確定Trial成果から、Standard／Advanced両方の完成音声まで制作する。

**今回の到達目標は、両レベルの完成音声・品質検査・ユーザー試聴まで。正式Production採用・配線は行わない。**

- Status：現状 VALIDATED（日本語R0限定）
- 今回到達可能なStatus：VALIDATED（音声化Trial）
- Production正式採用：ユーザーの別途明示承認が必要

Family X/Zの承認済み仕様を最大限流用し、必要十分な品質を守りつつ、最短・低コストで完成させる。

## 2. 入力原稿・再利用

以下を既存成果として使用する。

- `OPINION_BASED_02/EVAL_SET_04.md`
- `OPINION_BASED_02/FABLE_EVAL_03.md`
- 関連するVoice Card、出典対応表、Trial成果
- Family Y設計書、CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS

再配達テーマの日本語R0はFable評価でVALIDATED（限定）に到達済み。

**日本語R0のResearch・視点設計・人物設計・本文生成は原則やり直さない。**

音声化に必要なリード、Tension＋Closingなど、既存Trialに存在しない要素のみ補完する。必要な編集があっても、承認済み3 Voiceの立場・人物像・主張を勝手に変更しない。

既存の検証結果・費用・成果物を再利用し、不要な再生成を禁止する。

## 3. 英訳・記事構造

Standard／Advancedを制作する。

英訳は既存Family Xの承認済み方式を基本として継承する。

- Advanced：日本語R0の忠実英訳
- Standard：既存A2仕様に基づく英語簡易化
- 3人の人物像、主観性、一人称、葛藤、立場の違いを保持する
- Standardだからといって人物の個性や意見を不必要に削らない
- 英訳時に新しい事実・主張・経験を追加しない

本文は承認済みの5パート固定構成とする。

1. リード
2. Voice 1：現役ドライバー
3. Voice 2：共働きの受取人
4. Voice 3：受取方法を工夫している受取人
5. Tension＋Closing

Preview、Comment、Key Phrase、In One LineなどはFamily Yの既決設計とX共通仕様を適用する。

日本語・Standard・Advancedの本文5パートが正しい順序・話者で対応していることを確認する。

## 4. Voice・TTS

**以前決定したFamily Yの人物別Voice方式を使用する。新しいVoice選定Trialは行わない。**

- Family Zの正式Voice候補表と既定の割当方式を流用
- 3人に人物像と整合した別々のVoiceを割り当てる
- リード・Tension＋Closingは既存のナレーター方式
- 人物の性別は既存Voice Cardの明示情報に従う
- 既存の正式な速度・Style・TTS設定を継承

最新の承認記録を確認し、未承認のVoice選定方式やStyle変更を追加しない。

特にVoice 1とVoice 3は男性であるため、聞き分けられることを確認する。

品質確認では、自然な会話調、一人称の維持、感情表現の自然さを重視する。過剰な演技やニュースナレーター化は避ける。

## 5. 音声品質・受入条件

既存Family X/Zの正式な音声品質対策を、今回のTrial経路に適用する。

- TTS／ASRの承認済み検査
- Key Phraseの音声品質検査
- 発音・読み間違い対策
- Connected Speech、速度、ポーズ、音声の不自然さの検査
- retry／fallback／局所Rewrite
- 既存の安全上限・STOP条件

新しい5パート構造でも、必要な検査が漏れないようにする。

局所Rewriteが発動した場合は、意味だけでなく人物の一人称・立場・口調が保持されていることを確認する。

**既存仕様で品質基準を満たした時点で完成とし、追加の磨き込みTrialは行わない。**

不具合が起きた場合は、承認済み範囲・予算内で原因究明から修正・再検証まで自律対応する。同一手段の無益な反復を避ける。

## 6. 試聴・公開範囲

Standard／Advancedを切り替えて確認できる、既存標準形式の試聴ページを用意する。

必要なもの：

- 各レベルの通し再生
- パート別再生
- 本文・Preview・Comment・In One Lineの全スクリプト
- Key Phrase（英語・意味／解説）
- 3人の人物ラベル

今回はTrialであり、一般公開・Production公開の承認ではない。

**出典・権利上の注意：** 既存Fable評価ではVoice 1の根拠資料に再利用許諾未取得の個人ブログ・noteが含まれると報告されている。原稿・音声・公開ページの権利上の扱いを確認し、権利確認前に一般公開しないこと。ユーザー試聴のための限定的な共有方法を優先する。安全に試聴URLを公開できない場合は、ローカルで確認できる成果物等を提示する。

## 7. 費用・進め方

開発費は既存の日次1,000円（JST）の管理方針に従う。

- 既存成果を最大限再利用
- API呼び出しを必要最小限にする
- 独立作業は並列化
- 不要な日付分割、待機、工程停止をしない
- 着手前に残予算と作業費用の見積もりを確認
- 費用増の見込みが生じた場合は代替手段を優先
- 承認済み予算・Scopeを超える場合はSTOP

Fableは委任管理、品質・QCD照合、Trial Closeoutの独立評価を担当する。

## 8. STOP条件

以下の場合のみ、必要事項を整理してユーザー判断を求める。

- 既存の承認済み仕様では解決できない重大な品質問題
- 新たな仕様・品質基準・重要なモデル変更が必要
- 権利・安全上の問題
- 予算上限または明示STOP条件への到達
- 正式Production採用・配線が必要になる場合

技術的な不具合や既存仕様内の修正については、都度ユーザー判断を要求しない。

## 9. 最終報告・受入

最終報告では以下を示す。

1. Standard／Advancedの完成状態と試聴方法
2. 英訳で3人の人物像・主観性が保持されたか
3. Voiceの聞き分けと音声品質
4. TTS／ASR等の品質検査結果と残存問題
5. 実費・所要時間・量産単価への示唆
6. Fableの独立受入評価とTrial Closeout Status
7. 今後Production化する場合の未完了事項

必要なTrial成果・判断待ちをOPEN_ITEMS等に記録し、Gitへ反映する。

既存のProduction経路に無断配線しない。正式採用の判断はユーザー試聴後に行う。

**最終目標：ユーザーが両レベルの完成音声を試聴し、Family Yの英訳・音声品質を評価できる状態にすること。**