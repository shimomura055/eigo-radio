# -*- coding: utf-8 -*-
# ============================================================
# er110_family_y_persona_trial03_01.py
# FAMILY-Y-VOICES-DESIGN-01 委任_09B(Trial_03): 世界設定整合 + 案(d)(初回稿基準の手修正稿 it3)の入口(DEV/Trial専用)
# ============================================================
# 位置づけ: DEV/Trial経路のみ。Production到達経路に入れない(どのProduction runner/.env/起動scriptからも参照されない。flag・環境変数切替なし)。
#   er110_family_y_persona_text_trial_01(_run)/_audio_trial_01 は無変更。本fileは「モジュール属性の process内差替え」だけで
#   (1)共通前提(COMMON_PREMISE_JA)・Persona Sheet(SHEETS)・Comment 1の背景fact・日本語タイトルを世界設定整合版へ差し替え、
#   (2)Writer(high effort)を呼ばず、手修正した日本語本文(it3)をそのまま既存のGate→英訳→scaffold→RFへ流す。
# 世界設定の根拠: docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/WORLD_SETTING_01.md
# ============================================================
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import er110_family_y_persona_text_trial_01 as p
import er110_family_y_persona_text_trial_01_run as run
import er053_family_x_factlock_ja_writer_01 as w1

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
IT = "it3"
TEXT_BUDGET_JPY = 30.0     # it3のテキスト段(Gate・英訳・scaffold・RF)のrun dir単位の保険。超過見込みで停止

# 共通前提(日本の高校。現状=授業中のみ使用禁止、案=休み時間・昼休みを含む校内使用の禁止。持込は認めたまま)
COMMON_PREMISE_JA_03 = ("日本の高校が、スマホを授業中だけでなく休み時間や昼休みも含めて、学校にいる間はずっと使わないことにするかどうか"
                        "(今は授業中だけ使えない。持ち込みそのものは認めたまま、校内で使わせない範囲を広げる案)。")
JA_TITLE_03 = "休み時間もスマホを使わない学校、それぞれの声"
COMMENT1_FACT_IDS_03 = ("JP-03", "NL-01")      # 日本の通知(高校=校内使用の制限) + 授業中のみの使用制限の例(オランダ)。数字・英字略語を持ち込まない

# 手修正した日本語本文(初回稿 it1 を基準。変更は REASON 参照)
VOICES_03 = {
    "voice_1": ("俺は、娘の高校で、休み時間や昼休みもスマホを使わせない決まりに賛成だ。授業中だけじゃ足りない。"
                "現場から遅く帰って、毎晩スマホで揉めるのはしんどい。学校でもそう決まってると言えたら、俺だけが悪者にならずに済む。"
                "居間の充電カゴに入れる約束を、娘は守らなかった。取り上げた翌朝の食卓で、娘と口をききづらかった。"
                "「私だけ返事が遅れると外される」とも言われた。俺は言い返せなかった。決めたことは守ってほしいんだ。"
                "うちの親父みたいに怒鳴るのも嫌だ。ただ、昼間の学校で使えなくしても、夜の家は変わらない。"
                "学校に頼んで俺が楽になりたいだけな気もする。家じゃ段取りも組めない現場監督だ、俺は。"),
    "voice_2": ("朝いちばん、保健室へ来る子の顔を、私は毎朝見ている。眠い、って。頭が痛い、って。"
                "この前も、ベッドで休む子の枕元でスマホの画面が光っていた。明け方まで起きていたと聞くと、どう声をかけようかと迷う。"
                "昼間にスマホを取り上げられた翌日から、顔を見せなくなったあの子も気になる。来ないのと、つらくないのは同じなんだろうか。"
                "先生に「スマホを禁止にしたら、保健室に来る子は減る？」と聞かれて、私は答えに詰まった。"
                "学校が休み時間まで使えなくして、それで対策した気になってしまわないかな。それが、どうにも怖い。"
                "私は保健室では取り上げず、夜に何があったかを話せる場所を残したい。使えなくしたあと、あの子の話は誰が聞くんだろう。"),
    "voice_3": ("僕は、休み時間までスマホを使えなくする決まりには反対だ。昼は倉庫で働いて、夜は定時制に通っている。"
                "だから、学校にいる間ずっと連絡を切る約束はできない。授業の合間の休み時間に、シフト変更の連絡が来る。"
                "返事が遅いと、仕事はほかの人に回される。前に授業中、職場から着信が続いても出られず、あとで連絡がつかないのは困ると言われた。"
                "シフトも減らされかけた。僕はここで卒業したい。家に入れるお金も要る。"
                "授業が分かるようになったのに、仕事か学校かなんて、選びたくない。"
                "僕は授業中、鞄の奥にしまって触らないと約束する。でも、休み時間まで使えなくすると決める前に、僕の働き方も聞いてほしい。"),
}
TENSION_03 = ("朝の食卓でも、保健室の枕元でも、休み時間の仕事の連絡でも、相手と話せるままでいたい。"
              "使えない時間を広げれば、夜のカゴをめぐる押し問答は減るかもしれない。"
              "けれど、取り上げられた子は、枕元で話してくれなくなるかもしれない。"
              "授業中は守れても、休み時間のシフトの連絡まで止まれば、職場の信用が揺らぐ。"
              "学校に助けを求める父親も、取り上げたあとの沈黙は、もう繰り返したくない。"
              "使える時間の長さは食い違っても、話せる相手を残したいところは重なる。"
              "あなたがすぐに返したい連絡は、いつ、誰から届く？")


def build_sheets_03() -> dict:
    s = copy.deepcopy(p.SHEETS)
    s["voice_1"]["relation"] = "娘は全日制の高校(今は授業中だけスマホ使用禁止)。保護者会は仕事で半分しか行けず、学校の様子は娘の話とお知らせで知る。"
    s["voice_1"]["feel_reason"] = ("学校が授業中だけでなく休み時間や昼休みもスマホを使わせないと決めてくれるなら、正直助かる。家で毎晩、自分だけが悪者になる役を引き受けるのに疲れている。"
                                   "でも、それを学校に頼って楽になりたいだけではないか、という引っかかりもある。")
    s["voice_1"]["claim"] = "学校が休み時間や昼休みも使わせないと決めてくれれば、「学校もそう言ってる」と言える。俺ひとりが悪者にならずに済む。"
    s["voice_2"]["relation"] = ("保健室は「取り調べない、没収しない」を自分の流儀にしている。スマホの回収や取り締まりの担当ではないが、担任や生徒指導の先生とは対等に話せ、"
                                "保健室での扱いを先生たちに聞かれる立場。")
    s["voice_2"]["feel_reason"] = ("保健室まで没収の場にしたくない。校内で使わせない範囲を広げて「対策した」と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなるのが怖い。"
                                   "本当に言いたいのは、取り上げるかどうかより、そのあと誰が子どもの話を聞くのか、ということ。")
    s["voice_2"]["claim"] = "保健室まで没収の場にしたくない。休み時間まで禁止して「対策した」と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなる、と私は思う。"
    s["voice_3"]["feel_reason"] = ("授業中に触らないことは約束できる。でも、休み時間まで使えなくするのは守れない約束になる。仕事の連絡が切れたら、信用をなくして、"
                                   "仕事か学校かの二択になってしまう。全員一律に決める前に、自分のような生徒の事情を聞いてほしい。")
    s["voice_3"]["claim"] = "授業中は鞄の奥に入れると約束する。でも、休み時間まで使えなくするのは、仕事の連絡が切れるから守れない。"
    s["voice_3"]["seeds"][0] = "授業の合間の休み時間に来るシフト変更の連絡と、返事が遅いと他の人に回される仕事"
    s["voice_3"]["tension_object"] = "休み時間に届くシフトの連絡"
    return s


def apply_overrides() -> None:
    """process内のモジュール属性差替え(ファイルは変更しない)。"""
    p.COMMON_PREMISE_JA = COMMON_PREMISE_JA_03
    p.SHEETS = build_sheets_03()
    p.COMMENT1_FACT_IDS = COMMENT1_FACT_IDS_03
    run.JA_TITLE = JA_TITLE_03
    run.BUDGET = TEXT_BUDGET_JPY
    run.total_cost_jpy = _it3_cost


def _it3_cost(rd: str = None) -> float:
    import glob
    import er053_cost_aggregate_01 as ca
    base = f"{run.ROOT}/{IT}"
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{base}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def seed(overwrite: bool = False) -> None:
    rd = f"{run.ROOT}/{IT}"
    for s in p.VOICE_SLOTS:
        fp = f"{rd}/voices/{s}.txt"
        if os.path.exists(fp) and not overwrite:
            continue
        w1.wt(fp, VOICES_03[s] + "\n")
        w1.wj(f"{rd}/voices/{s}_meta.json", {"source": "HAND_EDIT_FROM_it1", "base": "it1/voices/" + s + ".txt", "llm_calls": 0})
    tp = f"{rd}/tension/tension.txt"
    if not os.path.exists(tp) or overwrite:
        w1.wt(tp, TENSION_03 + "\n")
        w1.wj(f"{rd}/tension/tension_meta.json", {"source": "HAND_EDIT_FROM_it2_tension", "llm_calls": 0})
    hp = f"{rd}/headings/headings.json"
    if not os.path.exists(hp) or overwrite:
        src = json.load(open(f"{run.ROOT}/it2/headings/headings.json", encoding="utf-8"))
        w1.wj(hp, {"headings": src["headings"], "history": [], "source": "REUSED_FROM_it2(本文の具体物と一致を確認済み。LLM 0 call)"})
    print("[Y-TRIAL03] seed done")


def main() -> None:
    ap = argparse.ArgumentParser(description="Family Y Trial_03 (it3) 入口(DEV/Trial専用)")
    ap.add_argument("cmd", choices=("seed", "validate", "text", "english", "scaffold", "rf", "eval"))
    ap.add_argument("--judge-model", default=p.MODEL_CHEAP)
    ap.add_argument("--judge-effort", default="high")
    ap.add_argument("--s3", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    a.iter = IT
    apply_overrides()
    if a.cmd == "seed":
        seed(a.overwrite)
    elif a.cmd == "validate":
        errs = p.validate_sheets()
        print(json.dumps({"sheet_errors": errs}, ensure_ascii=False))
        sys.exit(1 if errs else 0)
    elif a.cmd == "eval":
        import er110_family_y_persona_eval_01 as ev
        ev.cmd_eval(a)
    else:
        {"text": run.cmd_text, "english": run.cmd_english, "scaffold": run.cmd_scaffold, "rf": run.cmd_rf}[a.cmd](a)


if __name__ == "__main__":
    main()
