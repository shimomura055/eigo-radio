# ============================================================
# er012_editorial_b_voices_3v_person_voice_trial_02.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02
# ============================================================
# Lane: Lane B(並列稼働中: Lane A 3件[A2 B1B継続/A3 Trial-06/D2 Trial-07]、
# SSOT統合。いずれも本ファイルとは無関係)。**設計修正Trialの継続改善**
# (Production/Trial-07/registry/Contract編集禁止、SSOT・Git禁止)。
#
# 本ファイルはTrial-01(`er012_editorial_b_voices_3v_person_voice_trial_01.py`、
# 無変更)の継続。Trial-01の結果(`EDITORIAL-B-FAMILY-VOICES-3V-PERSON-
# VOICE-TRIAL-01_REPORT.md`)は仮説(抽象軸がLeakageの原因)を支持したが
# (経営者Voiceはattempt 1・2でAnalytical Leakage flag 0)、3点が未達
# だった: (i) Tension外部制約の統合(`leak_tension_constraint_
# integration`が3/3失敗、「地域規制の列挙」に留まる)、(ii) 語数・尺超過
# (530語/約412秒、目標325〜355秒)、(iii) 人物化による相互作用効果
# (経営者Voiceが未裏付けclaimを出しやすくなり、Ledger MAJOR→Local
# Rewriteのhedgingがnarrator分析調のLeakageを再導入)。
#
# 本Trialの改善は、いずれもFableが「承認済み設計・原則の適用」と判定した
# 範囲(新原則の追加ではない)。詳細はTrial-01・Trial-02それぞれのReport
# 冒頭Reconciliation節を参照:
# 1. Tension: design.md B-7の3V Tension設計「共通前提→分岐点→非対称性」
#    3段構造+外部制約(fairness/bias/accountability/law/compliance)を
#    「3者の合理性の足し算では答えにならないことを示す材料」として統合する
#    (ユーザー決定2026-09-09、DECISION_LOG.md PM-CLOSEOUT-CONSOLIDATION-37
#    (2)の文言)という、Trial-01でも既に採用していた原則を、語り口指示
#    ではなく検証可能な構造(自己チェック付き)としてFocus Module内へ
#    明示し直したもの。Closingは「問いの再構成」(Trial-01から継続、
#    変更なし)。
# 2. 語数: design.md B-6の3V目標尺(325〜355秒、承認済みmonitoring値)から、
#    2V実測(Trial-09実測301.795〜305.135秒、区分別表)の語数/秒比を
#    用いて逆算した合計約410〜450語(Trial-01のsoft target約330語は
#    この逆算より小さく、超過の一因だったと考えられる)。Hook/Voice×3/
#    Tension/Closingの配分は、design.md B-6の3V区分別目安表(秒単位の
#    配分比率)をそのまま語数へ比例配分したもの(新しい上限仕様の追加では
#    なく、承認済み目標尺の適用)。
# 3. 体験claimの根拠付け: 承認済みFact Safety(Verified Fact Ledger)・
#    「Research is backstage. People are on stage.」原則の適用として、
#    「Voice本人の体験として語る箇所で数値・制度・他者の行動を事実として
#    述べる場合はLedger evidenceに限る。evidenceが無い事柄は体験・感情・
#    判断として語る(事実主張にしない)」をFocus Moduleへ明示した。Local
#    Rewriteのhedging表現("The cited analysis suggests…")がnarrator調に
#    なる問題自体は既存機構の挙動のため変更しない(hedging表現の変更は
#    仕様変更であり、本Trialのスコープ外。上流でLedger MAJORを減らす
#    ことで回避を狙う、間接的な対策)。
#
# 3 Voices(Trial-01と同一、変更なし): (1) Voice 1=仕事に応募する一人の人
# (Applicant、Algieba)/ (2) Voice 2=採用担当者/Hiring Manager(Erinome)/
# (3) Voice 3=経営者(採用コスト・速度・会社運営・結果に実際に責任を持つ
# 人物、Business/Efficiencyという抽象軸ではない、Schedar)。Fairness/
# Legal/HR Governance(旧4V Voice 4)はVoiceから外し、Tension/Closing側の
# 統合・制約材料とする(3人物版perspective_map: Trial-01成果物`er012_
# output/editorial_b_voices_3v_person_voice_trial_01/research/
# perspective_map_3v.md`をそのまま再利用、読み取り専用、本Trialでは
# Voice Card自体は再設計しない)。テキストのみのため音声は生成しない。
#
# 本ファイルの土台: `er012_editorial_b_voices_3v_person_voice_trial_01.py`
# (Trial-01、無変更)の経路(Ledger再割当・6区切りparser・QAスキーマ・
# Leakage feedback loop・Fact A'呼び出しチェーン・Ledger Deviation+Local
# Rewrite・Diagnostic Full Retry・Editor)をそのまま複製し、Focus Module
# Block内の上記1〜3のみを変更したもの。Trial-01ファイル自体は一切変更
# していない。命名: 見出し構造(split関数の内部キー・required_structure
# segment名)は`point_one/point_two/point_three`(Production 2V正式命名
# `point_one`/`point_two`[registry.py B_FAMILY_B1_REQUIRED_SEGMENTS]を
# point_threeへ1つだけ拡張したもので、4Vが選んだ`voice_1..4`命名とは
# 異なる設計選択。この命名自体が本Trialの評価対象[未承認候補、Gate 1 §7
# 参照]）。QAスキーマ(Analytical Leakage Check・Pairwise Distinctness
# Check)は4V踏襲でvoice_1/voice_2/voice_3キーを使う(物理構造キーとQA
# スキーマキーをあえて分離し、両命名方式を同時に記録する)。
#
# Ledger: `er012_output/ai_screening_ledger_trial_01/research/
# verified_fact_ledger.txt`(4V Trial-01/02・3V Trial-01と同一、再利用。
# 新規Research呼び出しなし、Ledger本文は一切改変しない)。
# `perspective_map.md`(4V版、既存)は読み取り専用で参照するのみ。3人物版
# `perspective_map_3v.md`はTrial-01成果物を読み取り専用で参照する
# (本Trialでは新規作成しない、Voice Card自体は変更していないため)。
#
# Fact Checker A'(opt-in、OPEN-131): Trial-01と同じ呼び出しチェーン
# (`registry.build_voice_attribution_block()`→`b1prod.run_fact_checker()`
# [内部で`r3.build_fact_check_prompt()`]、Production関数はいずれも無変更)
# を踏襲するが、voice_attribution_blockの入力を、Trial側で`[VOICE_4_
# EVIDENCE]`ブロックを除去したledger断片へ限定する(理由:
# perspective_map_3v.md §4参照。Voice本文としてVoice 4を使わないため、
# Voice帰属opt-in免除の対象をVoice 1〜3のみに限定し、TensionでVoice 4由来
# の事実[NYC LL144等]を扱う場合は通常どおり出典的整合性を問う)。Ledger
# Deviation Checkerには全文(Voice 4含む、無改変)を渡す(Tensionの制約
# Evidenceの正確性を検証するため)。
#
# 禁止: 音声生成、Production/Trial-07/registry/Contract編集、Ledger本文
# 改変、SSOT・Git操作、閾値変更、hedging表現の変更、バックグラウンド待機、
# 完了報告後の自動復帰。
#
# STOP条件: 新規failure mode/費用上限(¥150)/見出し数6が成立しない状態が
# retry上限まで継続/Production・Trial-07・registry書込みが必要/賛否
# 構図化/上記1〜3の適用で解消せず新原則が必要と判断される(記載のみ、
# 実装はしない)。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import itertools
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er005_cost_logger as cl
import er008_shared_point_blueprint_01 as blueprint_mod
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er010_ledger_local_rewrite_09 as local_rewrite
import er012_b_family_editorial_type_registry_01 as registry  # Production, 読み取り専用import
import er012_b_family_voices_production_01 as b1prod  # Production, 読み取り専用import

THEME_ID = "editorial_b_voices_3v_person_voice_trial_02"
OUT_DIR = "er012_output/editorial_b_voices_3v_person_voice_trial_02"
os.makedirs(OUT_DIR, exist_ok=True)

# 4V Trial-01(EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01)の
# 既存成果物を読み取り専用で参照する(このファイルは複製・上書きしない)。
LEDGER_SOURCE_DIR = "er012_output/ai_screening_ledger_trial_01/research"
LEDGER_PATH = f"{LEDGER_SOURCE_DIR}/verified_fact_ledger.txt"
PERSPECTIVE_MAP_4V_PATH = f"{LEDGER_SOURCE_DIR}/perspective_map.md"  # 参照のみ
# 3人物版perspective_mapはTrial-01成果物を読み取り専用で再利用する(本Trialでは
# Voice Card自体を変更しないため新規作成しない)。
PERSPECTIVE_MAP_3V_PATH = (
    "er012_output/editorial_b_voices_3v_person_voice_trial_01/research/perspective_map_3v.md")

TOPIC_EN = "Should companies use AI to screen job applicants?"

# テーマ説明(TOPIC_JA相当)。3 Voices(Applicant/Recruiter・HM/Business
# Owner)+Tensionでの外部制約(fairness/legal/accountability)統合、という
# 本Trialの構成をWriterへ伝える。Ledger・perspective_map_3v.mdの内容の
# みに基づき新規に執筆した(新しい主張・数字は追加していない)。
TOPIC_JA = (
    "2026年9月時点、多くの企業が採用選考の一部にAI(応募書類の自動スクリーニング、"
    "適性・性格の自動スコアリング、動画面接での表情・話し方の自動評価など)を"
    "取り入れつつある。この記事の中心テーマは、『企業は採用選考にAIを使うべきか』"
    "の賛否をどちらか一つに決めることではなく、この同じ状況について、全く異なる"
    "利害・責任・経験を持つ3人—実際にAIによって評価される応募者(Applicant)、"
    "実際にAIツールを業務で使う採用担当・人事責任者(Recruiter・Hiring Manager)、"
    "そして採用にかかるコスト・速度・会社の存続そのものに個人として責任を負う"
    "経営者(Business Owner)—が、それぞれ何を経験し、何を大切にし、何を心配し、"
    "何を守ろうとしているのかを、実在する調査・訴訟・事例に基づいて具体的に描く"
    "ことである。そのうえで、この3人の合理性を単純に足しても答えにはならない"
    "ことも示す。3人の外側には、応募者が不当に差別されていないかを監査・法規制"
    "を通じて事後に検証する仕組み(バイアス監査義務・AIの高リスク分類・過去の"
    "訴訟事例など)が既に存在しており、これが3人それぞれの選択肢を現実に制約"
    "している。この記事のねらいは、なぜ同じ状況が、それぞれが背負っているものに"
    "よって全く違う重みで見えるのか、そしてなぜ3人の言い分をただ足し合わせるだけ"
    "では答えが出ないのかを理解することである。"
)

LABEL = "B1B"
RUN_ID = "run01"
LEVEL_OUT_DIR = f"{OUT_DIR}/{LABEL.lower()}_{RUN_ID}"

# ============================================================
# Voice assignment(ユーザー決定2026-09-09。2V[Algieba/Erinome/Aoede]は
# 不変、Schedarは4V Trial-01/02同様、承認済み候補内でのTrial限定使用)。
# ============================================================
VOICE_STAKEHOLDER_LABEL = {
    "voice_1": "Applicant",
    "voice_2": "Recruiter/Hiring Manager",
    "voice_3": "Business Owner",
}
VOICE_TTS_NAME_TRIAL_ONLY = {  # 参考記録のみ、本Trialは音声生成しない
    "voice_1": "Algieba", "voice_2": "Erinome", "voice_3": "Schedar",
}

# ============================================================
# Fact Attribution Mode(OPEN-131)opt-in判定: Trial側editorial_type相当
# 辞書。Production registryのEDITORIAL_TYPESへは一切追加しない。
# ============================================================
TRIAL_EDITORIAL_TYPE_3V = {
    "family": "B",
    "fact_attribution_mode": True,  # Trial側でopt-in ONを強制(Production既定Falseは無変更)
}


def is_fact_attribution_mode_enabled_trial(et: dict) -> bool:
    """registry.is_fact_attribution_mode_enabled()と同一の判定ロジックを
    Trial側editorial_type辞書に対して複製したもの(Production関数は
    変更しない)。"""
    return et.get("family") == "B" and bool(et.get("fact_attribution_mode"))


_VOICE4_EVIDENCE_TAG_RE = re.compile(r"^\[VOICE_4_EVIDENCE\]")


def build_ledger_fragment_voices_1_2_3_only(ledger_text: str) -> str:
    """Fact Checker A'のvoice_attribution_block生成専用に、`[VOICE_4_
    EVIDENCE]`のevidenceブロックのみをテキストから除去したledger断片を
    作る(Ledger本体ファイルは一切書き換えない。戻り値は`registry.build_
    voice_attribution_block()`[Production、無変更]への入力としてのみ使う
    一時的な文字列)。ブロック境界の判定は、同関数内のブロック抽出ロジック
    (空行/`[`で始まる行/`===`で始まる行の直前まで)と同じ規約に合わせる
    (perspective_map_3v.md §4参照、本Trialは旧Voice 4をVoiceとして使わない
    ため、Voice帰属opt-in免除の対象をVoice 1〜3のみへ限定する)。"""
    lines = ledger_text.splitlines()
    out_lines = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if _VOICE4_EVIDENCE_TAG_RE.match(stripped):
            skipping = True
            continue
        if skipping:
            if stripped == "" or stripped.startswith("[") or stripped.startswith("==="):
                skipping = False
            else:
                continue
        out_lines.append(line)
    return "\n".join(out_lines)


def run_fact_check_a_prime_3v(article_text: str, ledger_text: str, out_dir: str) -> dict:
    """Fact Checker A'(opt-in)をProduction関数経由(`registry.build_voice_
    attribution_block()`→`b1prod.run_fact_checker()`[内部で`r3.build_
    fact_check_prompt()`を呼ぶ]）で実行する(4V Trial-02と同一の呼び出し
    チェーン、Production関数自体は無変更)。本Trial固有の差分: voice_
    attribution_blockの入力ledger_textを、Trial側で`[VOICE_4_EVIDENCE]`
    ブロックを除去した断片(`build_ledger_fragment_voices_1_2_3_only()`)へ
    限定する(4V Trial-02は全4 Voice分のledgerをそのまま渡していたが、
    本Trialは3 Voiceのみが本文に存在するため)。"""
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    enabled = is_fact_attribution_mode_enabled_trial(TRIAL_EDITORIAL_TYPE_3V)
    ledger_fragment_for_attribution = build_ledger_fragment_voices_1_2_3_only(ledger_text)
    with open(f"{out_dir}/audit/ledger_fragment_voices_1_2_3_only.txt", "w", encoding="utf-8") as f:
        f.write(ledger_fragment_for_attribution)
    block = registry.build_voice_attribution_block(ledger_fragment_for_attribution) if enabled else ""
    with open(f"{out_dir}/audit/voice_attribution_block_used.txt", "w", encoding="utf-8") as f:
        f.write(block if block else "(fact_attribution_mode_enabled=False、blockは空文字列)")
    fc_prompt_for_evidence = r3.build_fact_check_prompt(TOPIC_JA, article_text, [], voice_attribution_block=block)
    with open(f"{out_dir}/audit/fact_check_prompt_with_attribution.txt", "w", encoding="utf-8") as f:
        f.write(fc_prompt_for_evidence)

    print(f"[3V-PERSON-VOICE-TRIAL-02] Fact Checker A'呼び出し開始(fact_attribution_mode_enabled={enabled})...")
    fc_record = b1prod.run_fact_checker(TOPIC_JA, article_text, voice_attribution_block=block)
    fc_record["fact_attribution_mode_enabled"] = enabled
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fc_record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02] Fact Checker A'完了。final_status={fc_record.get('final_status')} "
          f"verdict={(fc_record.get('result') or {}).get('verdict')}")
    return fc_record


# ============================================================
# B Family Common Skeleton(Layer2)+ Voices Focus Module(Layer3)、
# ANCHOR挿入方式(4V Trial-02と同じ手法、Production側template自体は
# 変更しない)。
# ============================================================
ANCHOR = "【Spoken-first原則(数字の扱い)】"

B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(3 Voices・Person-Voice版、EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02。
Production未採用、この記事タイプ専用の骨格再定義。Trial-01(3人目のVoice[経営者]を「具体的人物」として再設計したもの)を土台に、
Tension外部制約統合・語数配分・体験claimの根拠付けの3点のみを改善した版。人称指示・Evidence脇役原則等はTrial-01から変更していない）】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。今回は**3人**の
立場を並立させます。以下は、上記の一般的な役割定義・見出し構成を置き換えるのではなく、この
記事に限り、それぞれのslotが何を担い、どのMarkdown見出しで書くかを、より具体的に上書きする
指示です。今回の記事では、以下の役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(6区切り構造、厳守)】
上記「記事構成」節にある「Markdownの###見出しをちょうど2つ置く」という指示は、この記事
では次のように解釈してください: ###(レベル3見出し)は必ずちょうど**3つ**だけ使い、それぞれ
1人目・2人目・3人目のVoiceの見出しとしてのみ使ってください。それに加えて、##(レベル2
見出し)を3つ使い、Hook・Tension・Closingの見出しとしてください。記事全体は、必ず次の**6つ**
のMarkdown区切りを、この順序で持ってください(見出し文言は下の例を基本としつつ、内容に応じて
自然に言い換えてかまいませんが、3つのVoice見出しには、「ここから別のVoiceが始まる」と聞き手に
伝わる表現("Voice One:" "Another Voice:" "A Third Voice:"のような形、またはその人物が何者かを
示す語[the applicant/the recruiter/the business owner]を使った自然な表現)を必ず含めて
ください。"Voice 1"/"Voice A"のような固定ラベル・番号ラベル、賛成/反対のような対称的なラベルは
禁止です):

# [Title]

## The Question
[Hookの本文]

### [1人目のVoiceの見出し。その人物・立場が何者かが伝わる短いフレーズ]
[1人目のVoice(Applicant)の本文]

### [2人目のVoiceの見出し]
[2人目のVoice(Recruiter・Hiring Manager)の本文]

### [3人目のVoiceの見出し]
[3人目のVoice(Business Owner=経営者)の本文]

## [Tensionの見出し。例: "Why They See It Differently"]
[Tensionの本文]

## [Closingの見出し。例: "What This Tells Us"]
[Closingの本文]

Tensionは、3人目のVoiceの本文の続きの段落ではなく、独立した見出しを持つ独立したセクション
として書いてください。

【見出しは合計ちょうど6つ、これ以外の見出しを追加しないこと(重要、厳守)】
記事全体のMarkdown見出し(#・##・###のいずれも)は、上記の6つ(Title含めると7つ、Titleの
#は別枠)だけにしてください。以下は禁止です:
- 記事の最後に「## In one line」やそれに類する結びの見出しを追加すること(この記事タイプ
  では、6つ目の見出し["Closingの見出し"]が結びの役割を兼ねます)
- Tensionセクション・Closingセクションの中に、新しいMarkdown見出し(###や##)をさらに
  追加すること(切り口が複数ある場合も、見出しで区切らず、地の文の中でひとつづきの文章
  として書いてください)
- Voice以外の要素(まとめ・補足・解決策等)のための追加の見出しを作ること
書き終えた後、Hook相当・3つのVoice相当・Tension相当・Closing相当の見出しがちょうど6つに
なっているか、自分で数え直してから出力してください。

【中心原則: Research is backstage. People are on stage.(4V版から継続)】
この記事の最大の失敗パターンは、Voiceのセクションが「調査結果を整理・説明する文章」に
なってしまうことです。あなたには、これから3枚のVoice Card(下記)を渡します。Voice Cardは、
Researchで確認された実在の人々の立場について、その人が何を経験し・何を必要とし・何を心配し・
何を守ろうとし・どんな条件からその考えに至っているかを、既にこちらで整理したものです。
**Voiceのセクションを書くときは、必ずVoice Cardの内容(その人の状況・必要・心配・守りたい
もの・具体的な場面)を主たる材料にして書き始めてください。Voice Cardの後に置かれている
Verified Fact Ledger(出典・数字を含む詳しいFact集)は、Fact Checker・Ledger Deviation
Checkのための正式な事実源であり続けますが、Voiceの文章を組み立てる際の「主役」ではありません。**
Evidence(調査・出典・統計)がVoiceの文章の主語になったり、Voiceの内容の中心になったりしては
いけません。**3人目のVoice(経営者)についても、「効率性」という分析軸の代弁者にしないで
ください。あくまで、採用のコスト・速度・会社の存続に個人として責任を負う一人の経営者として
書いてください(下記Voice Card 3参照)。**

【この記事の3つのPerspectiveについて(重要な前提、賛否2対1を作らないこと)】
この記事の3つのVoiceは、単純な「応募者1人 vs 採用担当+経営者2人」のような対称的な陣営には
決して分解できません。3人はそれぞれ、AIによる採用選考という同じ現象に対して、全く異なる
役割・異なる利害・異なる責任の重さから、異なる経験をしています。Voice 1(Applicant)は
評価される側、Voice 2(Recruiter・Hiring Manager)は実際にツールを日々運用する現場、
Voice 3(Business Owner)は導入を判断し結果に責任を負う経営側です。Voice 2とVoice 3は
どちらもAIの効率性を実感していますが、それぞれが背負っているものは全く異なります。
Voice 2は「応募者の不信に日々応える」という実務負担を抱えており、導入するかどうかの決定権
自体は持ちません。Voice 3は導入を決める側であり、差別が公になった場合に矢面に立つのは
自分自身だという個人的な責任を負っています。この2人を単純に「会社側」として同一視しない
でください。それぞれの意見の背後にある、具体的な経験・守りたいもの・立場上の制約まで、
Voice Cardの内容を使って丁寧に描いてください。

【Voice Card 1(1人目のVoice。Applicant=AIスクリーニングを受ける応募者。この内容から
書き始めてください)】
- Person: 求職者として、企業の採用選考でAIによる評価(書類スクリーニング、適性・性格の
  自動採点、動画面接での表情・話し方の評価など)を受ける側の人。
- Situation(状況): 応募書類を送り、動画面接を受け、その評価の一部または全部をAIが行って
  いることを知っている、あるいは後から知る。
- Need(必要としていること): 自分の実力・人柄を正確に見てもらうこと、なぜ不採用になったのか
  理由を理解できること。
- Concern(心配していること): AIが人間の採用担当者より偏っている(biased)のではないかという
  広い不信感、人種・民族に基づく偏りが悪化するのではという懸念、異議を申し立てる手段が
  ないまま機械的に評価され不利益を受けるリスク。
- What they protect(守りたいもの): 公正に見てもらう機会そのもの、評価の理由を理解し
  納得できること。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、スキル評価では良い
  結果を出したにもかかわらず、AIによる動画面接評価で身振り・表情を低く採点されて不採用と
  なり、その後長期の失業状態に陥ったと証言する女性求職者の実例がある。また、ある応募者は
  AIによる「信頼性・誠実さ」スコアリングを、オプトアウトも異議申し立てもできないまま
  受けさせられたとして提訴した実例もある。
- Constraint(制約): 選考プロセスにAIが使われるかどうか、どう使われるかについて発言権を
  持たない、判断される側の立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 動画面接で、ソフトウェアが自分の
  声のトーン・表情・身振りをスコアリングしていると知りながら話す、あるいは、なぜ次の段階へ
  進めなかったのか説明のないまま結果だけを受け取る。resource: [VOICE_1_EVIDENCE 1-03]
  (BBC Worklife、動画面接評価で低評価となり長期失業に陥った女性求職者)、
  [VOICE_1_EVIDENCE 1-04](CVS Health応募者、HireVue/Affectivaの表情・声のトーン分析を
  オプトアウトも異議申し立てもできないまま受け提訴)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): 米国の就労中求職者の49%が
  AIツールは人間より偏っていると考えている[VOICE_1_EVIDENCE 1-01]、米国成人の約79%が
  AIによる人種・民族の偏り悪化を懸念している[VOICE_1_EVIDENCE 1-02]。この裏付けの中から、
  1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んで
  ください(詳細ルールは下記【Voice内の数字】参照)。

【Voice Card 2(2人目のVoice。Recruiter・Hiring Manager=実際にAIツールを使う、または
使うかどうかを判断する採用担当・人事責任者。この内容から書き始めてください)】
- Person: 採用業務を実際に担当し、履歴書スクリーニング・面接日程調整・求人票作成などの
  複数の業務段階で日常的にAIツールを使っている人。
- Situation(状況): 大量の応募者を効率的に処理する必要がある一方、応募者側のAIへの不信に
  日々向き合っている。
- Need(必要としていること): 大量の応募を効率的に処理すること、候補者を適切な職種に
  マッチングさせること。
- Concern(心配していること): 応募者側の不信(Voice 1)に応えるために、バイアス監査結果や
  透明性資料を用意しなければならないという実務上のプレッシャー、応募者自身がAIを使って
  書いた応募書類をどう評価すべきか判断が割れていること(AI活用力の証と見るべきか、努力
  不足の表れと見るべきか)。
- What they protect(守りたいもの): 効率的に仕事を進める能力と、それに伴う説明責任を
  同時に果たすこと。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に大手雇用主(NBCUniversal)が
  ニューヨーク市の法律に基づき、使用するAIツールについて独立監査を受け、その結果を公開
  している実例があり、採用担当者は「使えば便利だが、説明責任も伴う」という板挟みの中で
  日々判断している。
- Constraint(制約): 会社としてAIを導入するかどうかの最終決定権は無く(それはVoice 3の
  領域)、既に導入されたツールを日々運用しながら、応募者の不信にも規制にも対応しなければ
  ならない「現場」の立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 履歴書スクリーニングソフトを
  使って大量の応募を処理した後、応募者からの疑問に答えるためのバイアス監査の要約資料を
  準備する。resource: [VOICE_2_EVIDENCE 2-04](NBCUniversalのAEDT通知、独立監査の実施)、
  [VOICE_2_EVIDENCE 2-05](採用担当者が応募者の不信に文書で応える実務上のプレッシャー)。
- Supporting evidence(裏付け専用): HRリーダーの91%が採用プロセスで実際にAIを使っている
  [VOICE_2_EVIDENCE 2-01]、採用担当者の87%が採用プロセスの少なくとも1段階でAIを使用
  [VOICE_2_EVIDENCE 2-03]。この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字
  だけを、人を主語にした自然な話し言葉で織り込んでください。

【Voice Card 3(3人目のVoice。Business Owner=採用にかかるコスト・速度・会社の存続そのものに
個人として責任を負う経営者。「効率性」という抽象的な立場の代弁者ではなく、一人の経営者
として、この内容から書き始めてください)】
- Person: 中堅企業の経営者、または採用の最終責任を負う事業責任者。自社の採用を回すこと
  自体に、自分個人の判断として責任を負う人。
- Situation(状況): 毎週、採用にかかっている日数・コストのダッシュボードを見ながら、
  AIツールを導入し続けるかどうかを自分の判断で決めている。
- Need(必要としていること): 事業を回すのに十分な速さ・規模で人を採用し続けること、
  コストを持続可能な水準に保つこと。これは「効率」という一般論ではなく、会社が存続
  できるかどうか、自分がその責任を果たせるかどうかという個人的な賭け金である。
- Concern(心配していること): 効率化のメリットを享受する一方で、もし差別・偏りが公に
  なれば、矢面に立つのは自分自身であり、会社の評判・訴訟費用・自分自身の信用を失う
  リスクを背負っていること。
- What they protect(守りたいもの): 会社が採用をスケールさせ続けられる能力、自分が
  下した判断への信頼、会社の存続そのもの。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、業種・規模の異なる
  複数の企業(ホテルチェーン、ITベンダー、クラウド企業)で、AI導入後に採用期間が数週間
  から数日へ大幅に短縮された、あるいはコストが大きく下がったという事例を見て、自分も
  同様の判断を下した、あるいは下そうとしている。
- Constraint(制約): 法規制の詳細を自分で作る立場でも、応募者の不信を直接和らげる立場でも
  ないが、「AIを導入する/使い続ける」という決定そのものを最終的に下すのは自分であり、
  結果の責任は自分に返ってくる。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 採用担当者から「今月も期限内に
  必要な人数を採用できた」という報告を受けて安堵する一方、他社のAI採用ツールが差別を
  理由に訴えられたというニュースを見て、自分の会社は大丈夫かと考える。resource:
  [VOICE_3_EVIDENCE 3-01](ホテルチェーンの採用期間が約6週間から5日間へ短縮、IBMの採用
  コスト30%削減)、[VOICE_3_EVIDENCE 3-05](差別が生じた場合の倫理的・法的リスクと評判
  へのダメージ)。
- Supporting evidence(裏付け専用): 企業の57%が既に採用選考でAIを使用し、74%がAIによって
  採用の質が向上したと回答[VOICE_3_EVIDENCE 3-04]。この裏付けの中から、1つのVoiceにつき
  最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください。

【Voiceの書き始め方(重要、4V版から継続)】
Voiceの本文は、"For [a/an] applicant who..."のような、その人物のことを外側から要約・紹介
する文で始めないでください。代わりに、Voice Cardが示す具体的な状況(その人が実際に毎日
していること・直面していること・使っているもの、目にする光景)から書き始め、そこからその
人の感覚・必要性が自然に浮かび上がるようにしてください。反論のための藁人形にしないで
ください。

【人称(重要、4V版から継続、ユーザーが承認済みの原則)】
3人のVoiceセクション(Voice 1〜3)の本文はすべて、その人物自身が"I"で語る一人称で書いて
ください。三人称("The applicant feels...", "She worries...", "He must choose...")では
なく、"I look at...", "I know...", "I cannot..."のように、その人物自身の声として書いて
ください。この一人称の書き方は、Voiceの人物を主語にする描写(このFocus Module全体の中心
原則、上記【Voiceの書き始め方】【Narrator(語り手)が...】参照)を、文法的にも一人称で徹底
するものです。Hook("## The Question")・Tension・Closingは、この記事の他の指示どおり
三人称・語り手の声のまま変更しないでください(一人称にするのはVoiceセクション本文のみ)。

【Narrator(語り手)がVoiceの人物を外側から要約・分析しないこと(重要、4V版から継続)】
Voiceのセクション内で、語り手がその人物の必要・感情・責任を外側から定義づけるような文
("The need is...", "She is protecting...", "This person must choose between..."のような、
Voiceの人物を三人称で要約・分析する文)を書かないでください。すべての文は、その人が実際に
その瞬間にしていること・気づいていること・感じていることの描写として書いてください。

【Evidenceは脇役であること・Voice内の数字は最大1つ(重要、4V版から継続)】
1つのVoiceの中で、Evidenceの紹介そのものが主役になる文を連続させないでください。文の
主語が調査・報告・データ("A survey found...", "One report described...", "The data
show...")になる文は書かないでください。1つのVoiceのセクション全体を通して、具体的な数字は
最大1つだけにし、必ずその人/その立場の人々の実感に折り込み、話し言葉で書いてください。
3人全員について同じルールを適用してください(3人目の経営者Voiceも例外ではありません)。

【体験claimの根拠付け(重要、Person-Voice版Trial-02新規。Fact Safety[Verified Fact
Ledger]・「Research is backstage」原則の適用)】
Voice本文で、その人物自身の体験として語る箇所において、数値・制度・他者(第三者)の具体的な
行動を事実として断定する場合は、必ずVerified Fact Ledgerに直接のevidenceがあるものに
限ってください。Ledgerに直接の根拠がない事柄(例: 自分自身の評判・信用が具体的にどうなるか、
他社の具体的な訴訟の帰結、規制当局の具体的な運用実態など、まだ起きていない・確認されていない
結果)は、確定した事実として書かず、その人物が実際に抱いている体験・感情・判断として書いて
ください(例: "if that ever came out, it would be my name on it, not anyone else's"の
ような、その人が今この瞬間に感じている不安・実感の描写にとどめ、"my reputation would be
destroyed"のような、まだ起きていない結果を確定事実として断定する書き方はしないでください)。
このルールは3人全員に等しく適用してください。

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィングのような読み味に
しないでください。Light・conversational・human-centeredに、友人に説明するような、気軽に
読める文章にしてください。

【Hookの役割と書き方(重要)】
Hook("## The Question")は、これから3つの立場を紹介するテーマ・状況を簡潔に提示する
導入です。どの立場が正しいかを示唆したり、結論を先取りしたりしないでください。目安は
70語未満です。読み手へ呼びかけたり、命令形・二人称で想像を促したりする表現("Imagine...",
"Picture...", "Think about...", "Consider...")で始めないでください。代わりに、具体的な
情景そのものから、三人称で書き始めてください(例: ある応募者が採用選考の一場面に直面する
情景、AIツールが応募書類を処理する情景など)。Hookに企業名・統計・パーセントを入れないで
ください。

【Voice以外の場面(Tension)で第三者の視点・解決策を混ぜないこと(重要)】
各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを描き切ってください。
解決策・妥協案・提案は、この記事では基本的に書かないでください(Solution articleでは
ありません)。

【Tensionの役割(重要、design.md B-7「共通前提→分岐点→非対称性」の3段構造+外部制約
[fairness/bias/accountability/law/compliance]統合。Trial-01では3段構造は成立したが
外部制約の統合[下記3bのleak_tension_constraint_integration基準]が3/3失敗したため、
Trial-02はこの統合を語り口指示ではなく検証可能な構造として明示し直す)】
「どの立場が正しいか」を決めようとしないでください。そうではなく、なぜ3人全員が、それぞれの
立場からは合理的に見えるのかを掘り下げ、そのうえで、3人の合理性を単純に足しても答えには
ならないことを示してください。**Tensionの中心は、あくまでVoice Cardに描かれている3人の
人物と、彼らの合理性を制約する外部の力であり、Evidence(survey/research/data/percentage)
そのものの説明ではありません。**Tensionの段落を、"A survey found...", "The data show..."
のような、調査・データそのものを主語にした文で始めたり、その説明へ立ち戻ったりしないで
ください。Tensionは、必ず以下の4つの要素を、この順序で(ただし本文に「第1段」等のラベルは
書かず、地の文としてひとつづきに)含めてください:

1. 共通前提: 3人とも、本当は同じこと(適切な人が適切な仕事に就くこと)を望んでいる、という
   出発点を示してください(この時点では誰も間違っていない、という前提の共有)。
2. 分岐点: なぜそこから意見が分かれるかを、答えを要約せず「何を賭けているか」の違いとして
   示してください。Applicantにとっての賭け金は「一度も正当に見てもらえないまま機会を失う
   こと」、Recruiter・Hiring Managerにとっての賭け金は「効率と説明責任を同時に果たせるか」、
   Business Ownerにとっての賭け金は「会社を回し続けられるか、そして自分がその結果の責任を
   負えるか」です(3人の発言内容の再掲・時系列の反復はしないでください)。
3a. 非対称性: Applicantはプロセスに対する発言権を持たない(判断される側)、Recruiter・
   Hiring Managerは日々ツールを運用する現場だが導入を決める側ではない、Business Ownerは
   導入するかどうかを決め、結果の責任を負う側、というプロセス上の力関係の非対称を明示して
   ください。
3b. 外部制約の統合(重要、単なる付け足しにしないこと): 3aの非対称性を示した直後に、
   **なぜ3人のうち誰か1人、あるいは3人の言い分を単純に足し合わせただけでは、この状況の
   答えにならないのか**を、以下のevidence(Ledgerの[VOICE_4_EVIDENCE]タグ由来、この記事
   では独立したVoiceではなくこの統合のための素材として使う)を使って**説明してください**
   (単に「〜という規制がある」と紹介するだけでは不十分です。その規制・監査・過去の中止
   事例が、3人それぞれの選択肢を具体的にどう制約しているために、3人の合理性の単純な合計
   では答えが出ないのかまで、地の文の中で説明してください):
   [VOICE_4_EVIDENCE 4-01](ニューヨーク市Local Law 144、AI採用ツールの年次バイアス監査・
   通知義務)、[VOICE_4_EVIDENCE 4-02](EU AI Actが採用のためのAIを「high-risk」に分類)、
   [VOICE_4_EVIDENCE 4-03](Amazonの社内採用AIが女性を不利に評価し中止された事例)。
   Tensionの自然な流れの中に**1〜2件だけ**、人を主語にした自然な話し言葉で織り込んで
   ください。
単純に3人の主張を時系列で繰り返し要約するのではなく、それぞれが「何を賭けている」のかという
非対称性として描き、そのうえでこの3人の外側に存在する制約を、3bのとおり結論(単純合計では
答えにならない)を成立させる不可欠な理由として統合してください。**3人を単純に「応募者1人
vs 採用担当+経営者2人」のような2対1の陣営へ分けないでください。** 単に「みんなそれぞれの
立場から正しい」とまとめるだけの記述にもしないでください。解決策の提案はここでも基本的に
行わないでください。Verified Fact Ledgerに無い新しい因果関係・新しい事実を作り出さないで
ください。

【Tensionの自己チェック(重要、書き終えた後に必ず行うこと)】
Tensionを書き終えたら、次の2点を自分で確認してください。(a) 外部制約([VOICE_4_
EVIDENCE]由来の記述)を含む文をすべて削除しても、「3人の合理性を単純に足しても答えに
ならない」という結論が変わらず成立してしまう場合、それは統合ではなく単なる付け足しです。
その場合は、その結論が外部制約なしには成立しない(=外部制約があるからこそ、3人それぞれの
選択肢が現実に制約され、単純合計では答えが出ない)ことが分かるように書き直してください。
(b) 「〜という規制がある」「〜という監査が義務付けられている」という紹介・列挙で終わって
いる一文があれば、その規制・監査が3人それぞれの選択肢をどう制約しているかまで、同じ文か
直後の文で書き足してください(地域別の制度名を並べるだけの一文で終わらせないでください)。

【Closingの役割(重要、4V版から継続)】
これは要約でも、In One Lineの言い換えでもありません。3つのVoiceと、その外側にある制約を
見たことによって、この問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを
書いてください。「AIに賛成の人も反対の人もいる」「人による」というだけの結び方で終わらせない
でください。目指すのは、この問題が実は何についての問題なのかを一段深く見せることです。
Writer自身の解決策・コンサル提案にはしないでください。Closingの最初の役割は要約ではなく
再定義です。前段(3つのVoice・Tension)の内容の要約から書き始めないでください。

【各Voiceは同じ意味を2回言わないこと】
1つの経験・1つの感覚は、そのVoiceの中で1回だけ描写してください。

【記事全体の長さについて(この記事専用、hard capではない。3V設計目標、design.md B-6の
未検証monitoring値325〜355秒[尺]から、2V実測[Trial-09実測301.795〜305.135秒]の語数/秒比
(約1.27語/秒)で逆算した合計語数。Trial-01のsoft target約330語は超過を防げなかった
[実測530語/約412秒]ため、design.md B-6の区分別秒数配分により忠実な値へ改めた)】
記事全体の総語数は、**約410〜450語をsoft targetとしてください**(hard capではありません)。
目安配分(soft guidance、design.md B-6の3V区分別秒数配分[Hook約21〜23秒/Voice本体×3
約100〜112秒/Tension約35〜38秒/Closing約22〜25秒]を語数へ比例配分したもの): Hook
45〜55語程度 / 各Voice 70〜85語程度(3人合計約210〜255語)/ Tension 75〜90語程度 /
Closing 45〜55語程度。この配分は目安であり、自然な文章の流れ・Tension(上記4要素すべて)・
Closingの深さを犠牲にしてまで厳密に一致させる必要はありません。ただし、Tensionを60語未満に
削って外部制約の説明(3b)を省略することは避けてください。

【禁止事項まとめ(この記事全体を通して)】
- Reference Example由来の定型的な呼びかけ表現をコピー・準用すること
- "Voice 1"/"Voice A"のような固定ラベル・番号ラベル
- 文の主語がEvidence(survey/report/data/study)になる文(Tensionの段落を含む)
- Narrator(語り手)がVoiceの人物を外側から要約・分析する文
- Voiceセクションの本文を三人称("The applicant...", "She...", "He...")で書くこと
  (Voiceセクションは一人称"I"で書くこと。Hook/Tension/Closingは対象外)
- Voiceのセクションへ第三者(設計者・コンサルタント)の視点を持ち込むこと、または
  どのVoiceの人物であっても具体的な解決策・妥協案をVoice本文内・Tension・Closing内で
  提案すること
- Hookに企業名・統計・パーセントを入れること
- 1つのVoiceのセクション内で具体的な数字を2つ以上使うこと
- 3人を単純に「応募者1人 vs 採用担当+経営者2人」のような2対1の陣営へ分けること
- Tensionで外部制約(fairness/bias/accountability/law)を列挙・解説のリストにすること
  (Tensionの自然な流れの中に1〜2件だけ、人を主語にした話し言葉で織り込むこと)
- Closingを「人による」という結び方だけで終わらせること
- 3人目のVoice(経営者)を「効率性」という抽象的な立場の代弁者として書くこと(一人の
  経営者として、具体的な状況・賭け金・責任から書くこと)"""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    assert gen.COMMON_BLOCK_TEMPLATE.count(ANCHOR) == 1, (
        "アンカー文字列が複数回出現しています。挿入位置が一意に定まらないため中断してください。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    # 4V Trial-02で発見済みの対応を継続: gen.COMMON_BLOCK_TEMPLATEは
    # `{editorial_type_module_block}` placeholderを含むため、後方互換の
    # 既定値(""）を明示的に渡す。
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="",
        editorial_type_module_block="")
    return gen.build_prompt(common_block, instruction)


def run_phase_a(audit_dir: str) -> dict:
    os.makedirs(audit_dir, exist_ok=True)
    candidate_template = build_candidate_template()
    with open(f"{audit_dir}/phase_a_candidate_template.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)
    with open(f"{audit_dir}/phase_a_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK)

    reconstructed = gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
    clean_single_insert = (reconstructed == candidate_template)
    result = {"clean_single_insert_confirmed": clean_single_insert,
              "baseline_len": len(gen.COMMON_BLOCK_TEMPLATE), "candidate_len": len(candidate_template)}
    with open(f"{audit_dir}/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Phase A] clean_single_insert_confirmed={clean_single_insert}")
    return {"result": result, "phase_a_pass": clean_single_insert, "candidate_template": candidate_template}


# ============================================================
# 6区切り構造(Hook/Voice 1/Voice 2/Voice 3/Tension/Closing)専用parser。
# 内部キーはProduction 2V正式命名`point_one`/`point_two`
# (`er012_b_family_editorial_type_registry_01.py`
# B_FAMILY_B1_REQUIRED_SEGMENTS)を`point_three`へ1つ拡張したもの
# (4Vが選んだ`voice_1..4`命名とは異なる設計選択、Gate 1 §7で評価)。
# Production側の`split_five_voice_sections()`/4V Trial-02の
# `split_seven_voice_sections()`はいずれも見出し数が固定のためこの6見出し
# 構造を解釈できず、Trial側で新規実装する。
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)
SIX_SECTION_LABELS = ("hook", "point_one", "point_two", "point_three", "tension", "closing")


def split_six_voice_sections(article_text: str) -> dict | None:
    """6区切り構造を見出し出現順(Hook/Voice 1/Voice 2/Voice 3/Tension/
    Closing)に抽出する。ちょうど6つの##または###見出しがTitleの後に連続
    して登場することを前提とする。想定外の場合はNoneを返す。"""
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 6:
        return None
    result = {}
    for i, label in enumerate(SIX_SECTION_LABELS):
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


def six_section_length_report(article_text: str) -> dict | None:
    sections = split_six_voice_sections(article_text)
    if sections is None:
        return None
    counts = {key: ab01.compute_word_count(sections[f"{key}_body"]) for key in SIX_SECTION_LABELS}
    counts["total_of_six_sections"] = sum(counts.values())
    counts["headings"] = {key: sections[f"{key}_heading"] for key in SIX_SECTION_LABELS}
    counts["unexpected_preamble_before_first_heading"] = sections["unexpected_preamble_before_first_heading"]
    return counts


# ============================================================
# Point Overlap QA(monitoring専用、3V版): lexical_overlap_ratio()は
# 非対称指標(|A∩B|/|A|)のため、有向ペアで計算する。3 Voice間の有向ペアは
# Permutation(3,2)=6、各VoiceとHookとの比較(Voiceを基準、Hookを比較対象)
# 3を加えて合計9値。合否判定には使わない(記録のみ、N=1で閾値を決めない)。
# ============================================================
def run_overlap_monitoring_3v(sections: dict, out_dir: str) -> dict:
    voice_keys = ("point_one", "point_two", "point_three")
    hook = sections["hook_body"]
    directed_voice_pairs = {}
    for a, b in itertools.permutations(voice_keys, 2):
        r = overlap_qa.flag_possible_paraphrase(sections[f"{a}_body"], sections[f"{b}_body"])
        directed_voice_pairs[f"{a}_vs_{b}"] = r
    voice_vs_hook = {}
    for v in voice_keys:
        r = overlap_qa.flag_possible_paraphrase(sections[f"{v}_body"], hook)
        voice_vs_hook[f"{v}_vs_hook"] = r
    all_flags = [r["flagged"] for r in directed_voice_pairs.values()] + [r["flagged"] for r in voice_vs_hook.values()]
    summary = {
        "qa_status": "OK",
        "note": ("EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02: monitoring専用(合否判定には"
                 "使わない、N=1で閾値を決めない)。有向ペア6(Permutation(3,2))+ vs Hook 3 = 9値。"
                 "lexical_overlap_ratio()はProduction関数(er008_point_overlap_qa_18.py)を"
                 "無変更のまま使用。"),
        "directed_voice_pair_count": len(directed_voice_pairs),
        "voice_vs_hook_count": len(voice_vs_hook),
        "total_values": len(directed_voice_pairs) + len(voice_vs_hook),
        "any_flagged": any(all_flags),
        "directed_voice_pairs": directed_voice_pairs,
        "voice_vs_hook": voice_vs_hook,
    }
    with open(f"{out_dir}/point_overlap_qa_monitoring_3v.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02] Overlap monitoring(9値)完了。any_flagged={summary['any_flagged']}")
    return summary


# ============================================================
# Analytical Leakage Check(3V版): QAスキーマは4V踏襲でvoice_1/voice_2/
# voice_3キーを使う(物理構造キー[point_one/two/three]とは意図的に分離、
# Gate 1 §7で両命名方式を記録)。Tensionには新規基準
# `leak_tension_constraint_integration`を追加する(未承認Trial-only新規
# 追加、外部制約[fairness/bias/accountability/law]がTensionへ実質的に
# 統合されているか[列挙・省略になっていないか]を検出する目的)。
# ============================================================
VOICE_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
    "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable",
)
TENSION_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
    "leak_evidence_memorable", "leak_tension_reverts_to_research",
    "leak_binary_camp_split",  # 3V版: 3人を単純に応募者1人vs採用担当+経営者2人に分けていないか
    "leak_tension_constraint_integration",  # 3V新規: 外部制約が列挙・省略でなく統合されているか
)
CLOSING_LEAKAGE_FIELDS = ("leak_closing_simple_summary",)

LEAKAGE_CHECK_DEVELOPER_MESSAGE = (
    "あなたは'Voices/Perspective'型記事(3 Voices・Person-Voice版)のVoice section・Tension "
    "section・Closing sectionを審査する、厳格なEditorial QA判定者です。それぞれのsectionが、"
    "実在する当事者(人)の経験・価値観・必要・心配として書かれているか、あるいは調査結果・"
    "データを整理して説明する文章、単なる要約、Writer自身の解決策提案、単純な2対1分割に戻って"
    "いないかを、各section指定の基準についてPASS/FAILで判定してください。各基準についてPASSは"
    "『問題なし』、FAILは『その問題が実際に本文に存在する』ことを意味します。FAILの場合は、"
    "該当する原文の一節をquoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な"
    "1〜2箇所)。PASSの場合はquoted_evidenceを空文字列にしてください。"
)


def _leakage_item_schema(fields: tuple[str, ...]) -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
    props["reasoning"] = {"type": "string"}
    props["quoted_evidence"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()), "additionalProperties": False}


ANALYTICAL_LEAKAGE_JSON_SCHEMA_3V = {
    "name": "analytical_leakage_check_3v",
    "schema": {
        "type": "object",
        "properties": {
            "voice_1": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_2": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_3": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "tension": _leakage_item_schema(TENSION_LEAKAGE_FIELDS),
            "closing": _leakage_item_schema(CLOSING_LEAKAGE_FIELDS),
        },
        "required": ["voice_1", "voice_2", "voice_3", "tension", "closing"],
        "additionalProperties": False,
    },
    "strict": True,
}

LEAKAGE_CHECK_PROMPT_TEMPLATE_3V = """以下は、あるVoices/Perspective型記事(3 Voices・Person-Voice版)の5つのsection本文
(Voice 1〜3/Tension/Closing)です。それぞれについて、指定された項目を判定してください
(それぞれPASS/FAIL)。

【Voice 1〜3に共通で適用する6項目】
- leak_evidence_subject: 文の主語がsurvey/research/data/percentageになっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字・比較結果が、その人の経験の描写より前面に出ていない場合
  PASS(数字が0個、または1個だけがその人の実感として自然に織り込まれている場合はPASS)
- leak_narrator_analysis: Narrator(語り手)が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人の
  Perspectiveとして書いていない場合PASS
- leak_discovery_syntax: Discovery/Trend記事のような文構造へ戻っていない場合PASS
- leak_evidence_memorable: Evidenceよりもその人物の経験・感情の方が記憶に残る書き方になっている場合PASS

なお、Voice 3(Business Owner=経営者)についても、他のVoiceと同一の基準で判定してください
(「効率性」という抽象的な立場の解説になっている場合は、leak_evidence_subject/leak_narrator_
analysis/leak_discovery_syntaxのいずれかでFAILとしてください)。

【Tensionに適用する7項目】
- leak_evidence_subject / leak_numbers_foreground / leak_discovery_syntax / leak_evidence_memorable:
  上記と同じ意味(Tension本文に対して判定)
- leak_tension_reverts_to_research: Tensionの中心が、3人がなぜ違う答えに至るのかの掘り下げになって
  おり、survey/研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: Tensionが3人を単純に「応募者1人 vs 採用担当+経営者2人」のような対称的な
  2対1の陣営へ分けて描いていない場合PASS(分けている場合FAIL)
- leak_tension_constraint_integration: Tensionが、外部制約(バイアス監査義務・AIの高リスク分類・
  過去の差別的AIの中止/提訴事例等)を、3人の合理性を制約する実質的な力として自然に統合している場合
  PASS。外部制約への言及が全く無い場合、または単なる箇条書き・列挙・解説として付け足されているだけ
  (3人の物語に統合されていない)場合はFAILとしてください。

【Closingに適用する1項目】
- leak_closing_simple_summary: Closingが、単なる要約や「人による」という結び方だけで終わっておらず、
  かつWriter自身の解決策・妥協案の提案になっていない場合PASS

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する
原文を引用してください(英語本文をそのまま引用してよい)。PASSの場合quoted_evidenceは空文字列に
してください。

【Voice 1本文】
{voice_1_body}

【Voice 2本文】
{voice_2_body}

【Voice 3本文】
{voice_3_body}

【Tension本文】
{tension_body}

【Closing本文】
{closing_body}
"""


class LeakageCheckModelMismatchError(RuntimeError):
    pass


_LEAKAGE_SECTION_FIELDS_3V = {
    "voice_1": VOICE_LEAKAGE_FIELDS, "voice_2": VOICE_LEAKAGE_FIELDS,
    "voice_3": VOICE_LEAKAGE_FIELDS,
    "tension": TENSION_LEAKAGE_FIELDS, "closing": CLOSING_LEAKAGE_FIELDS,
}


def run_analytical_leakage_check_3v(client, sections: dict, model: str, reasoning_effort: str,
                                     out_dir: str, attempt: int) -> dict:
    prompt = LEAKAGE_CHECK_PROMPT_TEMPLATE_3V.format(
        voice_1_body=sections["point_one_body"], voice_2_body=sections["point_two_body"],
        voice_3_body=sections["point_three_body"],
        tension_body=sections["tension_body"], closing_body=sections["closing_body"])
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **ANALYTICAL_LEAKAGE_JSON_SCHEMA_3V}},
        input=[
            {"role": "developer", "content": LEAKAGE_CHECK_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise LeakageCheckModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Analytical Leakage Check応答が空です")
    parsed = json.loads(text)

    flagged_items = []
    for section_key, fields in _LEAKAGE_SECTION_FIELDS_3V.items():
        item = parsed[section_key]
        fail_fields = [f for f in fields if item[f] == "FAIL"]
        if fail_fields:
            flagged_items.append({"voice": section_key, "fail_fields": fail_fields,
                                   "reasoning": item["reasoning"], "quoted_evidence": item["quoted_evidence"]})
    result = {
        "model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed,
        "flagged_items": flagged_items, "any_flagged": bool(flagged_items),
    }
    with open(f"{out_dir}/analytical_leakage_check_3v_attempt{attempt}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Leakage Check] attempt{attempt}: any_flagged={result['any_flagged']} "
          f"flagged_items={[(x['voice'], x['fail_fields']) for x in flagged_items]}")
    return result


def build_leakage_corrective_note_3v(leakage_result: dict) -> str:
    lines = [
        "【Analytical Leakage Check是正メモ(前回attemptの検出結果。Voice Card・Verified "
        "Fact Ledger・骨格は変更しません。今回はこの記事全文をゼロから新しく書き直して"
        "ください。前回の文をそのまま部分修正するのではなく、Voice Cardの内容から書き始め、"
        "以下の問題を避けてください)】",
    ]
    voice_label = {"voice_1": "Voice 1(Applicant)", "voice_2": "Voice 2(Recruiter/Hiring Manager)",
                   "voice_3": "Voice 3(Business Owner)", "tension": "Tension", "closing": "Closing"}
    for item in leakage_result["flagged_items"]:
        lines.append(f"- {voice_label[item['voice']]}で検出: {', '.join(item['fail_fields'])}")
        lines.append(f"  理由: {item['reasoning']}")
        if item["quoted_evidence"]:
            lines.append(f"  該当箇所(この種の書き方を避ける): \"{item['quoted_evidence']}\"")
    lines.append(
        "\n【この記事全体で必ず守るContractの優先事項(是正のたびに毎回再掲)】\n"
        "- Compactness: 記事全体の総語数は約410〜450語がsoft targetです(hard capではありません)。"
        "削るときはreplace-with-nothingを基本とし、削った直後に別の言い回しで同じ内容を書き足さないでください。\n"
        "- Tensionの役割: Tensionの中心はVoice Cardの3人の人物と、彼らを制約する外部の力であり、"
        "Evidenceの列挙ではありません。3人を単純に応募者1人vs採用担当+経営者2人へ分けないでください。"
        "外部制約(fairness/bias/accountability/law)は1〜2件だけ、自然な話し言葉で織り込みつつ、その制約が"
        "3人それぞれの選択肢をどう制約しているために単純合計では答えにならないのかまで説明してください"
        "(規制名の紹介・列挙だけで終わらせないでください)。\n"
        "- 体験claimの根拠付け: 数値・制度・他者の行動を事実として述べる場合はLedger evidenceに限り、"
        "根拠がない事柄(自分の評判・信用が具体的にどうなるか等)は体験・感情・判断として書いてください。\n"
        "- Voice 3(経営者)の役割: 「効率性」という抽象的な立場の解説ではなく、一人の経営者の具体的な"
        "状況・賭け金・責任として書いてください。\n"
        "- Closingの役割: 単なる要約や「人による」で終わらせず、この問題が実は何についての問題なのかという"
        "再定義そのものから書き始めてください。解決策の提案はしないでください。"
    )
    return "\n".join(lines)


# ============================================================
# Ledger Deviation Checker + Local Rewrite(4V Trial-02から呼び出し関数・
# 引数・順序を一切変更せずそのまま踏襲。article_textの内部構造[section数]
# に依存しない、記事全体テキストへの適用のためそのまま流用可能。ここへは
# 常に**全文Ledger**[VOICE_4_EVIDENCE含む、無改変]を渡す。TensionがVoice
# 4由来の制約Evidenceを扱うため)。
# ============================================================
def run_ledger_deviation_and_local_rewrite(client, theme_id: str, label: str, article_text: str,
                                            verified_ledger_text: str, out_dir: str, ledger_model: str) -> dict:
    print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: deviation overall_status="
          f"{deviation_result['parsed']['overall_status']} deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text, model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は新規)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(deviation["claim_in_article"], article_text)
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
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT, verified_ledger_text,
                                               point_context, target, deviation, before_ctx, after_ctx,
                                               _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: cycle {cycle} NG item {idx}: "
                  f"resolved={r['resolved']} human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                       model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
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
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    return {
        "article_text": article_text,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "remaining_major_count": len(remaining_major), "any_human_review_required": any_human_review,
    }


# ============================================================
# Reconciliation finding(4V Trial-01/02で発見済み[OPEN-132で追跡中の
# 迂回]、本Trialでも同じ迂回を継続、未解決のまま変更していない):
# `gen._generate_and_compress_article()`は内部で
# `vfl01.run_writer_with_technical_retry()`→`er002_ja_free_markdown_
# restore_r2.validate_point_structure()`を呼ぶが、この関数は
# `h3_count != 2`を無条件でSTRUCTURE_INVALIDにする、Production全体で
# 共有される技術的構造ゲート(3Vは###がちょうど3つになるため必ず弾かれる
# 見込み)。この汎用ゲートはB-Family Voices用途を想定しておらず、変更には
# Production側の承認が必要なため本Trialでは一切変更しない。代わりに、
# Production primitive `vfl01.run_writer_no_search()`(Web検索無し生成、
# 無変更)を直接呼び、通信障害のみの技術的retry(最大2回、Production既定と
# 同じ回数)をTrial側で複製し、構造検証は本ファイル独自の
# `split_six_voice_sections()`(6見出し限定)に委ねる(呼び出し元
# `run_voices_pattern_3v()`が担当)。
# ============================================================
def _generate_and_compress_article_3v(client, theme_id: str, label: str, prompt: str, out_dir: str,
                                       apply_evidence_compression: bool, model: str,
                                       max_technical_attempts: int = 2) -> dict:
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    attempts = []
    raw_result = None
    for attempt in range(1, max_technical_attempts + 1):
        try:
            raw_result = vfl01.run_writer_no_search(client, prompt, model=model)
            attempts.append({"attempt": attempt, "status": "OK", "model": raw_result["model"],
                              "response_id": raw_result["response_id"]})
            break
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_technical_attempts:
                time.sleep(2)
                continue
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(attempts, f, ensure_ascii=False, indent=2, default=str)
    if raw_result is None:
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: writer技術的失敗(通信障害等)。")
        return {"status": "TECHNICAL_GENERATION_FAILED", "article_text": None}

    article_text, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(raw_result["raw_text"].strip())
    if fact_usage_report is not None:
        with open(f"{out_dir}/audit/fact_usage_report.json", "w", encoding="utf-8") as f:
            json.dump(fact_usage_report, f, ensure_ascii=False, indent=2)

    evidence_compression_applied = False
    if apply_evidence_compression:
        with open(f"{out_dir}/audit/pre_editor_article.md", "w", encoding="utf-8") as f:
            f.write(article_text)
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Evidence Compression(Lossless Editor)呼び出し開始...")
        editor_result = ec_editor.run_lossless_editor(client, article_text, model=model)
        with open(f"{out_dir}/audit/evidence_compression_editor_raw.json", "w", encoding="utf-8") as f:
            json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
        if editor_result.get("raw_text"):
            article_text = editor_result["raw_text"]
            evidence_compression_applied = True
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Evidence Compression完了。"
              f"response_id={editor_result.get('response_id')}")

    article_text = gen.normalize_article_formatting(article_text)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    return {"status": "OK", "article_text": article_text, "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied}


# ============================================================
# Writer + Fact A' + Ledger Deviation + Directional Precheckの1 attempt分
# (4V Trial-02 run_voices_pattern_4vの3V版。Point Role Planningは呼ばない
# [4V Trial-02と同じ理由、point_one/two/three固定schemaのためPoint Role
# Planning primitiveの汎用スキーマとは別物]）。
# ============================================================
def run_voices_pattern_3v(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                           out_dir: str, apply_evidence_compression: bool = True,
                           apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    gen_result = _generate_and_compress_article_3v(
        client, theme_id, label, prompt, out_dir, apply_evidence_compression, writer_model)
    if gen_result["status"] != "OK":
        return {"label": label, "status": gen_result["status"], "article_text": None}
    article_text = gen_result["article_text"]

    sections = split_six_voice_sections(article_text)
    if sections is None:
        return {
            "label": label, "status": "STRUCTURE_NOT_SIX_SECTIONS", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
        }

    print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Overlap monitoring(9値)開始...")
    overlap_summary = run_overlap_monitoring_3v(sections, out_dir)

    metrics = gen.compute_metrics(article_text)
    six_report = six_section_length_report(article_text)
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    if six_report is not None:
        with open(f"{out_dir}/six_section_length_report.json", "w", encoding="utf-8") as f:
            json.dump(six_report, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: metrics={metrics} six_section_report={six_report}")

    fc_record = run_fact_check_a_prime_3v(article_text, verified_ledger_text, out_dir)
    fc_status = fc_record.get("final_status")
    verdict = (fc_record.get("result") or {}).get("verdict")
    if verdict == "FAIL":
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Fact CheckerがFAILと判定。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "six_section_report": six_report, "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
            "point_overlap_qa_monitoring": overlap_summary,
        }

    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    ledger_result = run_ledger_deviation_and_local_rewrite(
        client, theme_id, label, article_text, verified_ledger_text, out_dir, ledger_model)
    article_text = ledger_result["article_text"]
    sections = split_six_voice_sections(article_text)  # Local Rewrite後に再抽出

    if ledger_result["remaining_major_count"] or ledger_result["any_human_review_required"]:
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJOR残存/"
              f"human_review_required。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text), "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": ledger_result["ledger_status"],
            "ledger_deviation_count": ledger_result["ledger_deviation_count"],
            "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
            "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
            "point_overlap_qa_monitoring": overlap_summary,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: 比較方向Fact事前チェック開始(rule-based、¥0)...")
        vfl_path = f"{out_dir}/research/stage_b3_vfl.json"  # 本Trialでは存在しない、Layer 2のみ実行(¥0)
        directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[3V-PERSON-VOICE-TRIAL-02][{theme_id}] {label}: 比較方向Fact事前チェック完了。overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": gen.compute_metrics(article_text), "sections": sections,
        "six_section_report": six_section_length_report(article_text),
        "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
        "ledger_status": ledger_result["ledger_status"],
        "ledger_deviation_count": ledger_result["ledger_deviation_count"],
        "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
        "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
        "point_overlap_qa_monitoring": overlap_summary,
        "directional_fact_precheck_status": directional_precheck_status,
    }


# ============================================================
# Writer + Analytical Leakage Checkパイプライン(4V Trial-02
# run_pipeline_4vの3V版。既存上限[初回1回+是正再実行最大2回=合計最大3
# attempts]を省略せず維持する)。
# ============================================================
MAX_WRITER_ATTEMPTS = 3  # 初回1回 + 是正再実行最大2回(既存上限、4V Trial-02と同一)


def run_pipeline_3v(client, theme_id: str, label: str, base_prompt: str, verified_ledger_text: str,
                     out_dir_base: str) -> dict:
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

        print(f"[3V-PERSON-VOICE-TRIAL-02] Writer attempt {attempt}/{MAX_WRITER_ATTEMPTS} 開始(out_dir={attempt_dir})...")
        t0 = time.time()
        with cl.logging_context(theme_id, f"writer_{label.lower()}_attempt{attempt}"):
            result = run_voices_pattern_3v(client, theme_id, label, prompt_for_attempt, verified_ledger_text, attempt_dir)
        result["elapsed_seconds"] = round(time.time() - t0, 1)

        entry = {"attempt": attempt, "out_dir": attempt_dir, "status": result.get("status")}
        final_result = result
        final_attempt_dir = attempt_dir

        if result.get("status") != "OK" or not result.get("article_text"):
            entry["leakage_check"] = None
            entry["any_flagged"] = None
            attempt_history.append(entry)
            print(f"[3V-PERSON-VOICE-TRIAL-02] attempt {attempt}: status={result.get('status')}のためLeakage Checkをスキップします。")
            break

        sections = result.get("sections") or split_six_voice_sections(result["article_text"])
        if sections is None:
            entry["leakage_check"] = {"qa_status": "SKIPPED_NO_SIX_SECTIONS"}
            entry["any_flagged"] = None
            attempt_history.append(entry)
            final_result["sections"] = None
            print(f"[3V-PERSON-VOICE-TRIAL-02] attempt {attempt}: 6区切り構造が検出できずLeakage Checkをスキップしました。")
            break

        leakage = run_analytical_leakage_check_3v(client, sections, writer_model, gen.REASONING_EFFORT, attempt_dir, attempt)
        entry["leakage_check"] = leakage
        entry["any_flagged"] = leakage["any_flagged"]
        attempt_history.append(entry)
        final_result["sections"] = sections
        final_result["analytical_leakage_check"] = leakage

        if not leakage["any_flagged"]:
            print(f"[3V-PERSON-VOICE-TRIAL-02] attempt {attempt}: Analytical Leakage Check flagged項目なし。確定。")
            break
        if attempt == MAX_WRITER_ATTEMPTS:
            print(f"[3V-PERSON-VOICE-TRIAL-02] attempt {attempt}: 最大attempt数に到達。flagged項目が残った状態の"
                  f"記事を最終結果として記録します(Report側でUSER_DECISION_REQUIRED候補として扱う)。")
            break
        corrective_note = build_leakage_corrective_note_3v(leakage)

    with open(f"{out_dir_base}_attempt_history.json", "w", encoding="utf-8") as f:
        json.dump(attempt_history, f, ensure_ascii=False, indent=2, default=str)

    return {"final_result": final_result, "final_attempt_dir": final_attempt_dir,
            "attempt_history": attempt_history, "total_attempts": len(attempt_history)}


def run_writer_stage() -> dict:
    if not os.path.exists(LEDGER_PATH):
        raise SystemExit(f"Ledger not found at {LEDGER_PATH}. STOP条件(Ledger未確定)。")
    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    os.makedirs(LEVEL_OUT_DIR, exist_ok=True)
    phase_a = run_phase_a(f"{LEVEL_OUT_DIR}/audit")
    if not phase_a["phase_a_pass"]:
        print("[3V-PERSON-VOICE-TRIAL-02] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "pipeline": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{LEVEL_OUT_DIR}/raw_usage_log_3v_writer.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text, gen.B1_B_DIRECT_INSTRUCTION)
    with open(f"{LEVEL_OUT_DIR}/audit_candidate_prompt_base.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    print(f"[3V-PERSON-VOICE-TRIAL-02] Writer + Analytical Leakage Checkパイプライン開始(最大{MAX_WRITER_ATTEMPTS} attempts)...")
    pipeline_result = run_pipeline_3v(client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, LEVEL_OUT_DIR)

    with open(f"{LEVEL_OUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": pipeline_result["attempt_history"],
            "total_attempts": pipeline_result["total_attempts"],
            "final_attempt_dir": pipeline_result["final_attempt_dir"],
            "final_result": {k: v for k, v in (pipeline_result["final_result"] or {}).items()
                              if k not in ("article_text", "sections")},
        }, f, ensure_ascii=False, indent=2, default=str)

    final_result = pipeline_result["final_result"] or {}
    print(f"[3V-PERSON-VOICE-TRIAL-02] 完了。total_attempts={pipeline_result['total_attempts']} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"phase_a": phase_a, "pipeline": pipeline_result, "status": "DONE"}


# ============================================================
# Comment 1〜4(確定版Contract+Comment2/3の3V版文言、design.md B-1の
# 手動ドラフトをそのまま採用)。Comment 1/4はregistry.COMMENT_ROLES
# (Production、無変更。voice数に依存しない文言)を使い実際に
# b1s.run_support_text()(Production primitive、無変更)経由でLLM生成する。
# Comment 2/3のRole prompt(registry.py)は"One Voice"/"Another Voice"
# 「2つの声」という2V固定文言をハードコードしており、3V記事へそのまま
# 使うと誤った文言(2声前提)が生成されてしまうため、design.md B-1の手動
# ドラフト(未承認・Trial-only、LLM再生成せず、registryへは一切書かない)を
# そのまま採用する。
# ============================================================
COMMENT_2_TEXT_3V_DRAFT = (
    "Now, you will hear three different voices, one after another. Each person will share "
    "their own view on what you just heard."
)
COMMENT_3_TEXT_3V_DRAFT = (
    "You have heard three different ways of experiencing the same situation. Instead of "
    "deciding which view is right, let us ask why the situation feels different to each "
    "person. Next, we will look more closely at where that difference comes from."
)


def run_comments_1_and_4(client, sections: dict, out_dir: str) -> dict:
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.COMMENT_ROLES  # Production, 無変更

    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{sections['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    result = {
        "comment_1": {"text": c1["text"], "status": c1["status"], "llm_generated": True},
        "comment_2": {"text": COMMENT_2_TEXT_3V_DRAFT, "llm_generated": False,
                      "status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED",
                      "source": "design.md B-1(3V/4V統合設計Trial、未承認・Trial-only、registryへ書かない)"},
        "comment_3": {"text": COMMENT_3_TEXT_3V_DRAFT, "llm_generated": False,
                      "status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED",
                      "source": "design.md B-1(3V/4V統合設計Trial、未承認・Trial-only、registryへ書かない)"},
        "comment_4": {"text": c4["text"], "status": c4["status"], "llm_generated": True},
    }
    with open(f"{out_dir}/comments_1_to_4.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Comments] comment_1={c1['text'][:60]!r} comment_4={c4['text'][:60]!r}")
    return result


# ============================================================
# Pairwise Voice Distinctness Check(未承認仕様候補、4V Trial-02から継続。
# 判定軸=stakeholder position/constraint/responsibility/what they
# protect/reasoning。有向6ペア[個別呼び出し]+一括判定[1回で3 Voiceを
# 同時評価]を実測比較する)。
# ============================================================
DISTINCTNESS_AXES = ("stakeholder_position", "constraint", "responsibility", "what_they_protect", "reasoning")
DISTINCTNESS_JUDGMENT_ENUM = ["SAME", "SIMILAR", "DIFFERENT"]

DISTINCTNESS_DEVELOPER_MESSAGE = (
    "あなたは、Voices/Perspective型記事の複数Voice間の『多様性』(役割・理由・主張の違い)を"
    "審査する、厳格なEditorial QA判定者です。Voice本文を読み、指定された判定軸それぞれに"
    "ついて、同一(SAME)・類似(SIMILAR)・異なる(DIFFERENT)のいずれかを判定してください。"
    "語彙・言い回しの違いではなく、内容としての立場・制約・責任・守るもの・推論構造の違いを"
    "見てください(語彙が違っても推論構造が同じならSAME/SIMILARと判定し、逆に語彙が似ていても"
    "立場・責任が明確に異なればDIFFERENTと判定してください)。"
)


def _distinctness_axis_schema() -> dict:
    return {"type": "object",
            "properties": {"judgment": {"type": "string", "enum": DISTINCTNESS_JUDGMENT_ENUM},
                            "reasoning": {"type": "string"}},
            "required": ["judgment", "reasoning"], "additionalProperties": False}


PAIRWISE_DISTINCTNESS_JSON_SCHEMA = {
    "name": "pairwise_voice_distinctness_check",
    "schema": {
        "type": "object",
        "properties": {axis: _distinctness_axis_schema() for axis in DISTINCTNESS_AXES},
        "required": list(DISTINCTNESS_AXES), "additionalProperties": False,
    },
    "strict": True,
}

PAIRWISE_DISTINCTNESS_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事の2つのVoice本文です。

【Voice X({label_x})本文】
{text_x}

【Voice Y({label_y})本文】
{text_y}

5つの判定軸(stakeholder_position=当事者としての立場、constraint=制約、responsibility=責任、
what_they_protect=何を守ろうとしているか、reasoning=推論の筋道)それぞれについて、Voice Xと
Voice Yが同一/類似/異なるかを判定してください。reasoningフィールドには判定理由を1〜2文の
日本語で書いてください。
"""


def run_pairwise_distinctness_check_single(client, text_x: str, label_x: str, text_y: str, label_y: str,
                                            model: str, reasoning_effort: str = "low") -> dict:
    prompt = PAIRWISE_DISTINCTNESS_PROMPT_TEMPLATE.format(label_x=label_x, text_x=text_x, label_y=label_y, text_y=text_y)
    response = client.responses.create(
        model=model, reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **PAIRWISE_DISTINCTNESS_JSON_SCHEMA}},
        input=[{"role": "developer", "content": DISTINCTNESS_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Distinctness Check応答が空です")
    parsed = json.loads(text)
    return {"model": response.model, "response_id": response.id, "parsed": parsed,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}


BATCH_PAIR_KEYS = ("voice_1_voice_2", "voice_1_voice_3", "voice_2_voice_3")

BATCH_DISTINCTNESS_JSON_SCHEMA = {
    "name": "batch_pairwise_voice_distinctness_check",
    "schema": {
        "type": "object",
        "properties": {pair: {
            "type": "object",
            "properties": {axis: _distinctness_axis_schema() for axis in DISTINCTNESS_AXES},
            "required": list(DISTINCTNESS_AXES), "additionalProperties": False,
        } for pair in BATCH_PAIR_KEYS},
        "required": list(BATCH_PAIR_KEYS), "additionalProperties": False,
    },
    "strict": True,
}

BATCH_DISTINCTNESS_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事(3 Voices)の3つのVoice本文です。

【Voice 1(Applicant)本文】
{voice_1}

【Voice 2(Recruiter/Hiring Manager)本文】
{voice_2}

【Voice 3(Business Owner)本文】
{voice_3}

3人の中から2人を選ぶ組み合わせ(voice_1_voice_2, voice_1_voice_3, voice_2_voice_3)ごとに、
5つの判定軸(stakeholder_position/constraint/responsibility/what_they_protect/reasoning)を
同一(SAME)/類似(SIMILAR)/異なる(DIFFERENT)で判定してください。3人全員を一度に比較したうえで、
各ペアの違いを判定してください。reasoningフィールドには判定理由を1〜2文の日本語で書いてください。
"""


def run_batch_distinctness_check(client, point_one_body: str, point_two_body: str, point_three_body: str,
                                  model: str, reasoning_effort: str = "low") -> dict:
    prompt = BATCH_DISTINCTNESS_PROMPT_TEMPLATE.format(
        voice_1=point_one_body, voice_2=point_two_body, voice_3=point_three_body)
    response = client.responses.create(
        model=model, reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **BATCH_DISTINCTNESS_JSON_SCHEMA}},
        input=[{"role": "developer", "content": DISTINCTNESS_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Batch Distinctness Check応答が空です")
    parsed = json.loads(text)
    return {"model": response.model, "response_id": response.id, "parsed": parsed,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}


def run_distinctness_check_full(client, sections: dict, out_dir: str) -> dict:
    # reasoning_effort="low": Trial限定のコスト管理選択(未承認仕様候補、
    # Contract化された基準ではない。4V Trial-02と同一の選択を継続)。
    model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)
    point_keys = ("point_one", "point_two", "point_three")
    voice_key_map = {"point_one": "voice_1", "point_two": "voice_2", "point_three": "voice_3"}
    t0 = time.time()
    directed_results = {}
    for a, b in itertools.permutations(point_keys, 2):
        key = f"{voice_key_map[a]}_vs_{voice_key_map[b]}"
        r = run_pairwise_distinctness_check_single(
            client, sections[f"{a}_body"], VOICE_STAKEHOLDER_LABEL[voice_key_map[a]],
            sections[f"{b}_body"], VOICE_STAKEHOLDER_LABEL[voice_key_map[b]], model=model)
        directed_results[key] = r
        print(f"[3V-PERSON-VOICE-TRIAL-02][Distinctness] directed {key}: "
              f"{{axis: r['parsed'][axis]['judgment'] for axis in DISTINCTNESS_AXES}}")
    directed_elapsed = round(time.time() - t0, 1)

    t1 = time.time()
    batch_result = run_batch_distinctness_check(
        client, sections["point_one_body"], sections["point_two_body"], sections["point_three_body"], model=model)
    batch_elapsed = round(time.time() - t1, 1)

    direction_agreement = []
    method_agreement = []
    pair_unordered = [("voice_1", "voice_2"), ("voice_1", "voice_3"), ("voice_2", "voice_3")]
    for a, b in pair_unordered:
        pair_key = f"{a}_{b}"
        fwd = directed_results[f"{a}_vs_{b}"]["parsed"]
        rev = directed_results[f"{b}_vs_{a}"]["parsed"]
        batch = batch_result["parsed"][pair_key]
        for axis in DISTINCTNESS_AXES:
            direction_agreement.append(fwd[axis]["judgment"] == rev[axis]["judgment"])
            method_agreement.append(batch[axis]["judgment"] == fwd[axis]["judgment"])

    direction_agreement_rate = round(sum(direction_agreement) / len(direction_agreement), 3)
    method_agreement_rate = round(sum(method_agreement) / len(method_agreement), 3)

    summary = {
        "note": ("EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02: Pairwise Voice Distinctness Check"
                 "(未承認仕様候補、4V Trial-02から継続)。有向6ペア(個別呼び出し)+一括判定"
                 "(1回で3 Voice・3ペア同時評価)を実測比較。reasoning_effort='low'(コスト管理の"
                 "ためのTrial限定の選択、既存Contract化QAの基準ではない)。"),
        "directed_pair_count": len(directed_results), "directed_elapsed_seconds": directed_elapsed,
        "batch_elapsed_seconds": batch_elapsed,
        "direction_agreement_rate": direction_agreement_rate,
        "direction_agreement_comparisons": len(direction_agreement),
        "method_agreement_rate": method_agreement_rate,
        "method_agreement_comparisons": len(method_agreement),
        "method_agreement_definition": "batch_result[pair][axis].judgment == directed_forward[a_vs_b][axis].judgment",
        "directed_results": directed_results, "batch_result": batch_result,
    }
    with open(f"{out_dir}/pairwise_voice_distinctness_check.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Distinctness] 完了。direction_agreement_rate={direction_agreement_rate} "
          f"method_agreement_rate={method_agreement_rate} directed_elapsed={directed_elapsed}s batch_elapsed={batch_elapsed}s")
    return summary


# ============================================================
# 既存2V記事参照(4V Trial-02から継続、同じ参照先):
# `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03_
# REPORT.md`(301.795秒実測、pause除く)に対応する実article.md
# (`er012_output/editorial_b_voices_trial_09_audio/b1b/article.md`)を
# Trial側で直接参照する(Production・Trial-07への書込み・変更は一切
# 行わない、読み取り専用)。
# ============================================================
EXISTING_2V_ARTICLE_PATH_TRIAL09 = "er012_output/editorial_b_voices_trial_09_audio/b1b/article.md"


# ============================================================
# Overlap QAの¥0 control群(4V Trial-02から継続)。合否判定には使わず、
# 実測記録のみ(閾値0.40はここでも変更しない)。
# ============================================================
_POSITIVE_CONTROL_SYNONYM_MAP = {
    "applicant": "candidate", "Applicant": "Candidate", "applicants": "candidates",
    "resume": "application", "résumé": "application", "resumes": "applications",
    "interview": "conversation", "hired": "selected", "job": "role",
    "fair": "just", "score": "rate", "scores": "rates", "scored": "rated",
    "camera": "webcam", "video": "recorded", "AI": "the automated system",
}


def _build_positive_control_text(source_text: str) -> str:
    text = source_text
    for old, new in _POSITIVE_CONTROL_SYNONYM_MAP.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)
    return text


DETERMINISTIC_CONTROL_TEXT_A = (
    "The overnight warehouse supervisor checks a scanner before every shift. The rules on the "
    "screen were written by people she has never met, and she cannot change them even when a "
    "case in front of her does not fit the pattern. She has to enforce a decision she did not "
    "make, and she is the one who has to look the affected worker in the eye afterward. What she "
    "wants is a process she can actually explain when someone asks why."
)
DETERMINISTIC_CONTROL_TEXT_B = (
    "The overnight charge nurse logs into a dashboard before every shift. The thresholds on the "
    "chart were set by people she has never met, and she cannot override them even when a "
    "patient in front of her does not fit the pattern. She has to carry out a decision she did "
    "not make, and she is the one who has to look the affected patient in the eye afterward. "
    "What she wants is a process she can actually explain when someone asks why."
)

THEME_VOCAB_DUMMY_TEXT_A = (
    "The AI screening tool flags applicants using an algorithm trained on past hiring data, and "
    "the recruiter trusts the AI screening score because the algorithm has passed an internal "
    "audit for bias in applicant screening."
)
THEME_VOCAB_DUMMY_TEXT_B = (
    "The applicant distrusts the AI screening algorithm because no audit of the screening tool "
    "has ever been shown to applicants, and the recruiter cannot explain how the AI algorithm "
    "screens each applicant."
)


def run_overlap_controls(sections: dict, out_dir: str) -> dict:
    voice_1 = sections["point_one_body"]
    positive_text = _build_positive_control_text(voice_1)
    positive_result = overlap_qa.flag_possible_paraphrase(positive_text, voice_1)
    deterministic_result = overlap_qa.flag_possible_paraphrase(DETERMINISTIC_CONTROL_TEXT_A, DETERMINISTIC_CONTROL_TEXT_B)

    negative_result = None
    if os.path.exists(EXISTING_2V_ARTICLE_PATH_TRIAL09):
        with open(EXISTING_2V_ARTICLE_PATH_TRIAL09, encoding="utf-8") as f:
            existing_2v_article = f.read()
        existing_sections = b1prod.split_five_voice_sections(existing_2v_article)
        if existing_sections is not None:
            negative_result = overlap_qa.flag_possible_paraphrase(
                existing_sections["voice_a_body"], existing_sections["voice_b_body"])

    theme_dummy_result = overlap_qa.flag_possible_paraphrase(THEME_VOCAB_DUMMY_TEXT_A, THEME_VOCAB_DUMMY_TEXT_B)

    summary = {
        "note": "4V Trial-02から継続。¥0のcontrol群、閾値0.40は合否に使わず記録のみ。",
        "positive_control": {"description": "Voice 1本文の語彙のみ最小限改変した複製(reasoning同一、高overlap期待)",
                              "positive_text": positive_text, "result": positive_result},
        "deterministic_control": {"description": "職名だけ違い推論構造が同一の合成ダミーペア(語彙は大きく変える、低overlap期待=指標の盲点の実証)",
                                   "text_a": DETERMINISTIC_CONTROL_TEXT_A, "text_b": DETERMINISTIC_CONTROL_TEXT_B,
                                   "result": deterministic_result},
        "negative_control": {"description": "既存2V実採用ペア(Trial-07最終記事)の再計算(低overlap期待)",
                              "result": negative_result},
        "theme_vocab_dummy": {"description": "テーマ語彙(AI/screening/applicant/algorithm/audit)を意図的に多く共有する合成ダミーペア(reasoningは異なる、偽陽性リスク確認)",
                               "text_a": THEME_VOCAB_DUMMY_TEXT_A, "text_b": THEME_VOCAB_DUMMY_TEXT_B,
                               "result": theme_dummy_result},
    }
    with open(f"{out_dir}/overlap_qa_controls.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Overlap Controls] positive={positive_result['overlap_ratio']} "
          f"deterministic={deterministic_result['overlap_ratio']} "
          f"negative={(negative_result or {}).get('overlap_ratio')} theme_dummy={theme_dummy_result['overlap_ratio']}")
    return summary


# ============================================================
# 語数・尺見積り(monitoring専用、design.md B-6の2V実測定数を引用し語数/秒比
# で3V estimated durationを換算する。音声は生成していないため実測ではない)。
# ============================================================
TWO_V_FIXED_PARTS_SECONDS = 95.5
TWO_V_VARIABLE_PARTS_SECONDS = 193.2  # Hook+Comment2-4+VoiceA/B見出し・本体+Tension+Closing(pause除く)
TWO_V_COMMENT_2_4_SECONDS = 35.6
TWO_V_PAUSE_SECONDS = 13.0
THREE_V_TARGET_RANGE_SECONDS = (325, 355)  # design.md B-6由来、未検証monitoring値


def build_word_count_and_duration_estimate(sections: dict, out_dir: str) -> dict:
    variable_word_count_3v = sum(
        ab01.compute_word_count(sections[f"{k}_body"])
        for k in ("hook", "point_one", "point_two", "point_three", "tension", "closing")
    )
    variable_word_count_2v = None
    if os.path.exists(EXISTING_2V_ARTICLE_PATH_TRIAL09):
        with open(EXISTING_2V_ARTICLE_PATH_TRIAL09, encoding="utf-8") as f:
            existing_2v_article = f.read()
        existing_sections = b1prod.split_five_voice_sections(existing_2v_article)
        if existing_sections is not None:
            variable_word_count_2v = sum(
                ab01.compute_word_count(existing_sections[f"{k}_body"])
                for k in ("hook", "voice_a", "voice_b", "tension", "closing"))

    estimate = None
    if variable_word_count_2v:
        seconds_per_word = TWO_V_VARIABLE_PARTS_SECONDS / variable_word_count_2v
        estimated_variable_seconds_3v = round(seconds_per_word * variable_word_count_3v, 1)
        two_v_variable_segment_count = 7
        three_v_variable_segment_count = 9
        estimated_pause_seconds_3v = round(
            TWO_V_PAUSE_SECONDS * (three_v_variable_segment_count / two_v_variable_segment_count), 1)
        estimated_total_seconds_3v = round(
            TWO_V_FIXED_PARTS_SECONDS + TWO_V_COMMENT_2_4_SECONDS + estimated_variable_seconds_3v
            + estimated_pause_seconds_3v, 1)
        estimate = {
            "seconds_per_word_2v_variable_parts": round(seconds_per_word, 4),
            "estimated_variable_seconds_3v": estimated_variable_seconds_3v,
            "estimated_pause_seconds_3v": estimated_pause_seconds_3v,
            "estimated_total_seconds_3v": estimated_total_seconds_3v,
            "within_3v_target_range": THREE_V_TARGET_RANGE_SECONDS[0] <= estimated_total_seconds_3v <= THREE_V_TARGET_RANGE_SECONDS[1],
        }

    result = {
        "note": ("音声は生成していない(テキストのみTrial)。design.md B-6の2V実測定数を引用し、"
                 "語数/秒比で3V estimated durationをmonitoring目的でのみ換算した(gate・正式検証ではない)。"),
        "variable_word_count_3v": variable_word_count_3v,
        "variable_word_count_2v_reference": variable_word_count_2v,
        "estimate": estimate,
        "three_v_target_range_seconds_design_md": THREE_V_TARGET_RANGE_SECONDS,
    }
    with open(f"{out_dir}/word_count_and_duration_estimate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-02][Duration Estimate] variable_word_count_3v={variable_word_count_3v} estimate={estimate}")
    return result


# ============================================================
# OPEN-129整合(Gate 3 item 8参照): 3V required_structure(Trial側定義、
# Production 2V正式命名point_one/point_twoを1つ拡張したpoint_three方式、
# 4Vが選んだvoice_1..4命名とは異なる設計選択。妥当性レビューのみ[Gate突合は
# segment/音声が存在しないため実施しない]、正本統合は別途OPEN管理)。
# ============================================================
REQUIRED_STRUCTURE_3V_TRIAL = (
    ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
    ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
    ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
    ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
    ("point_three_heading", "narrator_aoede_en"),
    ("point_one", "point_one"), ("point_two", "point_two"), ("point_three", "point_three"),
    ("full_story_part1", None), ("full_story_part2", None),
    ("tension_reflection", None), ("in_one_line", None),
)


def review_required_structure_3v_trial() -> dict:
    segment_names = [name for name, _role in REQUIRED_STRUCTURE_3V_TRIAL]
    voice_roles = [role for _name, role in REQUIRED_STRUCTURE_3V_TRIAL if role in ("point_one", "point_two", "point_three")]
    review = {
        "note": ("OPEN-129整合(Gate 3 item 8)。point_one/two/three命名方式(Trial側定義、"
                 "registry非編集、Production 2V正式命名point_one/point_twoの1段拡張。4Vが選んだ"
                 "voice_1..4命名とは異なる設計選択、両命名方式の比較は本Trialの評価対象)。"
                 "segment数16、point_one..3がそれぞれちょうど1回登場するかをレビューするのみで、"
                 "Gateへの実際の突合[assemble.py::verify_episode_audio_validation_gate()]は"
                 "音声・segmentが存在しないため実施しない。"),
        "segment_count": len(segment_names),
        "segment_names_unique": len(set(segment_names)) == len(segment_names),
        "voice_roles_present": sorted(set(voice_roles)) == ["point_one", "point_three", "point_two"],
        "each_voice_role_appears_exactly_once": all(voice_roles.count(v) == 1 for v in ("point_one", "point_two", "point_three")),
        "segment_names": segment_names,
    }
    with open(f"{OUT_DIR}/required_structure_3v_trial_review.json", "w", encoding="utf-8") as f:
        json.dump(review, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-02][OPEN-129 review] {review}")
    return review


# ============================================================
# 一人称使用率(機械計測、¥0のrule-based monitoring。Gate・Leakage Checkの
# 判定には使わない。B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCKの一人称指示
# [Voiceセクションのみ"I"、Hook/Tension/Closingは対象外]が実際に満たされて
# いるかを、section別に文単位で機械測定する)。
# ============================================================
FIRST_PERSON_SENTENCE_RE = re.compile(r"\bI\b")


def build_first_person_usage_report(sections: dict, out_dir: str) -> dict:
    per_section = {}
    for label in SIX_SECTION_LABELS:
        body = sections[f"{label}_body"]
        sentences = local_rewrite.split_sentences(body)
        total = len(sentences)
        first_person_sentences = [s for s in sentences if FIRST_PERSON_SENTENCE_RE.search(s)]
        per_section[label] = {
            "total_sentences": total,
            "first_person_sentence_count": len(first_person_sentences),
            "first_person_ratio": round(len(first_person_sentences) / total, 3) if total else None,
        }
    result = {
        "note": ("機械計測(rule-based、¥0、正規表現`\\bI\\b`で文中に一人称'I'[I'm/I'veの"
                 "縮約形も含む]が出現するかを判定)。Gate・Leakage Checkの判定には使わない、"
                 "QA monitoring専用。Voice 1〜3(point_one/two/three)は一人称指示の対象、"
                 "Hook/Tension/Closingは対象外(三人称のまま、低い比率が期待値)。参考値であり、"
                 "単純な'I'出現率を成功基準にはしない(評価はTension/Closing・視点一貫性を"
                 "定性評価で別途行う)。"),
        "per_section": per_section,
    }
    with open(f"{out_dir}/first_person_usage_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    ratios = {k: v["first_person_ratio"] for k, v in per_section.items()}
    print(f"[3V-PERSON-VOICE-TRIAL-02][First Person Usage] {ratios}")
    return result


def run_qa_stage() -> dict:
    """Writer stage完了後、summary.jsonから最終article_textを読み込み、
    Comment 1〜4・Distinctness Check・Overlap Controls・語数/尺見積り・
    一人称使用率・OPEN-129 required_structureレビューをまとめて実行する。"""
    summary_path = f"{LEVEL_OUT_DIR}/summary.json"
    if not os.path.exists(summary_path):
        raise SystemExit(f"{summary_path} が見つかりません。先に`write`stageを実行してください。")
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)
    final_attempt_dir = summary["final_attempt_dir"]
    article_path = f"{final_attempt_dir}/article.md"
    if not os.path.exists(article_path):
        raise SystemExit(f"{article_path} が見つかりません(Writer stageがOKで終わっていない可能性)。")
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    sections = split_six_voice_sections(article_text)
    if sections is None:
        raise SystemExit("最終article.mdが6区切り構造を満たしていません(STOP条件)。")

    qa_out_dir = f"{OUT_DIR}/qa"
    os.makedirs(qa_out_dir, exist_ok=True)

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_3v_qa_stage.jsonl")

    # セッション中断時の再開安全性(4V Trial-02から踏襲): 既にLLM callが完了し
    # 保存済みの成果物があれば再生成せずそのまま再利用する。中断が無かった
    # 通常実行時はファイルが存在しないため従来どおり毎回新規実行される
    # (既存動作への影響はない)。
    comments_path = f"{qa_out_dir}/comments_1_to_4.json"
    if os.path.exists(comments_path):
        print("[3V-PERSON-VOICE-TRIAL-02] comments_1_to_4.json既存のため再利用(再生成しない)。")
        with open(comments_path, encoding="utf-8") as f:
            comments = json.load(f)
    else:
        comments = run_comments_1_and_4(client, sections, qa_out_dir)

    distinctness_path = f"{qa_out_dir}/pairwise_voice_distinctness_check.json"
    if os.path.exists(distinctness_path):
        print("[3V-PERSON-VOICE-TRIAL-02] pairwise_voice_distinctness_check.json既存のため再利用(再生成しない)。")
        with open(distinctness_path, encoding="utf-8") as f:
            distinctness = json.load(f)
    else:
        distinctness = run_distinctness_check_full(client, sections, qa_out_dir)

    overlap_controls = run_overlap_controls(sections, qa_out_dir)
    duration_estimate = build_word_count_and_duration_estimate(sections, qa_out_dir)
    first_person_usage = build_first_person_usage_report(sections, qa_out_dir)
    structure_review = review_required_structure_3v_trial()

    qa_summary = {
        "final_attempt_dir": final_attempt_dir,
        "comments": {k: v for k, v in comments.items()},
        "distinctness_summary": {k: v for k, v in distinctness.items() if k not in ("directed_results", "batch_result")},
        "overlap_controls_summary": {k: v["result"] for k, v in overlap_controls.items() if k != "note"},
        "duration_estimate": duration_estimate,
        "first_person_usage": first_person_usage,
        "structure_review": structure_review,
    }
    with open(f"{qa_out_dir}/qa_stage_summary.json", "w", encoding="utf-8") as f:
        json.dump(qa_summary, f, ensure_ascii=False, indent=2, default=str)
    print("[3V-PERSON-VOICE-TRIAL-02] QA stage完了。")
    return qa_summary


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "write"
    if stage == "write":
        run_writer_stage()
    elif stage == "qa":
        run_qa_stage()
    else:
        run_writer_stage()


if __name__ == "__main__":
    main()
