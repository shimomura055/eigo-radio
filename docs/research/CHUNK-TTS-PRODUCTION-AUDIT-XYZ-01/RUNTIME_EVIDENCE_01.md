# RUNTIME_EVIDENCE_01 — Family X/Z/Y x Standard/Advanced の実発火(既存run artifact再利用、API 0、費用0)

管理ID: CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01(2026-10-26)。集計=`tools/chunk_audit_inventory_01.py`(read-only)→`inventory_01.json`(全値)。**fresh production_formal_path evidenceは本委任では取得していない(有料run 0)。** 以下は全て既存runの再利用(reuse)。

## A. 結論表(ユーザー§3の7項目をFamily×レベルで)
実発火の判定語彙: **発火**=分割・0.2秒が実音声に入っている / **正常な不発火**=規則上対象箇所が存在しない / **配線漏れ**=規則上対象なのに入っていない(本監査では0件) / **仕様上対象外**=Standard。

| Family | レベル | 本文の語数・段落構成(代表run) | 分割条件に該当 | 実分割回数・位置・0.2秒 | 実TTS call | 判定 |
|---|---|---|---|---|---|---|
| X | Adv | uk_train chunk_01: part1 150語/4段落・part2 152語/3段落・part3 126語/3段落。coffee r1: 145/3・144/3・174/3 | 該当(段落2以上) | uk_train: **10 chunk・0.2秒7箇所**(part1=63/14/30/43語、episode内 108.506/114.386/127.786s。part2=58/52/42、173.056/189.766s。part3=34/53/39、230.576/249.256s)。coffee r1: 9 chunk・6箇所(例 99.196s/117.606s…) | uk_train 10(raw_usage_log: 各chunk 1 call)、coffee r1 9、r2 10(part1_k3のみ2=retry) | **発火**(配線evidence run 3本。配線後の新規記事の完走runはまだ無い=ai_island_temple[2026-10-26]はTTS前) |
| X | Std | 同runのa2: part1〜3 = 123〜165語/3(〜4)段落 | 仕様上対象外 | 0 | 各part 1 call(coffee r1 raw_usage: a2 part1=2[retry]、part2=1、part3=1) | **仕様上対象外**(Std拡張時は uk_train=3 part全て3〜4 chunkに分かれる計算[replay]。`RUNTIME_EVIDENCE`機械表参照) |
| Z | Adv | tell_tale run_chunk_01: narrator 120語・126語の2 clip(他は<=100語またはDialogue)。melos run_p2_evidence_r3/r4: part2_c1 124語 | 該当(narrator>100語) | tell_tale: **2 clip→4 chunk・0.2秒2箇所**(part2_c1=58+62語[段落境界]、part3_c1=65+61語[段落境界])。melos: **1 clip→2 chunk・0.2秒1箇所**(74+50語[段落境界]) | tell_tale chunk 4(各chunk 1 attempt=2 attempt/clip)、melos 2 | **発火**(2作品) |
| Z | Adv(別作品) | monkeys_paw(narrator最大68語)・open_window・after_twenty_years(いずれも>100語narratorなし) | 非該当 | 0 | clipごと1 call | **正常な不発火**(語数のみで判定[plannerの全再現ではない]。配線前runのため参考) |
| Z | Std | tell_tale a2 part2_c1=129語・part3_c1=139語(slowdown=True)、melos a2 part2_c1=134語、gift_of_the_magi a2 part1_c1=122語 | 仕様上対象外(Advなら100語超でchunk化される規模) | 0 | 各clip 1 call | **仕様上対象外**(長いnarrator 1 callが残る) |
| Y | Adv | E-1宅配 y_voice_1=133語/y_voice_2=155語/y_voice_3=158語、lead 67、closing 123、intro 15〜21。E-3 SNS: 同様。**全8 segmentが1段落** | 非該当(`paragraphs=1<2`) | **0**(chunk_tts_decision.json 全8 segment chunked=false) | segmentごと1 call(y_voice_1のみ4 attempt=retry) | **正常な不発火に見えるが、ユーザーの意図(Voice内の長停止対策としての分割)は未達**。配線漏れではなく『承認済みX方式×承認済みY本文1段落契約』の組合せ不整合(OT-42) |
| Y | Std | E-1/E-3 a2: voice 120〜157語、全segment 1段落 | 仕様上対象外 かつ 1段落 | 0 | segmentごと1 call | **仕様上対象外**。仮にStd拡張しても分割0(1段落) |

## B. 不足evidenceと最小検証方法・見積(「確認済み」と誤認しない)
| 不足 | 状態 | 最小検証方法 | 見積(出典ある単価のみ) |
|---|---|---|---|
| X/Zの配線後『新規記事の正式初回』完走run | X: ai_island_temple run_ai_01はHR待ち・TTS前(OPEN-526)。Z: 配線後の新規作品なし | ai_island_temple のAudio stageが完走した時点で`chunk_plan_b1b.json`/`chunk_tts_evidence_b1b.json`/timelineを本スクリプトで再集計(replay予測: Adv part1=3 chunk[66/34/59語]、part2=2 chunk[54/88語]、part3=3 chunk[62/54/63語]=8 chunk・5箇所の0.2秒、Stdは3 call。これが一致すれば配線後の初回経路の実発火となる) | 追加費用0(既存の正式run内。本スクリプトは読み取りのみ) |
| chunk単位のretry/Local Rewrite/fallbackの実run発火 | 実runではattempt_count=1・LR None。resumeのみ実観測(coffee r1/r2、reused=true) | 配線時のmock testで担保。本環境は`google.genai`未導入で再実行できない→genai導入環境で`py run_project_regression.py --pattern "er117*_test_*.py"`等を無料で再実行 | 0円(無料・遮断下) |
| Yでchunkが実際に発火した実音声 | 0件(1段落契約) | Y新仕様(分割規則またはWriter契約)が決まった後に、Voice 1 1 segment(Adv)で2 chunk生成。合成testは`er121_family_y_audio_chunk_test_01.py:205-329`で担保済み | 単価出典=`28bad7b33`のcommit報告『Voice 1候補Std/Adv各3 take=17.52円』から1 take約2.9円→2 chunkで約6円以内(参考値) |
| Std(X/Z/Y)でchunk化した実音声 | 0件(仕様上対象外) | ユーザー判断後に設計(減速合成)→offline test→1記事分TTS | X: Adv TTS実費 2.51〜2.64円/記事(`CURRENT_SPEC.md:2946`/`DECISION_LOG.md:22397`)を目安にStd chunkで同程度。Z: tell_tale 全体16.67円(Std+Adv+KP、`CURRENT_SPEC.md:2946`)が上限目安 |

## C. 注意(正確性)
- 「attempts」はresultsの`attempts_log`/`attempts`件数。X Advのchunk callはraw_usage_log(stage=tts, model=gemini-3.8-flash-lite-tts)でもchunk id別に1 callを確認(uk_train 10、coffee r1 9、r2 10)。
- Z pre-wiring run(monkeys_paw等)の『>100語narratorなし』は語数のみの判定であり、planner全再現(段落・文境界の有無)ではない(本文再構成が必要なため)。
- X pre-wiring run(moon_shrinking run_ms_03、manga_ai_chat run_byus_01)はchunk配線(2026-10-25 13:00頃)より前の生成で、chunk無し。既存公開音声・manifestは変更していない(未再生成)。
- a2の『replay』分割は**仮に拡張した場合のplanner出力**の参考で、Stdに適用された事実ではない。

---
# 機械集計(chunk_audit_inventory_01.py の出力そのまま)

`replay_current_code`=現行 `er117_chunk_tts_production_01` plannerを当該本文へ適用した結果。`saved_plan`=当該runが生成時に保存した`audit/chunk_plan_b1b.json`。

## X(本文3 part。Std=a2は仕様上対象外)

| run | 状態 | level | part | 語数 | 段落数 | 現行plannerの分割 | 保存plan | chunk entry | attempts合計 | 追加0.2秒(episode内s) |
|---|---|---|---|---|---|---|---|---|---|---|
| uk_train chunk_01(配線evidence) | post | a2 | part1 | 145 | 4 | 分割[66, 14, 31, 34](但しこのlevelは仕様上対象外) | - | 0 | 2 | - |
| uk_train chunk_01(配線evidence) | post | a2 | part2 | 147 | 3 | 分割[56, 49, 42](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| uk_train chunk_01(配線evidence) | post | a2 | part3 | 123 | 3 | 分割[35, 52, 36](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| uk_train chunk_01(配線evidence) | post | b1b | part1 | 150 | 4 | 分割[63, 14, 30, 43] | chunked [63, 14, 30, 43] | 4 | 4 | [[108.506, 108.706], [114.386, 114.586], [127.786, 127.986]] |
| uk_train chunk_01(配線evidence) | post | b1b | part2 | 152 | 3 | 分割[58, 52, 42] | chunked [58, 52, 42] | 3 | 3 | [[173.056, 173.256], [189.766, 189.966]] |
| uk_train chunk_01(配線evidence) | post | b1b | part3 | 126 | 3 | 分割[34, 53, 39] | chunked [34, 53, 39] | 3 | 3 | [[230.576, 230.776], [249.256, 249.456]] |
| part2_hr_evidence run_r1(coffee_prices) | post | a2 | part1 | 136 | 3 | 分割[51, 47, 38](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r1(coffee_prices) | post | a2 | part2 | 144 | 3 | 分割[49, 49, 46](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r1(coffee_prices) | post | a2 | part3 | 165 | 3 | 分割[56, 64, 45](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r1(coffee_prices) | post | b1b | part1 | 145 | 3 | 分割[48, 51, 46] | chunked [48, 51, 46] | 3 | 3 | [[99.196, 99.396], [117.606, 117.806]] |
| part2_hr_evidence run_r1(coffee_prices) | post | b1b | part2 | 144 | 3 | 分割[45, 51, 48] | chunked [45, 51, 48] | 3 | 3 | [[157.016, 157.216], [174.926, 175.126]] |
| part2_hr_evidence run_r1(coffee_prices) | post | b1b | part3 | 174 | 3 | 分割[58, 67, 49] | chunked [58, 67, 49] | 3 | 3 | [[224.116, 224.316], [244.436, 244.636]] |
| part2_hr_evidence run_r2(coffee_prices) | post | a2 | part1 | 136 | 3 | 分割[51, 47, 38](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r2(coffee_prices) | post | a2 | part2 | 144 | 3 | 分割[49, 49, 46](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r2(coffee_prices) | post | a2 | part3 | 165 | 3 | 分割[56, 64, 45](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| part2_hr_evidence run_r2(coffee_prices) | post | b1b | part1 | 145 | 3 | 分割[48, 51, 46] | chunked [48, 51, 46] | 3 | 4 | - |
| part2_hr_evidence run_r2(coffee_prices) | post | b1b | part2 | 144 | 3 | 分割[45, 51, 48] | chunked [45, 51, 48] | 3 | 3 | - |
| part2_hr_evidence run_r2(coffee_prices) | post | b1b | part3 | 174 | 3 | 分割[58, 67, 49] | chunked [58, 67, 49] | 3 | 3 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | a2 | part1 | 177 | 3 | 分割[54, 71, 52](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | a2 | part2 | 155 | 3 | 分割[54, 51, 50](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | a2 | part3 | 163 | 3 | 分割[51, 40, 72](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | b1b | part1 | 182 | 3 | 分割[58, 71, 53] | - | 0 | 1 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | b1b | part2 | 154 | 3 | 分割[52, 52, 50] | - | 0 | 1 | - |
| moon_shrinking run_ms_03(配線前の最新正式) | pre | b1b | part3 | 163 | 3 | 分割[54, 40, 69] | - | 0 | 1 | - |
| manga_ai_chat run_byus_01(配線前) | pre | a2 | part1 | 166 | 3 | 分割[52, 57, 57](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| manga_ai_chat run_byus_01(配線前) | pre | a2 | part2 | 135 | 2 | 分割[72, 63](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| manga_ai_chat run_byus_01(配線前) | pre | a2 | part3 | 157 | 3 | 分割[57, 49, 51](但しこのlevelは仕様上対象外) | - | 0 | 1 | - |
| manga_ai_chat run_byus_01(配線前) | pre | b1b | part1 | 164 | 3 | 分割[54, 52, 58] | - | 0 | 3 | - |
| manga_ai_chat run_byus_01(配線前) | pre | b1b | part2 | 145 | 2 | 分割[75, 70] | - | 0 | 1 | - |
| manga_ai_chat run_byus_01(配線前) | pre | b1b | part3 | 158 | 3 | 分割[57, 48, 53] | - | 0 | 3 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | a2 | part1 | 146 | 3 | 分割[57, 34, 55](但しこのlevelは仕様上対象外) | - | 0 | 0 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | a2 | part2 | 136 | 2 | 分割[50, 86](但しこのlevelは仕様上対象外) | - | 0 | 0 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | a2 | part3 | 170 | 3 | 分割[60, 49, 61](但しこのlevelは仕様上対象外) | - | 0 | 0 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | b1b | part1 | 159 | 3 | 分割[66, 34, 59] | - | 0 | 0 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | b1b | part2 | 142 | 2 | 分割[54, 88] | - | 0 | 0 | - |
| ai_island_temple run_ai_01(2026-10-26、TTS未実行) | textonly | b1b | part3 | 179 | 3 | 分割[62, 54, 63] | - | 0 | 0 | - |

## Z(story clip。Adv narrator >100語のみ対象、Std=a2は仕様上対象外)

| run | 状態 | level | clip | voice | 語数 | 現行規則で対象か | (Stdのみ)100語超narrator | 保存plan | chunk entry | attempts |
|---|---|---|---|---|---|---|---|---|---|---|
| tell_tale_heart run_chunk_01(配線evidence) | post | a2 | (全6 clip、narrator>100語=2、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| tell_tale_heart run_chunk_01(配線evidence) | post | a2 | full_story_part2_c1 | narrator | 129 | False | True | - | 0 | 1(slowdown=True) |
| tell_tale_heart run_chunk_01(配線evidence) | post | a2 | full_story_part3_c1 | narrator | 139 | False | True | - | 0 | 1(slowdown=True) |
| tell_tale_heart run_chunk_01(配線evidence) | post | b1b | (全6 clip、narrator>100語=2、保存planでchunked=2。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| tell_tale_heart run_chunk_01(配線evidence) | post | b1b | full_story_part2_c1 | narrator | 120 | True | False | chunked [58, 62] ['paragraph', 'paragraph'] | 2 | 2(slowdown=None) |
| tell_tale_heart run_chunk_01(配線evidence) | post | b1b | full_story_part3_c1 | narrator | 126 | True | False | chunked [65, 61] ['paragraph', 'paragraph'] | 2 | 2(slowdown=None) |
| melos run_p2_evidence_r3(2026-10-25夜) | post | a2 | (全23 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_p2_evidence_r3(2026-10-25夜) | post | a2 | full_story_part2_c1 | narrator | 134 | False | True | - | 0 | 1(slowdown=True) |
| melos run_p2_evidence_r3(2026-10-25夜) | post | b1b | (全25 clip、narrator>100語=1、保存planでchunked=1。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_p2_evidence_r3(2026-10-25夜) | post | b1b | full_story_part2_c1 | narrator | 124 | True | False | chunked [74, 50] ['paragraph', 'paragraph'] | 2 | 2(slowdown=None) |
| melos run_p2_evidence_r4(2026-10-25夜) | post | a2 | (全23 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_p2_evidence_r4(2026-10-25夜) | post | a2 | full_story_part2_c1 | narrator | 134 | False | True | - | 0 | 1(slowdown=True) |
| melos run_p2_evidence_r4(2026-10-25夜) | post | b1b | (全25 clip、narrator>100語=1、保存planでchunked=1。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_p2_evidence_r4(2026-10-25夜) | post | b1b | full_story_part2_c1 | narrator | 124 | True | False | chunked [74, 50] ['paragraph', 'paragraph'] | 2 | 2(slowdown=None) |
| monkeys_paw run_sf_prod_01(配線前) | pre | a2 | (全30 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| monkeys_paw run_sf_prod_01(配線前) | pre | b1b | (全34 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_e2e_06(配線前) | pre | a2 | (全23 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_e2e_06(配線前) | pre | a2 | full_story_part2_c1 | narrator | 134 | False | True | - | 0 | 1(slowdown=True) |
| melos run_e2e_06(配線前) | pre | b1b | (全25 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| melos run_e2e_06(配線前) | pre | b1b | full_story_part2_c1 | narrator | 124 | True | False | - | 0 | 1(slowdown=None) |
| gift_of_the_magi run_sf_prod_01(配線前) | pre | a2 | (全18 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| gift_of_the_magi run_sf_prod_01(配線前) | pre | a2 | full_story_part1_c1 | narrator | 122 | False | True | - | 0 | 1(slowdown=True) |
| gift_of_the_magi run_sf_prod_01(配線前) | pre | b1b | (全18 clip、narrator>100語=1、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| gift_of_the_magi run_sf_prod_01(配線前) | pre | b1b | full_story_part1_c1 | narrator | 123 | True | False | - | 0 | 1(slowdown=None) |
| open_window run_sf_prod_01(配線前) | pre | a2 | (全33 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| open_window run_sf_prod_01(配線前) | pre | b1b | (全33 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| after_twenty_years run_sf_prod_01(配線前) | pre | a2 | (全28 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |
| after_twenty_years run_sf_prod_01(配線前) | pre | b1b | (全30 clip、narrator>100語=0、保存planでchunked=0。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |

## Y(8 segment、各1段落契約。Std=a2は仕様上対象外)

| run | level | segment | 語数 | 段落数 | 現行planner分割 | decision記録 | chunk entry | attempts |
|---|---|---|---|---|---|---|---|---|
| 宅配 redelivery_fee run_01(E-1) | a2 | y_lead | 62 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_closing | 124 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_intro_1 | 11 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_voice_1 | 120 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 0 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_intro_2 | 18 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_voice_2 | 157 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_intro_3 | 18 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | a2 | y_voice_3 | 156 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_lead | 67 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_closing | 123 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_intro_1 | 15 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_voice_1 | 133 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 4 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_intro_2 | 19 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_voice_2 | 155 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_intro_3 | 21 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| 宅配 redelivery_fee run_01(E-1) | b1b | y_voice_3 | 158 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_lead | 56 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_closing | 116 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_intro_1 | 20 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_voice_1 | 124 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_intro_2 | 28 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_voice_2 | 140 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 2 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_intro_3 | 22 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | a2 | y_voice_3 | 147 | 1 | False(paragraphs=1<2) | level対象外: Std(a2)本文はX同様chunk化しない | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_lead | 61 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_closing | 127 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_intro_1 | 23 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_voice_1 | 128 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_intro_2 | 32 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_voice_2 | 147 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_intro_3 | 27 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
| SNS年齢制限 sns_age_limit run_01(E-3) | b1b | y_voice_3 | 153 | 1 | False(paragraphs=1<2) | {'chunked': False, 'paragraphs': 1, 'reason': 'paragraphs=1<2', 'chunk_ids': []} | 0 | 1 |
