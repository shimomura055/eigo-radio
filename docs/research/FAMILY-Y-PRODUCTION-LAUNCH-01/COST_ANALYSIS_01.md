# COST_ANALYSIS_01: Family Y 原価要因分析(E-3 SNS年齢制限 実測82.72円)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_06 C / 2026-10-25(JST) / **API 0・実費0円**(既存の記録`er121_output/family_y_production_01/sns_age_limit/run_01/cost_log.jsonl`と`er110_output/family_y_opinion_based_0*/`の既存記録のみを再集計。コードは変更していない)。
単価はpricing snapshot(`er019._load_pricing`、USD_JPY=160)。cached tokenは割引単価で再計算したため、`cost_by_stage.json`(cachedを割引しない過大側)と合計が0.05円ずれる(本書82.663円/正式記録82.7182円)。**この文書は事実の分解と候補の提示であり、仕様・設定は変更していない。品質判断を伴う案の採否はユーザー/Fable判断。**

## 1. 内訳(call別集計、E-3 146 call)

| 区分 | call | 円 | 構成比 |
|---|---:|---:|---:|
| text: Closing生成(Sol high, 1 call) | 1 | 21.986 | 26.6% |
| text: Voice UNMAPPED再生成(Sol high) | 3 | 14.919 | 18.0% |
| text: Voice初回生成(Sol high) | 3 | 12.972 | 15.7% |
| text: 人物紹介(Sol, 初回+再生成1) | 2 | 4.795 | 5.8% |
| text: Lead(Sol) | 1 | 2.457 | 3.0% |
| **Sol合計(text)** | 10 | **57.129** | **69.1%** |
| text: 出典付番 m1/m2(luna) | 6 | 1.081 | 1.3% |
| text: 出典付番 最終(記録のみ,luna) | 3 | 0.397 | 0.5% |
| text: Voice Gate / 構造タグ / Lead+紹介Gate / Closing Gate(luna) | 4 | 0.418 | 0.5% |
| translate / support / kp(gloss含む)(luna) | 24 | 4.336 | 5.2% |
| tts段のLLM(luna) | 2 | 0.043 | 0.1% |
| TTS生成(gemini flash-lite) | 41 | 14.682 | 17.8% |
| ASR primary(gpt-4o-mini-transcribe) | 49 | 4.073 | 4.9% |
| ASR secondary(azure) | 7 | 0.504 | 0.6% |
| **合計** | 146 | **82.663** | |

→ **Sol(High)の10 callが69%**。そのうち出力tokenの84〜92%が推論(reasoning)token(下表)。量産単価70円との差+12.72円は、UNMAPPED再生成(14.92円)単独で超える。

| call | 入力tok(cached) | 出力tok(うちreasoning) | 秒 | 円 |
|---|---|---|---:|---:|
| Closing生成 | 4,197(0) | 12,902(10,876) | 268.8 | 21.986 |
| Voice1 初回 / UNMAPPED再生成 | 3,444(0) / 3,581(0) | 1,425(1,201) / 2,583(2,366) | 29.5 / 51.6 | 3.382 / 5.279 |
| Voice2 初回 / 再生成 | 3,507(0) / 3,659(0) | 2,800(2,588) / 2,606(2,386) | 60.5 / 51.2 | 5.602 / 5.340 |
| Voice3 初回 / 再生成 | 3,695(0) / 3,848(0) | 1,753(1,531) / 1,918(1,703) | 35.7 / 33.7 | 3.987 / 4.300 |
| Lead | 769(0) | 1,382(1,266) | 22.6 | 2.457 |
| 人物紹介 初回 / 再生成 | 1,674(0) / 1,704(0) | 1,148(1,003) / 1,173(1,034) | 32.1 / 24.6 | 2.372 / 2.422 |

## 2. (1) Voice UNMAPPED再生成が3/3発火(14.92円)の原因

**結論: 実装の不具合ではない(検査は仕様どおり動いている)。発火が多いのは(a)付番LLM(luna)の判定ばらつきと(b)検査規則が付番の`is_event_claim`に強く依存する構造による。再生成の効果も低い。規則を変えれば原価が下がるが品質ガード(OF-Y6-07)の変更なので、ユーザー判断事項。**

事実(コード`er121_family_y_text_core_01.py:1315-1405`、E-3記録、DEV記録`er110_output/family_y_opinion_based_0{1,2,3}/*/state.json`):
1. 発火条件は「Voice内に1文でもUNMAPPED」(`n_unmapped>0`。1366-1390行)。UNMAPPEDの理由は`NOT_LABELED`/`ID_NOT_IN_ALLOWLIST`/`NO_ID_NO_SUPPLEMENT`/`EVENT_CLAIM_WITHOUT_ID`/`EVENT_LIKE_WITHOUT_E_ID`。
2. **ID形式・入力形式・Prompt形式は原因ではない**: DEV記録30 map・UNMAPPED行20行の理由内訳は `EVENT_CLAIM_WITHOUT_ID` 18、`NO_ID_NO_SUPPLEMENT` 8、`EVENT_LIKE_WITHOUT_E_ID` 1(複数理由を重複計上)。`ID_NOT_IN_ALLOWLIST`・`NOT_LABELED`は0件=Theme Packageの出典ID形式の不整合や付番漏れは起きていない。
3. 主因は**`EVENT_CLAIM_WITHOUT_ID`**: lunaが「立場・状況の語り」(例「中学生の子どもに、いつ、どこまでSNSを使わせるか、親のわたしが決めることになる」)にも`is_event_claim=true`を付け、出典IDが空になるため。UNMAPPED 20行のうち6行は「年代・立場の手がかり」(補いとして許可された種別)を付けたうえで`is_event_claim=true`になったもの(`event_like`の正規表現にも該当しない立場文)。
4. **付番は同じ入力でも結果が変わる(非決定)**: E-3で最終本文=再生成後本文(3/3で文字列一致)なのに、Voice1は再生成直後の付番でUNMAPPED 1件、最終の付番(同一Promptのcache命中、入力1,264tokのうち1,261がcached)で0件。同じ入力で結果が割れる=発火は一部が付番ノイズ。
5. **再生成の効果は低い**: UNMAPPEDの件数 初回→再生成後 = Voice1 1→1、Voice2 1→0、Voice3 1→2(E-3)。「全て解消」は1/3、悪化が1/3。再生成後の残りは仕様どおり記録のみ(最終`voice_3`に2文が残る)。
6. DEV(5 run)の初回付番(`stages/map1`): 15 mapのうち8(53%)でUNMAPPED。E-3は3/3。

低減策(原価削減額は上限の見込み。**測定には有料Trialが必要**):
| # | 案 | 品質への影響 | 見込み削減 | 区分 |
|---|---|---|---:|---|
| U-1 | `map_voice`の行ごとの理由(reasons)・付番rowsをvoices_recordへ保存(今は件数しか残らず、E-3の個別理由が事後に特定できない) | なし(記録のみ) | 0円(次回以降の原因測定に必要) | **品質非影響。修正候補(text coreを所有する別委任に依頼)** |
| U-2 | 最終付番(`yp_vmap_*_final`、3 call)を、本文が再生成後付番と同一のとき再利用して省略(3/3が同一入力の重複call) | なし(記録のみ。ただし最終記録の値が付番再実行のばらつきを失う) | 0.40円/本 | 品質非影響(Yのtext core変更。委任_05の所有file) |
| U-3 | 立場文(`supplement_kinds`に「年代・立場の手がかり」を含み、`event_like`でない文)の`is_event_claim=true`をUNMAPPEDにしない | **品質ガードの緩和**(出来事の捏造検知の範囲が変わる) | DEV記録の初回UNMAPPED 8mapのうち4map(50%)が解消する計算(残り4mapは非立場文のUNMAPPEDが残る) → 再生成を約半分回避 ≈ 約7円/本(14.92円×50%) | **品質判断(ユーザー/Fable)** |
| U-4 | UNMAPPEDと判定されたら、Solで再生成する前にlunaで同一本文を再付番(約0.13円)し、再付番で解消すれば再生成しない | ガード基準の変更(ノイズ吸収)。通過判定が1回の付番から2回の付番に変わる | 再生成の一部(解消率は未測定) | **品質判断(ユーザー/Fable)** |
| U-5 | 再生成自体の廃止(記録のみ化) | 出来事の捏造を直す機会を失う | 14.92円 | 品質判断。**OF-Y6-07は承認済み仕様のため推奨しない** |

## 3. (2) Closing 1 call 21.99円

- 出力12,902tok中 **reasoning 10,876tok(84.3%)**、可視出力は2,026tok(3候補+選択のJSON/本文)。出力単価$10/Mtok×12,902 = 20.6円、入力4,197tok×$2/M = 1.3円。所要268.8秒。
- **cached_tokens: 0**(命中率0%)。Closingは1記事1 callのためrun内でcacheが効く余地がなく、run間の命中も(system promptが固定でも)間隔が空くため期待できない。命中を100%にしても節約は最大約1.3円(入力4,197tok×(2.0−0.1)$/M)。**cache最適化は原価要因にならない**。
- Voice生成(Sol high)も同様に3 callすべてcached 0(入力約3.4〜3.8k tok、約0.5〜0.6円/call分が上限)。lunaの`final`付番だけcacheが効いた(1,261/1,264)。
- 低減策: reasoning量を下げる(effort=high→medium/low、または推論を促さない指示)以外に有効なものはない。**effort変更はClosing品質の判断**(ユーザー承認の「Prompt 02+Sol high」の変更)なので採否はユーザー。効果の大きさは本書のデータでは測れない(effort別のreasoning量は未測定。要A/B Trial)。

## 4. (3) その他

- **人物紹介の再生成(2.42円)**: 初回の`voice_3:COPIES_VOICE_BODY_10CHARS`(紹介文がVoice本文の10文字以上を複写)という決定論検査に1回触れた(`intro_meta.json`)。仕様どおりの再生成。
- TTS生成41 callが14.68円(17.8%)、ASR(primary+secondary)4.58円。共有ナレーションはMaster Audio Storeから再利用(b1b reused9/generated3、a2 reused10/generated3、`reuse_telemetry.jsonl`)。Y本文8segmentは記事固有で再利用不可。
- kp/support/translateは計5.0円(6%)。重複callは見つからなかった(KP候補生成の外側retryは0〜1)。
- **重複call**: U-2の`final`付番3 callのみ(0.40円)。

## 5. 70円目標との差(+12.72円)の内訳
Y 1本の実測82.72円は、Sol(High)の10 callが57.13円(69%)。70円に収めるには −12.72円が必要。
- **品質非影響で確実に削れる額は0.40円(U-2)のみ**。cache・並列化・予算guardの調整では動かない。
- UNMAPPED再生成14.92円(U-3/U-4で一部、U-5で全部)とClosing/Voiceのreasoning(effort)が実質の削減余地で、**どちらも品質判断を伴う**。目安として U-3(約7円)+ Closing effort変更(21.99円の30〜50%なら−7〜−11円、**効果未測定**)で70円付近に届く可能性があるが、実測が必要。
- 推奨: (1) U-1(行ごとの理由保存)を次の有料run前に入れる(原価0・測定のため)。(2) U-3/U-4とeffortの効果を、1回のTrial(Y 2〜3本、品質評価付き)で測る提案をFable/ユーザーへ。独断では変更しない。

## 6. E-1(宅配)の原価(参考)
R0再利用でtextは0.12円。TTSが主費目(HR Lock対象segmentの再試行分を含む)。詳細は`BUDGET_LOG_02.md`。E-1/E-3とも**Part 1/Part 2(接続後)の追加原価は約0.74円/本**(Part 2候補抽出+Part 1解説+訳+Step B、実測。`EVIDENCE_02.md`)。
