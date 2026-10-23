# PHASE3_RUNTIME_EVIDENCE_01: 修正版B全体 Production配線の正式runtime evidence(『開いた窓』run_sf_prod_01)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_05 / 2026-10-23 / 正式Production経路(`er026_family_z_fiction_production_runner_01.py --stages seed_check,writer,std_adjust --mode real`)
Status候補: `WIRED_PENDING_FABLE`(`PRODUCTION_WIRED`はFable受入後のみ)。音声段は未実行(Phase 4で同run `run_sf_prod_01` を継続)。

## 1. 実行
- run dir: `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01`(新規。旧`run_e2e_01`は無変更・参照のみ)
- コマンド: `--story the_open_window --run run_sf_prod_01 --stages seed_check,writer,std_adjust --mode real --approved-budget-jpy 40`(1回のみ)。STOP確認 rc=0(`docs/pm/delegation_log/2026-10-23_FZSF5_stop_check.json`)。
- 費用: r0 2.2557 + r1 2.0912 + r2 1.9290 + std_adjust 6.3542 = **12.6301円**(出典=`run_sf_prod_01/cost_log.jsonl` 4行 / `e2e_stage_log.jsonl` spent_jpy_cumulative)。上限40円内。使用モデル=gpt-6.1-sol(全段、`provenance.json` actual_model_id。本番Writer既定)。LLM呼出=4回(retry/fallback 0、attempts=1)。所要=writer 97.3秒+std_adjust 89.2秒。
- seed_check: `source_essentials` present=true、items=5(上限5)、keep_names=[Framton, Vera]、source_quoteが`primary_text_excerpt.md`末尾段落に逐語一致、essentials_sha256 `5e624b717d97…`。

## 2. provenance(essentials shaの組込み)
`writer/provenance.json`: seed_sha256 `69f3e63cfd4f…`(新Seed)、`source_essentials_sha256`=`5e624b71…`。r0/r1/r2/std_adjust全entryに`essentials_sha256`=`5e624b717d…`、input_sha256=sha(親sha+"\n##ESSENTIALS##"+essentials_sha)(r0=`b0e9a6a950`、r1=`6b79d7cc4b`、r2=`cc38ff6db5`、std_adjust=`c7715a4c11`)。

## 3. Trial Promptとの一致(実run dump)
- R0 Prompt(`run_sf_prod_01/writer/r0_prompt.txt`) = T2 dump(`run_sftrial_t2_01/writer/r0_prompt.txt`) **byte一致(差分0)**。
- R1/R2 Prompt = T3 dump(本文部分のみ差替え)と、**意図した2点のみ**差分: (a)"Framton Nuttel"->"Framton" (b)REVISE側に「一方の名前のみ(first or last)」節を追加。それ以外 byte一致(スクリプトで確認、True)。
- Std Prompt = T3 dump(本文差替え)と byte一致(差分は「exactly N paragraphs」のN=31->29のみ=データ由来)。
- test固定: `er062_family_z_source_essentials_test_01.py::TrialPromptMatchTest`(T2/T3の2runのdumpと照合)。

## 4. 全段の保持結果(本文確定: Phase 4で使う本文)
| 項目 | R0 | R1 | R2(Adv) | Std |
|---|---|---|---|---|
| 語数(目安330-470) | 425 | 422 | 434 | 422 |
| 段落数 | - | - | 29 | 29(Adv一致) |
| 最終行(種明かし) | `Romance at short notice was her speciality.`(原作逐語) | `Inventing convincing stories at a moment's notice was Vera's speciality.` | 同左 | `Vera needed only seconds to invent a story people believed.` |
| 人名 | Framton / Vera | 同 | 同 | 同 |
| Nuttel/Sappleton/Ronnie | 0 | 0 | 0 | 0 |

既存決定論検査: R2 `warnings=[] failures=[]`、Std `failures=[]`、段落一致 True、同一文率0.0204(FAIL閾値0.50)、soft WARN `STD_AVG_SENT_LEN_NOT_SHORTER 8.61 vs 7.75`(既存のsoft gate。Trial T3 8.37/9.33と同種、過去のZ runも同種)。Std JA lint等の後段は未実行(Phase 4)。

## 5. Fable CP相当の記入(Sonnetが本文引用を貼付。判定はFable)
機械生成`writer/cp_checklist.md`の各行に対する本文引用(逐語)。

| # | 深刻度 | 項目 | R0 | R1 | R2 | Std |
|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal | "Romance at short notice was her speciality." | "Inventing convincing stories at a moment’s notice was Vera’s speciality." | 同R1 | "Vera needed only seconds to invent a story people believed." |
| 2 | 軽微 | withhold_until_end(結末前に作り話と分かる説明・結末直前の付加文が無い) | 最終のVeraの嘘の台詞内に"A rather unpleasant cure for sleeplessness."(台詞内の洒落。語り手の付加文ではない。R0は後段で言い換えられ不使用) | Vera台詞内"He couldn’t bear the sight of another dog."(台詞内。語り手の付加文なし) | Vera台詞の直後が最終行。語り手の付加文**なし** | Vera台詞の直後が最終行。語り手の付加文**なし** |
| 3 | 重大 | setup と payoff | setup "She keeps the window open until dark … white waterproof coat … ‘Bertie, why do you bound?’"->payoff "Three figures were crossing the lawn … One had a white coat … A tired brown spaniel … ‘I said, Bertie, why do you bound?’" | setup "That’s why she leaves the window open until dark. Her husband was carrying his white coat…‘Bertie…’"->payoff "A white coat hung over one man’s arm. Behind them came a tired brown spaniel."+"‘I said, Bertie, why do you bound?’" | setup "She keeps the window open until dark, waiting for them." "Her husband had his white coat over his arm…‘Bertie, why do you bound?’"->payoff "A white coat hung over one man’s arm. A brown spaniel followed close behind." "‘Bertie, why do you bound?’" | setup "That’s why she leaves the window open." "Her husband carried his white coat…‘Bertie, why do you bound?’"->payoff "One carried a white coat, and a brown spaniel followed." "‘Bertie, why do you bound?’" |
| 4 | 重大 | key_role keep_name=Framton | "Framton sat on the edge of his chair"(Nuttel 0) | 同(Framton) | 同(Framton)、"He grabbed his hat and stick and rushed out." | 同(Framton)、"He took his hat and stick and hurried outside." |
| 5 | 重大 | key_role keep_name=Vera | "said Vera, her fifteen-year-old niece" | "said Vera, her fifteen-year-old niece" | "said Vera, her fifteen-year-old niece" | "said fifteen-year-old Vera"(Veraの導入は自然) |
| 6 | 重大 | key_role(叔母=役割で表現、名前なし) | "her aunt"/"A most peculiar visitor,” said her aunt" | "her aunt"/"his wife" | "her aunt"/"his wife said" | "Her aunt"/"she replied"(名前なし) |
| 7 | 重大 | key_causality(作り話->信じる->叔母が裏付け->人影->逃走->犬の嘘) | "Framton searched for something safe to say."->"Here they are at last!"->"racing down the drive."->"It was the spaniel” Vera said calmly." | "grateful for a subject that had nothing to do with the dead."->"They had come back."->"racing down the drive."->"It was the spaniel,”" | "Framton felt a chill. So she really was waiting."->"The dead were coming towards the house."->"running down the drive."->"It was the spaniel,” Vera said calmly." | "Framton went cold because she really did expect them back."->"as the dead approached the house."->"racing down the drive."->"The dog frightened him,” Vera said, sounding perfectly calm." |

CP所見: **重大欠落 0件。軽微(結末直前の語り手の付加文)0件(R2/Std)**。よって処置規則(A)(B)とも発動なし=削除パッチ適用0・追加Writer呼出0・C案提示不要。R0/R1の台詞内洒落は最終採用本文(R2/Std)に残っていない。他人名の増加なし("Bertie"は歌詞の引用で原作どおり)。

## 6. resume整合(再生成0)
同run・同コマンドを再実行: seed_check/writer/std_adjust の elapsed 0.0秒、cost_log.jsonl 4行のまま(増分0)、provenance chain 4 entryのoutput_sha256不変(r0 `7d695ced`、r1 `f53c336a`、r2 `f07a1465`、std `9afb5926`)、`regenerations=[]`。再生成0・費用0を確認(essentials shaが入力指紋に入ったうえでの再利用)。

## 7. 不使用・未実施
音声段(plan以降)は未実行(Phase 4)。Vera発音: PNAP既存運用で足りる(Ledger未登録、Phase 4の音声QA/ASRで確認、Opus論点4)。
