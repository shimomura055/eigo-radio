# COST_02 費用(実測ベース、設計時点はAPI 0)
前提: 決定① Std②=C案(Adv Part 1と同型の完全版)。ハイライト(②③含む)はLLMなし=0円。音声は不変=TTS費用0。

## 1. 実測(既存artifact。COST_01と同一出所、`CURRENT_SPEC.md:2094`の記載と整合)
| 項目 | 実測 | 出所 |
|---|---|---|
| Part 1解説 1 call(5件) | ¥0.125〜0.130(output 1,424〜1,477 tok、gpt-6-luna=SUPPORT_MODEL) | `er019_output/**/kp_general_explanations.json` audit.calls |
| Part 1解説 1 call(3件) | ¥0.073〜0.097 | 同上 |
| T1訳 1 call(5件) | ¥0.030 | `part2_hr_evidence_01__run_r2/b1b/key_phrases/kp_source_sentence_ja.json` audit |
| 解説+訳(Z/X実績) | ¥0.103〜0.139/set(`CURRENT_SPEC.md:2094`) | 同 |

## 2. 記事あたり(量産単価への影響)
- **Std Part 1(5件)= 解説¥0.125〜0.130 + T1訳¥0.030 = 約¥0.155〜0.16/Std記事**(Adv Part 1の¥0.17相当と同水準)。1記事セット(Std+Adv)で**+約¥0.16**(70円目標比 約+0.23%)。
- retry最大1回(既存の技術retry 1回=解説/訳それぞれ最大2倍)の上限でも **+約¥0.32/記事セット**(約+0.46%)。通常はretry率が低く実績平均は上記。
- ハイライト(①②③)・③訳リスト・凡例: LLM 0・追加API 0 → **¥0**。
- Std ①のみ3件の記事(②0件)では、Part 1は①3件分(解説¥0.073〜0.097+訳約¥0.02)。
- 量産単価70円/記事セットの継続目標(Charter原則3)に対する低コスト化余地: (a)Std/Adv両levelのKP表現が重なる場合に解説をlevel間で再利用する案は、難易度別Promptのため不可(品質優先で採らない)。(b)T1訳は引用英文のみ入力=Std/Advで同一Promptのまま、引用文が同一の場合に限りsignature一致でreuseは既存機構(`ensure_stage`)で自動(追加実装0)。(c)Std Part 1とT1訳を1 callに統合する案は、T1専用翻訳工程(ユーザー正式承認2026-10-25、`CURRENT_SPEC.md:2092`)の分離を崩すため採らない。→現時点で削減余地は小さく、増加幅(+0.23%)を最小に留める。

## 3. 6経路の評価費用見込み(F: runtime evidence)
| 経路 | 内容 | API |
|---|---|---|
| X Std / X Adv | AI島の既存run(run_form_prod_01)を再利用。Std Part 1生成のみ(約¥0.16)。Advは既存生成物をreuse(API 0)。ページ再ビルド=API 0 | ¥0.16 |
| Z Std / Z Adv | 既存の複製run(GPG委任_05系evidence run等)+`stage_kp`のStd Part 1(`kp_part1_a2`)を新規生成(約¥0.16)。`--stages provision_shell,gate,assemble,pages,page_verify`を1起動(音声は既存再利用、API 0) | ¥0.16〜0.32 |
| Y Std / Y Adv | 05C evidenceで確定済みのY run上でStd Part 1生成(約¥0.16)。`pages`/`page_verify`はAPI 0 | ¥0.16〜0.32 |
| 異常系(fail-closed・多重出現・LR後span消失・重なり)evidence | 純関数test+fixture(API 0) | ¥0 |
| **合計** | Std Part 1生成3〜6回(各約¥0.16) | **約¥0.5〜1.0**(retry・再生成の余裕込みで**¥2〜3**見込み) |
- 新規にKP候補生成から回すevidence runが必要になった場合のみ追加(KP候補生成+検査は1記事あたり過去実績で数円。GPG委任_05の6経路evidence総額は¥3.30)。その場合でも**全体の見込み上限¥10**。
- **承認区分**: 7-7の承認済みScope内・案件見積300円以下に該当(上限見込み¥10 ≪ ¥300、日次1,000円も圧迫しない)→都度のユーザー承認は不要。分割による境界回避なし。超過見込みが出た場合のみFable報告。
- モデル: 開発評価も本番ラインと同じSUPPORT_MODEL(gpt-6-luna)で実行(`CLAUDE.md`「最新モデル原則」に対し、Std Part 1は本番ラインそのものの評価のため本番モデルで評価する例外=実行前にレポートに明記)。実行時は`actual model_id`を記録(受入条件10)。
