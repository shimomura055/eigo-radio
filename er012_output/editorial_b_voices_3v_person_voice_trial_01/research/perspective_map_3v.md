# Perspective Map(3V版)— EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01

テーマ固定: "Should companies use AI to screen job applicants?"(4V Trial-01/02と同一)。

## 0. 本Trialの前提(ユーザー決定、2026-09-09)

4V Trial-01/02で、Business/Efficiency(旧Voice 3)・Legal/Fairness(旧Voice 4)の
Analytical Leakage(特にDiscovery型逆戻り[leak_discovery_syntax])が
MAX_WRITER_ATTEMPTS(3)まで解消しなかった。原因仮説: この2 Voiceが「具体的人物」
ではなく「抽象的な分析軸(効率性/合法性)」として設計されていたため、Writerが
Research/EvidenceをVoiceの人物の経験・責任として語らず、数値・ROI・制度・規制の
解説文に戻った。本Trialはこの仮説を検証するため、**Voice設計そのものを4Vから
3Vへ変更する**(新しい語り口指示・Prompt強化ではなく、人物設計の修正のみ)。

3 Voices(いずれも「その立場からIで語れる具体的な人物」):
1. **Voice 1: 仕事に応募する一人の人(Applicant)** — 4V Voice 1をそのまま継続
   (既に「一人の人」として成立していたためVoice設計自体の変更なし)。
2. **Voice 2: 採用担当者/Hiring Manager(Recruiter/Hiring Manager)** — 4V Voice 2を
   そのまま継続(同上)。
3. **Voice 3: 経営者(Business Owner)** — 4V Voice 3(Business/Efficiency、抽象的な
   「効率性の立場」)を、**採用コスト・速度・会社運営・結果に実際に責任を持つ
   一人の経営者**として再設計する(本Trialの中心的変更点)。

4V Voice 4(Fairness/Legal/HR Governance)は、本Trialでは独立したVoiceとして
描かない。理由: Fairness/Legal/HR Governanceは、それ自体が「その立場からIで語れる
具体的人物」というより、応募者・採用担当・経営者という3者それぞれの合理性の外側に
存在する制度的制約(fairness/bias/accountability/law/compliance)であり、3者の
合理性を単純に足しても答えにならないことを示す構造材料として、**Tension/Closing側の
統合・制約材料**へ位置づけ直す。Ledger本体は改変せず、旧`VOICE_4_EVIDENCE`タグの
factをそのまま引用し、本Trialのマッピング上では便宜的に「Tension Constraint
Evidence」と呼ぶ(Ledgerファイル自体にはこのタグを新設しない)。

## 1. Voice別マッピング表(Ledgerタグ→3V配置)

| Ledgerタグ | 4V配置 | 3V配置 | 変更内容 |
|---|---|---|---|
| `[VOICE_1_EVIDENCE]`(Applicant) | Voice 1 | **Voice 1(point_one)** | 変更なし、そのまま継続 |
| `[VOICE_2_EVIDENCE]`(Recruiter/HM) | Voice 2 | **Voice 2(point_two)** | 変更なし、そのまま継続 |
| `[VOICE_3_EVIDENCE]`(Business/Efficiency) | Voice 3 | **Voice 3(point_three)** | **人物として再フレーム**(「効率性の立場」→「採用コスト・速度・会社運営・結果に責任を持つ一人の経営者」。同じevidenceを、経営者本人が下した判断・背負う結果として使う) |
| `[VOICE_4_EVIDENCE]`(Fairness/Legal/HR Governance) | Voice 4 | **Tension/Closing統合(独立Voiceなし)** | Voiceとしては使わない。Tension本文内で、3者の合理性を制約する外部要因("Tension Constraint Evidence")として本文中に引用する(Fact Checker A'のVoice帰属opt-in免除の対象外、通常どおり出典的整合性が問われる) |
| `[CROSS_REFERENCE]` | Hook/Tension/Closing横断 | 同左 | 変更なし |

## 2. Voice Card(3人物版、一人の人として成立させる)

### Voice 1: Applicant(応募者)— 変更なし

4V Voice 1と同一の人物像(Ledger 1-01〜1-05に基づく)。AIによる動画面接評価で
身振り・表情を理由に不採用になった経験([VOICE_1_EVIDENCE 1-03])、AIによる
「信頼性スコアリング」を拒否できないまま受けさせられた経験([VOICE_1_EVIDENCE
1-04])を持つ、一人の求職者。守りたいもの: 自分の実力・人柄を正確に見てもらうこと、
不採用の理由を理解し納得できること。得るもの: 公正に評価される機会。失うもの:
理由の分からないまま選考から排除されること。

### Voice 2: Recruiter/Hiring Manager(採用担当者)— 変更なし

4V Voice 2と同一の人物像(Ledger 2-01〜2-05に基づく)。履歴書スクリーニング・
面接日程調整・求人票作成などでAIを日常的に使う一人の採用担当者。NBCUniversalの
ような大手雇用主が独立監査を実施している実例([VOICE_2_EVIDENCE 2-04])を知り
ながら、日々「使えば便利だが、応募者の不信にも応えなければならない」という
板挟みの中で判断している。守りたいもの: 効率的に仕事を進める能力と、それに伴う
説明責任を同時に果たすこと。得るもの: 大量の応募を裁ける仕組み。失うもの:
応募者からの信頼、説明責任を果たせなかった場合の現場としての立場。

### Voice 3: Business Owner(経営者)— 本Trialで再設計

- Who: 中堅企業の経営者、または採用の最終責任を負う事業責任者。**「効率性」
  という分析軸ではなく、採用にかかるコスト・速度・会社の存続そのものに、
  自分個人の判断として責任を負う一人の人**。
- Situation(状況): 毎週、採用にかかっている日数・コストのダッシュボードを見て、
  AIツールを導入し続けるかどうかを自分の判断で決めている。
- Need(必要としていること): 事業を回すのに十分な速さ・規模で人を採用し続ける
  こと、コストを持続可能な水準に保つこと。これは抽象的な「効率」ではなく、
  会社が存続できるかどうか、自分がその責任を果たせるかどうかという個人的な
  賭け金である。
- Concern(心配していること): 効率化のメリットを享受する一方で、もし差別・
  偏りが公になれば、矢面に立つのは自分自身であり、会社の評判・訴訟費用・
  自分自身の信用を失うリスクを背負っていること。
- What they protect(守りたいもの): 会社が採用をスケールさせ続けられる能力、
  自分が下した判断への信頼、会社の存続そのもの。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、業種・
  規模の異なる複数の企業(ホテルチェーン、ITベンダー、クラウド企業)で、
  AI導入後に採用期間が数週間から数日へ大幅に短縮された、あるいはコストが
  大きく下がったという事例を見て、自分も同様の判断を下した、あるいは
  下そうとしている。同時に、AIによる採用選考が差別を引き起こしうるという
  懸念が既に広く報じられていることも知っており、それが自分の会社で起きた
  場合の結果を具体的に想像している。
- Constraint(制約): 法規制の詳細を自分で作る立場でも、応募者の不信を直接
  和らげる立場でもないが、「AIを導入する/使い続ける」という決定そのものを
  最終的に下すのは自分であり、結果の責任は自分に返ってくる。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 採用担当者から
  「今月も期限内に必要な人数を採用できた」という報告を受けて安堵する一方、
  他社のAI採用ツールが差別を理由に訴えられたというニュースを見て、自分の
  会社は大丈夫かと考える。resource: [VOICE_3_EVIDENCE 3-01](ホテルチェーンの
  採用期間が約6週間から5日間へ短縮、IBMの採用コスト30%削減)、
  [VOICE_3_EVIDENCE 3-05](差別が生じた場合の倫理的・法的リスクと評判への
  ダメージ、経営層が天秤にかける必要があるという指摘)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): 企業の57%が
  既にAIを採用選考で使用し、74%がAIによって採用の質が向上したと回答
  [VOICE_3_EVIDENCE 3-04]。

**再設計の要点**: 4V版では「Business・Efficiency」という立場そのものが主語に
なりやすく(「効率化は良いことだ」という分析軸)、Discovery型逆戻り(調査結果の
整理)を誘発しやすかったと考えられる。3V版では、同じevidenceを「一人の経営者が
下した判断・背負う結果」として再構成し、Voice Cardの主語を常に「私(経営者)」に
固定した。

## 3. 外部制約(Tension/Closing統合、独立Voiceとしないもの)

旧Voice 4(Fairness/Legal/HR Governance)のevidenceは、3者それぞれの合理性を
制約する「外部からの力」として、Tension本文内で扱う(独立した見出し・独立した
Voice本文としては書かない)。

- [VOICE_4_EVIDENCE 4-01]: ニューヨーク市Local Law 144(AEDTのバイアス監査・
  通知義務)。
- [VOICE_4_EVIDENCE 4-02]: EU AI Actが採用AIを「high-risk」に分類。
- [VOICE_4_EVIDENCE 4-03]: Amazonの社内採用ツールが女性を不利に評価し中止
  された事例。
- [VOICE_4_EVIDENCE 4-04]: HireVueが生体情報プライバシー法違反で375万ドルの
  和解に応じた事例。
- [VOICE_4_EVIDENCE 4-05]: 日本にはまだ同等の法規制が存在しない。

これらは、応募者(公正に見てほしい)・採用担当(効率と説明責任の両立)・経営者
(会社を回し続けたい)という3者それぞれの合理性を単純に足しても、「AIを
どう使うべきか」の答えにはならないことを示す構造材料として使う。3者の外側に、
監査・訴訟・法規制という具体的な力が既に存在し、それが3者それぞれの選択肢を
現実に制約している、という描き方をTensionで行う(要約・解説ではなく、3者の
賭け金・非対称性を制約する力として統合する)。

## 4. Fact Checker A'(opt-in)スコープの扱い

Voice帰属opt-in免除ルール(`registry.VOICE_ATTRIBUTION_RULE_TEXT`)は、本Trialでは
`[VOICE_1_EVIDENCE]`〜`[VOICE_3_EVIDENCE]`のみを対象にVoice attribution blockを
構築する(Trial側で`[VOICE_4_EVIDENCE]`ブロックを除去したledger断片を
`registry.build_voice_attribution_block()`[Production、無変更]へ渡す)。
Tension本文で`[VOICE_4_EVIDENCE]`由来の事実(NYC LL144・EU AI Act等)を扱う際は、
Voice本文ではなく地の文(Tension)であるため、そもそもVoice attribution免除の
対象外(`registry.VOICE_ATTRIBUTION_RULE_TEXT`が明記する既存の除外規定どおり)。
Ledger Deviation Checker(`vfl01.run_deviation_check`)へは、Fact Attribution
blockとは別に、**Ledger全文(VOICE_4_EVIDENCEを含む、無改変)**を渡す(Tensionの
制約Evidenceの正確性を検証するため)。

## 5. Perspective Diversity Check(3 Voice間の重複・偏りの確認)

- Evidence件数: Voice 1=5件(1-01〜1-05)、Voice 2=5件(2-01〜2-05)、Voice 3=
  5件(3-01〜3-05)。1者だけが突出して厚い状態にはなっていない(4Vと同一Ledger
  評価を継続)。
- 賛否2対1の対称構造になっていないか(3V-a型構成の既知リスク、design.md
  `EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03`の
  3V-a行が警告する「Applicant 1 vs Recruiter+Business 2」という2対1の陣営化
  リスク): 本Trialはこのリスクを、Recruiter・Businessを削って統合する対応
  ではなく、**外部制約(fairness/bias/accountability/law/compliance)をTension
  へ組み込むことで、3者の合理性が単純加算では答えにならない**という構造を
  明示することで緩和することを狙う(この狙いの成否は評価項目5・6で検証する)。
- Recruiter/HMはApplicantに最も近い「現場」の視点であり、Businessとは異なる
  次元の負担(応募者の不信に日々応える実務)を負っている点をVoice Cardに
  明記し、Recruiter=Business側の単純な同盟に見えないよう設計した。

## 6. 結論

3 Voice(Applicant/Recruiter・Hiring Manager/Business Owner)は、いずれも
「その立場からIで語れる具体的人物」として再設計され、旧Voice 4(Fairness/
Legal/HR Governance)はTension/Closing側の外部制約材料として統合した。
この設計変更が、Business Voiceの人物化によってAnalytical Leakageを改善
させるかは、次段階のWriter実行(本Trialの主内容)で検証する(結論はこの
時点では出さない、Trial入力資産としての設計整理まで)。
