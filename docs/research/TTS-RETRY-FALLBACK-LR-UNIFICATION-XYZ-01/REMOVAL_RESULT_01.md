# REMOVAL_RESULT_01 — 撤去・残置の実施結果(委任_02。台帳は`REMOVAL_01.md`)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02 / 2026-10-26。対象はX/Y/Z scope内の正式経路。A/B/C(Legacy凍結)の旧コードは温存(goldenでbyte同一を固定)。SSOT(`CURRENT_SPEC.md`等)は編集権限なし=文案をRESULT_PACKET(9)に添付。
Grep方法: `git grep --untracked -E "<pat>" -- '*.py'`(`_output/`・`.venv`は対象外)。前=委任着手時HEAD(3af84a499)、後=本commit時点。

## 1. 撤去(R)の実施結果
| ID | 結果 | 根拠 |
|---|---|---|
| R-01 | 完了 | `er127.COOLDOWN_SECONDS=180.0`が唯一の正式定義(`er127:30`)。`er020`は`LEGACY_COOLDOWN_SECONDS=600.0`(scope外専用)+別名`COOLDOWN_SECONDS`。scope内に迷い込んだ旧`maybe_cooldown_before_attempt`は`cooldown_core`(180秒+STOP確認)へ委譲(`er020:82`)。静的test`StaticTests.test_single_180_definition` |
| R-02 | 完了(scope内) | voice01/news_tail_fix/crosslevel/repro01の旧cooldown呼出は`else:`(`_blk is None`=scope外)分岐にのみ残り、scope内は`blk.step()`経由 |
| R-03 | 完了 | `er122.cooldown_seconds()`→`er127.COOLDOWN_SECONDS`、sleep本体は`er127.cooldown_core`(イベント名`CTX_COOLDOWN_BEFORE_FALLBACK`維持)、doc/comment 180秒化 |
| R-04 | 完了(scope内) | LR再TTSは3回ブロック(`BlockCtx(depth=1)`で同leafを再帰)。旧`max_attempts=1`はscope外helperのみ(Grep G-3) |
| R-05 | 完了(scope内) | `lr_recover`がdepth guard(`LocalRewriteReentryError`)+`_ACTIVE_GUARDED_OUT_PATHS` assert(`LocalRewriteContractError`)。`er020.run_local_rewrite_recovery(depth>=1)`は例外。OPEN-376(scope内)解消 |
| R-06 | 完了 | L2のLR再TTSが`style_prefix_override`を元のまま転送(OPEN-312)。L3の「minimal固定」は①②'=元Style/③'=Fallbackへ |
| R-07 | 完了 | Adv L1/L2はordinal 3で自関数内minimal分岐(Charon維持、Opus M-10)。F-Techは別枠として残置(K-05) |
| R-08 | 縮小(scope内は`lr_recover`) | 旧3helperはscope外分岐用に温存(golden)。scope内からは呼ばれない |
| R-09 | 縮小採用(Opus M-7許容) | KP二段3複製は残し、待機・STOP・resume・slotのみ`BlockRun.step`に共通化(DESIGN_02 I-5) |
| R-10 | 完了 | 解説は`_kp_explanation_unified`(①②解説Style→180秒→③minimal+Secondary必須、LRなし)。`KP_EXPLANATION_MAX_ATTEMPTS=3`は1ブロック試行数として注記訂正(`er019:1203`) |
| R-11 | 案A実施(scope内)・旧コードはscope外用に残置 | L4はattempt内減速+減速後ASR(post_hook)。旧`generate_a2_segment_with_slowdown`本体・`generate_with_a2_slowdown_outer_loop`(Z Adv会話、K-07)・`finalize_a2_slowdown_final_ng`は温存(scope外golden・Z Adv会話)。Grep G-7参照 |
| R-12 | 部分(コード/コメント完了、SSOT・er011コメントは文案添付) | `er122`/`er063:886,1024`/`er122_fzcw_runtime_evidence_01:5,43`は「180秒・1ブロック3回」へ。`er011_human_review_lock_01.py`は編集禁止(委任文)のため旧「総4/4回目以降」コメントは残存=Fableへ(RESULT_PACKET(9)) |
| R-13 | 同上 | `er020`は旧10分記述に「旧決定・A/B/C専用」を明記。voice01/news_tail_fix/crosslevel/repro01の旧待機コメントはscope外分岐の記述として残置(G-5)。`CURRENT_SPEC`は文案 |
| R-14 | 完了 | 下記3 |
| R-15 | 完了 | `er121_family_y_audio_01.py`の「Std本文はchunk化しない」を是正済み仕様(2026-10-26 Std chunk対象)へ訂正 |

## 2. 残置(K)の確認
K-01(`LEGACY_COOLDOWN_SECONDS`・旧シグネチャ・旧LR helper・`max_attempts=1`旧LR retts)=scope外専用に残置。X/Y/Z専用module(er019/er121/er063/er122/er026/er127本体)に`er020.COOLDOWN_SECONDS`/`LEGACY_COOLDOWN_SECONDS`参照0件(Grep G-1、静的test固定。er127内の文字列は定義コメント1件のみ)。
K-02(Trial/観測の独自定数)・K-03(stop_retrying)・K-04(`min(max_attempts,3)`)・K-05(F-Tech)・K-06(SHELL_EN)・K-07(Z Adv外側ループ)・K-08(Gate規則)・K-09(ER-011安全上限)=変更なし(`git diff 3af84a499 HEAD`で該当行に差分なし)。

## 3. 旧test更新
| test | 処置 |
|---|---|
| `er122_fz_ctx_policy_test_01.py` | 600→180(`cooldown_seconds()==er127.COOLDOWN_SECONDS==180`、`LEGACY=600`を明示)、resume系を180秒基準に |
| `er122_fzcw_runtime_evidence_test_01.py` | 2clip×600=1200 → 2clip×180=360 |
| `er063_fz_ctx_wiring_test_01.py` | 600→180。`test_w11b`は`_kp_en_two_stage`のer127差込み4種を除くと基準commitと同一、と再表現 |
| `er063_family_z_audio_01_test_01.py` | fixture値600→180 |
| `er078_asr_unified_wiring_10_test_01.py` | force_secondary=True固定call siteを1箇所→2箇所(Std ③=crosslevel、KP解説③=`_kp_explanation_unified`) |
| `er109_xz_isolation_01_test_01.py` | scope読取importerに`er127_tts_block_policy_01.py`(読取のみ)を追加 |
| `er019_family_x_fx_20261016_wiring_01_test_01.py` | `generate_key_phrase_component_verified`署名に`_blk`、K2 store利用者にer127 test、`fallback_used`読取元にer127/crosslevel(自分のresult dictのみ) |
| 変更なし(legacy golden) | `er020_tts_retry_local_rewrite_01_test_01`・`er007_ja_tts_retry_path_fix_test_01`・`er026_family_z_stop_sentinel_test_01`・`er058_asr_tts_prodfix_01_test_01`・`er003_lr_post_rewrite_outer_loop_fzaq8_test_01` 等(scope外の旧挙動を固定。scope内の対応は`er127_tts_block_policy_01_test_01`に新設) |
注意: `er122_*_test_01.py`・`er063_fz_ctx_wiring_test_01.py`等はpytest形式のため`run_project_regression.py`(unittest discover)では収集されない。更新後に`pytest`で確認した。

## 4. Dangling Reference Grep(G-1〜G-11)
| # | pattern | 前 | 後(全体/ファイル数) | X/Y/Z専用module(非test)後 | 判定 |
|---|---|---|---|---|---|
| G-1 | `COOLDOWN_SECONDS` | 26件/10 | 40件/13(er127本体・test追加分) | `er020.`/`retry_primitive.`参照0、正式定義`er127:30`のみ | 合格 |
| G-2 | `maybe_cooldown_before_attempt` | 25件/14 | 30件/17(test・golden増) | 呼出は`crosslevel:211`/`repro01:352`/`news_tail:205`/`voice01:222`(いずれもscope外分岐)・定義`er020:69`。X/Y/Z専用moduleは0(説明コメント1) | 合格 |
| G-3 | `max_attempts=1`(LR文脈) | 3箇所 | 3箇所(`voice01:445`・`news_tail:453`は旧helper内、`crosslevel:344`はdocstring) | scope内LR経路0 | 合格 |
| G-4 | `_local_rewrite_recovery_for_` | 38件/12 | 39件/13 | X/Y/Z専用module 0。leaf内の呼出は旧分岐(`crosslevel:299,329`/`news_tail:377,408`/`voice01:380,405`)のみ。`er053_family_x_open256_runtime_01.py`は旧helperを直接呼ぶ観測toolで影響なし | 合格 |
| G-5 | `600秒`・`固定600`・`10分` | 74件/42 | 84件/47 | er063/er122/er122_fzcw_runtime_evidence_01は新仕様注記つきのみ(旧決定の履歴注記)。voice01/news_tail/crosslevel/repro01/er020の旧記述はscope外分岐の説明 | 合格(履歴・legacy明示注記のみ) |
| G-6 | `KP_EXPLANATION_MAX_ATTEMPTS` | 5件/3 | 9件/3 | 定数を1ブロック試行数として注記訂正、`_kp_explanation_unified`が使用 | 合格(新仕様注記つき) |
| G-7 | `prior_generations\|cooldown_total_budget\|generations_used` | 86件/32 | 92件/33 | er063:933,954/er122:249(Z Adv会話の外側ループ=K-07据置)・`tts_generations_used`(会計項目)。L4の周回は新分岐が不使用 | 合格(K-07/scope外の残置) |
| G-8 | `minimal_fallback`のAdv gate記述 | — | Gate規則不変。③採用でtop-level正規化(M-5) | `GateContractTests`で検知を固定 | 合格 |
| G-9 | 「4回目以降は絶対にTTS生成しない」等 | — | `er011`コメント・`CURRENT_SPEC`に残存 | er011は編集禁止、CURRENT_SPECは編集権限なし | 文案をFableへ |
| G-10 | scope外golden | — | A/B/C leaf出力byte同一(80ケース、既知欠陥4件除外) | `GoldenTests`7本PASS | 合格 |
| G-11 | OPEN-376/312/536/538 | — | 解消根拠: 376=`LrAndHrqTests`(再入禁止・LR<=1)、312=`StyleVoiceTests.test_lr_block_keeps_caller_style_then_fallback_third`、538(D11)=`RoleTests`。536は未確認(本委任の範囲外) | 状態更新はFable | 文案添付 |
