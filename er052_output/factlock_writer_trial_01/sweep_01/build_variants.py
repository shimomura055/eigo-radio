# -*- coding: utf-8 -*-
"""sweep_01/variants.json を生成する(委任_04a、FACTLOCK-WRITER-REDESIGN-TRIAL-01)。API呼び出しなし。
R0_PROMPTの置換元文字列は er019 writer の R0_PROMPT 行から機械的に取得する(全角記号の不一致を防ぐ)。
実行: .venv\\Scripts\\python.exe -X utf8 er052_output/factlock_writer_trial_01/sweep_01/build_variants.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
import er019_family_x_ja_writer_o_r1_r2_01 as jaw  # noqa: E402  (読み取りのみ)

LINES = jaw.R0_PROMPT.split("\n")


def line_starting(prefix):
    hit = [l for l in LINES if l.startswith(prefix)]
    assert len(hit) == 1, prefix
    return hit[0]


L_GOAL = line_starting("以下のニュースを、友人に")
L_VIEW = line_starting("ニュースの中から、最も意外な事実ではなく")
L_TONE = line_starting("語り口は自然で軽快にします")
L_FAR = line_starting("遠い地域だけの特殊な話に見える場合は")
L_LEN = line_starting("長さ")

# ---- 共通部品(全文) ----
TAG_INTRO = ("\n\nニュース欄の各事実の行頭には【事実1】【事実2】のような番号が付いています。"
             "事実を述べる文の末尾に、根拠にした事実の番号を【事実1】のように付けてください。")
# 共通修正T(DESIGN_02 §0-2、委任_04b): タグ番号の取り違え防止。S7以外の全タグ付き変種のR0へ入れる
COMMON_T = ("番号は【事実N】のNだけを使い、ニュース欄の事実の後ろに書かれているF-011やHF-002のような"
            "別の番号は、タグに使わないでください。")
TAG_INTRO_T = TAG_INTRO + COMMON_T
NO_OUTSIDE = "ニュース欄にないことは書かないでください。"
NUMERIC_SHORT = ("数字は、ニュース欄で【中核数値】と印の付いたものだけを、ニュース欄の表記のまま使えます。"
                 "【周辺数値】の数字は書かず、数字を使わずに述べてください。印そのものは書かないでください。")
KEEP_TWO = ("\n\n文末に【事実N】が付いた文は、その事実を変えず、【事実N】を付けたまま残してください。"
            "新しい事実を述べる文は足さないでください。")
LENGTH_LINE = "長さは800～1000字にしてください。"
MEANS_LIST = ("\n面白くする手段の例として、生活の場面に置き換えたたとえ話、対比、読者への問いかけ、"
              "意外性のある導入、テンポのよい短い文があります。ここから選んでも、自分で考えてもかまいません。")
R3_INSTRUCTION_BASE = "この記事を、事実関係は変えずに、さらにさらにもっとエンターテインメント性の高い記事に修正してください。"

NUMERIC_S11 = ("数字は、ニュース欄で【中核数値】と印の付いたものも含め、原則として書かず、数字を使わずに述べてください。"
               "記事の理解に本当に必要な場合だけ、ニュース欄の表記のままで最大1つ使えます。印そのものは書かないでください。")

R0_S3 = TAG_INTRO_T + NO_OUTSIDE + NUMERIC_SHORT
R0_S11 = TAG_INTRO_T + NO_OUTSIDE + NUMERIC_S11

# S12: DESIGN_02 案A(blocks_v2.json の A.R0 / A.R1_R2 を逐語で読む)
_B2 = json.load(open(os.path.join(os.path.dirname(__file__), "..", "v2_design", "blocks_v2.json"), encoding="utf-8"))
S12_R0 = _B2["A"]["R0"]
S12_R1R2 = _B2["A"]["R1_R2"]


def v(id_, axis, hyp, fact, fun, **kw):
    d = {"id": id_, "axis": axis, "hypothesis": hyp, "fact_effect_expected": fact, "fun_effect_expected": fun,
         "tag_mode": "full", "brief_marks": "keep", "chain": "previous_response_id",
         "r0": {"mode": "append", "block": "", "prompt_replace": []},
         "r1": {"mode": "append", "text": ""}, "r2": {"mode": "append", "text": ""}, "r3": None}
    d.update(kw)
    return d


VARIANTS = [
    v("S1", "タグ付与のみ(規則文なし)",
      "出典タグを付けさせるだけで、事実の誤りや文体はどう変わるか(タグ自体の副作用)",
      "タグ付与だけで事実の根拠意識が働き多少減る可能性。規則が無いので限定的と見込む",
      "R1/R2は現行のままなのでS0に近い見込み。タグが文を区切り多少窮屈になる可能性",
      brief_marks="strip",
      r0={"mode": "append", "block": TAG_INTRO_T, "prompt_replace": []}),
    v("S2", "S1+「ニュース欄にないことは書かない」1文",
      "最小の禁止1文(R0のみ)で、台帳外の断定がどれだけ減るか",
      "台帳外の断定(unsupported/new_specific_claim)がS1より減る見込み。R1/R2は無制約のため増幅は残る",
      "R0の1文だけなのでS1と同程度の見込み",
      brief_marks="strip",
      r0={"mode": "append", "block": TAG_INTRO_T + NO_OUTSIDE, "prompt_replace": []}),
    v("S3", "S2+数値規則(短文版)、R1/R2は無制約",
      "R0だけを固め、Reviseを自由にしたとき事実の崩れ(増幅量)がどれだけ出るか",
      "R0は固まるがR1/R2で新事実や数字が増える可能性(R0→R2の悪化量がこの変種の読みどころ)",
      "R1/R2が現行のままなのでS0と同程度の面白さを維持する見込み",
      r0={"mode": "replace_numeric", "block": R0_S3, "prompt_replace": []}),
    v("S4", "S3+R1/R2に2文(事実を変えない・新事実を足さない)",
      "R1/R2へ最小の2文を足すだけで、増幅が止まり面白さが落ちないか",
      "S3より増幅が減る見込み(2文のみのため抜け道は残る)",
      "2文のみなのでv1(7則)より面白さが残る見込み。タグを残す指示で文構造が少し固まる可能性",
      r0={"mode": "replace_numeric", "block": R0_S3, "prompt_replace": []},
      r1={"mode": "append", "text": KEEP_TWO}, r2={"mode": "append", "text": KEEP_TWO}),
    v("S6", "骨格→肉付け(R0は事実の骨格のみ、R1/R2でEntertainment)",
      "事実と面白さを段で分担すると、事実を保ったまま面白さが乗るか",
      "R0が短く事実だけなので誤りが少ない見込み。R1/R2での肉付けで新事実が入る可能性",
      "R0は面白くない前提で、R1/R2の2回で800~1000字へ膨らませる。膨らませ方が単調になる可能性",
      r0={"mode": "replace_numeric", "block": R0_S3,
          "prompt_replace": [
              [L_GOAL, "以下のニュースの事実を、短い文で正確にまとめてください。この段階では面白さは求めず、読み物の土台になる事実の骨格だけを書きます。"],
              [L_VIEW, "ニュースの中から、話の中心になる事実を選び、その事実に必要なものだけを使ってください。"],
              [L_TONE, "難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。"],
              [L_FAR, ""],
              [L_LEN, "長さ：300～400字"]]},
      r1={"mode": "append", "text": KEEP_TWO + LENGTH_LINE}, r2={"mode": "append", "text": KEEP_TWO + LENGTH_LINE}),
    v("S7", "目標形(規則を書かず目標文のみ、R1/R2の指示も目標文に置換)",
      "禁止や手順でなく目標で書くと、事実と面白さの両方が規則形より良いか",
      "規則が無いので台帳外の断定は残りやすい見込み。目標が事実重視なので多少抑えられる可能性",
      "指定が少なく1パターン化しにくい見込み。現行の「エンターテインメント性」の語が無くなる影響は不明",
      brief_marks="strip",
      r0={"mode": "append",
          "block": ("\n\nこの記事の目標は、読者がニュース欄の事実を正確に受け取れることです。"
                    "ニュース欄の各事実の行頭には【事実1】のような番号が付いています。"
                    "事実を述べる文の末尾に、根拠にした事実の番号を【事実1】のように付けてください。"),
          "prompt_replace": []},
      r1={"mode": "replace",
          "text": "この記事を、友人に「これ、ちょっと面白くない？」と話すような読み物に直してください。ニュース欄の事実はそのままにして、文末の【事実N】は残してください。"},
      r2={"mode": "replace",
          "text": "この記事を、さらに「これ、ちょっと面白くない？」と友人に話したくなる読み物にしてください。ニュース欄の事実はそのままにして、文末の【事実N】は残してください。"}),
    v("S8", "連鎖切り(R1/R2はタグ除去済み本文を新規contextで渡す)",
      "タグ・規則・台帳が視界に無い状態でReviseさせると面白さが伸びるか、事実はどれだけ崩れるか",
      "Reviseが台帳もタグも見ないので事実の崩れが増える可能性が最も高い(事後タグ再付与で測る)",
      "窮屈さが最も少なく、面白さが最も伸びる見込み",
      tag_mode="retag", chain="cut",
      r0={"mode": "replace_numeric", "block": R0_S3, "prompt_replace": []}),
    v("S9", "S4+R3(Entertainment Revisionを3回)",
      "Revision回数を増やすと面白さは伸びるか、事実は崩れるか",
      "回数が増えるほど崩れる機会が増える。R3後にもJA Fact Check(測定+採否)を入れる",
      "S4より面白さが伸びる可能性。伸びが小さければ回数は効かない",
      r0={"mode": "replace_numeric", "block": R0_S3, "prompt_replace": []},
      r1={"mode": "append", "text": KEEP_TWO}, r2={"mode": "append", "text": KEEP_TWO},
      r3={"instruction": R3_INSTRUCTION_BASE + KEEP_TWO}),
    v("S10", "S4+面白さの手段リスト(選択肢の列挙)",
      "手段を例示すると、面白さが上がるか、3記事の構成・比喩が似通う(1パターン化する)か",
      "S4と同等の見込み(事実規則は同じ)",
      "手段リストに寄って3記事が似る可能性。ユーザー指摘「指定を多くすると1パターン化」の検証",
      r0={"mode": "replace_numeric", "block": R0_S3, "prompt_replace": []},
      r1={"mode": "append", "text": KEEP_TWO + MEANS_LIST}, r2={"mode": "append", "text": KEEP_TWO + MEANS_LIST}),
    v("S11", "S4と同一で数値規則だけ差替え(中核数値も原則書かない)",
      "数字を原則書かせないと、数字の増加(診断:2.6倍)と数値不一致・文体の硬さがどう変わるか(S4との1要素差)",
      "数値不一致が減る見込み。数字が無い分、記事の具体性が下がる可能性",
      "数字が少なく話し言葉寄りになる可能性。具体性が落ちて面白さが下がる可能性もある",
      r0={"mode": "replace_numeric", "block": R0_S11, "prompt_replace": []},
      r1={"mode": "append", "text": KEEP_TWO}, r2={"mode": "append", "text": KEEP_TWO}),
    v("S12", "案A(v1規則を維持+語り口規則。ユーザー仮説「誘導は効かない」の検証端点)",
      "規則を維持したまま語り口の規則(比喩1系統・暮らし・否定1回・話し言葉・結び)を足すと、面白さは戻るか、事実は保たれるか",
      "v1規則は逐語維持のため事実面はv1並みの見込み。語り口規則が台帳語の言い換えを許すため言い換え由来の逸脱が出る可能性",
      "ユーザー仮説どおりなら誘導は効かない(S5並み)。効けば比喩の重なり・硬さが改善する",
      r0={"mode": "replace_all", "block": S12_R0, "prompt_replace": []},
      r1={"mode": "append", "text": S12_R1R2}, r2={"mode": "append", "text": S12_R1R2}),
]

REFS = [
    {"id": "S0", "ref": "all6", "desc": "6-luna x 現行prompt(既存、再生成しない)",
     "path_template": "er052_output/all6_writer_redesign_necessity_01/runs/{slug}/control/b{b}__all6__r{rep}",
     "rep_default": 1, "rep_override": {"space_weapons/b3": 2},
     "note": "space_weapons/b3 のall6 r1は phase2 でJA_RECHECK_REQUIREDによりSTOP(EN記事なし)のためr2を参照"},
    {"id": "S5", "ref": "factlock_v1", "desc": "6-luna x Fact Lock v1(既存、再生成しない)",
     "path_template": "er052_output/factlock_writer_trial_01/runs/{slug}/control/b{b}__factlock__r{rep}", "rep_default": 1, "rep_override": {}},
]

OUT = os.path.join(os.path.dirname(__file__), "variants.json")
if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"schema": 1, "briefs": [["meta", 2], ["hormuz", 4], ["space_weapons", 3]],
                   "references": REFS, "variants": VARIANTS}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, len(VARIANTS), "variants")
