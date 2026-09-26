# Natural English Gate: "main idea" 候補の Trial-02 FAIL と run_01 PASS の整合性確認

管理ID: TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(修正1回目、
Fable指摘対応の一環。再生成は行わない、記録のみ)。

## 背景(Fableからの指摘)

Trial-02(`er020_tts_local_rewrite_natural_english_qa_trial_02.py`、
`er020_output/tts_local_rewrite_natural_english_qa_trial_02/qa_results.md`)
では、"main idea" を含む候補(`candidate_main_idea_previous`)が
Natural English Gate で **FAIL** した。一方、本番run_01
(`er020_output/tts_local_rewrite_production_wiring_01/
comment_4_cooldown_local_rewrite_evidence.json`)では、"main idea" を
含む候補(`candidate_3`: "boil it down to the main idea")が同じGateで
**PASS** し、実際に採用された。一見矛盾に見えるため、両方の実際の
Luna判定ログを突き合わせて確認する。

## 突き合わせ結果

| 出典 | candidate_id | 実際の文言(変更後span) | Natural English Gate | 判定理由(Lunaの実際の出力) |
|---|---|---|---|---|
| Trial-02 | `candidate_main_idea_previous` | "bring the main idea together" | **FAIL** | "It is equally natural as the plain point-to-idea swap because it is exactly that swap, but both versions sound unnatural and stilted. A native speaker would more likely say 'sum up the main idea' or 'bring the main idea into focus.'" |
| run_01 | `candidate_1` | "bring the main idea together" | **FAIL** | "'Bring the main idea together' is understandable but not idiomatic in this narration context; native speakers would more naturally say 'sum up' or 'bring the main points together.'" |
| run_01 | `candidate_3`(採用) | "boil it down to the main idea" | **PASS** | "'Let's boil it down to the main idea' is idiomatic and natural in spoken narration." |
| run_01 | `candidate_5` | "distill it into one main idea" | **PASS** | "'Let's distill it into one main idea' is natural and idiomatic spoken English." |

## 結論

矛盾ではない。Trial-02とrun_01の両方で、**同一の具体的な言い回し
"bring the main idea together"(originalの"bring the main point
together"を"point"→"idea"へ単語だけ機械的に置換した形)は、両方の
実行で一貫してNatural English Gate FAILと判定されている**(Trial-02の
Luna判定理由自身が、代替として"sum up the main idea"や"bring the main
idea into focus"を挙げていた)。

run_01で実際に採用されたのは、この機械的な単語置換ではなく、"main
idea"という語自体は保持しつつ、"boil it down to X"という別の自然な
慣用表現でspan全体を言い換えた候補("boil it down to the main idea"、
candidate_3)である。これはTrial-02のLuna自身が示唆した代替案の方向性
(慣用的な言い回しへの言い換え)と整合する。

すなわちQA Gateは「"main idea"という語そのもの」を拒否/許可している
のではなく、「"bring...together"という特定のコロケーションを"point"→
"idea"へ単語だけ置換した不自然な形」を一貫して拒否し、「"boil it down
to"/"distill...into"のような別の自然な慣用表現で"main idea"を使う形」
を一貫して許可している。両Trial/本番runでLunaの判定は一貫しており、
矛盾は確認されなかった。

## 参照

- `er020_output/tts_local_rewrite_natural_english_qa_trial_02/qa_results.md`
- `er020_output/tts_local_rewrite_production_wiring_01/
  comment_4_cooldown_local_rewrite_evidence.json`
  (`result.local_rewrite_recovery.candidates`の各`qa_llm.natural_english`)
