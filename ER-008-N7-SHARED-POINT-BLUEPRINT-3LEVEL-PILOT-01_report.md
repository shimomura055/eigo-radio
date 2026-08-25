# ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01 完了報告

## 総括

No.7「Assigned Desks Are Back in Some Offices」を対象に、Research→Evidence
Pack/VFL→**Shared Point Blueprint(初回実LLM生成)**→A2/B1 Writer→Fact
Check/Ledger Deviation→Support→TTS(今回のみ同期モード)/ASR→Assembly
という正式Production相当Pipelineを、実際のAPI呼び出しで最後まで実行した。
**B1・A2・Middle(新設)の3種類の完成音声を生成し、比較試聴Artifactを
公開した。**

**結論**: `3-VERSION PILOT READY FOR USER LISTENING`。Shared Point
Blueprintは実LLMで問題なく生成でき、A2/B1 WriterはPoint Oneで完全に
一致するFact構成を選び、Point Twoも必須Factでは一致した(補助的な
Factの選び方に軽微な差異あり、6節参照)。Middle音声は**新規TTS/ASR
呼び出し0件**で、既存の同期TTS音声を組み合わせるだけで完成した。
音声の機械検証は概ね良好だが、A2側2segmentで人間による聴取確認が
必要な箇所を発見した(既知のJA ASR Validator限界の実例、8節参照)。

## 実装状況の要約(推測で「解決済み」としない)

| 項目 | 状態 |
|---|---|
| No.7 Research/VFL | **実施済み**(実Web調査3件、実LLM Evidence Pack/VFL/Verification) |
| Shared Point Blueprint生成 | **実施済み**(初回実LLM生成、schema検証PASS) |
| A2/B1 Writer(Blueprint使用) | **実施済み**(実LLM、fact_id自己申告付き) |
| Structural Validator(Writer段階) | **実施済み・PASS** |
| Support(Comment 3/4、comment_anchor使用) | **実施済み**(実LLM) |
| Structural Validator(Comment段階) | **実施済み・PASS**(ただし自己申告が空配列、9節で解釈を補足) |
| B1完成音声 | **実施済み**(同期TTS、機械検証全PASS) |
| A2完成音声 | **実施済み**(同期TTS、13segment中11 PASS、2件は人間による聴取確認が必要) |
| Middle完成音声 | **実施済み**(新規TTS/ASR 0件、既存音声の組み合わせのみ) |
| 比較試聴Artifact | **公開済み** |
| Production採用可否 | **今回は判断しない**(タスク仕様通り、ユーザー試聴後に判断) |

## 1. No.7 Research / VFL結果

Web検索で実在する3ソースを新規に選定した(Perplexity等の既存Research
Agentではなく、担当者[Claude]がWebSearch/WebFetchで直接調査・検証した):

- **SRC-001**: Bisnow「Assigned Seating Is Slowly, Quietly Coming Back To
  Offices」(2026-06-18、Bisnow New York Office Conferenceの取材記事、
  Scotiabank/iCapital Network/Rudinの発言、HubStar/Genslerのデータ引用)
- **SRC-002**: Korn Ferry「Hot-Desking: Not So Hot with Employees」
  (2023、Mark Royal, Ph.D.ら、hot-desking研究レビューの紹介)
- **SRC-003**: CBRE「2024 Americas Office Occupier Sentiment Survey」
  (2024-08-13、225名の企業不動産幹部への調査)

Evidence Pack(17項目)→VFL(12 Fact、F-001〜F-012)→Verification
(VERIFIED 7件、PARTIALLY_SUPPORTED 5件、NEEDS_EXTERNAL_CHECK 0件、
REJECTED 0件)。所要時間84.5秒。

## 2. 実生成Shared Point Blueprint全文

```json
{
  "point_1": {
    "role": "一部の職場で固定席が戻る背景と、従業員の受け止め",
    "common_claim": "一部の職場では、ホットデスキングへの不満や、固定席のある環境で帰属感と集中を感じやすいという調査結果を背景に、固定席を戻す動きが見られる。",
    "common_fact_ids": ["F-001", "F-004", "F-005", "F-007"],
    "optional_b1_fact_ids": ["F-002", "F-003", "F-006"],
    "required_in_a2_fact_ids": ["F-001", "F-004", "F-005"],
    "comment_anchor": "一部の職場では固定席を戻す動きがあり、固定席のある従業員は、ない従業員より職場への帰属感や集中を感じたと答える割合が高かった。ホットデスキングへの不満には、席の予測しにくさや一貫性の低さなどがある。",
    "prohibited_reference_fact_ids": ["F-008", "F-009", "F-010", "F-011", "F-012"]
  },
  "point_2": {
    "role": "固定席回帰の範囲を示す、企業全体の座席・オフィス運用の動向",
    "common_claim": "ただし、固定席への回帰は企業全体の流れを反転させたものではなく、共有席や柔軟なオフィス運用はなお広く残っている。",
    "common_fact_ids": ["F-008"],
    "optional_b1_fact_ids": ["F-009", "F-010", "F-011", "F-012"],
    "required_in_a2_fact_ids": ["F-008"],
    "comment_anchor": "企業全体では、従業員数に対してデスクが十分にある企業の割合が下がっており、共有席を使う職場はなお一定数ある。したがって、固定席の復活は一部の職場に見られる動きとして捉える必要がある。",
    "prohibited_reference_fact_ids": []
  },
  "point_transition": "従業員の体験や不満が一部の職場での固定席回帰につながっているように見える一方、企業全体の座席運用を見ると、共有席・柔軟なスペースの流れは続いており、固定席回帰は限定的な動きである。"
}
```

## 3. Blueprint API Cost

実測: input_tokens=4,184、output_tokens=1,596、所要17.3秒、モデル
gpt-5.6-luna(Approved Model、`SHARED_POINT_BLUEPRINT`という新規
process名で`er006_model_routing_contract_01.py`のSSOTへ追加した)。
コスト概算(Luna標準単価: input $0.2/1M、output $1.2/1M): 約$0.0027
(約¥0.4)。

## 4. A2/B1 WriterがBlueprintに従ったか

**Point One: 完全一致**。A2・B1とも`point_1_fact_ids_used`が両方とも
`['F-001', 'F-004', 'F-005', 'F-007']`(Blueprintのcommon_fact_idsと
完全に同一)。Writer出力末尾のfact_id自己申告(fenced JSON block)も
問題なく抽出できた。

**Point Two: 必須Factは一致、補助Factの選択に軽微な差異**。両者とも
必須の`F-008`(CBRE比率低下)は使用。B1は`F-009`(2026年予測)を追加
使用、A2は`F-012`(flex space増加)を追加使用。F-012は本来
`optional_b1_fact_ids`(B1のみ使用を想定)に分類していたが、A2が
これを使用した。ただし、この逸脱は(a)Point自体は変えていない
(F-012はcommon_claimの範囲内)、(b)F-012自体はA2でも平易に説明できる
単純な統計値であり、内容の矛盾や難易度の急上昇を引き起こしていない。
根本原因は、`render_blueprint_for_writer()`がA2向けpromptで
`optional_b1_fact_ids`を明示的に「使うな」と伝えていなかったこと
(A2には「required_in_a2以外のcommon_fact_idsは省略してよい」としか
伝えていない)。9節でこの改善余地を記録する。

## 5. Structural Validator結果

**Writer段階**: `validate_topic()`実行結果は`ok=True`(violation 0件)。
4節のF-012の件は、現在のValidator設計では「Point所属自体は正しい
(point_2のまま)」ため違反として検出されない(意図した設計、5節参照)。

**Comment段階**: `check_comment_fact_reference()`実行結果は`ok=True`。
ただし、B1のComment 3・4が申告したfact_idはいずれも空配列
(`referenced_fact_ids: []`)だった。9節で、これが「該当なし(合格)」
と「自己申告メカニズムが機能しなかった」のどちらかを人手で確認した
結果を記録する。

## 6. Point One alignment

**成立**。A2・B1双方が「固定席のある従業員は帰属感・集中力の面で
高い評価を答えた」という同一のcommon_claim・同一4件のfact_idに基づいて
執筆した。表現・情報量は各レベルで独立に最適化されている(B1は
Korn Ferryの解説をより詳しく展開、A2は「Should a desk belong to one
person, or to whoever arrives first?」という平易な二択の問いで導入)。

## 7. Point Two alignment

**必須Factは成立、補助Factの選択に軽微な差異(4節参照)**。両者とも
「固定席回帰は市場全体の反転ではない」というcommon_claimと、CBRE
比率低下(F-008)を中心に置いた。A2が`optional_b1_fact_ids`の1件
(F-012)を追加で使った点は、内容の矛盾やネタバレを生んでいないため
実害は無いと判断するが、Blueprint設計の厳密な運用としては改善余地
として記録する(9節)。

## 8. B1 Comment 1互換性

**互換**。"Listen for what is changing in some offices now and the
question that change raises." は完全に汎用的な聞き取り指示で、A2 Full
Story Part 1(パンデミック後のhot-desking普及と、その見直しの動き)と
矛盾なく接続する。B1本文固有のFact・指示語への依存は無い。

## 9. B1 Comment 2互換性

**互換**。"Some workplaces are bringing back assigned desks after years
of shared seating. As you listen, ask: is this a full return to
personal desks, or are shared desks still part of office life?" は、
A2 Full Story Part 1の内容(固定席回帰の動き)を正しく振り返り、A2
Full Story Part 2の内容(「一方向だけの変化ではない」)への問いかけ
としても正確に機能する。

## 10. B1 Comment 3互換性

**互換**。"For some workers, a regular desk can make the workday feel
different. Shared desks can also feel hard to predict and less
consistent. Next, we will look at two sides of this change." は、
Blueprintのcomment_anchor(Point One分)の範囲に収まっており、A2
Point One本文([帰属感・集中力・予測しにくさ]と一致)とも矛盾しない。
Support Fact Checkでは「can make」がやや因果的表現に聞こえるという
MINOR指摘があった(14節参照、内容自体の誤りではない)。

## 11. B1 Comment 4互換性

**互換**。"Across companies, the share with enough desks for all
employees has gone down, and shared seating is still used in some
workplaces. So the return of assigned desks is a change seen in some
workplaces, not a broad shift across the whole market." は、Blueprint
のcomment_anchor(Point Two分、F-008のみ)の範囲に収まっており、B1
限定Fact(F-009等)への依存は無い。A2 Point Two本文(F-008の同じ
CBRE比率低下)と直接対応する。Support Fact Checkでは「Across
companies」という一般化がやや広いというMINOR指摘があった(14節参照)。

## 12. Key Phrase採用案

**A2の既存推奨(ER-008-A2-STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01)を
再確認し、A2 Key Phraseを採用した**。

| A2 Key Phrase | B1 Key Phrase | 重複 |
|---|---|---|
| hot-desking, assigned desk, full reversal, belong at work, flexible workspace | hot-desking, market reversal, unwanted closeness, mixed picture, quiet comeback | 1/5(hot-deskingのみ) |

B1 Key Phraseの大半(market reversal / unwanted closeness / mixed
picture / quiet comeback)はB1本文固有の言い回しから抽出されており、
Middleで使うA2 Full Story本文には登場しない語も含まれる。A2 Key
Phraseは全てA2本文由来のため、Middleの本文(A2)と一致する。新規
Middle専用Key Phraseは生成していない(非対象事項の通り)。

## 13. Evidence Densityへの影響

Blueprint導入前後で比較する基準記事は無いが(No.7は今回が初回生成)、
以下を確認した: (1) B1本文はPoint Two で3つの独立した数値
(56%→40%低下、およそ3分の1への予測)を含み、Evidence Compression
方針([既存Decision])に反する過剰な圧縮は見られない。(2) B1のWriter
promptにはBlueprintの制約(fact所属)を追加したのみで、Evidence
Compressionや語数・情報量に関する既存の指示文言は一切変更していない。
(3) Fact Check・Ledger Deviationの結果(14節)は、B1がFactを不必要に
Pointへ詰め込んでいる兆候ではなく、既存Production(No.4〜6)でも
同種の頻度で見られる、記事のscope表現に関する通常の指摘だった。
以上より、Blueprint導入によるEvidence Density悪化・不自然な圧縮は
確認されなかったと判断する。

## 14. B1 Fact Check / Ledger結果

- **Writer Fact Check**: verdict=`PASS`
- **Writer Ledger Deviation**: `LEDGER_DEVIATION`、8件(MAJOR 6件、
  MINOR 2件)。全て「調査対象の範囲(米国・カナダ・ラテンアメリカの
  225社等)を超えて一般化した表現」「関連性を因果的に強めた表現」の
  類(例:「the wider market」「a full return across the office
  world」)であり、Ledgerに存在しない新規Factの捏造ではない
- **Support Fact Check**: verdict=`MINOR_FIX`、3件(全てMINOR、15節
  参照)

**既存Productionとの比較**: No.4〜6の生成時点のLedger Deviation件数は
1〜4件(平均約2.5件)、Fact Check verdictはPASS/REVIEW_REQUIREDが
混在していた(6/6levelのうち5levelがREVIEW_REQUIRED)。No.7のB1(8件)
はやや多いが、**内容の性質(scope表現の一般化)は既存Topicと同種**で
あり、Blueprint導入固有の新しい問題ではないと判断する。

## 15. A2 Fact Check / Ledger結果

- **Writer Fact Check**: verdict=`REVIEW_REQUIRED`。実Web検索による
  再検証で、「Scotiabank and iCapital Network are among the companies
  bringing back assigned desks」のうち、iCapital Networkについては
  「rightsizing to optimizingへの移行」という発言のみ確認でき、
  assigned deskへの回帰を明言した根拠は確認できなかった(Scotiabank
  分は確認できた)。また「Korn Ferry says changing desks and nearby
  coworkers can make work less predictable」もやや拡張解釈を含む
- **Writer Ledger Deviation**: `LEDGER_DEVIATION`、4件(全てMAJOR)。
  B1と同種のscope一般化表現
- **Support Fact Check**: verdict=`PASS`(issue 0件)

A2のiCapital Networkに関する記述は、事実の捏造ではなく「複数の
実例のうち1社分の帰属が厳密でない」という**具体的で妥当な指摘**で
あり、人間の編集レビューで容易に修正可能な性質と判断する。

## 16. B1完成音声

- 生成方式: 同期TTS(19節参照)
- segment状況: 13/13segment全てOK(ASR機械検証も全て合格)
- 出力: `er006_output/pool_pilot_01/pool_n7_assigned_desks/b1b/assembled/English_Your_Way_B1B_POOL_N7_ASSIGNED_DESKS.wav`
  (304.4秒、clipping無し、peak 0.915)

## 17. A2完成音声

- 生成方式: 同期TTS(19節参照)
- segment状況: 13/13segment中11 OK、**2件は人間による聴取確認が必要**
  (8節参照): `preview`(status=`ASR_VALIDATION_UNCERTAIN`)、
  `comment_1`(status=`STOPPED`、直近の生成音声ファイルは存在するが
  機械検証未合格のまま採用)
- 出力: `er006_output/pool_pilot_01/pool_n7_assigned_desks/a2/assembled/English_Your_Way_A2_POOL_N7_ASSIGNED_DESKS.wav`
  (304.6秒、clipping無し、peak 0.955)

### 8. 2件の詳細(ER-007の既知の限界の実例)

いずれも**ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01完了報告で既に開示済みの
残存限界**が、今回の新規生成で実際に発生した例であり、Blueprint機構
とは無関係。

- **preview(ASR_VALIDATION_UNCERTAIN)**: canonical「聞き終える**ころ**
  には」に対しASRが「聞き終える**頃**には」と書き起こし、kakasiが
  「頃」を連濁形「ごろ」と誤って読んだ。修正済みの`phonetic_uncertain`
  判定により`ASR_VALIDATION_UNCERTAIN`(Cascade対象)へ正しく分類され、
  Cascadeを尽くしても解決せず(4段階とも「頃」表記で一貫)、
  修正済みの`stop_retrying`短絡処理により**無駄なTTS再生成なく**
  打ち切られたことを確認した(ER-007両修正の実運用での動作確認と
  なった)。実際の音声はTTS入力どおり「ころ」と発話されている可能性が
  高いが、未検証(人間の聴取推奨)
- **comment_1(STOPPED)**: canonical「パンデミックの**あと**」に対し
  ASRが「パンデミックの**後**」と書き起こし、kakasiが「後」を
  「のち」(canonical側の「あと」とは無関係な読み)と読んだ。この
  ケースは濁点/半濁点の関係にないため、ER-007の`phonetic_uncertain`
  修正の対象外(既に「後のあと/のち」として既知の未解決限界として
  記録済み)。`TRUE_CONTENT_MISMATCH`として標準6回・フォールバック6回
  (計12回)のTTS再生成を消費し、最終的に`STOPPED`。最後の生成音声
  ファイルはnarrationディレクトリに残っており、A2完成音声へそのまま
  含まれている。TTS自体は「あと」を正しく発話している可能性が高いが、
  機械検証は一度も合格していないため、**この1segmentは必ず人間が
  聴取確認すること**を推奨する

## 18. Middle完成音声

新設のPilot専用組み立て関数(`er008_n7_pilot_run_01.py`の
`build_middle_timeline_and_assemble()`、Production側の
`er003_v1_n3_01_assemble.py`は無変更)で組み立てた。B1の既存timeline
構造(Charon Comment/Aoede本文の確立済みpause値)をそのまま踏襲し、
本文側の音源をA2の完成音声へ差し替えた。

- 構成: Topic intro・Japanese title(A2) / Preview・Comment 1〜4
  (B1) / Key Phrase 1〜5(A2) / Full Story Part1・Part2(A2) /
  Point One・Two見出し+本文(A2) / In One Line(A2)
- 音量調整: B1のPreview/Comment音源を、A2の本文が使っているtarget_rms
  へ再スケーリングした(新規TTSではなく既存音声の音量調整のみ)
- 出力: `er006_output/pool_pilot_01/pool_n7_assigned_desks/middle/assembled/English_Your_Way_MIDDLE_POOL_N7_ASSIGNED_DESKS.wav`
  (282.5秒、clipping無し、peak 0.955)

## 19. Middle専用Writer/TTS/ASR call数

**0件**。`build_middle_timeline_and_assemble()`は既存WAVファイルの
読み込み・音量調整・連結のみを行い、Writer・Support・TTS・ASRいずれの
API呼び出しも一切行っていない(コード上、当該関数はAPI clientを
一切受け取らない設計にした)。

## 20. Middle追加Cost

**$0(API呼び出し0件のため)**。ローカルでの音声処理(numpy演算・
soundfile書き出し)のみ、所要時間は数秒程度。

## 21. 同期TTS総wall-clock

| 工程 | 秒 |
|---|---|
| Research(Evidence Pack+VFL+Verification) | 84.5 |
| Shared Point Blueprint生成 | 17.3 |
| Writer(B1+A2、Fact Check・Deviation Check込み) | 301.1 |
| Support(B1+A2、Comment・Preview・Key Phrase・Support Fact Check込み) | 218.7 |
| TTS(B1、同期) | 525.9 |
| TTS(A2、同期) | 534.5 |
| Assembly(B1+A2) | 4.0 |
| Middle組み立て | 数秒 |
| **合計** | **約1,686秒(約28.1分)** |

## 22. 同期TTS実測Cost

| 項目 | 実測 |
|---|---|
| Gemini TTS(同期/Standardレート、実測) | $0.5338(約¥85.4) |
| Gemini TTS(同一token数をBatchレートで計算した仮想値、参考) | $0.2669(約¥42.7) |
| OpenAI ASR(English Primary) | $0.0286 |
| Azure(JA Secondary ASR Cascade、4回) | 数円未満(短いsegment×4回、時間従量$1/時間換算) |

同期モードは、既存のBatch実績(約50%オフ)と比較して、今回のTTS部分で
約2倍のコストになった。ただし絶対額としては1 Topicあたり1ドル未満
(¥100前後)であり、DEV/VALIDATION用途としては許容範囲と判断する。
**Production標準は引き続きBatch APIであり、本Pilotの同期モードは
今回限りの検証用であることを明記する**(非対象事項、CURRENT_SPECの
Production TTS標準は変更していない)。

## 23. 3版比較Artifact URL

https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7

B1・Middle・A2の音声プレイヤーと、Preview/Comment 1〜4/Point One/
Point Twoのscript比較(Middle列は各segmentがA2/B1どちらの音声かを
明示するタグ付き)を1ページにまとめた。

## 24. regression test結果

`run_project_regression.py`: **1774/1775 PASS**(1件は既知のharness
自己テスト失敗、実際の回帰ではない)。本タスクで追加した
`er006_model_routing_contract_01.py`の`SHARED_POINT_BLUEPRINT`
process登録も含め、既存テストへの影響は無かった。

## 25. 総API Cost

| 区分 | Cost |
|---|---|
| Luna(Research+Blueprint+Writer+Support+FactCheck、全17呼び出し) | $0.1042 |
| Gemini TTS(同期、Standardレート) | $0.5338 |
| OpenAI ASR | $0.0286 |
| Azure(JA Secondary Cascade、参考) | 数円未満 |
| **合計** | **約$0.67(約¥107 @160円/$)** |

Middle組み立て分の追加費用は$0(20節)。

## 26. 残存Open Item

1. **A2 preview/comment_1の人間による聴取確認**: 17節・8節参照。特に
   comment_1は12回のTTS再生成を経ても機械検証に合格しなかった、既知の
   「後のあと/のち」限界の実例であり、実際の発話内容を人間が確認する
   必要がある
2. **A2がoptional_b1_fact_id(F-012)を使用した件**: 4/5/7節参照。実害は
   確認されなかったが、`render_blueprint_for_writer()`のA2向け文言へ
   「optional_b1_fact_idsは使用しないでください」という明示的な禁止
   文言を追加する改善余地がある(次回以降のPilot/採用判断時に検討)
3. **B1 Comment 3/4のfact_id自己申告が空配列だった件**: 5節参照。
   Comment側の自己申告メカニズムが「具体的な数字を直接引用した場合
   のみfact_idを申告する」という保守的な解釈で動いている可能性があり、
   より広い定義(paraphraseも申告対象に含める等)にするか、現状の
   保守的な挙動を許容するかは、今後のBlueprint運用実績を見て判断する
4. **Fact Check/Ledger Deviationの指摘(14・15節)**: 人間による編集
   レビューが必要(Scotiabank/iCapital Networkの帰属精度、scope
   表現の一般化)。既存Production(No.4〜6)と同水準の指摘であり、
   Blueprint固有の新規問題ではない
5. **Middle組み立てロジックの本格実装**: 今回はPilot専用スクリプト
   (`er008_n7_pilot_run_01.py`)内に実装し、Production側の
   `er003_v1_n3_01_assemble.py`は変更していない。正式採用する場合は、
   このロジックをProduction assembly scriptへ正式に組み込む別タスクが
   必要
6. **同期TTS実行の一回性**: 19-22節で報告した通り今回限りのDEV/
   VALIDATION実行であり、Production標準(Batch API)は変更していない

## 27. Production正式採用の推奨/非推奨

**今回は判断しない(タスク仕様16節の通り)**。ただし、判断材料として
次を記録する: Shared Point Blueprintの中心仮説(「生成前の共通設計で
Point構造の意味的整合性を担保できる」)は、No.7の実LLM検証で
**支持された**(Point Oneは完全一致、Point Twoは必須Factで一致)。
B1 Comment 1〜4は全てA2本文接続時も自然に成立した。Middle音声は
新規TTS/ASR無しで完成した。一方、A2の2segmentに人間による聴取確認が
必要な箇所が残っており(既存の既知課題、Blueprint起因ではない)、
また26節の残存Open Itemがある。次のステップは、比較試聴Artifactを
ユーザーが実際に聴取し、Middle体験の質(12節の評価軸)を判断すること。

## 非対象・完了

Production Level追加、Level名称決定、UI変更、Subscription仕様、
全既存Topicへの展開は決定していない。CURRENT_SPECのProduction TTS
標準(Batch API)は変更していない。完了後STOPする。
