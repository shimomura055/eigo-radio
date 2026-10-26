# FIX_01 — 是正の可否判定: **是正は実施しない**(Production code・test変更 0)

管理ID: CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01(2026-10-26)。判定根拠=委任文「是正の許可条件(a)〜(d)」。**1つでも欠ければ実装せず判断候補**。

| 条件 | 判定 | 根拠 |
|---|---|---|
| (a) ユーザー承認原文にStd/Adv双方を対象とする記述、または一方を除外する記述が無い | **不成立(曖昧)** | 『除外』の明示は無いが、『Advancedのみ』(Trial、`FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md:31`)、『適用範囲は承認済みTrial条件と照合し未承認の対象拡大を行わない』(`FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md:24,32`)、『Standardは承認済み仕様どおり維持する』(`FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md:49`)がレベル範囲に触れており、『双方を対象にする記述が無い』とも『一方除外の記述が無い』とも断定できない。2026-10-26のユーザー原文(Std/Adv双方を意図)は新しい意図表明。→ 承認記録の曖昧さ=委任文§4『実質的な新仕様決定を要する場合はUSER_DECISION_REQUIRED』に該当 |
| (b) Std除外がユーザー承認なしに設計判断・実装都合で入った経緯が特定できる | 成立 | Fable委任文(`2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md:8`)+Sonnet Phase 0設計(`EXISTING_SPEC_CHECK_01.md:116,120`、`WIRING_DESIGN_01.md:117`)。理由=6%減速との相互作用が未Trial。Opus指摘由来ではない |
| (c) 是正が「既存の承認済み分割規則をStandardにも同一条件で適用する」だけで新規則・閾値変更・Prompt変更を伴わない | **不成立** | Stdは生成後にsegment wav全体へ6%減速(ffmpeg atempo)を掛け、無音も同率で伸びる。chunk化すると『chunk別減速→0.2秒pad』か『chunk連結後減速』か(追加ポーズが0.2秒か約0.212秒か)、Zの`verify_std_english_slowdown`・reuse_key・Style/Gate・親wav整合の再設計が必要で、新規設計(Opus条件A該当の可能性)。ユーザーはStd chunk音声を聴いていない(Trial=Advancedのみ)。さらにYは**拡張しても1段落契約で分割0**(別の新仕様が必要) |
| (d) 他Family・他レベルの既存挙動を変えない(回帰test PASS) | 判定不能 | 本環境は`google.genai`未導入でX/Z/Y配線testがimport不可(14 error/43、他は module import失敗)。実装しないため未実施 |

## 結論
- **Production code/test編集 0**(`git status --short -- er117_chunk_tts_production_01.py er019_family_x_audio_production_runner_01.py er063_family_z_audio_01.py er121_family_y_audio_01.py er121_family_y_runner_01.py er121_family_y_structure_01.py` = 差分なし)。
- 判断候補(D=真に新しい判断): ①X/Z/YのStandardへchunk分割を拡張するか(拡張する場合の減速との合成方式を含む) ②Yの1段落契約とX方式の不整合の解消方法(OPEN-527/UDR-YFB-1。文境界分割等の新規則 or Writer契約変更 or 現状維持)。詳細選択肢はRESULT_PACKET_CHK1.md。
- 11-8の分類: 『ユーザー承認と実装のStd範囲』は承認記録の曖昧さに由来する範囲判断=**ユーザー判断要(D)**。『X Adv・Z Advの配線』は不具合なし=**実害なし**。『Yの不発火』はOPEN-527/OT-42既存=**ユーザー判断要(D、既存)**。
