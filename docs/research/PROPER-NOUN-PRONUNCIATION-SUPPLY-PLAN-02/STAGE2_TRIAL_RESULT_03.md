# STAGE2_TRIAL_RESULT_03: 固有名詞発音 Stage 2 Trial 第3巡(TTS入力側の読み制御)結果(ユーザー§7の順)

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_09 / 2026-10-22 / 到達Status: `TRIAL_R3_DONE_PENDING_FABLE`(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`はFable判定)。Production・正式Ledger・HR queue・Master Audio Store・Validator・Prompt・モデル構成 無変更。
設計=`STAGE2_TRIAL_DESIGN_03.md`。証跡=`er100_output/pnps_stage2_trial_01/r3/`(`agg.json` `gen.json` `gen_b.json` `paid_calls.jsonl`)。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/pnps_stage2_hr7_listen_03/index.html (Gate 7: 公開Pagesで98/98再生、console error 0、HTTP>=400 0、`r3/gate7_play_verify.json`)。

## 1. 結論: Human Reviewを何件削減できたか
**TTS入力側の読み制御は、語を選べば効く。ただし効く語は7語中Khaiteのみ。第2巡HRプロキシ25(現行TTS take1)に対し、実測で3件(12%)・同一方式を他の同系segmentへ当てはめた推定で9件(36%)。40%には届かない(A階層のみ供給なら0件)。**

| 区分 | 母数 | 読み制御後PASS(現行判定=置換後テキストで比較、Reicher方式) | 備考 |
|---|---|---|---|
| 第2巡HRプロキシ25のうち実際に再生成して測れた対象語segment | 6(Khaite s12/s13/s16、Meink s02/s03、Altuzarra+Toteme s17) | **3**(Khaite 3/3、いずれも2 take中2/2) | Meink 0/2、s17は供給不可のTotemeが残り0/1 |
| 同上の推定(Khaite同系の未再生成6segment[s08/s14/s15/s20/s21/s22]へ当てはめ) | 25 | **9**(36%) | **推定**。Khaiteは4つの異なる本文×2 take=8/8がkate(4エンジン全一致)。95%片側下限は約69%/音声(ルール・オブ・スリー)。標本は小さい |
| A階層のみ供給(Meink) | 25 | **0**(0%) | Meinkは綴り置換3方式・発音ヒントとも制御不能(後述) |
| A+B階層供給(Khaite・Meink・Altuzarra) | 25 | 実測3/推定9 | Altuzarraは0(後述) |
| 供給不可(Toteme・Zabelina・Melos・Canele) | 11(HR25のうち語別割当) | 0 | ESTIMATED/取得なし/弱い根拠のため供給せず、削減0 |
- 7語全体のHR削減率: 実測 3/25=12%、推定 9/25=36%。判定側の改善だけの第2巡(2/37、5%)よりは高いが、効果基準40%は未達。
- HR25の語別内訳: Khaite 9、Meink 2、Altuzarra+Toteme同居 3、その他(Toteme/Zabelina/Canele/Melos) 11。

## 2. 語別・階層別・arm別(原綴り比較=現行プロキシ/N5_UND、置換後比較=Reicher方式)
各行は対象語がその音声で「機械判定上、誤発音とされなかった」本数。nは音声本数(2 take×segment)。
| 語(階層) | arm | n | 原綴り比較: 現行プロキシPASS | 原綴り比較: N5 PASS | 置換後比較PASS(完全一致/音素一致) | segment全体N5 PASS |
|---|---|---|---|---|---|---|
| Khaite(B) | N 無供給(r2再利用) | 8 | 1 | 2 | - | - |
| Khaite(B) | **R 綴り置換→Kate** | 8 | 0(原綴り比較は不可) | **8** | **8/8 / 8/8** | **8** |
| Khaite(B) | H 発音ヒント"kate" | 8 | 2 | 2 | - | 2 |
| Meink(A) | N | 3 | 1 | 0 | - | - |
| Meink(A) | R→Meenk | 4 | 1 | 0 | 0 / 0 | 0 |
| Meink(A) | R2→Meank, Meenck(追加phase) | 4 | 1 | 0 | 0 / 0 | 0 |
| Meink(A) | H "meenk" | 4 | 1 | 0 | - | 0 |
| Altuzarra(B) | N(alt_short含む) | 3 | 3 | 0 | - | - |
| Altuzarra(B) | R→Altoozahra | 4 | 4 | 0 | 0 / 0 | 0(s17はToteme残) |
| Altuzarra(B) | R2→Ahl-too-ZAH-rah, Altoozarra | 4 | 4 | 0 | 0 / 0 | 0 |
| Altuzarra(B) | H "ahl-too-ZAH-rah" | 4 | 4 | 0 | - | 0 |
- **Khaite**: 綴り置換(Kate)は4本文×2 take=8本すべてで4エンジン(OpenAI/Azure/Whisper small/medium)が「kate」と書き起こした。第2巡の無供給では同じ本文で「kite」「kites」「kayu」等に割れていた。発音ヒント注入(styleへ"kate"を追記)は8本中2本のみ(多くは「kite」「kites」「khaite」のまま)で、**TTSはstyle内の発音ヒントよりも本文の綴りに強く従う**。
- **Meink**: 綴り置換3方式(Meenk/Meank/Meenck)も発音ヒントも制御不能(「mink」「meeks」「menink」「munich」等)。TTSはMeinkを「MEENK」に読めない。A階層(本人Wikipedia)の供給でも効果0。
- **Altuzarra**: 現行プロキシは無供給でも3/3、置換でも4/4でPASS(PrimaryがAltuzarraと綴るため)。Azure・Whisperは「altazara」「altezara」等で返し続け、N5では全armでNG。綴り置換・ヒント・取得した綴りそのまま(Ahl-too-ZAH-rah)のいずれでも変化なし。**TTSは「too」の母音を弱化して読む傾向が変わらない**(その読みが誤りか許容かは耳での確認が要る)。
- 供給不可語は生成していない(供給しない方針)。

## 3. 誤読対照(誤った読みを供給した場合)—方式の安全性は供給発音の正しさに全面依存
| 語 | arm | 供給した誤り | 4エンジンの結果 | 置換後比較 | 原綴り比較(N5) |
|---|---|---|---|---|---|
| Meink | R | Mink | 全員"mink" | **PASS(完全一致4/4)** | NG |
| Khaite | R | Kite | Primary"kate spade"/Azure"kites"/Whisper"kite"x2 | Primary/Azure基準ではno(ASR誤記のため)。Whisper2本は一致(4中2) | NG |
| Altuzarra | R | Altuzairah | altuzarra/altizera/altezera/altazera | no(TTSは誤り通りには読まず) | NG |
| Khaite/Meink/Altuzarra | H | kite/mink/al-tuh-ZAIR-ah | 本文は原綴りのまま | (置換なし) | 全てNG(原綴り比較はヒントに自己一致しない) |
- 事実: **綴り置換+置換後テキストで比較する方式(Reicher方式)は、誤った読みを供給するとそれを正解としてPASSにしてしまう**(Meink→Minkで実証)。誤読対照のPASS化は3語中1語(ASR誤記に依存する偶然の側面もあり、安全の保証にはならない)。発音ヒント注入(H)は本文が原綴りのまま判定できるため自己一致は起きないが、効果も弱い(Khaite 2/8)。
- 現行プロキシ(Primary単独の綴り一致)の弱さの再確認: Meink H(wrong供給"mink")でPrimaryが"meink"と返し現行プロキシはPASSになる(第2巡S2R-06と同じ型)。Altuzarra全armでPrimaryは常にAltuzarraと綴る。
- **A階層とB階層のリスク差**(供給元別):
| 供給元 | 本巡の語 | 誤供給リスク | この方式での影響 |
|---|---|---|---|
| A: 本人記事・公式(引用実在確認済み) | Meink(Wikipedia、IPA+MEENKの併記) | 低(本人/百科の記述、二重表記で相互確認) | 置換自体は制御不能(Meink)。供給できても効果が出ない語がある |
| B: 報道/ファッション媒体1〜5件一致 | Khaite(Nylon 1件)、Altuzarra(5件一致) | 中(1件引用=Khaiteは単一出所。表記ゆれ・誤記の可能性は残る) | Khaiteは制御が効く(8/8)が、Nylon単独が誤っていた場合、全記事の読みと比較対象が誤りで固定される(Reicher方式は誤りを検出しない) |
| ESTIMATED/取得なし(Toteme/Zabelina/Melos) | 供給しない | 高(計画v4-5で禁止) | 削減0 |

## 4. 供給不可語の扱い
Toteme・Zabelina・Melos=取得なしで供給せず(ESTIMATED供給禁止 v4-5)。Canelé=辞書サイト1件のみ(弱い)で供給せず。いずれもHR維持(削減0)。第2巡で受理集合が空(Toteme・Melos)であることとTTS実誤読(totem・mello)の両方が残る。

## 5. 初回で効果が限定的だった原因・Opus指摘・改善内容・再Trial結果
- 第2巡の原因: HR主因=TTS実誤読(18/25)、判定側天井24%。→ Opus OF-PNPS-S2R-10(1)=TTS入力側の読み制御を本巡でTrial。
- 本巡の改善内容: arm R(綴り置換、Reicher方式踏襲)・arm H(styleの発音ヒント、既存`er006_pronunciation_tts_injection_01`の形式を読取のみ利用)。置換後/原綴りの両方で判定。
- 再Trial結果: R armでKhaiteのHRは実測3/3→PASS(推定9/25=36%)。Meink・Altuzarraは制御不能/判定NG、他4語は供給不可。H armは効果弱(2/8)。方式全体の効果基準(40%)は未達。
- Opus指摘との対応: S2R-10(1)実施。注意点=制御は「綴りに追従する」前提で効く。MeinkのようにTTSが「Meenk」を「Mink」に読む語は綴り置換でも制御できない。

## 6. 使用総額・量産単価への影響
- 本巡 **JPY49.85**(`r3/paid_calls.jsonl`、台帳のkind名`r2_*`は流用コードの名残): TTS 30.71(48呼出)、OpenAI ASR 5.07(48呼出、上限見積)、Azure STT 14.07(48呼出)。LLM 0。為替USD_JPY=160。**Guardrail60内(残10.15)**。
- 構成: 第1phase 40音声(JPY43.37)+追加phase(Meink/Altuzarra別綴りR2、8音声、JPY6.48)。追加phaseは第1phaseの結果(Meink・Altuzarra制御不能)を受けた同一設計の拡張で、Guardrail内。
- Trial累計Cap300: 79.09+49.85=**128.94**(残171.06)。当日(JST 2026-10-22): 委任文の既使用約749.6+49.85=**約799.5/1,000**(残約200.5)。
- 量産単価への影響: 読み制御は既存の置換辞書(`tts_safe_name_pronunciation_en`、`er003_v1_n3_01_tts_generate.py:990-999`)の拡張であり**追加API呼出0**(置換は文字列処理のみ)。HRが減ればHR起票・再生成retryが減るので量産単価は下がる方向だが、効果は本巡では語依存(Khaiteのみ)。ただしLedger→置換辞書への自動供給は現時点で未実装(Ledgerのhintはstyle注入[H相当]に使われる設計であり、R相当の置換は辞書手編集)。実装する場合は新仕様(Production挙動の意味的変更)でユーザー承認が必要。

## 7. Fable独立評価、Trial終了Status
(Fable記入欄)到達Status=`TRIAL_R3_DONE_PENDING_FABLE`。

## 8. Production採用に必要なユーザー判断
(Fable記入欄)判断候補(Fable向け整理のみ): (a)B階層(報道/媒体1〜5件一致)の発音をTTS入力側へ供給してよいか(本巡のKhaite効果はB階層のみ)。(b)Ledgerの取得発音を置換辞書へ自動供給する仕様化(Production挙動変更)。(c)Reicher方式の置換後比較は誤供給をPASSにするため、供給元の品質ゲート(引用実在確認+複数出所)をどう置くか。いずれもProduction未採用・Trial結果のみ。

---
## 付録 限界の開示
(1) 標本が小さい(Khaite 4本文×2 take、Meink 2本文、Altuzarra 1本文+短文)。TTSは確率的で、Khaite 8/8でも将来の全再生成で一定とは限らない。(2) Khaite 9件の推定は「同系の別本文でもKate置換で同様に読まれる」という仮定。(3) 「PASS」は機械判定で、実際の発音の正否は耳での確認が必要(試聴ページ)。(4) ASR窓切り出し・OpenAI単価上限見積は第2巡と同じ。(5) Std生成後6%減速・Production再試行ループは再現していない。(6) 保護ファイル検査: 第1phase終了時、`er011_output/attempt_history.jsonl`が他process(`wiring_theme_*`のrun、`er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01.py`由来と推定)により+7行追記され、assertが停止した(先頭16,826行のsha256は生成前と一致=純追記、HR queue/manifest/reuse_telemetryは不変、当Trialは当該ファイルへ書込まない。`r3/protect_note.json`)。追加phaseでは保護対象を個別比較し全て不変(`protect_note_b.json`)。生成・台帳は検査前に保存済みで再実行していない。(7)Altuzarraの「altazara」読みが許容か誤りかは未確認(受理集合はahl-too-ZAH-rah=UW母音)。
