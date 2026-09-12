# ============================================================
# er012_b_family_voices_theme_ai_screening_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-
# GENERALIZATION-AND-REGRESSION
# ============================================================
# テーマ固有データモジュール(Writer原則ではない、Ledger/Voice Card供給の
# ためのデータのみ)。「企業は採用選考にAIを使うべきか」テーマの3 Voice
# 構成を、`er012_editorial_b_voices_3v_person_voice_trial_02.py`の
# Verified Fact Ledger・Voice Card 1〜3・Tension content・外部制約素材から
# **そのまま**(新しい主張・数字・Voice設計を一切加えず)移した。
#
# 目的: 「新しい汎用Writerテンプレート(er012_b_family_voices_writer_
# generic_01.py)+テーマ固有Ledger/Voice Card」という正式候補経路で、
# 既存の承認済みAI採用選考記事(Trial-02、3V成立確認済み)をRegression
# 再生成するための入力データ。旧Trial-02ファイル自体は一切importしない
# (Gate 4、および禁止事項「旧テーマ固有Prompt裏利用の禁止」)。
#
# データの出典(全てTrial-02本体の該当箇所からの転記、要約・改変なし):
#   - Ledger: er012_output/ai_screening_ledger_trial_01/research/
#     verified_fact_ledger.txt(無変更、Trial-02と同一ファイルをそのまま参照)
#   - topic_ja: Trial-02 `TOPIC_JA`(L146-163)の全文
#   - Voice Card 1/2/3: Trial-02 Focus Module L350-442の該当ブロック
#   - Tension共通前提/非対称性/賭け金: Trial-02 Focus Module L514-527
#   - 外部制約統合素材: Trial-02 Focus Module L528-539
#   - similar_voices_clarification: Trial-02 Focus Module L343-348
from __future__ import annotations

import er012_b_family_voices_writer_generic_01 as writer_generic

LEDGER_PATH = "er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt"

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

VOICE_CARD_1 = writer_generic.make_voice_card(
    voice_key="voice_1", stakeholder_label="Applicant",
    role_description_ja="AIスクリーニングを受ける応募者", reference_phrase="the applicant",
    person=("求職者として、企業の採用選考でAIによる評価(書類スクリーニング、適性・性格の"
            "自動採点、動画面接での表情・話し方の評価など)を受ける側の人。"),
    situation=("応募書類を送り、動画面接を受け、その評価の一部または全部をAIが行って"
               "いることを知っている、あるいは後から知る。"),
    need="自分の実力・人柄を正確に見てもらうこと、なぜ不採用になったのか理由を理解できること。",
    concern=("AIが人間の採用担当者より偏っている(biased)のではないかという広い不信感、"
             "人種・民族に基づく偏りが悪化するのではという懸念、異議を申し立てる手段が"
             "ないまま機械的に評価され不利益を受けるリスク。"),
    protect="公正に見てもらう機会そのもの、評価の理由を理解し納得できること。",
    why=("実際に、スキル評価では良い結果を出したにもかかわらず、AIによる動画面接評価で"
         "身振り・表情を低く採点されて不採用となり、その後長期の失業状態に陥ったと証言する"
         "女性求職者の実例がある。また、ある応募者はAIによる「信頼性・誠実さ」スコアリングを、"
         "オプトアウトも異議申し立てもできないまま受けさせられたとして提訴した実例もある。"),
    constraint="選考プロセスにAIが使われるかどうか、どう使われるかについて発言権を持たない、判断される側の立場。",
    concrete_scene=("動画面接で、ソフトウェアが自分の声のトーン・表情・身振りをスコアリングしていると"
                     "知りながら話す、あるいは、なぜ次の段階へ進めなかったのか説明のないまま結果だけを"
                     "受け取る。resource: [VOICE_1_EVIDENCE 1-03](BBC Worklife、動画面接評価で低評価"
                     "となり長期失業に陥った女性求職者)、[VOICE_1_EVIDENCE 1-04](CVS Health応募者、"
                     "HireVue/Affectivaの表情・声のトーン分析をオプトアウトも異議申し立てもできないまま"
                     "受け提訴)。"),
    supporting_evidence=("米国の就労中求職者の49%がAIツールは人間より偏っていると考えている"
                          "[VOICE_1_EVIDENCE 1-01]、米国成人の約79%がAIによる人種・民族の偏り悪化を"
                          "懸念している[VOICE_1_EVIDENCE 1-02]。"),
    stake="一度も正当に見てもらえないまま機会を失うこと",
)

VOICE_CARD_2 = writer_generic.make_voice_card(
    voice_key="voice_2", stakeholder_label="Recruiter/Hiring Manager",
    role_description_ja="実際にAIツールを使う、または使うかどうかを判断する採用担当・人事責任者",
    reference_phrase="the recruiter",
    person=("採用業務を実際に担当し、履歴書スクリーニング・面接日程調整・求人票作成などの"
            "複数の業務段階で日常的にAIツールを使っている人。"),
    situation="大量の応募者を効率的に処理する必要がある一方、応募者側のAIへの不信に日々向き合っている。",
    need="大量の応募を効率的に処理すること、候補者を適切な職種にマッチングさせること。",
    concern=("応募者側の不信(Applicant Voice)に応えるために、バイアス監査結果や透明性資料を"
             "用意しなければならないという実務上のプレッシャー、応募者自身がAIを使って書いた"
             "応募書類をどう評価すべきか判断が割れていること(AI活用力の証と見るべきか、"
             "努力不足の表れと見るべきか)。"),
    protect="効率的に仕事を進める能力と、それに伴う説明責任を同時に果たすこと。",
    why=("実際に大手雇用主(NBCUniversal)がニューヨーク市の法律に基づき、使用するAIツールに"
         "ついて独立監査を受け、その結果を公開している実例があり、採用担当者は「使えば便利だが、"
         "説明責任も伴う」という板挟みの中で日々判断している。"),
    constraint=("会社としてAIを導入するかどうかの最終決定権は無く(それはBusiness Owner Voiceの"
                "領域)、既に導入されたツールを日々運用しながら、応募者の不信にも規制にも対応"
                "しなければならない「現場」の立場。"),
    concrete_scene=("履歴書スクリーニングソフトを使って大量の応募を処理した後、応募者からの疑問に"
                     "答えるためのバイアス監査の要約資料を準備する。resource: [VOICE_2_EVIDENCE 2-04]"
                     "(NBCUniversalのAEDT通知、独立監査の実施)、[VOICE_2_EVIDENCE 2-05](採用担当者が"
                     "応募者の不信に文書で応える実務上のプレッシャー)。"),
    supporting_evidence=("HRリーダーの91%が採用プロセスで実際にAIを使っている[VOICE_2_EVIDENCE 2-01]、"
                          "採用担当者の87%が採用プロセスの少なくとも1段階でAIを使用"
                          "[VOICE_2_EVIDENCE 2-03]。"),
    stake="効率と説明責任を同時に果たせるか",
)

VOICE_CARD_3 = writer_generic.make_voice_card(
    voice_key="voice_3", stakeholder_label="Business Owner",
    role_description_ja="採用にかかるコスト・速度・会社の存続そのものに個人として責任を負う経営者",
    reference_phrase="the business owner",
    person=("中堅企業の経営者、または採用の最終責任を負う事業責任者。自社の採用を回すこと自体に、"
            "自分個人の判断として責任を負う人。"),
    situation=("毎週、採用にかかっている日数・コストのダッシュボードを見ながら、AIツールを"
               "導入し続けるかどうかを自分の判断で決めている。"),
    need=("事業を回すのに十分な速さ・規模で人を採用し続けること、コストを持続可能な水準に"
          "保つこと。これは「効率」という一般論ではなく、会社が存続できるかどうか、自分が"
          "その責任を果たせるかどうかという個人的な賭け金である。"),
    concern=("効率化のメリットを享受する一方で、もし差別・偏りが公になれば、矢面に立つのは"
             "自分自身であり、会社の評判・訴訟費用・自分自身の信用を失うリスクを背負っていること。"),
    protect="会社が採用をスケールさせ続けられる能力、自分が下した判断への信頼、会社の存続そのもの。",
    why=("実際に、業種・規模の異なる複数の企業(ホテルチェーン、ITベンダー、クラウド企業)で、"
         "AI導入後に採用期間が数週間から数日へ大幅に短縮された、あるいはコストが大きく下がった"
         "という事例を見て、自分も同様の判断を下した、あるいは下そうとしている。"),
    constraint=("法規制の詳細を自分で作る立場でも、応募者の不信を直接和らげる立場でもないが、"
                "「AIを導入する/使い続ける」という決定そのものを最終的に下すのは自分であり、"
                "結果の責任は自分に返ってくる。"),
    concrete_scene=("採用担当者から「今月も期限内に必要な人数を採用できた」という報告を受けて"
                     "安堵する一方、他社のAI採用ツールが差別を理由に訴えられたというニュースを見て、"
                     "自分の会社は大丈夫かと考える。resource: [VOICE_3_EVIDENCE 3-01](ホテルチェーンの"
                     "採用期間が約6週間から5日間へ短縮、IBMの採用コスト30%削減)、[VOICE_3_EVIDENCE 3-05]"
                     "(差別が生じた場合の倫理的・法的リスクと評判へのダメージ)。"),
    supporting_evidence=("企業の57%が既に採用選考でAIを使用し、74%がAIによって採用の質が向上したと"
                          "回答[VOICE_3_EVIDENCE 3-04]。"),
    stake="会社を回し続けられるか、そして自分がその結果の責任を負えるか",
    card_intro_caveat="「効率性」という抽象的な立場の代弁者ではなく、一人の経営者として、",
)

SIMILAR_VOICES_CLARIFICATION = (
    "Recruiter/Hiring ManagerとBusiness Ownerはどちらもこの状況でAIの効率性を実感していますが、"
    "それぞれが背負っているものは全く異なります。Recruiter/Hiring Managerは「応募者の不信に"
    "日々応える」という実務負担を抱えており、導入するかどうかの決定権自体は持ちません。"
    "Business Ownerは導入を決める側であり、差別が公になった場合に矢面に立つのは自分自身だという"
    "個人的な責任を負っています。この2人を単純に「会社側」として同一視しないでください。"
    "それぞれの意見の背後にある、具体的な経験・守りたいもの・立場上の制約まで、Voice Cardの内容を"
    "使って丁寧に描いてください。"
)

TENSION_COMMON_GROUND_VALUE = "適切な人が適切な仕事に就くこと"
TENSION_ASYMMETRY_VALUE = (
    "Applicantはプロセスに対する発言権を持たない(判断される側)、Recruiter・Hiring Managerは"
    "日々ツールを運用する現場だが導入を決める側ではない、Business Ownerは導入するかどうかを決め、"
    "結果の責任を負う側"
)

EXTERNAL_CONSTRAINT = writer_generic.make_external_constraint(
    evidence_voice_number=4,
    items_text=(
        "[VOICE_4_EVIDENCE 4-01](ニューヨーク市Local Law 144、AI採用ツールの年次バイアス監査・"
        "通知義務)、[VOICE_4_EVIDENCE 4-02](EU AI Actが採用のためのAIを「high-risk」に分類)、"
        "[VOICE_4_EVIDENCE 4-03](Amazonの社内採用AIが女性を不利に評価し中止された事例)。"
    ),
)

THEME_CONFIG = writer_generic.make_theme_config(
    theme_id="editorial_b_voices_3v_generalization_regression_01",
    topic_ja=TOPIC_JA,
    ledger_path=LEDGER_PATH,
    voice_cards=[VOICE_CARD_1, VOICE_CARD_2, VOICE_CARD_3],
    tension_common_ground_value=TENSION_COMMON_GROUND_VALUE,
    tension_asymmetry_value=TENSION_ASYMMETRY_VALUE,
    similar_voices_clarification=SIMILAR_VOICES_CLARIFICATION,
    external_constraint=EXTERNAL_CONSTRAINT,
)
