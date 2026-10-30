# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01 DESIGN_01(設計+API 0 Trial。Production未配線・未承認)

ユーザー原文: `docs/pm/delegation_log/2026-10-30_FX4-LATTER-APPROVAL-AND-FLAP-T-TRIAL_USER.md`(origin/main `43c5144f7`で反映を確認、§3-§7を参照)。
現状・数値の根拠=`CURRENT_STATE_01.md`。Trial実装=`tools/`(Trial専用・Production経路からimportされない)。

## 1. 問題と線引き(11-8)
- 問題: 米音flap-T(母音間の/t/が[ɾ]化しd綴り語と同音になる)で、TTSが正しく`latter`を発話してもASRは文脈なしだと`ladder`を選ぶ。FX4⑨は4 TTS attempt x ASR2系統=8判定すべて『Ladder』→STOPPED→HR。既存の同音救済はCMU音素列の完全一致が根拠で、`L AE1 T ER0`≠`L AE1 D ER0`のため届かない(CURRENT_STATE a-2)。
- 範囲内(本委任): 設計、Trial専用実装(`tools/flapt_equivalence_proto_01.py`)、既存記録の分析(API 0)。
- 範囲外: Production配線、既存Gate緩和、閾値・Prompt・辞書の変更、ASR収束を根拠にする救済。
- 位置付け: 新しい救済仕様(Production挙動の意味的変更)=**ユーザー正式採用が必要**。Trial成功=VALIDATED止まり(PRODUCTION_WIREDではない)。

## 2. 不変条件(全案共通。破れば不採用)
- I-1 **文字列t↔d置換は禁止**。根拠は(CMU音素列 + flap環境規則)に限る。ten/den・time/dimeを救済しない。
- I-2 **母音は音素列で完全一致**(強勢2値化後)。差が許されるのはT↔Dの入替のみ。
- I-3 **全てのt/d差位置がflap環境**(直前=強勢母音、直後=無強勢母音、直前がR/子音でない、直後が音節的n[AH0+N]でない)。語頭・語末・強勢T(attack)・クラスター(alter/alder)は不可。
- I-4 canonicalの強勢読みが複数ある語(putting=AH/UH)は救済しない(er008 strict_homophone_pair=P-01と同原則)。ASR語は代表(先頭)読みで比較。
- I-5 AY/AWを核とする語(writer/rider・title/tidal)は**自動救済しない**(REQUIRES_EXTRA_EVIDENCE=従来どおりNG)。CMUでは母音が同一(AY1)なので**辞書だけでは区別不能**で、実音声ではCanadian raising/母音長の差が残りうる。ユーザー指示『母音差が残る場合は子音同等性のみでPASSしない』を、辞書で判別できない領域は保守側(NG維持=HR)に倒すことで満たす。
- I-6 差分は『1:1語置換のみ』。挿入・欠落・1語対2語は対象外(多語同音はPNMH層の担当)。CMU未登録語は判定不能=非救済(fail-closed)。例外・判定不能は全て『同値ではない』。
- I-7 **ASR収束は根拠にしない**(『全ASRがLadder』は救済根拠に使わない。CURRENT_SPEC.md:1864)。独立ASRの一致を証拠として数えない。
- I-8 **Voice適用境界**(4節): flap実証済みVoiceのみ。既定=全Voice不適用(fail-closed)。
- I-9 既存閾値・Gate・retry/fallback上限・最終ANDゲートは緩めない。救済は『Primary/各票のPASS判定を1つ増やす』だけで、値/否定ガードは従来どおり通す(`APPROVED_EQUIVALENCE_BASES`へは入れない=er109のORTHO_BASISと同じ扱い。`er078_asr_unified_judge_01.py:73-77`)。
- I-10 救済は**必ずwarningラベル付き**(`FLAP_T_EQUIVALENT`)=PASS_WITH_WARNING→事後試聴リスト。救済根拠(canonical/ASR語・音素列・環境・Voice)を内部ログに残す。

## 3. 方式候補
### M1(推奨): CMU音素 + Flap環境規則(API 0)
- 判定: 1:1語置換差ごとに、両語の音素列が同長で、差のある全位置が{T,D}の入替かつ両語とも flap環境(I-3)、直前母音がAY/AW以外(I-5)、canonical単一読み(I-4)。flap規則適用後(flap環境のT/DをDXに正規化)に**完全一致**。Trial実装=`tools/flapt_equivalence_proto_01.py::judge_pair/evaluate`。
- 組込位置(既存機構優先): er109と同型の**第3層**。er109は『run scope(X/Y/Z)+単一flag読取関数+UKUS第2層が親flag従属で併設』という前例を持つ(`er109_xz_scope_01.py:92/100/149`)。呼出点は既に3箇所(Primary `er006_secondary_asr_01.py:1135`、Secondary :1207、票 `er104_kp_three_asr_vote_01.py:246`)あり、`decision()`窓口にFlap層を足せば**全ASR票(OpenAI/Azure/Whisper)が同じ基準で救済可否を判定**でき、新規call siteが増えない。
  - 実装形態は2択(委任_02以降でFableが選択): (A)er109内に第3層追加(UKUS同型)/(B)新規module+`decision()`に1呼出追加(er109本体は無変更=11-7(2)『既存の直接編集不可』に最も素直)。**推奨=(B)**。いずれも既定OFF・単一flag読取関数・env/引数/設定dictからONにできない・DefaultOffIsolation test(11-7の5条件)が必要。
  - 要精査(未調査、委任_02): er109救済音声のStore再利用ガード(`er109_xz_scope_01.py:36-37` OUT_OF_SCOPE_BLOCK_REASON)と同型のFlap用ガード、`ortho_contributed`相当の監査、`make_voter`のlabel判定(`er104:287`)の拡張。
- 費用: **API 0**(CMU辞書のみ)。追加ASR/LLM呼出なし。
- 偽救済リスク: 救済面は有界。CMU全体(alpha・3文字以上)から機械列挙した救済ペアは**431**(+AY/AW 73が自動救済外)、内訳は人名・固有語が多く、否定語は0(`rescue_surface_01.json`)。実害の型=『TTSが本当に別語を発話したのにflap同音として通す』だが、その場合もflap環境では音響的にほぼ同一(学習者が聞く音は同じ)。crisp-tで発話するVoiceが`ladder`を誤発話した場合は検知不能→**Voice適用境界(4節)で限定**。
- 救済漏れ: putting型(複数読み)・複合語の非flap・AY/AW核・R直後(party/hardy)・音節的n(eaten/Eden)・語境界をまたぐflap(what a→wad a)はv1で非救済。

### M2: M1 + LLM二重確認(別系列)
- M1がRESCUE/REQUIRES_EXTRA_EVIDENCEと判定した対のみ、別系列LLMに『General American話者が文脈なしで発話した場合に同音か』を確認。
- 利点: AY/AW等の曖昧領域を追加判断できる可能性。欠点: LLMは音声を聞かず辞書知識の再生に過ぎない(M1と独立な証拠にならない)、再現性なし、費用>0(1回¥0.05未満見込みだが救済候補ごと)、CURRENT_SPEC『LLM推測による代替合格禁止』(KP CMU Gate節 CURRENT_SPEC.md:2023)の趣旨と衝突。**非推奨**。AY/AW領域は『音声を実測する』(M2'=下記)方が筋。
- M2'(任意・Phase 2): AY/AW核の語対だけ、実音声のASR再現性(同一wavを複数ASR/温度で書き起こしてwriter/riderが割れるか)を実測し、『ASRが常に同じ語に倒れる=区別不能』と実証できた範囲に限り警告付き救済を提案。区別できる音声が多いなら非救済のまま。

### M3(不採用): ASR側の操作で期待語に寄せる
- Azure phrase list/OpenAI promptへcanonicalを渡して転写を`latter`に寄せる案。期待語を教えて期待語を得るため**循環(独立証拠でない)**。既存でも『Azure PL有は投票から除外』方針(`docs/pm/delegation_log/..._PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01_委任_02.md` R-09)。I-7に反するため不採用。
- 『片系統が期待語を出していれば…』型の系統間相互一致は既存多数決(`er104:160 tally`)が既に担う。Flap事象では**全系統がd綴り**なので相互一致は救済に寄与しない。ただし整合条件として採用: 票ごとに判定するため、ある系統が第三の語(letter等)を出せばその票はNG(I-1/I-2で自然に成立)。

## 4. Voice別適用(米音Voiceのみ)
- 設定上は全EN TTSが`language_code="en-us"`(`er002_gemini_client.py:62-70`)で非米音Voiceの設定は無い。ただし**設定≠実音声**(Voice名は言語/アクセントと独立。CURRENT_STATE b-1)。
- 判定法: (1)`confirmed_voices`(許可リスト)に載ったVoiceのみ適用。既定=空。Voice不明(attempt_ctxに`voice`が無い/None)も不適用(`tools/flapt_equivalence_proto_01.py::voice_applicable`、test済)。(2)許可リストへの追加根拠=**flap実証**: ①保存記録でt綴りcanonicalがd綴りで全ASR転写された実例がある(現在 Aoede・Zephyr・Schedarの3種)、または②Voice probe(Phase 2)で対象語のd綴り転写が観測された。『flapの記録がない』は不適用のまま(未確認を米音と決めつけない)。
- wiring要件(Production化の際): `attempt_ctx`へ`voice`(effective_voice、`er002_gemini_client.py:54`)を加算で渡す。voice不明は不適用。許可リストはrunner側ではなく単一のSSOT file(sha付き、audit記録)に置く。
- 英国英語等の非適用Voice: EN本番経路に設定として存在しない(確認済み)。将来追加する場合は許可リストに載せない限り自動的に不適用。

## 5. テストケース表(`tools/flapt_equivalence_proto_01_test_01.py`、36 PASS。実行結果=`case_results_01.json`)
期待=設計判断。反例はNO_RESCUE/NOT_APPLICABLEでNG維持を期待。

| ID | canonical | ASR | 期待 | 実測 | 理由 |
|---|---|---|---|---|---|
| P01 | latter | Ladder | RESCUE | RESCUE | 実データFX4⑨ |
| P02 | metal | medal | RESCUE | RESCUE | |
| P03 | betting | bedding | RESCUE | RESCUE | |
| P04 | atom | Adam | RESCUE | RESCUE | |
| P05 | waiting | wading | RESCUE | RESCUE | |
| P06 | coating | coding | RESCUE | RESCUE | |
| P07 | Bertie | Birdie | RESCUE | RESCUE | 実データFZ |
| P08 | The latter option is cheaper. | The ladder option is cheaper. | RESCUE | RESCUE | 文脈つき |
| P09 | ladder | latter | RESCUE | RESCUE | 逆方向(対称) |
| P10-12 | bitter/bidder, tutor/Tudor, rated/raided | | RESCUE | RESCUE | |
| N01 | ten | den | NO | NO | 語頭(flapなし) |
| N02 | time | dime | NO | NO | 語頭 |
| N03 | putting | pudding | NO | NO | canonical 2読み(AH/UH)=I-4 |
| N04 | heartbeat | heartbead | NO | NO | 非語=CMU未登録(複合語のT+Bは非flap) |
| N05 | eaten | Eden | NO | NO | 音節的n(声門閉鎖化) |
| N06 | water | wader | NO | NO | 母音差(AO/EY) |
| N07 | letter | leader | NO | NO | 母音差(EH/IY) |
| N08 | battle | paddle | NO | NO | t/d以外の子音差(B/P) |
| N09 | party | pardy | NO | NO | R直後 |
| N10 | attack | Adak | NO | NO | T直前が無強勢母音(aspirated) |
| N11 | feed | feet | NO | NO | 語末 |
| N12 | latter | later | NO | NO | 別語(EY1) |
| N13/N14 | 挿入あり/別語差あり | | NA/NO | NA/NO | 1:1置換のみ |
| N15 | total | toad all | NA | NA | 1語対2語は対象外 |
| N16 | metal | mettle | NO | NO | 音素同一=既存homophone層の担当(二重救済防止) |
| N17 | alter | alder | NO | NO | T/Dの前がL(子音) |
| N18 | Burton | burden | NO | NO | 音節的n |
| X01 | writer | rider | REQUIRES_EXTRA_EVIDENCE | 同左 | AY核。辞書は母音同一=**辞書だけでは区別不能**。自動救済せずNG維持(I-5) |
| X02 | title | tidal | REQUIRES_EXTRA_EVIDENCE | 同左 | 実データ(AKB48 b1b)・AY核 |
| X03 | Wright | ride | NO | NO | 語末 |
| U01 | Zorbo | Zorpo | NO | NO | CMU未登録=fail-closed |
| V1 | voice_applicable | | 既定/None/未確認Voice=False | 同左 | fail-closed |

未収載(ご指定項目の扱い): `heartbeat`等の複合語=N04(非語綴りで代用、実語の複合語は『非flap位置のT』のため差が出ない)。『語頭語末t・強勢後でないケース・t/d以外の子音差』=N01/02/10/11/08/12。
**反例が示す設計上の注意**: (1)I-4でputting/pudding型の実在ペアを意図的に取りこぼす(保守側の代償)。(2)writer/riderはM1の『限界の自己申告』であり、解決は音声実測(M2')か人の耳(HR)に委ねる。

## 6. Trial手順
- **Phase 1(完了・API 0)**: 規則実装+36ケース+実データ再判定+辞書全体の救済面列挙。結果=CURRENT_STATE (c)・`rescue_surface_01.json`・`case_results_01.json`。実データの正解率: 救済13行(7 distinct)はlatter→ladder(FX4⑨、X)とBertie→Birdie(FZ、Z)のみで、いずれもcanonicalを意図どおり発話した音声(Birdie側は`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_01.md:17`が『音声は意図どおり』と記録)。誤救済に当たる行は0(ground truthは当該記録と聴取による既存判断に依存し、**全件の独立試聴は未実施**)。
- **Phase 2(任意・有料・Cap案≤¥30、実行は別承認範囲確認)**: Voice probe。11 Voice x 12語(flap正例8+writer/rider/title/tidal)x1 attempt=132 clip(+Std 6%減速版を3 Voiceで追加確認、追加費用はごく小)。単価根拠=`er005_output/cost_baseline_01/pricing_snapshot.json`(2.5-pro TTS音声出力 $20/1Mtok=約¥0.08/秒[25tok/s]、flash-lite $6/1Mtok=約¥0.024/秒、gpt-4o-mini-transcribe、Azure $1/hour=`er078_asr_unified_judge_01.py` AZURE_USD_PER_HOUR)。概算(clip 1.2秒、TTS+OpenAI+Azure各1回): flash-lite経路 約¥12、2.5-pro経路 約¥21(**実行前に確定**、Cap案≤¥30に収まる見込み)。測定: Voiceごとの正例d綴り出現率(許可リスト判定)、AY/AW語の割れ方(M2'の要否)。出力は`docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/`既存構造内。
- **Phase 3(API 0、Production配線の前提)**: ⑨Adv `vocab_extra_english`のHR記録を、既存の再判定tool(`er109_hr_lock_rejudge_01.py`の方式)でoffline再判定し、Flap層ON/OFFの差を確認(既存attemptのrecordのみ・Gate緩和なし)。
- 11-7限定例外に該当する将来のProduction配線: flag名と『未承認・既定OFF』を`OPEN_ITEMS.md`に記録。本委任はflag実装を持たないので未発生。

## 7. 評価指標
| 観点 | 指標 | 現状(Phase 1) |
|---|---|---|
| 正しく救済 | 正例P01-P12のRESCUE率 | 12/12 |
| 誤救済 | 反例N/X/Uのうち RESCUE となった数 | 0/22(NG維持。うちAY/AWはREQUIRES_EXTRA_EVIDENCEで自動救済外) |
| 救済漏れ | 実在flap同音ペアのうち非救済となる型 | putting型・R直後・音節的n・AY/AW・語境界flap(5型。5節末) |
| 既存機構との整合 | 既存回帰(er006/er078/er104/er109 test)の差分 | 未実施(Production無変更のため本委任では不要。配線時に必須) |
| 再生成/HR削減 | 救済可能なSTOPPED/HR数、NG attempt数 | HR 1/131(X 1/17)、NG attempt 9(Z 4 seg) |
| 費用・単価 | 追加API | 0円(M1) |

## 8. 後段Gate・再生成との整合(配線時の確認項目)
- ASR長さ上限: 影響なし(同長)。Repetition QA方式A: flap語を含む3語以上spanが台本で意図的に繰り返される場合のみ偽NGの可能性(CURRENT_STATE a-3)。配線時にtestで固定。
- retry/fallback: Flap層は各attempt判定にPASSを1つ加えるだけで、回数上限・安全装置は不変。救済があれば初回で終わるためretry/fallback起動回数は減る方向のみ。
- HR Lock/approve_regenerate: 救済済みsegmentはHRに入らない。救済を取り消す/対象外Voiceに戻す場合は従来どおり再判定でNG→HR(`er011_human_review_lock_01.py:475`)。

## 9. Closeout判定基準(原文§4.3の受入条件7件との対応)
| §4.3 | 条件 | 本設計での充足方法 | Phase 1結果 |
|---|---|---|---|
| 1 | 典型的Flap-T同音を適切に救済 | M1 正例P01-P12 | 12/12 RESCUE |
| 2 | 単純なt/d置換による誤救済なし | I-1(文字列置換禁止)・I-3(flap環境)。ten/den・time/dime・語頭語末・クラスター | N01-N18 全てNG維持(0/18誤救済) |
| 3 | 音韻環境や母音差の不一致を無条件にPASSさせない | I-2(母音完全一致)・I-5(AY/AWは自動救済せずNG維持)・I-4(複数読み)・I-6(CMU未登録=fail-closed) | N06/N07/X01/X02/N03/U01 |
| 4 | 既存ASR Gate・同音救済・retry・fallbackと整合 | I-9: 各票のPASSを1つ増やすだけ。approved_equivalence非編入・最終ANDゲート不変・回数上限不変。er109同型の窓口(`decision()`)で新規call site最小 | 設計(整合の回帰testは配線時に必須) |
| 5 | 承認済み品質基準を引き下げない | 閾値・Gate・Prompt・辞書の変更0。根拠を音韻規則に限定し、ASR収束を根拠にしない(I-7)。救済は必ずwarning付き(I-10) | 変更0 |
| 6 | Family・Voice・レベルごとの適用境界が明確 | Family=X/Y/Z run scopeのみ(A/B/C対象外。er109 `APPROVED_SCOPES`同型)。Voice=許可リスト(4節、既定不適用)。レベル=Std/Advとも同一規則(Voice設定はレベル差なし。Stdの6%減速[CURRENT_SPEC.md:1620]でflapが保たれるかをPhase 2で確認) | 4節 |
| 7 | 再生成削減効果と量産単価への影響を評価 | CURRENT_STATE (c)の実データ件数。単価増0(API 0) | HR 1/131(X 1/17)・NG attempt 9(Z) |

判定: 7条件を満たし、ユーザー試聴/正式採用判断を経るまで`VALIDATED`止まり(原文§5)。PRODUCTION_WIREDではない。再Trialは見込みのある変更(Phase 2の実測でAY/AW方針を見直す等)がある場合のみ行い、同一方式の反復はしない(原文§4.2)。

## 10. 実データの取り込み方法
- 既存tool `tools/flapt_stored_census_01.py` が全`tts_generation_results`(再帰走査)とHR queueを読み取り専用で取り込む(Production telemetry追記はno-op化)。新規run後は同scriptを再実行するだけで拡張できる。
- 実音声のASR NG(wavの再ASR)が必要な場合のみPhase 2/3の有料または再判定を用いる。
