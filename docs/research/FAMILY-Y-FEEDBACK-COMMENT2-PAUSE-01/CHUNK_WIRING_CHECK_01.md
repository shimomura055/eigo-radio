# CHUNK_WIRING_CHECK_01 — Family Yの「段落分割+0.2秒ポーズ」の承認履歴・配線・実適用(read-only、API 0)

管理ID: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02(Lane B)、2026-10-26。ユーザー原文§3(1〜7)への回答。
表記: 【確認済み】=コード行またはruntime記録で直接確認 / 【記録なし】 / 【推定】。

## 結論(先に)
- **コードは配線済みだが、『宅配』E-1では全segmentで一度も発火していない(分割0・追加0.2秒0)。Std/Adv両方、全Voice・導入・Closing・Leadで同じ。** 【確認済み】
- 原因は不具合ではなく**設計上の不発火**: Y本文の承認済み構造契約は「各segment=1段落・改行なし」(`er121_family_y_text_core_01.py:175,1266,1494` `MULTI_PARAGRAPH`検査)、X規則は「段落が2つ未満なら分割しない」(`er117_chunk_tts_production_01.py:90-93`)。両者が重なるとYでは通常分割が発火しない(DECISION_LOG 22449行・OT-42として既に記録済みの事実)。
- **Standard(a2)はそもそも対象外**(X方式=Advanced本文のみ。`er121_family_y_structure_01.py:111` `CHUNK_TTS_Y_LEVELS=("b1b",)`、CURRENT_SPEC『Family X・Z Advanced…のchunk TTS』節の対象外にStandard明記)。ユーザー原文の「Std/Adv両方」とは範囲が食い違う可能性がある(判断候補、後述)。
- 今回の不自然なポーズとの因果関係: **なし**(分割も0.2秒も入っていない音声で起きている)。【確認済み】

## §3-1 承認履歴・仕様との整合
| 出所 | 内容(逐語) |
|---|---|
| `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md:13-25` | 「Family X方式（段落分割＋0.2秒ポーズ）をFamily Yに正式採用する。Status：APPROVED_FOR_PRODUCTION。…既存のX方式を最大限再利用する。…セリフや話者の切替を不自然に結合・分割しない。事前の追加Trial・ユーザー試聴承認は不要。正式Production実走時に音声品質・分割位置・ポーズを検証する。今回の承認はX方式のY適用であり、ZのB_r1方式は採用しない。」 |
| 同:148(受入条件5) | 「X方式Chunk分割＋0.2秒ポーズがYで機能する。」 |
| `DECISION_LOG.md:22449` | 委任_04の実装記録。「**事実: 現行のY本文契約は各segment=1段落のため、X規則により通常は分割が発火せず従来の1 call**(OT-42)」。Adv(b1b)のみ。 |
| `docs/pm/RESULT_PACKET_YPL4.md:8,13` | 受入条件5は「機構は実装・offline検証済み、正式実走での実証は未取得、現契約では通常分割が発火しない(OT-42)→部分達成」、OT-42は分類D・「聴取で『速い/詰まる』が出た後に限り判断」と記録。 |
| `CURRENT_SPEC.md`『Family X・Z Advanced…のchunk TTS』節(2941-2947付近) | X=段落+0.2秒(24kHzで4800 sample)、対象=Advanced本文、**対象外=Standard・Dialogue・KP・Preview・Comment・Family Y**と書かれている。Yへの適用はUSER_02 ①(同節にはY配線の記述なし=節はX/Z限定の記述のまま)。 |
| `OPEN_ITEMS.md` OPEN-525 | 同じE-1 `y_voice_1`でRepetition QA D'が境界flag(b1b 7中6、a2全attempt)。選択肢に「Y Voiceの文境界Chunk(OT-42同根、現状1段落契約でChunk分割0)」を列挙済み。 |

仕様の定義(コード確定): 分割=空行区切りの段落(`split_x_paragraphs`、`er117:83-84`)、段落2つ以上のときだけ`<segment>_k<j>`へ(`:87-100`)、無音=`EXTRA_PAUSE_SECONDS=0.2`(`:24`)=24kHzで4800 sample(`:74-75`)、chunk間にのみ挿入、適用=本文8 segment(lead/intro×3/voice×3/closing。`er121_family_y_audio_01.py:264-272`)のsegment内側だけ。話者切替(intro→voice等)は結合も分割もしない(`:266`)。Commentは対象外。

## §3-2 Y正式初回Production経路に存在するか(コード経路、【確認済み】)
runner→audio→er117:
- 課金前の決定記録+plan: `er121_family_y_audio_01.py:285-308` `_record_chunk_decision`(適用表がYを非適用なら課金前STOP `:288-290`、plan保存済みとの不一致もSTOP `:298-300`)。b1b生成の入口で呼ぶ `:397`、a2は`:505`(`chunk_tts_applied_at_this_level=false`と理由「Std(a2)本文はX同様chunk化しない」を記録)。
- 分割: `plan_y_chunks` `:264-272`(`chunk_tts.plan_x_part`を直接呼ぶ)。chunk生成: `_generate_y_body_segment_chunked` `:363-390`(chunkごとに非chunkと同じ呼出、直列、OK chunkは再利用)。親wav(生連結)+親集約entry: `refresh_y_chunk_parents` `:347-360`。
- 組立: `_load_y_body_chunks` `:675-702`(整合検査+親wav=chunk連結の整数sample一致)→gain→0.2秒pad(`_chunk_assembly_summary_y` `:805-826`が分割位置・0.2秒実測offsetを`assemble_summary`系に記録)。assemble前にも親を再構築 `:855`。
- 共通role解決: `er020_tts_retry_local_rewrite_01.py:132` `_FAMILY_Y_SEGMENT_PATTERN`は既に`(?:_k[1-9][0-9]*)?`を含む=OT-44の「Y chunk IDがFULL_STORYへ解決されない」は現在は解消済み(`_assert_chunk_roles` `er121_family_y_audio_01.py:275-282`はE-1 b1bで通過)。
- 回帰test: `er121_family_y_audio_chunk_test_01.py`に`test_single_paragraph_segments_are_not_chunked`(`:137`)=「1段落は分割しない」を**期待値として固定**、複数段落fixtureでの生成・0.2秒組立・resume・失敗chunk・Style Gate・scope復帰fail-closedは合成データのみ(`:205-329`)。**実Y本文での発火実績はない**。(本環境は`google.genai`未導入でtest再実行不可=`ImportError`、test結果は今回未取得。)

## §3-3 Std/Adv両方で発動しているか
| level | 適用可否(コード) | 実際(`audit/chunk_tts_decision.json`) |
|---|---|---|
| Adv b1b | 適用対象 | `chunk_tts_applied_at_this_level=true`、`planner_version=chunk_tts_v1_x_paragraph_z_r1_20261025`、`extra_pause_seconds=0.2`。ただし**8 segment全て`chunked=false, paragraphs=1, reason="paragraphs=1<2", chunk_ids=[]`** |
| Std a2 | 対象外 | `chunk_tts_applied_at_this_level=false, not_applied_reason="Std(a2)本文はX同様chunk化しない"` |
(E-1=`er121_output/family_y_production_01/redelivery_fee/run_01/{a2,b1b}/audit/chunk_tts_decision.json`、E-3 SNS `…/sns_age_limit/run_01/…`も同じ。全4runで chunk 0。)

## §3-4/3-5 『宅配』各Voiceの実分割位置と0.2秒挿入位置(【確認済み】)
`parts.json`の全segmentが改行0(空行0)。TTS入力は全segmentとも**1 call=1 chunk**。

| level | segment | 語数 | 実TTS分割 | 追加0.2秒 | 完成wav長=narration wav長 |
|---|---|---|---|---|---|
| Std a2 | y_voice_1 (Algieba) | 120 | なし(1 call、対象外) | 0箇所 | 46.465s=timeline 46.465s |
| Std a2 | y_voice_2 (Zephyr) | 157 | なし | 0 | 51.58s |
| Std a2 | y_voice_3 (Schedar) | 156 | なし | 0 | 52.408s |
| Adv b1b | y_voice_1 | 133 | なし(paragraphs=1) | 0 | 44.36s |
| Adv b1b | y_voice_2 | 155 | なし | 0 | 45.84s |
| Adv b1b | y_voice_3 | 158 | なし | 0 | 49.84s |
| 両level | y_lead / y_intro_1〜3 / y_closing | 62〜124 | なし | 0 | — |
`audit/timeline.json`の各segment durationはnarration wavの長さと一致し、segment間に入るのは固定gap(`pause_intro_to_voice`等0.8s、`er121_family_y_audio_01.py:752-762`)のみ。Voice 1の内部に追加された無音は0。b1bの`chunk_plan_b1b.json`もchunked=false 8件。

## §3-6 retry/resume/regeneration
- resume(OK chunk再利用・0 TTS): 実装`er121_family_y_audio_01.py:201-203,311-323`(旧planner版chunk破棄・chunk化しなくなったsegmentの旧chunk集約破棄)、`--only-segments`の親→chunk id展開 `:326-336`、`_k`指定はb1bのみ許可(Stdで`_k`指定→拒否 `:111-113`)。【コードで確認、実Y runでは発火せず=実測なし】
- Local Rewrite/retry: chunkもsegmentと同じ関数・同じ3 attempt・同じfallback(`:363-366`)、roleは`er020:132`で解決。
- HR採用(`er121_e1_hr_adopt_r0_01.py`): chunk idの扱いなし(grep `chunk`=0件)。E-1では不要(非chunk)だが、将来chunk化したsegmentをHR採用する場合は未対応=要追加(本調査の範囲外、仕様判断後)。
- Std 6%減速(`er121_family_y_audio_01.py:482-566`、`er121_e1_hr_adopt_r0_01.py:112-121`): 非chunkのsegment wav全体に`apply_a2_slowdown`(ffmpeg atempo)。減速が**無音も同率**で伸ばすことは実測で確認(同一音声のoriginal→減速後で無音平均535→564ms=+5.4%、総時間43.85→46.465s=×1.0597)。Stdをchunk化する場合の「chunk別減速かchunk結合後減速か、0.2秒の扱い」は**未定義**(新設計=Opus条件A該当の可能性)。

## §3-7 今回の不自然なポーズとの因果
分割0・0.2秒0のため、分割・0.2秒は原因ではない。原因切り分けは`INVESTIGATION_01.md`/`PAUSE_MEASUREMENT_01.md`。

## 判断候補(分類D=真に新しい判断。Open Itemにあるだけではない=ユーザーが『適用済み』と認識している指示と実状が異なるため)
「Yに段落分割+0.2秒」が実音声で効くようにするには次のいずれかの新仕様が必要(いずれも承認済み仕様の変更):
1. **Y専用の文境界分割**(例: 100語前後以上のsegmentを文境界で2〜3 chunkへ)。Z B_r1は明示不採用(USER_02)なのでY用の第三の規則=新規。変更箇所は`er121_family_y_audio_01.py:264-272`の`plan_y_chunks`のみ(共通er117・X/Zは不変)で影響範囲は小。品質影響は未検証(chunkごとにTTSするため声のトーン連続性は要試聴)。
2. **Writerが長いVoiceを複数段落で出す**(Y本文契約`MULTI_PARAGRAPH`の変更、日本語text coreのPrompt/検査変更、段落数契約)。影響大(Text Gate・Prompt)で非推奨。
3. **現状維持**(OT-42のまま。ポーズ過多は別対処)。
4. **Standardへの適用拡張**(減速との合成設計が要る)。
推奨: 費用・影響が最小の1を、まず『宅配』E-1 Voice 1のみで比較Trial(後述の見積)してから正式採用判断。ポーズ過多の主因が分割有無でない可能性(`INVESTIGATION_01.md`)があるため、採用前にTrialで効果を確認する。
