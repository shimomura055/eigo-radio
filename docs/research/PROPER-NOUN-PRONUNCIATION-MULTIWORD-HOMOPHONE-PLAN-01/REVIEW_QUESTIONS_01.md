# REVIEW_QUESTIONS_01: Fable独立レビュー(+Opus条件A)に判断を仰ぎたい論点

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01 / Status管理ラベル: `PLAN_DRAFT_PENDING_FABLE_REVIEW`
各項目は『Sonnet自己評価(計画段階・実測の裏付け付き)』と『未確定点』。『判断候補』の表記はFable付与前の候補(分類A既判断/B承認範囲内で自己解決/C現タスクと独立/D真に新しい判断、27-3)。

## 1. ユーザー§4の10観点

| # | 観点 | Sonnet自己評価 | 未確定点・根拠の限界 |
|---|---|---|---|
| 1 | 正しい同音表記を十分に救済できるか | 適用域内(片側1語・他方連続2〜3語、全token CMU収録)は救済。保存転写3,493ペアで`byus→buy us`の4ペア全て救済、事前測定ケース30件で期待どおり(`TRIAL_PLAN_01.md`§3)。救えないもの=ASR側が辞書外綴り(`Baias/BAYAS/FAYAS`)・CMU辞書外の名前(Melos等、案A+/B2の領域)・他の内容語差分と共存するもの(M3: 他diffでUNCERTAINのまま) | 実データの該当は**1記事(run_byus_01)由来の6転写**のみで一般化の根拠は薄い。新Primary/Secondaryで多語化の頻度が変わる(ASR依存) |
| 2 | 誤PASSの見逃しリスク最小化 | 判定は『音素列の完全一致』のみで、脱落・追加・近音・数値・否定・OOVは非救済。**新規誤PASS 0**(オフライン)。ラベル付き544転写(ASR 3方式比較Trialの保存分、読取専用)でも判定変化0・問題音声の新規PASS 0。限界効果のあるガードはG5(canonical側3字以上)のみ実証(`ai phone→iPhone`)。G4は実証なし(任意) | (a)土台が『期待発音=CMU綴り発音』で、byus/ai等でCMUが公式/期待と一致する保証はない(**既存の1:1救済と同じ前提**)。(b)ASRがcanonicalに寄せる偏り(PL/promptによるLion→LINE型、K5)は判定側では検出不能。(c)ストレス・リズム・ポーズ（`by-us`の区切り)は見ない(CMUストレス無視は承認済みの1:1と同じ) |
| 3 | #133との統合の合理性 | L1(判定)とL2(供給)を分離し、L1を先行、L2はB2として段階化・条件付き。UDR #133の選択肢では『(イ)現状維持＋案A追加』を推奨(Fable推奨(イ)と整合) | **GitHub Issue #133本文は未確認**(404)。UDR #133との同一性は推定 |
| 4 | 既存Validator・Ledger・retry/fallbackとの整合 | 入口(`homophone_candidate`)の拡張のみ。下流(`_step_alternate_pass`、統一judge、Secondary許容集合、M1、HR、retry、cooldown)は無改変。story-making是正とは適用順で衝突しない(空白差span除外が先)。Ledgerは新規スキーマなし(PNEP V1'-V6とER-23のunconfirmed entry) | Primary単独でPASSする既存の挙動(`cmu_alternate`即時PASS、`sec:946`)を新ルールにも適用する前提(論点Q2)。M1との合成(A+)は未検証 |
| 5 | 発音情報の取得・正規化・管理の信頼性 | Tier表(T0 CMU→T1 英語公式→T2a 辞書→T2b 公開参照データ→T3 JA公式読み[候補のみ]→T4 AI推定[根拠にしない])。登録=PNEP V1'-V6、キャッシュ=Ledger、negative cacheで再調査抑止 | **T2b(Wikipedia/Wiktionary/Wikidata)の有効性は未検証**(本調査ではネット取得をしていない)。Perplexity枠切れ(#134)で調査手段はOpenAI web_search(高コスト)が現実的。negative cacheのTTL(案90日)・保存形式は未決。『信頼できる辞書』にWikipedia系を含めてよいか |
| 6 | より単純で効果的な代替 | 比較した10案(A〜J)のうち、Aが最も単純(純関数1つ＋条件1行)。C(Writer併記)は費用0だがWriter原則の変更、Jは偽NGが残る | もっと単純な案があれば指摘してほしい(例: 期待発音を持たないまま、分かち書き差のspan規則をCMU一致まで一般化する、という本案以上に狭い案は思い当たらない) |
| 7 | Trialケースの網羅性・検証効率 | ユーザー§4の全8種別をケース化(M正例/N負例/F designed audio/R Regression/EX既存の穴/固有名詞以外)。API 0の事前測定を先に済ませ、有料は構成音声48本のみ(約25〜40円)。層A(ASR生)/層B(救済)/層C(最終)の分離評価 | 実音声の誤発音(TTSが実際にBIOS等と読んだ)の自然発生例は少ないため構成音声が中心(3方式ASR比較Trialと同じ偏り)。F0(byUsそのまま)は正解不明の可能性 |
| 8 | 量産単価70円/記事への影響 | 案A: 実行時0円、期待値は再試行削減による微減(0〜0.1円/記事オーダー、発生率0.11%・全て1記事由来のため不確実性大)。B1は11〜16円/記事の悪化見込みで非推奨、B2は期待0〜数円(未測定) | 再試行削減の絶対値は小さく、案Aの価値は『偽NGの種類を1つ消す(予防)』が中心。QCDの『D』『C』への寄与は小さい |
| 9 | Family共通仕様・既存Production経路との整合 | `evaluate_attempt_with_cascade[_detail]`→`val.classify_asr_match`の1経路にFamily X/Z(将来Y)が集約されるため単一箇所の変更で共通化できる(CURRENT_SPEC.md:452、`grep`で呼出元確認)。JA判定は対象外 | KPとBodyでASR構成が異なる場合の挙動はTrial時に別集計 |
| 10 | 過剰な仕組み・検査・費用 | 新規は純関数＋条件1行。ガードは必要最小限(G5のみ実証、G4は任意)。B2は『不一致が実際に起きた語だけ』『CMU収録語は調査しない』で費用を絞る。D/E/F/G/H/Iを不採用 | G4削除、適用域の限定(A-ent)、negative cacheの要否は過剰性の観点で判断を仰ぎたい |

## 2. 論点（Fable/Opusの判断を仰ぎたい）

- **Q1 適用域**: A-all(全語、推奨)かA-ent(固有名詞/造語/Ledger登録語に限定)か。A-allは通常語にも及ぶ(保存語彙で461組が理論上等価、実際の発火はbyusのみ)。A-entは小文字始まり造語(byUs)を拾うために新たな検出規則が必要でOPEN-208(NOT_ADOPTED)と衝突。→ 判断候補U1(D: 新仕様の適用範囲)。
- **Q2 Primary単独PASS**: 新ルールで救済した判定も、既存1:1同音と同様にPrimary単独でPASS(`cmu_alternate`)させてよいか。代替=Secondary確認を必須にする(約2.2円/件・稀)か、PASS_WITH_WARNING相当の事後試聴ラベルを付ける。推奨=既存と同一＋additive audit key。
- **Q3 G4の要否**: 保存データ上の限界効果0。削除して簡素化するか、防御として残すか。
- **Q4 既存の穴(今回の対象外)**: (a)`AI`→`Eye`が`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`でPASS(CMU `ai`代表発音=AY1)、(b)`us`→`u s`・`am`→`a m`が空白差規則でPASS。承認済み仕様どおりの挙動だが、TTSの略語/代名詞の誤読を素通しし得る。11-8の『承認済み仕様との矛盾』ではなく『仕様の範囲内の穴』と判断しているが、Fableの判定を仰ぎたい。→ 判断候補U5(D: 新規の品質判断/仕様変更に当たる)。
- **Q5 stopword脱落の許容**: 既存仕様では`the`等のstopwordの脱落はdiffに数えない(M1の実例で`the→∅`が共存してもPASS)。ユーザー要求『単語の脱落・追加を誤PASSしない』との関係で、本計画は**この既存の許容を変更しない**。変更するなら別仕様(判断候補)。
- **Q6 T2b情報源の位置付け**: Wikipedia/Wiktionary/Wikidataの発音欄を『信頼できる辞書』に準ずる情報源として登録可能(confidence=medium以下)にしてよいか、それとも辞書(Oxford等)と権利者公式に限るか。
- **Q7 J7(byUs)**: 権利者公式の日本語読み「バイアス」を、英語の期待発音(`B AY AH S`)の根拠として認めるか。L1の成立には影響しない。Trialの正例ラベルの根拠のみ(S1/S2)。既存未回答(OPEN-434)。
- **Q8 11-7限定例外の不使用**: Trialまでは隔離で完結、採用後に直接Production実装、でよいか(flag経由の先行配線はしない)。
- **Q9 Opus条件Aレビュー**: 『新しい判定ルールの設計』として、Trial実行前にOpus独立レビューを入れるか。
- **Q10 P2(B2サブTrial)の扱い**: 今回のPLAN_FIXEDに含めるか、#133(イ)を確認した後に切り出すか。
- **Q11 Cap**: P1=JPY100(見積約25〜40円)、P2=別途JPY50(任意、0〜約40円)。7-7上は新仕様のため承認区分。
- **Q12 GitHub Issue #133**: 本文の貼付/対応関係の確認。

## 3. 判断候補一覧(Sonnet付与はしない。分類は27-3のA/B/C/D案)

| ID | 内容 | 分類案 | 根拠 |
|---|---|---|---|
| U1 | 案Aの適用域(A-all/A-ent) | D | 新仕様の範囲設定。CURRENT_SPEC.md:1839の拡張 |
| U2 | 案A自体の採否(VALIDATED後) | D | 『単一語置換差』(CURRENT_SPEC.md:1839)の拡張は承認済み仕様の変更 |
| U3 | J7(byUs公式JA読みの扱い) | D(既存未回答、OPEN-434) | `TRIAL_RESULT_01.md`§9 |
| U4 | UDR #133(ア/イ/ウ)＋本統合方針『(イ)＋案A』 | D(既存未回答) | `USER_DECISION_REGISTER_01.md:318` |
| U5 | 既存の穴(AI→eye、us→u s、am→a m)の扱い | D(仕様範囲内の穴＝品質判断) | `INVESTIGATION_01.md` §2-追加5, §5 |
| U6 | #134(調査手段・Perplexity枠切れ) | 既存未回答 | OPEN-434 |
| U7 | Trial費用Cap(P1/P2) | D(新仕様のTrial=7-7) | `TRIAL_PLAN_01.md`§7 |
| U8 | GitHub Issue #133本文の確認 | C(現タスクと独立、情報提供) | 404で取得不能 |
