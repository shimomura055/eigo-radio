ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01(Fableから): 『英単語ガチャ』で発生した「gacha→gotcha」型(辞書未登録語・借用語のASR同音誤認→誤NG→TTS再試行・Azure追加呼出・Human Review・費用超過)の**包括的な根本対策**の、原因究明と対策設計(Phase 1)。ユーザー指示: 個別単語の例外登録が目的ではない。正しい発音を誤NGにせず、実際の誤発音は確実に検出する。既存の仕組みを活用し複雑化しない。X/Z/将来のY共通。70円/記事セット整合。Production採用は未承認(Trialの到達上限VALIDATED、既存承認仕様の単なる不具合修正なら自律修正可)。記事完成(別agent、同run)と並行し、**Productionコード(共有Validator等)を本委任で変更しない**(Trial専用コードは`er1xx_*_trial_*.py`または`docs/research`配下)。

## 0. 最初に(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語)を `docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_USER.md` に保存。
- 既存資料: `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/{GACHA_HOMOPHONE_01,RUNTIME_EVIDENCE_01}.md`、run `er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/audit/{tts_generation_results,review_lock_state}.json`(attempt別のASR転写・Azure結果・wav)、er109(`er109_asr_orthographic_equivalence_01.py`、CMU fail-closed)、er008 homophone_en(`_HOMOPHONE_OVERRIDE_GROUPS`)、PNAP/RET/UKUS(X/Z WIRED)、Secondary(Azure)発火条件、Local Rewrite recovery、CURRENT_SPECの該当節(節Grep: 同音/homophone/PNAP/RET/UKUS/Secondary/orthographic)、DECISION_LOGの同音救済・不採用方式(Grep: 同音, homophone, G2P, prompt, 語彙ヒント, vocabulary)。**過去に不採用とした方式は再導入しない**(見つけたら列挙)。

## 1. 原因究明(`ROOT_CAUSE_01.md`、保存済み音声・ASR結果を最大限再利用、オフライン優先)
(a) TTS音声は正しく発音されていたか: Azure転写(gacha)、一次ASRの他語一致、attempt別の差、音声の音素的根拠(可能なら保存wavをオフラインで解析: 発話区間の長さ・スペクトル比較は任意)。AIは耳確認できないので証拠の種類を明記。
(b) OpenAI Primary ASR(gpt-4o-mini-transcribe)が繰り返しgotchaにした理由: 言語モデルの高頻度語バイアス(gacha /ˈɡɑːtʃə/ ≈ gotcha)。**ASR APIの`prompt`(語彙ヒント)引数が現行Production呼出で使われているか**をコードで確認(使われていなければ、それが最有力の既存仕組み内の対策候補)。
(c) 既存機構が効かなかった理由を層別に: er109(CMU未登録→fail-closed)、er008 override表(空)、PNAP/RET(固有名詞でないため実体表に載らない)、UKUS(対象外)、Secondary(Azureは正しく転写したのに、なぜ3回のTTS再試行の後まで救済にならなかったか=発火条件・順序・費用の構造。Secondaryが「確認」ではなく「再試行後」になる設計理由をDECISION_LOGで確認)、Local Rewrite(無関係語の書換えで通過=本来不要だった)。
(d) 一般性: 保存ASR記録(約4,877件)から、CMU未登録語を含むsegmentを機械抽出し、それらのNG率・Secondary発火率・再試行率を通常segmentと比較(gacha以外に同型が起きているかの実データ)。借用語・造語・サービス名・新語の例を列挙。
(e) 費用構造: 同音誤認1件が招く追加費用(TTS再試行×3、Azure呼出の秒課金、Local Rewrite)を本runの実績で定量化。

## 2. 対策候補の比較(`DESIGN_01.md`。実装は最小のTrial専用コードのみ、Productionは触らない)
候補を少なくとも次の4系統で比較(効果・誤PASSリスク・複雑さ・費用・X/Z/Y共通性・既存仕様との整合・過去不採用との関係):
- A: **ASR語彙ヒント**(Primary ASR呼出の`prompt`に、本文のCMU未登録語/固有名詞/KPを渡す。ASR側で正しい綴りに寄せる=誤NGの源を絶つ。誤PASSリスク: ヒント語へ過剰に寄せる可能性→実際の誤発音検出への影響を評価する必要)。
- B: **辞書未登録語の発音推定(G2P)フォールバック**でer109の同音判定を拡張(CMUにない語はG2Pで音素列を推定し、既存の同音判定ロジックに渡す。fail-closedをfail-phoneticに。誤PASSリスク: G2P誤差)。
- C: **Secondaryの発火位置の見直し**(Primary NGが「本文と1語のみ差・その語がCMU未登録」の型なら、TTS再試行の前にSecondaryで確認する。TTS再試行・Local Rewriteの削減)。
- D: 個別override表への登録(現行設計の口。非スケーラブル、比較の基準として)。
- 組合せ案(例: A+C、B+C)。推奨案と理由、QCD影響(誤NG削減見込み・Azure呼出削減・誤PASS変化・単価)。
- 「過去に不採用」「承認済み仕様と矛盾」に該当する候補は明示して除外。

## 3. オフライン/低費用の先行検証(上限15円、保存wav再利用)
- B: 保存ASR記録でG2Pフォールバック(例: `g2p_en`等、依存追加はTrial専用環境で。入手不能なら簡易規則でも可、限界を記録)を**オフライン再判定**: PASS→NG 0、NG→UNCERTAIN/PASSの件数、誤発音の既知異常例(過去のTRUE_CONTENT_MISMATCHで本当に誤発音だったもの=review_queue/human_reviewの記録から抽出)がPASSにならないこと。
- A: 保存wav(gachaの各attempt、他のCMU未登録語を含むsegment数件、既知の誤発音例数件)に対し、Primary ASRを`prompt`ヒント付きで再実行(API、1件≈0.1〜0.5円、合計≤15円)。ヒントあり/なしの転写差、誤発音例がヒントで誤って正しく転写されないか(=誤PASS検査)。
- C: 本runの履歴から「Cを適用していたら」のTTS再試行・Azure呼出・費用のカウンターファクチュアルを算出(0円)。
- 結果を `TRIAL_01_RESULT.md` に(数値表)。

## 4. 停止点(重要)
- 本委任はPhase 1(原因・設計・先行検証)まで。**Production/共有Validatorの変更、新経路の配線はしない。** Phase 1完了でhandback→FableがOpus独立レビュー(条件A: 新しい処理フロー)にかける→Phase 2(Trial実装・Regression・VALIDATED判定・ユーザー判断)は次委任。
- 既存承認仕様の「単なる不具合」と判明した部分(例: 明らかな設定漏れ)があれば、11-8に従い分類し、Productionへ触れる場合はFableへ先に報告(本委任では触らない)。

## 5. 記録・Git
- `docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/{ROOT_CAUSE_01,DESIGN_01,TRIAL_01_RESULT_01,BUDGET_LOG_01,OPUS_REVIEW_REQUEST_01(Fable用下書き)}.md`。OPEN_ITEMSにOPEN-498を本管理IDへ紐付け(分類=修正へ進む・包括対策へ)。DECISION_LOGは本委任では触らない。
- Git: `git status`→`git commit --only`→`git push origin HEAD:main`(他agent差分を巻き込まない=一時index、禁止操作なし、secret grep 0件、wav不追跡)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_DELEGATION_01.md`(Nは先頭「ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01」を含むAgent呼出の0始まり通番、直近470以降)。
- 日次: 10-24把握分約610円+本委任≤15円。

## 6. handback: 根本原因(層別)、既存仕様が機能しなかった理由、候補比較表と推奨、先行検証の数値、過去不採用との照合結果、費用、Phase 2の提案(実装範囲・Regression計画・費用見積)、Opusレビュー論点、commit hash、raw URL。RESULT_PACKET 4行。

【ユーザー原文】
# Claude Codeへの指示
## Family X『英単語ガチャ』完成・ASR同音誤認の根本対策

### 1. ユーザー承認事項

Family X『英単語ガチャ』Advanced最終パートの現行音声を承認する。

- `full_story_part3` の人間承認を正式記録する。
- 追加TTS生成は不要。
- 承認済みのStandard／Advancedを正式組立する。
- 両レベルを切り替えて試聴できる最終ページを公開する。
- 音声・スクリプト・Key Phraseを含め、既存の最終公開品質検査を完了する。

**Standard／Advanced双方の最終版試聴URLを提出すること。**

今回の承認は現行音声の受入であり、新しいASR救済仕様のProduction採用を意味しない。

### 2. `gacha` ASR問題の原因究明

今回、`gacha` が繰り返し `gotcha` と転写され、TTS再試行、Azure追加検査、Human Review、費用超過が発生した。

単なる個別単語の登録ではなく、同種の問題を包括的に解決する。

以下を調査する。

- 実際のTTS音声は正しく発音されていたのか。
- OpenAI Primary ASRはなぜ繰り返し `gotcha` と認識したのか。
- 既存の同音判定・異表記救済・発音辞書・Azure Secondaryがなぜ十分に機能しなかったのか。
- 過去に承認・実装した包括的な同音救済仕様との関係。
- `gacha` 以外の外来語・辞書未登録語でも同じ問題が発生するのか。
- 同音誤認が不必要なTTS再生成やAzure呼出につながる原因。

CURRENT_SPEC、DECISION_LOG、過去Trial、既存Productionコードを照合すること。

### 3. 対策立案

目標は、**正しい発音を誤ってNGにせず、実際の誤発音は確実に検出すること**。

対策は特定の単語だけでなく、辞書未登録語・借用語などにも通用する方式を優先する。

既存の仕組みを可能な限り活用し、判定機構を不必要に複雑化しない。

以下を重視する。

1. 誤NGによる不要なTTS再生成の削減。
2. Azure Secondaryの不要な呼出削減。
3. 誤PASSを増やさないこと。
4. Family X／Z／将来のYへの共通適用。
5. 量産単価70円／記事セットとの整合。

過去に不採用とした方式や、承認済み仕様と矛盾する方式を無断で再導入しない。

### 4. 検証Trial・自律解決

原因調査から対策立案、Trial、評価、必要な修正・再検証まで、Fable管理下で自律的に進める。

- まず保存済み音声・ASR結果を最大限再利用する。
- 独立した調査・検証は並列化する。
- 可能な限りオフラインで検証し、API費用を抑える。
- 正しい発音の救済率と、実際の誤発音の検出維持を両方評価する。
- 過去の正常例・異常例を使ってRegressionを行う。
- 必要な場合は、異なる原因を代表するケースで追加Trialを行う。
- 効果が乏しい方式は反復せず、原因・前提・アプローチを見直す。

既存の承認済み開発予算内で自律的に費用配分すること。品質を犠牲にした原価削減は認めない。

### 5. Production適用の境界

今回承認されたのは記事最終音声であり、ASR対策の新仕様ではない。

したがって、

- 原因調査・Trial・Trial専用コード変更は承認範囲内で進める。
- 新しい同音判定方式や救済仕様をProductionへ無断採用しない。
- Trial成功時はVALIDATEDとして報告する。
- Production採用が必要な場合は、QCD影響と既存仕様との差分を明示してユーザー判断を求める。

既存の承認済み仕様の単なる不具合修正であれば、既存の委任・承認範囲に従って自律的に修正・検証してよい。

### 6. 報告事項

**A. 記事完成報告**

- Standard／Advancedの最終試聴URL
- 両レベルの正式組立・公開検査結果
- Human Review承認記録
- 最終実費
- Production完成状況と残Open Item

**B. ASR根本対策Trial報告**

- 根本原因
- 既存仕様が機能しなかった理由
- 検討した対策と比較結果
- Trialの実測結果
- 誤NG・誤PASS・Azure呼出・TTS再生成・コストへの影響
- Family X／Z／Yへの適用範囲
- Fable独立評価
- Trial Closeout Status
- Production採用に必要なユーザー判断

必要なSSOT・OPEN_ITEMS・Git記録を更新すること。

### 7. 実行上の重要事項

**記事完成とASR改善Trialは並行して進める。**

記事の公開をASR改善Trialの終了まで待たせない。

また、今回は単に `gacha` と `gotcha` を例外登録することが目的ではない。

**類似する外来語・辞書未登録語で同じ不具合を繰り返さず、品質を維持しながら量産費用を下げられる仕組みを目指すこと。**

品質・予算・承認境界を遵守しながら、自律的に原因究明と検証を完了させること。