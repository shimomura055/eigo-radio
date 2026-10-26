# DESIGN_02 — DESIGN_01からの差分(Opus M-1〜M-4 / R-1〜R-8 とFable判定の反映)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02 / 性質=承認済み仕様(fx_20261017継承)とY runnerの乖離是正(11-8 B・T1)。新Style・新Prompt・新flag・Voice変更・Adv Comment 2復活・本文改変なし。
DESIGN_01(`DESIGN_01.md`)の方式(X方式`resolve_run_profile`+固定記録+M3、新run dir)は変更しない。以下はDESIGN_01との差分のみ。

## 1. Opus必須(M-1〜M-4)の反映
| ID | 反映内容 | 実装箇所 |
|---|---|---|
| M-1 | 網羅検査は`x_gate.checked`ではなく、Y側期待集合`Y_ROLE_COVERAGE`(role×level×segment)と『実際にevaluate_segment_evidenceを実行した集合』の**完全一致**で判定。不足=`Y_STYLE_COVERAGE_EMPTY`、期待外=`Y_STYLE_COVERAGE_UNEXPECTED`、role表とprofileのrole集合の不一致=`Y_STYLE_ROLE_TABLE_DRIFT`。chunk化したYのsegmentは『全chunkが検査された場合のみ検査済み』 | `er121_family_y_audio_01.py` `Y_ROLE_COVERAGE`/`y_expected_coverage`/`y_style_gate` |
| M-2 | legacy waiverは**作らない**(`--style-profile`/`--legacy-style-waiver-ref`のCLIを追加しない)。runnerはYの承認profileだけを`resolve_run_profile`へ渡す。既存run state(TTS結果/Review Lock/人間承認)があり固定記録のないdirは、Xと同じM2で課金前STOP。旧run(`run_01`/`run_voice_puck_ev_01`等)の再pagesは不要のため救済経路を作らない(waiver機能自体への制限は本委任範囲外=設計記載のみ) | `er121_family_y_runner_01.py` `resolve_style_profile` |
| M-3 | Voice 1〜3(Std/Adv 6 segment)は「S9未評価のユーザー判断項目」として旧`_02`(default)と新版をsegment単位で並べた比較節を公開ページに置く(`COMPARISON_01.md`/公開`_03`)。Fable受入でも「完成」「PRODUCTION_WIRED」とは呼ばない。V2(Voice本文のみdefault維持)は本委任で実装しない(新例外=ユーザー判断後に別委任) | 公開`_03`・`COMPARISON_01.md` |
| M-4 | `audit/style_actual_vs_approved.json`の日本語role(SUPPORT_JA/KP_JA_MEANING)は、entryのtop-level `style_prefix`(送信instruction。再利用でも生成時の値が保持され、`attach_segment_profile_record`で上書きされるのは`style_profile`記録のみ)のsha256を実測値とする。取れない場合は`measured_kind="意図sha(実測なし)"`・`match=false`とし、`JA_STYLE_ACTUAL_UNMEASURED`でBLOCK(一致扱いにしない)。X実run(`fxpw_01_s3prod`)で`style_prefix==承認text`を確認済み(厳密一致) | `y_style_gate` |

## 2. Opus推奨(R-1〜R-8)の扱い
| ID | 採否 | 内容 |
|---|---|---|
| R-1 | 採用 | 前後比較表にWPM(秒数/語数から算出)を入れる(`COMPARISON_01.md`) |
| R-2 | 採用 | V2実装は無いため該当なし。DESIGN_01 2-2-4のV2案で`_base`を使う場合はStdで`_base_slower`にする(注記のみ) |
| R-3 | 不採用(本委任範囲外) | er127(TTS統一)が短文Styleを承認済み通常成功経路にする場合の『採用attempt番号+承認Style変種一覧』Gate参照は、er127確定後のY Gate改修(次委任)。現Gateは`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`で保守的にBLOCKする(fail-closed維持) |
| R-4 | 採用 | profile有効化でAdv `ADV_MINIMAL_FALLBACK`/Std `STD_FALLBACK_USED_OR_UNKNOWN`がYにも効く。HR待ち件数を`REGEN_RESULT_01.md`/`COMPARISON_01.md`に記録 |
| R-5 | 採用 | Style不変の5 clip(約2.5円)を再生成する理由=音声再利用機構が同一out_dir限定で、新dirへの引継ぎ機構を新設しない(`REGEN_PLAN_01.md` §4 案R) |
| R-6 | 採用 | KP英語(K2)がStd/Advで同じMaster Store keyを共有する場合のStore hit件数を記録 |
| R-7 | 採用 | `er121_family_y_style_profile_test_01.py`の`TestCrossFamilyRegistry`: X/Y/Z runnerをglobで列挙し、登録表に無ければFAIL。登録済みaudio runnerにはStyle配線markerが存在することを検査(X: `resolve_run_profile`等、Z: `assert_style_table_integrity`、Y: `resolve_style_profile`等)。Entertainment/Trial runnerは免除理由つきで登録 |
| R-8 | 採用 | `er019_family_x_style_profile_01.py`は編集しない(`m3_assembly_gate`のdefault分岐も不変)。Yの入口で『新規runは承認profile必須』を`resolve_style_profile`のassertで保証(承認profile以外はYE2EStop) |

## 3. Opus見落としリスクの扱い
1. 再利用entryの意図sha自己一致 → M-4で日本語roleは送信instruction実測。さらにY経路での`migrate_record`使用をAST testで禁止。
2. Puck×PD06(177字)のretry率は未知 → Cap60円内。実測を`REGEN_RESULT_01.md`へ。
3. Gate内でも`read_record`を正とし、引数と食い違えば`Y_STYLE_PROFILE_ARG_DISAGREES_WITH_RECORD`でBLOCK。
4. 並行作業 → OPEN-527 testの`r.STYLE_PROFILE`参照は`ya.Y_APPROVED_STYLE_PROFILE`へ更新(旧名は撤去しAttributeErrorで検出)。er127未コミット変更は取り込まず、Family runner call siteは触らない。

## 4. DESIGN_01との差分(実装上の決定)
- profile名の単一ソースは`er121_family_y_audio_01.py`の`Y_APPROVED_STYLE_PROFILE`(Gateが同moduleで使うため。runnerは`_ya().Y_APPROVED_STYLE_PROFILE`を参照。DESIGN_01の「runnerにリテラル」から変更)。
- `YContext.style_profile`/`style_profile_source`を追加。`build_real_context`は`_launch_guard`の後・`load_dotenv`/client生成/cost logger install**前**に`resolve_style_profile`を呼ぶ(課金前STOP)。`build_mock_context`も同関数を呼ぶ。dry-runは`write=False`で報告のみ。
- `_style_profile(ctx)`: 各stage(`_tts_input_sha`/`stage_tts`/`stage_gate`/`stage_assemble`)の入口で未解決/承認profile以外/固定記録欠落・不一致をSTOP。
- `y_style_gate`は承認profileで検査できない場合(記録欠落/不一致/承認外/引数不一致)は評価に進まず必ずBLOCK(`y_profile_blocked`)。`gate_summary.json`に`y_profile_blocked`/`coverage`を追加。level別`{a2,b1b}/audit/style_actual_vs_approved.json`と統合版`audit/style_actual_vs_approved.json`を出力。
- mock(`er121_family_y_mock_01.py`)の偽TTSは『送ったStyle(`style_prefix_override`)をentryに記録する』形に変更(本物の下位関数と同じ。KP偽関数はK2 Store key・profile記録を付ける)。Gateの実測照合をmockが空振りさせないため。
- legacy `default`経路の撤去: `STYLE_PROFILE = "default"`(runner)、`generate_y_*`の`style_profile="default"`既定、mock KP偽関数の`style_profile="default"`既定。残置(意図): Xの`PROFILE_DEFAULT`と`resolve_role_style`のdefault素通し(X/Z/legacy用)。
