# TRIAL_SUMMARY_01: Family Y 統合Trial 成果物8項目の材料整理(FAMILY-Y-VOICES-DESIGN-01 委任_04+委任_05)

位置づけ: ユーザー原文(`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02.md` §5)の成果物8項目へ1対1で対応する節に、**既存資料へのパス・要点・数値を集約**したもの(新規評価はしていない)。Status=`TRIAL_PHASE3_DONE_PENDING_FABLE`(OPEN-463)。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。DEV/Trial経路のみ・X/Z Production変更0。

## 0. Fableが独立評価するための読取対象(先頭に列挙)
基準dir: `er110_output/family_y_trial_01/`(以下「Y」)。
| 対象 | R2g(主候補) | R0g(比較候補) | 備考 |
|---|---|---|---|
| 日本語完成稿(Leakage Gate通過後) | `Y/school_phone_ban/y_writer/gate_r2/article_final.md` | `Y/school_phone_ban/y_writer/gate_r0/article_final.md` | R1g=`gate_r1/article_final.md`。Gate前のraw=`y_writer/{r0,r1,r2}/*_final.md` |
| 英語 Advanced | `Y/school_phone_ban/english_r2/b1b/article.md` | `Y/school_phone_ban/english_r0/b1b/article.md` | 契約=`b1b/contract.json` |
| 英語 Standard | `Y/school_phone_ban/english_r2/a2/article.md` | `Y/school_phone_ban/english_r0/a2/article.md` | S2版=`english_r2/a2_s2/article.md`(参考) |
| 日本語タイトル / Preview・Comment1〜3・KP(Std/Adv) | `english_r2/japanese_title.json`、`english_r2/scaffold_{b1b,a2}/` | `english_r0/…` | Comment 4なし |
| Voice Card | `Y/school_phone_ban/y_cast/voice_cards.json`(要約=`VOICE_CARDS_01.md`) | 同左 | 3人共通 |
| 音声(個別wav・最終Assembly) | `Y/audio/r2/{a2,b1b}/narration/`、`Y/audio/r2/a2/assembled*/` | `Y/audio/r0/{a2,b1b}/narration/`、`Y/audio/r0/{a2,b1b}/assembled*/` | R2g Advはassembled未作成(§5) |
| 試聴ページ(公開) | https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_01/index.html | | 実再生: `Y/audio/play_verify.json` |

## 1. R0/R1/R2の日本語原稿比較と品質評価
- 資料: `WRITER_COMPARISON_01.md`(全文・比較表・原稿全文)。
- 要点(事実): 費用 R0 9.06/R1 4.83/R2 5.73円。本文字数(raw)907/923/911。5段落契約・話者取り違え確認は3段ともPASS、再生成0。Voice段落の数字0、リードの「取材」系表現0、「です・ます」0。1回目Leakage flag(raw)= R0 6項目/R1 6項目/R2 7項目(いずれも背景factを持つ人物1・2のみ、人物3は全段0)。Gate後は3段ともPASS(判定2回・局所書き換え1回)。
- 所見(Sonnetの読み、事実と区別): 構造とLeakage耐性はR0で確立、R1/R2は壊さず導入・比喩・独白の面白さを上げた(R2>R1>R0)。OPEN-217/218の悪化は再現せず(n=1)。人物間の語り口の質感の同質性、R2での言い回し共有(「手が止まる」)は未改善。R1+R2の追加費用は+10.56円/セット。
- 音声での追加材料: Phase 3でR2gとR0gを音声化(R1gは原稿比較のみ)。R0gは全レベル完成。R2gはStd完成・Advは人物2が自動検査で停止(§5)。

## 2. 3人のVoice Cardと立場・人物像
- 資料: `VOICE_CARDS_01.md`、`Y/school_phone_ban/y_cast/{cast_candidates.json,voice_cards.json}`。
- 要点(事実): 人物1=Algieba・男性40代・中学校国語教員(軸=優先順位、背景F1)。人物2=Zephyr・女性50代・自治体の学校予算査定職員(軸=利害、背景F2)。人物3=Schedar・男性30代・働きながら定時制に通う成人の生徒(軸=価値観、背景なし)。賛否の機械配置なし、`not_my_point`は決定論生成、検証1回でPASS。Voice Cardの要約は試聴ページ冒頭に人物設定表として掲載。
- 所見: 3人の判断対象は別だが、Cardが「書類を前に手を止めて考える大人」の同型になりやすい(場面の同質性)。親・保護者の視点は入らなかった。

## 3. Standard/Advancedの英語本文
- 資料: `EN_COMPARISON_01.md`(英語全文・数値・評価)、パスは§0。
- 要点(事実): 5段落契約PASS(再生成0)。本文語数 Adv/Std = R0g 495/460、R1g 529/503、R2g 570/536。In One Line 34〜40語。Voice段落の数値表現0。Std英語S3監視Leakage 0件(3原稿)。RF flag Adv/Std = R0g 2/0・R1g 3/4・R2g 7/7(大半が人物の自己紹介文で台帳外の事実断定は0)。英語化費用 0.84〜1.85円。
- 所見: 人物の一人称・立場・迷いは英語でも保持。Stdは文が短くなり3人のリズムが近づく。最終パートが抽象的でA2学習者には重い。語数はXより+6〜24%。

## 4. Analytical Leakage Check・Acceptance Gate結果
- 資料: `LEAKAGE_CALIBRATION_01.md`(M7事前校正)、`WRITER_COMPARISON_01.md` §1・§3、`Y/school_phone_ban/y_writer/gate_{r0,r1,r2}/{gate_result.json,leak_check_*.json}`、英語側の監視=`english_*/s3_monitor_leakage.json`。
- 要点(事実): M7: 旧B 3V記事7件を日本語化して判定器を校正。**見逃し0**(NG 5/5検出)、判定器=gpt-6-luna(high、0.44円/回、Sol mediumの約1/7、検出同等)。Gate: 3原稿ともAcceptance Gate PASS(LEAKAGE_RESIDUAL_STOP 0、判定ノイズ0、書き換え後も一人称保持)。台帳外の事実創作0。
- 設計上の観測(事実): M1の「Voice段落に世界スコープ事実1件まで」と`leak_evidence_subject`が衝突し、事実を持つ人物は必ずflag→書き換えで台帳Factが完成稿から消える。対策弱化アーム(A0)は個性ある一文が出る一方、解説者化・台帳外の経験談の創作が出た。→ Gateが自由な発言を阻害した決定的証拠はなし。Voice背景fact 0件(A1)でVoice指摘0。
- 音声段階の関連(事実): 音声側のRepetition QAがR2g Adv 人物2で偽陽性により停止(AUDIO_QA_01.md §6)。Leakage Gateとは別の検査。

## 5. Standard/Advancedの音声試聴ページ
- 資料: `AUDIO_QA_01.md`(音声QA・Voice別実測・長さ・減速比較・停止の原因と選択肢)、`PHASE3_PLAN_01.md`(計画)。
- URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_01/index.html (候補A=R2g/候補B=R0g × Standard/Advanced切替、全編通し再生、パート別再生、全スクリプト、日本語元原稿、Key Phrase、人物設定表、Std「減速あり/人物の語りだけ減速なし」比較、「Trial(未採用)」表示)。
- 要点(事実): R0g Std/Adv・R2g Stdは全編完成(R0g Adv 292.2秒/Std 303.2秒、R2g Std 327.8秒)。**R2g Advは人物2のパートがRepetition QA偽陽性で停止し全編未作成**(ページではパート別音声と「人間確認待ち」表示で提示。承認後はAPI 0で再組立可)。ページ実再生検証=92/92音声再生OK・シーク全OK・タブ切替OK・console error 0・HTTP>=400 0(`Y/audio/play_verify.json`)。ページ標準検査(候補ごとのrender_standard_page相当)=PASS(`Y/audio/page_standard_check.json`)。
- 数値(事実): 固定Voice(Algieba/Zephyr/Schedar)で全呼出が指定Voice、Pro TTS不使用、HR Lock 1件(上記)、再生成はR0g Stdの3件のみ、PASS_WITH_WARNING 1件(R2g Std 人物3「wanna」)。男性2人のF0中央値差は1.9〜2.6半音(R0g Stdは差なし)、重心・話速で差(AUDIO_QA_01.md §4)。

## 6. 既存Family X基盤の継承状況とFamily Y固有の追加部分
- 資料: `INHERITANCE_STATUS_01.md`(T1〜T17、再Grep一覧、Y追加ファイル、隔離証拠)。Phase 3での更新:
  - T8(segment ID検査)・T9(TTS生成/Voice割当)・T10(Style profile)・T11(Assembly timeline)・T12(試聴ページ)は**Phase 3で実施**: alias ID方式で共有検証部品(resolve_narrative_role等)をそのまま使い、Style GateはY版で本文5segmentに拡張、Assemblyはtimeline builder新設、ページ新設。M4(同一run resume時のVoice照合)はY側ラッパー`voice_guard_cached`で実装(unit test済み、有料run後に追加したため有料runでは未実行)。
  - T13(scope限定機構へ"Y"追加)は**実施せず**: X/Z Production .py変更0の指示のため、er109/PNAPのscopeはYで非活性のまま(AUDIO_QA_01.md §2)。採用時の課題。
  - T15(STOP/RUN_LOCK): 有料run前に`tools/stop_scope_check_01.py`をrc=0で確認(`Y/audio/stop_check_a{0,1}.json`)。
- Y固有の追加ファイル(全て新規、Production file参照0): Phase 0〜2=`er110_family_y_text_trial_01*.py`、`er110_family_y_m7_*`。Phase 3=`er110_family_y_audio_trial_01.py`(runner)、`er110_family_y_audio_report_01.py`(音声QA集計)、`er110_family_y_audio_page_01.py`(ページ)、`er110_family_y_audio_play_verify_01.py`(実再生検証)、`er110_family_y_audio_trial_01_test_01.py`(offline test、15件)。
- 隔離(事実): Yを参照するProduction .pyは0(test固定)、環境変数/flag/CLI経路なし、tracked .pyの変更は新規er110ファイルとtest側allowlist2件のみ(Phase 0〜2)。Master Audio StoreはTrial名前空間(スナップショットコピー)。

## 7. 開発費・Trial費用・推定量産単価
- 資料: `COST_ESTIMATE_01.md`(Phase 0〜2の見積と実費)、`AUDIO_QA_01.md` §1(Phase 3実費)、`Y/audio/pre_run_estimate.json`(音声段の実行前見積と判断記録)。
- 費用(実測): Phase 0〜2 = 146.28円、Phase 3音声 = 29.10円(R2g 14.70/R0g 14.40)、**通算175.38円 / 上限250円(残74.62円)**。事前見積: Phase 3 40〜64円(2候補)に対し実費は約半分。
- 推定量産単価(**推定**。実測部品の合成で、Researchは今回のテーマ実績をそのまま使用):
  | 経路 | text | audio(scaffold+TTS/ASR) | 合計 | Xの直近実績(記事B 87.87円 = text 63.65 + audio 24.22)との差 |
  |---|---|---|---|---|
  | Y R2経路(R0→R1→R2→Gate、Std+Adv、音声含む) | 約87.0 | 約16.1(scaffold約1.4+14.70) | **約103円** | +約15円 |
  | Y R0経路(R0→Gate) | 約76.3 | 約15.8(scaffold約1.4+14.40) | **約92円** | +約4円 |
  内訳(text): Research 26.55・Ledger 22.98・B3 7.93・視点候補+Card 4.61・Writer(R2経路はR0 9.06+R1 4.83+R2 5.73、R0経路はR0のみ)・Gate(R2 2.19/R0 2.68)・英語化(R2g約1.4/R0g 0.84)・RF(1.80/1.68)。Researchが今回は49.5円(Xの記事Bは39.6円)と高く、これを記事Bと同水準にすると R2経路約93円・R0経路約82円。**70円目標はどの経路でも未達の見込み**で、主因はXと共通のResearch/Ledger(約40〜50円)。音声段はXより安い(14.4〜14.7円 vs X audio 24.2円)。
  Charter 3上の改善余地: Voice背景fact 0件化でGate書き換え回避(1.8〜2.4円)、Cast+CardをB3へ統合(−2〜−4円見込み)、R1/R2を使わずR0のみ(−10.6円。品質差はユーザー試聴で判断)、Gate判定器はLuna(0.44円/回)で足りる(M7)。
- 日次1,000円: 他案件分は`ACTIVE_TASK.md`参照(本委任の累計175.38円を含めて超過見込みなし)。

## 8. Fable独立評価とProduction採用に向けた残課題(材料)
Fable独立評価(未実施・本資料の範囲外): 日本語・英語の完成稿を§0のパスで読み、(a)3人の個性・一人称の自然さ・独立性 (b)R2gとR0gの差が追加費用に見合うか (c)Gateの強さ (d)音声の聞き分けしやすさ(ユーザー試聴の結果を含む)を判定し、`VALIDATED`可否を決める。
残課題(現状。委任_04の10項目を引継ぎ):
1. **Voice背景fact 0件化(M1との衝突)**: 設計変更(撤去)の扱い=Fable判断。音声段階でも新情報なし(人物の背景factは完成稿から消えたまま)。
2. **Std Voice partの減速**: 減速あり/なしの比較を無料で併置済み(§5、約2%/Voice part単体6%)。採否はユーザー試聴で判断。
3. **人物の語り口の質感の多様性・B3の米国研究2件偏り**: 未改善。音声では声の差(特に男性2人の差は小さい: AUDIO_QA_01.md §4)が頼り。
4. **Gateが書き換えで台帳Factを消す点**: 未改善(設計課題として記録のみ)。
5. **R1/R2のY採用(旧D4再開)**: ユーザー試聴後の判断(R2g Advは人間確認待ち)。
6. **Fable独立評価と`VALIDATED`判定**: 未実施。
7. **(新)R2g Adv 人物2のRepetition QA偽陽性(HR)**: 選択肢A〜D=AUDIO_QA_01.md §6。承認はユーザーの実聴が前提。Production側の偽陽性是正は別案件。
8. **(新)男性Voice 2人(Algieba/Schedar)の聞き分け**: 数値上はF0差が小さい(R0g Stdは差なし)。固定割当の変更は勝手に行っていない(ユーザー決定)。試聴結果次第でFable報告。
9. **(新)採用時に必要になる共有部品側の対応**: scope"Y"の追加(er109/PNAP)、`A2_SLOWDOWN_TARGET_SEGMENTS`の穴(OPEN-466、Yは自前確認で代替)、本文5segmentのID方式(alias→正式ID化)、parity testの正式化。いずれも採用判断後(Production変更に当たるため本Trialでは触れていない)。
10. **(新)Pageの運用**: 40MBの試聴音声をリポジトリで公開(通常のTrialページと同じ運用)。不要になれば削除可。
