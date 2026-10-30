# EVIDENCE_04 (KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_04): 較正案v3(難/激難の定義具体化)のheld-out評価 -> 採用

結論: v3は採用条件(i)〜(v)を全て満たし**本番Promptへ採用**(sha 3d9c3c83... -> 402d3b1a...)。別系列(gemini)比較は費用Capのため**X 4セット29件のみ**(要注意、下記)。実費4.09円(Cap 4円を0.09円超過=下記)。

## 条件
held-out 68件(委任_02の55件=ai_island_temple/redelivery_fee/melos、委任_03の52件=uk_train/sns_age_limit/tell_tale_heartと記事重複なし)。X=coffee_prices(run_kpbf_ev_02)+middle_east_yemen_saudi(run_kpbf_ev_03)、Y=surname_choice(run_02)、Z=in_a_grove(run_sf_prod_01)、各Std(a2)+Adv(b1b)、既存run保存docのkp_candidates.json。
Sonnet 5.5実読(blind)=kpd04_out/kpd04_sonnet_labels.json: 易7/中44/難17/激難0。LLM呼出前にkpd04_sonnet_labels_make.pyで確定(生成時刻 < 最初のcall)。
LLM=gpt-6-luna(本番と同一grade())。v1=現行Prompt(sha 3d9c3c8322af...)、v3=sha 402d3b1aabd9...(文言=kpd04_common_01.v3_text、rely on/make room for/narrow downは含めず)。別系列=gemini-3.8-flash(thinking_budget=0)。
v3の変更点(Prompt文言のみ): 「難」=(a)比喩的・慣用的な句動詞/イディオム (b)文語・文学語 (c)抽象語・概念語 (d)辞書で上級(C1相当)の語義・用法、各例付き。「激難」=稀な文学語・専門語・古風な表現(ネイティブでも日常ではまず使わない)。「易」=中学〜高校初級の基本語・基本句動詞。「中」=それ以外の一般語・一般句動詞。規則5=「迷っても段階を下げない」(旧: 迷ったら極端を避ける)。

## 結果(集計=kpd04_eval_01.py、生=kpd04_out/kpd04_eval_result.json、cost=kpd04_out/kpd04_cost_ledger.jsonl)
| 項目 | v1(luna) | v3(luna) | 採用条件 | v3 |
|---|---|---|---|---|
| (i) Sonnetとの一致/隣接/2段階以上 | 36/32/0 | 42/26/0 | 2段階以上<=1 | OK(0) |
| (ii) Sonnet難17件のうちLLMが難/激難 | 2/17 | 10/17(59%) | >=50% | OK |
| (iii) rely on / make room for / narrow down (Std,Adv) | 易,易,中 / 易,易,中 | 易,易,中 / 中,易,中 | 隣接以内(期待 易/中/難) | OK(全隣接以内。narrow down=難の一致は**未達**=望ましい条件、記録) |
| (iv) 同一表現のStd/Adv差(7表現) | 最大1(at ease) | 最大1(ballistic missile, adopted) | <=1 | OK |
| (v) Sonnet易をLLMが難以上にした件 | 0 | 0 | 0 | OK |
| 分布 | 易23/中42/難3 | 易13/中38/難17 | (Sonnet 易7/中44/難17) | |
| 参考: SonnetがLLMより難と見て取りこぼし(難->中) | 15 | 7 | | |
| 参考: Sonnet中/易をLLMが難にした件(いずれも隣接) | 1 | 7 | | |
| gemini-3.8-flash(**X 29件のみ**): 隣接以内率 / 2段階以上 / Sonnet難4件中の難捕捉 | 100% / 0 / 1 | 100% / 0 / 2 | v3>=v1 | OK(同率、ただし部分) |

## 注意・限界
- **Cap超過**: ledger計4.088円 > Cap 4.0円(+0.088円)。原因=geminiをluna並列に起動し、guard(Cap*0.85到達後は新規jobに入らない)が2プロセス並走かつgemini 1call約0.37円で粗かった。超過後は新規callなし。geminiはY/Zの4セット x 2系列(約3円)を完了できず**X 4セットで打切り**(gemini隣接以内率はv1=v3=100%・n=29・2段階乖離0)。Cap引上げは行っていない。
- Sonnetラベラーは単一(私)。ラベルは判定Prompt(v3)文言を見る前の基準(日本人学習者の難しさ)だが、v3作成者と同一であり、(b)文語等の方針はv3定義と近い。Sonnet難17のうちZ(in_a_grove)が10件で文学作品に偏る。
- v3は難を17件(25%)出す一方、Sonnet中を難にする件が7(v1は1)。いずれも隣接段階(2段階乖離0)。narrow down=難には届かず中(v1と同じ)。
- v3でも未捕捉の難(Sonnet難->LLM中): intercepted and destroy / overlap with / constable x2 / trampled / veiled / seize(文学語・やや硬い語の一部)。
