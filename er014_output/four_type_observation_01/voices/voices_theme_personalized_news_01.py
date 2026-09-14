# ============================================================
# er014_output/four_type_observation_01/voices/voices_theme_personalized_news_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-
# WIRING-01(OPEN-151)
# ============================================================
# テーマ固有データモジュール(Writer原則ではない、Ledger/Voice Card供給の
# ためのデータのみ、`er012_b_family_voices_theme_ai_screening_01.py`と
# 同型)。「Is personalized news good for us?」(2 Voices)の2V runtime
# evidence用テーマデータ。Voice Card 1/2の内容(person/situation/need/
# concern等の枠組み)はFableが構成したが、concrete_scene/supporting_
# evidence内の事実はすべて`research/verified_fact_ledger.txt`の
# VOICE_n_EVIDENCEタグ付きVERIFIED factそのもの(Sonnet自身の知識で
# 事実を補っていない、run_voices_2v_b1.py Phase 1のResearch→Verification
# 結果)。
from __future__ import annotations

import er012_b_family_voices_writer_generic_01 as writer_generic

LEDGER_PATH = "er014_output/four_type_observation_01/voices/research/verified_fact_ledger.txt"

TOPIC_JA = (
    "2026年9月時点、多くのニュースアプリ・SNS・検索エンジンが、利用者の"
    "過去のクリック・興味・行動履歴に基づいてニュースをパーソナライズする"
    "アルゴリズムを使っている。この記事の中心テーマは、パーソナライズされた"
    "ニュースが良いか悪いかを単純などちらか一方に決めることではなく、"
    "この同じ状況について、全く異なる経験をしている2人—パーソナライズされた"
    "feedに日々頼り、その便利さ・関連性の高さを実感している読者(Voice 1)と、"
    "自分のfeedが特定の話題・視点ばかりになってきたと感じ、"
    "worldview narrowing(視野が自己強化的に狭まっていくこと)や"
    "editorial control(人間の編集者ではなく商業的インセンティブを持つ"
    "不透明なアルゴリズムが何を見せるかを決めていること)を懸念する読者"
    "(Voice 2)—が、それぞれ何を経験し、何を大切にし、何を心配しているのかを、"
    "実在する調査・研究に基づいて具体的に描くことである。そのうえで、"
    "この2人の合理性を単純に足しても答えにはならないことも示す。"
)

VOICE_CARD_1 = writer_generic.make_voice_card(
    voice_key="voice_a", stakeholder_label="The reader who relies on her personalized feed",
    role_description_ja="パーソナライズされたfeedに日々頼る、便利さ・関連性を重視する読者",
    reference_phrase="the reader who counts on her personalized feed",
    person=("忙しい生活の合間に、Google Newsの「For you」やFacebookのNews Feedなど、"
            "パーソナライズされたニュースfeedで日々の出来事を追っている読者。"),
    situation="朝の通勤中や仕事の合間に、自分の興味・関心に合わせて並べ替えられたニュースを開いて読む。",
    need="情報過多に埋もれずに、自分の生活に本当に関係のあるニュースへ効率的にたどり着くこと。",
    concern=("すべてを自動選択に任せることで大事な話題を見逃すのではという漠然とした不安があるが、"
             "フォロー・非表示などの設定を実際に使って自分でも調整している。"),
    protect="忙しい毎日の中でもニュースに追いつき続けられているという感覚、自分の関心に合った情報へのアクセス。",
    why=("Reuters Instituteの調査で、パーソナライズに肯定的な人は、ニュースが自分の生活により"
         "関連性が高く、興味のない話題を避けたりすべてを見る時間を省けたりするため効率的だと"
         "感じていることが分かっている。自動選択を「ニュースを得る良い方法」と答えた米国の"
         "回答者は、編集者による選択を挙げた人より多かった。"),
    constraint=("Facebookのランキングが実際にどんなシグナルで決まっているかを完全には把握できず、"
                "フォロー・非表示などの設定機能はあっても、日々忙しい中で細かく調整する余裕は無い。"),
    concrete_scene=("朝、通勤中にGoogle Newsの「For you」を開き、自分の関心に合った記事がすぐに"
                     "並んでいることに安心する。resource: [VOICE_1_EVIDENCE 1-01](Google Newsが"
                     "関心・フォロー中のソース、Googleサービス・YouTubeでの過去の活動に基づき"
                     "パーソナライズしている)、[VOICE_1_EVIDENCE 1-02](フォロー・非表示など"
                     "利用者が自分で調整できる設定機能がある)。"),
    supporting_evidence=("Reuters Institute(27市場)調査で回答者の約半数が自動選択に「快適」と"
                          "回答[VOICE_1_EVIDENCE 1-03]、自由回答では効率的だと説明[VOICE_1_EVIDENCE "
                          "1-04]、米国では自動選択を良い方法と答えた人が37%で編集者選択の22%を"
                          "上回った[VOICE_1_EVIDENCE 1-05]。"),
    stake="自分の時間の中で、関連性の高いニュースに追いつき続けられるかどうか",
)

VOICE_CARD_2 = writer_generic.make_voice_card(
    voice_key="voice_b", stakeholder_label="The reader who worries her feed is closing in",
    role_description_ja="自分のfeedが特定の話題・視点ばかりになってきたと感じ、"
                         "worldview narrowingとeditorial controlの所在を懸念する読者",
    reference_phrase="the reader who worries her feed is narrowing",
    person="Voice 1と同じように日々ニュースアプリやSNSに触れているが、最近、自分のfeedの様子に違和感を覚え始めた読者。",
    situation="SNSやニュースアプリを開くたびに、似たような論調・似たような話題ばかりが並んでいることに気づき始めている。",
    need="自分がどんな基準で記事を選ばれているかを理解し、幅広い視点に触れ続けられること。",
    concern=("ランキングを決めているのは人間の編集者ではなく、エンゲージメントや広告収益に合わせて"
             "チューニングされうる、不透明なアルゴリズムだという事実。"),
    protect="自分の世界の見え方が、知らないうちに狭まっていくことを防ぎたいという感覚。",
    why=("実際に、米国Facebookユーザー1,010万人を分析した研究で、アルゴリズムによるランキングが"
         "クロスカッティングな(異なる立場の)ニュースへの接触を減らしたことが分かっている。"
         "2020年の米大統領選期には、政治的に似た意見のソースからのコンテンツが、アクティブな"
         "成人Facebookユーザーが見る内容の多数を占めていた。"),
    constraint=("個々の利用者はアルゴリズムのパラメータを自分では変えられない。Reuters Institute"
                "調査でも、米国回答者の59%が異なる視点を見逃すことを心配していた。"),
    concrete_scene=("SNSのfeedをスクロールしながら、いつも似たような意見の投稿ばかりが流れてくることに"
                     "気づき、ふと自分の世界が狭まっているのではと思う。resource: [VOICE_2_EVIDENCE "
                     "2-03](アルゴリズムによるFacebook News Feedランキングがクロスカッティングな"
                     "ニュースへの接触を減らした)、[VOICE_2_EVIDENCE 2-04](2020年選挙期、似た意見の"
                     "ソースからのコンテンツがFacebookユーザーが見る内容の多数を占めた)。"),
    supporting_evidence=("米国回答者の59%が異なる視点を見逃すことを心配[VOICE_2_EVIDENCE 2-01]、"
                          "SNS事業者はエンゲージメント・広告収益の最大化に合わせてアルゴリズムを"
                          "調整できると議会調査局が説明[VOICE_2_EVIDENCE 2-09]、EUデジタルサービス法は"
                          "大規模プラットフォームに非プロファイリングの選択肢提供を義務付けている"
                          "[VOICE_2_EVIDENCE 2-10]。"),
    stake="自分でも気づかないうちに、狭い視野の中に閉じ込められてしまうかどうか",
)

TENSION_COMMON_GROUND_VALUE = (
    "自分が実際に何を目にするかが、自分の理解や生活の質に大きく影響すると考えていること"
)
TENSION_ASYMMETRY_VALUE = (
    "Voice 1はfeedのパーソナライズを、フォロー・非表示といった自分の選択・設定として経験して"
    "いるのに対し、Voice 2は同じランキングの仕組みを、自分には把握できない基準で決められる"
    "受け身の立場として経験している(研究自体も、短期的には測定可能な政治的態度の変化を検出"
    "できていない一方で、長期的な累積効果は研究設計上まだ捉えられていないという、単純に"
    "白黒つけられない状態にある)"
)

THEME_CONFIG = writer_generic.make_theme_config(
    theme_id="voices_2v_personalized_news_open151",
    topic_ja=TOPIC_JA,
    ledger_path=LEDGER_PATH,
    voice_cards=[VOICE_CARD_1, VOICE_CARD_2],
    tension_common_ground_value=TENSION_COMMON_GROUND_VALUE,
    tension_asymmetry_value=TENSION_ASYMMETRY_VALUE,
    similar_voices_clarification="",
)
