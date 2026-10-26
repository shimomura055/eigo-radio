# DESIGN_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26) — API実行前に固定

Status: Trial(到達上限 VALIDATED / REJECTED / 判断候補)。Production(Prompt・選定ルール・Gate・Human Review・候補数仕様)は変更しない。

## 1. 方式(採用: P7→W3 の2 call直列)
- call1 = **P7**(フレーズ・表現・イディオム、2語以上、最大7件・順位付け・理由)。call2 = **W3**(単語単体1語、最大3件・順位付け・理由。入力にP7のGate通過句を「すでに選ばれた表現」として与え、学習価値の重複を避けさせる)。
- 現行方式(比較対象)= Production `er119_kp_candidates_01.generate_candidates` の既定(call1=Prompt 2で3件 + call2=Prompt 2-Vで最大5件 = 要求最大8件)。
- Trial方式は `generate_candidates` に **select_fn(call1相当=P7)** と **vocab_call_fn(call2相当=W3)** を注入するだけで、以降の処理
  (選定段gate・canonicalization[LLM]・gloss再整合・CMU post-canon・記号・[Z]人称整合/SRC D1・Human NG・Redundancy QA)は **Productionコードそのまま**。
  外側retryのみ `max_outer=1`(候補list全体の置換を避け、Gate除外を素のまま測るため。Production既定は3。Productionが外側retryを発火する条件[AUTO<3かつGate除外あり]に該当した場合は結果に旗を付ける)。
- 合体1 call変種(P7W3を1 promptで両枠要求): **本Trialでは実行しない**。理由=(1)「フレーズ側が単語に引きずられる/単語側がフレーズ重複を避けられない」影響を分離して説明しにくく、現行(2 call直列=call1→call2に既存フレーズを渡す構造)との比較可能性が下がる (2)2 call直列のcall数は現行と同数(2 call)で費用差が出ない (3)必要十分な品質が確認できれば追加Trialを行わない(Charter 1)。必要になれば後続判断。
- 反復: 各level × 2回(同一Prompt・同一モデル gpt-6-luna・temperature既定)。現行方式のfresh baseline(AI島以外)は各level 1回。

## 2. モデル(PM_GOVERNANCE 25節)
- 候補生成(P7/W3/canonicalization/gloss/RQA)= `gpt-6-luna`(Production SUPPORT_MODEL。`er105.SELECTION_MODEL_ID`/`er006` routing。比較条件統一のためProduction現行モデルを使用。最新世代最上位ではないが「現行方式との比較条件統一」が明確な例外理由)。
- LLM judge = `gpt-6.1-sol`(リポ内で使用中の最新最上位系。`er006_model_routing_contract_01.py` FAMILY_X_STORYLINE_B3等、pricing_snapshotに単価あり)。reasoning effort=low。judge結果は単独の合否根拠にしない。

## 3. 入力本文(Production候補生成が受け取るのと同じ本文)
- X: `{source_dir}/{lv}/article.md` をそのまま(er019_family_x_audio_production_runner_01.py:740 `load_text`、:801 `run_kp_with_review(text=article_text)`)。
- Z: `canonical_article_text(w62.rd(writer/std.md|r2.md))`(er026_family_z_fiction_production_runner_01.py:1296,2011)。
- 本文の同一性: 既存のProduction selector prompt内の本文と`==`で一致を確認済み(`current_baseline_01.json` の `prompt_body_equals_text`/`formal_3kp_prompt_body_equals_text`=True、全6 level)。
- 対象: 3記事 × a2(Standard)/b1b(Advanced) = 6 level。AI島=er019_output/ai_island_temple/run_ai_01、英国電車マナー=er019_output/uk_train_speaker_playback/run_nws_02(正式run=uk_train_speaker_playback__run_nws_02)、
  猿の手(Z)=er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01(CLOSED_USER_PASS、CLOSEOUT=docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/CLOSEOUT_01.md。Zのレベル構成はa2=Standard[std.md]/b1b=Advanced[r2.md])。run_fzcw_e1_01(STOP残置)は不使用。

## 4. 単語/フレーズの判定基準(事前固定)
- 判定対象は canonicalization 後の `used_form`(HR表の「英語表現」)。**空白を含まない1トークン=単語(word)**(ハイフン複合語 well-known 等も1トークン=word)。**空白で区切られる2語以上=フレーズ(phrase)**(句動詞 carry over・空白区切り複合名詞 work area も phrase)。

## 5. Prompt(全文。sha256はコードの定数と一致)
P7 sha256 = `2e93019300f960e5ff3070dd83b12a81566b8ceb87b44b335d554a7a711eb291`  /  W3 sha256 = `7a9c47a01410bd9f56222c210f15353f4e4da74e56edfa67ec33201e2ee891ab`
Production Prompt 2(`er105.PROMPT_2_SHA256`)・Prompt 2-V(`PROMPT_2V_SHA256_PINNED`)は無変更(testで固定)。P7はPrompt 2から「冒頭の件数文」と「条件6」の2行だけを置換(testで固定)。難易度はProduction同様Prompt側で区別しない(Prompt 2は全levelで『英語上級者』基準。本文自体がレベル適合済み)。レベル適合は評価ルーブリックで判定する。

### P7
```
以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム(2語以上の連続した語句)を、学習価値の高い順に**最大7つ**選んでください(単語単体は別の枠で選ぶため、ここでは選びません)。

以下の順序で処理し、上位条件を優先してください。

1. **本文一致（絶対条件）**：本文中の連続した語句だけを抜き出す。変更・言い換え・追加・創作は禁止。
2. **5語以内（絶対条件）**：スペース区切りで正確に数える。6語以上は出力禁止。
3. **学習ポイントの明確化と最小化（必須）**：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。
4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. **最大7件・順位付け**：条件を満たす候補から、学習価値の高い順に最大7件を選び、1位から順に並べる。互いに同一、または一方がもう一方を含む類似の表現を重ねて選ばない。適切な候補が不足する場合のみ7件未満とし、数合わせはしない。各候補に、選んだ理由を日本語で1文(40字以内)添える。

**出力直前に各候補を本文と照合し、改変がないこと、5語以内であることを再確認してください。語数も併記してください。**
```
### W3
```
以下の記事から、英語上級者が学ぶ価値のある**単語単体(1語)**を、学習価値の高い順に**最大3つ**選んでください(すでに選ばれたフレーズ・表現は、記事本文の後ろに示します)。

以下の順序で処理し、上位条件を優先してください。

1. **本文一致（絶対条件）**：本文中に実在する単語だけを、本文に現れる形のまま抜き出す。変更・言い換え・追加・創作は禁止。
2. **1語（絶対条件）**：スペースを含まない1語だけを出力する。2語以上は出力禁止。
3. **単語単体の学習価値（必須）**：その単語そのものを学ぶ価値があること。意味の明確さ・他の文脈での汎用性・難易度を評価して選ぶ。固有名詞・数字・この記事だけでしか使えない語は避ける。
4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙を優先する。
5. **易しい語の除外**：基本語や、上級者なら知っている易しい語は除外する。
6. **重複の回避**：すでに選ばれたフレーズ・表現に含まれる語は、フレーズ側で学べるため選ばない。
7. **最大3件・順位付け**：条件を満たす候補から、学習価値の高い順に最大3件を選び、1位から順に並べる。適切な候補が不足する場合のみ3件未満とし、数合わせはしない(簡単すぎる語や不自然な語で3件に揃えない)。各候補に、選んだ理由を日本語で1文(40字以内)添える。

**出力直前に各候補を本文と照合し、改変がないこと、1語であることを再確認してください。語数も併記してください。**
```
(本文は `

---

【記事本文】
` + 本文、W3は更に `

---

【すでに選ばれた表現(これらは選ばない)】
- ...` を後置。区切りはProductionと同一定数。)

## 6. Gate適用表(Production関数をimport、同一引数)
| Gate | 関数(ファイル) | フレーズ(P7) | 単語(W3) |
|---|---|---|---|
| 本文連続一致・文境界・1〜5語・重複・有限助動詞(have役割判定)・数値placeholder | `er105.validate_and_resolve`(`selection_gate`経由) | 適用 | 適用(1語もこの範囲) |
| 既存候補との同一/包含 | `er119.run_vocab_selection`内 `_containment`(Production) | P7内では非適用(Production call1同様) | **適用**(P7通過句に含まれる語は`duplicate_of_top3`で除外=学習価値重複の機械判定) |
| Human NG(明示除外) | `ft.phrase_key`照合 + `rv.match_ng`(generate_candidates内) | 適用(NG空=今回は除外0) | 適用 |
| CMU辞書 | `er108.reasons_for_phrase` | 適用 | 適用 |
| canonicalization(LLM。基本形化・Rule7・QA) | `sc.run_key_phrase_canonicalization` | 適用 | 適用(1語の扱いは実測で記録) |
| gloss再整合 / CMU post-canon / 記号 | `ga.align_glosses` / `cmu.canonicalized_check` / `sc.detect_key_phrase_symbol_findings` | 適用 | 適用 |
| [Z]人称整合 / SRC D1 | `kcand.make_person_repair_fn` / `kcand.make_z_src_fn` | Zのみ適用 | Zのみ適用 |
| Redundancy QA(旗) | `sc.run_key_phrase_redundancy_qa` | 候補全体1回 | 候補全体1回 |
| 最大8の上限 | `rv.KP_CANDIDATE_MAX` | **Trialでは適用しない**(通過件数をそのまま記録。8超は注記) | 同左 |
単語に追加した確認: 「本文実在」はvalidate_and_resolve(連続一致)で担保。「レベル適合」はGateではなく下記ルーブリックで評価(Gateは新設しない=受理面を広げない)。除外は全件を理由コード付きで記録し、救済フローは適用しない。

## 7. 事前固定の評価ルーブリック(Y/B/N。候補単位)
基準(すべて「当該levelの学習者」基準。Standard=a2はA2〜B1学習者、Advanced=b1bはB1〜B2学習者):
- R2 自然さ: 単独で自然に成立する語句で、切り出しが不自然・文脈依存でない。
- R3 汎用性: 他の文脈で再利用でき、記事固有の固有名詞・数値・物名でない。
- R4 難易度適合: 学ぶ価値がある(少し上の語彙)が、易しすぎる基本語/極端に難しい語でない。
- R5 学習価値の非重複: 同一run内の他の採用候補と学習ポイント(語幹・包含・同概念)が重ならない。
判定: **Y**=R2〜R5すべて充足 / **B**=1項目だけ境界 / **N**=1項目以上が明確に不充足。「品質基準を満たす有用候補」=Y(Bは別計上、合算しない)。同一run内の重複(R5)は先順位のみY、後順位をNとする。
- 数合わせ(filler)判定: N かつ 理由が R4 易しすぎ/R2 不自然/R5 重複 のもの。
- judge(gpt-6.1-sol): 同一ルーブリックで、現行候補とTrial候補(各rep)をlevel単位で匿名化・順序シャッフルして1 call判定(各候補にR2〜R5の充足可否とY/B/N、filler旗)。

## 8. 安定性評価・Status判定基準(事前固定)
- 指標: 12 run(6 level×2)それぞれの (a)Gate通過件数 (b)Y件数(自ルーブリック) (c)自ルーブリックYかつjudge一致Y件数。分布(min/median/max)と、Y≥6の達成run数。
- **VALIDATED(提案)**= (1)12 runのY件数 median≥6 かつ min≥5 (2)単語候補にY判定が≥1件あるlevelが6 level中≥4 (3)フレーズ側のY率が現行方式のY率より10ポイント超低下しない (4)filler(N)の割合が現行+10ポイント以内 (5)Gate関数のProduction同一適用が崩れていない。
- **REJECTED**= Y件数 median<5、または フレーズY率が現行より10ポイント超低下、またはfiller割合が+10ポイント超。
- 上記の中間、または結果がlevel間で一貫しない場合は **判断候補**(ユーザー判断)。Production採用の推奨はFable/ユーザー判断であり、VALIDATEDでもProduction実装へ移行しない。

## 9. 一般化できる範囲(事前)
3記事×2level×2回の範囲。Family X(2記事)とZ(1作品)で確認。Family Yは正式KP経路が未存在(OPEN-484)のため机上確認のみ(STATUS_01.md)。

## 10. 副作用の隔離
- cost logger・telemetry(`sc.KP_BACKEND_TELEMETRY_PATH`)は `runs/<tag>/` へ。既存run dir・er030_output・HR候補ファイルには書かない。HR CLIは実行しない。
