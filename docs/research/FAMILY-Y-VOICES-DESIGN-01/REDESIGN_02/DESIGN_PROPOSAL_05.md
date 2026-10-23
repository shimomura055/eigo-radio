# DESIGN_PROPOSAL_05: Family Y「Persona選定・Voice生成」6段階仕様(FAMILY-Y-VOICES-DESIGN-01 委任_13 Phase A / T-2)

Status: `DESIGN_FOR_OPUS_REVIEW`(DEV/Trial専用の設計案。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。API 0・コード変更0・Production変更0・既存`er110_*`変更0。
根拠: ユーザー原文`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_05.md`(§2の6段階、§3の評価A/B/C、§5の検証方針)、原因=`ROOT_CAUSE_02.md`(S1〜S9)。前版=`../REDESIGN_01/DESIGN_PROPOSAL_03.md`・`_04.md`(履歴として残置。本書は工程S1〜S5(Persona設計)と評価をすべて置き換え、S6(Voice Writer)の指定規則を改める。Leakage 13項目・構成・R0は維持)。
本書の工程名はユーザー原文の6段階に合わせ「S1〜S6」と呼ぶ(DESIGN_PROPOSAL_03のS0〜S10とは別体系)。

## 0. 設計方針(ROOT_CAUSE_02の原因S1〜S9への対応)
1. **選定をパイプライン内の独立工程に分ける**(探索 → 主張探索 → 組合せ選定 → 構築)。設計者の手作業にしない(S9)。
2. **探索と選定を分離**し、探索段(S2・S3)は選ばない・評価しない。選ぶのはS4だけ(S1・S4)。
3. **人物から主張を作る**。台帳Factは主張の入力にしない(S3)。世界設定は人物より先に固定し、人物ごとに許される前提の変種も先に宣言する(S6)。
4. **音声・TTS・既出記事の都合を選定に入れない**(S1)。音声の割当は選定後。
5. **人物差は「指定」でなく人物から生じさせる**。骨格順序・締め型の指定を撤去(S7)。
6. **評価A/B/Cは選定時の理由つき自己評価と、事後の盲検判定の両方で使う**(S8)。点数ゲートや新Validatorは作らない。
7. 差戻しを設計の一部にする(S5)。手作業の人物修正は禁止(ユーザー原文§1)。

## 1. 工程の全体像(入出力は構造化出力=JSON schema)
```
S1 世界設定 ─→ S2 当事者の洗い出し ─→ S3 立場×主張の探索 ─→ S4 3 Voiceの組合せ選定
   world_frame     stakeholders(≥8)        claim_seeds(立場ごと3〜4)      trio + 選定理由A/B/C + 反論
                                                                         │
        ┌────────────────── 差戻し(上限あり)────────────────────────┘
        ▼
S5 Persona構築(×3並列) ─→ S6 Voice R0生成(×3並列) ─→ 既存Voice Gate(旧B 7項目) ─→ 構造同型の監視(1回だけ再生成)
   persona_sheet+因果説明          voice_text
   自然さ自己検証 → (adjust/replace) → S3/S4へ差戻し
```
前提・既存資産の再利用: school_phone_banのS1は`TRIAL_03/WORLD_SETTING_01.md`(ユーザー承認済みの世界設定)をそのままJSON化して再利用(API 0)。台帳15件・Perplexity検索結果も再利用。

## 2. 各段階の仕様
共通: 使用モデルは`gpt-6.1-sol`(Production Writerと同じ。25節「最新世代最上位系」。本番ライン採用時のモデル選定は別判断)。Leakage判定は`gpt-6-luna`(M7校正済みの旧B判定器、判定器・定義は不変)。reasoning effortは下記。LLM callはすべて既存`y0.chat`相当の構造化出力。

### S1 世界設定の明確化(①)
- 入力: テーマseed(`topic_ja`)、既存Research台帳(Fact ID・scope[国/地域]・出典)。
- 出力(`world_frame`): `question_ja`(争点を「〜するか」の1文。具体的な規則・行為と、現状からの変化)／`setting`{country, institution_type(例:学校種別)、population(対象者)、era}／`status_quo_ja`(現行の実態。各文に台帳ID or 出典URL)／`shared_premise_ja`(全Voice共通の前提、100字以内、Comment 1にそのまま使う)／`premise_variants`(人物ごとに異なってよい前提[例:全日制/定時制]と、その差が争点に与える影響。**Personaが勝手に発明してはならず、ここで先に宣言**)／`fact_scopes`{domestic, foreign_reference_only, out_of_scope}(台帳Factの区分。外国Factは「国による違い」の対照でのみ使用可)／`distinctions`(混同しやすい区分の定義。例:持込禁止/校内使用禁止/授業中のみ禁止/預かり・返却)／`unverified`(確認できていない点)。
- Prompt要点: 外国の制度を日本の一般的な状況として書かない。実態の根拠が弱ければ争点そのものを見直す(争点の再提案可)。
- 決定論: schema完備、`status_quo_ja`の各文に根拠ID、`shared_premise_ja`に`foreign_reference_only`のFactを使っていない、`premise_variants`が空でも可(空なら「全員同一前提」)。
- 評価(選定時): 「国・制度・対象者の混同がないか」の根拠つき自己点検(`self_check_ja`、3問程度)。
- call: 新題材=1 call(effort high)+Perplexity検索0〜1回(約1.3円、`WORLD_SETTING_01.md` §B-4の実績)。school_phone_ban=再利用で0。

### S2 立場の洗い出し(②)
- 入力: `world_frame`のみ(台帳Factは渡さない)。
- 出力(`stakeholders` ≥8件): `id`、`who_ja`(年齢層・生活/役割を一言)、`contact_point_ja`(**この争点・規則が、その人の日々の何に作用するか**)、`stakes_ja`(得るもの・失うもの・負うもの)、`is_primary`(規則の対象者本人・実施運用者・直接影響を受ける家族/同居者/第三者のいずれか)、`why_would_speak_ja`。`primary_parties_excluded`(主要当事者を候補に入れない場合のみ。`reason_ja`必須)。
- Prompt要点: 「誰がこの争点の当事者になり得るか」を直接の当事者・間接の当事者・制度側・周辺に分けて**最初から3人に絞らず**洗い出す。賛成/反対のラベルは付けない。当事者の型(対象者本人・実施運用者・家族・直接コストを負う第三者・制度設計側…)は**考える観点のヒントで必須の枠ではない**(該当なしは理由を書く)。除外理由に使えないもの: 声・年齢・音声化・既に使った型・記事の都合。few-shotの人物例は与えない(固定化防止)。
- 決定論: 件数≥8、`id`重複なし、`stance`系フィールドが存在しない、主要当事者が(`is_primary`の定義に該当する立場が)1件以上存在し、除外は`reason_ja`あり。
- 評価(選定時、A当事者性): 各立場に「この人が語る自然な理由」(`why_would_speak_ja`)を必須化。点数は付けない。
- call: 1 call(effort medium。広く列挙する段で、選定判断は含まない)。

### S3 立場ごとの主張探索(③)
- 入力: `world_frame`、`stakeholders`。**台帳Factは入力にしない**(事実は`world_frame.status_quo_ja`の範囲のみ。ROOT_CAUSE_02 S3)。
- 出力(`claim_seeds`、立場ごと3〜4件): `claim_ja`(本人の言葉で一文)、`kind`(要求/拒否/不安/怒り/願望/あきらめ/思い込み/自己都合/矛盾した本音/その他。**立場ごとに2種類以上、うち1件以上は自己都合・感情的反発・矛盾のいずれか**)、`origin_ja`(経験・利害・感情・価値観のどこから生じるか、1〜2文)、`rationality`(筋が通る/本人なりの理屈/感情先行/思い込みを含む)、`self_contradiction_ja`(任意)、`factual_risk`(`status_quo_ja`にない制度・統計・事実の断定を含むなら`yes`)。
- Prompt要点: 同じ立場から相反する主張が出てよい。合理的・客観的に正しい必要はない。感情的な反発・自己中心的な願望・思い込み・本人なりの理屈・矛盾を含める。ただし制度・事実を誤って説明する主張は作らない(本人の推測・印象として語れる範囲に限る)。**人物固有の発言(セリフ)は作らない**(後段で固定しすぎない)。
- 決定論: 全立場に3件以上、`kind`の種類数、`origin_ja`あり、`factual_risk=yes`はS4候補から除外(除外件数を記録)。
- 評価(選定時、B主張の必然性): `origin_ja`が立場の`contact_point_ja`・`stakes_ja`に接続しているかの自己点検(`necessity_note`)。
- call: 1 call(effort medium〜high。出力は24件前後)。

### S4 3 Voiceの組合せ選定(④)
- 入力: `world_frame`、`stakeholders`、`claim_seeds`。
- 出力: `candidate_trios`(3組。互いに少なくとも1人は異なる)。各組: `members`{stakeholder_id, claim_id}×3、`reason_A_ja`(当事者性。`contact_point_ja`を引用)／`reason_B_ja`(主張の必然性。`origin_ja`を引用)／`reason_C_ja`(3人を聞くと単独では得られない何が生まれるか。対立・発見・面白さを具体的に1〜2文)／`diversity_note_ja`(視点の多様性。向きの分布が2対1や型の繰り返しになっていないか)／`listener_note_ja`(聞き手の理解しやすさ)／`strongest_objection_ja`(この組合せで「この人がこの主張をするのは不自然」と言える最大の反論と、それでも採る理由)。最後に`selected`(1組)と`why_not_others_ja`。
- Prompt要点: 3軸固定。評価は当事者性・主張の自然さ・視点の多様性・対立の面白さ・聞き手の理解しやすさ。賛成・反対の役割を機械的に割り当てない。2対1に整理できてしまう場合は理由を示す。**単に異なる意見を3つ揃えるための不自然な人物選定をしない**。特定の型(例:家族/現場/第三者)に毎回収束しないこと。事前の候補人物(5候補例・過去記事の人物)は与えない。
- 決定論: 3人の立場が異なる、主張がその立場の`claim_seeds`に属する、`factual_risk=yes`が含まれない、`candidate_trios`が3組で互いに異なる。
- 評価(選定時、A・B・C): 上記`reason_A/B/C`と`strongest_objection`が選定時の評価本体(形式点数なし)。
- call: 1 call(effort high。選定・反証・自己評価を同一callで行う)。

### S5 具体的なPersonaの構築(⑤)
- 入力(Voiceごと別call、3並列): `world_frame`、当該メンバーの立場+主張候補、他2人の主張の一文(重複回避のためのみ)。
- 出力(`persona_sheet`): 年齢・性別・職業/役割・生活(1日の流れ・家族・住環境)・`world_variant`(`premise_variants`のどれか)／この争点との接点／具体的な経験(2つ以内。1つは痛み・失敗)／困りごと／望み(本音と建前の両方)／感情の癖／価値観／利害／矛盾・弱さ／`speech_style`(英訳後も残る特徴: 文長の型、問い返し頻度、断言/留保、語彙層、一人称)／`entry_mood`(語り出す時の心の状態。例:言い訳から/怒りから/戸惑いから)／`claim_core_ja`(この人が言いたいことの芯。**セリフではなく方向性**。固定しすぎない)／`why_this_person_says_this_ja`(この人物の生活・経験・利害から主張が生まれる道筋を3〜5文)。
- 自然さ自己検証(`naturalness_check`、Gateではなく差戻しの判断材料): Q1この人の日常でこの争点は何に作用するか(1文)／Q2この人が別の言い方・別の主張をしそうな点／Q3この主張が不自然に聞こえる最大の理由／判定`natural|adjust_claim|replace_person`。
- 差戻し(§3): `adjust_claim`→S3の同一立場の別`claim_seed`で当該Voiceのみ再実行。`replace_person`→S4の次点の組合せ/立場で当該Voiceのみ再選定(→S5)。
- 決定論: Sheet項目の完備、`world_variant`が宣言済みの変種、数字・実在名が`claim_core_ja`にない、年齢帯の記録(音声の割当は選定後に別判断)。
- call: Voiceごと1 call×3(effort high)。

### S6 一人称Voice(R0)の生成・評価(⑥)
- 入力(Voiceごと別call): `shared_premise_ja`、当該`persona_sheet`のみ(他Voice・台帳Factは渡さない。許容する事実は`persona_sheet`が明示した1件まで)。
- Prompt: 既存`VOICE_PROMPT_TMPL`(`er110_family_y_persona_text_trial_01.py:243-267`)を**新DEV moduleで複製して**下記を変更する(既存ファイルは無変更)。変更点は§6の差分表。要点: 本人として自由に主観的に語る／Research・Factの説明や言い換えにしない／理屈の正しさより「この人が本当にそう言いそうか」を優先／複数の本音が混ざってよい／3人が同じ構造・展開・結びにならない(指定でなく`entry_mood`・`speech_style`で差を出す)。
- 後処理(既存): 旧B Analytical Leakage 13項目の判定器(判定器・定義・Acceptance Gate上限3は不変)。
- 新規の監視(記録+1回だけの是正、新Validatorではない): 構造タグ付け(luna、3Voiceまとめて1 call)で`opening_type`・`closing_type`・展開の型を付け、2人以上で3つがすべて一致したら**当該の後の方のVoice1本だけ**を`entry_mood`を強調して1回再生成。2回目以降は行わず、結果を記録。
- 評価: §4の事後評価。R0のみ(R1/R2は呼ばない)。
- call: Voiceごと1 call×3(effort high)+Gate(luna)+構造タグ(luna)。

## 3. 差戻し・停止条件
- 差戻しは**S5が判定した場合のみ**、1記事あたり合計2回まで(`adjust_claim`1回+`replace_person`1回、または同一種別2回)。差戻し後はS5をそのVoiceだけ再実行し、S4の`reason_C_ja`だけ再評価(1 call、lunaでなくsol)。
- 差戻し上限を超えて自然さが得られない場合は、**手作業で人物・主張を直さず**、工程の原因(S2の幅/S3の探索/S4の基準)を特定してFableへ報告する(ユーザー原文§1・§5(6))。
- S2が8件未満、または主要当事者の根拠なき除外があれば、S2を1回だけやり直し、それでも満たさなければSTOP。
- 有料run: 作業開始時と有料run開始前に`tools/stop_scope_check_01.py`を実行し、rc=3なら停止。再起動はFable委任文が許可した回数のみ。原因不明のrc≠0が2回続いたら即STOP。監督ループ・自動再試行ラッパは作らない。
- 予算: チェックポイント(§8-4)で累計を確認し、上限超過見込みで停止前に報告。

## 4. 評価設計
### 4-1. 選定時の評価(AIの自己評価+理由。工程の一部で、Gateでも点数でもない)
| 評価 | 場所 | 内容 |
|---|---|---|
| A 当事者性 | S2、S4`reason_A_ja` | 各立場の`contact_point_ja`(規則が日々の何に作用するか)と`why_would_speak_ja`。選定理由は`contact_point_ja`の引用必須 |
| B 主張の必然性 | S3`origin_ja`、S4`reason_B_ja`、S5`why_this_person_says_this_ja`・`naturalness_check` | 経験・感情・価値観・利害から主張が生まれる道筋。S5で不自然なら差戻し |
| C 組合せ価値 | S4`reason_C_ja`・`diversity_note_ja`・`strongest_objection_ja` | 3人を聞くと何が生まれるか。2対1・型の繰り返しの自己点検 |
目的: 「理由が書かれていること」ではなく、**理由が引用(`contact_point`/`origin`)で裏付けられていること**を決定論で確認する(欠けたら該当callを1回だけやり直し)。形式的な点数合わせはしない。

### 4-2. 事後評価(盲検・引用つき・3段階)
入力はVoice本文と`shared_premise_ja`のみ(Persona Sheet・設計意図・選定理由は見せない)。判定者: (1)Opus・Fable盲検(Fableが別途opus-consultantへ依頼。主評価)、(2)`gpt-6.1-sol`の盲検判定(補助。生成と同系統のモデルなので偏りの可能性を開示)。
- A'(当事者性): 「この人物が、この争点について語る自然な理由が本文から分かるか」→ あり/やや弱い/なし+根拠引用。
- B'(主張の必然性): 「この人の経験・感情・価値観から、この主張が生まれることに納得できるか」→ 明確/やや弱い/弱い+不自然な箇所の引用。
- C'(組合せ価値、3人まとめて): 「3人を聞いて、単独では得られない対立・発見・面白さがあるか」→ あり/やや弱い/なし+具体の列挙。
- 旧稿比較(school_phone_ban): 旧稿=Trial_03最終稿(`it3/article_ja.md`の3 Voice)と新稿を順序ランダム・ラベルなしで提示。問い:「どちらが実在の人が語っているか」「どちらが説明している感が強いか」「各Voiceの主張に納得できるか」。
- 補助の既存観測(Gate化しない): 主張抽出、聞き分け、抽象語率、感情語、締め型の種類(`er110_family_y_persona_text_trial_01.py`のE系)は記録のみ。主評価にしない。
### 4-3. Phase Bの合格判定(止めどころ。VALIDATED候補の条件でありVALIDATEDの宣言ではない)
- P1 選定の質: 各題材・各runの選定trioが、事後評価で A'=3人とも「あり」、B'=「明確」が2人以上かつ「弱い」0人、C'=「あり」。
- P2 旧稿比較: school_phone_banで新稿が旧稿よりB'で優位(盲検でOpus・Fableが新稿を支持、またはVoice単位で同等以上かつ旧V2・V3相当で優位)。
- P3 再現性: 同一題材をS2〜S4だけ独立に2回実行(§4-4)して、2回ともP1相当の選定理由(`reason_A/B/C`が引用つき、`strongest_objection`に妥当な反論)が得られ、S2の`primary_parties`の網羅が一致する。選ばれる人物が同一であることは求めない(多様性は許容、質の下限が安定することを見る)。
- P4 別題材: 別題材でもP1・P3を満たす。かつ2題材のtrioの「型」(例:当事者本人+家族+周縁、実施者+対象者+管理者)が機械的に同一でない。
- P5 Leakage: 旧B 13項目がAcceptance Gate内(`LEAKAGE_RESIDUAL_STOP` 0)。
- P6 差戻し: 1記事あたり差戻し≤2、手作業修正0。
- 未達の扱い: 工程の原因(S2〜S6のどこか)へ戻り、Prompt/工程を直して再実行(上限はFable判断)。手作業の人物修正はしない。

### 4-4. 再現性の測り方
同一題材(S1固定)でS2〜S4を独立に2回実行(seed固定なし、同一Prompt)。観測: (a)S2の`primary_parties`集合の一致、(b)選ばれたtrioの異同、(c)各回のA/B/C理由の質(引用の有無・反論の妥当性。Opus/Fableが読む)、(d)再現runはS5・S6まで実行しない(費用上の限界。Voice本文レベルのA'/B'は再現runでは測れず、S4の選定理由と`strongest_objection`の質で代替する。この限界は報告で開示する)。**再現性とは同じ人物が選ばれることではなく、質の下限が毎回満たされること**と定義する。

## 5. 別題材検証の候補(検証用途。新規記事ではない。最終選定はFable/ユーザー確認)
学校スマホ(争点の主体=生徒・保護者・学校、規則・制度中心、対象に未成年)と性質が異なる既存題材を3つ挙げる。いずれも既存Ledgerあり、新規Research費用0。
| # | 題材 | Ledger(既存) | 学校スマホとの性質差 | 主な検証ポイント | 懸念 |
|---|---|---|---|---|---|
| (b)推奨 | オフィスの席(固定席かフリーアドレスか) | `er012_output/editorial_b_voices_trial_06/research/verified_fact_ledger.txt`(14件中13 CONFIRMED。日本の会社員が対象。旧B承認の2V記事`editorial_b_voices_a2_free_address_04`あり) | 争点の主体=従業員・管理職・総務(会社の内部)。規則より**生活習慣・価値観・働き方の対立**。当事者がすべて成人でTTS制約が出ない | 「固定席派/自由席派」の二項に収束せず、総務・育児中・在宅併用・新入社員等の主要当事者を拾えるか。旧稿(2V、二項型)との比較が可能 | 旧稿が2Vで型が違う(Voice単位の比較) |
| (a) | パーソナライズされたニュース | `er014_output/four_type_observation_01/voices/research/verified_fact_ledger.txt`(18 VERIFIED) | 争点の主体=個人の読者(消費者)とプラットフォーム。規則なし・習慣と信頼の話 | 規則のない題材でS1〜S4が機能するか | Ledgerの国・地域が日本に限らず、S1(国・地域の明確化)に追加調査が要る可能性 |
| (c) | 企業が採用でAIを使うか | `er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt` | 争点の主体=応募者・採用担当・経営(企業と個人の非対称)。外国制度(NYC/EU)が多い | S1の「外国制度を日本に無批判適用しない」の試金石。旧B承認版が**役割割当型**(応募者/採用担当/経営者、`INVENTORY_OLD_B_VOICES_01.md:66-69`)で比較対象になる | 日本の事情のResearchが薄く、S1で新規検索が必要になる可能性(費用+) |
推奨(b): Ledgerが日本の会社員で完結し新規費用が最小、学校との性質差(組織内・成人・価値観の対立)が大きく、旧稿(二項型の2V)との対比で「当事者の幅広い探索」の効果が見えやすい。(c)は価値があるが費用と不確実性が高く、(b)で不足が出たとき次点。**開示**: 新規記事の作成ではなく検証用途の既存題材の再利用。最終選定はFable/ユーザー確認(判断候補として報告)。

## 6. 旧設計との差分表
| 領域 | 旧(Trial_02/03) | 新(本書) |
|---|---|---|
| 工程 | Persona設計=Sonnet手作業(Arm H)→Sheet→Voice | S1世界設定→S2洗い出し→S3主張探索→S4組合せ選定→S5構築(差戻し)→S6 Voice。全工程がDEV module内のLLM call+決定論 |
| 世界設定 | Persona確定後に検証(争点を人物に合わせて修正) | 最初に固定。`premise_variants`を先に宣言 |
| 候補探索 | 14類型の○△×表(設計者1名、基準に声・Fact) | ≥8立場、除外理由に制作都合を使えない、few-shotなし |
| 主張 | Sheetの`claim`1文を固定。台帳Fact(OECD-02等)が骨格 | 立場ごと3〜4件の`claim_seeds`(感情・自己都合・矛盾を含む)。台帳Factは入力しない |
| 組合せ | 時間・場所の非重複、賛否1:1:1 | A/B/C+多様性+反論の自問。2対1・型の固定を避ける |
| Persona | 属性+主張を支える生活場面 | 利害・矛盾・経験に加え`why_this_person_says_this`と自然さ検証、差戻し |
| Voice Prompt | 骨格順序・締め型を人物別に指定(:254,260)、主張の核は1つ(:256)、ためらい≤1(:258) | 指定撤去、複数本音可、迷い・矛盾は人物が持つ分、「理屈より言いそうか」を優先。人物差は`entry_mood`・`speech_style`から |
| 構造同型 | 指定で防止 | 事後の構造タグ監視+後のVoice1本のみ1回再生成 |
| 評価 | E1〜E14(形式指標)、自己判定「達成」 | 選定時A/B/C(引用つき理由)+事後盲検A'/B'/C'(3段階+引用)+旧稿比較+再現性(質の下限の安定) |
| 差戻し | なし(手作業で1文足す) | S5→S3/S4(上限2)。超えたら工程原因へ(手作業禁止) |

## 7. 撤去・残置(R-P*系の続き)
- 撤去(新DEV moduleに持ち込まない): `closing_type`・`order`のSheet指定と対応するPrompt規則2・8、規則4の「主張の核は1つだけ…締めの一言で主張の核に戻る」、規則6の「ためらいは多くても1か所」、`derive_not_my_point`の「領分」を主張の禁止領域にする使い方(重複回避は他2人の主張の一文を渡すのみ)、`PERSONA_CANDIDATES_01.md`型の手作業候補表。
- 残置: 旧B Leakage 13項目と判定器、Acceptance Gate、数字禁止・実在名禁止、一人称、固定Voice、Fact Safety、R0のみ、4パート構成(Y Trial仕様)。Grepは実装時(Phase B)に新moduleで0件を確認する(識別子: `closing_type`、`order`、`中心となる見方`、`20代以上`)。
- 既存`er110_*`は変更しない。Phase Bの新module名案: `er110_family_y_persona_pipeline_01.py`(+`_run.py`+`_test_01.py`)。Production importなし、flag不要(未配線の独立DEV module)。DefaultOff型testは「他moduleからimportされない・API呼出0でimportできる」確認で代替し、Phase Bで実装時に提示する。

## 8. Phase B計画(次委任。Opus条件Aレビュー後)
### 8-1. 実行
1. DEV module実装+決定論test(API 0)。
2. 並列で2題材×{メイン1回}と、同一題材のS2〜S4再現run(各題材)を実行: school_phone_ban(S1再利用)と別題材(推奨(b))。独立なので別processで並列(出力dirは分離、共有stateなし)。
3. 事後評価: sol盲検判定(補助)を実行し、盲検資料(旧稿vs新稿、ラベルなし)をFableへ渡す(Opus/Fableが主評価)。
4. 結果を`REDESIGN_02/`にまとめず、既存規則どおり`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_04/`配下(新Trial、旧REDESIGNと分離)へ保存(Fable承認時)。
クリティカルパス: S2→S3→S4→S5→S6→Gate≒6 LLM波、各30〜90秒。1記事のテキスト工程は約10〜20分。実装とtestが律速(約1.5〜2時間)。

### 8-2. 費用見積(円。単価の出典=`TRIAL_02_RESULT_01.md` §8、`WORLD_SETTING_01.md` §B-4)
単価の根拠: Voice 1 callの実績4.2〜4.9円(高effort、約300字出力、Voice×3=12.56〜14.61円)、Tension 5.0〜7.4円、Perplexity検索1.3円、luna判定0.1〜1円。S2〜S5の出力が長い段は同一effortで1.2〜1.5倍と仮定(未実測のため幅を持たせる)。
| 段 | school_phone_ban | 別題材(b) | 同一題材再現run(S2〜S4)×2題材 |
|---|---|---|---|
| S1 | 0(再利用) | 4〜5.5(1 call+検索1) | 0 |
| S2(medium) | 3〜4 | 3〜4 | 3〜4 ×2 |
| S3(medium〜high) | 4〜6 | 4〜6 | 4〜6 ×2 |
| S4(high) | 5〜7 | 5〜7 | 5〜7 ×2 |
| S5(high、3 call) | 13〜18 | 13〜18 | — |
| S6(high、3 call)+Gate+構造タグ | 13〜16 | 13〜16 | — |
| 事後評価(sol盲検A'/B'/C'/旧稿比較) | 5〜6 | 3〜4(旧稿比較なし) | S4出力の簡易確認 1〜2 ×2 |
| 小計 | 43〜57 | 45〜61 | 25〜38(2題材分) |
合計: 約113〜156円、中央約135円。差戻し1回の予備(S3+S5+S6の1 Voice分、約10円)を含めて**上限案150円**。Tension+Closing・音声は含めない(Voice単位でA'/B'/C'を評価し、音声化はR0通過後に別途)。**150円を超える場合は事前にユーザー承認が必要**(委任文どおり)。
累計: Family Y Trial 現在約330.3円+Phase A約0円+Phase B 150円=約480.3円。上限600円内で、音声化用の残約119.7円が残る。日次(10-24以降1,000円)は他タスクの当日使用額を作業開始時に`daily_dev_cost_01.py`で確認する。

### 8-3. 費用抑制の工夫(Charter 3)
S2・S3はmedium effort(広く列挙する段)。再現runはS2〜S4のみ。S1はschoolで再利用、別題材も既存台帳。S5を1 callで3 Sheet出力する案はPhase Bの比較対象にしない(独立性と再現性を優先)。Phase B後に実測してS5/S6のeffort・長さを見直す。

### 8-4. チェックポイントと予算管理
累計が80円・120円に達した時点で残工程の見込みを再計算し、150円超過見込みなら**停止する前に**報告する。上限を理由に打ち切らず、超過見込みの報告と推奨を添える。

## 9. 量産への影響(費用・時間)
- 追加される費用: Persona設計がDESIGN_PROPOSAL_03の「Persona Generator 1 call」(推定数円)から、S2〜S5で約25〜35円へ(1記事あたり)。既存の量産推定約100円/記事(`TRIAL_02_RESULT_01.md` §8、目標70円は未達)に上乗せされ、約125〜135円になる見込み(未実測)。
- 原価低減の候補: 台帳Fact選定(B3)をPersona設計と統合、S2・S3を同一callに統合してPhase Bで品質が保たれるか比較、S5の出力項目の削減。いずれもPhase B実測後に検討(品質が先、費用は後。Q>D>C)。
- 時間: テキスト工程の追加は約10〜20分/記事。Gemini batch待ちが律速の音声工程に比べ小さい。

## 10. 承認境界・Production安全性
- DEV/Trial専用。Productionのコード・Prompt・flag・閾値を変更しない。11-7の限定例外は使わない(新コード経路は独立DEV moduleでProductionからimportされない)。
- 新仕様のProduction採用は、Phase BでVALIDATED候補となった後、ユーザーの明示的判断が必要。
- 既存のretry/fallback/Gate(Acceptance Gate、Repetition QA、HR Lock)は迂回しない。Std V1のHR Lockは本設計で触れない。
