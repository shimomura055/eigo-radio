# KP Human Review 候補数の仕様確認(read-only、API 0、2026-10-26)

判定: **(3) 承認済み仕様に曖昧さ・記録漏れがある**(実装不具合ではない。ユーザー認識の「8件固定」は仕様上は「最大8件」)。

## 1. 結果表(AI島 run_ai_01)

| 項目 | Standard(a2) | Advanced(b1b) |
|---|---|---|
| 承認済み候補数 | TOP 8**まで**(上限。下限・補充義務なし) | 同左(Std/Advで規則差なし) |
| 初期抽出数(LLM出力) | 7(call1=3 + call2=4。call2は最大5件の依頼に4件返答) | 7(call1=3 + call2=4) |
| Gate除外数 | 2(validate 1: "too soon to wave a flag"=6語 / canonicalization 1: "studied separately") | 0 |
| 補充数 | 0(補充機構は仕様・実装とも存在しない) | 0 |
| 最終提示数 | 5 | 7 |
| 仕様との一致 | 一致(上限8以内・数合わせ禁止・補充規定なし) | 一致 |

注: 8件に達しなかった第一の原因はGate除外ではなくLLM返答数。Std=7→5(Gate除外2)、Adv=7→7(除外0)。Advが7なのはcall2が4件しか返さなかったため(Prompt 2-Vは「適切な候補が不足する場合のみ5件未満、数合わせはしない」)。

## 2. 承認記録(「8件」の出所と意味)

- ユーザー原文 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md:24` 「学習価値が高い候補を**TOP 8まで順位付きで選定**する」(=上限)。:32 「不自然な表現や学習価値の低い表現を、候補数を埋めるために採用しない」(=数合わせ禁止)。:38 「AIのTOP 8候補をHumanへ提示する」。:187 検証項目「AI候補TOP 8…が仕様どおり選定・保存される」。
- 8件はGate通過後の提示件数の上限(初期抽出数ではない)。「Gate除外で8件未満なら補充」という文言はユーザー原文・DECISION_LOG・CURRENT_SPECのどこにもない(Grep: CURRENT_SPEC.mdに「TOP 8/最大8」該当なし=未反映。DECISION_LOG.md:7はR-1設計決定のみ)。
- Std/Adv差: 候補数規則は同一(KP候補は各レベル最大8)。差はHuman選択数のみ(Std=KP3、Adv=KP3+単語解説5。USER.md:40-43、DESIGN_01.md:74)。
- 変更履歴: 初案DESIGN_01.md:14-18(Prompt 2-R=1 callで最大8)→Opus条件Aレビュー(OPUS_REVIEW_01.md:54「vocabの4〜5件目不足はshortfallとして受容、数合わせのretryはしない」)→Fable決定 DECISION_LOG.md:7(2026-10-25 委任_02、R-1=2 call構成: call1=Prompt 2無変更で3件+call2=Prompt 2-Vで最大5件、DESIGN_02.md:18 M-7c)。この「補充しない/shortfall受容」はFable設計判断で、ユーザーの明示承認文はない(ユーザーは「数合わせ禁止」「TOP 8まで」を承認、補充の要否は未規定)。

## 3. 実装箇所(照合済み)

- `er119_kp_human_review_01.py:49` KP_CANDIDATE_MAX=8(上限。`:48-51`でKP_FINAL_MAX=3,VOCAB=5)。
- `er119_kp_candidates_01.py:180-204` call1(Prompt 2無変更・3件、reason_ja=""固定 :204)、`:191` call2(Prompt 2-V)、`:94`(5件超のみoverflow除外)、`:334` 外側retryは「AUTO採用可能件数<3 かつGate除外あり」のみ(Std=5件でAUTO可5≥3のため非発火。outer_attempts=1)、`:353` `shortfall = 件数<8`をJSONに記録(補充なし)。
- `er119_kp_prompt_2v_01.py:19,26-29` 最大5件・「不足する場合のみ5件未満、数合わせはしない」(sha固定 :35)。
- 実動作: `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/{a2,b1b}/key_phrases/kp_candidates.json`(shortfall=true、outer_retry_log: Std n_candidates=5/n_auto=5/n_gate_dropped=2、Adv 7/7/0。a2は canonicalization_0=INVALIDで"studied separately"を除外し再実行→PASS :work/outer_retry_log.json)。
- Standard 2件除外後に補充されなかった理由: 補充(refill)機構が設計に存在しない(外側retryも「AUTO可<3」のときだけ全体置換)。実装漏れではなく設計どおり。

## 4. 他記事の実績(同一方式の候補数)

| run | Std(a2) | Adv(b1b) |
|---|---|---|
| AI島 | 5(除外2) | 7(除外0) |
| EV R1(X) | 7 | 8 |
| EV R2(X、NG入り) | 6 | 6 |
| EV R3/R4(Z melos、b1b) | - | 4 / 5 |
| Y 再配達 | 4(除外2) | 6(除外1) |
| Y SNS年齢 | 8 | 6(除外2) |

8件に達するのは12レベル中2(EV R1 b1b、Y SNS a2)。多くは4〜7件で、ばらつきは設計(数合わせ禁止・補充なし)の帰結。

## 5. 判定(3)の根拠と最小修正案(実装しない)

実装は承認済み文言(TOP 8まで・数合わせ禁止)どおり。ただし(a)CURRENT_SPECに「最大8・補充なし」の記載がなく、(b)HR依頼書に「最大8件のうち本記事はN件、理由」の注記がなく(shortfallはJSONのみ、request.mdに出ない)、(c)「Gate除外後に補充するか」はユーザー未決。ユーザーが「8件」を期待したのは自然。
- 案A(推奨・費用0): 仕様記録のみ。CURRENT_SPECへ「候補は最大8件・Gate除外/LLM返答不足時も補充せず数合わせしない」を追記+HR依頼書(`render_request` :1190付近)に「提示N件/上限8、除外M件」表示を追加。Prompt/Gate/件数不変。
- 案B(要ユーザー判断、新仕様): Gate除外後に1回補充callを追加(除外句をexcludedに渡し、3+5を満たすまで)。Std 1記事あたり+1 call(推定+0.3〜0.8円/レベル)。ただし「数合わせ禁止」との緊張(LLMがcall2で4件しか返さない事実が示す通り、補充は低品質候補を引き出すリスク)。Prompt 2-V変更(sha固定)や閾値変更を伴う場合はユーザー承認必須。
- 案C: call2の依頼上限を5→7に増やしGate除外を吸収(Prompt 2-V変更=sha再固定・ユーザー承認要)。
影響範囲: X/Z/Y共通核(`er119_kp_candidates_01.py`)。

## 6. 付随: AI推奨KP 1〜3の「AI理由」欄が空欄になる原因

仕様どおりの動作(不具合ではない)。KP 1〜3はcall1(Prompt 2無変更・sha固定)由来で、Prompt 2は理由を出力しない。`er119_kp_candidates_01.py:204`でreason_ja=""固定。理由は4件目以降(call2、Prompt 2-V)のみ。ユーザー原文USER_02.md「選定理由を既存仕様どおり提示」はあるが、call1由来の理由は設計上存在しない(記録漏れ=判定(3)に該当)。最小修正案: (i)依頼書に「(Prompt 2は理由を出力しない仕様)」と明記(費用0、推奨) (ii)理由生成の小call追加(新仕様、ユーザー判断)。

## 7. 保全確認

`py er119_kp_human_review_cli_01.py status --run …/ai_island_temple__run_ai_01` で a2/b1b=pending、grammar_pending=b1b/study_text。候補・本文は変更なし。selectコマンド未実行。API 0・費用0円。
