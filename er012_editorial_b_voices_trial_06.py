# ============================================================
# er012_editorial_b_voices_trial_06.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-06-PERSPECTIVE-SELECTION-EDITOR-DIAG-01
# ============================================================
# Lane: Lane B / Voices-Perspective。Lane A(OPEN-112/OPEN-117/ER-011系、
# docs/pm/*、er011_*、er006_*、er003_*Production本体等)とは完全に独立。
# 本ファイルはer012_editorial_b_voices_trial_05.pyを土台にコピーし、
# Trial-05本体は一切変更していない。本タスクではGit操作(add/commit/push/
# reset等)を一切行わない(Fableが後で統合commitする)。
#
# 背景(ユーザー判断、EDITORIAL-B-FAMILY-VOICES-TRIAL-06-PERSPECTIVE-
# SELECTION-EDITOR-DIAG-01タスク文書より):
# 1. Trial-05のPerspective組み合わせ(週の大半をオフィスで働く社員 vs
#    ワークプレイス戦略責任者)は不採用。今回のテーマでは「固定席を好む
#    社員 vs 自由席(フリーアドレス)を好む社員」という、より一般的・王道の
#    対立軸でよい。重要なのは「好みが違う」で終わらせず、それぞれ「なぜ
#    好むのか/何を守りたいか/何を不便・不安・価値と感じるか/どんな経験・
#    条件からその主張になるか」まで掘り、主張とその背景を戦わせること。
#    Perspective Diversity=「必ず職種・立場を変える」ではない。同じ
#    Stakeholder群(どちらも一社員)でも、主要意見が明確に異なり、理由・
#    価値観・経験・制約が異なれば成立する(Trial-05のDiversity Check
#    基準を、本Trialではユーザー判断により上書きする)。
# 2. Perspective選定基準(Trial上採用): 「そのテーマで一般視聴者が認識
#    しやすい主要な意見・代表的な意見から順に採用」(Voice 1=最も主要、
#    Voice 2=次に主要…)。例外は面白さ・対立軸の明確さ・意味の違い・
#    Research裏付けのために認めるが、「diversity=特殊な立場を選ぶこと」
#    とは誤解しない。
#
# 本Trialの3段階:
# Phase A: 同じ固定席/free-addressテーマで、新Perspective(固定席派/
#   自由席派の社員2名)によるVoices記事を生成する。Research・5区切り
#   adapter・Analytical Leakage CheckはTrial-04/05から関数名も含め無
#   変更のまま再利用し、Focus Module Block(Voice Card・Diversity
#   Check根拠・Tension誘導)のみを書き直す。
# Phase B: Phase Aで得た同一Writer出力(pre_editor、Editor適用前)を
#   起点に、(1)Production既存Evidence Compression Editorあり版
#   (無変更で適用、Phase Aの最終article.mdがこれに相当)と、(2)Editor
#   なし版(Writer出力そのまま)を作り、Fact Safety(Fact Checker/Ledger
#   Deviation Checker+Local Rewrite/Directional Fact Precheck)を両方に
#   適用したうえで比較する。
# Phase C: EditorがVoices記事を明確に劣化させていると判断できる場合、
#   Production Editor本体は無変更のまま、Trial側の派生Editor block
#   (post-process)を設計し、(3)改善Editor案版を生成して3版比較する。
#   実際の劣化が無い/軽微な場合は、この派生blockを軽量な形にとどめるか、
#   Report内で理由とともに実施を見送る。
#
# 禁止: Production Prompt/code変更、B Family骨格の正式採用、Voice数3以上
# への拡張、Point Overlap/Value QA閾値変更、「品質が良くなるまで」の
# 無制限再生成(Writer本体は最大3回=初回+Leakage是正2回)、Case Story
# 設計、A Family 4層構造の正式化、テーマ自体の変更(固定席/free-address、
# POOL_TOPIC_MASTER.md No.7のまま)、A2/TTS/Assembly/11-part対応、3+
# Voices、Master記事正式採用、既存Fact Safety/Validatorの大きな変更、
# Git操作(成果物は作業ツリーに残し、Fableが後で統合commit)。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import requests

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "editorial_b_voices_trial_06_assigned_desks"
OUT_DIR = f"er012_output/editorial_b_voices_trial_06"
RESEARCH_DIR = f"{OUT_DIR}/research"
os.makedirs(RESEARCH_DIR, exist_ok=True)

# EDITORIAL-B-FAMILY-VOICES-TRIAL-06: テーマ・TOPIC_JA自体はTrial-04/05
# から変更しない(タスク指定「固定席テーマ」、POOL_TOPIC_MASTER.md No.7)。
# 本Trialでは、対比させる2つの立場をユーザーが「固定席を好む社員 vs
# 自由席(フリーアドレス)を好む社員」と先に指定しているが、その中で実際に
# どのようなConcern/Need/Protect/経験として描くかはPerspective Map・
# Diversity Check(下記、research/perspective_map.md参照)に委ねる。
TOPIC_JA = (
    "2026年9月時点、オフィスの座席運用が変わりつつある。パンデミック下で広がった"
    "フリーアドレス制(ホットデスキング、社員が毎日座席を選ぶ方式)をやめ、社員一人"
    "ひとりに専用の「固定席」を再び割り当てる動きが一部の企業で見られる一方、"
    "デスク共有(ホットデスキング)を維持・拡大する企業も依然として多い。この記事の"
    "中心テーマは、『固定席派 vs フリーアドレス派』のどちらが正しいかを決めることでは"
    "なく、同じオフィスで働く社員という同じ立場の中にも、固定席を好む人と自由席"
    "(フリーアドレス)を好む人がいて、それぞれになぜそう思うのか、何を大切にし、"
    "何を不便・不安・価値と感じ、どんな経験や条件からその考えに至っているのかを、"
    "実在する発言・調査・事例に基づいて具体的に描き、そのうえで、なぜ同じ状況が"
    "人によって違って見えるのかを理解することである。"
)

LABEL = "B1B"
# EDITORIAL-B-FAMILY-VOICES-TRIAL-06: run_trial06_pipeline()(Trial-05の
# run_trial06_pipeline()を関数名のみ変えて再利用)がAnalytical Leakage
# Check flaggedの場合に内部でWriterを最大2回再実行する(合計最大3
# attempts、Phase Aのみ)。各attemptの出力はb1b_run01_attempt1/・
# b1b_run01_attempt2/...のようにattempt番号付きの別ディレクトリへ保存し、
# 上書きしない(RUN_ID自体は固定、attempt番号はpipeline内部で管理する)。
RUN_ID = "run01"
LEVEL_OUT_DIR = f"{OUT_DIR}/{LABEL.lower()}_{RUN_ID}"


# ============================================================
# Research: Perplexity sonar-pro(既存承認済み呼び出しパターンの再実装、
# er011_open112_engagement_reference_cross_topic_ab_trial_11.py参照)
# ============================================================
PERPLEXITY_MODEL = "sonar-pro"


def _perplexity_call(theme_id: str, stage: str, model: str, messages: list[dict],
                      response_format: dict | None = None, timeout: float = 120.0) -> dict:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "CREDENTIAL_REQUIRED"}
    payload = {"model": model, "messages": messages}
    if response_format:
        payload["response_format"] = response_format
    t0 = time.time()
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload, timeout=timeout,
    )
    elapsed = round(time.time() - t0, 3)
    success = resp.status_code == 200
    if not success:
        cl.record({
            "provider": "perplexity", "api": "chat_completions", "model_id": model, "stage": stage,
            "attempt_number": 1, "success": False, "elapsed_seconds": elapsed,
            "usage_source": "N/A_FAILED_CALL", "http_status": resp.status_code,
        })
        return {"status": "FAILED", "http_status": resp.status_code, "elapsed_seconds": elapsed,
                "body": resp.text[:800]}
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    cl.record({
        "provider": "perplexity", "api": "chat_completions", "model_id": data.get("model"), "stage": stage,
        "theme": theme_id, "attempt_number": 1, "success": True, "elapsed_seconds": elapsed,
        "usage_source": "OFFICIAL_API_RESPONSE", "http_status": resp.status_code,
        "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    })
    return {
        "status": "OK", "content": content, "citations": data.get("citations", []),
        "search_results": data.get("search_results", []), "model": data.get("model"),
        "response_id": data.get("id"), "elapsed_seconds": elapsed, "usage": usage,
    }


# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: Trial-04のStage 1B/2B追加Research
# (14 facts、うち13件CONFIRMED・1件PARTIALLY_CONFIRMED)を、そのまま
# Perspective Map・Verified Fact Ledgerの土台として再利用する。新規
# Perplexity呼び出しは行わない(_perplexity_call()は既存承認済み呼び出し
# パターンとして関数のみ残すが、本Trialの標準経路では未使用)。
def run_research_stage() -> None:
    print("[TRIAL-06][Research] EDITORIAL-B-FAMILY-VOICES-TRIAL-05は新規Perplexity"
          "呼び出しを行わない。er012_output/editorial_b_voices_trial_04/research/配下"
          "(raw_facts_research_stakeholder.json・raw_facts_verification_stakeholder.json・"
          "facts_research_stakeholder_readable.txt・facts_verification_stakeholder_readable.txt、"
          "いずれも無変更のTrial-04資産)をそのまま参照し、Perspective Map"
          "(research/perspective_map.md)・Verified Fact Ledger"
          "(research/verified_fact_ledger.txt)を本Trial側で手作業でcurationする。")


# ============================================================
# B Family Common Skeleton(Layer2案)+ Voices Focus Module(Layer3案)
# ANCHOR挿入方式(Trial-05/09/10/11と同じ手法)
# ============================================================
ANCHOR = "【Spoken-first原則(数字の扱い)】"

B_FAMILY_VOICES_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(EDITORIAL-B-FAMILY-VOICES-TRIAL-06-PERSPECTIVE-SELECTION-EDITOR-DIAG-01、2026-09-07。Production未採用。この記事タイプ専用の骨格再定義)】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。以下は、上記の
一般的な役割定義・見出し構成を置き換えるのではなく、この記事に限り、それぞれのslotが何を
担い、どのMarkdown見出しで書くかを、より具体的に上書きする指示です。今回の記事では、以下の
役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(5区切り構造、厳守)】
上記「記事構成」節にある「Markdownの###見出しをちょうど2つ置く」という指示は、この記事
では次のように解釈してください: ###(レベル3見出し)は必ずちょうど2つだけ使い、それぞれ
1つ目のVoice・2つ目のVoiceの見出しとしてのみ使ってください。それに加えて、##(レベル2
見出し)を3つ使い、Hook・Tension・Closingの見出しとしてください。「Main Storyには見出しを
付けない」「## In one lineという見出し文言を使う」という上記の一般的な指示は、この記事に
限り、以下に置き換わります。記事全体は、必ず次の5つのMarkdown区切りを、この順序で持って
ください(見出し文言は下の例を基本としつつ、内容に応じて自然に言い換えてかまいませんが、
2つ目・3つ目の見出しには、「ここから別のVoiceが始まる」と聞き手に伝わる表現("One Voice:"
"Another Voice:"のような形)を必ず含めてください。"Voice A"/"Voice B"/"Perspective A"の
ような固定ラベル・番号ラベル、賛成/反対のような対称的なラベルは禁止です):

# [Title]

## The Question
[Hookの本文]

### One Voice: [その人物・立場が何者かが伝わる短いフレーズ]
[1つ目のVoiceの本文]

### Another Voice: [その人物・立場が何者かが伝わる短いフレーズ]
[2つ目のVoiceの本文]

## [Tensionの見出し。例: "Why They See It Differently"]
[Tensionの本文]

## [Closingの見出し。例: "What This Tells Us"]
[Closingの本文]

Tensionは、2つ目のVoiceの本文の続きの段落ではなく、独立した見出しを持つ独立したセクション
として書いてください。

【見出しは合計ちょうど5つ、これ以外の見出しを追加しないこと(重要、厳守)】
記事全体のMarkdown見出し(#・##・###のいずれも)は、上記の5つ(Title含めると6つ、Titleの
#は別枠)だけにしてください。以下は禁止です:
- 記事の最後に「## In one line」やそれに類する結びの見出しを追加すること(この記事タイプ
  では、5つ目の見出し["Closingの見出し"]が結びの役割を兼ねます。「## In one line」は
  別に追加しないでください)
- Tensionセクション・Closingセクションの中に、新しいMarkdown見出し(###や##)をさらに
  追加すること(切り口が複数ある場合も、見出しで区切らず、地の文の中でひとつづきの文章
  として書いてください)
- Voice以外の要素(まとめ・補足・解決策等)のための追加の見出しを作ること
書き終えた後、Hook相当・One Voice相当・Another Voice相当・Tension相当・Closing相当の
見出しがちょうど5つになっているか、自分で数え直してから出力してください。

【中心原則: Research is backstage. People are on stage.(EDITORIAL-B-FAMILY-VOICES-TRIAL-05で
導入、TRIAL-06でも維持)】
この記事の最大の失敗パターンは、Voiceのセクションが「調査結果を整理・説明する文章」に
なってしまうことです。これは個々の文をNGワードに置き換えるだけでは直らないため、今回は
書き始める前の材料の与え方そのものを変えます。あなたには、これから2枚のVoice Card(下記)を
渡します。Voice Cardは、Researchで確認された実在の人々の立場について、その人が何を経験し・
何を必要とし・何を心配し・何を守ろうとし・どんな条件からその考えに至っているかを、既に
こちらで整理したものです。**Voiceのセクションを書くときは、必ずVoice Cardの内容(その人の
状況・必要・心配・守りたいもの・具体的な場面)を主たる材料にして書き始めてください。
Voice Cardの後に置かれているVerified Fact Ledger(出典・数字を含む詳しいFact集)は、
Fact Checker・Ledger Deviation Checkのための正式な事実源であり続けますが、Voiceの文章を
組み立てる際の「主役」ではありません。** Ledgerは、Voice Cardに書かれている人物像が
実在することを裏側で支える裏付けとして、必要な範囲でさりげなく使ってください。Evidence
(調査・出典・統計)がVoiceの文章の主語になったり、Voiceの内容の中心になったりしては
いけません。

【この記事のPerspective選定について(重要な前提)】
この記事の2つのVoiceは、どちらも「同じオフィスで働く社員」という同じ立場の人です。役職や
責任の重さを変えて対立させるのではなく、同じ立場の人々の中でも意見が大きく分かれる、
最も一般的で代表的な2つの意見(Voice 1=固定席を好む/Voice 2=自由席・フリーアドレスを
好む)を、実在するResearch(街頭インタビュー・当事者インタビュー・従業員調査)から選んで
います。これは「特殊な立場を選ぶこと」がPerspective Diversityなのではなく、「同じ状況を
生きる人々の中で、なぜ結論が分かれるのか」を掘り下げることがPerspective Diversityである、
という考え方に基づいています。したがって、この2人を単なる「好みが違うだけの人」として
軽く扱わないでください。それぞれの意見の背後にある、具体的な経験・守りたいもの・
不便や不安に感じていることまで、Voice Cardの内容を使って丁寧に描いてください。

【Voice Card 1(1つ目のVoice。固定席を好む社員。この内容から書き始めてください)】
- Person: 週の大半をオフィスで働く社員。以前は「自分の席」があったが、今は毎回別の席を
  探す働き方(ホットデスキング)に置かれている。
- Situation(状況): 毎朝オフィスに来て、まだ誰にも使われていない空いている机を探す。
  昨日誰が座っていたかも分からない机に座ることもある。
- Need(必要としていること): 探さずに座れる、決まった居場所。資料や私物を置いておける
  場所。毎日同じような環境で仕事を始められる予測可能性。
- Concern(心配していること): 他人が使った後の机やキーボードに座ることへの衛生面の不安、
  私物を置く場所がないことへのストレス、職場に「自分の居場所」が無いという感覚。
- What they protect(守りたいもの): 職場での所属感と、集中して働ける感覚。
- Why they feel this way(なぜそう感じるのか、経験・条件): 毎日同じ机・同じ引き出し・
  同じ景色があることで、迷わずすぐ仕事に入れるという体験を積み重ねてきた。逆に、日によって
  違う人が隣に座る・違う机で作業する経験を重ねるうちに、「ここは自分の場所ではない」という
  感覚が積み重なっていった。
- Constraint(制約): 座席運用の決定権は無く、その日その日、与えられた環境の中で働くしか
  ない立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 毎朝オフィスに着いて、空いている
  机を探して座る。resource: [A-02/fact_003](衛生面の懸念・パーソナルスペース喪失への反発)、
  [A-05/fact_007](日本のフリーアドレス職場のパート社員が「自分の席がないので落ち着かない」
  「資料や私物を置く場所に困る」と語った実例)、[A-08/fact_008](TOKYO MX街頭インタビューで
  「席を探す時間がムダ」「チームが散るとコミュニケーションしづらいので固定席がいい」と
  語った会社員)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): Gensler調査(固定席ありの
  従業員は所属感87%・固定席なし74%、集中80%・67%)[A-01/fact_001]、Forbes調査で固定席の
  ない職場を「非人間的」「方向感覚を失う」「精神的に疲れる」と表現[A-03/fact_004]、
  ワークプレイス心理学者Oselandのコメント[A-04/fact_006]、ITmedia調査でフリーアドレス
  勤務者の36.8%が「席が固定化しがち」と回答[A-06/fact_009]。この裏付けの中から、1つの
  Voiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください
  (詳細ルールは下記【Voice内の数字】参照)。

【Voice Card 2(2つ目のVoice。自由席(フリーアドレス)を好む社員。この内容から書き始めて
ください)】
- Person: 同じオフィスで働く社員だが、決まった席を持つことより、その日ごとに場所を選べる
  ことを好むタイプ。
- Situation(状況): 出社する日ごとに、その日の仕事内容や気分に合わせて座る場所を選んでいる。
  静かに集中したい日は静かな一角に、他部署の人と話したい日はにぎやかなエリアに座る。
- Need(必要としていること): その日その日に必要な環境(集中できる場所か、人と話しやすい
  場所か)に応じて席を選べる自由。同じ場所・同じ顔ぶれに固定されないこと。
- Concern(心配していること): 毎日同じ席・同じ隣人に固定されることで、身動きが取れなく
  なる息苦しさ。人間関係で気まずいことがあったときや、単に離れたい気分のときに、逃げ場・
  距離を取る手段が無くなること。
- What they protect(守りたいもの): その日の自分のペース・気分・タスクに合わせて働ける
  自由度、色々な人と関われる開放感。
- Why they feel this way(なぜそう感じるのか、経験・条件): 在宅勤務等で既に自分だけの
  作業環境を持てるようになった結果、オフィスに「決まった居場所」を求める必要性を感じなく
  なり、むしろオフィスでは人と話せる・場所を変えられることに価値を見出すようになった。
  また、フリーアドレスで違う部署の人と話す機会が増えた経験や、集中したいときと協働したい
  ときで違うゾーンを選べた経験が、この考え方を後押ししている。
- Constraint(制約): Voice Card 1と同様、座席運用の決定権は無い立場。固定席へ戻す動きが
  進むほど、この自由度自体が失われていく側でもある。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 「その日の気分で場所を選べる自由が
  好き」「人間関係から距離を取りたい時に席を変えられる」というTOKYO MX街頭インタビューでの
  声[fact_008]。resource: [fact_012](Carr Workplacesが取材した12人のリーダーが語る、
  「社員はその日必要な思考に応じて場所を選び、その場所が固定席かどうかは重要ではない」と
  いう、集中ゾーン・協働ゾーンなど「認知ゾーン」で働き方を選ぶ発想)、[fact_007の一部]
  (日本のフリーアドレス職場のパート社員が「他部署の人と話しやすくなった」と語った実例、
  同じインタビューには「落ち着かない」という声も同居するが、Voice Card 2ではこの
  コミュニケーション面の実感のみを使う)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): CNET Japanの記事で、在宅勤務で
  自分の作業環境を持てた社員が、オフィスでは固定席にこだわらずコミュニケーションや共有
  空間に価値を見出すようになったという解説[fact_014]、TOKYO MXの街頭インタビューで50人中
  40人が「フリーアドレスはあり」と答えたという結果[fact_008]。この裏付けの中から、1つの
  Voiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください
  (詳細ルールは下記【Voice内の数字】参照)。

【この2つのVoiceがなぜ「単なる好みの違い」で終わらせてはいけないか(重要、Perspective
Diversity Checkの結果)】
Voice Card 1とVoice Card 2は、どちらも同じ立場(オフィスで働く社員)の人であり、「固定席が
好き/フリーアドレスが好き」という表面的な対立に見えるかもしれません。しかし、それぞれの
意見は、異なる経験・異なる条件から生まれています。Voice Card 1は、日々の小さな不便(机を
探す、私物の置き場がない、隣の人が毎日変わる)の積み重ねから、「決まった場所があることが
安心と集中を生む」という結論に至っています。Voice Card 2は、在宅勤務等で既に自分の落ち着ける
場所を持てるようになった経験や、場所を変えることで得られる交流・気分転換の経験から、
「決まった場所に縛られないことが自由と適応力を生む」という結論に至っています。どちらも
「自分にとって何が働きやすさなのか」という、それぞれにとって筋の通った結論です。**この
記事のTensionを書くときは、「どちらが正しいか」を決めるのではなく、なぜ同じオフィスで
働く社員という同じ立場でも、日々の経験や何を大事にしたいかの違いによって、合理的に違う
結論にたどり着くのかを掘り下げてください。** 候補となる切り口(これはあくまで候補であり、
どれか一つに決め打ちしないでください): 一貫性・予測可能性を求める気持ち vs 自由・変化を
求める気持ち / 「安心」の作り方の違い(同じ場所にいることで安心する人と、選べることで
安心する人) / 何によって「自分の居場所」を感じるかの違い(場所そのものか、その日必要な
ことができる環境か)。実際にどの切り口が最も説得力を持つかは、Voice Cardの内容と
Verified Fact Ledgerの範囲内で、あなた自身が判断してください。

【Voiceの書き始め方(重要)】
Voiceの本文は、"For [a/an] worker who..."のような、その人物のことを外側から要約・紹介する
文で始めないでください。これはVoiceを「説明されている対象」にしてしまい、当事者の視点
そのものとして立ち上がることを妨げます。代わりに、Voice Cardが示す具体的な状況(その人が
実際に毎日していること・直面していること・使っているもの、目にする光景)から書き始め、
そこからその人の感覚・必要性が自然に浮かび上がるようにしてください。目標は、読み手が
「この立場なら、たしかにそう感じるだろうな」と、外から説明されるのではなく内側から実感
できることです。反論のための藁人形にしないでください。

【Narrator(語り手)がVoiceの人物を外側から要約・分析しないこと(重要、Trial-05で最も
頻繁に検出された問題)】
Voiceのセクション内で、語り手がその人物の必要・感情・責任を外側から定義づけるような文
("The need is a stable start, with enough continuity to focus and feel included."、
"She is protecting her own sense of freedom."、"This person must choose between..."の
ような、Voiceの人物を三人称で要約・分析する文)を書かないでください。同様に、その人物
自身が実際には考えなさそうな、外部の分析的な視点(比較の含意・一般化した結論)を、その人の
Perspectiveであるかのように書かないでください。すべての文は、その人が実際にその瞬間に
していること・気づいていること・感じていることの描写として書いてください。

【Evidenceは脇役であること(重要)】
1つのVoiceの中で、Evidenceの紹介そのものが主役になる文を連続させないでください。その人の
経験・価値観・必要性の描写を主体にし、Evidence(Voice Cardの「Supporting evidence」欄、
およびVerified Fact Ledger)はその描写を裏から支えるためだけに、さりげなく織り込んで
ください。文の主語が調査・報告・データ("A survey found...", "One report described...",
"The data show...", "Research shows...", "Studies suggest...")になる文、"X% of workers
said..."、"People with X more often reported..."、"Compared with..."、"This suggests
that..."のような分析者の言い回しは書かないでください。数字を使うときは、必ず人を主語に
した実感として書いてください(例:「決まった机がある人の方が、職場に居場所があると感じ
やすい」のように、人が感じることとして表現し、"87% versus 74%"のような比較の形そのものを
読み上げないでください)。

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィング・リサーチサマリー
のような読み味にしないでください。Light・conversational・human-centeredに、友人に説明
するような、気軽に読める文章にしてください。専門用語や硬い分析用語を地の文で使うのでは
なく、日常の言葉でその人の感じ方を描いてください。

【Hookの役割と書き方(重要)】
Hook("## The Question")は、これから複数の立場を紹介するテーマ・状況を簡潔に提示する
導入です。どちらの立場が正しいかを示唆したり、結論を先取りしたりしないでください。目安は
100語未満です。読み手へ呼びかけたり、命令形・二人称で想像を促したりする表現("Imagine...",
"Picture...", "Think about...", "Consider...", "Now look at..."等)で始めないでください。
代わりに、具体的な情景そのものから、三人称で書き始めてください。小さく具体的な日常の一場面
(誰かがオフィスに来て、席を探す、どこに座るか選ぶ、荷物を置く、といった動作)を描写し、
そこから今回の問いへつなげてください。Hookに企業名・統計・パーセント・「移り変わりつつ
ある」というだけの業界動向要約を入れないでください。背景となる事実がどうしても必要な場合
でも1文以内にとどめ、数字を使わずに書いてください(例:「一部の会社は席を決め直し、別の
会社は自由席を続けている」程度の、数字を含まない一般的な書き方にとどめる)。

【Voice内の数字は最大1つ、必ずその人の実感に折り込むこと(重要)】
1つのVoiceのセクション全体を通して、具体的な数字(パーセント・人数・比率等)は最大1つ
だけにしてください。複数の数字を並べたり比較したりしないでください。その数字は、必ず
その人/その立場の人々の実感・経験に折り込み、話し言葉で書いてください。「a study of more
than 16,000」「reported」「showed the same pattern」「compared with」のような、調査・
比較を報告する文構造は使わないでください。2つ目のVoiceについても同じルールを適用して
ください。

【2つ目のVoiceの見出しの役割】
Voice Card 2の人物を、Voice Card 1と同様に、Verified Fact Ledgerの事実を用いて描いて
ください。2つのVoiceは、単に異なる数字・異なるデータを引用しているだけであってはいけ
ません。何によって安心・自由を感じるか・何を不便や息苦しさと感じるか・どんな経験が
その考えを形作ったかという、根本的な部分で異なっている必要があります(上記【この2つの
Voiceがなぜ「単なる好みの違い」で終わらせてはいけないか】参照)。

【Voice内に第三者の視点・解決策を混ぜないこと(重要)】
各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを描き切ってください。
解決策・妥協案・提案は、この記事では基本的に書かないでください(Solution articleでは
ありません)。どちらのVoiceの人物であっても、Voice本文の中で「こうすればよい」という
具体的な解決策の提案(例: 半固定席・ゾーン制の提案)を書かないでください。その人が抱える
悩み・気持ちの描写にとどめてください。

【Tensionの役割("## Why They See It Differently"相当)】
「どちらの考え方が正しいか」を決めようとしないでください。そうではなく、なぜ両方の
Voiceが、それぞれの立場からは合理的に見えるのかを掘り下げてください。具体的には: なぜ
両方とも理にかなって聞こえるのか / それぞれがどんな経験からその考えに至ったのか / それぞれ
が何を優先しているのか / それぞれにとって「自分の居場所がある」とはどういう状態を指すのか、
といった問いを言語化してください(候補となる切り口は上記【この2つのVoiceがなぜ「単なる
好みの違い」で終わらせてはいけないか】参照、どれか一つに決め打ちしないでください)。この
段落では2つのVoiceそれぞれが使った事実を横断的に参照してもかまいませんが、Verified Fact
Ledgerに無い新しい因果関係・新しい事実を作り出さないでください。単に「両方とも一理ある」
とまとめるだけの記述にしないでください。解決策の提案はここでも基本的に行わないでください。

【Closingの役割("## What This Tells Us"相当)】
これは要約でも、In One Lineの言い換えでもありません。2つのVoiceを両方見たことによって、
この問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを書いてください。
「どちらが正しいか」を決めず、「この2つのVoiceを知る前と後で、この問題をどう考えるべきか
がどう変わるか」という一段深い理解へ着地してください。内容はVerified Fact Ledgerが示す
複数のVoiceの構造的な違い(経験・価値観・必要・心配・得失の違い)の範囲内にとどめ、
Ledgerにない新しい因果関係・断定を創作しないでください(Evidence-bounded Interpretation
原則を継続して守ってください)。

【Point Balance原則・言い換え禁止・Point長さ目標(上記既存指示)の扱いについて】
上記の一般的なPoint One/Two役割リスト(切り口・示唆・背景・心理・社会的含意等)は、
この記事では「異なる実在のstakeholder perspectiveを描く」という上記の役割に置き換わり
ます。ただし、「本文の言い換え禁止」「Point同士が同じ役割を担わない」という原則自体は
維持してください。Point One・Point Twoの長さ目標(30-60語、許容範囲25-70語)は、
Discovery/Why記事向けの目安でありこの記事には適用しません。

【記事全体の長さについて(この記事専用、hard/soft gateなし)】
記事全体の総語数は、350〜420語程度を観察用の目安としてよいですが、hard capでもsoft gate
でもありません。長さを目安に合わせるための不自然な削除・水増しはせず、Voiceの人間らしい
描写を削らないでください。

【禁止事項まとめ(この記事全体を通して)】
- Reference Example由来の定型的な呼びかけ表現("Imagine...", "Picture...", "Think
  about...", "Consider..."等)をコピー・準用すること
- "Voice A"/"Voice B"/"Perspective A"のような固定ラベル・番号ラベル
- 文の主語がEvidence(survey/report/data/study)になる文
- Narrator(語り手)がVoiceの人物を外側から要約・分析する文(例: "The need is...",
  "She is protecting...", "This person must...")
- Voiceのセクションへ第三者(設計者・コンサルタント)の視点を持ち込むこと、または
  どちらのVoiceの人物であっても具体的な解決策・妥協案をVoice本文内で提案すること
- Hookに企業名・統計・パーセント・業界動向のトレンド要約を入れること
- 1つのVoiceのセクション内で具体的な数字を2つ以上使うこと、または「a study of...」
  「reported」「showed the same pattern」「compared with」のような調査・比較を
  報告する文構造を使うこと
- Voice Cardの内容を経由せず、Verified Fact Ledgerの記述(出典名・数字の列挙)から
  直接Voiceの文章を組み立てること"""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    assert gen.COMMON_BLOCK_TEMPLATE.count(ANCHOR) == 1, (
        "アンカー文字列が複数回出現しています。挿入位置が一意に定まらないため中断してください。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


def run_phase_a(audit_dir: str) -> dict:
    # EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02: 監査ファイルの出力先を
    # 呼び出し元から受け取るように変更(run01のOUT_DIR/audit/配下を上書き
    # しないため、run02からはLEVEL_OUT_DIR/audit/配下を渡す)。
    os.makedirs(audit_dir, exist_ok=True)
    candidate_template = build_candidate_template()
    with open(f"{audit_dir}/phase_a_candidate_template.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)
    with open(f"{audit_dir}/phase_a_b_family_voices_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(B_FAMILY_VOICES_FOCUS_MODULE_BLOCK)

    reconstructed = gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
    clean_single_insert = (reconstructed == candidate_template)
    result = {"clean_single_insert_confirmed": clean_single_insert,
              "baseline_len": len(gen.COMMON_BLOCK_TEMPLATE), "candidate_len": len(candidate_template)}
    with open(f"{audit_dir}/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-06][Phase A] clean_single_insert_confirmed={clean_single_insert}")
    return {"result": result, "phase_a_pass": clean_single_insert, "candidate_template": candidate_template}


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run03専用: 5区切り構造(Hook/Voice A/
# Voice B/Tension/Closing)のTrial-only parser。Production側のsplit_common_
# sections_for_point_qa()は「###見出しがちょうど2つ」であることを検出できる
# ため実際には呼び出せてしまうが、point_two_bodyの終端を「## In one line」
# という特定文言でしか検出できず、run03の"## Why They See It Differently"
# "## What This Tells Us"は終端として認識されない(Voice B本文にTension・
# Closingまで混入してしまう)。そのため、5見出し全てを見出し出現順にそのまま
# 抽出する専用parserをここに実装する(Production側のファイルは一切変更
# しない、読み取り専用importのまま)。
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)


def split_five_voice_sections(article_text: str) -> dict | None:
    """run03の5区切り構造を見出し出現順(Hook/Voice A/Voice B/Tension/
    Closing)に抽出する。ちょうど5つの##または###見出しがTitleの後に
    連続して登場することを前提とする。想定外の構造(見出し数が5でない等)
    の場合はNoneを返す(呼び出し側はmonitoring不能として記録する)。"""
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 5:
        return None
    labels = ["hook", "voice_a", "voice_b", "tension", "closing"]
    result = {}
    for i, label in enumerate(labels):
        heading_text = matches[i].group(2).strip()
        heading_level = len(matches[i].group(1))
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_heading_level"] = heading_level
        result[f"{label}_body"] = body[content_start:content_end].strip()
    preamble = body[:matches[0].start()].strip()
    result["unexpected_preamble_before_first_heading"] = preamble
    return result


def run_five_section_point_qa_monitoring(client, sections: dict, writer_model: str, out_dir: str) -> dict:
    """run03専用のPoint Overlap/Value QA monitoring。ACTIVE_TASK指示
    「Voice A/Bをpoint_one/point_two相当として個別に呼ぶ」に対応し、
    gen.run_point_overlap_qa_and_regenerate()を経由せず、その内部で使われて
    いるer008_point_overlap_qa_18.flag_possible_paraphrase()と
    er011_point_role_value_planning_01.run_point_value_qa()を、
    split_five_voice_sections()で抽出したHook/Voice A/Voice Bへ直接個別に
    呼び出す(Production側の2関数自体は無変更)。既存policy通りmonitoring
    専用(flaggedでもretry・早期returnしない、本文も変更しない)。"""
    hook = sections["hook_body"]
    voice_a = sections["voice_a_body"]
    voice_b = sections["voice_b_body"]

    voice_a_vs_hook = overlap_qa.flag_possible_paraphrase(voice_a, hook)
    voice_b_vs_hook = overlap_qa.flag_possible_paraphrase(voice_b, hook)
    voice_a_vs_voice_b = overlap_qa.flag_possible_paraphrase(voice_a, voice_b)
    voice_b_vs_voice_a = overlap_qa.flag_possible_paraphrase(voice_b, voice_a)
    lexical_flagged = any(r["flagged"] for r in
                           (voice_a_vs_hook, voice_b_vs_hook, voice_a_vs_voice_b, voice_b_vs_voice_a))

    value_qa_result = point_planning.run_point_value_qa(
        client, hook, voice_a, voice_b, model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
    value_qa_flagged = value_qa_result["status"] == "NG"

    monitoring_summary = {
        "qa_status": "OK",
        "lexical_flagged": lexical_flagged,
        "value_qa_flagged": value_qa_flagged,
        "note": ("EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run03のユーザー決定によりmonitoring専用。"
                 "flaggedであっても記事全体retry・Point-only regenerationは一切発生させず、"
                 "本文は変更せずそのままFact Checker以降へ進める。gen.run_point_overlap_qa_and_"
                 "regenerate()ではなく、5区切り構造専用のsplit_five_voice_sections()で抽出した"
                 "Voice A/Voice Bを、同じProduction primitive関数(overlap_qa.flag_possible_"
                 "paraphrase / point_planning.run_point_value_qa)へ個別に渡している。"),
        "voice_a_vs_hook": voice_a_vs_hook,
        "voice_b_vs_hook": voice_b_vs_hook,
        "voice_a_vs_voice_b": voice_a_vs_voice_b,
        "voice_b_vs_voice_a": voice_b_vs_voice_a,
        "value_qa_status": value_qa_result["status"],
        "value_qa_result": value_qa_result,
    }
    with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
        json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-06][run03] Point Overlap/Value QA monitoring(5区切り専用) "
          f"lexical_flagged={lexical_flagged} value_qa_flagged={value_qa_flagged}(gateにはしない)")
    return monitoring_summary


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: 5区切り構造専用Writer Trial adapter
# (Trial-04のrun_voices_pattern_run03()を関数名も含め無変更のまま再利用)。
# gen.run_one_pattern()のFact Checker/Ledger Deviation Checker(+Local
# Rewrite)/Directional Fact Precheckの呼び出し・引数・順序は一切変更せず
# コピーする。Point Overlap/Value QAはmonitoring専用(gateにしない、
# retryを誘発しない)。5区切り構造(Hook/Voice A/Voice B/Tension/Closing)
# 専用のsplit_five_voice_sections()を使ってQA monitoring・語数内訳を計算
# する。Production側のsplit_common_sections_for_point_qa()は「## In one
# line」という特定文言でしか終端を検出できず、sf1r1.section_word_counts()
# も同様にこの5見出し構造を正しく解釈しない(Hook/Tension/Closingの内容が
# 丸ごと欠落する)ため、5区切りの正確な内訳はfive_section_length_report.json
# へ別途保存する(sf1r1.section_word_counts()自体は無変更のまま参考値として
# 引き続き呼び出す)。
# ============================================================
def _five_section_length_report(article_text: str) -> dict | None:
    sections = split_five_voice_sections(article_text)
    if sections is None:
        return None
    counts = {
        key: ab01.compute_word_count(sections[f"{key}_body"])
        for key in ("hook", "voice_a", "voice_b", "tension", "closing")
    }
    counts["total_of_five_sections"] = sum(counts.values())
    counts["headings"] = {
        key: sections[f"{key}_heading"] for key in ("hook", "voice_a", "voice_b", "tension", "closing")
    }
    counts["unexpected_preamble_before_first_heading"] = sections["unexpected_preamble_before_first_heading"]
    return counts


def run_voices_pattern_run03(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                              topic: str, out_dir: str, apply_evidence_compression: bool = True,
                              apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    role_plan_result = point_planning.run_point_role_planning(
        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
    with open(f"{out_dir}/audit/point_role_planning_initial.json", "w", encoding="utf-8") as f:
        json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
    prompt_with_plan = prompt + "\n" + point_planning.build_role_planning_block(role_plan_result["parsed"])

    gen_result = gen._generate_and_compress_article(
        client, theme_id, label, prompt_with_plan, out_dir, apply_evidence_compression, writer_model)
    if gen_result["status"] != "OK":
        return {"label": label, "status": gen_result["status"], "article_text": None}
    article_text = gen_result["article_text"]
    fact_usage_report = gen_result["fact_usage_report"]
    evidence_compression_applied = gen_result["evidence_compression_applied"]

    # --- Point Overlap QA / Point Value QA: monitoring専用、5区切り構造専用
    # parser経由(理由は上記コメント参照)。
    print(f"[TRIAL-06][{theme_id}] {label}: Point Overlap/Value QA(monitoring専用、5区切り版)開始...")
    five_sections = split_five_voice_sections(article_text)
    if five_sections is None:
        monitoring_summary = {
            "qa_status": "SKIPPED",
            "lexical_flagged": False, "value_qa_flagged": False,
            "note": ("split_five_voice_sections()が想定する5見出し構造(Title後に##/###見出しが"
                     "ちょうど5つ、Hook/Voice A/Voice B/Tension/Closingの順)を検出できなかった"
                     "ため、Point Overlap/Value QA monitoringはmonitoring不能として記録する。"),
        }
        with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
            json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-06][{theme_id}] {label}: 5区切り構造が検出できずQA monitoring不能として記録しました。")
    else:
        monitoring_summary = run_five_section_point_qa_monitoring(client, five_sections, writer_model, out_dir)

    # --- 以下、gen.run_one_pattern()のFact Checker/Ledger Deviation
    # Checker/Local Rewrite/Directional Fact Precheckロジックを、呼び出す
    # 関数・引数・順序とも一切変更せずそのままコピーする(run_voices_pattern()
    # と同一)。length_reportのみ5区切り版へ差し替える。---
    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    five_section_report = _five_section_length_report(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
        "sf1r1_section_word_counts_note": ("sf1r1.section_word_counts()はrun03の5見出し構造を"
            "正確には解釈しない(「in one line」を含まない##見出し=Hook/Tension/Closingの内容を"
            "header_skipとして集計から丸ごと落とす。intro/in_one_lineは常に0になる。point_one/"
            "point_twoの値自体はrun03が###見出しを常にちょうど2つ[Voice A/Voice Bのみ]しか使わない"
            "設計のため実測上は正しいが、Hook/Tension/Closingが欠落するため記事全体の内訳としては"
            "使えない)。参考値としてのみ残す。正確な内訳はfive_section_length_report.jsonを参照。"),
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    if five_section_report is not None:
        with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
            json.dump(five_section_report, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-06][{theme_id}] {label}: metrics={metrics} five_section_report={five_section_report}")

    print(f"[TRIAL-06][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[TRIAL-06][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    if verdict == "FAIL":
        print(f"[TRIAL-06][{theme_id}] {label}: fact checkerがFAILと判定しました。自動続行せず"
              f"NG_REVIEW_REQUIREDとして報告します(ledger逸脱チェック以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
            "five_section_length_report": five_section_report,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_result,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_value_qa_monitoring": monitoring_summary,
        }

    print(f"[TRIAL-06][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[TRIAL-06][{theme_id}] {label}: deviation overall_status="
          f"{deviation_result['parsed']['overall_status']} deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[TRIAL-06][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は新規)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[TRIAL-06][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
                  f"human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        metrics = gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        five_section_report = _five_section_length_report(article_text)
        length_report = {
            **section_wc, "total": metrics["word_count"],
            "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
            "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
            "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
            "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
            "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
        }
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
            json.dump(length_report, f, ensure_ascii=False, indent=2)
        if five_section_report is not None:
            with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
                json.dump(five_section_report, f, ensure_ascii=False, indent=2)

        print(f"[TRIAL-06][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[TRIAL-06][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[TRIAL-06][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存、"
              f"またはhuman_review_requiredな項目があります。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
            "five_section_length_report": five_section_report,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_value_qa_monitoring": monitoring_summary,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[TRIAL-06][{theme_id}] {label}: 比較方向Fact事前チェック開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-06][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "five_section_length_report": five_section_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "fact_usage_report": fact_usage_report,
        "evidence_compression_applied": evidence_compression_applied,
        "point_overlap_value_qa_monitoring": monitoring_summary,
        "directional_fact_precheck_status": directional_precheck_status,
    }


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: Analytical Leakage Check(新規、
# タスク文書§J準拠)。Production側コードは一切変更しない。既存の
# er011_point_role_value_planning_01.run_point_value_qa()と同じ
# client.responses.create() + json_schema(strict) + reasoning_effort +
# response.model一致検証パターンを踏襲した、本Trial限定の新規関数。
# Writer生成後、split_five_voice_sections()で抽出したVoice A/Voice B本文
# それぞれについて、タスク文書§Jの6基準を判定する。flaggedの場合、記事本文
# を手で書き換えるのではなく、具体的な引用付きの是正メモをpromptへ追加して
# Writerを再実行する(run_trial06_pipeline())。
# ============================================================
LEAKAGE_CHECK_FIELDS = (
    "leak_evidence_subject",     # J(1): survey/research/data/percentageが主語になっていないか
    "leak_numbers_foreground",   # J(2): 数字・比較結果がVoiceより前面に出ていないか
    "leak_narrator_analysis",    # J(3): NarratorがVoiceを外から分析していないか
    "leak_unknowable_analysis",  # J(4): Voice本人には知り得ない分析をその人のPerspectiveとして書いていないか
    "leak_discovery_syntax",     # J(5): Discovery/Trend型の説明構文へ戻っていないか
    "leak_evidence_memorable",   # J(6): 「人」よりEvidenceの方が記憶に残るsectionになっていないか
)

LEAKAGE_CHECK_DEVELOPER_MESSAGE = (
    "あなたは'Voices/Perspective'型記事のVoice sectionを審査する、厳格なEditorial QA判定者"
    "です。Voice sectionが、実在する当事者(人)の経験・価値観・必要・心配として書かれて"
    "いるか、それとも調査結果・データを整理して説明する文章に戻っていないかを、6つの基準"
    "それぞれについてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、FAILは"
    "『その問題が実際に本文に存在する』ことを意味します。FAILの場合は、該当する原文の一節を"
    "quoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。PASSの"
    "場合はquoted_evidenceを空文字列にしてください。"
)


def _leakage_item_schema() -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in LEAKAGE_CHECK_FIELDS}
    props["reasoning"] = {"type": "string"}
    props["quoted_evidence"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()),
            "additionalProperties": False}


ANALYTICAL_LEAKAGE_JSON_SCHEMA = {
    "name": "analytical_leakage_check",
    "schema": {
        "type": "object",
        "properties": {"voice_a": _leakage_item_schema(), "voice_b": _leakage_item_schema()},
        "required": ["voice_a", "voice_b"],
        "additionalProperties": False,
    },
    "strict": True,
}

LEAKAGE_CHECK_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事の2つのVoice section本文です。
それぞれについて、以下6項目を判定してください(それぞれPASS/FAIL)。

- leak_evidence_subject: 文の主語がsurvey/research/data/percentage(調査・報告・データ)に
  なっている文が無い場合PASS(例: "A survey found...", "Research shows...", "X% of
  workers said..."のような文が無い場合PASS)
- leak_numbers_foreground: 具体的な数字・比較結果(パーセント・人数比較等)が、その人の
  経験の描写より前面に出ていない場合PASS(数字が0個、または1個だけがその人の実感として
  自然に織り込まれている場合はPASS。複数の数字が連続して比較されている場合はFAIL)
- leak_narrator_analysis: Narrator(語り手)が、Voiceの人物を外側から分析・要約していない
  場合PASS(例: "For a worker who..."のような紹介・要約文で始まっていたり、"This suggests
  that..."のような分析者の言い回しが無い場合PASS)
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点
  (第三者の解決策・比較の含意等)を、その人のPerspectiveとして書いていない場合PASS
- leak_discovery_syntax: 「調査結果を整理して説明する」Discovery/Trend記事のような文構造
  (reported/showed the same pattern/compared with等)へ戻っていない場合PASS
- leak_evidence_memorable: このsectionを読み終えたときに、Evidence(数字・出典)よりも
  その人物の経験・感情の方が記憶に残る書き方になっている場合PASS

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに
該当する原文を引用してください(英語本文をそのまま引用してよい)。PASSの場合quoted_evidence
は空文字列にしてください。

【One Voice(Voice A)本文】
{voice_a_body}

【Another Voice(Voice B)本文】
{voice_b_body}
"""


class LeakageCheckModelMismatchError(RuntimeError):
    pass


def run_analytical_leakage_check(client, sections: dict, model: str, reasoning_effort: str,
                                  out_dir: str, attempt: int) -> dict:
    voice_a_body = sections["voice_a_body"]
    voice_b_body = sections["voice_b_body"]
    prompt = LEAKAGE_CHECK_PROMPT_TEMPLATE.format(voice_a_body=voice_a_body, voice_b_body=voice_b_body)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **ANALYTICAL_LEAKAGE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": LEAKAGE_CHECK_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise LeakageCheckModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Analytical Leakage Check応答が空です")
    parsed = json.loads(text)

    flagged_items = []
    for voice_key in ("voice_a", "voice_b"):
        item = parsed[voice_key]
        fail_fields = [f for f in LEAKAGE_CHECK_FIELDS if item[f] == "FAIL"]
        if fail_fields:
            flagged_items.append({
                "voice": voice_key, "fail_fields": fail_fields,
                "reasoning": item["reasoning"], "quoted_evidence": item["quoted_evidence"],
            })
    result = {
        "model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed,
        "flagged_items": flagged_items, "any_flagged": bool(flagged_items),
    }
    with open(f"{out_dir}/analytical_leakage_check_attempt{attempt}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-06][Leakage Check] attempt{attempt}: any_flagged={result['any_flagged']} "
          f"flagged_items={[(x['voice'], x['fail_fields']) for x in flagged_items]}")
    return result


def build_leakage_corrective_note(leakage_result: dict) -> str:
    """flagged項目を具体的な引用付きでprompt末尾へ追加する是正メモ。記事本文を
    手で書き換えるのではなく、Writerへ次のattemptで避けるべき点を明示する。"""
    lines = [
        "【Analytical Leakage Check是正メモ(前回attemptの検出結果。Voice Card・Verified "
        "Fact Ledger・骨格は変更しません。今回はこの記事全文をゼロから新しく書き直して"
        "ください。前回の文をそのまま部分修正するのではなく、Voice Cardの内容[人物の状況・"
        "必要・心配・守りたいもの・具体的な場面]から書き始め、以下の問題を避けてください)】",
    ]
    voice_label = {"voice_a": "One Voice(Voice A)", "voice_b": "Another Voice(Voice B)"}
    for item in leakage_result["flagged_items"]:
        lines.append(f"- {voice_label[item['voice']]}で検出: {', '.join(item['fail_fields'])}")
        lines.append(f"  理由: {item['reasoning']}")
        if item["quoted_evidence"]:
            lines.append(f"  該当箇所(この種の書き方を避ける): \"{item['quoted_evidence']}\"")
    return "\n".join(lines)


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: Writer + Analytical Leakage Check
# パイプライン。Analytical Leakage Checkがflaggedの場合、記事本文を手で
# 書き換えず、build_leakage_corrective_note()をpromptへ追加してWriterを
# 再実行する(run_voices_pattern_run03()をフルパイプラインとして再実行、
# Fact Checker/Ledger Deviation Checker等も含め全てやり直す)。最大2回まで
# 再実行する(合計最大3 attempts)。各attemptの出力はattempt番号付きの別
# ディレクトリへ保存し、上書きしない。
# ============================================================
MAX_WRITER_ATTEMPTS = 3  # 初回1回 + 是正再実行最大2回


def run_trial06_pipeline(client, theme_id: str, label: str, base_prompt: str, verified_ledger_text: str,
                          topic: str, out_dir_base: str) -> dict:
    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    attempt_history = []
    corrective_note = ""
    final_result = None
    final_attempt_dir = None

    for attempt in range(1, MAX_WRITER_ATTEMPTS + 1):
        attempt_dir = f"{out_dir_base}_attempt{attempt}"
        prompt_for_attempt = base_prompt + (f"\n\n{corrective_note}" if corrective_note else "")
        os.makedirs(f"{attempt_dir}/audit", exist_ok=True)
        with open(f"{attempt_dir}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
            f.write(prompt_for_attempt)

        print(f"[TRIAL-06] Writer attempt {attempt}/{MAX_WRITER_ATTEMPTS} 開始(out_dir={attempt_dir})...")
        t0 = time.time()
        with cl.logging_context(theme_id, f"writer_{label.lower()}_attempt{attempt}"):
            result = run_voices_pattern_run03(
                client, theme_id, label, prompt_for_attempt, verified_ledger_text, topic, attempt_dir)
        result["elapsed_seconds"] = round(time.time() - t0, 1)

        entry = {"attempt": attempt, "out_dir": attempt_dir, "status": result.get("status")}
        final_result = result
        final_attempt_dir = attempt_dir

        if result.get("status") != "OK" or not result.get("article_text"):
            entry["leakage_check"] = None
            entry["any_flagged"] = None
            attempt_history.append(entry)
            print(f"[TRIAL-06] attempt {attempt}: status={result.get('status')}のためLeakage Check"
                  f"をスキップします。")
            break

        sections = split_five_voice_sections(result["article_text"])
        if sections is None:
            entry["leakage_check"] = {"qa_status": "SKIPPED_NO_FIVE_SECTIONS"}
            entry["any_flagged"] = None
            attempt_history.append(entry)
            final_result["five_voice_sections"] = None
            print(f"[TRIAL-06] attempt {attempt}: 5区切り構造が検出できずLeakage Checkをスキップ"
                  f"しました。")
            break

        leakage = run_analytical_leakage_check(
            client, sections, writer_model, gen.REASONING_EFFORT, attempt_dir, attempt)
        entry["leakage_check"] = leakage
        entry["any_flagged"] = leakage["any_flagged"]
        attempt_history.append(entry)
        final_result["five_voice_sections"] = sections
        final_result["analytical_leakage_check"] = leakage

        if not leakage["any_flagged"]:
            print(f"[TRIAL-06] attempt {attempt}: Analytical Leakage Check flagged項目なし。確定。")
            break
        if attempt == MAX_WRITER_ATTEMPTS:
            print(f"[TRIAL-06] attempt {attempt}: 最大attempt数に到達。flagged項目が残った状態の"
                  f"記事を最終結果として記録します(Report側でUSER_DECISION_REQUIRED候補として扱う)。")
            break
        corrective_note = build_leakage_corrective_note(leakage)

    with open(f"{out_dir_base}_attempt_history.json", "w", encoding="utf-8") as f:
        json.dump(attempt_history, f, ensure_ascii=False, indent=2, default=str)

    return {
        "final_result": final_result, "final_attempt_dir": final_attempt_dir,
        "attempt_history": attempt_history, "total_attempts": len(attempt_history),
    }


def run_writer_stage() -> dict:
    ledger_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    if not os.path.exists(ledger_path):
        raise SystemExit(f"Curated ledger not found at {ledger_path}. Run research stage and curate first.")
    with open(ledger_path, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    phase_a = run_phase_a(f"{OUT_DIR}/audit")
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-06] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "pipeline": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial06_writer.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text,
        gen.B1_B_DIRECT_INSTRUCTION)
    with open(f"{OUT_DIR}/audit_candidate_prompt_base.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    print(f"[TRIAL-06] Writer + Analytical Leakage Checkパイプライン開始"
          f"(最大{MAX_WRITER_ATTEMPTS} attempts)...")
    pipeline_result = run_trial06_pipeline(
        client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, TOPIC_JA, LEVEL_OUT_DIR)

    with open(f"{OUT_DIR}/trial06_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": pipeline_result["attempt_history"],
            "total_attempts": pipeline_result["total_attempts"],
            "final_attempt_dir": pipeline_result["final_attempt_dir"],
            "final_result": {k: v for k, v in (pipeline_result["final_result"] or {}).items()
                              if k not in ("article_text", "five_voice_sections")},
        }, f, ensure_ascii=False, indent=2, default=str)

    final_result = pipeline_result["final_result"] or {}
    print(f"[TRIAL-06] 完了。total_attempts={pipeline_result['total_attempts']} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"phase_a": phase_a, "pipeline": pipeline_result, "status": "DONE"}


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-06 Phase B/C: Editorあり/なし/改善案の
# 比較(タスク文書のPhase B/C)。run_voices_pattern_run03()の後半(Writer+
# Editor呼び出しの直後、metrics以降)と全く同じFact Safety/QAロジックを、
# 「既に確定しているarticle_text」に対して適用できるよう関数として切り出す
# (Production側関数の呼び出し・引数・順序は一切変更しない、単に呼び出す
# タイミングをWriter直後から任意のarticle_textへ変えるだけ)。これにより、
# Phase Aで得たpre_editor_article.md(Editorなし版)・改善Editor案適用後の
# テキストの双方に、Phase Aのeditorあり版(article.md)と全く同じFact
# Checker/Ledger Deviation Checker(+Local Rewrite)/Directional Fact
# Precheck/Point Overlap・Value QA monitoring/Analytical Leakage Checkを
# 適用できる。
# ============================================================
def run_fact_safety_and_qa_from_text(client, theme_id: str, label: str, article_text: str,
                                      verified_ledger_text: str, topic: str, out_dir: str,
                                      apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: Point Overlap/Value QA(monitoring専用、5区切り版)開始...")
    five_sections = split_five_voice_sections(article_text)
    if five_sections is None:
        monitoring_summary = {
            "qa_status": "SKIPPED",
            "lexical_flagged": False, "value_qa_flagged": False,
            "note": ("split_five_voice_sections()が想定する5見出し構造を検出できなかったため、"
                     "Point Overlap/Value QA monitoringはmonitoring不能として記録する。"),
        }
        with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
            json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
    else:
        monitoring_summary = run_five_section_point_qa_monitoring(client, five_sections, writer_model, out_dir)

    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    five_section_report = _five_section_length_report(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    if five_section_report is not None:
        with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
            json.dump(five_section_report, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: metrics={metrics}")

    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    leakage_result = None
    if five_sections is not None:
        leakage_result = run_analytical_leakage_check(
            client, five_sections, writer_model, gen.REASONING_EFFORT, out_dir, 1)

    if verdict == "FAIL":
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: fact checkerがFAILと判定。"
              f"ledger逸脱チェック以降は実行せずNG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
            "five_section_length_report": five_section_report, "five_voice_sections": five_sections,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_result,
            "point_overlap_value_qa_monitoring": monitoring_summary,
            "analytical_leakage_check": leakage_result,
        }

    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: deviation overall_status="
          f"{deviation_result['parsed']['overall_status']} deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は新規)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
                  f"human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        metrics = gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        five_section_report = _five_section_length_report(article_text)
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        if five_section_report is not None:
            with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
                json.dump(five_section_report, f, ensure_ascii=False, indent=2)

        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが"
              f"残存、またはhuman_review_requiredな項目があります。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
            "five_section_length_report": five_section_report, "five_voice_sections": five_sections,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
            "point_overlap_value_qa_monitoring": monitoring_summary,
            "analytical_leakage_check": leakage_result,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: 比較方向Fact事前チェック開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-06][PhaseB/C][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "five_section_length_report": five_section_report, "five_voice_sections": five_sections,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "point_overlap_value_qa_monitoring": monitoring_summary,
        "directional_fact_precheck_status": directional_precheck_status,
        "analytical_leakage_check": leakage_result,
    }


def _load_phase_a_final() -> dict:
    """Phase B/Cから、Phase Aで既に確定した最終attemptの情報(article_text
    [Editorあり版]・pre_editor_article.md[Editorなし、Writer生の出力]・
    verified_ledger_text)を読み込む。Phase Aを事前に実行しておく必要がある
    (run_writer_stage()、または`python er012_editorial_b_voices_trial_06.py write`)。"""
    summary_path = f"{OUT_DIR}/trial06_summary.json"
    if not os.path.exists(summary_path):
        raise SystemExit(f"{summary_path} が見つかりません。先にPhase A(stage=write)を実行してください。")
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)
    final_attempt_dir = summary["final_attempt_dir"]
    with open(f"{final_attempt_dir}/article.md", encoding="utf-8") as f:
        editor_article_text = f.read()
    pre_editor_path = f"{final_attempt_dir}/audit/pre_editor_article.md"
    if not os.path.exists(pre_editor_path):
        raise SystemExit(f"{pre_editor_path} が見つかりません(Evidence Compression Editorが"
                          f"適用されなかった可能性)。apply_evidence_compression=Trueで再実行してください。")
    with open(pre_editor_path, encoding="utf-8") as f:
        pre_editor_text = f.read()
    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()
    return {
        "final_attempt_dir": final_attempt_dir,
        "editor_article_text": editor_article_text,
        "pre_editor_text": pre_editor_text,
        "verified_ledger_text": verified_ledger_text,
        "summary": summary,
    }


def _unified_word_diff(label_a: str, text_a: str, label_b: str, text_b: str) -> list[str]:
    """行単位のunified diff(段落・見出しごとに改行が入っているMarkdown本文
    なので行単位で十分な粒度になる)。原文引用付きのReport作成用。"""
    import difflib
    return list(difflib.unified_diff(
        text_a.splitlines(), text_b.splitlines(), fromfile=label_a, tofile=label_b, lineterm=""))


def run_phase_b() -> dict:
    """タスク文書Phase B: 同一Writer出力(pre_editor)を起点に、(1)Editorあり版
    (Phase Aのarticle.md、無変更で適用済み)と(2)Editorなし版(pre_editor_
    article.mdそのもの)を比較する。(2)にはFact Safety(Fact Checker/Ledger
    Deviation Checker+Local Rewrite/Directional Fact Precheck)・Point
    Overlap/Value QA monitoring・Analytical Leakage Checkを、(1)と全く同じ
    ロジックで新規に適用する(Production側関数は無変更のまま)。"""
    phase_a_final = _load_phase_a_final()
    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial06_phase_b.jsonl")

    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()

    version2_dir = f"{OUT_DIR}/phase_b_no_editor"
    print(f"[TRIAL-06][PhaseB] Editorなし版(pre_editor_article.mdそのもの)へFact Safety/QAを適用...")
    version2_result = run_fact_safety_and_qa_from_text(
        client, THEME_ID, LABEL, phase_a_final["pre_editor_text"], verified_ledger_text, TOPIC_JA,
        version2_dir)

    diff_lines = _unified_word_diff(
        "editor_version(article.md)", phase_a_final["editor_article_text"],
        "no_editor_version(pre_editor_article.md)", phase_a_final["pre_editor_text"])
    diff_text = "\n".join(diff_lines)
    with open(f"{OUT_DIR}/phase_b_editor_vs_no_editor.diff", "w", encoding="utf-8") as f:
        f.write(diff_text)

    summary = {
        "phase_a_final_attempt_dir": phase_a_final["final_attempt_dir"],
        "version1_editor": {
            "status": "OK (Phase Aの最終attemptをそのまま参照。再実行していない)",
            "article_path": f"{phase_a_final['final_attempt_dir']}/article.md",
        },
        "version2_no_editor": {k: v for k, v in version2_result.items()
                                if k not in ("article_text", "five_voice_sections")},
        "diff_line_count": len(diff_lines),
    }
    with open(f"{OUT_DIR}/phase_b_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-06][PhaseB] 完了。version2_status={version2_result.get('status')} "
          f"diff_line_count={len(diff_lines)}")
    return {"phase_a_final": phase_a_final, "version2_result": version2_result,
            "diff_lines": diff_lines, "summary": summary}


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-06 Phase C: Trial側の派生Editor(Production
# Editor本体[er003_v1_n3_01_evidence_compression_editor.py]は無変更のまま)。
# Phase A/Bの実測diff(phase_b_editor_vs_no_editor.diff)で実際に観測された
# 劣化パターンにのみ対応する、最小限の追加ルールブロックをProduction Editor
# の同じprompt template(EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE、未変更)
# の末尾(禁止事項リストの直前)へ追加する。Production側のimport・関数は
# 一切変更せず、ここではclient.responses.create()を直接呼ぶ(ec_editor.
# run_lossless_editor()と同じ呼び出し形。model・developer messageは
# Production既定のec_editor.EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE
# をそのまま再利用する)。
# ============================================================
import er003_v1_n3_01_evidence_compression_editor as ec_editor

TRIAL06_IMPROVED_EDITOR_EXTRA_BLOCK = """【追加ルール(EDITORIAL-B-FAMILY-VOICES-TRIAL-06、Trial限定の派生ルール。
Voices/Perspective型記事専用)】
この記事はVoices/Perspective型記事です(実在する人物・立場の経験を、Markdown内の
"### One Voice: ..." "### Another Voice: ..." という2つの見出しの中で描いています)。
この2つの見出しの本文に対しては、以下を追加で守ってください:
- その人物を指す代名詞(he/she/his/her等)や、その人物の行動を能動態で描いている文
  ("She described..." "He explained..."のような文)を、受動態("It was described as...")
  や、"This person"のような一般名詞へ書き換えないでください。Voicesという記事タイプでは、
  その人物が能動的に感じ・考え・語っている、という文法上の主語の位置そのものが、記事の
  中心的な意味です。
- その人物の所有格代名詞(her/his)を使って書かれている「守りたいもの・責任・悩み」の
  表現("her decision" "his concern"等)を、所有格を取り除いた抽象名詞句("the decision"
  "the concern"等)へ書き換えないでください。
- 出典名の一般化ルール(企業名・調査会社名等を"a survey"等へ一般化するルール)は、
  Voice本人の実在の氏名(記事内でその人物として発言・行動しているとして書かれている
  固有の人名)には適用しないでください。ここでいう「出典名」とは、その人物が引用した
  調査・報告の出典を指し、その人物自身の名前を指すものではありません。
上記以外の許可された編集(不要な出典名の一般化・近似数字の削減・不要な日付/地名の
一般化・spoken wordingの簡素化)は、この2つの見出しの本文以外の部分(Hook・Tension・
Closing)には引き続き適用してかまいません。"""

EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_TRIAL06 = ec_editor.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.replace(
    ec_editor._EC_FORBIDDEN_EDITS_MARKER,
    TRIAL06_IMPROVED_EDITOR_EXTRA_BLOCK + "\n\n" + ec_editor._EC_FORBIDDEN_EDITS_MARKER)


def run_improved_editor(client, article_text: str, model: str) -> dict:
    assert TRIAL06_IMPROVED_EDITOR_EXTRA_BLOCK in EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_TRIAL06, (
        "追加ブロックの挿入に失敗しています(marker不一致の可能性)。")
    prompt = EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_TRIAL06.format(article_text=article_text)
    resp = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        input=[{"role": "developer", "content": ec_editor.EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    edited_text = resp.output_text.strip()
    return {
        "prompt": prompt, "raw_text": edited_text, "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


def run_phase_c() -> dict:
    """タスク文書Phase C: PhaseA/Bの実測diffでEditorがVoices記事を劣化させて
    いると判断した場合に実施する。改善Editor案(TRIAL06_IMPROVED_EDITOR_EXTRA_
    BLOCK、Production Editor本体は無変更)をpre_editor_article.mdへ適用し、
    その結果にPhase Bと同じFact Safety/QA/Analytical Leakage Checkを適用する。"""
    phase_a_final = _load_phase_a_final()
    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial06_phase_c.jsonl")
    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)

    version3_dir = f"{OUT_DIR}/phase_c_improved_editor"
    os.makedirs(f"{version3_dir}/audit", exist_ok=True)
    print(f"[TRIAL-06][PhaseC] 改善Editor案(Trial限定派生ブロック)をpre_editor_article.mdへ適用...")
    editor_result = run_improved_editor(client, phase_a_final["pre_editor_text"], writer_model)
    with open(f"{version3_dir}/audit/improved_editor_raw.json", "w", encoding="utf-8") as f:
        json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
    improved_text = gen.normalize_article_formatting(editor_result["raw_text"])

    print(f"[TRIAL-06][PhaseC] 改善Editor案適用後のテキストへFact Safety/QAを適用...")
    version3_result = run_fact_safety_and_qa_from_text(
        client, THEME_ID, LABEL, improved_text, phase_a_final["verified_ledger_text"], TOPIC_JA, version3_dir)

    diff_vs_editor = _unified_word_diff(
        "editor_version(article.md)", phase_a_final["editor_article_text"],
        "improved_editor_version", improved_text)
    diff_vs_no_editor = _unified_word_diff(
        "no_editor_version(pre_editor_article.md)", phase_a_final["pre_editor_text"],
        "improved_editor_version", improved_text)
    with open(f"{OUT_DIR}/phase_c_improved_vs_editor.diff", "w", encoding="utf-8") as f:
        f.write("\n".join(diff_vs_editor))
    with open(f"{OUT_DIR}/phase_c_improved_vs_no_editor.diff", "w", encoding="utf-8") as f:
        f.write("\n".join(diff_vs_no_editor))

    summary = {
        "phase_a_final_attempt_dir": phase_a_final["final_attempt_dir"],
        "version3_improved_editor": {k: v for k, v in version3_result.items()
                                      if k not in ("article_text", "five_voice_sections")},
        "diff_vs_editor_line_count": len(diff_vs_editor),
        "diff_vs_no_editor_line_count": len(diff_vs_no_editor),
    }
    with open(f"{OUT_DIR}/phase_c_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-06][PhaseC] 完了。version3_status={version3_result.get('status')}")
    return {"phase_a_final": phase_a_final, "version3_result": version3_result, "summary": summary}


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "research":
        run_research_stage()
    elif stage == "write" or stage == "phase_a":
        run_writer_stage()
    elif stage == "phase_b":
        run_phase_b()
    elif stage == "phase_c":
        run_phase_c()
    else:
        run_research_stage()
        run_writer_stage()


if __name__ == "__main__":
    main()
