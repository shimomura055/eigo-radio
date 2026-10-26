## 管理ID

FAMILY-Y-VOICE1-MALE7-TRIAL-01 委任_01(ユーザー再Trial指示。設計固定→既存音声の再利用判定→有料生成(適応的2段階)→計測→試聴ページ→推奨案)。並行Agent: (1)FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(所有=er063/er012_b/er003_n3/er122_*/SSOT/ACTIVE_TASK) (2)CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01(所有=er117/er019/`er121_family_y_{structure,audio,runner}_01.py`のStd chunk配線部分+test) (3)KP-GATE-EXCLUSION-RESCUE-DESIGN-02(KP系)。本委任の所有=`docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/**`、`er121_output/family_y_voice1_male7_trial_01/**`(音声)、`user_test/family_y_voice1_male7_trial_01/**`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE1-MALE7-TRIAL-01_*`、`docs/pm/RESULT_PACKET_YM7.md`。**`er121_*.py`は読取・import専用(並行Agentが編集中。生成関数のimportは開始時に1回行い、以後の変更に影響されないよう使用する関数名・sha・設定JSONを記録)。SSOT・ACTIVE_TASK・Production・公開音声・Voice Registryは編集しない。**

## 性質/到達上限Status/禁止事項

- 性質: 有料Trial(TTS+ASR/QA)。Family Y Voice 1に適した**男性Voice**を7名(Algieba現行/Schedar/Fenrir/Orus/Puck+追加男性2名)から、長ポーズの自然さ・安定性・音声品質で選定し、最終推奨1名の材料を作る(最終推奨の選定はFable独立評価、Production採用はユーザー)。
- 到達上限Status: VALIDATED(限定)/REJECTED/判断候補。**ProductionのVoice割当・公開音声・Voice Registry・他FamilyのVoice構成・TTS Prompt/Style・品質Gateは変更禁止。**
- 禁止: Production code編集禁止(Trial scriptは`docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/tools/`に置き、前回Trialの`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/tools/yvp_*`を流用・派生)/`run_01/`配下へ書込禁止/女性Voiceを比較対象に含めない/意図的な本文・句読点変更禁止/評価基準・追加生成条件・停止条件を結果を見た後に変更しない(DESIGN_01で固定、sha記録、変更が必要なら観測後改訂として履歴付きで開示)/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)/wav・raw_usage_log・STOP・lock・RUN_LOCKはcommitしない(公開mp3は`user_test/`のみ)。
- 有料run規律: `.venv\Scripts\python.exe`、`TTS_EXECUTION_MODE=STANDARD`明示、各起動前に`py tools/stop_scope_check_01.py`(rc=0確認)、起動間隔150秒以上(`Get-Date`記録)、同一run 5分以内3回起動禁止。生成順序の偏り回避=1起動内でVoice×本文×レベルを交互(ラウンドロビン)に並べ、起動ごとに開始Voiceを回転させる。想定外の全再生成・無意味なretry loopはAPI実行前にSTOP。
- 費用上限: 「上限¥250(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」**見積が300円を超える設計になった場合は有料実行前にSTOPして報告**(ユーザー原文「案件見積が事前承認を要する上限を超える場合は、予算判断のみユーザーへ求める」)。
- 修正範囲の線引き(11-8): Trialのため範囲内=計測・比較・推奨材料。範囲外=Voice変更のProduction適用、Style/Prompt変更、新Gate。
- Opus独立技術レビューGate(11-3): 非該当(新構造なし。Voice変更のProduction採用提案時に条件Cを別途判定)。
- 時間見込み: 4〜5時間(設計40分、Phase 1生成90〜120分[起動間隔含む]、Phase 2生成60分、計測・ページ・報告60分)。並列化: 他3案件と並列。生成待ち中に計測・集計・ページscriptを先行作成。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約214(出典: ACTIVE_TASK/RESULT_PACKET_YVP1)/残約786/本委任見積JPY約140〜230(根拠: 前回実績91.12円÷39 take=約2.34円/take[TTS+ASR/QA+retry込み、出典 docs/pm/RESULT_PACKET_YVP1.md]×Phase 1 約60 take≒140円+Phase 2 最大約36 take≒84円。他案件の本日残り有料工程[Z Phase 2 約48〜75円、Chunk Phase 2 約100円]と合算しても日次1,000円以内)/改善見込み高/承認区分: A(Fable判断可: 承認済みScope内・見積300円以下・日次内)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記定型文に従う。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 640 --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-VOICE1-MALE7-TRIAL-01_DELEGATION_01.md`(先頭が「## 管理ID」+「FAMILY-Y-VOICE1-MALE7-TRIAL-01 委任_01」でなければ636〜652を順に試す)→check実行。
ユーザー原文保存: 下記「ユーザー指示(原文)」の全文を一字も変えず`docs\pm\delegation_log\2026-10-26_FAMILY-Y-VOICE1-MALE7-TRIAL-01_USER.md`へ保存(先頭に`<!-- ユーザー再Trial指示原文(2026-10-26)。逐語。Fable委任_01同梱の写しから転記 -->`の1行可)。

## ユーザー指示(原文)

# 【再Trial指示】Family Y Voice 1｜男性7 Voiceのポーズ比較・最終推奨選定

## 1. 背景と目的

前回のVoice 1長ポーズ原因切り分けTrial（FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01）は、生成ごとのばらつきが大きいことを確認した一方、Voice変更の判断に必要な男性候補の比較を実施していなかった。

にもかかわらず、女性VoiceのZephyrへの変更を推奨したことは不適切だった。

**今回の目的は、Family Y Voice 1に適した男性Voiceを、ポーズの自然さ・安定性・音声品質に基づいて選定すること。**

単にVoice間の有意差を調べるのではなく、量産時に長い不自然なポーズが出にくいVoiceを見極め、最終推奨を1名提示する。

今回の到達StatusはVALIDATED／REJECTED／USER_DECISION_REQUIRED。ProductionのVoice変更は行わない。

## 2. 比較対象

**既存の男性Voice 5名＋追加男性Voice 2名＝合計7名。**

既存5名：

1. Algieba（現行Voice 1）
2. Schedar
3. Fenrir
4. Orus
5. Puck

追加2名は、現行TTSで利用可能な男性Voiceから選定すること。

選定にあたっては、既存5名との声質の違い、英語の自然さ、Family Yの人物Voiceとしての適性を考慮する。

追加2名の名前と選定理由は記録する。

**女性Voiceは今回の比較対象に含めない。**

## 3. Trial設計

前回の反省を踏まえ、生成ごとのばらつきを考慮してもVoiceの違いを判断できる比較試験を設計する。

### 比較条件

- 同一本文を7 Voiceすべてに読ませる。
- Family Y『宅配の再配達は有料にすべきか？』の既存Voice本文を使用する。
- Voice 1本文だけでなく、Voice 2／3の本文も比較対象とし、特定の文章だけに依存した結果を避ける。
- Standard／Advancedの両方で検証する。
- モデル、Style、音声生成設定、速度条件、品質検査条件を揃える。
- 意図的な文章変更や句読点変更は行わない。
- 既存Trial音声は、条件の同一性を確認できる場合のみ再利用する。

### 生成ばらつきへの対策

前回は同一条件でも長ポーズが0〜3回発生し、生成ばらつきが主要因だった。

したがって、各Voiceを1〜2回生成して比較するだけでは不十分。

Claude/Fable側で、以下を考慮した試験計画を策定すること。

- 各Voice・本文・レベルで必要な反復生成回数
- 生成順序の偏りを避ける方法
- Voice間の比較精度
- 平均値だけでなく、悪いtakeが出る頻度
- 結果のばらつきと推定の不確実性
- どの時点で追加生成を終了できるか

必要十分な反復回数を事前に設計する。

初期比較から差が明らかな候補には不要な生成を追加せず、上位候補の差が不明確な場合に重点的に追加検証するなど、品質を守りながら費用と時間を最適化する。

ただし、少数takeの偶然の好結果だけで推奨Voiceを決定しないこと。

評価基準・追加生成条件・停止条件は、結果を見る前に定める。事後的に有利な基準へ変更しない。

## 4. 評価項目

### 最重要：長い不自然なポーズ

少なくとも以下を評価する。

1. 1秒以上の長ポーズの発生回数・発生率
2. ポーズの長さと、1音声あたりの停止占有率
3. 同じVoiceを繰り返し生成した際のばらつき
4. 特に悪いtakeが出る確率
5. 本文・Standard／Advancedによる違い
6. 文末・文境界の自然な間と、文中の不自然な停止の区別

**単にポーズが短ければよいわけではない。** 自然な間は残し、不自然な長停止を減らすことが目的。

### その他の品質条件

- ASR・発音・内容一致
- 繰り返し発話、言い直し、欠落
- 声質の自然さ
- Family Yの一人称Voiceとしての聴きやすさ
- 現行Voice 1の人物像との適合性
- 既存Voice 2／3との聞き分けやすさ
- Standard／Advanced両方での安定性

ポーズが少なくても、音声品質や人物像の適合性が悪ければ推奨しない。

## 5. 分析・最終推奨

次を明確に切り分けること。

- Voice固有の傾向
- 本文固有の傾向
- 生成ごとの偶然のばらつき
- Standard／Advancedの差
- Voiceと本文の組み合わせによる差

前回の結果も比較に活用するが、男女混合の結果を根拠に男性Voiceを推奨しないこと。

7名それぞれについて、長ポーズの発生頻度、平均・ばらつき、悪いtakeの割合、ASR／QA合格率を比較する。

**Fableが独立評価したうえで、最終推奨の男性Voiceを原則1名選定する。**

推奨時には以下を明示する。

- 推奨Voice名
- 現行Algiebaに対する改善幅と不確実性
- なぜ他の候補より優れているか
- 人物像・他Voiceとの整合
- 量産コストへの影響
- 残るリスク

明確な優位性が認められない場合は、無理に新しいVoiceを推奨せず、その理由を数値で示すこと。

## 6. 試聴ページ

7 Voiceの比較試聴ページを作成する。

同じ本文をVoice別に比較でき、Standard／Advancedを切り替えられること。

推奨Voiceと現行Algiebaについては、平均的なtakeだけでなく、長ポーズの多いtakeも確認できるようにする。

各Voiceのポーズ統計・ASR／QA結果を併記する。

ユーザーが実際の声質・人物像への適合性を判断できる構成にすること。

## 7. QCD・予算・進行

品質 ＞ Delivery ＞ 量産単価。

既存音声・計測コード・評価データを再利用し、不要なAPI生成を避ける。

独立した生成・計測・分析・レビューは、競合やrate limit等の制約がなければ並列化する。

**有料API実行前に試験の必要十分なサンプル数と費用を見積もる。** 既存の個別承認枠・日次1,000円（JST）を守り、案件見積が事前承認を要する上限を超える場合は、予算判断のみユーザーへ求めること。無断で範囲・予算を拡大しない。

また、全7名を完全に同数生成すること自体を目的にしない。比較の公平性と結論の信頼性を確保したうえで、生成回数を最適化する。

## 8. Production変更禁止・Closeout

今回の作業はTrialであり、ProductionのVoice割当は変更しない。

- 現行公開音声の差替え禁止
- Voice Registryの正式変更禁止
- 他FamilyのVoice構成変更禁止
- 未承認のTTS Prompt・Style変更禁止
- 既存の品質Gateの緩和禁止

結果はFable独立受入後、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSおよびTrial証跡に適切に反映する。

報告では7名比較表、生成回数、費用、試聴URL、最終推奨Voice、判断根拠、残リスクを提示する。

**最終目的は、生成ごとのばらつきに惑わされず、Family YのVoice 1に最も適した男性Voiceを根拠をもって推奨すること。単なる再調査や候補一覧で終了しないこと。**

## KPI provenance欄

停止計測=fresh(本Trial)+reuse(前回Trial FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01のAlgieba/Schedar音声。全Voice同一Style・同モデル・同減速=条件同一性を`er121_family_y_audio_01.py:454,560`の設定JSONで確認できる場合のみ。前回の女性Voice Zephyrの音声は本比較に含めない)。混在時は表ごとにfresh/reuse内訳。E2E自己確認=No。

## Opus台帳更新

該当なし。

## Fableからの前提・既知事実

- 前回Trial(`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/{DESIGN_01,RESULT_MATRIX_01}.md`、`measure/samples_measured.json`、`tools/yvp_cross_generate_01.py`・`yvp_summarize_01.py`・ページ生成script、`docs/pm/RESULT_PACKET_YVP1.md`): 全Voice同一の`FULL_STORY` Style・同モデル・同QA・同減速、Voice名のみ差(`er121_family_y_audio_01.py:454,560`)。Algieba: Std 本文1 n=9〜16/本文2・3 n=3〜4、Adv 本文1 n=14〜23/他n=3〜4。Schedar(V3): 各本文n=3〜10。既存音声は`er121_output/family_y_voice_pause_trial_01/{a2,b1b}/`とrun_01正式take・Voice 1候補。計測条件: −40 dBFS・≥150 ms・<120 ms結合、`yfb_pause_align_01`で停止位置と本文・句読点を対応付け可能(文境界/文中の区別に使う)。
- 前回結果: 1秒以上停止/sample Std Algieba 1.31・Schedar 0.89(・Zephyr 0.10は女性で対象外)、Adv 0.61・0.70。cell内分散がStd 84%/Adv 65%。Repetition QA旗はAlgiebaに集中(別事象)。
- Voice名の所在: `er121_family_y_structure_01.py`(Y Voice 1〜3)、Voice Registry/Z正式表(YL-C10)・X/ZのVoice割当(Grep `Algieba|Schedar|Fenrir|Orus|Puck|Charon|Enceladus|Iapetus|Umbriel|Algenib|Rasalgethi|Achird|Zubenelgenubi|Sadachbia|Sadaltager|Alnilam|Gacrux|Kore|Zephyr` in `*.py`・`docs/`)。追加2名はTTS backendで利用可能な男性Voice一覧(`er003_*tts*`/`er012_b`/設定ファイルのGrep)から、既存5名・Y Voice 2/3・X/Zの主要Voiceと重複せず声質が異なるものを選び理由を記録(性別はbackendのVoice説明/既存Registryの記載で確認し、出典を書く。確認できないVoiceは選ばない)。
- Fable設計既定(DESIGN_01で固定。合理的理由があれば変更可・理由記録): **主要指標**=「文中の不自然な長停止」=`yfb_pause_align_01`で文境界(`. ? ! …`直後・段落境界)に対応しない≥1.0秒の停止の1 sampleあたり回数(primary)、補助=文境界含む≥1.0秒回数、停止占有率、最長停止、悪いtake率=P(文中≥1.0秒停止が1回以上)、ASR/QA合格率、Repetition旗率。**Phase 1**=追加5 Voice(Fenrir/Orus/Puck/追加2)×3本文×2レベル×2 take=60 take、Algieba/Schedarは既存再利用(cell n<2なら補充)。**停止/継続規則(事前固定)**: Phase 1後、primaryのVoice別平均と95%区間(ブートストラップ、本文・レベルで層別)を算出。(i)上位候補と区間が重ならない下位Voiceは追加生成なし。(ii)上位3 Voice(Algiebaを含まなければAlgiebaを加える)に対し各cell+2 take(最大36 take)。(iii)Phase 2後も上位2名の区間が重なる場合は追加生成せず「明確な優位なし」として数値で報告(Guardrail内での追加はFable判断事項として報告に残す)。**推奨条件**: primaryでAlgiebaより改善し区間が重ならないか、重なっても悪いtake率が半減以上、かつASR/QA合格率・Repetition旗率がAlgieba以上、かつ声質の決定論的問題(ASR不一致・欠落)がないこと。該当なしなら推奨せず。
- 聴感(声質・人物像適合・聞き分け)は機械評価できないため、試聴ページで判断材料を提示し、Fable/ユーザー判断に委ねる(Sonnetは主観評価を結論にしない)。

## 事前指定Read一覧

1. 前回Trial: `docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/{DESIGN_01,RESULT_MATRIX_01}.md` 全文、`tools/yvp_cross_generate_01.py`・`yvp_summarize_01.py`・ページ生成script 全文(派生元)、`measure/samples_measured.json`(schema把握、先頭のみ)。
2. `er121_family_y_audio_01.py` :440-470, :550-575(Style/モデル/減速設定の確認。読取のみ)、`er121_family_y_structure_01.py` Grep `Voice|voice`。
3. Voice一覧・性別: Grep上記Voice名群 in `*.py`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/**`(Y Voice選定時の候補表があればそれを使う)、`CURRENT_SPEC.md` Grep `Voice Registry|YL-C10|Algieba`。
4. 計測tool: `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/{yfb_silence_scan_01,yfb_pause_align_01,yfb_pause_stats_01}.py` の`--help`/docstring。
5. `tools/stop_scope_check_01.py --help`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- SSOT編集なし。OPEN-531更新文案・DECISION_LOG文案・CURRENT_SPEC(Voice変更はユーザー判断後)をRESULT_PACKETへ。

## 実行コマンド全文

- 設計固定後にsha記録: `py -c "import hashlib;print(hashlib.sha256(open('docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/DESIGN_01.md','rb').read()).hexdigest())"`。
- 生成(例、実値で。1起動=ラウンドロビン配列の1バッチ): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe docs\research\FAMILY-Y-VOICE1-MALE7-TRIAL-01\tools\ym7_generate_01.py --plan docs\research\FAMILY-Y-VOICE1-MALE7-TRIAL-01\plan_phase1.json --batch 1 --out er121_output\family_y_voice1_male7_trial_01 --budget-jpy 250`(各起動前`py tools/stop_scope_check_01.py`、`Get-Date`記録、間隔150秒以上)。
- 計測・集計: `py docs\research\FAMILY-Y-VOICE1-MALE7-TRIAL-01\tools\ym7_measure_01.py --in er121_output\family_y_voice1_male7_trial_01 --reuse docs\research\FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01\measure\samples_measured.json --out docs\research\FAMILY-Y-VOICE1-MALE7-TRIAL-01\measure\samples_01.json`、`py …\ym7_summarize_01.py --in …\samples_01.json --design …\DESIGN_01.md --out …\RESULT_01.md --json …\summary_01.json`(ブートストラップ区間、Voice×本文×レベル表、Phase 2対象の機械判定)。
- ページ: `py …\ym7_page_01.py --summary …\summary_01.json --out user_test\family_y_voice1_male7_trial_01\index.html`(本文×レベル切替、Voice別、各Voiceの統計/ASR/QA併記、推奨候補と現行Algiebaは平均的takeと長停止の多いtakeを併置、Trial注記)。
- offline test(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py -m pytest docs\research\FAMILY-Y-VOICE1-MALE7-TRIAL-01\tools\ym7_tools_test_01.py -q`(設定同一性assert・ラウンドロビン順序・停止規則の決定論)。
- Production不変: `git status --short -- er121_family_y_audio_01.py er121_family_y_structure_01.py er121_output/family_y_production_01/redelivery_fee/run_01 user_test/family_y_production_redelivery_fee_01`(本委任由来の差分0。並行Agentの差分は記録のみ)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。

## 成果物(`docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/`)

`DESIGN_01.md`(比較対象7名と追加2名の選定理由・出典、条件同一性、指標定義、Phase 1/2の生成計画と費用見積、停止/継続規則、推奨条件、ブートストラップ手順。生成前にsha固定)、`REUSE_CHECK_01.md`(前回音声の条件同一性判定と採否)、`plan_phase1.json`/`plan_phase2.json`、`tools/`、`measure/`、`RESULT_01.md`(7名比較表: 文中≥1s/全≥1s/占有率/最長/悪いtake率/ASR・QA合格率/Repetition旗率、各々平均・区間・n・fresh/reuse内訳、本文別・レベル別、Voice×本文交互作用、Algieba比改善幅と不確実性)、`BUDGET_LOG_01.md`(起動ごと時刻・take数・実費・累計)、`user_test/family_y_voice1_male7_trial_01/index.html`+mp3、`docs/pm/RESULT_PACKET_YM7.md`。

## SSOT追記文

文案のみ: OPEN-531更新(本Trial結果・Status候補・推奨候補)、DECISION_LOG(Fable受入後)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。ACTIVE_TASK編集なし。
- 明示add: `docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/**`(wav不可)、`user_test/family_y_voice1_male7_trial_01/**`、delegation_log 2ファイル+check.json。
- commit: `git commit --only <paths…> -m "FAMILY-Y-VOICE1-MALE7-TRIAL-01 委任_01: Y Voice 1男性7Voice×3本文×2レベル 適応的ポーズ比較Trial(新規<N> take、実費<X>円、Production未変更、試聴ページ)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(推奨条件を満たすVoiceの有無、満たす場合の候補と数値、満たさない場合の理由数値。Sonnetは「推奨候補」と表記、最終推奨はFable) (2)7名比較表(fresh/reuse内訳付き) (3)切り分け(Voice固有/本文固有/ばらつき/レベル差/交互作用) (4)追加2名の名前・選定理由・出典 (5)停止規則の適用経過(Phase 1→2の対象Voice、追加take数、終了理由) (6)Algieba比の改善幅・不確実性、人物像・V2/V3との聞き分けの材料(試聴ページ上の位置) (7)量産コスト影響(Voice変更=0円、選別方式を併用する場合の単価は前回値を引用) (8)残リスク・未確定 (9)費用(起動ごと・実費・累計/Cap 250、共有台帳への書込行数) (10)保全・Production不変 (11)試聴URL `https://shimomura055.github.io/eigo-radio/user_test/family_y_voice1_male7_trial_01/index.html`+ローカル検証 (12)commit/push・raw URL (13)一覧外Read (14)Fable向け懸念(過剰断定の自己点検)。最終行に要約10行以内。