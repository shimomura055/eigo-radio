# -*- coding: utf-8 -*-
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: runtime_evidence_*.out.json から RUNTIME_EVIDENCE_01.md を機械生成する(貼付ミス防止。API 0)。
import json, os, re

D = "docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01"


def J(n):
    return json.load(open(f"{D}/runtime_evidence_{n}_01.out.json", encoding="utf-8"))


def block_only(txt):
    return txt.split("===== 固有名詞発音アラーム報告")[0].rstrip()


def row(r, keys):
    return "| " + " | ".join(",".join(map(str, r.get(k))) if isinstance(r.get(k), list) else str(r.get(k)) for k in keys) + " |"


e0, e1, e1b, e1c, e2, e3 = J("e0"), J("e1"), J("e1b"), J("e1c"), J("e2"), J("e3")
out = []
w = out.append
w("# RUNTIME_EVIDENCE_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A。**実走の出力を機械的に貼付**。生成: `tools/make_runtime_evidence_md_01.py`)")
w("")
w("## 0. 実験構成(何が本物で、何が代替か)")
w("- **本物**: Production判定の実コード(`n3_tts.generate_a2_japanese_with_reading_safety` -> `generate_narration_snippet_verified_strict` -> `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail` -> 新module `er078_ja_v2beta_01`、`unified_judge`無改変)、"
  "実scope(`er109_xz_scope_01.run_scope`: Xは`generate_family_x_a2_segments`、Yは`generate_y_a2_segments`、Zは`run_tts_stage`が自ら設定)、実run単位Secondary hook(`with_secondary_run`)、"
  "実Family完了hook(`write_listening_list_safe(completion_label=...)`)、実ASR(OpenAI `gpt-4o-mini-transcribe` + Azure Speech `azure-speech-stt`、Production routing `er006_asr_provider_routing_01`)。")
w("- **代替(唯一)**: TTS。`er003_b1_p9a_audio.generate_narration_snippet`だけを、保存済みの実wav(月タイトル6本=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_{ms_03,reselect_01}/a2/narration/attempts/japanese_title_attempt{1,2,3}_*.wav`)を`out_path`へコピーする関数に差し替え(Gemini TTS 0円・声/モデル不変の既存wav再利用)。")
w("- **書込先**: すべて一時dir(`%TEMP%/ja_v2beta_rt_*`)。Production results・Master Audio Store・承認記録・Production監査ログ/HR queueへは書かない(`test_state_isolation_01`でattempt_history/HR queueをtmpへ退避。Y fixtureは既存Y run `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`のjson 5本のみを一時dirへコピー)。")
w("- 全有料phase前に`tools/stop_scope_check_01.py`をrc=0で確認(`stop_check_*_paid.json`)。費用はCOST_01.md。")
w("- **制約(正直に)**: Y/Z familyは記事全体のfixture無しで`japanese_title`1 Sectionのみを選択して実走(`_ONLY_SEGMENTS`/`only_clips`)。Familyの組立・試聴ページ全体の生成は未実走(節のrender関数は実際の呼出し=同じ`render_html_section(load_listening_list(...))`/`_y_pww_aux_html`を実行)。")
w("")
w("## 1. E0(API 0): 保存済み転写を実Production経路(X scope)に注入 -> 月6本 = 4 PASS_W / 2 HR")
w("Primary=各attempt jsonの`asr_text`、Secondary(Azure)=EVAL_UNIFIED_03 §1aの記録。OpenAI/Azure呼出はstub、ネットワークはsocket guardで遮断。")
w("")
w("| draw | verdict | reason_code | rescue_basis | warnings | judge_rule_version | 期待(委任文) |")
w("|---|---|---|---|---|---|---|")
for r in e0["rows"]:
    w(row(r, ["label", "verdict", "reason_code", "rescue_basis", "warnings", "judge_rule_version", "expected"]))
w("")
w("scope外(None=A/B/C相当)で同じ6転写を判定: 新キー(`ja_v2beta`/`verdict`/`rescue_basis`/`judge_rule_version`)は**全行で無し**、判定は従来(L0)のまま。")
w("")
w("| draw | state(従来) | reason_code | 新キーの有無 |")
w("|---|---|---|---|")
for r in e0["scope_none_rows"]:
    w(f"| {r['label']} | {r['state']} | {r['reason_code']} | {r['has_new_keys']} |")
w("")
w("## 2. E1(有料・実ASR): 同じ6本の実wavを実ASRで判定(X scope、1 attempt、3 draw)")
w("**重要な観測**: OpenAI `gpt-4o-mini-transcribe`のPrimary転写は、**同一wavでも呼出しごとに変わる**(下表)。判定は転写に対して決定的(E0・単体testで固定)だが、wav -> verdictは転写の揺らぎで変わる。"
  "保存済み転写での4/6は『その転写がその形だった場合』の値であり、同じwavを新たに再ASRすると2〜3/6になった。"
  "これは新方式の欠陥ではなく、Primary ASRの非決定性(従来から存在)の露出。ASR再試行は承認済み仕様(UDR #204)で不採用のため、本IDでは是正しない(報告のみ)。")
w("")
for name, d in (("draw 1 (e1)", e1), ("draw 2 (e1b)", e1b), ("draw 3 (e1c)", e1c)):
    w(f"### {name}")
    w("| wav | verdict | reason_code | rescue_basis | Primary転写 | Secondary転写 | 費用(audit) |")
    w("|---|---|---|---|---|---|---|")
    for r in d["rows"]:
        w(f"| {r['moon_label']} | {r['verdict']} | {r['reason_code']} | {r['rescue_basis']} | {r['primary_text']} | {r['secondary_text']} | {r['audit_cost_est_jpy_sum']} |")
    w("")
cnt = [sum(1 for r in d["rows"] if r["verdict"] == "PASS_W") for d in (e1, e1b, e1c)]
w(f"PASS_W件数(3 draw): {cnt} / 6。HRは従来どおりの根拠(`p1_value_diff`/`secondary_not_accepted`/`p2_exclusion`)で、新層による誤った救済は無い。")
w("")
w("model_id / routing(1件分。全rowの`asr_judgement.r5.models`に同形で記録):")
w("```json")
w(json.dumps(e1["rows"][1]["r5"]["models"], ensure_ascii=False, indent=1))
w("```")
w("")
w("## 3. E2(有料・実ASR): X / Y / Z それぞれ family関数で 1 Section(`japanese_title`)")
w("音声=`reselect a2`(E1の3 drawすべてでPASS_Wになった音声。ただし実ASRの誤転写で落ちる draw もある=3-F)。Family関数がscopeを自ら設定し、生成+Secondary hook+完了hookまで実走。本表・§4は最終run(run4。fallback経路も偽TTS化後)。")
w("")
w("| Family | 実走した関数 | status | verdict | reason_code | rescue_basis | judge_rule_version | model_id(primary / secondary) | 費用 audit vs RunState |")
w("|---|---|---|---|---|---|---|---|---|")
for k in "XYZ":
    s = e2[k]["summary"]
    m = (s["r5"] or {}).get("models") or {}
    pm = (m.get("primary") or {}).get("model")
    sm = (m.get("secondary") or {}).get("model_id") if m.get("secondary") else None
    snap = (s.get("run_state_snapshots") or [{}])[0]
    w(f"| {k} | {s['label']} | {s['status']} | {s['verdict']} | {s['reason_code']} | {s['rescue_basis']} | {s['judge_rule_version']} | {pm} / {sm} | audit {s['audit_cost_est_jpy_sum']} = RunState {snap.get('est_jpy_total')} (Secondary呼出 {snap.get('secondary_calls')}) |")
w("")
zc = e2["Z"]["summary"]["audit_cost"] or {}
zs = (e2["Z"]["summary"].get("run_state_snapshots") or [{}])[0]
w(f"**β追加Azure費用の整合(M-2)**: Zの実走ではβが発火(`rescue_basis={e2['Z']['summary']['rescue_basis']}`)。監査record `cost`={json.dumps(zc, ensure_ascii=False)} は、"
  f"run単位`RunState.est_jpy_total`({zs.get('est_jpy_total')})・`secondary_calls`({zs.get('secondary_calls')})と一致。raw usage log(`raw_usage_log_runtime_evidence_e2_01.jsonl`)にもAzure 1件(`azure_stt_strict_scg`)。")
w("")
for k in "XYZ":
    s = e2[k]["summary"]
    w(f"### 3-{k}. Family {k}: 新方式の記録(抜粋)")
    w("```json")
    w(json.dumps({"state": s["state"], "verdict": s["verdict"], "reason_code": s["reason_code"], "rescue_basis": s["rescue_basis"], "rescue_reason_ja": s["rescue_reason_ja"],
                  "judge_rule_version": s["judge_rule_version"], "warnings": s["warnings"], "ja_v2beta.layers": s["ja_v2beta_layers"], "ja_v2beta.error": s["ja_v2beta_error"],
                  "primary_text": s["primary_text"], "secondary_text": s["secondary_text"], "segment_statuses": s["segment_statuses"]}, ensure_ascii=False, indent=1))
    w("```")
    w("")
e2s = json.load(open(f"{D}/runtime_evidence_e2_stopped_run3_01.out.json", encoding="utf-8"))
w("### 3-F. 失敗経路の最終成果物(同じ音声・同じ実Production経路で、実ASRが3回とも誤転写した draw。`runtime_evidence_e2_stopped_run3_01.out.json`)")
w("実ASR(OpenAI mini)は同一wav(`reselect a2`)を『発線900本超』『8000級本超』と誤転写し、標準2回が `NG_PROTECTED/p1_value_diff`(従来どおりの根拠・新層は救済せず)。"
  "この draw では minimal-instruction fallback の3回目が**ハーネスの不備**で実TTSへ出ようとして通信監視に止められた(= 3回目のASRまで到達せず STOPPED。実TTSは呼ばれていない・費用0)。"
  "run4でfallback経路も偽TTSにし、全familyでPASS_Wを得ている。失敗経路としての最終成果物は次のとおり: segment status=STOPPED・HR Lock登録1件・完了ブロックは新方式PASS_W『0件』と『要Human Review: japanese_title』を明示・組立/納品候補は従来どおりGateで止まる(PASS_Wではないため)。")
w("")
for k in "YZ":
    sm = e2s[k]["summary"]
    w(f"- Family {k}: segment status=`{sm['segment_statuses'].get('japanese_title')}`")
    w("```")
    w(block_only(e2s[k]["completion_block_stdout"]))
    w("```")
w("(注: Zの失敗entryは `asr_judgement`/`attempts_log` に判定recordを持たない形式のため、完了ブロックの『JA判定record 0件』はZ失敗segmentでは判定回数を反映しない[既存のZ失敗entry形式の制約。HR Lock登録とSTOPPEDは正しく報告される]。)")
w("")
w("## 4. 最終制作報告の掲載例(実走から生成。完了ブロック=標準出力、JSON=`audit/pass_with_warning_listening_list.json`、試聴ページ節)")
for k, title in (("X", "Family X a2(Standard)"), ("Y", "Family Y a2(Standard)"), ("Z", "Family Z a2")):
    w(f"### 4-{k}-1. 完了ブロック(標準出力。{title}。固有名詞アラーム報告は省略=同JSONに全文)")
    w("```")
    w(block_only(e2[k]["completion_block_stdout"]))
    w("```")
    w(f"### 4-{k}-2. JSON(`pass_with_warning_listening_list.json`の`entries[0]`と`ja_v2beta_summary`)")
    lst = e2[k]["listening_list_json"]
    ent = dict(lst["entries"][0])
    ent["audio_path"] = "<一時dir>/" + os.path.basename(ent.get("audio_path") or "")
    w("```json")
    w(json.dumps({"count": lst["count"], "entries[0]": ent, "ja_v2beta_summary": lst.get("ja_v2beta_summary")}, ensure_ascii=False, indent=1))
    w("```")
    note = "(dev試聴ページ。公開(public)ページには出ない=下記)" if k == "Y" else ""
    w(f"### 4-{k}-3. 試聴ページ節HTML(`render_html_section`の出力){note}")
    h = e2[k].get("section_html") or e2[k].get("y_dev_page_section_html")
    h = re.sub(r'src="[^"]*"', 'src="<音声path>"', h)
    w("```html")
    w(h)
    w("```")
    if k == "Y":
        w(f"Y公開(public)ページの節出力: `{e2['Y']['y_public_page_section_html']!r}`(空=公開物に内部の判定情報を出さない設計どおり)。")
    w("")
zb = e2.get("Z_with_beta_sample")
if zb:
    w("### 4-Zβ. v2 + β混在の完了ブロック(Z a2のv2/β例 + E1の実β判定record=`" + zb["beta_sample_source"] + "`を同じ試聴リストに載せて生成)")
    w("```")
    w(block_only(zb["completion_block_stdout"]))
    w("```")
    w("")
w("## 5. E3(有料・実ASR): 負例とscope外")
w("同じ音声(`reselect a2`)に対し、**原稿の数値だけを誤り**にした負例を判定(期待=NG/HR、`rescue_basis=None`)。")
w("")
w("| 条件 | scope | status | verdict | state | reason_code | rescue_basis | Primary転写 |")
w("|---|---|---|---|---|---|---|---|")
for r in e3["rows"]:
    w(f"| {r['label']} ({r['canonical_text']}) | {r['scope']} | {r['status']} | {r['verdict']} | {r['state']} | {r['reason_code']} | {r['rescue_basis']} | {r['primary_text']} |")
w("")
w("scope外の行の新キー有無: " + str([r.get("has_new_keys") for r in e3["rows"] if r.get("has_new_keys")]))
w("(この1本は、実ASRのPrimary転写がその回に崩れたため従来NGだった。scope外=従来出力の同一性は、保存済み転写での§1の表と、`gen_golden_scope_none_01`の396判定byte一致[TEST_RESULTS_01.md]で確認している。)")
w("")
w("## 6. 月タイトル6音声の新判定(再掲。保存済み転写=EVAL_UNIFIED_03と同じ決定対、R-1 OFF、配線後のProduction判定)")
w("| draw | 判定 | reason_code | rescue_basis | 警告 | 扱い |")
w("|---|---|---|---|---|---|")
for r in e0["rows"]:
    nm = r["label"][3:].replace("_", " ")
    if r["verdict"] == "PASS_W":
        how = "PASS_W(非ブロッキング。試聴は任意・推奨)" + ("。**証拠が最も弱い**(Secondary読み相違あり。試聴推奨)" if "JA_COMPOSITE_SECONDARY_READING_CONFLICT" in (r["warnings"] or []) else "")
    else:
        how = "HR(従来どおり。既存HR Lock -> 個別採用[HUMAN_APPROVED]で扱う。UDR #203=未決。本IDでは判断しない)"
    w(f"| {nm} | {r['verdict']} | {r['reason_code']} | {r['rescue_basis']} | {','.join(r['warnings'] or [])} | {how} |")
w("")
w("**ユーザーの既試聴判断との整合(1行)**: ユーザーは6音声を試聴して全てOKと判断済みで、新判定の4本(PASS_W)はその判断と矛盾せず(機械が通した音声にユーザーNGのものは無い)、残る2本(ms_03 a1・reselect a3)はユーザーがOKでも機械はHR扱いのまま=既存HR Lock -> 個別採用(HUMAN_APPROVED)で扱い、既存のHUMAN_APPROVED記録は変更していない。")
w("")
w(f"**実wavの再ASR(§2)**: 同じ6本を新たにASRすると PASS_W は draw別に {cnt} / 6(OpenAI miniの転写が呼出しごとに変わるため。保存転写の4/6は上限に近い値)。6本すべてが機械PASSになることは合格条件にしない(ユーザー原文§5)。")
w("")
open(f"{D}/RUNTIME_EVIDENCE_01.md", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("wrote RUNTIME_EVIDENCE_01.md", len(out), "lines")
