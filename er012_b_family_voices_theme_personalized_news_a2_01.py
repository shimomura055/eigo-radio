# ============================================================
# er012_b_family_voices_theme_personalized_news_a2_01.py
# 管理ID: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B
# ============================================================
# テーマ固有データモジュール(Writer原則ではない、Ledger/Voice Card/日本語
# タイトル供給のためのデータのみ)。「パーソナライズされたニュース」テーマの
# A2(2 Voices)版。既存B1(2V)のVerified Fact Ledger(`er014_output/
# four_type_observation_01/voices/research/verified_fact_ledger.txt`、
# Research再実行なしで再利用)を直接入力として、A2独自のVoice Cardを
# 新規作成した(ユーザー正式決定1、2026-09-17: B1完成記事からの翻案は
# 使わない。B1記事本文[`er014_output/four_type_observation_01/voices/
# audio/b1_2v_v2/b1b/article.md`]の文言はここでは一切参照・転記していない、
# Ledgerの[VOICE_1/2_EVIDENCE]タグ付きfactのみを根拠にしている)。
#
# 日本語タイトル(`JAPANESE_TITLE_A2`)はwrite_new_theme stage実行後、A2 Writer
# が実際に確定した英語タイトルを見てから、その自然な直訳として作成した
# (新しい主張・数字は追加しない、ユーザー正式決定3のconfig供給契約)。
from __future__ import annotations

import er012_b_family_voices_writer_generic_01 as writer_generic

LEDGER_PATH = "er014_output/four_type_observation_01/voices/research/verified_fact_ledger.txt"

TOPIC_JA = (
    "2026年9月時点、多くのニュースアプリ・SNS・検索エンジンが、利用者の過去の"
    "クリック・興味・行動履歴に基づいてニュースを並び替える(パーソナライズする)"
    "アルゴリズムを使っている。この記事の中心テーマは、パーソナライズされた"
    "ニュースが『良いか悪いか』のどちらか一つに決めることではなく、全く同じ"
    "この仕組みについて、異なる経験をしている2人の読者—パーソナライズされた"
    "feedに日々頼り、限られた時間の中で効率よくニュースを追う読者(One Voice)と、"
    "同じような意見ばかりが表示されることに気づき、自分の視野が狭まっていない"
    "か不安に思う読者(Another Voice)—が、それぞれ何を経験し、何を必要とし、"
    "何を心配し、何を守ろうとしているのかを、実在する調査・研究に基づいて"
    "具体的に描くことである。そのうえで、2人の合理性を単純に足しても答えには"
    "ならないことも示す。"
)

VOICE_CARD_1 = writer_generic.make_voice_card(
    voice_key="voice_a", stakeholder_label="One Voice",
    role_description_ja="パーソナライズされたfeedに日々頼る通勤読者",
    reference_phrase="the commuter who relies on her personalized feed",
    person="毎朝、通勤中にスマートフォンでパーソナライズされたニュースfeedを確認する読者。",
    situation=("通勤電車の中でニュースアプリの「For you」ページを開き、自分の関心・フォロー中の"
               "ソースに近い記事が先に表示されることを期待している。"),
    need="限られた通勤時間の中で、無関係な記事を読み飛ばさずに効率よくニュースに追いつくこと。",
    concern="重要なニュースがfeedから漏れて自分の目に入らないかもしれないという不安。",
    protect="限られた朝の時間と、自分でfeedをコントロールできているという感覚。",
    why=("Google Newsは、利用者が指定した関心・フォロー中のソースに加え、Googleサービス・"
         "YouTubeでの過去の活動に基づいて「For you」「Following」を選定している"
         "[VOICE_1_EVIDENCE 1-01]。トピック・ソースのフォロー/フォロー解除、記事の表示量調整、"
         "ソースの非表示など、利用者自身が調整できる機能もある[VOICE_1_EVIDENCE 1-02]。"),
    constraint="ランキングの裏にある信号のすべてを見ることはできず、許された範囲の調整しかできない。",
    concrete_scene=("電車の中で「For you」ページを開くと、フォローしているトピックが既に上の方に"
                     "並んでいて、駅に着く前に見出しだけでも確認できる[VOICE_1_EVIDENCE 1-01]"
                     "[VOICE_1_EVIDENCE 1-02]。"),
    supporting_evidence=("2025年の27市場調査では、回答者の約半数が過去の好みに基づく自動選択に"
                          "「快適」と回答した[VOICE_1_EVIDENCE 1-03]。パーソナライズに肯定的な"
                          "回答者は、自分の生活に関連性が高く、興味のない話題を避けられて効率的だと"
                          "説明している[VOICE_1_EVIDENCE 1-04]。別の調査では、自分の過去の消費に"
                          "基づく自動選択を『ニュースを得る良い方法』と答えた人が37%で、編集者による"
                          "選択(22%)や友人の消費に基づく選択(17%)を上回った[VOICE_1_EVIDENCE 1-05]。"),
    stake="朝の時間を管理可能に保ち、自分のfeedを自分でコントロールできている感覚",
)

VOICE_CARD_2 = writer_generic.make_voice_card(
    voice_key="voice_b", stakeholder_label="Another Voice",
    role_description_ja="自分のfeedが狭まっていくことを懸念する読者",
    reference_phrase="another reader who feels her feed narrowing",
    person="スマートフォンのfeedで同じような意見や話題が繰り返し表示されることに気づいた読者。",
    situation="feedをスクロールするたびに似た立場のニュースばかりが並び、ランキングの裏側は見えない。",
    need="なぜある記事が別の記事より優先して表示されるのかを知り、隠された設定を変えられること。",
    concern=("feedのランキングが、自分がニュースを理解する助けになるためではなく、クリックや"
             "広告収益のために調整されているのではないかという懸念[VOICE_2_EVIDENCE 2-09]。"),
    protect="異なる視点に触れる機会と、偏りのない全体像を持てているという感覚。",
    why=("1,010万人の米国Facebook利用者を分析した研究では、アルゴリズムによるNews Feed"
         "ランキングが、友人が共有した内容に比べて異なる立場のニュースへの接触を減らしていた"
         "(ただし利用者自身のクリックの方がその接触をさらに制限していた)[VOICE_2_EVIDENCE 2-03]。"
         "2020年米大統領選期には、政治的に似た意見のソースからの内容が、アクティブな成人利用者が"
         "見る内容の多数を占めていた[VOICE_2_EVIDENCE 2-04]。"),
    constraint=("ランキングの仕組み自体を止めることはできず、短期間の実験では、この状態が何年も"
                "続いた場合に人がどう変わるかまでは確かめられていない[VOICE_2_EVIDENCE 2-11]。"),
    concrete_scene="同じアプリを開くたびに見慣れた主張や情報源ばかりが並び、何が表示されていないのか気になる。",
    supporting_evidence=("ある調査では、59%の人がパーソナライズによって異なる視点を見逃すかもしれないと"
                          "懸念し、60%が重要な情報を見逃すかもしれないと懸念していた[VOICE_2_EVIDENCE 2-01]。"),
    stake="自分の普段のfeedの外にある視点や情報を見失わないこと",
)

TENSION_COMMON_GROUND_VALUE = "自分のfeedに表示されるものが、自分が何を理解するかを形作っているということ"
TENSION_ASYMMETRY_VALUE = (
    "One Voiceはフォロー・非表示・表示量調整という形で自分の選択の一部を変えられるが、"
    "Another Voiceはランキングの裏側にある規則そのものには触れられず、それが見えない形で"
    "自分の視野を形作っているかもしれないという非対称"
)

THEME_CONFIG = writer_generic.make_theme_config(
    theme_id="personalized_news_a2_new_topic_01",
    topic_ja=TOPIC_JA,
    ledger_path=LEDGER_PATH,
    voice_cards=[VOICE_CARD_1, VOICE_CARD_2],
    tension_common_ground_value=TENSION_COMMON_GROUND_VALUE,
    tension_asymmetry_value=TENSION_ASYMMETRY_VALUE,
)

# PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B(ユーザー正式決定3):
# 日本語タイトルはconfig供給。write_new_theme stage実行後、A2 Writerが
# 実際に確定した英語タイトル("The News You See, and the News You Miss"、
# attempt3/最終article.md)の自然な直訳へ更新した(新しい主張・数字は
# 追加しない)。
JAPANESE_TITLE_A2 = "見えているニュースと、見えていないニュース"
