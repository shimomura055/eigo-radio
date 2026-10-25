# OPEN-333系(しわ↔すわ=N3-07)判定経路のProduction実行trace。API 0(socket guard)・Production file無変更・読取専用。
# 再現: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_trace_01.py
import difflib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
E.api0_guard_on()


def trace(canon, asr, tag):
    print(f"--- {tag}: canon={canon!r} asr={asr!r}")
    cn, an = javal.normalize_ja(canon), javal.normalize_ja(asr)
    sm = difflib.SequenceMatcher(None, cn, an, autojunk=False)
    for op in sm.get_opcodes():
        if op[0] != "equal":
            print(f"  opcode {op[0]}: canon[{op[1]}:{op[2]}]={cn[op[1]:op[2]]!r} -> asr[{op[3]}:{op[4]}]={an[op[3]:op[4]]!r}")
    p = javal.protected_check_ja(cn, an)
    print(f"  protected_check_ja: passed={p.passed} number_mismatches={p.number_mismatches} negation_mismatches={p.negation_mismatches}")
    print(f"  content_diffs(Candidate Eが見る集合)={[ (d['canonical'], d['asr']) for d in p.content_diffs]}")
    for d in p.content_diffs:
        cv, av = VL._kanji_candidate_reading_variants(d["canonical"]), VL._kanji_candidate_reading_variants(d["asr"])
        print(f"    E候補: {d['canonical']!r}={sorted(cv) if cv is not None else None} / {d['asr']!r}={sorted(av) if av is not None else None} 共通={sorted((cv or set()) & (av or set()))}")
    cd, ad = VL.prepare_text_for_candidate_d1(canon), VL.prepare_text_for_candidate_d1(asr)
    print(f"  D-1正規化: canon={cd!r} asr={ad!r} 文字列一致={cd == ad} morph読み一致={VL._reading_equal_morph(cd, ad)}")
    r = javal.classify_ja_asr_match(canon, asr, allow_reading_resolver=False)
    print(f"  classify_ja_asr_match -> {r.classification} / reason={r.reason[:90]}")
    st = E.primary_stage(canon, asr, False)
    print(f"  Production Primary段(unified_judge込み) -> state={st['state']} reason={st['reason']} label={st['label']} warnings={st['warnings']}")
    return r


javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
print("== 1. N3-07 本体 ==")
trace("月のしわ、8,900本超", "月の巣は八千九百本長。", "N3-07")
print("== 2. 反事実(Candidate Eを通る『偶然の同音差』を外す) ==")
trace("月のしわ、8,900本超", "月の巣は八千九百本超。", "CF1: 超長の差なし")
trace("月のしわ、8,900本", "月の巣は八千九百本", "CF2: 数値バンドルのみ")
print("== 3. 反事実(数値のバンドルを外す) ==")
trace("月のしわ、本超", "月の巣は本長。", "CF3: 数値なし(非数値entry)")
print("== 4. 同型の類似例(母音違い/濁音/長音が数値と同居) ==")
for c, a in [("月のしわ、8,900本超", "月のしば八千九百本長"), ("月のしわ、8,900本超", "月のすわ八千九百本長"), ("月のしわ、8,900本超", "月のしわ八千九百本長"),
             ("コーヒー、8,900本超", "コヒ八千九百本長"), ("月のしわ、8,900本間", "月のしわ八千九百本目")]:
    trace(c, a, "SIM")
E.api0_guard_off()
