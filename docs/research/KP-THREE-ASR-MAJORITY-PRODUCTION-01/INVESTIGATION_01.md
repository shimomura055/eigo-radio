# INVESTIGATION_01: 現行「KP英語phrase 両方PASS必須」(er096、OPEN-440)の配線点・流れ・X/Z差 (KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01)

2026-10-22 / API 0・JPY0 / コード行番号は作業時点のHEAD(`abe2d7407`以降の作業ツリー)。Production既存ファイルは未編集。
ユーザー原文=`docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_USER.md`(2,692文字、sha256=631a9561fb39de8c2e7adf61c534bfb541071686082af1f9468a81caa3d9aa85)。

## 1. 現行の判定フロー(置換対象)
`er078_asr_unified_judge_01.py`の`AttemptCtx.dual_required`(L266)=Trueのとき`unified_judge`が次を行う(KP英語phrase専用):
- audit`dual`キー作成 L391-398。Primary取得失敗=`NG_PRIMARY_ASR_FAILURE`、P1(値DIFF/否定差)・P2(除外表)は従来どおり短絡(`NG_PROTECTED`/`NG_EXCLUDED`)。
- Primary PASSでも「Azure転写に依存した救済」(`primary_rescued_by_secondary`)・AMBIGUOUS/length降格は「Primary自身のPASSではない」(L460-471)。Primary自身のPASSなら`dual["primary_pass"]=True`。
- **Primary NGでもSecondaryを必ず呼ぶ**(短絡しない、L471近辺。OF-KPD-P-05)。Secondary取得不能=`NG_SECONDARY_UNAVAILABLE`(L502, L541。PASS不可・技術STOP)。
- Secondary受理(`secondary_accept_fn`)時`dual["secondary_pass"]=True`。`primary_pass`なら`PASS`(`dual_agreed`、L596前後)。Primary非PASSなら`done()`が`NG_DUAL_PRIMARY_NOT_PASS`へ変換(L403-410)。Secondary不受理=`NG_BOTH`。
- `done()`(L400-421)が唯一の出口。`dual`時のみ`secondary_called/secondary_text/outcome`を埋める。

アダプタ`er006_secondary_asr_01.py`:
- `attempt_ctx["dual_required"]`でfail-closed(cascade OFFならPrimary単独で通さない) L853-860。
- 救済フラグ`signals["primary_rescued_by_secondary"]`(L1076-1085)、Secondary step名`secondary_dual`(L1090)、`AttemptCtx(dual_required=_dual)`(L1092)、dual PASS時にclassificationをSecondaryで上書きしない(L1150前後)、`NG_SECONDARY_UNAVAILABLE`のみの最終slotはHRに入れず技術STOP(L1167-1175 `_tech_only`)。
- `_secondary_accept`(L1106-1120)=`classify_asr_match`→`_step_alternate_pass`(CMU/同音救済)→M1(Secondary転写)。Whisperには**M1を適用しない**(より保守側)方針とする。

## 2. 配線点(Grepで全列挙。dual関連識別子 `kp_dual_reuse_ok|dual_pass_required|dual_required|kp_dual_check|+dual1|NG_DUAL_PRIMARY_NOT_PASS|NG_SECONDARY_UNAVAILABLE|KP_EN_PHRASE_DUAL_REQUIRED|dual_enabled`)

| 層 | ファイル:行 | 内容 | 新方式での扱い |
|---|---|---|---|
| flag/部品 | `er096_kp_dual_pass_01.py` L32(`KP_EN_PHRASE_DUAL_REQUIRED`)、L42(`dual_enabled()`)、L34(`+dual1`)、L83-100(証跡)、L108-143(`evaluate_dual`)、L172-232(`kp_dual_reuse_ok`)、L245-261(`KpDualReuseGate`)、L268-289(X default key/`ensure_..._x_dual`) | 両方PASS前提の証跡・再利用helper | 判定部のみ3-ASR多数決へ置換(§設計6) |
| 判定 | `er078_asr_unified_judge_01.py` L266, L391-410, L460-471, L596-600, STATES L47-53 | `dual_required`/`NG_DUAL_PRIMARY_NOT_PASS` | `done()`出口で多数決へ置換 |
| 引数 | `er078_asr_unified_attempt_ctx_01.py` L22-38 | `build_attempt_ctx(..., dual_required)` | 同名維持(§設計6の命名方針) |
| adapter | `er006_secondary_asr_01.py` L841-860, L914, L1076-1092, L1140, L1150-1175 | 上記 | Whisper tie-break closure・技術STOP分類を追加 |
| 生成 | `er003_v1_repro01_main_generate.py` L270-289(kwarg+KP以外ValueError), L373(`build_attempt_ctx`へ), L785(`_dual_circuit_open`), L806-860(KP2段+ENGLISH_LOCK前circuit確認) | 4回構成(Minimal/Styled 2+English Lock 2)、最終slotのみHR | 不変(回数・HR Lock意味) |
| X default | `er019_family_x_audio_production_runner_01.py` L705-707(`kp_dual_canonical`/`kp_dual_required`), L720-736(`kp_dual_reuse_ok`→再利用点1), L1061-1062(`+dual1` X専用関数), L1734(assembly audit) | 前回results再利用 | 判定helperが新方式になるだけ(呼出点不変) |
| X K2 | `er019_family_x_kp_en_k2_store_01.py` L62, L67-69, L83, L86, L116 | `_styled_two_stage` primary/lock、`KpDualReuseGate` key A/B | 不変 |
| X inheritance | `er019_family_x_validation_inheritance_01.py` L191-215 | `try_inherit_from_cached`(API 0。S1なし) | 保存Whisper転写がなければローカルWhisper(API 0)を呼ぶ拡張 |
| Z | `er063_family_z_audio_01.py` L735-752(再利用点6), L849-867(`_kp_en_two_stage` primary/lock), L1012-1013(entryへ`kp_dual_check`) | 同上 | 不変 |
| Store | `er006_master_audio_store_01.py` L111-163, L194-195, L230-246(`reuse_gate`、`kp_dual_check`の保存・復元) | gateのaction reuse/regenerate/technical_stop | 不変(キー`kp_dual_check`を読み書き) |
| test | `er096_kp_dual_pass_01_test_01.py`・`er096_kp_dual_pass_01_wiring_test_01.py`・`er078_asr_unified_wiring_10_test_01.py`ほか(`dual_required`/`NG_DUAL_PRIMARY_NOT_PASS`をassert) | 旧ルールをassert | 配線委任で更新(§設計9) |

KPのdual参照点は**6呼出点**(X default Minimal/Lock、X K2 primary/lock、Z primary/lock)と**再利用6点**(§設計6の表)に尽きる。Family A/B/Cへのdual引数伝播は0(AST testで固定済み)。

## 3. Store / resume / retry の流れ
- 生成: 1 attempt = 1 judge。dual NGは通常のNG attempt(次slotへ)。最大4回(`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`)、最終slotのNGのみHR queue。Azure障害のみのNGはHRに入れず技術STOP。
- 再利用(6点): `kp_dual_reuse_ok`が(1)wav実在/sha256 (2)保存`kp_dual_check`(canonical/sha一致・両Provider転写あり)を現行分類器でAPI 0再判定 (3)証跡なし→`allow_s1=True`ならPrimary保存転写+Azure 1回(S1)、`allow_s1=False`(inheritance)なら不可 (4)Azure障害=technical_stop(再利用も再生成もしない)。
- Storeのkey: K2はkey A/B(X専用)。X defaultは旧共有keyを上書きしない`+dual1`別key。**実Production manifestの実測**(`er006_output/master_audio_store_01/manifest.json`、440件): KP英語entryは旧共有key 354(v1 99/v2_margin030 255、いずれも`kp_dual_check`なし)・K2 48(うち`kp_dual_check`あり15)。**`+dual1` entryは本番Storeに0件**(証跡runは別Store)。したがって`+dual1`を維持しても改名しても本番Storeのorphan/再生成コストは0。

## 4. X / Z の差
- X: 前回results再利用(runner)・validation inheritance(API 0)・Store(K2 key A/B、default `+dual1`)の3系。Z: `generate_or_reuse_z`(前回results)とKP 2段(primary/lock)のみで、Store経由なし。
- 判定の呼出(`dual_pass_required`)・`kp_dual_check`保存はX/Zで同一helper。

## 5. 既存Production環境でのWhisper依存(重要な前提確認)
- **faster-whisper(small, cpu, int8)は既にProduction依存**: `er008_disfluency_qa_18._get_model`(`WhisperModel(size, device="cpu", compute_type="int8")`)が、KP英語を含む英語snippet生成の全verified音声に対し`disfluency_qa=True`(`er003_v1_repro01_main_generate.py` L795, 828, 852、K2 store `disfluency_qa=True`)で吃音QAとして**既に毎回**実行されている。さらに`er006_secondary_asr_01.py` L533-545(Connected Speech Equivalence層)も同じloaderを共有。よって新方式は「ローカルWhisperのProduction新規依存」ではなく、既存loader・既存モデルキャッシュの再利用。
- 実測(`whisper_env_check_01.json`): Python 3.14.6 / faster_whisper 1.2.1 / ctranslate2 4.8.1 / CPU 16コア。モデルキャッシュ=`C:\Users\tensh\.cache\huggingface\hub`(tiny/small/medium)。import 0.40秒・small初回ロード2.0秒・1 KP clipあたり平均2.07秒(初回2.20、最大2.42、n=12、音声長0.98〜1.94秒の短いclip)。`HF_HUB_OFFLINE=1`でもキャッシュから転写成功(offline 4.22秒=ロード込み)。
- 注意: `_get_model`は`local_files_only`未指定=キャッシュ欠落時のみネット取得(初回のみ)。Production環境=このWindows環境(venv)で既に取得済み。

## 6. 固有名詞アラーム方式(PNAP、並行設計中)との境界
PNAP(OPEN-450)はKP以外のsegmentの最終救済。KPは対象外。KPに固有名詞が含まれる場合も3-ASR多数決がそのまま適用される(緩和なし)。PNAPが`er103_*`を新設して別経路で動くため、本件(判定は`unified_judge`のdualブランチ内)とは同一関数を触るが、PNAPは`NG_BOTH`後の救済でありdual branchの外(競合は配線委任でPNAP配線後のgit差分を再確認)。
