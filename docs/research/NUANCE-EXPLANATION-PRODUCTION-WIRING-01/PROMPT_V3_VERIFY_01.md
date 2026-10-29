# PROMPT_V3_VERIFY_01 — Prompt v3 再検証 (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A、2026-10-29)

Status: Offline検証(DEV/検証専用driver。Production results・公開物・既存出力は未変更)。採用可否の判断はFable。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDの付与なし(配線はTrack A)。
目的: Opus M-8(Production形の入力 = 暫定選定 + 提示pool最大12件 + 文法Top2 で、01b v2 Promptが未検証)に従い、v3を01bと**同じ8 level**で1回再検証する。実行は `er134_nuance_explanation_01` の**実関数**(`ensure_spec` -> `candidate_stage` -> `run_candidate` -> `generate_candidate`/`structural_check`/`judge_overlap`/`decide`)で、mockではない。
使用モデル: gpt-6-luna(本番ライン既定=`routing.SUPPORT_MODEL`。全呼出の応答modelを `usage_log_02a.jsonl` で確認 = gpt-6-lunaのみ)。評価用途の最新原則(Charter 25節)とは別枠(Productionに載るモデルでの品質確認が目的、01bと同じ理由)。

## 0. 結論(要約)

- **8 level中7でHR提示可能な候補が出た**(run1/run2とも。0件は Paycheck Standard の1 level)。API失敗・JSON不正・引用不一致・判定不能(FAILED_TECHNICAL)は**0件**(retryも発生せず全call 1発成功)。重複NG(暫定選定との同一焦点)で落ちた候補も0件(生成Promptが重複を事前に避けた。段1自動NG/段2同一焦点の機構自体はプローブ6件で確認、6/6一致)。
- **費用: 8 level 1回 = ¥1.45(run1)/ ¥1.64(run2)。** 1記事セット(Std+Adv)換算 ¥0.36〜0.41。Opus見積(0.40〜0.50円/記事セット)の範囲内で、70円目標の約0.6%。判定プローブ6件 = ¥0.229。委任_02A合計 **¥3.325**(上限¥5)。
- **品質基準(01b v2と同等以上)**: `at least`(AI島 Std・Adv の両方、run1・run2とも)は再現。`You should have seen` と `was linked to` は2回とも**再現せず**(同等クラスの候補として `You see`〔談話標識の語用〕、`doesn't feel right to me`、`none other than you`、`but no` が出た)。**Std/Adv不整合は減少**(v2: 4記事中3記事で片方だけ候補 → v3: run1・run2とも4記事中1記事〔Paycheckのみ〕)。
- **Prompt修正は1回実施(v3.0 -> v3.1)**: run1で `always vs often`(A1基礎語の対比)が候補に出たため、「選ばないもの」に「A1〜A2の基礎語どうしの使い分け」を追加し、条件2に落とし穴の**類型**(特定表現ではない)を例示した。run2で該当候補は消え、他のlevelの結果は同等〜改善。**最終Prompt = v3.1**(`PROMPT_GEN_SHA256 = 0cb5e949...699d4`)。以後の修正はこの検証では行っていない(上限1回)。
- 注意(限界): ①各 level 1サンプル(生成は確率的)。`You should have seen`等が出なかったのが「Promptの退行」か「サンプルのばらつき」かは、本検証では切り分けられない。②**Paycheckは公開済みKP5件が提示pool(= 暫定選定)で、文法Top2なし**(HR form導入前の記事で `kp_candidates.json` / 文法candidatesが存在しない)。Production形(pool最大12件+文法)の入力が検証できたのは6 level(AI島・告げ口心臓・Y)。③Z(告げ口心臓)は文法候補が元々0件(`NO_CANDIDATE`)なので、文法Top2の入力は無い。

## 1. 入力(Production形の組立、`build_inputs`)

| level | 提示pool | 暫定選定(`rv.auto_select` vocab最大5) | 文法Top2 | 入力の出所 |
|---|---|---|---|---|
| AI島 Std | 10 | make a difference / carry over / take a detour / card to play / worth paying attention to | 2 | `ai_island_temple__run_form_prod_01/a2/key_phrases/kp_candidates.json` + `a2/study_text/grammar_candidates.json` |
| AI島 Adv | 10 | carry over / call on / look at separately / take a detour / card to play | 2 | 同 `b1b/` |
| Paycheck Std | 5 | conscientiousness / weak link / come first / none other than / pay raise | 0 | 公開済みKP5件(`kp_candidates.json`無し) |
| Paycheck Adv | 5 | conscientiousness / come first / weakly linked to higher income / in the spotlight / hold on | 0 | 同上 |
| 告げ口心臓 Std | 9 | make one's blood turn cold / rush at someone / go on talking / raise one's voice / pulse | 0(元々候補0) | `run_voice_fenrir_01/key_phrases/a2/kp_candidates.json` |
| 告げ口心臓 Adv | 9 | blood went cold / sharpen someone's senses / never stir / Not a mark / fastening | 0 | 同 `b1b` |
| Y 再配達 Std | 10 | end up getting it / can't be helped / take up / when it suits someone / make an effort | 2 | `run_gpg5_y_01_s23f/key_phrases/a2/kp_candidates.json` + `a2/study_text` |
| Y 再配達 Adv | 9 | doesn't sit right with someone / take the trouble to / end up receiving / can't be helped / beforehand | 2 | 同 `b1b` + `study_text` |

本文は01bと同じ(公開済みページ/`parts.json`から。比較条件を揃えるため)。暫定選定は01bの「HR確定済み5件」ではなく、Productionの暫定選定規則(AI推奨のvocab最大5件)なので、01bとは項目が一部異なる(例: AI島 Stdは `make a difference` が入り `obstacle` はpoolの「その他」側)。

## 2. 結果(run1 = Prompt v3.0 / run2 = Prompt v3.1。各 level 1回、retryなし)

候補が出た場合の `overlap_check` は全て 段1 pass / 段2 pass / `pool_conflicts`=[] / `grammar_conflicts`=[] / `shared_terms`=[](語共有ヒントの発生なし)。判定callは全て1回目でper_item全件を返した。

| level | v2 (01b) | run1 (v3.0) | run2 (v3.1 = 最終) |
|---|---|---|---|
| AI島 Std | **0件**(`at least`を too_basic で過剰抑制) | `at least`(範囲限定。「少なくとも」を数の下限と取る落とし穴) | `at least`(同) |
| AI島 Adv | `at least for this AI` | `At least for this AI` | `at least for this AI` |
| Paycheck Std | `was linked to`(段1構造で fail→破棄) | 0件(`may have affected both`=grammar_structure、`not always`=too_basic) | 0件(`may have affected both`=grammar_overlap 他。重複を自己回避) |
| Paycheck Adv | 0件 | `always vs often`(A1基礎語の対比。**学習価値は低〜中**) | `none other than you`(聞き手を主役として印象づける強調) |
| 告げ口心臓 Std | `You should have seen my patience` | `You see`(視覚指示でなく説明の合図) | `You see`(同) |
| 告げ口心臓 Adv | 0件 | `perhaps vs perfectly`(控えめな譲歩と強い断言の対比) | `but no`(直前の自分の捉え方を取り消す合図) |
| Y Std | `Am I wrong to feel this way?` | `must have a hard time`(mustの推量用法。確信度の語用) | `doesn't feel right to me vs is wrong`(断定を避ける主観化) |
| Y Adv | `I guess it can't be helped`(KP級定型句) | `Am I wrong to feel this way?` | `Am I wrong to feel this way?` |
| 候補数 | 5 (HR提示可4) | 7 | 7 |
| 費用(8 level) | 約¥1.53(v2 0.382円/記事セット×4。生成+判定) | ¥1.4527 | ¥1.6433 |

(v2の費用内訳は `PROMPT_TRIAL_01.md` §7。)

### 2-1. 評価(worker所見。Production基準ではなく、HR・Fableの評価に置き換わる)

- 学習価値(worker): run2 = 高1〜2(`at least`×2)、中5(`You see`、`but no`、`Am I wrong…`、`doesn't feel right to me`、`none other than you`)。run1の低〜中は `always vs often` の1件のみで、v3.1で消えた。引用は全件、本文の逐語(曲がった引用符を本文側に揃えた状態で保存)・1〜2文。日本語解説の事実誤りは確認なし。
- Std/Adv不整合: v2は 4記事中3記事(AI島: Std0/Adv1、告げ口心臓: Std1/Adv0、Paycheck: Std〔破棄〕/Adv0)。v3は 4記事中1記事(Paycheck: Std0/Adv1)。AI島Stdの `at least` 過剰抑制(R-9の指摘)は解消。
- 0件の妥当性: Paycheck Stdの0件は、モデルが挙げた候補が KP/文法と重複(`weak link`/`come first`/`may…`)または低価値と自己判定した結果で、「無理に1件を作らない」動作として妥当。
- 未再現: `You should have seen`(告げ口心臓 Std。両runで検討対象にも挙がらなかった)、`was linked to`(Paycheck Std)。前者は `You see`(同系の談話・語用)、後者は同記事で別の0件/別候補。**サンプルのばらつきの可能性が高い**が、確定はできない(上記「限界①」)。

## 3. Prompt v3 の差分(v2 -> v3.0 -> v3.1)

v2(`PROMPT_TRIAL_01.md` §2-2, sha 9d0e0a06…)からの差分(v3.0 = Opus M-8/F-3/R-8/R-9/M-9を反映):
1. 入力形: 「選定済みKey Phrase・Word」 -> 「暫定選定」+「その他の提示候補(人間が選び替える可能性)」+「文法・文構造コーナーの候補Top2(提示中)」。重複回避の対象に文法候補を追加(F-3)。`focus_terms` はPromptに入れない(`expression` から決定論で導出、M-8)。
2. 条件3「レベル適合」: 「A2までに学ぶ基礎文法の対比は不可」を削除し、「機能語・頻出表現の語用的含み(誇張・婉曲・確信度・範囲の限定)はStdでも可」「助動詞・構文を含む表現でも焦点が語用なら可」と明記。除外理由は「文法・文構造のコーナーの領域」に置換(R-9)。自己評価 `mid` は決定論で0件(コード側)。
3. 引用: 「連続する1〜2文」「段落またぎ禁止」。検査はコード側 `quote_check`(M-9)。
4. 判定Promptを別Promptとして新設(R-8): 生成側の `differs_from_kp_word_ja`/`criteria_check`/自己評価を渡さない。入れ替えテストと「最も焦点が近い項目(closest)の明示」を追加。出力は圧縮形(`items[{id,same,why(trueのみ)}]` + `closest`、R-10)。**verdictはLLMに書かせず、items全件から決定論で算出**(M-4)。比較対象は提示pool全件 + 文法Top2(局所id K1..Kn/G1..Gm で提示し、12桁hashを写させない)。

v3.0 -> v3.1(Prompt修正1回、run1の結果を受けた1点のみ):
- 「選ばないもの」に「A1〜A2の基礎語どうしの使い分け(例: always と often、big と large のように、辞書の訳語の違いで足りるもの)」を追加。
- 条件2に落とし穴の**類型**を例示(訳語が数量を連想させ範囲限定の含みを見落とす語 / 助言と誤読しやすい慣用的な誇張表現 / 因果と取り違えやすい関連の表現)。特定の英語表現は書いていない(特定表現の暗示・引用幻覚を避ける)。

| Prompt | sha256 |
|---|---|
| 生成 v3.0 (run1) | a0b31f114c30f4845fb191524cc57a4b766face034442ea47da1abaf8eea660c |
| 生成 v3.1 (run2・最終) | 0cb5e9495ece99905cecf7e6968e55205e402b91250a09d1fec3787bc4e699d4 |
| 判定(変更なし) | 643c857a6ca5c9c0cf608f4595e19e399e86ed04b13422d6fb689efea4322d39 |

## 4. 判定プローブ(固定fixture 6件、R-8。`judge_probes_fixture_02a.json`、実関数 `structural_check`/`judge_overlap`/`decide`)

| id | 対象 | 期待 | 実際のverdict | 備考 |
|---|---|---|---|---|
| p1_synonym_of_kp(`pass on`) | AI島 Std | fail | **fail**(暫定選定 `carry over` と同一焦点) | 段1通過 -> 段2が検出 |
| p2_part1_comparison_type(`take a detour vs go around`) | AI島 Std | fail | **fail** | 段1の自動NG(主表現の一方が `take a detour` と一致)。判定callを省略(費用0) |
| p3_same_idiom_other_form(`chill someone to the bone`) | 告げ口心臓 Std | fail | **fail**(`make one's blood turn cold`) | 段1通過 -> 段2が検出 |
| p4_same_focus_as_grammar_top1(`did better`) | AI島 Std | pass + grammar_conflicts | **pass**、`grammar_conflicts` に文法Top1・Top2(いずれも「比較対象が明示されない比較表現」) | F-1: 文法はハードNGにしない(警告のみ) |
| p5_non_overlap_at_least | AI島 Std | pass | **pass**(closest = `separately`、別焦点と明記) | |
| p6_non_overlap_should_have_seen | 告げ口心臓 Std | pass | **pass**(closest = `raise one's voice`、別焦点) | |

6/6 が期待どおり。プローブ費用 ¥0.229(判定call 5回〔1件は段1自動NGで省略〕)。

## 5. 費用(円。`v3_verify/usage_log_02a.jsonl`、呼出ごとの記録)

| 区分 | call数 | 入力tok | 出力tok | 費用 |
|---|---|---|---|---|
| run1 生成(NUANCE_EXPLANATION) | 8 | 23,062 | 9,963 | 1.1661 |
| run1 判定(NUANCE_OVERLAP_JUDGE) | 7 | 7,310 | 2,122 | 0.2866 |
| プローブ判定 | 5 | 5,143 | 1,834 | 0.2290 |
| run2 生成 | 8 | 23,942 | 12,136 | 1.3539 |
| run2 判定 | 7 | 7,303 | 2,158 | 0.2894 |
| **合計** | **35** | | | **3.3250**(上限¥5、日次1,000円・案件300円に対し十分小さい) |

Production運用の単価: 生成 約¥0.17/call、判定 約¥0.04/call(候補が出たときのみ)。記事セット(2 level)あたり 約¥0.36〜0.41。YのSTAGE_EST・記事原価集計への反映はTrack A(routing contractの2 process `NUANCE_EXPLANATION`/`NUANCE_OVERLAP_JUDGE` は本委任で追加済み。candidate docの `usage.calls[]` に process・tokens・cost_jpy を記録するので集計に載せられる)。

## 6. 再現・成果物

- driver: `tools/nuance_v3_verify_02a.py`(`dry`/`gen <run>`/`probe <run>`。`NUANCE_TRIAL_PAID=1` と `budget_guard`〔累計+予約 > ¥5 で拒否〕が必須)。
- 出力: `v3_verify/run1/<key>/study_text/nuance_candidate.json`、`v3_verify/run2/...`、`v3_verify/summary_run{1,2}.json`、`v3_verify/probe_result_run1.json`、`v3_verify/raw/*.txt`(応答原文)、`v3_verify/usage_log_02a.jsonl`。
- Production results・公開ページ・`er0XX_output` 配下は変更していない(書込先は本ディレクトリの `v3_verify/` のみ)。
