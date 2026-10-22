# KP英語フレーズ「3-ASR多数決(OpenAI・Azure・Whisper、2/3 PASSで最終PASS)」Family X/Z Production実装設計書(Opus条件Aレビュー用)

管理ID: KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01 / 2026-10-22 / Status: `APPROVED_FOR_PRODUCTION`(ユーザー原文=`docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_USER.md`)。本設計時点は**未配線**(Production既存ファイル未編集=`PRODUCTION_WIRED`ではない)。API 0・JPY0。調査=`INVESTIGATION_01.md`。
到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`。置換対象=`er096_kp_dual_pass_01.py`の「両方PASS必須」(OPEN-440 `CLOSED_PRODUCTION_WIRED`、CURRENT_SPEC「Key Phrase英語phraseのPrimary・Secondary両方PASS必須」節)。

## 0. 要件(ユーザー§2〜§5)
KP英語フレーズのみ、2/3 PASSで最終PASS。両PASSならWhisper不要、両NGもWhisper不要、**片側NGのときだけWhisper**。Whisper失敗・未利用でPASSにしない。KP英語解説・その他音声・Family A/B/Cは現行維持。再生成上限・retry/fallback・安全STOP・HR Lockは維持。再利用(Store/前回results/inheritance)全6点にも新判定を一貫適用。大規模追加Trialはせず保存資産で再評価。

## 1. 真理値表(ユーザー§2をそのまま固定、`er104_kp_three_asr_vote_01_test_01.py` TruthTable 6行)
| Primary(OpenAI) | Secondary(Azure) | Whisper | 最終 | 内部state |
|---|---|---|---|---|
| PASS | PASS | 呼ばない | PASS | `PASS_DUAL` |
| PASS | NG | PASS | PASS | `PASS_VOTE_2OF3` |
| PASS | NG | NG | NG | `NG_VOTE_WHISPER_NG` |
| NG | PASS | PASS | PASS | `PASS_VOTE_2OF3` |
| NG | PASS | NG | NG | `NG_VOTE_WHISPER_NG` |
| NG | NG | 呼ばない | NG | `NG_BOTH` |
「PASS」の意味=現行分類器(`classify_asr_match`+CMU同音救済`_step_alternate_pass`+値/否定ガード)のPASS。**Primaryは「OpenAI自身のPASS」**: Azure転写に依存した救済(非ラテンKP層・Tier3・cs_equivalence)・AMBIGUOUS/length降格PASSは**Primary NG票**(er096のOF-KPD-P-06踏襲)。Whisper判定は`make_voter`(`classify_asr_match`+`_step_alternate_pass`+値/否定ガード。**M1は適用しない**=保守側。新基準は作らない)。長さ制約(`max_len`、A3)は各票に適用(長さNGの転写はNG票)。最終状態の`PASS_VOTE_2OF3`は判定表上`PASS`(warning labelなし。監査は`kp_vote_check`/`assembly_audit`で追跡)。

## 2. 呼出順と条件(コストを最小に)
1. Primary取得失敗=`NG_PRIMARY_ASR_FAILURE`。Primary保護差(P1: 値DIFF/否定差)・除外(P2)は**既存どおり短絡**(`NG_PROTECTED`/`NG_EXCLUDED`)。Secondary/Whisperを呼ばない。
2. Secondary(Azure)を必ず呼ぶ(現行dualと同じ。Primary NGでも呼ぶ=P3相当)。
3. P/Sが一致 → 確定(Whisper不呼出)。**割れたときだけ**Whisperを1回(ローカル、API 0)。
4. 反対票側(割れた側のNG票)に保護差(値DIFF/否定差=別の数/否定を言っている)があれば2/3を成立させない(`NG_PROTECTED_DISSENT`、保守側。KPに数字はほぼ無く影響は極小。Opus確認観点O-3)。
Whisperは同一wavにつき1回(per-process memo可。`sha256`キー)。

## 3. fail-closed と Secondary障害時の扱い
- Whisper例外・未導入・空転写・timeout(既定60秒)・`whisper_fn`未設定 = `NG_WHISPER_UNAVAILABLE`(**PASSにしない**)。通常NG attemptとして次slotへ回すのではなく、`NG_SECONDARY_UNAVAILABLE`と同じ**技術STOP分類**(HRに入れない、再実行で再開可。`er006_secondary_asr_01.py` L1167-1175の`_tech_only`にstateを追加)を推奨。理由: 環境障害を人間のHRに流すのは誤り(Opus確認観点O-4)。
- **Whisper circuit/事前確認(推奨)**: KP stage開始時(X/Z)に`whisper_preflight()`(モデルロード確認、約2秒)を1回行い、失敗なら最初のTTS前に技術STOP。連続Whisper不能が閾値(Azureと同じ3)を超えたらENGLISH_LOCK段スキップ(`_dual_circuit_open`同型)。
- **Secondary(Azure)取得不能(例外・空転写・circuit open)=従来どおり`NG_SECONDARY_UNAVAILABLE`、Whisperを呼ばない・Primary+Whisperの2/3へ降格しない**。根拠: 現行承認(UDR #139)「Azure障害でPrimary単独PASSへ降格しない」の趣旨を維持。ユーザー§2の表はAzure「NG」の行であり「障害」の行を定義していない。技術STOP・再実行で再開可、HRに入れない(現行どおり)。→ Opus確認観点O-2(Azure障害時の2/3降格を認めない解釈で良いか)。
- tie-break無効化の段階rollback定数 `KP_WHISPER_TIEBREAK_ENABLED=False`: Whisperを呼ばず、割れ=通常NG(`NG_SPLIT_TIEBREAK_OFF`)。全8通りが旧「両方PASS必須」と一致(test固定)。旧ルールのコードを残さずに旧挙動へ戻せる。

## 4. Whisper構成と環境(実測=`whisper_env_check_01.json`)
- 構成: faster-whisper `small` / cpu / int8(Production既存の`er008_disfluency_qa_18._get_model`を共有。既存検証[ASR3W・er099]と同一)。medium不採用(ユーザー§4「不要な比較はしない」。small 7件・take partの結果が指示§3と一致=下表§10)。
- **新規依存ではない**: 同じloaderが全verified英語snippetの吃音QA(`disfluency_qa=True`)と`er006_secondary_asr_01.py` L533のCS Equivalence層で既に毎回動作(INVESTIGATION §5)。実環境: Python 3.14.6、faster_whisper 1.2.1、ctranslate2 4.8.1、16コア、キャッシュ`~\.cache\huggingface\hub`(tiny/small/medium)、import 0.40秒・ロード2.0秒・1clip 2.07秒平均(n=12、0.98〜1.94秒の音声)・`HF_HUB_OFFLINE=1`でも成功。
- ローカル実行のためWhisper API費用0。X/Zの並列processでもモデルは各process 1ロード(約2秒、CPUメモリ約数百MB)。重い並列時のCPU競合は未計測(KPでのWhisper発火は割れた時のみ=下記発火率)。

## 5. 判定統合方式(judge)
`er078_asr_unified_judge_01.py`の`done()`(唯一の出口)でdual分岐を置換する(最小差分):
- 現行: `done()`が「PASSだがprimary_pass=False」→`NG_DUAL_PRIMARY_NOT_PASS`。
- 新: dual分岐(識別子は§6で`vote_required`へ改名)の`done()`が、ハード状態(`NG_PROTECTED`/`NG_EXCLUDED`/`NG_PRIMARY_ASR_FAILURE`/`NG_SECONDARY_UNAVAILABLE`)以外で`primary_pass != secondary_pass`なら`ctx.whisper_fn`を呼び、PASSなら`PASS`(reason`vote_2of3:*`)、NGなら`NG_BOTH`相当(reason`whisper_ng_1of3`)。`secondary_pass`は既存の設定箇所(受理+length OK時)を使い、Secondary値/否定DIFFの出口に`dual["secondary_protected_diff"]=True`を追加(O-3のため)。
- 共通核`er104_kp_three_asr_vote_01.decide()`(純関数、API 0)を**真理値のSSOT**とし、judge分岐とaudit形式(`pass_count`/`whisper_called`)を同一にする。**配線時にjudgeの分岐と`decide()`が全組合せ(P×S×W×unavailable)で一致することを検証するequivalence testを必須化**(実装二重化のdrift防止)。
- adapter(`evaluate_attempt_with_cascade_detail`): `whisper_fn`(`whisper_transcribe`+`make_voter`同等の許容判定)をctxに注入。step名`whisper_vote`、provider`faster_whisper`、audit`dual.whisper={called,text,accepted,label,error,ms}`。Azure `SecondaryCache`と同様、同一wav sha内でWhisper結果をmemoし再呼出しない。
- 同一ファイルの競合: PNAP(OPEN-450)は`NG_BOTH`後の救済でdual分岐外。配線は PNAP配線完了後 or 差分再確認のうえ実施。

## 6. 配線点ごとの差分案・命名・Store(「旧dual」を残置せず置換)
**命名方針(推奨、O-5)**: 永続名と状態名は`vote`へ全面改名し、旧名を撤去(旧名の残置は旧ルールとの混同源)。
| 旧 | 新 |
|---|---|
| `KP_EN_PHRASE_DUAL_REQUIRED` / `dual_enabled()` | `KP_THREE_ASR_VOTE_ENABLED` / `vote_enabled()`(単一flag読取関数) |
| `dual_pass_required`(kwarg)/`dual_required`(ctx)/`build_attempt_ctx(dual_required)` | `vote_pass_required` / `vote_required` |
| `NG_DUAL_PRIMARY_NOT_PASS`(state) | 廃止(`NG_VOTE_*`/`NG_BOTH`)。`STATES`・読み手(`er078_auw_runtime_evidence_10.py`等)をGrepで更新 |
| `audit["dual"]` / step名`secondary_dual` | `audit["dual"]`は`audit["vote"]`へ。step名`secondary_vote`+`whisper_vote` |
| `kp_dual_check`(v1)/Store field | `kp_vote_check`(v1)。**旧`kp_dual_check_v1`は読取のみ**(中のPrimary/Secondary転写でAPI 0再判定。書込は新fieldのみ) |
| X default key `+dual1` | `+vote1`。**本番Store manifestの`+dual1` entryは0件**(INVESTIGATION §3)なので改名のorphan/再生成費用は0。旧共有keyは引き続き上書きしない |
| `kp_dual_reuse_ok`/`KpDualReuseGate`/`evaluate_dual`/`assembly_audit` | `kp_vote_reuse_ok`/`KpVoteReuseGate`/`evaluate_vote`/`assembly_audit`を`er104_kp_three_asr_vote_01.py`へ移設し`er096_kp_dual_pass_01.py`を削除(testも移設) |
代替案(最小差分、識別子`dual`を維持し意味だけ変更)は編集箇所が少ないが、名前と意味の不一致が残るため非推奨。どちらでもequivalence testとAST testで保護する。

**配線(6呼出点+再利用6点、呼出点の数・位置は不変)**:
| # | 点 | 変更 |
|---|---|---|
| 呼出1,2 | X default `generate_key_phrase_component_verified`(Minimal 2/English Lock 2)via`ensure_key_phrase_english_component_x_vote` | kwarg改名のみ |
| 呼出3,4 | X K2 `_styled_two_stage` primary・`_gen_lock` | 同 |
| 呼出5,6 | Z `_kp_en_two_stage` primary・lock | 同 |
| 再利用1 | X runner `_generate_or_reuse_kp` role=english(前回results、S1可) | helperが新判定。保存`kp_vote_check`/旧`kp_dual_check`のP/S転写から再判定。割れ→保存Whisper転写(同sha)があればそれ、無ければローカルWhisper。Azure再呼出なし |
| 再利用2 | `try_inherit_from_cached`(API 0) | 同。ローカルWhisperはAPI 0扱い(許容。"Azureを呼ばない"のが契約) |
| 再利用3,4 | K2 Store key A/B `reuse_gate` | `KpVoteReuseGate` |
| 再利用5 | X default `+vote1` key | 同 |
| 再利用6 | Z `generate_or_reuse_z` kp_en | 同 |
**Store再利用の意味**: 既存`kp_dual_check`にP/S転写が保存済みなら再利用時にAzure再呼出なし(0円)。think up/blurt型(現行NGで再生成予定のentry)は**TTS・Primary・Azure全て不要でWhisper(ローカル2秒)のみ**で再利用可否が決まる=再生成削減。証跡なしの旧entryは従来のS1(Primary保存転写+Azure 1回)→必要ならWhisper。判定不能(転写欠落/sha不一致)は再利用しない(fail-closed)。Azure障害=技術STOP(従来)。

## 7. 旧ルール・旧検査の整理(撤去/書換/残置)
| 識別子 | 場所 | 扱い |
|---|---|---|
| `NG_DUAL_PRIMARY_NOT_PASS` | judge L47-53, L403-410, L596-600、`er078_auw_runtime_evidence_10.py`、test | 撤去(`STATES`含む) |
| 「Secondary単独PASSは最終合格にしない」(`done()`内`not dual["primary_pass"]`変換) | judge L403-410 | 撤去(2/3多数決に置換。Secondary単独PASSはWhisperが同意しなければ従来どおりNG) |
| `primary_rescued_by_secondary`のPrimary NG扱い | judge L460-471、adapter L1076-1085 | **維持**(救済PASSをOpenAI票に数えない) |
| `er096_kp_dual_pass_01.py`全体、`er096_kp_dual_pass_01_test_01.py`/`_wiring_test_01.py` | | 新module/testへ移設後に削除(判定表assertを3-ASR版に更新) |
| CURRENT_SPEC「KP PASS条件表」(L2914-2935)、2818/2819/2820/2828、1839注記 | | 置換案は`RESULT_PACKET_KP3V1.md`(本委任では編集しない) |
| `+dual1`/`kp_dual_check`/`secondary_dual` | | §6の表どおり改名。旧fieldは読取のみ(migration reader) |
| 他の「両方PASS」記述 | `er096_kp_dual_pass_01.py`コメント、docs/research/KPDUAL... | 履歴として残置(docs)。Production .pyコメントは移設時に更新 |
配線後に`grep -rn "dual_pass_required|dual_required|NG_DUAL_PRIMARY|kp_dual_check|+dual1|secondary_dual|KP_EN_PHRASE_DUAL" --include=*.py`を実行し、legacy readerの1箇所と履歴test以外0件であることを受入条件にする。

## 8. test計画(配線委任で実施。本委任で下記★は実装・PASS済み)
- ★unit真理値表(6行+呼出回数)・fail-closed(Whisper例外/空/未設定/timeout)・Azure障害(Whisper不呼出・2/3降格なし)・Primary失敗/保護差短絡・反対票保護差・tie-break無効=旧dual一致・実転写4ケース(think up/blurt/take part不良/合格)・旧`kp_dual_check_v1`の再判定・隔離(Production .pyが`er104_*`をimportしない)=28件(`er104_kp_three_asr_vote_01_test_01.py`)。
- 配線test: (a)judge分岐と`decide()`のequivalence(全組合せ) (b)X default/K2/Zの`strict`をrouting+Azure+Whisper mockで実行(4回構成・最終slotのみHR・割れでWhisper 1回・両PASS/両NGでWhisper 0回) (c)再利用6点が新helperを通る(AST+呼出) (d)AST: `vote_pass_required`を渡す呼出点がKP英語6点のみ、解説(`KP_EXPLANATION_MAX_ATTEMPTS`)・phrase_repeat・日本語・A/B/Cは渡さない (e)Whisper不能時に最終成果物がPASS扱いにならない・HRに入らない。
- Regression: 非KPの保存4,032ペア(配線前後バイト一致)、既存のer006/er078/er019/er063系(2,339件)、保存音声の新旧判定(`stored_audio_reeval_01.json`、下記§10)。
- 11-7限定例外は不適用(ユーザー承認済み既定ON実装)。

## 9. runtime evidence計画・見積(配線委任、API最小)
- **X**: byUs記事のKP Store再利用(正式runnerのKP stageのみ)。think up/blurtのentryは`kp_dual_check`(P/S転写)保存済み→再利用時に割れ→**ローカルWhisperのみ**でPASS→再利用(Primary/Azure再呼出0、費用¥0)。加えて新規生成1KPを正式経路で(TTS+Primary+Azure≈¥0.12、割れは自然発生待ち)。
- **Z**: Z KP stage(`generate_or_reuse_z`)で、`cause a stir`型(P NG/S PASS/W PASS、保存wav `er096_output/kp_dual_prod_01/stats/theme/b1b/narration/attempts/kp22_en_attempt3_*.wav`)の前回results entryを再利用点6に通し、Whisper発火・PASSを記録。新規生成1KP(≈¥0.12)。
- 見積合計≤¥5(上限10円、案件300円以下、日次1,000円内:当日既使用約¥878+見積≤¥5=約¥883)。翌JST日待ちは不要。配線自体はコスト0。
- 記録項目: 両/三Provider判定・呼出有無(Whisper発火回数)・model_id(OpenAI/Azure/faster-whisper small int8)・`kp_vote_check`・routing・attempt/slot。

## 10. 保存音声での新旧判定(0円、`stored_audio_reeval_01.json`、`er104_stored_audio_reeval_01.py`)
OpenAI/Azure=保存転写、Whisper=er091保存転写または保存wavへのローカルsmall再転写。判定関数=Production既存分類器。
| 対象 | 件数 | 旧(両方PASS) | 新(2/3) | NG→PASSに変わる件 | PASS→NG |
|---|---|---|---|---|---|
| byUs KP7(think up/can't wait/fan stories/take part/story-maker/blurt/bring in) | 7 | 5 | 7 | `think up`(P PASS/S NG/W PASS)、`blurt`(P NG/S PASS/W PASS) | 0 |
| take part 旧問題音声(er088 10回+Production実呼出3回、同一wav) | 13 | 0 | 0 | 0(P PASSの3試行はWhisper『Take Tarte.』でNG_VOTE_WHISPER_NG) | 0 |
| take part 合格音声 | 1 | 1 | 1 | 0(3系統PASS) | 0 |
| ASR3W KP(正常+HR難例28+問題8、3系統の保存転写が揃う36件) | 36 | 27 | 27 | 0 | 0 |
| 24 KP生成attempt(stats、27 attempts) | 27 | 23 | 25 | `cause a stir` attempt3/4(P NG/S PASS/W PASS) | 0 |
- **問題音声21件(ASR3W問題8+take part 13)の新規誤PASS=0**(旧も0)。TTS構成の誤読5本(weaken→Weekend、turn on→off、make rewards、for bank、take tart)・splice脱落2本・user報告take tartの全てで、3系統のうち2つ以上が誤読を転写(P/S両NG=Whisper不呼出)、またはPrimary PASSの3試行でWhisperが『Take Tarte.』でNG。
- ユーザー§3の4ケースを再現: think up=P PASS/S NG/W PASS→PASS、blurt=P NG/S PASS/W PASS→PASS、take part旧問題音声=3系統NG→NG、合格音声=3系統PASS→PASS。smallで一致(mediumは不要)。
- 残存リスクの明示: 誤PASSにはPrimaryとWhisper(またはAzureとWhisper)が**同じ誤りで揃って正しく聞く**必要がある。独立した問題音声は実質take part 1本+構成5本+splice2本(n小)で、統計的保証ではない。Whisperはtake partで『Tarte』を一貫して返し(small/medium・10回とも同一)、Primaryの「言語prior補正」を打ち消す方向に働いた。`cause a stir`の2attemptsは人間聴取ラベルなし(Azure・Whisperとも『Cause a stir』と転写、Primaryのみ『Causeister』『Cause of stir.』)で、PASSの妥当性は未聴取(Fableが数本聴取する価値あり)。
- ASR3W KP 39件のうち3件は3系統の保存転写が揃わず除外。

## 11. 処理時間・再生成削減見込み
- 追加時間: Whisperは割れた時だけ約2.1秒/clip(再利用時はモデルロード約2秒が1回)。割れの発生率(保存資料): 24KP attempts 2/27=7.4%、ASR3W正常 1/28=3.6%、byUs Store7件 2/7(うち現行NGのentry)。10 KP/article set換算の期待追加≈0.4〜1.5回×2.1秒≈1〜3秒/セット。disfluency QA(既存、全verified clipで同じloader)と合わせても許容(重大な悪影響なし)。
- 再生成削減(保存データ、小標本): attempt NG率 4/27(14.8%)→2/27(7.4%)、`cause a stir`はNG4回→HR(STOPPED)がattempt3で成立。byUs Storeの2/7(think up/blurt)は再生成が不要。1 attemptの再生成費用≈¥0.12(24KP statsの実費¥3.18/27attempts)+TTS待ち時間。KPのHR発生は24KPで1件(4%)→新方式で0件(小標本)。追加原価=Whisperは¥0、Azure追加呼出なし(現行dualと同数)。
- 逆方向の代償: なし(旧PASSがNGになる件は保存資産で0)。

## 12. 固有名詞アラーム方式(PNAP、OPEN-450)との整合
KPは対象外(PNAPはKP以外のsegmentの`NG_BOTH`後最終救済)。KPに固有名詞(例: Melos)が含まれても3-ASR多数決が適用され緩和はない。同音救済(CMU/M1)は各票の判定内に含まれ、PNAPの人間確認フローとは独立。

## 13. rollback
- 一次: `KP_THREE_ASR_VOTE_ENABLED=False`(単一flag読取関数。環境変数・引数・設定dictからの迂回なし)→6呼出点が`vote_pass_required=False`=dual導入前(Primary単独)の挙動。
- 二次(推奨の段階rollback): `KP_WHISPER_TIEBREAK_ENABLED=False`→割れ=NG、旧「両方PASS必須」と同一結果(コード不要)。Whisper環境障害時の運用逃げ道。

## 14. Opus条件Aレビュー確認観点(ユーザー判断ではなく技術確認)
- O-1: 判定の置換位置(`done()`出口)と、`decide()`純関数との二重実装のdrift防止(equivalence testで足りるか)。
- O-2: Azure取得不能時に「Primary+Whisperの2/3」へ降格しない(技術STOP維持)解釈の妥当性(ユーザー表は「NG」行のみ。降格を認めるとAzure障害中の品質低下リスク、認めないとAzure障害中はKP生成が止まる=現行と同じ)。
- O-3: 反対票側の保護差(値/否定DIFF)で2/3を成立させない保守側ルール(表に無い追加条件だが既存の保護ガードの延長)。不要なら`protected_dissent_blocks=False`で表どおりになる。
- O-4: `NG_WHISPER_UNAVAILABLE`を技術STOP(HR不投入)にするか・事前確認(preflight)とWhisper circuitの要否。
- O-5: 全面改名(`dual`→`vote`、`+vote1`、field `kp_vote_check`)か、識別子維持の最小差分か。
- O-6: Whisperのみ追加でM1非適用・smallのみで十分か(誤PASS最小化=保守側)。
- O-7: ローカルWhisperを「API 0」文脈(inheritance)で許容する契約解釈。
- O-8: 既存disfluency QA(同loader・同clip)との2重転写(約2秒、割れ時のみ)を許容するか(sha memoで統合する最適化は`er008`編集を伴うため不採用推奨)。

## 15. 実装ファイル(本委任で作成済み・未配線)
`er104_kp_three_asr_vote_01.py`(判定核・Voter・`decide`・`make_voter`・`whisper_transcribe`・`rejudge_stored`・`vote_check_from_decision`)、`er104_kp_three_asr_vote_01_test_01.py`(28件PASS)、`er104_whisper_env_check_01.py`、`er104_stored_audio_reeval_01.py`。実行: `.venv\Scripts\python.exe -m unittest er104_kp_three_asr_vote_01_test_01 -v`。

---

# 委任_02 追記: Opus条件Aレビュー(OF-KP3V-P-01〜12)の反映(2026-10-22)
本節は §1〜§15 の設計を**上書きする箇所**を明記する(§1〜§15は委任_01時点の設計として残す)。Opus全文要旨=`OPUS_REVIEW_COND_A_01.md`。

## 16-1 設計変更の一覧(P-xx → 反映先)
| P | 設計変更 | 反映先(ファイル:関数) |
|---|---|---|
| P-01 | 再利用6点の再判定は**本番adapter経由**(`evaluate_attempt_with_cascade_detail`、`vote_required=True`、保存Secondary転写をcacheへ注入、保存Whisper転写[同sha]または既定ローカルWhisper)に統一。手書き`rejudge_stored`は**削除**。旧`asr_judgement.dual`/`kp_dual_check_v1`は読取専用。保存音声再評価も本番adapter経路(`er104_stored_audio_reeval_02.py`) | `er104_kp_vote_reuse_01.py:evaluate_vote/kp_vote_reuse_ok`、`er104_stored_audio_reeval_02.py` |
| P-02 | Whisper票にも呼出元と同じ`max_len`長さ判定、値ガードAMBIGUOUSは**PASS票にしない**(`ambiguous_blocks`) | `er104_kp_three_asr_vote_01.py:make_voter/whisper_vote` |
| P-03 | 表4行目(P NG/S PASS/W PASS)=`PASS_WITH_WARNING`+`SECONDARY_CONFIRMED`(事後試聴リスト)。表2行目(P PASS/S NG/W PASS)=警告なし`PASS`。adapterのclassification上書きは行ごとに整理(行1・行2=Primary根拠保持、行4=Secondary分類) | `er078:finish_vote`、`er006:evaluate_attempt_with_cascade_detail`(`row in (P+S,P+W)`) |
| P-04 | 戻しスイッチは`KP_WHISPER_TIEBREAK_ENABLED=False`(=旧「両方PASS必須」)の**1本のみ**。Primary単独へ落とすスイッチは置かない。定数読取は単一関数(`vote_enabled()`/`tiebreak_enabled()`) | `er104_kp_three_asr_vote_01.py`(testで「Primary単独スイッチ不在」を固定) |
| P-05 | **混合方式**: 意味名[flag関数・kwarg・ctx・state・step名]は`vote`へ(`vote_enabled()`/`vote_pass_required`/`vote_required`/`audit["vote"]`/`secondary_vote`/`whisper_vote`)、`NG_DUAL_PRIMARY_NOT_PASS`は**撤去**。保存容器名`kp_dual_check`・telemetry名(`reuse_blocked_by_kp_dual_gate`/`kp_dual_gate`/`kp_dual_reuse_gate`)は**維持**(共有Store`er006_master_audio_store_01.py`無編集)し、`version="kp_vote_check_v1"`で新旧を区別。X default Store keyは`+vote1`(本番manifestの`+dual1`は0件を実測=orphanなし)。er096は**履歴script**として残置(Production importなしをAST+unittestで固定)。PNAPのKP除外は新flag(`vote_required`)へ追従 | 全配線点(§16-3)、`er096_kp_dual_pass_01_test_01.py`(履歴固定)、`er103_proper_noun_alarm_policy_01.py` |
| P-06 | Zのruntime evidenceは**正式経路のみ**(dual導入前のZ KP entryを再利用点6のS1経路へ+新規KP)。人工entry・HR Lock迂回は禁止。発火が観測できなければ「Xで発火観測+Zが同じadapterを通ることをtestで固定+Zの正式runで`kp_vote_check_v1`記録が出ること」を事実として記録 | `RUNTIME_EVIDENCE_02.md`(c commit) |
| P-07 | 解釈の明記(§16-5) | CURRENT_SPEC/DECISION_LOG/closeout |
| P-08 | 空転写=NG票(通常再生成)、例外/import失敗/timeout/circuit open=**技術STOP**(`NG_WHISPER_UNAVAILABLE`、HRに入れない、再実行で再開可)。timeoutはcircuit閾値1で即open。KP stage生成前にWhisper事前確認(preflight、model cache有無・load秒・model/compute type記録)、English Lock前のcircuit確認をAzureに加えWhisperにも拡張。OPEN-371(Azure障害時の技術STOPがHR Lockへ入る現行挙動)の露出はWhisperにも及ぶ点をOPEN-371へ追記 | `er104_kp_three_asr_vote_01.py:whisper_vote/whisper_preflight`、`er104_kp_vote_reuse_01.py:guard_whisper`、`er003:_vote_circuit_open` |
| P-09 | judgeの`done()`出口は**純粋集計関数`tally()`を1つ呼ぶ**(`finish_vote`)。`decide()`も同じ`tally()/whisper_needed()`。状態変換(PASS/PASS_WITH_WARNING/NG)は`done()`のPASS→PASS_WITH_WARNING変換とLR_REWRITTEN付与より前。票集計前に確定する除外状態4つ=`NG_PRIMARY_ASR_FAILURE`/`NG_PROTECTED`(P1)/`NG_EXCLUDED`(P2)/`NG_SECONDARY_UNAVAILABLE` | `er078:finish_vote`、`er104:tally/whisper_needed/decide`、test`test_P09_judge_and_decide_agree_on_all_combinations` |
| P-10 | `kp_vote_check`に**合格した行**(`row`: P+S/P+W/S+W)を記録。think up・blurt・cause a stir#3/#4の4本は運営者向け試聴ページ`user_test/kp3v_vote_evidence_01/index.html`へ(c commit) | `er104:vote_check_from_audit` |
| P-11 | SSOT更新範囲(§16-6) | c commit |
| P-12 | test追加(§16-4) | `er104_kp_three_asr_vote_01_test_02.py`、`er104_kp_vote_wiring_test_01.py` |

## 16-2 P-01 本番adapter経路での保存音声再評価(0円)
`er104_stored_audio_reeval_02.py`: 保存Primary/Secondary転写を本番adapter(`vote_required=True`)へ通し、Whisperは割れたときだけ既定のローカルsmall(実経路)。結果=`stored_audio_reeval_02.json`。受入条件=旧script結果(`stored_audio_reeval_01.json`)との84行一致、問題音声21件の新規誤PASS 0、判定変化4件(think up/blurt/cause a stir#3/#4)。

## 16-3 配線点(実装済み、コミット(b))
`er078_asr_unified_judge_01.py`(`vote_required`/`whisper_fn`/`finish_vote`、`NG_WHISPER_UNAVAILABLE`、`TECHNICAL_STOP_STATES`)、`er078_asr_unified_attempt_ctx_01.py`、`er006_secondary_asr_01.py`(adapter: whisper_fn供給・step`whisper_vote`・classification行別・`_tech_only`・Cascade OFF fail-closed)、`er003_v1_repro01_main_generate.py`(`vote_pass_required`・`_vote_circuit_open`)、X: `er019_family_x_audio_production_runner_01.py`(guard_whisper・reuse・assembly audit)/`er019_family_x_kp_en_k2_store_01.py`/`er019_family_x_validation_inheritance_01.py`(`kp_vote_required`・`TECHNICAL_STOP_WHISPER_UNAVAILABLE`)、Z: `er063_family_z_audio_01.py`、共通部品: `er104_kp_vote_reuse_01.py`(旧er096後継)、判定核: `er104_kp_three_asr_vote_01.py`。

## 16-4 test(P-12全項目)
真理値表6行+呼出回数(judge・adapter・strict層)/行別classification/Whisperの長さ・AMBIGUOUS/空転写=NG票/例外・timeout・circuit(閾値1)/preflight失敗でTTS前停止(X・Z)/Azure障害でWhisper不呼出(2/3降格なし)/旧dual_v1・asr_judgement.dual読取のみ/再利用6点が本番adapterを通る/AST(`vote_pass_required`はKP英語6点のみ・Trueリテラル無し・旧識別子撤去・er096 Production import 0・er104 import許可集合)/rollback(KP_THREE_ASR_VOTE_ENABLED=False→旧経路バイト同一、TIEBREAK=False→両方PASS必須と一致)/judgeとdecideの全組合せ一致。

## 16-5 P-07 解釈の明記(ユーザー承認依頼ではない)
(a) Azure障害(例外・空転写・circuit open)時は**技術STOP維持**(Primary+Whisperの2/3へ降格しない)。ユーザー§2の表は「Azure NG」の行のみを定義しており、障害は定義外=現行承認(UDR #139の「Azure障害でPrimary単独PASSへ降格しない」)を踏襲。
(b) `NG_PROTECTED_DISSENT`(反対票側に値DIFF/否定差があれば2/3を成立させない)は、**承認済みの値/否定ガード(P1)の対称適用**であり新基準ではない。既定ON(KPに数字はほぼ無く影響は極小)。
(c) WhisperにM1(multi-candidate)は適用しない(保守側)。ProductionのSecondary側のみ既存M1経路を維持。
(d) 救済PASS(Azure転写に依存した非ラテン救済・Tier3・cs_equivalence)はPrimary **NG票**として数える。

## 16-6 旧ルール・旧識別子の整理(撤去/書換/残置)
撤去: `NG_DUAL_PRIMARY_NOT_PASS`(judge STATES・done変換・test)、`dual_required`(AttemptCtx/ctx/adapter)、`dual_pass_required`(kwarg)、`_dual_circuit_open`、`kp_dual_*`の関数名(`kp_vote_*`へ)、`KP_EN_PHRASE_DUAL_REQUIRED`、`+dual1`、`secondary_dual`、`er096_kp_dual_pass_01_wiring_test_01.py`(`er104_kp_vote_wiring_test_01.py`へ3-ASR版として移設)。残置(意図的): 保存容器名`kp_dual_check`/telemetry名(P-05)、`er096_kp_dual_pass_01.py`(履歴script。`evaluate_dual`は実行不可)、`er096_kp_dual_runtime_evidence_01.py`/`er099`(履歴)、`docs/research/PROPER-NOUN-.../onoff_differential_02.py`(PNAP履歴script)。
