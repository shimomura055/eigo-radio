FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_07-PERSONA-VOICE-REDESIGN-20261023

# 委任_07: Family Y 「Persona→Voice」包括改善Trial — Phase A(根本原因・既存仕様対応整理・Persona/構成/Leakage整合の再設計、Opusレビュー前まで)。API費用0(Persona設計はSonnet自身が行う。LLM呼出不要)。DEV/Trialのみ。

## 背景(ユーザー新指示 2026-10-23)
現行Trial(school_phone_ban)は「3人の立場は違うが主張が曖昧で個性・感情・主観性が弱く、優等生が丁寧に説明する似た文章」。目標=実在しそうな3人が人生・経験・価値観から自然に自分の意見を語る番組。最重要原則=**Persona→Voice**(主張に都合のよい人物を後付けしない。具体的で一貫した人物像から主張が生まれる。各Voice本文は「明確な主張+具体論」+その人らしい主観・感情)。3 Voice固定維持、選定順序=テーマ明確化→当事者を広く検討→3 Persona設計→各Personaの自然な主張→明確・非重複・聞く価値の組合せに調整。教師・親・生徒など主要当事者を検討(予算担当者は排除しないが明確で興味深い主張が必要)。中学/高校・年齢・生活環境の整合。Research is backstage=調査事実の排除ではない(本人が知っていそうな事実を自然に使う。件数目的化しない)。Leakage Checkが主観発言への事実織込みを妨げていないか確認し検査と設計の矛盾を解消。番組構成: Comment 1=テーマ導入(人物説明なし)/Comment 2=Voiceへの導入(人物紹介繰返しなし・Comment 1と重複なし)/各Voice直前にナレーターが短い見出し(例 `One Voice: The desk that lets work begin`)/Voice 1-3一人称/Tension+Closing 1パート(具体的に違いを整理、抽象化しすぎない、一度聞いて理解できる、無理な結論・教訓なし)。**R0のみ**(R1/R2比較不要・将来R工程は未決定・既存R1/R2は削除変更しない)。Trial→VALIDATED、採用はユーザー試聴後。費用上限は独断拡大しない。**原文を保存して全文読むこと。**

## T-0
1. **ユーザー指示原文を逐語保存**: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新userメッセージ(「# Claude Code / Fableへの指示 ## Family Y — Voice設計・構成・人物表現の包括改善Trial」)を `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_03.md` へ無改変保存。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_07.md`(index 353以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行: ASR-QUALITY PN/UKUS、FX-KP-GM の3 agent。`er111_*`/`er112_*`とそのdocs不可触)。OPEN-463 Status=`REDESIGN_PERSONA_VOICE_IN_PROGRESS(ユーザー指示2026-10-23 USER_03)`。UDR #167は「本指示で上書き(R0/R2比較・R2 Adv take承認は不要化、Std減速の有無は新Trialページで再判断、事実0件化の方針は本Trialで検証)」と追記。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 1. 根本原因(既存Trialで品質が不足した理由、証拠付き)
- 現行Y Writer(`er110_family_y_text_trial_01.py`、DESIGN_PROPOSAL_02、Voice Card仕様、M1〜M7)のPrompt・Voice Card構造・Gate(Leakage Check/`leak_evidence_subject`/局所書き換え/Acceptance Gate/RF)・B3/Research投入を読み、(a)Voice Cardが「属性リスト」で、経験・感情・価値観・話し方が主張に接続されていない、(b)Prompt制約(数字禁止・取材表現禁止・Leakage回避・5段落契約・語数)が「安全で丁寧な語り」を誘導、(c)Leakage判定が本人の知識としての事実まで消す(M1衝突、OPEN-470)、(d)R0→R1→R2が面白さの表層(比喩)だけを足した、(e)5パート目の抽象化、等を実データ(gate_r0/gate_r2の article_before_judgement、Leakage flag一覧、書き換え差分)で裏付ける。過去のFamily B Voices(旧3V記事)での同種指摘・ユーザー実検証コメント(「最後の段落の抽象化は耳で理解しづらい」)をSSOT/HISTORYからGrepして引用。

## 2. 既存承認仕様と今回改善事項の対応表
CURRENT_SPEC(Family Y節・Family B Voices旧仕様・Comment構成・Voice見出しに相当する既存仕様の有無[Zの話者見出し/Xのcomment role等]・ナレーターRole・Std減速・Leakage Check・Acceptance Gate・3 Voice固定・独立Closing廃止U3・Voice固定割当)・DESIGN_PROPOSAL_02・過去Trial(Family B/Y)を照合し、各改善事項が「承認済み仕様の範囲内/変更が必要(ユーザー判断)/Family固有/未承認候補」のどれかを表にする。特に: Comment 1/2の役割分担(現行の5パート `full_story_part1〜5` との対応: part1導入をComment 1/2へ分割するのか、Comment segmentを再導入するのか=segment-id parity M3・reuse key M4・ページ生成・TTS Roleへの影響)、Voice見出しの音声Role(ナレーターAoede、短文、TTS/ASR検査の扱い、X/Zの既存類似仕様)、Tension+Closing(DESIGN_PROPOSAL_02 L196の設計を維持しつつ具体化の規則)、R0のみ(R1/R2 DEV runnerはそのまま、呼ばない)。

## 3. 再設計(DESIGN_PROPOSAL_03、Opusレビュー対象)
- **Persona設計手順**の仕様化(ユーザー§3の5段階を工程に落とす。Persona Sheet項目=年齢/職業/生活環境/家庭・学校との関係/過去の経験・現在の悩み/価値観/性格・感情表現・話し方の特徴/テーマに何を感じなぜそう考えるか/「この人だからこそ語れること」/自然に生まれる主張(1文)+具体論の種(2〜3)/本人が知っていそうな事実(Research Ledgerから、任意0〜2件)。主張の後付け禁止の自己点検項目)。
- **今回テーマの3 Persona案**: Sonnetが当事者マップ(生徒[中/高・通学形態]、保護者、教師、養護教諭、部活顧問、塾、スクールカウンセラー、通信/定時制、PTA、自治体…)を作り、3人を選定(選定理由・却下理由付き、年齢・学校種の整合[中学か高校かを明示]、主張が明確・非重複・聞く価値)。例示(働きながら通う生徒=仕事連絡の切実さ)は固定指示ではない。Voice固定(V1=Algieba男性的/V2=Zephyr女性的/V3=Schedar男性的)との性別・年齢感の整合も考慮。
- **Voice本文Prompt(R0)の再設計**: 「主張+具体論」を骨格に、主観・感情・話し方の差(語彙・文長・口調・ためらい/断定)をPersonaから導く。優等生化を防ぐ具体規則(抽象語の上限、具体場面1つ以上、感情語の自然さ、芝居・誇張禁止)。数字・取材表現の既存制約は維持しつつ「本人が知っていそうな事実」の許容規則(M1改訂案)を定義。
- **Leakage Check整合**: `leak_evidence_subject`等の判定が「Persona Sheetで許容された事実(本人の知識として自然)」をflagしない例外設計(OPEN-470 ア/イ/ウのうち本Trialで検証する案を1つ推奨、理由)。検査の安全性(Research断片の無自覚な漏出=本来のLeakage)は維持。
- **構成**: Comment 1(テーマ導入、人物説明なし)/Comment 2(Voiceへの導入、重複なし)/見出し×3(形式 `One Voice: …`/`Second Voice: …`? 表現形式はOpusと合わせ決める。短く興味を引く、ナレーターAoede)/Voice×3/Tension+Closing(具体的整理・非抽象・一聴理解・結論強制なし)。segment構成・Role・TTS/ASR/減速/ページ表示の設計(M3/M4への影響)。Std/Adv英語化はR0本文から既存経路。
- **評価基準**(Opus/Fable/ユーザー試聴用): Personaの実在感、主観性、主張の明確さ(聞けば一文で言える)、具体性、3Voiceの差(語り口・思考・感情)、音声での理解しやすさ、事実の自然な織込み、Leakage 0、芝居・誇張なし。数値化できるもの(抽象語率、具体場面数、感情語、文長分散、主張文の有無)と目視項目。
- **費用見積**: R0(日本語)+Leakage/Gate+英語化Std/Adv+音声(Std/Adv 1候補)+ページ。Family Y Trial上限250円の残74.62円内に収まるか(収まらなければ最小構成案と差額を明示。独断拡大しない)。反復1回あたりの費用。

## 4. 成果物
`docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_01/{ROOT_CAUSE_01,SPEC_MAPPING_01,DESIGN_PROPOSAL_03,PERSONA_CANDIDATES_01,OPUS_REVIEW_REQUEST_01}.md`。commit/push(明示add、secret_scan hits=0)。

## 5. 禁止
LLM呼出・音声生成(Phase Aは0円)、Production(X/Z)変更、R1/R2の削除・変更、`er110_*`の実装変更(設計のみ。実装はOpus後の次委任)、他agentファイル編集、費用上限拡大。

## 6. 報告(docs/pm/RESULT_PACKET_FYT4.md)
(1)根本原因(a)〜(e)と証拠 (2)仕様対応表の要約(ユーザー判断が必要な項目の明示) (3)3 Persona案と選定理由 (4)構成・Prompt・Leakage整合の設計要点 (5)評価基準 (6)費用見積と残予算 (7)Opus論点 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。