<!-- 抽出元transcript: agent-a4905e8bc3dd3730f.jsonl(subagents配下。指定の.outputは0バイトで抽出不能だったため同内容のsubagent transcriptを使用)。抽出日時: 2026-10-02T21:37:24。本文(最後のassistantメッセージ)は改変していない。 -->

# 委任_43 報告: 日本語側を修正しない場合の実害調査と「英語だけ直す」設計(read-only、¥0、編集なし)

記号: 「runner」は `git show e0ae8de0` で取り出した修正前コピー(一時ディレクトリの `runner_e0ae8de0.py`)の行番号。他は作業ツリー(現行)の行番号。

## 1. 結論
- **「英語だけ修正して終了」は、Self-Recovery Flow(Trial専用)では成立する。** 日本語記事が使われる後続処理は3つだけで、いずれも実害は限定的か、検査で検知できる(Q1)。
- 日本語記事は、英語記事の生成原稿としてだけ使われている。英語本文・Comment・Preview・Key Phraseの日本語訳・player表示は、英語記事(`article.md`)から作られている。**日本語の本文はユーザーに届かない**。
- **実害の経路は2つ見つかった。** 1つ目はProductionの再生成で、`ja_writer/revision2.md`から英語を翻訳し直す経路(Q2)。2つ目は日本語タイトルの読み上げで、`derive_japanese_title`が日本語R2由来のタイトルを音声とplayerに出す経路(Q1表の行3)。
- 1つ目は、Self-Recovery FlowがProductionに組み込まれ、かつ英語が直された後にProductionで再生成が走る場合にだけ発動する。再生成後の英語は必ず逸脱検査をやり直すので、**無言で誤りが戻ることはなく、検知される**。2つ目は、Ledger逸脱が日本語タイトルに入っているかが**未確認**。
- 「日英整合を保ちたい」という理由だけの害は数えていない。
- **Opus L2レビュー#1の前提の一部は、現行コードと一致しない。** 「audioはEN/JA双方から作られる」(opus_01 L162)は、本文については当たらない(Q1)。
- 外す対象は、`paired_rewrite`、JA対応箇所の推測5段、JA Recheck、`ja_pending_deviation`、`ja_fail_open_guard`、JA/EN等価チェック、JA指摘の次周回合流。効果の根拠は弱い〜中(集計は観察データで、設計変更前の旧世代の実行が混ざる)。
- STOP条件: Trial範囲に限れば非該当。**Productionへ組み込む時点で**、Family Xの「忠実英訳」「案B(JA差し戻し1回)」との関係でユーザー判断が必要になる可能性が高い。
- Existing Spec / Prior Trial Check は **A + B(部分)** に分類する(§8)。

## 2. Q1: Production正式pathでの日本語記事の役割

### 生成元(Family X、現行Production)
- 日本語R2が先に作られる。作成はJA Writer(Original→R1→R2)で、JA Fact Checkを通る(CURRENT_SPEC L1228-1235、項目4)。
- 英語Advancedは日本語R2の「忠実英訳」で、`adv_gen.generate_family_x_faithful_translation(ja_text)`(er012_e L361, 365, 403)。
- 英語Standardは英語Advancedから作られる(`std_gen.generate_family_x_standard_a2_no_heading(advanced_text)`、er012_e L471)。日本語は入力に入らない。
- Family Zは日本語記事がない(CURRENT_SPEC L1322-1471で日本語・Ledger・Deviationの記述にヒットなし)。
- en_direct(Ledgerから直接英語)は`er003_v1_en_direct_vfl_01_generate.py`で、Legacy扱い(CURRENT_SPEC L1472以降の「Family体系」)。同ファイルは、Family Xの検査関数`run_deviation_check`の定義元でもある。

### 日本語記事の後続利用の全数

| # | 利用箇所 | ファイル:行 | 使われる日本語の種類 | 正式出力か内部入力か |
|---|---|---|---|---|
| 1 | 英語Advanced生成(忠実英訳)。再生成・段落数retry・deviation must-fix retryでも同じ入力 | er012_e L361, 365, 403 | 日本語R2全文(原文記事) | 内部入力 |
| 2 | 再実行時のR2再利用。`revision2.md`があれば読み、`run_writer_stage(only=advanced/standard)`へ渡す | er019_family_x_entertainment_production_runner_01.py L358-363, L376, L386, L397 | `ja_writer/revision2.md` | 内部入力 |
| 3 | **日本語タイトルの読み上げ**。`derive_japanese_title`が`runtime_evidence.json["title"]`、なければ`revision2.md`の1行目を読む。用途はA2の`japanese_title`セグメントとplayerの「Japanese title」行 | er019_family_x_audio_production_runner_01.py L133-147, L1852, L1917 / playerは約L1582-1605(`label == "Japanese title"`) | 日本語R2のタイトル行だけ | **正式出力(音声・player)** |
| 4 | Deviation Checkの`source_article_text`(起源タグ付け専用) | er012_e L383, 416, 479, 510 → vfl01 L792-798, L667-675 | 日本語R2全文 | 内部入力(検査の参考) |
| 5 | 案B(ja_source MAJORでJAを1回再生成→AdvancedとStandardを再実行) | er012_e L581-666 | 日本語R2。再生成して`ja_writer/*.md`を上書き | 内部入力(JA再生成の起点) |
| 6 | Comment1-4・Preview(B1/A2) | er019_family_x_audio_production_runner_01.py L240-300 | **使わない**。`parts['part1..3']`と`reconstruct(parts)`、つまり英語本文だけを渡している | — |
| 7 | Key Phrase | 同 L320-341(`sc.run_key_phrases(article_text...)`) | 使わない(英語記事から生成) | — |
| 8 | 音声本文TTSとplayerの本文行 | 同 L204-228, L1582-1780 | 使わない(`{level}/article.md`の英語)。日本語は上記3のタイトルのみ | — |

- 行3以外では、日本語本文はユーザーに届かない。Local Rewrite(Production)も英語記事上で動き、日本語を入力にしない(CURRENT_SPEC L991-1013、L1396)。
- B-Familyの`source_article_text`(er012_b_family_production_runner_01.py L193, L707, L1383)は、Key Phraseの流用元と流用先の本文が同一かを確かめるsha一致のためのもの。日本語記事ではない。
- Legacy(Family A/B/C、`er003_ja_to_en_translation.py`など)は、新規実装・追従しない方針(CURRENT_SPEC L1480-1490)なので深追いしていない。

## 3. Q2・Q4: 英語への誤りの再流入と、日本語から英語を作り直す経路

### Production(確認済み)
- 英語を日本語から作り直す経路は、Q1表の行1・2・5の3つ。
- **発動条件:** (a) Advanced生成の段落数retry(er012_e L364-371)、(b) Advanced deviation must-fix retry(L403-407)、(c) `--regenerate-stage advanced`、または`stage in ("advanced","all")`での再実行(er019_..._entertainment_production_runner L376-386)。
- いずれも日本語R2を読む。**Self-Recovery Flowが英語だけ直して日本語を更新していなければ、再翻訳で元の誤りが戻りうる。**
- 戻った場合の挙動: 再生成された英語は必ず`run_deviation_check`を通る(er012_e L382, L415)。**Checkerが検知する**ので「無言で戻る」ことはなく、同じ指摘に対する再修正が必要になる(コスト・周回の問題)。現行仕様は、この場合ja_sourceならSTOP→案Bで日本語を直す設計(CURRENT_SPEC L1236-1259)。
- Standardの再生成は、ディスク上のAdvanced(`b1b/article.md`)から行う(er012_e L458-459)。Advancedが先に直されていれば、その修正を引き継ぐ。
- Production側の`run_deviation_check`にretryロジックはない(CURRENT_SPEC L1951)。Deviation Check後のretryは`must_fix`付きの全文再生成のみ。

### Self-Recovery Flow内
- 英語のRewrite(`single_text_rewrite`、runner L2731〜)の入力に日本語は入らない。`source_article_text`をruner内でgrepした結果、該当は検査・Stage 2・S1d・Recheck(L1294-1300, 1351, 1397, 1436, 1502-1504, 1655-1657, 2103, 2116)と、`paired_rewrite`/`run_stage3_for_claim`(L2927, L3093, L3202-3207)だけ。
- したがって、**Rewrite自体が古い日本語を根拠に英語を元へ戻す経路は確認できなかった。**
- 日本語を渡している各Promptの文言は「参考、逸脱の発生源特定用」(`er052_open233_self_recovery_stage2_01.py` L52, `er052_open233_self_recovery_s1d_trial_01.py` L68、vfl01 L667-675)。判定ではなく起源タグ付けのためだけの入力。
- 実運用で発動しうるのは次の1点だけ。Self-Recovery Flowの結果(`article.md`)がProductionの`ja_writer`/`revision2.md`を更新しないまま、Productionの再生成が走る場合。**現状、Self-Recovery FlowはProduction未配線**なので、今は発動しない。

## 4. Q3: 日本語がそのまま正式出力に使われるか。JA fail-open封鎖の導入理由
- 本文は使われない(Q1表の行6-8)。**日本語タイトルだけは音声・playerで使われる**(行3)。
  - 日本語タイトルがLedgerから逸脱している実例は**未確認**。JA Fact CheckがタイトルをLedger照合の対象に含むかも**未確認**(`er019_family_x_ja_writer_o_r1_r2_01.py`は未読)。
- **JA fail-open封鎖の導入理由は「日英整合」でも「日本語が正式出力だから」でもない。** 理由は、paired J-1が日本語を編集する以上、その編集結果を検査する安全網が働いていなかったこと。
  - 設計書§6-7(L2761-2771): paired J-1が「指摘されたJA文を一字も変えず、別段落の無関係なJA文を削除」し、`ja_recheck_overall_status: LEDGER_DEVIATION`、`ja_en_equivalence_verdict: FAIL`だったのに`RESOLVED_REWRITE_THEN_DOWNGRADE`(false PASS)となった。
  - Opus L2レビュー#4 §0(L28-31): 「実質的な false PASS(指摘された JA 文が未修正のまま『解決』)」「その唯一の安全網(JA 全文 Recheck)自体が現状 fail-open」。
  - つまり封鎖は、「日本語を編集する」という選択をした前提で、その編集の安全網を直したもの。日本語を編集しなければ、封鎖が必要になる前提そのものがなくなる。
- 日本語を直す理由づけの出所は、Opus L2レビュー#1。
  - 論点1(A)(L40): 「EN局所RewriteをJA起因claimに適用すると、誰もチェックしないJA/EN乖離が生じる。…Family Xの二段階生成の前提(忠実英訳)を壊す」
  - 論点4(L162): 「JA/EN乖離が最大のSafetyリスク…audioはEN/JA双方から作られる前提が壊れる」
  - 設計書§5-2(L1735-1740)がこれを採用し、「ja_sourceにEN局所Rewriteを適用しない」(A4)とした。
  - 前述のとおり、audioが日本語から作られるのはタイトルだけ(Q1)。Opusが想定した「EN/JA双方から作られる」ことは、現行の音声経路では成立しない。

## 5. Q5: JA関連処理の全数と、外した場合の影響

### 処理の全数(runner行)

| 処理 | 行 | 導入経緯(設計書) | 外すと検出・是正されなくなるもの | 外すと変わるもの |
|---|---|---|---|---|
| `paired_rewrite` と呼び出し分岐 `use_pairing` | 2920-3193、3199-3203 | §5-4(J-1)、A4(Opus#1論点1(A)) | ja_source指摘の「日本語側の是正」 | ja_sourceの指摘は`single_text_rewrite`(英語のみ、runner L3211相当)に回る |
| JA対応箇所の推測(5段) | 2940-2973、2497-2536 | §5-4(委任_10) | 日本語側の対応文の特定 | 不要になる(文数が1対1でない問題も消える: handoff設計書L243-244) |
| JA Recheck | 4513-4527 | §5-4「JA側1call+EN側1call」 | 日本語本文のLedger整合 | ¥0.333/回(実測)の節約 |
| `ja_pending_deviation` / `ja_deviation_unresolved` | 4059、4129-4131、4489、4557-4560 | §6-7(i)(委任_20 W1) | 日本語未解消の見落とし防止 | このStage 4理由が消える |
| `ja_fail_open_guard` ほか補助(`is_predominantly_ja` 2431、`split_ja_sentences` 2418) | 3423、4398、4467-4474 | §6-7(iii) | 日本語編集の逐語残存・段落外JA文消失の検知 | 不要になる(日本語を編集しない) |
| JA/EN等価チェックとgating(`run_ja_en_equivalence_check` 1043、`resolve_ja_ok_after_equivalence_gating` 3354) | 4435-4465、4530-4545 | §6-7(ii)、§6-11 | 日英の意味乖離 | ¥0.105/回の節約。日本語を直さないので乖離は前提 |
| JA指摘の次周回合流 | 4606-4631 | §6-7(i) | 日本語指摘を次周回の標的にする処理 | 不要になる |
| 日本語側precheck(`baseline_precheck_ja`、`rewrite_new_findings_ja`) | 4064-4067、4414-4418 | §4(委任_11 B-6) | 日本語側の新規逸脱検出 | 不要になる |
| `full_recheck_required`のJA引数 | 3275〜3350 | §6-7 | — | 引数を外す |

### 実測(`er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`、`results_01.json`、およびer052_output配下の`instances_*/*.json`の`call_log`を集計。全文Readなし)
- 書き換えのあった260件のうち、`j1_*`始まりが91件(35%)。`+ladder6_disabled`系7件を含めると98件で、委任_41の値と整合。
- 277 instance-run中、Stage 4は40件。**`ja_deviation_unresolved`は11件で、Stage 4理由の中で最多(27.5%)**。うち10件は`j1_*`の書き換えを行った経路。
- JA Recheck 82回=¥27.33(平均¥0.333)、等価チェック82回=¥8.60(平均¥0.105)。合計¥35.9で、総費用¥257.84の約13.9%。
- instance単位で見た書き換えありの比較(交絡あり):
  - j1経路を含む70件: Stage 4が25件(36%)。
  - 英語のみ(`ja_source`指摘を含む)26件: Stage 4が6件(23%)。
  - 英語のみ(`ja_source`指摘なし)101件: Stage 4が9件(9%)。
  - 条件が違うため、効果の裏付けとしては弱い。

### 外した場合の見込み
- 人間確認(Stage 4)では、`ja_deviation_unresolved`の11件は消える。ただし、その11件の英語側の指摘が別の理由でStage 4になるか、英語だけで解消するかは**未測定**。上記の英語のみ(ja_sourceあり)の23%を目安にできるが、交絡がある。
- 周回の数は、日本語指摘の合流による周回が減る可能性がある。`cycle_limit_exhausted_after_recheck`のうちja_sourceが13件(EN 6件+空欄7件)だが、日本語由来かは未確認。
- コストでは、日本語検査の約¥35.9(約13.9%)は確実に減る。日本語編集のLLM呼び出し分は、今回は分離集計していない。

## 6. Q6: ja_sourceの指摘を英語だけ直した後の再指摘
- **再指摘される構造は確認できなかった。**
  - 逸脱の判定本体は、英語記事とLedgerの照合(`DEVIATION_PROMPT_TEMPLATE`、vfl01 L502-601)。
  - 日本語原文が渡るのは追加指示`ORIGIN_INSTRUCTION_TEMPLATE`(vfl01 L667-675)で、目的は各deviationを`ja_source`か`translation`に分類すること。Prompt文面は「各deviationについて…既に存在していたか…判定し、originとして記録」。
  - Recheckも同じ(runner L1499-1508、L1655-1657): Ledger照合+prior_issuesの解消確認+originタグ。日本語との不一致を新しい指摘にする指示はない。
  - 英語が直れば逸脱自体がなくなるので、originタグも付かない。
- 残るリスクは、LLMが日本語との不一致を逸脱として拾う「モデル挙動の揺れ」。コードとPromptからは確認できず、**実測では未確認**。
- 英語だけ直した後も、`working_fixture["source_article_text"]`は古い日本語のまま渡り続ける(runner L3207)。起源タグだけに使われるので、残しても害は確認できない。ただし、渡さない選択肢もある(§7)。

## 7. 設計案(実装しない)

### 基本案: 英語だけ修正して終了(Trial範囲)
- **外す処理:** §5表の全行。具体的には、`use_pairing`分岐(L3199-3203)、`paired_rewrite`(2920〜)、`locate_ja_counterpart_by_position`(2497〜)、JA Recheck(4513-4527)、`ja_pending_deviation`(4059、4129-4131、4489、4557-4560)、`ja_fail_open_guard`と補助(3423、4398、4467-4474、2418、2431)、等価チェック(1043、4435-4465、3354、4530-4545)、JA合流(4606-4631)、日本語側precheck(4064-4067、4414-4418)。
- **残す処理:** Stage 1〜3(Stage 2のmaterial判定、英語のE-1/E-2 Rewrite、`single_text_rewrite`)、英語のRecheck、`ja_source`/`translation`のタグ付け(起源の統計のため)。
- **外した後の流れ:** `ja_source`の指摘も`translation`と同じ扱いにする。Stage 2→英語Rewrite→英語Recheck。`ja_deviation_unresolved`は存在しなくなる。
- **保証しなくなること:**
  1. Trial内で、日本語本文のLedger整合を検査・保証しない(日本語R2はProductionのJA Fact Checkを通過済みという前提のみに依存)。
  2. Trial出力の英語と日本語R2の意味の一致。
  3. 日本語タイトルのLedger整合(**未確認**の経路、§2行3)。
- **記録しておくべきこと(¥0の案):** `ja_not_updated=True`のフラグと、英語で直した指摘のうち`origin=ja_source`のもの。Production組み込みの段階で、人間または日本語タイトルの再確認に回せる。
- **選択肢D1(推奨):** `source_article_text`を起源タグ用に渡し続ける。測定の連続性を保てる。
- **選択肢D2:** `source_article_text`を渡さない。Prompt入力が減り、Q6の揺れの懸念が消えるが、起源の統計が取れなくなる。

### 実害が見つかった経路への最小対策(比較)
- **経路A: 再生成が日本語R2から翻訳し直す**(Q2)。
  - 案A1: Production組み込み時に「再生成後も必ずSelf-Recovery Flowを通す」と明記する(検知はすでに働くので追加コードなし。コスト増の可能性)。
  - 案A2: 英語の修正内容を`must_fix`として、再生成の入力へ添える(Production変更になるためユーザー判断)。
  - 案A3: 日本語R2も更新する(今回外した処理の復活。設計複雑化)。
  - A1が最小。組み込み前に決める事項として、Opusに判断を仰ぎたい。
- **経路B: 日本語タイトル**(Q1行3)。
  - 案B1: 日本語タイトルだけを`precheck`(¥0、決定論)の対象に加える。
  - 案B2: 現状維持(未確認の経路なので、実例が出てから対応)。

## 8. STOP条件・Existing Spec / Prior Trial Check
- **Trial範囲(英語だけ直す設計)**: STOP条件には触れない。新しいProduct原則・Safety原則の変更・Production仕様の変更は伴わない。
- **Productionへ組み込む時点**: 触れる可能性が高い。
  - CURRENT_SPEC L1236-1259(項目5): ja_source MAJORで「英語を盲目的に再生成せず」「JAをOriginal段へ差し戻し1回」。`APPROVED_FOR_PRODUCTION`。
  - 同L1261-1286(項目6)と項目1付近: 「忠実英訳」(日本語R2から英語へ)がユーザー決定。英語だけ直せば、英語は日本語R2の忠実な訳でなくなる。
  - 今回のユーザー指示(日本語は手段)は、この「忠実英訳」を緩める方向。Production化の前に、ユーザーの明示判断が必要になる見込み。
- **Existing Spec / Prior Trial Check: A + B(部分)**
  - **A:** 案B(Production承認済み、CURRENT_SPEC L1236-1259)と、設計書A4(「ja_sourceにEN局所Rewriteを適用しない」、設計書L1735-1740、Opus#1論点1(A)・論点4が出所)。
  - **B(部分):** 「英語だけ」の経路そのものを単独で測った記録はない。ただし、設計書にJ2(「各言語は自言語のCheckerが返したspanだけで直す」、handoff設計書§4-3 L254付近)があり、Opus#5(L72)も「②なければEN側だけ直し、JA再検査に任せる」と書いている。`use_pairing`の条件で日本語が空のときはすでに英語のみに回る(runner L3199-3203, 3211)。
  - 却下理由の主要部分は「JA/EN乖離を誰も検査しない」(Opus#1)と「audioはEN/JA双方から作られる」(Opus#1論点4)。後者は現行コードと一致しない(Q1)。ユーザー指示(日本語は手段)により、前者も実害とは扱わない。

## 9. 確認済み / 未確認、Opusに見てほしい論点

### 確認済み
- Productionの英語・日本語の生成順序と依存(Q1)、日本語本文がuser-facingに出ないこと、再生成が日本語R2から翻訳し直すこと(Q2)。
- Self-Recovery Flow内で英語Rewriteに日本語が入らないこと(runnerのgrep)。
- 各Promptの日本語が「起源タグ付け専用」の文言であること。
- Self-Recovery Flow内でJA関連処理が使われる範囲(§5)と、費用・件数の集計値。

### 未確認
- 日本語タイトルにLedger逸脱が実際に入ったことがあるか、JA Fact Checkがタイトルを対象にしているか。
- `ja_deviation_unresolved`の11件が英語のみで解消するか。
- Production組み込み後の再生成頻度。
- LLMが古い日本語を理由に英語を指摘し直す揺れ(実測なし)。
- Legacy(Family A/B/C)の日本語の扱い。
- `paired_rewrite`のLLM呼び出しコストを`single_text_rewrite`と分離した集計。

### Opusに特に見てほしい論点
1. Opus#1論点4「audioはEN/JA双方から作られる」の前提が、現行の音声経路(日本語はタイトルのみ)と合うか。
2. Production組み込み時の再生成経路(§3、案A1〜A3)の扱い。
3. D1(日本語を起源タグ用に渡す)とD2(渡さない)のどちらを採るか。
4. 日本語タイトルへの対応要否(案B1/B2)。
5. 集計(§5)に交絡があるため、効果の裏付けとして十分か(実測Trialの要否)。

## 10. 読んだファイルと行範囲、T-0結果、作成ファイル
- 読んだ範囲(主なもの):
  - `CURRENT_SPEC.md` L1150-1321、L1472-1510、L829-830、L1951、L991-1013付近のgrep。
  - `er012_e_family_entertainment_two_level_runner_01.py` L340-419、L436-478、L520-568、L581-670。
  - `er019_family_x_entertainment_production_runner_01.py` L352-402。
  - `er019_family_x_audio_production_runner_01.py` L118-160、L240-300、L1582-1780の該当箇所。
  - `er003_v1_en_direct_vfl_01_generate.py` L640-680、L776-830、L502-520。
  - 修正前runnerコピー L1043-1060、L1485-1515、L2920-3010、L3190-3274、L4040-4135、L4385-4660。
  - `docs/pm/design_open233_self_recovery_flow_01.md` L30-45、L645-656、L1686-1745、L1826-1925、L2759-2830。
  - `docs/pm/opus_l2_review_open233_self_recovery_01.md` L25-47、L162、L273。
  - `opus_l2_review_open233_self_recovery_04.md` L20-32とgrep、`..._05.md` L15-34、L70-91のgrep。
  - `design_open233_violation_span_handoff_01.md` L236-258。
  - `er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`、`results_01.json`(集計のみ)。
  - `er052_output/**/instances_*/*.json`の`call_log`(集計のみ)。
- 一覧外の追加Read/Grep: `PM_GOVERNANCE.md` 21節(A/B/C定義の確認)、`er052_open233_self_recovery_stage2_01.py`・`..._s1d_trial_01.py`のPrompt文面、`er003_key_phrase_source_gate_01.py`・`er012_b_family_*`の`source_article_text`該当行。
- T-0結果(1行): **FAIL**。理由は「事前指定Grep一覧+追記位置・更新位置の手順」の見出しが、私が保存した複製で「事前指定Read・Grep一覧」に統合されていたため(原文の見出しは存在、保存時の複製ミス)。TTS関連のwarningは本委任に無関係。作業は継続した。
- 作成ファイル(2件のみ):
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md`
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md_check.json`
- 一時ディレクトリ(スクラッチパッド): `runner_e0ae8de0.py`、`agg.py`〜`agg5.py`(集計スクリプト)。リポジトリ内ではない。
- コード・SSOT・RESULT_PACKET・ACTIVE_TASKは未編集。git add/commit/pushなし。