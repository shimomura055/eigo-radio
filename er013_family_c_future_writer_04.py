# ============================================================
# er013_family_c_future_writer_04.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04
# ============================================================
# 目的: er013_family_c_future_writer_03.py(無編集のまま保持)からの仕様
# 再設計。本ファイルのREPORT
# (EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_REPORT.md)
# で実施した構造診断の結論を反映する。
#
# --- 診断で判明した長文化の主因(¥0構造診断、実データ根拠) ---
# 1. 【最大の要因、Writer Prompt自体ではなくLayer2/3出力の事前構造化】
#    Trial-02で生成されたLayer2/3出力(layer23_v2_result.json、本Trialでも
#    無変更のまま再利用)は、本テーマについて[IMAGINED_FUTURE]を3件
#    (SCENE-LOCAL-ASSISTANCE/SCENE-HOUSEHOLD-LEARNING/
#    SCENE-DIFFERENT-HOUSEHOLDS)、具体的なscene_id・timeframe・
#    scene_summaryとして"完成品に近い場面材料"の形でWriterへ渡していた。
#    Writer Prompt(v2/v3)自体は「機械的に3時点へ当てはめる必要はない」と
#    明記していたにもかかわらず、実際のTrial-02/03の出力は両方とも、
#    提供された3件の場面材料をそのまま1対1で3つの[[IMAGINED]]ブロックへ
#    展開していた(Layer2/3側のプロンプトも「機械的に3時点」を求めては
#    いないが、実際に3件生成されており、それがそのままWriterへの
#    "既製の台本"として機能していた)。
# 2. 【第2の要因、v3 Writer Prompt自体の場面あたり要求の重なり】
#    Trial-03実記事(A2=550語/B1=744語)を段落単位で実測した結果、各時点は
#    ほぼ均等に「[[IMAGINED]]枠(場面+反応+選択、約150-250語)」+
#    「枠外の一般示唆パラグラフ(hedge付き、約30-75語)」+
#    「期待/希望と不安/懸念の対比文(多くの場面で重複、約25-60語)」の
#    3要素を繰り返しており、3時点×これらの要素 という積が総語数を
#    ほぼそのまま説明した(A2: 188+166+194語の3ブロック=548語、実測550語と
#    ほぼ一致。B1: 245+245+244+7語=741語、実測744語とほぼ一致)。
#    「期待/希望 vs 不安/懸念」の対比は、Prompt上は「記事のどこかで
#    1回」の指示だったが、各場面の反応が自然と両価的になり、結果として
#    ほぼ毎場面で対比が再生産されていた(重複要求)。
# 3. 【副次的要因、World Scaffold・Layer2/3の入力量】
#    World Scaffoldは25件の生statementをそのままWriterへ渡していたが、
#    実記事を確認したところ、直接言及されたのは各記事とも数テーマ
#    (充電・専用床面、洗濯・ベッド整え・片付け、階段・天井・深い汚れ、
#    実演からの学習、家庭差)のみで、25件を網羅的に使い切る圧力は
#    確認できなかった(主要因ではない)。ただしWriterへの入力トークン量・
#    ノイズ削減の観点では、実際に使われた場面(要因1で選択したscene)に
#    grounded_inで紐づく項目だけに絞ることが可能であり、無駄な情報量の
#    削減として実施する。
# 4. 【想像/事実の区別指示】v3で既に「場面直結の反応・選択まで
#    [[IMAGINED]]枠内に含める」よう変更した結果、枠内hedge密度は
#    Trial-03実測でA2=0%/B1=2.3%(閾値内)であり、この指示自体は既に
#    有効に機能していた(v2時点の問題であり、v3で解消済み。本v4でも
#    この設計は無変更で維持する)。
# 5. 【A2/B1標準分量とcontractの関係】CURRENT_SPEC.mdに、A-Family
#    Future記事に対する正式なhard word_count target値は存在しない
#    (writer_03のREPORT・本ファイルREPORTで確認済み)。Trial-03の
#    450-600(A2)/500-700(B1)はユーザー指示書の例示値をそのまま採用した
#    Trial限定の目安であり、実測はA2=550語(目安内、PASS)、
#    B1=744語(目安を44語=6.3%超過、編集Gate FAIL理由の一部)だった。
#    「550/744語」自体は、Trial-03当時の目安に対しては大幅超過ではなく
#    (A2は範囲内、B1は軽度超過)、この点はユーザー原文の前提
#    (「単なる軽微な超過ではない」)と実測が一致しない箇所として
#    REPORTで訂正報告する。ただし、要因1・2で確認した「時点数×場面
#    必須要素」の構造は、テーマが変わった場合にLayer2/3がより多くの
#    場面を生成すれば語数がさらに増える構造的リスクを持つため、
#    (a)場面数を明示的に絞る、(b)場面あたりの重複要素を減らす、という
#    respecは実測超過の大小によらず妥当と判断した。
#
# --- v4での変更点(要約) ---
# (a) 場面数の既定を2に削減する(Layer2/3出力を無変更のまま再利用しつつ、
#     コード側で決定的に2場面へ絞り込む。追加LLM呼び出し費用¥0。
#     3件以上ある場合は最初と最後を採用し、中間の場面を除く
#     [本テーマでは"導入期"と"分岐期"を残し、"学習期"を除く])。
# (b) 各場面の役割を"1つ目=変化の始まりと期待寄り"
#     "2つ目=定着後の葛藤・懸念寄り"に整理し、感情の重複配分を減らす。
# (c) 各場面で行動/台詞により示す感情は1つに限定する(v3は「最低1回」
#     だったため複数感情が重なりやすかった)。
# (d) 期待/希望 vs 不安/懸念の対比は、全場面終了後の単一の
#     "統合示唆パラグラフ"内で1回だけ書かせる(各場面の枠外パラグラフでの
#     重複を禁止)。
# (e) 場面ごとの枠外パラグラフを廃止し、全場面のあとに置く単一の統合
#     示唆パラグラフ1つに統一する(重複した移行文の削減)。
# (f) World Scaffold・FUTURE_ASSUMPTIONを、実際に採用した2場面の
#     grounded_inで参照される項目のみに絞る(コード側の決定的フィルタ、
#     追加LLM呼び出し費用¥0)。
# (g) 語数目安を場面数削減に合わせて調整する(A2: 380-520語、
#     B1: 450-620語。Trial限定の目安であり、正式Production仕様では
#     ない点はv3と同じ)。
# (h) 禁止表現・FACT例外・IMAGINED/META構文・枠内hedging免除の設計は
#     v3から無変更で維持する(既に有効に機能していたため)。
#
# 既存A-Family/B-Family・既存er013_*_01/_02/_03は一切import・編集しない
# (writer_02のマーカー定数のみ再利用、v3と同じ方針)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_02 as fcw2
import er013_family_c_future_writer_03 as fcw3  # generate_family_c_article_v3()を再利用(汎用関数、v4専用ロジックなし)

IMAGINED_OPEN_TEMPLATE = fcw2.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = fcw2.IMAGINED_CLOSE
FACT_OPEN_TEMPLATE = fcw2.FACT_OPEN_TEMPLATE
FACT_CLOSE = fcw2.FACT_CLOSE
META_OPEN = fcw2.META_OPEN
META_CLOSE = fcw2.META_CLOSE
MAX_FACT_EXCEPTIONS = fcw2.MAX_FACT_EXCEPTIONS

# generate_family_c_article_v3()は developer message・引数を汎用的に扱う
# ため、v4でもそのまま再利用する(重複実装を避ける)。
generate_family_c_article_v4 = fcw3.generate_family_c_article_v3

# Trial限定の目安(v3の450-600/500-700から、場面数削減[3→2]・場面あたり
# 重複要素削減に合わせて調整。CURRENT_SPECの正式値ではない)。
WORD_COUNT_TARGET_RANGE = {
    "a2": (380, 520),
    "b1": (450, 620),
}

# 場面あたりの語数目安(prompt内の目安表示用、hard gateではない。
# 実際の語数gateはWORD_COUNT_TARGET_RANGE[level]の記事全体レンジのみ)。
PER_SCENE_WORD_BUDGET_GUIDANCE = {
    "a2": 110,
    "b1": 140,
}
SYNTHESIS_PARAGRAPH_WORD_BUDGET_GUIDANCE = {
    "a2": 70,
    "b1": 90,
}


def select_scenes_for_v4(layer23_parsed: dict, max_scenes: int = 2) -> list:
    """Layer2/3の[IMAGINED_FUTURE]から、決定的(非LLM、¥0)に最大
    max_scenes件を選ぶ。3件以上ある場合は最初と最後を採用し、中間の
    場面を除く("導入期"と"分岐期"を残し、"定着期"を除く、という
    v4の場面役割整理[1つ目=変化の始まりと期待、2つ目=定着後の葛藤]に
    最も自然に対応するため)。2件以下の場合はそのまま全件を返す。"""
    scenes = list(layer23_parsed.get("imagined_futures") or [])
    if len(scenes) <= max_scenes:
        return scenes
    if max_scenes == 2:
        return [scenes[0], scenes[-1]]
    # max_scenes != 2 の一般ケース(将来の拡張用): 先頭からmax_scenes件
    return scenes[:max_scenes]


def build_trimmed_world_package_text(world_scaffold_parsed: dict, layer23_parsed: dict,
                                      selected_scenes: list) -> str:
    """v4用に入力量を削減したWorld Package textを組み立てる(決定的、
    ¥0、追加LLM呼び出しなし)。選択済み場面(selected_scenes)の
    grounded_inで参照されるFUTURE_ASSUMPTION・World Scaffold項目のみを
    残す。assemble_world_package_text()と同じ出力形式を維持する
    (Writer Promptの{world_package_text}差し込み先と互換)。"""
    assumptions = list(layer23_parsed.get("future_assumptions") or [])
    scaffold_items = list(world_scaffold_parsed.get("scaffold_items") or [])

    selected_scene_ids = {s.get("scene_id") for s in selected_scenes}
    referenced_ids = set()
    for s in selected_scenes:
        referenced_ids.update(s.get("grounded_in") or [])

    kept_assumptions = [a for a in assumptions if a.get("assumption_id") in referenced_ids]
    kept_assumption_ids = {a.get("assumption_id") for a in kept_assumptions}

    scaffold_id_pool = set()
    for ref in referenced_ids:
        if ref not in kept_assumption_ids:
            scaffold_id_pool.add(ref)  # scaffold_idを直接参照しているケース
    for a in kept_assumptions:
        scaffold_id_pool.update(a.get("based_on") or [])

    kept_scaffold_items = [it for it in scaffold_items if it.get("scaffold_id") in scaffold_id_pool]

    lines = ["[WORLD_SCAFFOLD]"]
    for it in kept_scaffold_items:
        lines.append(f"scaffold_id: {it.get('scaffold_id')}")
        lines.append(f"category: {it.get('category')}")
        lines.append(f"statement: {it.get('statement')}")
        lines.append("")
    lines.append("[FUTURE_ASSUMPTION]")
    for a in kept_assumptions:
        lines.append(f"assumption_id: {a.get('assumption_id')}")
        lines.append(f"assumption: {a.get('assumption')}")
        lines.append(f"based_on: {', '.join(a.get('based_on') or [])}")
        lines.append("")
    lines.append("[IMAGINED_FUTURE]")
    for s in selected_scenes:
        lines.append(f"scene_id: {s.get('scene_id')}")
        lines.append(f"timeframe: {s.get('timeframe')}")
        lines.append(f"scene_summary: {s.get('scene_summary')}")
        lines.append(f"grounded_in: {', '.join(s.get('grounded_in') or [])}")
        lines.append("")
    lines.append("[STRUCTURE_RATIONALE_REFERENCE_ONLY]")
    lines.append(
        f"v4診断respecにより、元の{len(layer23_parsed.get('imagined_futures') or [])}場面から"
        f"{len(selected_scenes)}場面(scene_id: {', '.join(sorted(selected_scene_ids))})へ"
        "決定的に絞り込んだ(中間の場面を除外)。1つ目の場面=変化の始まりと期待寄り、"
        "2つ目の場面=定着後の葛藤・懸念寄りとして描くこと。"
    )
    return "\n".join(lines).rstrip("\n") + "\n", {
        "kept_scaffold_ids": sorted(it.get("scaffold_id") for it in kept_scaffold_items),
        "kept_assumption_ids": sorted(kept_assumption_ids),
        "selected_scene_ids": sorted(selected_scene_ids),
        "dropped_scaffold_count": len(scaffold_items) - len(kept_scaffold_items),
        "dropped_assumption_count": len(assumptions) - len(kept_assumptions),
    }


LEVEL_GUIDANCE_V4 = {
    "a2": (
        "A2レベル: 短く明確な文を使ってください。[[IMAGINED]]の枠外・"
        "移行文での仮定・未来のhedgingは\"might\"/\"could\"/明確な条件節"
        "(\"If ... , ...\")のような単純な形を使ってください。1文はできる"
        "だけ1つの内容にとどめてください。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['a2'][0]}〜{WORD_COUNT_TARGET_RANGE['a2'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
        f"各[[IMAGINED]]場面は、目安として{PER_SCENE_WORD_BUDGET_GUIDANCE['a2']}語程度"
        "までにまとめてください(場面+反応+選択のみに絞り、複数の感情を"
        "詰め込まないでください)。"
    ),
    "b1": (
        "B1レベル: A2よりやや複雑な文・仮定法・条件構文を使ってよいですが、"
        "難解な専門語は避けてください。[[IMAGINED]]の枠外・移行文での仮定・"
        "未来のhedgingは\"might\"/\"could\"に加え、やや複雑な仮定法"
        "(\"If this trend continued, cities could ...\"のような)も使って"
        "よいです。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['b1'][0]}〜{WORD_COUNT_TARGET_RANGE['b1'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
        f"各[[IMAGINED]]場面は、目安として{PER_SCENE_WORD_BUDGET_GUIDANCE['b1']}語程度"
        "までにまとめてください(場面+反応+選択のみに絞り、複数の感情を"
        "詰め込まないでください)。"
    ),
}

FAMILY_C_FUTURE_WRITER_V4_DEVELOPER_MESSAGE = fcw2.FAMILY_C_FUTURE_WRITER_V2_DEVELOPER_MESSAGE

# ------------------------------------------------------------
# Writer Prompt本体(v3から継承。変更点: 場面数をLayer2/3側で決定的に
# 絞り込んだ前提で「材料にある場面の数だけを使う」よう明示し、場面の
# 役割分担・感情1つ限定・統合示唆パラグラフ1つのみ、を追加した)。
# 禁止語リスト・FACT例外・META・[[IMAGINED]]枠内の書き方の原則(反応まで
# 枠内に含める・hedging不要)はv3のまま無変更で維持する。
# ------------------------------------------------------------
FAMILY_C_FUTURE_WRITER_V4_PROMPT_TEMPLATE = """テーマ: {topic}

【使ってよい材料(この範囲外の具体的な現在の事実・数字・固有名詞・
製品名を新たに作り出さないでください)】
{world_package_text}

【記事の主役(最重要)】
この記事の主役は、未来の生活場面・そこで何が起きるか・それが人の生活や
感情や選択にもたらすもの・楽しみや期待や不安や葛藤です。Research・現在の
事実・統計・製品情報は、その未来像を無根拠にしないための内部の足場に
すぎません。読者に説明する必要がなければ、本文には出さないでください。

【固く禁止する表現(1つでも本文に出た場合、記事は不合格になります)】
- 統計値・比率・パーセンテージ・年次データ・具体的な販売台数や調査対象
  人数などの数字(想像した未来の時間軸を表す表現[例: "around 2035"、
  "a decade from now"]は数字を含んでも構いません。禁止されるのは調査・
  統計・過去/現在の実績データとしての数字です)。
- "study/studies/research/survey/report/researcher/scientist"のような、
  研究・調査であることを示す語、および"found/shows/showed/suggests/
  indicates/according to"のような研究結果を読者へ説明する言い回し。
- 製品名・型番・企業名・ブランド名の列挙。
- Researchの結果を読者へ解説する構造(「〜という調査結果があります」
  「〜という研究が示しています」のように、記事が現在の根拠を説明する
  ための記事になること)。
- 記事を短くするために、場面や感情の描写を削って上記の研究解説的な
  要約表現へ戻すこと(分量調整は、重複した言い回し・説明的な接続文を
  削ることで行ってください)。

【現在の事実に触れてよい例外(最大{max_fact_exceptions}件のみ)】
未来像の説得力にどうしても必要で、読者に説明が必要な現在の事実がある
場合に限り、記事全体で最大{max_fact_exceptions}件まで、Worldscaffoldの
statementを平易に言い換えた一文として本文に含めてよいです。その場合は
必ず次の形式で挟んでください(数字・出典・固有名詞は入れないでください、
Worldscaffoldの言い換えのみ):

{fact_open_example}
(ここに、Worldscaffoldのいずれか1項目を平易に言い換えた1文。数字・
出典・固有名詞は含めないでください。)
{fact_close}

このマーカーを使わない現在事実への言及(地の文でさりげなく現在の様子に
触れる程度の1文)は、統計・研究・製品情報でない限り問題ありません。

【場面数・構成(重要な変更点)】
【使ってよい材料】の[IMAGINED_FUTURE]に列挙されている場面の数だけを
使ってください(材料にない場面を新たに追加しない、材料にある場面を
省略しない)。1つ目の場面は、変化が始まったばかりの時期として、
主に期待・意欲を中心に描いてください。2つ目の場面(材料に2つ目が
ある場合)は、その変化が定着したあとの時期として、主に葛藤・懸念を
中心に描いてください(両方の感情を両方の場面に均等に詰め込まないで
ください。各場面で行動または短い台詞により示す具体的な感情は1つに
絞ってください)。

【最低限の構成要素(型は固定しません。テーマに最も合う展開を選んで
ください)】
1. 入口: 統計から始めず、いきなり生活場面から始めてください。時間軸
   (いつの未来を描くか)は、場面の中で自然に伝わるようにしてください。
2. 場面で起きること: 具体的な未来の場面で、何が起きるかを描いてください。
3. 人の生活・感情・選択への影響: その出来事が、登場する人(または聞き手
   自身)の生活・感情・選択にどう影響するかを、行動または短い台詞
   (セリフ)で示してください(単なる形容詞の羅列[例: "この状況は
   不安だ"]ではなく、何をした/何を言ったかで示す)。
4. 全ての場面を描き終えたあと、記事の終わり近くに、複数の場面にまたがる
   一般的な示唆をまとめる段落を「1つだけ」書いてください。期待・希望と、
   不安・懸念という2つの感情の対立の対比は、この統合示唆段落の中で
   1回だけ行ってください(個々の場面の中や、場面ごとの移行文では、この
   対比を繰り返さないでください)。
5. 持ち帰りの一行: 記事の終わりに、聞き手が持ち帰る印象(わくわく/
   不安の余韻)を一行で残してください。事実の要約にしないでください。

構成は##等の短い見出しで区切ってください(後工程での区切り把握のため)。
見出しの文言・数は自由です。

【想像した未来の場面の書き方】
具体的な未来の場面・情景を描くときは、必ず次の形式で挟んでください:

{imagined_open_example}
(ここに、その場面の英語の本文。読み手が「これは想像された未来だ」と
自然に理解できる入口の一文から始めてください。例: "Picture a Tuesday
evening in 2035, when ..."のような、時間軸を含む自然な導入文。)
{imagined_close}

この枠の中では、入口の一文で既に「これは想像だ」と示せているため、
"might"/"could"/"may"/"perhaps"/"possibly"のようなhedging語を使う
必要はありません。現在形・断定調で、情景・人物の行動・選択・感情を
はっきりと描いてください(例: "The robot pauses. She watches it,
unsure whether to help."のように)。

**この枠は、場面の情景描写だけで終わらせず、その場面から直接生まれる
人物の反応・気持ち・その場での選択までを、同じ枠の中に含めてください**
(例: 場面の中でロボットが失敗し、その場でその人がどう感じ、次に
何をするかまでを枠内で描く)。枠を閉じるのは、その1つの具体的な場面
から離れ、複数の場面にまたがる一般的な示唆・まとめ・別の話題へ移る
ときにしてください。ただし、この場面の中で「現在は既に〜だ」という
現在の事実の主張を新たに作らないでください。

枠を離れて、全場面終了後の統合示唆段落を書くとき(例: 「もしこうした
変化が広がれば」)は、従来どおり"might"/"could"のようなhedgingや
"If ... , ..."の条件節を使い、未来を確定事実であるかのように断定
しないでください。個々の場面の直後には、この統合示唆段落を置かないで
ください(全場面を描き終えたあとに1回だけ置いてください)。

上記のマーカー(角括弧2つ)は、実際に本文中にそのまま書いてください
(このマーカーは最終読者向け出力では自動的に取り除かれます)。

【内部メモ(読者には見せません)】
本文の最後に、以下の形式で内部メモを1つだけ書いてください(読者向け
出力からは自動的に完全に取り除かれます)。なぜこの場面数・間隔・
場面の役割分担を選んだかを1〜2文で説明してください:

{meta_open}
(この記事の場面数・間隔・役割分担を選んだ理由。1〜2文。)
{meta_close}

{level_guidance}

英文のみを出力してください(日本語の解説・見出し訳は不要です)。"""


def build_family_c_writer_v4_prompt(topic: str, level: str, world_package_text: str,
                                     gate_feedback: str = "") -> str:
    level_key = level.lower()
    if level_key not in LEVEL_GUIDANCE_V4:
        raise ValueError(f"未知のlevel: {level!r}(a2/b1のいずれかを指定してください)")
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    fact_open_example = FACT_OPEN_TEMPLATE.format(ref_id="WS-003")
    prompt = FAMILY_C_FUTURE_WRITER_V4_PROMPT_TEMPLATE.format(
        topic=topic, world_package_text=world_package_text,
        max_fact_exceptions=MAX_FACT_EXCEPTIONS,
        fact_open_example=fact_open_example, fact_close=FACT_CLOSE,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        meta_open=META_OPEN, meta_close=META_CLOSE,
        level_guidance=LEVEL_GUIDANCE_V4[level_key])
    if gate_feedback:
        prompt += (
            "\n\n【前回の下書きが編集Gateで不合格になった理由(必ず今回は"
            "避けてください)】\n" + gate_feedback
        )
    return prompt
