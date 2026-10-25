# DESIGN_04(Trial-04 上流設計改善: Part 1=本文背景なし別LLM / Part 2=選定と執筆の分離)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_08(Phase 0。API 0円・Production変更0)/日付: 2026-10-25
Status: Trial承認済み(ユーザー2026-10-25、原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_04.md`)/ Production採用・配線: 未承認 / Opus条件Aレビュー待ち(`OPUS_REVIEW_REQUEST_02.md`)
実装: `run_trial_04.py`(DEV専用。Trial-03の`run_trial_03.build`・`run_trial_01`の本文/KPを流用。Production非参照) / Prompt全文: `PROMPT_04.md`・`_prompt_04_*.txt`

## 0. 要点(結論)
| 項目 | 内容 |
|---|---|
| Part 1 | 本文背景を持たない別LLMが、KPそのものの一般解説だけを書く。**推奨=案α(KPの英語表現のみを渡す)を主、案β(KP+本文での日本語意味)を比較腕**として同Trialで両方走らせ、評価で最終決定する(P1は1 call約0.15〜0.2円と安く、Trialの知見を最大化できる) |
| Part 2 | Step A(選定・本文全体入力・JSON出力・0件可・上限2)→Step B(執筆専念・入力は選定英文+構文名+要点+本文での位置づけ1文のみ)。選定理由(開発者向け)はStep Bに渡さないため、ユーザー向け本文への混入が構造上起きない |
| 後段Validator | 新設なし。引用逐語照合は既存の決定論スクリプト(check_quotes_03流用の`check_quotes_04.py`、評価時のみ)。Prompt混入確認は`run_trial_04.py dry-run`内の1回限りのgrep確認(Pipelineに組込まない) |
| 呼出数 | Trial-03=1 call/記事セット → Trial-04=4 call(P1・Step A・Step B・Part 3/4)、Part 2が0件なら3 call。費用 約0.28円 → 約0.5〜0.76円(推定。実測は委任_09) |
| Part 3/4 | Promptのブロックは03dと完全一致(`run_trial_04.p34_prompt`が`assert`)。変更は「出力するPartの宣言」と「Part 2で扱う文」入力の追加のみ |

## 1. 既存機構の確認(重複を作らない)
- 英語学習テキスト解説(Part 1〜4)の生成は**Productionに存在しない**(`*.py`のGrep: `英語学習テキスト解説`・`Vocabulary & Expressions` 該当0)。Trial-01〜03はDEV専用で、本Trial-04もDEV専用。Production配線は未承認。
- Production側のKP関連: `er003_key_words_gloss_alignment.py:128` `NEWGEN_MEANING_FIELDS=("meaning_in_text_en","naive_ja","naive_ja_conveys")`、`:95` `japanese_gloss`。つまり「本文中の意味」はProduction KP glossが既に確定しており、Trial-04はそれを**そのまま表示用の確定値として使う**(Part 1の別LLMに再生成させない=重複処理を作らない)。`meaning_in_text_en`は本文文脈を使って作られる英語の言い換えなので、別LLMには渡さない(本文に引っ張られる経路になるため)。
- Production音声側のKP英語解説(`kp_explanations.json`等、音声用)は別成果物。Trial-03ではPart 1 Promptに「既存の音声解説(重複回避用)」として渡していたが、Trial-04のPart 1別LLMには**渡さない**(本文文脈由来の説明を持ち込まないため)。学習テキストと音声の重複は、役割が異なる(音声=短い英語定義、テキスト=日本語の一般解説)ため許容。
- 将来の配線位置(参考。未承認): KP確定(canonical化+gloss整合)の**後**に、Advanced学習テキスト生成の独立段として置く。入力はKP英語表現(+β案ならgloss)のみなので、本文生成・KP選定・gloss整合の既存段を一切変更せず、後付け可能。

## 2. 入力(既存工程の確定値)
- 本文・KP: Trial-03と同一(`INPUT_CHECK_03.md`の出典・sha。賢者=`.../the_gift_of_the_magi/run_sf_prod_01/writer/r2.md`、イグ・ノーベル賞2026=`er019_output/ig_nobel_2026/run_nws_02/b1b/article.md`[`## In one line`除外]、開いた窓=`.../the_open_window/run_sf_prod_01/writer/r2.md`)。
- 「本文中の意味(日本語)」: Production KP gloss(`run_trial_01.KP`・`run_trial_03.WORKS`の`g`欄、`keywords_canonicalized.json`由来)を使用。どちらを使ったか=Production gloss。
- 本文引用英文: KPの`本文の該当文`(本文から逐語。`run_trial_03`が`s in text`をassert)。
- 引用英文の日本語訳: 既存工程に独立した確定訳はないため、Trial-03(03d第1標本)の項目4を`INPUT_04.json`に**固定**して全Runで共通利用(`run_trial_04.py make-inputs`、出典は`OUTPUT_03d_<work>_RAW.md`)。Trial-04の評価対象外(Beforeと同一値にすることで差を生まない)。

## 3. Part 1 設計
### 3-1. 表示(組立は決定論。LLMを使わない)
`1 英語表現 / 2 日本語の意味(本文中での意味)[確定値] / 3 本文中の英文[確定値] / 4 英文の日本語訳[確定値] / 5 解説[別LLM]`。表示名「実用性を重視した解説」→「解説」。本文中の意味(2〜4)と一般解説(5)はUI上も物理的に別欄で、別LLMは2〜4を生成しない。
### 3-2. 別LLMに渡す情報の比較
| 案 | 渡す情報 | 利点 | 懸念 |
|---|---|---|---|
| α(推奨・主) | KPの英語表現のみ(本文・あらすじ・gloss・引用文・作品名なし) | ユーザー指摘の根本原因(本文への引きずり)を入力段で完全に遮断。原則「記事全文・あらすじ・物語背景を受け取らない」に最も忠実。 | 多義のKPで、本文の意味と異なる意味から説明を始める可能性(本文中の意味との矛盾の評価が必要) |
| β(比較腕) | KP+本文での日本語意味(gloss)のみ | 多義語の取り違え・本文中の意味との矛盾を防ぎやすい | glossが「崩れる」等の場合、字義(地面が崩れる)へ再び引きずられる恐れ。Promptで「この意味に偏らず核となる意味から」と指示して緩和 |
推奨理由: ユーザーの現状課題が「本文に引っ張られる」なので、まずαで遮断し、矛盾が出たときだけβを正式採用する。P1は1 call 0.15〜0.2円で、両腕を同Trialで走らせても追加約0.5〜1円と安いため、**Trial-04内でα(全6セット)とβ(各作品1セット)の両方を実行して比較**する(Charter 2「1回のTrialで多くの知見」)。判定ルール(事前登録): αで「gloss/本文中の意味との矛盾」が3作品9KP中1件以上出たらβを採用候補、0件ならα。
### 3-3. 複合表現
入力側で「学習価値の中心語句」を人手指定する方式は採らない(量産でKPごとの指定が必要になり、手間とばらつきが増える)。Promptで「複合表現では、学習価値の中心となる語句を中心に説明してよい」と汎用に指示し、LLMに判断させる。`nutrient-rich`等の個別例はPromptに入れない(Trial-03同様、参考例を入れると評価にならない)。
### 3-4. Promptの要点(全文は`PROMPT_04.md`)
観点=核となる意味/主要用法と場面/コロケーション/類義語との違い/自然な比喩・拡張用法を、機械的列挙でなく必要十分な自然文で。使用頻度順位の根拠なき断定・類義語差の過度な断定・不自然な用法の創作・水増し・文法への脱線を禁止。Trial-02で承認済みの「独立した追加例文は書かない」を維持(コロケーション表記は可)。

## 4. Part 2 設計
### 4-1. Step A(選定、本文全体入力)
- 入力: 番号付き本文全体+選定観点(ユーザー指定5観点。文法用語の難しさ自体を評価しない)。03d由来の「基礎文法は埋め草にしない」「0件可」「上限2」を維持。
- 出力JSON: `candidates_considered`(DEV専用、最大5件、採否理由1行)/`selected[]`(`para`・`sentence`[逐語]・`construct_ja`・`points_ja`≤3・`context_ja`[本文の事実のみ1文]・`reason_dev`[開発者向け選定理由])/`none_reason_dev`。
- 0件判定の置き場: `selected=[]`。0件ならStep Bを呼ばず、決定論の固定文(「今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。」)を表示(LLMに「無理に作る」余地を作らない)。
- 倒置・後置修飾などの見落とし対策: Step Aは本文全体を見て候補比較を内部で行い、`candidates_considered`に残す(DEV。見落とし評価に使う)。Prompt内に作品固有の構文例は入れない(賢者の`handed down`・倒置は参考例として評価時の基準にのみ使う)。
### 4-2. Step B(執筆専念)
- 入力: `sentence`・`construct_ja`・`points_ja`・`context_ja`のみ。**`reason_dev`と`candidates_considered`は渡さない**ため、開発者向け選定理由・難易度評価がユーザー向け本文へ混入する経路がない。本文全体も渡さない。
- 出力: 日本語訳→文法・構文の仕組み→(必要なときだけ)通常表現・語順との比較→意味・ニュアンス・表現効果。ユーザー表示は先頭に「対象となる本文英文」(Step Aの逐語文を決定論で挿入)。選定理由・難易度・品質判定・工程への言及を禁止。
- `context_ja`をStepBに渡すのは、Trial-03で評価された「表現効果を作品の文脈と結びつける」ため(本文全体を渡さず、1文の事実メモだけ)。Opusレビュー論点(b)。
### 4-3. Part 3/4
03dのPart 3/4ブロックを**一字一句そのまま**使い、別callで生成する。Part 3の「Part 1・2と重複させない」を保つため、Step Aの選定文のみ入力に追加(Part 1の解説文は渡さない=Part 1との重複回避はKPリストに依存。Trial-03との差として評価で確認する)。Part 3/4はStep Aの完了を待つ(依存)。

## 5. 呼出構成・処理時間・費用
依存: P1とStep Aは独立(並列)→ Step BとPart 3/4はStep A後に並列。
| call | 入力 | 出力 | 費用/円(推定) |
|---|---|---|---|
| P1(3KPまとめて1 call) | 約0.5〜0.7k token | visible約1.0〜1.4k+reasoning 0.5〜1.0k | 0.14〜0.20 |
| Step A | 約1.9〜2.2k | JSON約0.7k+reasoning 1.0〜2.0k | 0.15〜0.23 |
| Step B(1〜2件まとめて1 call) | 約0.5k | visible 1.0〜1.5k+reasoning 0.3〜0.8k | 0.11〜0.19 |
| Part 3/4 | 約2.0〜2.3k | visible約0.6k+reasoning 0.3〜0.8k | 0.10〜0.14 |
| **合計** | | | **約0.50〜0.76円/記事セット**(Part 2が0件なら約0.39〜0.57円) |
推定の出典: `usage_03d_*.json`(1 call: input 2.7k・output 2.7〜3.7k[reasoning 0.9〜1.8k]・0.22〜0.34円・28〜39秒)。単価=Luna input $0.10/M・cached $0.01/M・output $0.50/M(¥160/$、Trial-01〜03と同一式)。出力tokenが費用の約88%を占めるため、Part別の出力量で按分した。
- Trial-03比: 約+0.2〜0.5円/記事セット(約1.8〜2.7倍)。70円/記事セット目標に対し約0.7〜1.1%(Trial-03は約0.4%)。
- 処理時間(推定): P1∥Step A約25〜40秒 → Step B∥Part 3/4約20〜30秒 = **約45〜70秒**(Trial-03は28〜39秒)。逐次実行なら約80〜120秒。
- 呼出削減の代替(今回は採らない・記録のみ): ①Part 3/4をStep Aと同一callにする(−1 call、約−0.1円。Step Aの選定に執筆が混ざる懸念)。②P1を3 call(+0.2円・並列でも時間不変。KP間の干渉は消えるが費用増)。品質が基準を満たしたうえでの費用最適化は、成立後に別判断。
- Trial-04の費用見積(委任_09): 3作品×N=2=6セット(24 call≈3.0〜4.6円)+β腕P1 3 call(≈0.5円)=約3.5〜5.1円。1回の再設計ループ分(同額)を見込んでも約12円以内。Fable上限20円(自律枠)に収まる。

## 6. 評価計画
- 条件: 同3作品、各N=2(r1・r2、同一Prompt・同一入力)。Before=03d(第1標本、イグ・開いたには第2標本03dR2もあり)。α腕は全6セット、β腕はr1のP1のみ。
- 出力ファイル: `OUTPUT_04_<work>_<run>_USER.md`(学習者向け完成形。Part 1〜4)と`OUTPUT_04_<work>_<run>_DEV.md`(Step A候補・選定理由・usage)に分離(`run_trial_04.py`が生成)。
- 評価観点(ユーザー原文§6)と事前登録の基準:
  - Part 1: ①核の意味から説明しているか(give way/at a moment's notice/nutrient-richで本文固有の字義・用法から始めていないか) ②主要場面・コロケーションの有無 ③類義語差・拡張用法の正確性 ④gloss(本文中の意味)との矛盾なし ⑤創作用法・水増し・頻度順位の断定なし。
  - Part 2: ①基礎文法のみの選定でない(賢者で基本の`whose`だけに戻らない) ②賢者=後置修飾(`handed down`)または倒置など学習価値の高い文を選ぶ/見落としは`candidates_considered`で確認 ③イグ・ノーベル賞/開いた窓: 2 Runで選定の判断(0件か、どの文か)が安定し、基礎文法で埋めない ④ユーザー向け本文に開発者向け語(選定理由・学習価値・難易度・Advanced・理解しにくい等)が無い(評価時のgrep) ⑤0件時に無理に作らない。
  - 引用逐語照合: `check_quotes_04.py`(check_quotes_03と同ロジック、評価時のみ)。
- 再現性(N=2)で言えること: 同条件で選定・0件判断が一致するかの観察のみ。統計的な安定性や確率は主張しない(Trial-03と同じ限定)。
- 採否判断: 基準を満たした時点でTrialを終了し磨き込みを追加しない(ユーザー原文§7)。満たさない場合、Prompt微調整の反復ではなく、原因(Step Aの選定観点/Step Bへの受け渡し/P1の入力)に応じて工程設計を見直す。

## 7. Validator新設なし・既存資産再利用
- 追加の判定Gate・Checker・Validatorなし。工程出力の組立(parse)は構造の解析のみで、不合格時に再生成する機構を持たない。parse失敗は例外停止し、手動で原因を確認する(自動再試行ラッパなし)。
- 再利用: `run_trial_03.build`(03d Prompt生成)、`run_trial_01`の本文/KP、`check_quotes_03`の逐語照合ロジック、`usage_*.json`形式。

## 8. 禁止事項の確認
Production code/Prompt/flag変更0、KP追加選定なし、音声生成なし、Web検索なし、Part 3/4 Prompt変更なし(ブロック一致をassert)、Checker/Validator新設なし、API呼出0(`real_llm`は`TRIAL04_PAID_APPROVED=1`が無い限り`assert`で拒否)。

## 9. 委任_09 反映(Opus条件A、`OPUS_REVIEW_02.md`)
- M1: `run_trial_04.resolve_verbatim`/`parse_stepa`(本文側文字列への差替え、見つからなければ例外)。selftestで曲がったアポストロフィ差替え・不一致例外・全文(3作品122文)の引当てを確認。
- M2: `PREREGISTERED_CRITERIA_04.md`(矛盾=語義不一致のみ/α→β切替は両側条件/`bound to the protein`別集計/Part 2数値固定/本文引っ張り再現時は設計見直し)を**生成前にcommit**。上記§3-2の旧ルール「αで矛盾1件以上ならβ」は、事前登録の1-4両側条件に置換(旧ルールは撤去・本節が上書き)。
- R1: Step Bへ前後1文の逐語(決定論取得)を追加(`local_context`)。R2: Part 3/4へPart 1解説を入力。R3: Step A Promptに評価語禁止の1行。R4: KP引用英文と一致する選定文に固定訳を参考訳として渡す。R5: 各作品でStep Aのみr3・r4、β P1をr1・r2。
- 安全線: 実行は`TRIAL04_PAID_APPROVED=1`必須、累計18円で新規call拒否(`CAP_JPY`)、parse/call失敗は記録のみで自動再試行しない。
