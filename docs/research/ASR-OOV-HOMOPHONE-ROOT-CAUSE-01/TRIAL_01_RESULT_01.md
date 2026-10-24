# TRIAL_01_RESULT_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01 §3 先行検証、2026-10-24)

Trial専用コード(Productionから未import・未配線): `trial_oov_ledger_m1_01.py`(E1)、`trial_direct_ledger_phoneme_01.py`(E2)、`trial_b_g2p_01.py`(B)、`prompt_arm_01.py`(A)、`azure_window_arm_01.py`(C)、`cost_cf_01.py`。コンソール出力=`work/console_*.txt`、結果JSON=本ディレクトリ。実費=約8円(BUDGET_LOG_01.md)。使用モデル: OpenAI ASR `gpt-4o-mini-transcribe`(Production Primary、最新世代の推奨系)、Azure Speech STT(Production Secondary)、ローカル faster-whisper small(第3の独立エンジン、診断用)、OpenAI `tts-1`(masking対照音声の生成のみ。旧世代だが「別系統の実発話」を作る用途で、比較対象の品質評価ではない)。

## 表A. 候補A(Primary ASRへ語彙ヒント prompt)  ※API実測
| 条件 | gacha発話窓8本(実TTS音声) で gacha と転写 | masking対照(音声が実際は別語)で gacha と誤転写 |
|---|---|---|
| prompt無し | 0/8 | 0/8(gaycha→geisha、gotta→gada、got you→gotyou 等。誤りは誤りのまま) |
| prompt='gacha' | **2/8(25%)** | **1件: 音声が gaycha(誤発音様)→ `gacha`**。`got you`→`gotcha`(別語を勝手に寄せる) |
| prompt='The transcript may contain the word gacha.' | 1/8(12.5%) | gaycha→geisha(寄らず)、got you→gotcha |
評価: 救済率が低く(12〜25%)、誤PASS方向のmaskingが実在(過去er065の再現)。**不採用**(独立証拠にならない)。

## 表B. 候補B(CMU未登録語のG2P推定、g2p_en 2.1.0)  ※オフライン
| 項目 | 結果 |
|---|---|
| gacha の G2P | `G AE CH AH`(/æ/)。gotcha(`G AA CH AH`)と**不一致**→厳密一致方式では救済0。本件の実音声(F2解析で /ɑ/)・Ledger(米 /ɑː/)とも不一致 |
| 保存Primary非PASS行(1語置換型・正準語がCMU外・ASR語がCMU内)の厳密一致 | 検査81件中 **0件**受理。1音素だけ違う「緩和すれば受理されるが別語の危険がある」件=12件(緩和は誤PASSを生む) |
| G2P精度の目安(神経網predict、CMU収録語600語、学習データを含むため楽観値) | 完全一致 447/600=74.5%。OOV語ではより低い |
評価: 効果0・誤PASS誘因あり・過去不採用(C3/UDR #52)。**除外**(再導入しない)。

## 表C. 候補C(Secondaryを発話窓だけに絞る)  ※Azure API実測+オフライン試算
| 項目 | 結果 |
|---|---|
| Azure窓(平均6.4秒)の転写 | PhraseListなし: gotcha 6/8・gacha 2/8。PhraseList=[gacha]: **8/8 gacha**(窓でも全文でもPhraseListが決定要因) |
| masking対照(PhraseList=[gacha]を付与) | gaycha→**gacha**(誤PASS方向)、gotcha→gacha、catcher/gadget/gutter は寄らない |
| 費用 | 窓6.4秒=約0.28円/呼出 vs 全文47〜50秒=約2.1〜2.2円(-87%)。本run試算: gacha関連Azure 23.43円→約3円(-約20円)。ただしTTS再試行は減らない |
評価: 費用は大きく下がるが、**PhraseListバイアスで「gachaに寄せた」転写は独立証拠にならない**(音は gotcha 側)。窓切出しに追加のASR(局所Whisperで位置特定)が要り、過去Trialの「短clipは文脈欠如で精度低下」(er065)も残る。新フロー(Opus条件A)。単独では非推奨、E2の補完候補(Ledger読みが無い語のみ)として保留。

## 表E2. 候補E2(Ledgerの出典付き読みに対する直接音素一致)  ※オフライン、Production判定関数+既存M1凍結候補を無変更で再利用
受理条件: 1語:1語のreplaceのみ/正準語がCMU外でLedger C2候補(sources非空・disabled無・IPA変換可・segment開始前凍結)を持つ/ASR語がCMU収録でその代表発音(ストレス除く)がC2候補と完全一致/置換後に既存`classify_asr_match`が should_pass。
| 検査 | 結果 |
|---|---|
| 本run Adv part3 の8テイク(Primary転写) | **attempt 1・2・5・8が受理**(gacha→gotcha が唯一の差)。attempt 3・4・6・7は gacha以外にも差(`you've→you`、`oh`欠落等)があり**非受理(正しくNGのまま)** |
| 合成15件=正例1+負例14(gacha→gutter/gadget/gotta/catcher/gatcha[CMU外]/gaycha[CMU外]、gacha脱落、got you、重複、他の内容語差、数値差、否定追加、語脱落、you've→you) | **受理は正例1件のみ。負例14件の誤受理0** |
| 保存Primary非PASS(正準語にLedger読み付きOOVを含む)ユニーク110ペア(Ledger全件を開始前扱い=最大緩和) | 受理3件(gacha×2[topic_intro attempt1・part3 attempt1]、**meink←mink** [Troy Meink、space_weapons、ASR_VALIDATION_UNCERTAIN→STOPPED]=いずれもLedgerの読みと一致する正例)。誤受理と思われるもの0。Meinkのみ confidence=low の読み(→設計パラメータ「confidence≥medium」で除外可能、Opus論点) |
| PASS→NG変化 | 0(受理を足すだけの設計。既存PASSは通る) |
| 既存M1(承認済み)の受理(参考) | Melosの `mello/mellow→melo`型11件は現行ゲートのまま維持(E2は干渉しない) |

## 表E1. 候補E1(M1入口を緩め、Ledger読み付きOOVを entity_like 扱い)  ※オフライン
本run part3 8テイク: 入口は通るが、attempt1は `F1_RESIDUAL_CONTENT`(’ 不具合、ROOT_CAUSE §6)、2・5・8は `MULTI_CANDIDATE_NO_MATCH`(M1の期待綴りCMU要件で構造的に比較不能)、3・4・6・7は他の差で対象外。**受理0**。→ M1の仕組みのままでは gacha 型は救えない(E2が必要)。

## 表F. 候補F(語単位のクロスエンジン確認=Primary差分語をSecondaryが正準どおり、Secondary差分語をPrimaryが正準どおり転写)  ※オフライン(`census_03_union.py`)
| 項目 | 結果 |
|---|---|
| 保存の両転写あり144行中、Primary非PASS68行 | 現行 NG_BOTH 31行のうち、全正準語がどちらかのエンジンで一致=10行(32%) |
| 内訳の質 | 10行中、`turn→turned`(Primary)+`raised→raise`(Secondary)、`says→said`、`pass→path`、`messages stop→message is stopped` 等、**時制・語彙の食い違いを含む**。本run part3 att1 の gacha/you've/word's は正当だが、他は「互いに違う誤り」を許す危険が高い |
評価: 一般則としては誤PASSリスクが高く(**不採用**)、救えるのは gacha 型の一部のみ。E2のほうが狭く安全。

## 表D. 候補D(個別override `{gacha,gotcha}`)  ※GACHA_HOMOPHONE_01.mdの再掲
データ1件追加でgachaのみ降格(NG→UNCERTAIN)。他語に効かず、ユーザー不採用(UDR #183)。比較基準のみ。

## 本run履歴へのカウンターファクチュアル(`cost_cf_01.py`、API 0、推計)
| 項目 | 実績(gacha含むsegmentのみ) | E2適用 |
|---|---|---|
| Adv part3 TTS回数 | 8 | **1**(attempt1で受理) |
| Azure呼出(gacha関連) | 全NG attemptに発火 | part3 attempt1はPrimary段で受理→0(他segmentは現行どおり) |
| 費用(TTS+Primary ASR+Azure) | 38.58円 | **16.02円(-22.55円)** |
| Local Rewrite・HR Lock・Style Gate・人間承認 | 発生 | 発生せず(PASS_WITH_WARNING+事後試聴リスト) |
| 案件合計(104.73円) | — | 約82円(-22%) |
注: topic_intro等の初回出現segmentは、Ledger読みが未作成のため従来どおりSecondary経由(E2は2回目以降の出現と、既にLedger登録済みの語に効く)。事前にLedgerへ読みを入れる供給側(G)は未検証・Phase 2で費用実測。

## 判定の整理(誤NG削減/誤PASS/Azure/TTS/コスト)
| 候補 | 誤NG削減 | 誤PASS | Azure呼出 | TTS再生成 | 費用 | 判定 |
|---|---|---|---|---|---|---|
| A prompt | 25%程度 | **増(masking実例)** | 不変 | 一部減 | 0 | 非推奨 |
| B G2P | 0 | 増の恐れ(緩和時) | 不変 | 不変 | 0 | 除外(過去不採用+効果0) |
| C 窓Secondary | 不変 | PhraseListバイアス | **-87%/呼出** | 不変 | -約20円/本件 | 単独非推奨・補完候補 |
| D 個別登録 | 1語のみ | 不変 | 不変 | 不変 | 0 | 非スケーラブル |
| E1 入口緩和 | 0 | — | — | — | — | 単独では無効 |
| F 語単位クロス確認 | 一部 | **高** | 不変 | 一部減 | 0 | 不採用 |
| **E2 Ledger直接音素一致** | gacha型を解消(Ledger読みのある語) | **負例14件で誤受理0、保存110ペアで正例3** | **減(Primary段で受理)** | **減(1回で通過)** | **-約22円/本件** | **推奨(Phase 2でTrial実装・Regression)** |
