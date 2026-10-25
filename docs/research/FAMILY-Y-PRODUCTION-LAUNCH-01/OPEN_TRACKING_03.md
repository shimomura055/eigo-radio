# OPEN_TRACKING_03: Family Y Production立上げ — 未完了事項の追跡(委任_04更新)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_04 / 2026-10-25(JST)。`OPEN_TRACKING_02.md`(OT-01〜OT-40)からの**更新と追加**のみを書く。正本の追跡先は`OPEN_ITEMS.md`(OPEN-520/484/463)。分類は11-8(修正へ進む/ユーザー判断要/実害なし)。
ユーザー追加決定の原文: `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md`(以下「U2」)。台帳=`SPEC_LEDGER_03.md`(66行)。

## 1. OT-01〜40の更新

| ID | 更新内容 | 現Status(2026-10-25 委任_04) | 11-8分類 |
|---|---|---|---|
| OT-20 | Gate文言(`leak_tension_reverts_to_research`肯定側/`leak_discovery_syntax`等)の扱い: **ユーザー決定U2 §1-②「現行Prompt 02・既存Gateを変更せずに進める。PromptとGateの不整合は既存OPEN_ITEMSで継続管理する。Prompt 03への変更やGate条件の緩和は行わない」**。G-1/G-2(Gate文言の補足・変更)は**実施しない**。実績(Y実走のGate判定履歴)を貯めて将来整理 | **決定済み(変更しない)+OPEN継続管理**。台帳YL-E02=EXCLUDE_OPEN | 実害なし(将来整理) |
| OT-21 | Chunk TTSのYへの扱い: **U2 §1-①で「Family X方式をYに正式採用(APPROVED_FOR_PRODUCTION)」**。除外+OPEN記録を解除し、台帳YL-B08=APPLY。実装済み(OT-41へ移管) | **解消→OT-41** | クローズ |
| OT-27 | 案B(ユーザー承認の固定Closing)のGate方針を**改訂**: 旧「判定1回・FAILなら即STOP」→ **新「既存の再判定機構(判定<=3回)を使う。ユーザー承認本文は書換えない(承認本文の保護)。3回判定後もFAILなら公開せずSTOP(`FIXED_CLOSING_RESIDUAL_FAIL`)→ユーザー判断」**(U2 §1-② 「既存の局所修正・再判定機構を利用」「Gate FAILが解消しない場合は公開しない」+Fable判断)。各判定の結果は`closing_record.json`(`judgements[]`、FAILでも保存)へ記録。一般Closing(Prompt 02)は従来どおり判定<=3+局所書換え+残存FAIL=`LEAKAGE_RESIDUAL_STOP`(公開しない)。test固定(`test_fixed_gate_rejudges_three_times_...`ほか) | **実装済み(offline test PASS)。実走待ち**(E-1) | 修正へ進む(実走で通過可否を確認) |
| OT-22 | I-4(固定本文は書換え禁止STOP)の更新: 書換え禁止は維持。「判定再試行禁止」はOT-27改訂により「同一本文の再判定<=3回は可(書換えなし)」へ変更 | 実装済み | 修正へ進む→完了 |
| OT-33 | 台帳運用: SPEC_LEDGER_03(66行)へ更新。Closeout項目33を追加(OT-43) | 台帳03完了 | 修正へ進む |
| OT-34/OT-35/OT-36 | 変更なし(Cap 170円=Fable自律枠・routing 2キー登録・runner結線は委任_03の領域) | — | — |

## 2. 新規追加

| ID | 区分 | 項目 | 適用対象 | 現Status | 残作業 | 解消条件 | 追跡先 | 11-8分類 |
|---|---|---|---|---|---|---|---|---|
| **OT-41** | 実装(承認済み仕様の配線) | **X方式Chunk TTS(段落分割+0.2秒ポーズ)のY適用**(U2 §1-①)。`er121_family_y_audio_01.py`: `plan_y_chunks`(共通`er117.plan_x_part`をY segment 8個へ)・`_generate_y_body_segment_chunked`・`refresh_y_chunk_parents`・chunk単位の`y_style_gate`・`_load_y_body_chunks`(整合検査+親wav生連結検証)・共通`apply_family_x_b1_gain`(chunk別gain+0.2秒)。Adv(b1b)本文のみ(X同様Std非chunk)。Y chunk ID=`<segment_id>_k<j>`。話者切替境界(intro→voice、voice→次のintro)は別segment=結合しない。新規test 16件PASS | Y | **実装済み・offline test済み。Production runtime evidence未取得** | (a)共通`er020`の`_FAMILY_Y_SEGMENT_PATTERN`にchunk接尾辞`(?:_k[1-9][0-9]*)?`追加(OT-44) (b)正式実走で音声品質・分割位置・ポーズを検証(U2 §1-①)。`chunk_tts_decision.json`/`chunk_tts_assembly_b1b.json`/`chunk_tts_evidence_b1b.json` | 正式初回実走のevidence確認 | OPEN-520 / SPEC_LEDGER_03 YL-B08 | 修正へ進む |
| **OT-42** | 発見(ユーザー判断候補の可能性・低) | **現行のY本文契約(各segment=1段落)では、X規則(段落が2つ以上のときだけ分割)によりChunk分割が発火しない**(全segmentが従来の1 call)。Voice約134〜172語(宅配R0実測)が1段落のまま。`check_voice_pl`/`check_closing`/`check_lead`/`check_intro`が1段落を強制し、承認済みの5パート構成と整合 | Y | 記録 | 分割を実際に発火させるにはsegment契約(1段落)の変更=承認済み仕様の変更が必要。**現状は変更せず**、正式実走で『分割0=従来の1 call』をchunk_tts_decision.jsonに記録して検証(受入条件5の読み方を含めFable判断)。聴取で『速い/詰まる』所見が出た場合のみ契約変更を提案 | Fable判断/聴取所見 | OPEN-520 | **ユーザー判断要の可能性(新仕様候補)**: 27-3分類=D(真に新しい判断。ただし発生は聴取所見後) |
| **OT-43** | 運用ルール | PM Closeout Mandatory Check**項目33**「共通仕様のX/Y/Z配線Status確認」を`PM_GOVERNANCE.md` 3節へ追加(U2 §3。28節の実装) | 全体 | **追加済み** | CURRENT_SPEC配線Status表のY列更新はY実装・evidence後 | — | OPEN-413 | クローズ(追記済み) |
| **OT-44** | 他委任・他領域への要求 | (a)**共通`er020_tts_retry_local_rewrite_01.py`**: `_FAMILY_Y_SEGMENT_PATTERN = re.compile(r"y_(?:lead|closing|intro_[1-3]|voice_[1-3])")`を`...(?:_k[1-9][0-9]*)?`へ拡張し、import時自己検査に`y_voice_2_k1`等を追加(追加のみ・既存ID不変)。**未反映の間は、複数段落segmentの生成を課金前にSTOP**(`FAMILY_Y_CHUNK_ID_ROLE_UNRESOLVED`。fail-closed。現契約では1段落のため通常は発火しない)。(b)**runner(`er121_family_y_runner_01.py`、委任_03所有)**: 行297 `res["chunk_tts"]=ys.chunk_decision_record("b1b")`は新内容で自動追従。行668/765の文字列`"chunk_tts": "not_applicable_Y"`を`"applied_X_method"`へ更新(manifest表記)。(c)runner test(`er121_family_y_runner_01_test_01.py`)は本委任で2か所を最小更新済み(chunk_tts_decision.jsonの期待値、er117のimport禁止リストからer117を除外)。runner本体のmanifest文字列(行668/765)は`runner_01_test_01.py:118`の期待値`"not_applicable_Y"`と対であり、更新時は同testも同時に更新すること | Y/共通 | 要求(未反映) | 上記(a)(b) | er020変更+runner文字列更新 | OPEN-520 | 修正へ進む(次委任) |
| **OT-45** | 記録(実害なし) | 案Bの再判定(同一本文を最大3回判定)はLLM判定の揺らぎにより、初回FAILでも再判定でPASSし得る(ユーザー決定U2 §1-②「既存の再判定機構を利用」に従う設計)。各判定の結果(本文sha不変・flag有無・FAIL項目・model・prompt sha)を`closing_record.judgements[]`へ全記録し、判定結果の恣意的な選別でないことを事後確認できるようにした | Y(宅配) | 記録 | 実走で『何回目でPASSしたか』を確認。毎回初回FAIL→再判定PASSなら判定揺らぎが大きい兆候としてFableが評価 | 実績 | OPEN-520 | 実害なし |
| **OT-46** | 継続管理(省略不可) | **Voice生成方式の公開前条件**(U2 §1-③「公開前の出典・利用許諾に関する既存課題は継続管理し、必要な公開条件を省略しない」): V1根拠R2+のみの出典・利用許諾/人手収集約25分/目視1名/V2単一出典例外(台帳YL-C03、OPEN-463/484/520)。U2 §7 STOP条件「公開条件・権利関係の未解決によって公開できない」に該当する場合は公開せずSTOP | Y | 継続管理 | 権利確認(OPEN-484/463)が解消するまで公開しない(限定共有ページはunlisted・noindex・転載不可注記) | 権利確認完了 | OPEN-463 / OPEN-484 / OPEN-520 | ユーザー判断要の可能性(権利関係が未解決のまま公開要求する場合) |

## 3. 完了条件の更新

OT-01〜07・22〜24が揃い、OT-12〜13の接続点が結線され、OT-27(案B実走結果)・OT-41(Chunk実走検証)・OT-44(er020/runner)が解消し、E-1〜E-5が完了した時点で`PRODUCTION_WIRED`の検討(判定はFable、ユーザー最終試聴PASSは別Status)。OT-46(公開条件)は公開時の条件であり、PRODUCTION_WIRED判定とは別に省略しない。
