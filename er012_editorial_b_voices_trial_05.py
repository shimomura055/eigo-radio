# ============================================================
# er012_editorial_b_voices_trial_05.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-05-PERSPECTIVE-CONTRACT-01
# ============================================================
# Lane: Lane B / Voices-Perspective(新管理ID)。Lane A(OPEN-112/OPEN-117/
# ER-011系、docs/pm/*、er011_*、er006_*、er003_*Production等)とは完全に
# 独立。本ファイルはer012_editorial_b_voices_trial_04.pyを土台にコピーし、
# Trial-04本体は一切変更していない。
#
# 目的: EDITORIAL-B-FAMILY-VOICES-TRIAL-04(往復3回=run01〜run04、Focus
# Module Blockへの追加指示による反復修正)に対するユーザー評価は、5区切り
# 構造(Hook/One Voice/Another Voice/Tension/Closing)自体は強い方向性
# (VALIDATED候補)だが、Voice section内に依然としてDiscovery/分析型の
# 記述("At the same time, about 37% of free-address workers in a survey
# said...")が残っており、原因は文章修正レベルの追加指示ではなく、Writerが
# 「調査結果を整理・説明するWriter」として動作する構造そのものにある、と
# いうものだった。そのためTrial-05では、Focus Module Blockへの注意書き
# 追加という同じアプローチを繰り返すのではなく、**生成方式そのもの**を
# 再設計する: Research → Perspective Map(想像で埋めない、根拠なしは空欄)
# → Voice Cards(Person/Situation/Need/Concern/Protect/Constraint/Concrete
# scene主体、Supporting evidenceは別枠に隔離)→ Perspective Diversity
# Check(「単なる好みの違いA/B」でないかの判定)→ Voices Writer(Voice
# Cardを主役としてWriterへ渡す)→ Analytical Leakage Check(Writer後、
# 検出時はWriter再実行、手でのarticle編集はしない)。
#
# Research: 新規Perplexity呼び出しは行わない。EDITORIAL-B-FAMILY-VOICES-
# TRIAL-04のStage 1B/2B追加Research(er012_output/editorial_b_voices_
# trial_04/research/raw_facts_research_stakeholder.json、raw_facts_
# verification_stakeholder.json、facts_research_stakeholder_readable.txt
# 等、無変更のTrial-04資産)を再利用する。Trial-04のperspective_
# candidates.jsonで整理された候補(candidate_A〜E)を土台に、Perspective
# Mapを本Trialの様式(Who/Situation/Protect/Difficulty/Notice/
# Responsibility/Concrete scene/Research evidence)へ作り直し、Perspective
# Diversity Checkを実施したうえで採用2件を選定する(詳細はReport §3-4)。
#
# Ledger→Writer: Production Writer本体(er003_v1_n3_01_articles_generate.py
# のCOMMON_BLOCK_TEMPLATE/run_one_pattern等)は一切変更しない。5区切り
# 骨格(Trial-04 run03/run04で確立済み、###×2[Voice A/Voice B]+##×3
# [Hook/Tension/Closing])は維持しつつ、Focus Module Block自体は全面的に
# 書き直し、Voice Card(人物本体)を、Evidence(裏付け)より前・より詳しく
# 明示的に提示する構成にする(挿入位置はTrial-04と同じANCHOR挿入方式。
# COMMON_BLOCK_TEMPLATE内で{verified_ledger_text}はANCHORより後に置かれて
# いるため、ANCHOR位置へVoice Cardを挿入するだけで、Writerが読む順序として
# 「Voice Card→(Ledger本体)」を実現できる。挿入位置の変更・Production側
# の並び替えは行っていない)。
#
# Point Overlap QA / Point Value QA: Trial-04と同じくユーザー決定により
# monitoring専用(gateにしない、retryを誘発しない)。run_voices_pattern_
# run03()・split_five_voice_sections()・run_five_section_point_qa_
# monitoring()はTrial-04から関数名も含め無変更のまま再利用する(呼び出す
# 関数・引数・順序は完全に同一)。Fact Checker/Ledger Deviation Checker
# (+Local Rewrite)/Directional Fact Precheckのロジック自体もTrial-04から
# 一切変更しない。
#
# Analytical Leakage Check(本Trialの新規追加部分): Writer生成後、
# split_five_voice_sections()で抽出したVoice A/Voice B本文に対し、
# タスク文書§Jの6基準(survey/research/data主語・数字前面化・Narrator
# 分析・当事者が知り得ない分析・Discovery型構文・Evidence>人)をLLM
# judgeで判定する(Trial限定の新規関数run_analytical_leakage_check()、
# Production側コードは一切変更しない、client.responses.create()を
# 直接呼ぶ既存パターン[er011_point_role_value_planning_01.run_point_
# value_qa()と同じjson_schema/reasoning_effort/response.model一致検証
# パターン]を踏襲)。flaggedの場合、記事本文を手で書き換えるのではなく、
# 具体的な引用付きの是正メモをprompt末尾へ追加してWriterを再実行する
# (run_trial05_pipeline()、最大2回まで=合計最大3 Writer attempts、
# 各attemptはFact Checker/Ledger Deviation Checker等を含むフルパイプ
# ラインとして実行し、結果をattempt_history.jsonとして全て記録する)。
#
# 禁止: Production Prompt/code変更、B Family骨格の正式採用、Voice数3以上
# への拡張、Point Overlap/Value QA閾値変更、「品質が良くなるまで」の
# 無制限再生成(Writer再実行は最大2回=合計3 attemptsまで)、Case Story
# 設計、A Family 4層構造の正式化、テーマ自体の変更(固定席/free-address、
# POOL_TOPIC_MASTER.md No.7のまま)、A2/TTS/Assembly/11-part対応、3+
# Voices、Master記事正式採用、Git操作(Report内で指示された3ファイルのみを
# 本ファイル完成後に別途Bashでcommit)。
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

THEME_ID = "editorial_b_voices_trial_05_assigned_desks"
OUT_DIR = f"er012_output/editorial_b_voices_trial_05"
RESEARCH_DIR = f"{OUT_DIR}/research"
os.makedirs(RESEARCH_DIR, exist_ok=True)

# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: テーマ・TOPIC_JA自体はTrial-04から
# 変更しない(タスク指定「固定席テーマ」、POOL_TOPIC_MASTER.md No.7)。
# Trial-04と同じく、どの2つの立場を対比させるかをここで先に固定せず、
# 実際にどのstakeholder perspectiveを描くかはPerspective Map・Diversity
# Check(下記、research/perspective_map.md参照)に委ねる。
TOPIC_JA = (
    "2026年9月時点、オフィスの座席運用が変わりつつある。パンデミック下で広がった"
    "フリーアドレス制(ホットデスキング、社員が毎日座席を選ぶ方式)をやめ、社員一人"
    "ひとりに専用の「固定席」を再び割り当てる動きが一部の企業で見られる一方、"
    "デスク共有(ホットデスキング)を維持・拡大する企業も依然として多い。この記事の"
    "中心テーマは、『固定席派 vs フリーアドレス派』のどちらが正しいかを決めることでは"
    "なく、この同じ状況を実際に生きている複数の当事者(例えば、日々オフィスで働く人、"
    "チームや職場の運営に責任を持つ人など)が、それぞれ何を経験し、何を大切にし、"
    "何を心配し、何に責任を持っているのかを、実在する発言・調査・事例に基づいて"
    "具体的に描き、そのうえで、なぜ同じ状況が立場によって違って見えるのかを理解する"
    "ことである。"
)

LABEL = "B1B"
# EDITORIAL-B-FAMILY-VOICES-TRIAL-05: run_trial05_pipeline()がAnalytical
# Leakage Check flaggedの場合に内部でWriterを最大2回再実行する(合計最大
# 3 attempts)。各attemptの出力はb1b_run01_attempt1/・b1b_run01_attempt2/
# ...のようにattempt番号付きの別ディレクトリへ保存し、上書きしない
# (RUN_ID自体は固定、attempt番号はpipeline内部で管理する)。
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
    print("[TRIAL-05][Research] EDITORIAL-B-FAMILY-VOICES-TRIAL-05は新規Perplexity"
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

B_FAMILY_VOICES_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(EDITORIAL-B-FAMILY-VOICES-TRIAL-05-PERSPECTIVE-CONTRACT-01、2026-09-06。Production未採用。この記事タイプ専用の骨格再定義)】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。以下は、上記の
一般的な役割定義・見出し構成を置き換えるのではなく、この記事に限り、それぞれのslotが何を
担い、どのMarkdown見出しで書くかを、より具体的に上書きする指示です。今回の記事では、以下の
役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(5区切り構造)】
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

【中心原則: Research is backstage. People are on stage.(EDITORIAL-B-FAMILY-VOICES-TRIAL-05の
新原則)】
この記事の最大の失敗パターンは、Voiceのセクションが「調査結果を整理・説明する文章」に
なってしまうことです。これは個々の文をNGワードに置き換えるだけでは直らないため、今回は
書き始める前の材料の与え方そのものを変えます。あなたには、これから2枚のVoice Card(下記)を
渡します。Voice Cardは、Researchで確認された実在の人物・立場について、その人が何を経験し・
何を必要とし・何を心配し・何を守ろうとし・どんな制約や責任を負っているかを、既にこちらで
整理したものです。**Voiceのセクションを書くときは、必ずVoice Cardの内容(その人の状況・
必要・心配・守りたいもの・責任・具体的な場面)を主たる材料にして書き始めてください。
Voice Cardの後に置かれているVerified Fact Ledger(出典・数字を含む詳しいFact集)は、
Fact Checker・Ledger Deviation Checkのための正式な事実源であり続けますが、Voiceの文章を
組み立てる際の「主役」ではありません。** Ledgerは、Voice Cardに書かれている人物像が
実在することを裏側で支える裏付けとして、必要な範囲でさりげなく使ってください。Evidence
(調査・出典・統計)がVoiceの文章の主語になったり、Voiceの内容の中心になったりしては
いけません。

【Voice Card 1(1つ目のVoiceの主材料。この内容から書き始めてください)】
- Person: 週の大半をオフィスで働く社員。以前は「自分の席」があったが、今は毎回別の席を
  探す働き方(ホットデスキング)に置かれている。
- Situation(状況): 毎朝オフィスに来て、まだ誰にも使われていない空いている机を探す。
  昨日誰が座っていたかも分からない机に座ることもある。
- Need(必要としていること): 探さずに座れる、決まった居場所。資料や私物を置いておける
  場所。毎日同じような環境で仕事を始められる予測可能性。
- Concern(心配していること): 他人が使った後の机やキーボードに座ることへの衛生面の不安、
  私物を置く場所がないことへのストレス、職場に「自分の居場所」が無いという感覚。
- What they protect(守りたいもの): 職場での所属感と、集中して働ける感覚。
- Constraint/Responsibility(制約・責任): 座席運用の決定権は無く、その日その日、与えられた
  環境の中で働くしかない立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 毎朝オフィスに着いて、空いている
  机を探して座る。resource: [A-02/fact_003](衛生面の懸念・パーソナルスペース喪失への反発)、
  [A-05/fact_007](日本のフリーアドレス職場のパート社員が「自分の席がないので落ち着かない」
  「資料や私物を置く場所に困る」と語った実例)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): Gensler調査(固定席ありの
  従業員は所属感87%・固定席なし74%、集中80%・67%)[A-01/fact_001]、Forbes調査で固定席の
  ない職場を「非人間的」「方向感覚を失う」「精神的に疲れる」と表現[A-03/fact_004]、
  ワークプレイス心理学者Oselandのコメント[A-04/fact_006]、ITmedia調査でフリーアドレス
  勤務者の36.8%が「席が固定化しがち」と回答[A-06/fact_009]。この裏付けの中から、1つの
  Voiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください
  (詳細ルールは下記【Voice内の数字】参照)。

【Voice Card 2(2つ目のVoiceの主材料。この内容から書き始めてください)】
- Person: 会社全体のオフィス空間の使い方・座席運用を決める職務を持つ、ワークプレイス戦略
  責任者(実在の発言例: Scotiabank Global Head of Real Estate & Corporate Services、
  Linda Foggie氏)。
- Situation(状況): ハイブリッド勤務が広がった結果、フロアの席の多くが日によっては空いた
  ままになっている。それでも、出社する社員は職場に自分の居場所を感じたいと望んでいる。
- Need(必要としていること): 使われない席にかかり続けるコストと、社員が感じる所属感・
  チームとしての一体感との、両方を同時に成り立たせる座席運用。
- Concern(心配していること): フレックス席を広げすぎれば社員の所属感・チームの一体感が
  静かに損なわれていく。固定席を戻しすぎればコストが膨らむ。どちらへ寄せすぎても、
  誰かから責任を問われる立場にある。
- What they protect(守りたいもの): 会社全体としてのオフィスの持続可能性(コスト)と、
  そこで働く一人ひとりの所属感の両立。個人の好みではなく、組織全体の均衡。
- Constraint/Responsibility(制約・責任): 経営層に対してスペースコストの説明責任を負う。
  一人の社員の希望だけでなく、出社頻度も働き方も異なる全社員のニーズに応える座席運用を
  設計しなければならない。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 「静かに、固定席が増えフレックス
  席が減る方向へのシフトが起きている」という発言に象徴されるように、フレックス席中心の
  運用を見直し、少しずつ固定席を増やす方向へ舵を切りつつある。resource:
  [fact_005](Linda Foggie氏の発言、CONFIRMED)、[fact_011](ワークプレイス担当者が
  「多くの席が空いている」現実に直面している記述)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): CBREベンチマークで固定席
  運用企業の割合が83%から55%へ低下(2024年)[fact_011]、Desking.appのコンサルタントに
  よる「チームごとの半固定席」という中間解の提案[fact_010]。この裏付けの中から、1つの
  Voiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください
  (詳細ルールは下記【Voice内の数字】参照)。

【この2つのVoiceがなぜ「単なる好みの違い」ではないか(重要、Perspective Diversity Check
の結果)】
Voice Card 1とVoice Card 2は、どちらも「固定席が好き/フリーアドレスが好き」という対称的な
好みの対立ではありません。Voice Card 1は、その日その日を生きる一人の社員が、自分の毎日の
感覚(所属感・集中・落ち着き)として経験していることです。Voice Card 2は、個人の好みでは
なく、コストの説明責任と、全社員の異なるニーズに応える責任を負う立場から見えていることです。
この記事のTensionは、「どちらが正しいか」ではなく、**なぜ「良い座席運用とは何か」という
問い自体が、それぞれの立場によって測る対象が違うのか**(個人が毎日感じる所属感・集中か、
組織として持続可能かどうか)を掘り下げてください。Voice Card 2の人物を、単なる「経営側の
意見」「もう一人の従業員の意見」として書かないでください。この人物の責任・立場の重さを、
Voice本文の中で(数字の紹介としてではなく、その人の悩み・判断としてさりげなく)感じさせて
ください。

【Voiceの書き始め方(重要)】
Voiceの本文は、"For [a/an] worker who..."のような、その人物のことを外側から要約・紹介する
文で始めないでください。これはVoiceを「説明されている対象」にしてしまい、当事者の視点
そのものとして立ち上がることを妨げます。代わりに、Voice Cardが示す具体的な状況(その人が
実際に毎日していること・直面していること・使っているもの、目にする光景)から書き始め、
そこからその人の感覚・必要性が自然に浮かび上がるようにしてください。目標は、読み手が
「この立場なら、たしかにそう感じるだろうな」と、外から説明されるのではなく内側から実感
できることです。反論のための藁人形にしないでください。

【Evidenceは脇役であること(重要)】
1つのVoiceの中で、Evidenceの紹介そのものが主役になる文を連続させないでください。その人の
経験・価値観・必要性・責任の描写を主体にし、Evidence(Voice Cardの「Supporting evidence」
欄、およびVerified Fact Ledger)はその描写を裏から支えるためだけに、さりげなく織り込んで
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
ません。責任(responsibility)・動機(incentive)・生きられた経験(lived experience)・
制約(constraint)・価値観(value)・優先順位(priority)のうち、根本的な部分で異なって
いる必要があります(上記【この2つのVoiceがなぜ「単なる好みの違い」ではないか】参照)。

【Voice内に第三者の視点・解決策を混ぜないこと(重要)】
各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを描き切ってください。
解決策・妥協案・提案は、この記事では基本的に書かないでください(Solution articleでは
ありません)。Voice Card 2の人物自身が座席運用の意思決定に関わる立場であっても、Voice本文
の中で「こうすればよい」という具体的な解決策の提案(例: 半固定席・ゾーン制の提案)を
書かないでください。その人が抱える悩み・責任の重さを描くにとどめてください。

【Tensionの役割("## Why They See It Differently"相当)】
「どちらのデータが正しいか」を決めようとしないでください。そうではなく、なぜ両方の
Voiceが、それぞれの立場からは合理的に見えるのかを掘り下げてください。具体的には: なぜ
両方とも理にかなって聞こえるのか / それぞれがどんな前提の違いに立っているのか / それぞれ
が何を優先しているのか / それぞれが(もし何かを測っているとすれば)何を測っているのか /
それぞれの責任範囲がどう違うのか、といった問いを言語化してください。この段落では2つの
Voiceそれぞれが使った事実を横断的に参照してもかまいませんが、Verified Fact Ledgerに無い
新しい因果関係・新しい事実を作り出さないでください。単に「両方とも一理ある」とまとめる
だけの記述にしないでください。解決策の提案はここでも基本的に行わないでください。

【Closingの役割("## What This Tells Us"相当)】
これは要約でも、In One Lineの言い換えでもありません。2つのVoiceを両方見たことによって、
この問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを書いてください。
「どちらが正しいか」を決めず、「この2つのVoiceを知る前と後で、この問題をどう考えるべきか
がどう変わるか」という一段深い理解へ着地してください。内容はVerified Fact Ledgerが示す
複数のVoiceの構造的な違い(経験・価値観・必要・心配・責任・得失の違い)の範囲内にとどめ、
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
- Voiceのセクションへ第三者(設計者・コンサルタント)の視点を持ち込むこと、または
  Voice Card 2の人物自身であっても具体的な解決策・妥協案をVoice本文内で提案すること
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
    print(f"[TRIAL-05][Phase A] clean_single_insert_confirmed={clean_single_insert}")
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
    print(f"[TRIAL-05][run03] Point Overlap/Value QA monitoring(5区切り専用) "
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
    print(f"[TRIAL-05][{theme_id}] {label}: Point Overlap/Value QA(monitoring専用、5区切り版)開始...")
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
        print(f"[TRIAL-05][{theme_id}] {label}: 5区切り構造が検出できずQA monitoring不能として記録しました。")
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
    print(f"[TRIAL-05][{theme_id}] {label}: metrics={metrics} five_section_report={five_section_report}")

    print(f"[TRIAL-05][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[TRIAL-05][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
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
        print(f"[TRIAL-05][{theme_id}] {label}: fact checkerがFAILと判定しました。自動続行せず"
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

    print(f"[TRIAL-05][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[TRIAL-05][{theme_id}] {label}: deviation overall_status="
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
        print(f"[TRIAL-05][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
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
            print(f"[TRIAL-05][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
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

        print(f"[TRIAL-05][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[TRIAL-05][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
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
        print(f"[TRIAL-05][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存、"
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
        print(f"[TRIAL-05][{theme_id}] {label}: 比較方向Fact事前チェック開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-05][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
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
# Writerを再実行する(run_trial05_pipeline())。
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
    print(f"[TRIAL-05][Leakage Check] attempt{attempt}: any_flagged={result['any_flagged']} "
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


def run_trial05_pipeline(client, theme_id: str, label: str, base_prompt: str, verified_ledger_text: str,
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

        print(f"[TRIAL-05] Writer attempt {attempt}/{MAX_WRITER_ATTEMPTS} 開始(out_dir={attempt_dir})...")
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
            print(f"[TRIAL-05] attempt {attempt}: status={result.get('status')}のためLeakage Check"
                  f"をスキップします。")
            break

        sections = split_five_voice_sections(result["article_text"])
        if sections is None:
            entry["leakage_check"] = {"qa_status": "SKIPPED_NO_FIVE_SECTIONS"}
            entry["any_flagged"] = None
            attempt_history.append(entry)
            final_result["five_voice_sections"] = None
            print(f"[TRIAL-05] attempt {attempt}: 5区切り構造が検出できずLeakage Checkをスキップ"
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
            print(f"[TRIAL-05] attempt {attempt}: Analytical Leakage Check flagged項目なし。確定。")
            break
        if attempt == MAX_WRITER_ATTEMPTS:
            print(f"[TRIAL-05] attempt {attempt}: 最大attempt数に到達。flagged項目が残った状態の"
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
        print("[TRIAL-05] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "pipeline": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial05_writer.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text,
        gen.B1_B_DIRECT_INSTRUCTION)
    with open(f"{OUT_DIR}/audit_candidate_prompt_base.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    print(f"[TRIAL-05] Writer + Analytical Leakage Checkパイプライン開始"
          f"(最大{MAX_WRITER_ATTEMPTS} attempts)...")
    pipeline_result = run_trial05_pipeline(
        client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, TOPIC_JA, LEVEL_OUT_DIR)

    with open(f"{OUT_DIR}/trial05_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": pipeline_result["attempt_history"],
            "total_attempts": pipeline_result["total_attempts"],
            "final_attempt_dir": pipeline_result["final_attempt_dir"],
            "final_result": {k: v for k, v in (pipeline_result["final_result"] or {}).items()
                              if k not in ("article_text", "five_voice_sections")},
        }, f, ensure_ascii=False, indent=2, default=str)

    final_result = pipeline_result["final_result"] or {}
    print(f"[TRIAL-05] 完了。total_attempts={pipeline_result['total_attempts']} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"phase_a": phase_a, "pipeline": pipeline_result, "status": "DONE"}


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "research":
        run_research_stage()
    elif stage == "write":
        run_writer_stage()
    else:
        run_research_stage()
        run_writer_stage()


if __name__ == "__main__":
    main()
