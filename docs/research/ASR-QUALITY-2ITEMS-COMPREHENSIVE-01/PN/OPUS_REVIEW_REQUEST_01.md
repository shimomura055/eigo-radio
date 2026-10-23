# OPUS_REVIEW_REQUEST_01: ①固有名詞 包括対策(Run Entity Table)の独立レビュー依頼

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN / 条件A(新しい構造・処理フローの設計)に該当 / 2026-10-23
読むもの(この順): ROOT_CAUSE_01.md(§0・§4・§5)→ DESIGN_01.md(§2・§4・§6)。根拠実装=`er103_proper_noun_alarm_policy_01.py`(特に:167-229 `proper_noun_evidence`、:246-290 `_noun_checks`、:293-440 `evaluate_alarm_eligibility`、:355-366 G3隣接語規則、:697-712 `ledger_surface_tokens`)、`er006_secondary_asr_01.py:823,1280,347-390`、`er019_family_x_validation_inheritance_01.py:349-352`。

## 0. 要約(判断材料)
- 現象: 『開いた窓』の `Bertie`(CMU収録の英語人名、Ledger未登録、歌詞の引用符直後/文頭のみ)が `Birdie` と聞かれ、PNAPが `NO_PROPER_NOUN_EVIDENCE` で不受理→HR Lock。
- 原因: 「固有名詞の認識」の定義が分類器(緩い)とPNAP証拠(厳しい)で分裂し、救済側の証拠が「Ledger(事後・調査成功依存)/CMU未収録/文中の大文字」の代理指標だけ。CMU収録の人名・組織名は出現位置次第で救済されない。固有名詞のみ候補67イベントのうち、証拠欠落(B)+span跨ぎ(C)が現行で19(28%)、Ledger全除外(初見)で25(37%)。
- 案: run単位の“本文実体表”(RET)=決定論スキャン+宣言済み実体(Z Seed)+LLM NER 1回(gpt-6-luna、実測0.026円/本文)。2シグナル規則で証拠化(declared/confirmed)、PNAPの受理境界は不変。Secondary span許容は実体表tokenのみ。LLM失敗時は現行同等へ縮退。Trial=DEV経路、Production未配線(今回承認はVALIDATEDまで)。

## 1. 論点(これに絞って回答を求める)

### Q1 抜け漏れ(最重要)
1. 認識の供給源として他に拾うべき経路があるか(KP英語phrase・Support文・日本語タイトル中の英語名・Preview/TOPIC_INTRO/IN_ONE_LINE roleの固有名詞・歌詞/引用内の名前)。LLM NERを“level text”単位で1回呼ぶ粒度で足りるか(segment単位が必要なケースは?)。
2. **英語の一般語と同形の人名/地名/組織(Bill/Mark/Rose/Will/Iran/Apple/Meta)**: 現行は全tokenが一般語(CMU∧zipf≥4.0)なら受理しない(`R_GENERAL_WORD`、er103:269-270)。実体表で`category=person/place`を持つ場合にこのブロックを緩めるか。設計案は**緩めない**(40%の実体が全token一般語=国名等だが、保存HR queue 88イベントに該当事象は0。緩めると Iran→iron / Mark→Mike 型を受理するリスク)。この判断は妥当か。
3. Zの作品名・登場人物が日本語の“カタカナ読み”経路(`ja_reading_katakana`)と交差する箇所は今回の対象外としたが、見落としはないか。
4. HR Lock済み・NG_BOTH起点の既存音声(『開いた窓』4clip)の救済経路。案は①再生成(2〜5円)を既定、②保存転写再評価のNG_BOTH起点拡張(HR Lock解除=人承認が必要)は別判断。妥当か。

### Q2 誤PASSリスク(最重要)
1. **2シグナル規則**(LLM ∧ 大文字一貫性 ∧ 決定論の大文字出現)で表の精度は十分か。LLMが通常語を“ブランド”と誤タグ付けした場合(実測では偽候補5語は0誤検出だが“題名・Consumer Price Index”は拾う)の影響を既存ガードでどこまで防げるか。
2. **parity主張**: 「表由来証拠の判定 = 同一tokenをLedger登録した場合の判定」であり、受理境界は緩まない、という論理(DESIGN_01 §4・SC-5)。証拠源を広げることが“Ledger人承認フローを迂回する”ことに当たらないか(Ledgerは発音供給/TTS注入の正本で、PNAP証拠としては元々語を区別せず“登録surface全て”を使っている=er103:697-712、`human_approved`・confidence・entity_type不問)。
3. **RET-3(span許容)**: Secondary diff spanの全tokenが実体表token(+`s`)ならentity-onlyとみなす規則。`elle mimon`(L.)や`christie say`(Tse)のように、Secondary側だけが名前+隣接語を一語化する場面で誤って別語を通す穴はないか。`melos drank → mellow strength`は拒否維持。
4. **音素近接ゲートの棄却**: 承認方針の受理済み30差分(距離0.00〜0.50)と合成の別語聞き違い21(0.10〜0.57)が分離不能だったため追加ゲートにしなかった(`phonetic_gate_probe_01.py`)。別の識別手段(複数attempt・複数ASR間の一貫性、Primary/Secondary一致度、カテゴリ別閾値)で、実効的な誤PASS削減が見込めるか。見込みが無ければ“既存ガードが実効境界”の現設計でよいか。
5. `bertie→birdie`は`birdie`のzipf 3.26<4.0のため P-03 を通る(境界が単語頻度の閾値に依存)。この依存は許容か。

### Q3 過去REJECTEDとの整合
- Stage 2判定側方式(取得/推定発音とASR転写の音素照合で発音の正しさを判定)はREJECTED(HR削減0〜2件、主因は現行TTSの実誤読、天井約24%)。本案は発音の正しさを判定せず、承認済みPNAPの“固有名詞であることの証拠”だけを広げ、実誤読もアラーム記録で運営者へ(止めない)。この位置づけはREJECTEDの理由と矛盾しないか。TTS供給(Khaite型B階層)の人承認フローとの責務分担は適切か。
- 承認(2026-10-22)の意図に対し、本案は「承認済み仕様の実装不足の是正」と「新仕様候補(新証拠源LLM NER・span規則)」のどちらに寄るか(Fableが11-8区分を判断するための所見)。

### Q4 費用・性能・構造
- 追加費用(実測0.026円/call、0.05〜0.09円/記事セット)と70円目標の整合。LLMモデル選択(gpt-6-luna vs flash-lite等)、Std/Adv 2 callを1 callに統合する案、再構築トリガー(Local Rewrite)の妥当性。
- 配線点(`run_with_alarm_hook`でscope内・TTS前に構築、run-scoped holder経由でPNAPが参照、継承再判定のためtable shaと使用entryを`pronunciation_alarm`ブロックへ保存)の設計で、並行run/共有state/resumeの競合が起きないか。

### Q5 改善余地
- 「定義の正本を1つに」(`val.capitalized_flags`とPNAP証拠をRETへ一本化)は今回Trial範囲外とした。採用後の第2段階として妥当か、それとも今回含めるべきか。
- Writer宣言型(Prompt変更=ユーザー承認事項)を将来案としたが、LLM NERの代替/補強として優先度は。

### Q6 検証計画(DESIGN_01 §6)
- SC-1〜SC-9の数値(recall≥0.90/カテゴリ別≥0.85/Bertie型100%、精度偽候補0、初見受理B類≥8/9・C類≥12/13、parity100%、費用≤0.1円、安定性Jaccard≥0.90)は“必要十分”か(過剰=磨き込み、不足=見逃し)。保存HR queueが人名・ブランド偏重(地名・作品名・組織名が乏しい)であることを合成データで補う設計で足りるか。leave-one-out設計の妥当性。

## 2. 事前に確認済みの事実(再調査不要)
- 実データ集計(API 0): HR queue 88実イベントの再評価(現行Ledger/Ledger全除外)、実runのアラーム証拠ラベル(cmu_oov 52/ledger 1)、53実体の語彙性(全tokenCMU収録44=83%/全token一般語21=40%)、露出コーパス(Bertie/Meta/Reuters/Vera 等)。
- LLM NER小規模実測(0.5767円): Bertie・Vera・Framton等検出、偽候補0。
- 音素近接ゲート分離能の実測(棄却根拠)。
- Perplexity発音調査が401(PHASE4_RESULT_01.md:43)で事後Ledger経路が機能していない可能性(本件の原因ではなく環境所見)。

## 3. レビュー出力に期待する形式
指摘ごとに OF-PN-RET-xx(Blocker/Major/Minor/Info)、採否に必要な根拠、推奨修正、追加すべきtest観点。Q1・Q2は網羅的に、Q3〜Q6は要点のみ。Opusレビュー後はFableが照合し、11-3のSTOP条件に該当しなければ次工程(Trial実装、別委任)へ進む。
