FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_08-PHASE-B-PERSONA-VOICE-TRIAL-20261023

# 委任_08: Phase B — Opus条件Aレビュー反映→新規DEV実装(`er110_family_y_persona_*`)→B-0 control→R0テキスト(日本語→Std/Adv英語)→評価→必要なら再設計1回→最終稿のみ音声化→試聴ページ→Fable評価資料。X/Z Production・R1/R2無変更。費用上限=Family Y Trial残枠 **74.62円**(独断拡大禁止)。

## 前提読込
`docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_01/{DESIGN_PROPOSAL_03,PERSONA_CANDIDATES_01,SPEC_MAPPING_01,ROOT_CAUSE_01}.md`、`docs/pm/RESULT_PACKET_FYT4.md`、ユーザー原文 USER_03・USER_02、前Trial `TRIAL_01/AUDIO_QA_01.md`。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_08.md`(index 356以降、先頭MARKER一致)。
2. **Opusレビュー保存**: 下記所見を `REDESIGN_01/OPUS_REVIEW_02.md`(Fable転記と明記)。
3. ACTIVE_TASK自分の行のみ(並行: FX-KP-GM Trial agent=`er112_*`不可触)。TTS前に他行「有料run(TTS)進行中」確認・待機、自分の開始/終了を記す。**日次予算確認**: 当日(JST)採用済み開発費を集計し、本Phase見積(55〜70円)を足して1,000円超過見込みなら有料部分を開始せず報告(本日は他案件で約800円消費見込み)。

## Fable判定(記録用)
Opus総合判定=「必須修正を済ませればPhase B可、再設計不要」。骨格(工程反転・Persona Sheet・Voice別call・4パート+見出し+Comment 1/2・R0のみ・旧B 13項目維持・評価Gate化なし)は実質一致。対立点5(Leakageは判定器を変えない案を先に検証/人物差は英語で残る特徴で設計・英語で評価/Tension生成はGate後/V2の後付け是正と事実0件/尺・費用見積と音声は最終稿のみ)はいずれも品質・費用の技術修正→**Fable判断でPhase Bへ進む**。5パート→4パートの変更はTrialではDEV経路で実施し、採用時にユーザー判断事項として明示(OF-Y3-15)。Leakage判定入力の調整(ア')が必要になった場合も「Y Trial限定」とし採用時に開示。

## Opus所見(逐語要約。必須=01〜09、推奨=10〜16、情報=17〜18)
- OF-Y3-01[必須] 人物差が英語音声に届かない(一人称・語尾は英訳で消える、Std簡易化で文長が揃う)。(a)Sheetの「話し方」は英訳後も残る特徴(文長の型、問い返し頻度、断言/留保、短い断片、職業語彙、we)で書く (b)Y専用の英訳・簡易化wrapperに「段落ごとの話者の文長コントラスト・ためらい・直截さを保つ」1文追加(X関数は無変更) (c)E1/E2/E6はStd英語(主)とAdv英語で測る。
- OF-Y3-02[必須] 「禁止」の対象を具体化: 共通前提=「朝に一律回収し下校時に返す(登校中は終日預かる)ルールにするか」をComment 1とSheet両方に固定。V1主張=「学校が一律に決めてくれれば『学校もそう言ってる』と言える。俺ひとりが悪者にならずに済む」(学校ルールを家の後ろ盾に)。V3主張=「授業中は鞄の奥に入れると約束する。でも一日回収は仕事の連絡が切れる」。回収ボックス対シフト連絡の具体物対立。
- OF-Y3-03[必須] 冒頭2文以内に身元の手がかりを自然に入れる(自己紹介文は禁止のまま)。例 "My daughter's in her second year of high school." / "Every morning, kids come into the nurse's office…" / "I sort boxes at a warehouse all day, then go to night school." E2「冒頭2文のみ」版追加。
- OF-Y3-04[必須] Tension+ClosingはGate通過後(局所書き換え後)のVoice本文から生成: Voice×3→Voice Gate→Tension生成→Tension Gate。Voice書き換え時はTension再生成・再判定。
- OF-Y3-05[必須] 見出し音声: `er012_b_family_voices_a2_production_01.py:740-743` は常にA2減速を適用→Stdはそのまま、Advは減速なし経路を明示(独立予算・disfluency QA・アンカー語にordinal=F11教訓)。見出しの事前ASR確認はStd/Adv各2回程度。`Voice One:`へ切替える場合はユーザー例と異なる形式として開示。
- OF-Y3-06[必須] Leakage: 判定器を変える前に「変えなくてよいか」を確認。(a)B-0冒頭で許容リストなしの現行判定(日本語移植版)にpositive control(本人主語の伝聞1文)を入れる。PASSならア'不要、直すのはWriter Prompt(伝聞形例示)と書き換え規則`:568`のみ(区分問題消滅、M7回帰省略可)。(b)ア'が必要な場合: 「論証に使わない」は「主張は事実なしでも成立し、事実は補助の一言。データとしての比較・因果の断言をしない」に言い換え/アンカリング対策control(許容事実を正しい形+別文に研究主語の漏出→FAIL必須、各control 3回以上)/区分「Y Trial限定の判定入力の調整」、採用時に開示。(c)事実タグ規則(`er110:373-385`)はVoice段落で「伝聞文の文末にタグ」と例示し「〜という」型を誘導しない。
- OF-Y3-07[必須] 架空人物の「観察」による世界一般化禁止(USER_02:46): 人物が書けるのは個別の出来事(「ある子が」「この前」)のみ、頻度・因果の一般化は台帳になければ書かない。Sheet自己点検とWriter規則に1行ずつ。V2主張は本人の推測形に。
- OF-Y3-08[必須] 撤去漏れ: R-P12 一人称「私」固定(`er110:367`,`:568`)、R-P13 書き換え規則の「冒頭1文で誰か分かる」(`:568`)、R-P14 事実タグ文言、R-P15 全体800〜1000字(`:371`)を新規ファイルに持ち込まない。
- OF-Y3-09[必須] 3人の締めの同型化防止: Sheetに締めの型を人物別指定(V1=自嘲的な断言、V2=問い返し、V3=約束+要求)。E6に「締めの型3種」追加。骨格順序はSheetで1か所入替可(V2は場面→感情→主張)。
- OF-Y3-10[推奨] 尺・費用見積修正: Voice 190→310字は+63%、本文全体+28%、英語Adv 1 Voice約160〜170語・65〜70秒。まず260〜300字で始め、収まらない場合のみ広げる。TTS/ASR費用・尺を再計算。
- OF-Y3-11[推奨] 順序: B-0→テキスト1回目→評価→(必要なら)テキスト2回目→最終稿でだけ音声1回。節約: Y版B3再実行せずComment 1用背景fact 2〜3件を台帳から手で選ぶ(6〜8円減)、OF-06(a)成立ならM7回帰省略(約3円減)。見込み55〜70円。Arm G見送り。止めどころ: E1 3/3(英語)、E8 0、E14 PASS、OF-14の対比較でbaselineより明確に良い、E10で具体物3つ→数値追い込みせず音声化・試聴へ。
- OF-Y3-12[推奨] V2再設計: 主張をResearch形から本人の価値観起点へ(例「保健室まで没収の場にしたくない。禁止で『対策した』と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなる」)。OECD-02は外し事実0件(混在する証拠はComment 1でナレーターが中立提示)。事実使用の検証はV1のJP-03 1件で十分。
- OF-Y3-13[推奨] Tension+Closingの締めの問いは聞き手が自分の生活から答えられる具体的な問いに限定(例「あなたの家では、夜、スマホはどこに置いてある?」)、抽象名詞主語の問い禁止、共通前提は3人の具体物に結びつける。In One Lineに結論・教訓がないか観測(Gate化なし)。
- OF-Y3-14[推奨] 評価: E2は冒頭2文版+英語版。E13は盲検でないため主評価はblind対比較(前回R0gと新稿を順序ランダム・ラベルなしで「どちらが実在の人が語っているか」「どちらが丁寧に説明している感が強いか」、Opusへは設計意図・Sheetを渡さず本文のみ)。LLM判定は補助、最終はユーザー試聴。
- OF-Y3-15[推奨] 4パートはTrialでは案Aで進めてよいが、採用時に「5→4パート変更」をユーザー判断事項として明示。Comment 1/2が連続同声(Std=日本語Aoede)は試聴確認。Comment 2のrole文に取材表現回避(「話を聞いた」「we talked to」禁止)を明記。
- OF-Y3-16[推奨] 見出し語彙にA2確認("The basket where the phones sleep"は負担、"The headaches that start at night"/"The shift I can't lose"は良い)。
- OF-Y3-17[情報] VALIDATED提案時は「手作業Sheet・1テーマでの検証」と範囲明記、量産可能性と区別、推定単価95〜98円>70円を報告。
- OF-Y3-18[情報] Repetition QA誤検知(OPEN-469)で止まりやすい→人間確認待ち、迂回しない。
- Persona評価: V1父=修正して採用(因果を「学校ルールを家の後ろ盾に」へ。Alt-A不要)。V2養護教諭=修正して採用(価値観起点・事実0件・一般化禁止。教師枠として成立する理由を報告)。V3定時制生徒=採用可(小修正: 「守れる約束と守れない約束」「信用は自分で作る」を前面に、前回V3・ユーザー例示と同類型である点を開示)。男性2声のどちらが若く聞こえるかを前回音声で確認し、合わなければ話す順番(=Persona)の入替を検討可。

## 1. 設計更新 `DESIGN_PROPOSAL_04.md`(OF反映差分表、Persona Sheet最終版3枚[英訳後も残る話し方特徴・締めの型・身元手がかり・自己点検]、工程順序、Leakage方針(a)優先、尺260〜300字、費用再見積、撤去R-P01〜15)。

## 2. 実装(新規DEVファイル `er110_family_y_persona_text_trial_01.py` 等。既存 `er110_family_y_text_trial_01.py` は無変更で残置)
- Comment 1(テーマ導入、人物説明なし、共通前提=朝回収・下校返却ルールを具体提示、背景fact 2〜3件は台帳から手選び・中立)/Comment 2(Voice導入、人物紹介繰返しなし、取材表現禁止)/見出し×3(`One Voice:`/`Another Voice:`/`A Third Voice:`、A2語彙確認)/Voice×3(別call、Sheet入力、骨格、締めの型、身元手がかり、一般化禁止、伝聞形例示)/Tension+Closing(Gate後生成、骨格、最長文45字、抽象名詞≤2、二重否定0、具体的な問い)/In One Line(既存)。
- 英訳・Std簡易化はY専用wrapper(X関数無変更、話者コントラスト保持1文追加)。
- 見出し音声経路: Std=既存A2減速関数、Adv=減速なし経路(独立予算・disfluency QA・ordinalアンカー)。
- 隔離test(Production参照0、env/flag/CLI切替なし)、M3/M4 parity(4パート+Comment/見出しsegment ID)。

## 3. 実行
- B-0: Leakage positive/negative control(現行判定、各3回)→(a)成立ならア'不要と記録。不成立なら(b)の条件で最小調整(Y Trial限定・開示)。
- テキスト1回目(R0、日本語→Gate→Tension→Gate→英訳Std/Adv)→評価E1〜E14(英語主体、blind対比較はOpusへ本文のみで依頼する準備=Fableが別途opus-consultantへ依頼するので、`BLIND_PAIRS_01.md` に順序ランダム・ラベルなしの対を用意し、正解キーは別ファイル)。
- 未達なら原因分析→再設計(Sheet/Prompt/骨格)→テキスト2回目(1回まで)。`ITERATION_LOG_01.md`。
- 止めどころ(OF-11)を満たしたら、最終稿のみ音声化(Std/Adv各1回、固定Voice、見出しAoede、Std減速は既存仕様で生成し「Voice part減速なし」版は後処理で併置)→試聴ページ `user_test/family_y_trial_02/index.html`(全編・パート別・全スクリプト・日本語原稿・人物設定要約・Trial表示・前回R0gとの比較リンク)→HTTP 200+Playwright全audio実再生+ページ標準検査。
- 費用は各段で記録、74.62円超過見込みなら開始前に停止報告。

## 4. Fable評価資料 `TRIAL_02_RESULT_01.md`: 最終報告10項目の1〜7・9(Persona 3枚、構成実例[Comment 1/2・見出し・Tension+Closing]、Std/Adv本文、評価結果、Leakage整合の結論、費用・推定単価・時間)。VALIDATED自己宣言なし、範囲(手作業Sheet・1テーマ)明記。

## 5. SSOT・Git: OPEN-463 Status、OPEN-470(Leakage整合の結論)、OPEN-469参照、DECISION_LOG(Fable判断: Opus反映→Phase B)、REPORT_LEDGER。明示add(mp3のみ)、secret_scan hits=0、`git push origin HEAD:main`。全回帰は最後に単独実行し分類。

## 6. 禁止: X/Z Production変更、R1/R2変更・削除、既存er110 text trialの変更、`er112_*`編集、74.62円超過、日次1,000円超過見込みでの有料実行、Gate/HR迂回、VALIDATED自己宣言、音声の複数回生成。

## 7. 報告(docs/pm/RESULT_PACKET_FYT5.md): (1)OF反映表 (2)Persona Sheet 3枚要約 (3)B-0結果とLeakage方針の結論 (4)テキスト1回目(2回目)の評価表と実例 (5)音声QA・試聴URL・再生検証 (6)費用(出典)・残枠・推定単価・時間 (7)blind対比較の準備物 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。