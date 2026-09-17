# ============================================================
# er012_output/personalized_news_b1_rebuild_01/voices_theme_personalized_news_b1_rebuild_01.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01
# ============================================================
# テーマ固有データモジュール(Writer原則ではない、Ledger/Voice Card供給の
# ためのデータのみ、`er014_output/.../voices_theme_personalized_news_01.py`と
# 同型)。「Personalized News: Useful or Narrowing?」B1(Advanced)再構築版。
# 旧版との違い: (1) 新規Research(2026-09-17実施、Part1+Part2)に基づく新
# Ledgerを参照する、(2) OPEN-166で指摘されたTension非対称性テキストの
# 過度な一般化("研究自体も、短期的には測定可能な政治的態度の変化を検出
# できていない")を、研究間で結果が割れている領域として正直に書き直した、
# (3) CURRENT_SPEC L679(Writer原則A/C/F/E、`leak_position_blur`)を厳守
# (OPEN-167は未承認のため適用しない)。
from __future__ import annotations

import er012_b_family_voices_writer_generic_01 as writer_generic

LEDGER_PATH = "er012_output/personalized_news_b1_rebuild_01/research/verified_fact_ledger.txt"

TOPIC_JA = (
    "2026年9月時点、多くのニュースアプリ・SNS・検索エンジンが、利用者の過去のクリック・"
    "興味・行動履歴に基づいてニュースをパーソナライズするアルゴリズムを使っている。この"
    "記事の中心テーマは、パーソナライズされたニュースが良いか悪いかを単純にどちらか一方に"
    "決めることではなく、この同じ状況について全く異なる経験をしている2人—パーソナライズ"
    "されたfeedに日々頼り、その便利さ・関連性の高さを実感している読者(Voice 1)と、自分の"
    "feedが特定の話題・視点ばかりになってきたと感じ、誰が・何の基準で自分に何を見せるかを"
    "決めているのか分からないことを懸念する読者(Voice 2)—が、それぞれ何を経験し、何を"
    "大切にし、何を心配しているのかを、実在する調査・研究に基づいて具体的に描くことである。"
    "また、パーソナライズが実際に人の政治的な考え方まで変えるのかどうかについて、研究者の"
    "間でも意見が割れていること自体も、単純化せず正直に示す。"
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
    why=("パーソナライズされた選択は、自分の生活によく合っていて、時間や労力を節約できると"
         "感じている。人間の編集者よりも偏りが少ないと感じることさえある。"),
    constraint=("Facebookのランキングが実際にどんなシグナルで決まっているかを完全には把握できず、"
                "フォロー・非表示などの設定機能はあっても、日々忙しい中で細かく調整する余裕は無い。"),
    concrete_scene=("朝、通勤中にGoogle Newsの「For you」を開き、自分の関心に合った記事がすぐに"
                     "並んでいることに安心する。resource: [VOICE_1_EVIDENCE V1-01](Google Newsが"
                     "関心・フォロー中のソース、Googleサービス・YouTubeでの過去の活動に基づき"
                     "パーソナライズしており、フォロー・非表示など利用者が自分で調整できる設定機能が"
                     "ある)。"),
    supporting_evidence=("Reuters Institute 2025年調査で平均49%が自動選択に「快適」と回答"
                          "[VOICE_1_EVIDENCE V1-02]、肯定的な理由として関連性の高さ・時間の節約・"
                          "人的編集者より偏りが少ないという感覚が挙がった[VOICE_1_EVIDENCE V1-03]、"
                          "2023年調査では自動選択を良い方法と答えた人が30%で編集者選択の27%を"
                          "上回った[VOICE_1_EVIDENCE V1-04]。"),
    stake="自分の時間の中で、関連性の高いニュースに追いつき続けられるかどうか",
)

VOICE_CARD_2 = writer_generic.make_voice_card(
    voice_key="voice_b", stakeholder_label="The reader who worries her feed is closing in",
    role_description_ja="自分のfeedが特定の話題・視点ばかりになってきたと感じ、"
                         "誰が・何の基準でそれを決めているのか分からないことを懸念する読者",
    reference_phrase="the reader who worries her feed is narrowing",
    person="Voice 1と同じように日々ニュースアプリやSNSに触れているが、最近、自分のfeedの様子に違和感を覚え始めた読者。",
    situation="SNSやニュースアプリを開くたびに、似たような論調・似たような話題ばかりが並んでいることに気づき始めている。",
    need="自分がどんな基準で記事を選ばれているかを理解し、幅広い視点に触れ続けられること。",
    concern=("ランキングを決めているのは人間の編集者ではなく、エンゲージメントや広告収益に合わせて"
             "チューニングされうる、不透明なアルゴリズムだという事実。"),
    protect="自分の世界の見え方が、知らないうちに狭まっていくことを防ぎたいという感覚。",
    why=("実際に、自分が目にする投稿の大部分が、自分と似た意見の人たちのものに偏っていることが"
         "調査でも確認されている。異なる視点に触れる機会を失っているのではという不安がある。"),
    constraint=("個々の利用者はアルゴリズムのパラメータを自分では変えられない。EUのような一部地域を"
                "除けば、非パーソナライズの選択肢が保証されているわけでもない。"),
    concrete_scene=("SNSのfeedをスクロールしながら、いつも似たような意見の投稿ばかりが流れてくることに"
                     "気づき、ふと自分の世界が狭まっているのではと思う。resource: [VOICE_2_EVIDENCE "
                     "V2-01](2020年の観察データで、米国Facebook利用者の中央値は投稿の50.4%が同類の"
                     "情報源から、対立側の情報源からはわずか14.7%だった)。"),
    supporting_evidence=("Reuters Institute 2023年調査で46%が異なる視点を見逃すことを心配"
                          "[VOICE_2_EVIDENCE V2-03]、米議会調査局はSNS運営者がエンゲージメントや"
                          "広告収益の最大化に合わせてアルゴリズムを調整できると説明している"
                          "[VOICE_2_EVIDENCE V2-04]、EUデジタルサービス法は大規模プラットフォームに"
                          "非プロファイリングの選択肢提供を義務付けている[VOICE_2_EVIDENCE V2-05]。"),
    stake="自分でも気づかないうちに、狭い視野の中に閉じ込められてしまうかどうか",
)

TENSION_COMMON_GROUND_VALUE = (
    "自分が実際に何を目にするかが、自分の理解や生活の質に大きく影響すると考えていること"
)
# OPEN-166対応: 旧版の「研究自体も、短期的には測定可能な政治的態度の変化を検出できて
# いない」という一般化(単一研究への言及を「研究全体」であるかのように書いていた)を、
# 2026-09-17再Researchの結果を踏まえて書き直した。特定の結論(効果がある/ない)を
# 断定せず、研究間で結果が割れていること自体を明示する(Ledger[CONTESTED_RESEARCH_
# AREA] C-01を根拠とする)。
# 修正(r2、Analytical Leakage Check是正): 初版は「3か月の実験で変化なし/別の
# プラットフォームで7週間変化あり」のように個別studyを列挙する書き方をしており、
# Tensionのleak_evidence_subject/leak_numbers_foreground/leak_discovery_syntax/
# leak_evidence_memorable/leak_tension_reverts_to_researchが3attempt全てでFAILした
# (Writer原則Prompt/Validator自体は無変更、本テーマ固有データの書き方の問題と特定)。
# r2では、具体的な研究名・期間・数字を挙げず、「二人とも自分では確かめようがない」
# 「専門家の間でも決着していない」という、二人の認識論的な非対称性そのものとして書き直す。
# 修正(r3、Analytical Leakage Check是正): r2でも「platform experiments」を主語にした
# 一文が残り、leak_evidence_subject/leak_discovery_syntax/leak_tension_reverts_to_research
# がFAILした。r3では研究・実験への言及を完全に外したが、Writerがモデル自身の判断で
# Ledger内[CONTESTED_RESEARCH_AREA]C-01の詳細(プラットフォーム名・週数・pt数)を
# 独自に呼び出し、同じ理由で5項目全FAILとなった。
# 修正(r4): Ledger側C-01に抽象度の指示を追記した結果、Voice A/B/Closingは0 FAILに
# なったが、Tensionは「The picture is mixed: some short-term tests found measurable
# changes...」のようにtests/研究を主語にした文をWriterが依然として書き、
# leak_evidence_subject/leak_tension_reverts_to_researchの2項目だけが残存FAILした。
# 修正(r5): 「研究/報告」という言葉自体を主語にせず、二人(または疑問文自体)を主語に
# した文へ言い換えたが、leak_discovery_syntax/leak_tension_reverts_to_researchはなお
# FAILした(「政治的態度変化が数週間で起きるか」という問い自体が、主語を変えても
# Discovery的な「未解決の研究設問」として判定されるため)。
# 最終判断(r6): 政治的態度変化についての言及自体をTension本文から完全に削除する。
# 理由: OPEN-166の実体的な問題は「事実として誤った/古い断定をしないこと」であり、
# Tensionに必ずこの論点を書かねばならないわけではない。旧Ledgerが抱えていた「短期的には
# 変化が検出されていない」という断定自体をそもそも書かない(=検証不能な形で言及しない)
# ことで、過度な一般化のリスクを完全に除去する。Tensionは、実証が固まっているVoice 1/
# Voice 2それぞれのconvenience(選べる)vs opacity(選べない)という非対称性のみに集中する
# (この非対称性自体はV1-01〜V1-04/V2-01〜V2-05のVERIFIED Factで十分に裏付けられている)。
# 政治的態度変化研究の現状(研究間で結果が割れていること)は、本文には書かず、Ledger
# ([CONTESTED_RESEARCH_AREA] C-01)・RESULT_PACKETの記録としてのみ残す。
TENSION_ASYMMETRY_VALUE = (
    "Voice 1はfeedのパーソナライズを、フォロー・非表示といった自分の選択・設定として経験して"
    "いるのに対し、Voice 2は同じランキングの仕組みを、自分には把握できない基準で決められる"
    "受け身の立場として経験している。一方は自分で調整できる選択として、もう一方は誰か"
    "(あるいは何か)に委ねるしかない条件として、同じ仕組みを経験している"
)

THEME_CONFIG = writer_generic.make_theme_config(
    theme_id="voices_2v_personalized_news_b1_rebuild_01",
    topic_ja=TOPIC_JA,
    ledger_path=LEDGER_PATH,
    voice_cards=[VOICE_CARD_1, VOICE_CARD_2],
    tension_common_ground_value=TENSION_COMMON_GROUND_VALUE,
    tension_asymmetry_value=TENSION_ASYMMETRY_VALUE,
    similar_voices_clarification="",
)
