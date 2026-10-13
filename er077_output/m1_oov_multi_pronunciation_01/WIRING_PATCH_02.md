# WIRING_PATCH_02 M1 複数発音候補 module の配線差分案(委任_03で適用。本委任では既存Production file無編集)

管理ID: ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 / 対象module: `er006_m1_multi_candidate_01.py`(新規・未importのまま) / 行番号は2026-10-13時点(適用時にGrepで再確認)

## 0. 設計方針(最小差分)
- 配線ファイルは実質 **`er006_secondary_asr_01.py` 1つ**。Primary#1/P2/S1/S2/forced-secondary/減速後rescue(`er003_v1_n3_01_tts_generate.py` L146は`evaluate_attempt_with_cascade_detail`を呼ぶだけ)/dialogue/point_headings(`evaluate_attempt_with_cascade`→`_detail`)/KPは全て`evaluate_attempt_with_cascade_detail`を通る(grepで確認: 呼出元は`er003_v1_n3_01_tts_generate.py`・`er003_v1_*`・`er003_v1_sing01_*`・KP等のwrapper経由)。**呼出側(retry loop)の編集は不要**。
- **凍結(OF-179)**: `evaluate_attempt_with_cascade_detail`の入口で`_m1_frozen_for(canonical_text)`を呼ぶ。プロセス内dict(key=canonical_text)に最初の呼出時(=そのsegmentの最初の試行)だけ`freeze_candidates`で作り、以降のretry/fallback/regen/減速後(同一canonical_text)は**同じ凍結物を再利用**(再計算しない)。Ledger読込は`pronun_ledger._load()`の1回スナップショット、`segment_started_at`=凍結時刻。Tier3の`upsert`がcascade末尾で走っても凍結物は不変。例外時は`None`(M1不発=従来挙動、fail-closed)。テスト用に`_reset_m1_freeze_cache()`を用意。
- 追加kwarg: `evaluate_attempt_with_cascade_detail(..., m1_enabled: bool = True)`(既定True)。`cascade_enabled=False`は既存のearly return(L729)で到達しないため**自動的に不発**(OF-174)。`language != "en-US"`は`m1_multi_candidate_judge(lang=…)`が不発(R_LANG)。

## 1. 差分 A: import・helper(`er006_secondary_asr_01.py` L150-161のimport群の後)
```python
import er006_m1_multi_candidate_01 as m1_multi   # 委任_03で追加

_M1_FROZEN_CACHE: dict = {}

def _reset_m1_freeze_cache() -> None:
    _M1_FROZEN_CACHE.clear()

def _m1_frozen_for(canonical_text: str):
    """segment最初の試行前に1回だけ候補集合を凍結(OF-179)。同一canonical_textの2回目以降は同じ凍結物を返す。失敗時None(M1不発)。"""
    if canonical_text in _M1_FROZEN_CACHE:
        return _M1_FROZEN_CACHE[canonical_text]
    try:
        snap = copy.deepcopy(pronun_ledger._load())
        fz = m1_multi.freeze_candidates(canonical_text, ledger_snapshot=snap, segment_started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
    except Exception:
        fz = None
    _M1_FROZEN_CACHE[canonical_text] = fz
    return fz

def _m1_try(canonical_text, asr_text, cls_step, frozen, *, language, m1_enabled, secondary_text=None, step_name):
    """M1を試し、受理なら(label, audit)、不受理なら(None, audit|None)。例外はfail-closedでNone。"""
    if frozen is None or not m1_enabled:
        return None, None
    try:
        r = m1_multi.m1_multi_candidate_judge(canonical_text, asr_text, frozen, base_cls=cls_step, secondary_asr_text=secondary_text,
                                              m1_enabled=m1_enabled, lang=language)
    except Exception as exc:
        return None, {"m1_error": f"{type(exc).__name__}: {exc}", "step": step_name}
    audit = dict(r.audit, step=step_name, reason=r.reason)
    return (m1_multi.ACCEPT_REASON if r.accepted else None), audit
```
(`copy`/`time`のimport有無を確認して追加。)

## 2. 差分 B: 各step(いずれも`should_pass`/`_step_alternate_pass`が偽だったときの直後)
共通の受理処理(既存`immediate_label`分岐と同形): `result["verified"]=True; result["stop_retrying"]=False; result["final_status"]=m1_multi.ACCEPT_REASON; result["m1_multi_candidate"]=audit; steps.append({"step":"m1_multi_candidate", ...audit...}); return result`。不受理でも`audit`(no_match_reason付き)を`result["m1_multi_candidate_rejected"]`へ残す(telemetry、OF-184)。

| 位置(現行行) | step | 挿入 | secondary_text |
|---|---|---|---|
| L739-745 `immediate_label`の直後(`cascade_invoked=True`より前) | Primary#1 | `lab, au = _m1_try(canonical_text, asr_text, cls, frozen, step_name="primary_1", ...)` | `None`(後続stepで取れた転写は不使用) |
| L764-772 `_step_alternate_pass(cls_p2)`の直後 | Primary#2 | `cls_p2`/`text_p2`で同様 | `None` |
| L795-803 `_step_alternate_pass(cls_s1)`の直後 | Secondary#1 | `cls_s1`/`text_s1`、`secondary_text=asr_text`(Primary#1の転写=手元にある他方) | Primary#1転写 |
| L826-834 `_step_alternate_pass(cls_s2)`の直後 | Secondary#2 | `cls_s2`/`text_s2`、`secondary_text=text_s1 or asr_text` | 他方 |
| L711-725 forced-secondary: `cls_s_forced.should_pass`が偽のとき、HR化(`human_review_required=True`)の**前** | forced-secondary | `cls_s_forced`/`text_s_forced`、`secondary_text=asr_text`(Primary転写。Primaryは既にPASS済み) | Primary転写 |

- Primary#1での`secondary_text=None`は意図どおり(OF-183「両転写が手元にある場合のみ矛盾拒否」)。S1/S2/forcedでは手元にある他方の転写を渡し、`SECONDARY_CONTRADICTION`(他方がprotected failまたは内容誤り)なら非PASS。
- cost guard(L774付近)・Tier3(L628-680)の既存順序は変更しない。M1は追加ASR呼出なし(コスト0)。
- 既存の上限(`COST_GUARD_MAX_USD_PER_SEGMENT`・HR化・same_signature上限)は無変更。M1不受理なら従来どおり次stepへ進む。

## 3. 差分 C: 減速後再検証
- `er003_v1_n3_01_tts_generate.py` L146 `_post_slowdown_cascade_rescue`は`evaluate_attempt_with_cascade_detail`を呼ぶため**編集不要**(同一canonical_text=同一凍結物。`audit.step`に`post_slowdown_cascade`は既存`result["post_slowdown_cascade"]`で判別可能。必要なら`detail["m1_multi_candidate"]`を同dictへ転記する1行を追加)。
- L196付近の直接`classify_asr_match`は**M1対象外**(OF-164: L146 rescue経由のみ)。

## 4. 差分 D: KP(OF-185 案K-A)
- KP呼出(`enable_non_latin_cascade=True`経路)も同じ`evaluate_attempt_with_cascade_detail`を通るため、`m1_enabled`既定True=C1+C2が自動適用される。
- 効果測定先行: 配線前に`SSOT_DRAFT_02.md`のOPEN「KP効果測定」を実施する場合は、KP呼出側で`m1_enabled=False`を一時的に渡す(呼出側1行)。人手確認は**測定段階のみ**、runtime Gateにはしない。

## 5. 差分 E: D-2' docstring更新案(`er006_secondary_asr_01.py` L215-225付近)
現行: 「この関数が返す情報はHuman Reviewパッケージを充実させるためだけに使う。IPA→ARPAbet変換等による自動PASSの根拠には一切使わない。」
更新案: 「(D-2'限定置換, 2026-10-13 ユーザー承認『辞書未収録語は既存Pronunciation Ledgerや利用可能な発音情報から合理的な候補を取得する』)自動PASSの根拠に使うのは、**M1(`er006_m1_multi_candidate_01`)が、CMU未収録語かつLedgerのexpected/alternate IPA(canonical_spelling一致・sources非空・segment開始前のエントリ)を凍結候補として、F1の全差分点検とPattern A/B/C(f1_explained)で説明できる場合に限る**。それ以外(Tier3の調査結果の即時利用、ASR側転写からの後付け候補、綴りからの推定)は引き続き自動PASSの根拠にしない。」

## 6. 作業量見積(委任_03)
- 差分A/B/C/D/E: `er006_secondary_asr_01.py`のみ約60行追加(importとhelper約35行、step挿入5か所×約5行)。既存関数の戻り値キー追加のみ(後方互換)。
- 回帰test: `er006_m1_multi_candidate_01_test_01.py`(既存68件)に加え、配線test(5 step×受理/不受理、forced-secondary、cascade_enabled=False不発、en-US以外不発、凍結再利用、`m1_enabled=False`で従来挙動)を新規test fileで約15件。既存`er006_retry_cascade_prod_01*`系の回帰を再実行(共有ファイル追記testは禁止リスト参照)。
- 実機: `er077_m1_oov_multi_pronunciation_01_evidence_runner.py`(完成済みの隔離+plan。`--execute`本体のTTS/clipループは配線後に委任_03で追加実装、約40行)。推定¥3.3(24観測)。
- 並行Coffee run(ASR Validator使用中)との衝突回避: 配線commitはCoffee run完了(または停止)後に適用する。適用前に`git status`で`er006_secondary_asr_01.py`に他者の未commit差分がないことを確認。

## 7. 非実装(意図的)
- 所有格正規化(`Mello's`→`Mellos`)の再試行: 委任_01 offlineには有ったが本moduleでは凍結候補がcanonical語のみのため未移植(OPEN案)。
- ASR側OOVのstem+s救済(`cmu_stem+regular_s`): 未移植(取りこぼし側、誤PASSなし)。
- 子音骨格sanity check(OF-181任意項目): 未実装。
