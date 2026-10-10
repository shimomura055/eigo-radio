# PREREGISTRATION_03(D-det v2 差分の事前登録。確定後は結果を見ての基準変更・規則修正・再実行を禁止、E9は技術retryのみ可)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 委任_03 Phase 2b。確定日 2026-10-10。Production code/Prompt/CURRENT_SPECは変更しない。LLM追加call・後段AI追加なし(E9のR0 6 callのみ)。PREREGISTRATION_02(Phase 2a)の基準・腕・凍結入力は本ファイルで置き換えない(追記のみ)。
確定の担保: `b3r2_v2eval_03.py freeze`(または同等の手順)が本ファイルのsha256・`b3r2_rank_01.py`(v1)・`b3r2_rank_02.py`(v2)のsha256・凍結入力(台帳・topic)のshaを `frozen_b3r2_03.json` に記録し、評価・E9は毎回照合する(不一致=STOP)。

## 0. v2差分はpost-hoc修正である(開示)
- 発端: Phase 2aのBlind目視で、D-det v1(`b3r2_rank_01.py`)のcentral_bank_mortgageにて、Storylineの主役数値「25ベーシスポイント」が周辺に落ち、「12対0」「30年」が中核になった(危険な誤り1件)。原因は、Storyline側表記「25ベーシスポイント」(主数字25)とFact本文側表記「0.25パーセントポイント」(主数字0.25)が別物扱いで紐付かず、さらに台帳`numeric_value`欄(「25ベーシスポイント引き上げ」)との適格判定でも0.25が不一致になること。
- **本v2は、その結果を見てから設計した修正であり、独立予測ではない**。v2の規則(下記)は上記1テーマの結果を知った上で決めた。他8テーマでの副作用は「同一出力」を合格基準とすることで検証する。
- freeze前に1回、v2が動作するかの動作確認probe(`--probe`、frozen照合なし)を実行し、central_bankの差分を見た(25ベーシスポイントが中核化し、押し出しで7.40%が周辺になる、他8テーマは同一)。probe結果を見てv2の規則を追加修正はしていない(probe前のv2コードがそのままfreeze対象)。

## 1. v2規則(v1からの最小差分。`b3r2_rank_02.py` のdiffで確認可能)
Storyline表記とFact側表記の紐付けは、**値の正規化(単位換算)**で行い、台帳`numeric_value`欄の適格判定も同じ正規化を通す。
- V2-1 単位換算表(`canon_unit`): ベーシスポイント / パーセントポイント / %ポイント / ポイント → 同一単位`<pp>`。パーセント → `%`(％は既にNFKCで`%`)。
- V2-2 `main_numbers`: 単位が「ベーシスポイント」の数値は10進で100分の1に換算(25ベーシスポイント → 0.25)。「0.25パーセントポイント」「0.25ポイント」「0.25%ポイント」は0.25。
- V2-3 `_numbers_of`(適格判定の台帳側数値集合): 台帳欄の「N ベーシスポイント」に N/100 も加える(「25ベーシスポイント」という台帳欄で0.25パーセントポイントも適格)。
- V2-4 `unit_of`: `canon_unit`を通す(同一Fact内の概念束ねが単位表記ゆれに依存しない)。
- 変更なし(v1で対応済み): 全角半角(NFKC)、桁区切り(1,500=1500)、万・億・兆の桁展開(2億5,000万=250000000、1万5000=15000)、合成数。
- 対象外(今回の9テーマに実在しない): ASCII「bp」「bps」表記、%と小数(0.25=25%)の換算、為替・通貨間換算。出現した場合は未換算のまま(別物扱い)。Storyline表記の日付の包含(「9月16日」が「2026年9月16日」に紐付かない)はv1のまま(変更しない)。
- LLM追加なし、追加コスト0。

## 2. 合格基準(段階1、決定論・¥0、`b3r2_v2eval_03.py`)
1. central_bank誤判定の解消: Storylineの「25ベーシスポイント」とFactの「0.25パーセントポイント」が**中核**になる(Blind目視で、Storylineの主役数値が周辺に落ちる誤りが0)。
2. 副作用0: central_bank以外の8テーマで、v1とv2の出力(各表記のFact紐付け・role・適格・cap・capped_off)が**同一**。差分が出た場合は1件ずつ理由と良否を記載し、**説明不能な差分が1件でもあればSTOP**。
3. central_bank内の差分も全件説明する(予想: 25bpの中核化、cap枠6の押し出しで7.40%が周辺化)。押し出された数値が内容上重要でないかをBlind目視で判定し記載。
4. 既存注記検査(`b3_annotation_check_01.py`無改変、9テーマ): `annotator`欄(`DETERMINISTIC`)以外の問題が0 = 9/9。
5. 再実行完全一致(同一入力で2回、全表記・role・適格が一致)。
6. GT参考比較(C0のMERGED注記): v1と同じ方法で算出し併記。**既知値(D-detはC0に対する注記検査の判定を見て調整した規則)であり独立予測ではない**ことを明記。GT側の「25ベーシスポイント」「0.25パーセントポイント」は、v2では同じ概念キーになるためGT件数が1減る(55→54)点を併記。
7. Blind目視(v2のcore/peripheral一覧、9テーマ): 危険な誤り(Storylineの主役数値が周辺/無関係な数値が中核の主役扱い)が0。
- Closeout(段階1): 1〜5・7を満たす→D-det v2 `VALIDATED_PENDING_M10`(E9待ち)。2が不合格→`REJECTED`(v1に戻す選択はUSER_DECISION_REQUIRED)。

## 3. 段階2: E9計画(R0影響確認、main上、課金あり)
- 対象: 問題5テーマ(PROBLEM5)+byd_recall = 6テーマ。腕 = **D-det v2** のみ(各1回、R0 6 call)。対照 = ROOTFIX-01のE9既存出力(C0 = 現行brief、D = D-full・数値印なし)を再利用し、新規callしない。
- 入力組立: D-base(Dfull)のFact行(`assemble_D`)に、v2決定論の【事実N】【中核数値】【周辺数値】を挿入(`b3r2_eval_01.build_annotated`、無改変)。Storylineも印付き(Production runnerが注記版briefのStorylineを使う仕様[worker_new_r0]に合わせる)。制約ブロック(`constraints_text`、Fact外)は`compose_news_field`で後置き、制約行に【事実N】・数値印は付けない。
- R0: Fact Lock R0(`gpt-6-luna`、effort=high、Trial同一Prompt=`fl.apply_factlock_patches`)、JA Fact Check呼ばない(`full_ledger_text=None`)、R1/R2なし。技術retryのみ。
- 使用モデル: `gpt-6-luna`(Production R0と同一条件。gpt-6世代の最新だが最上位系かは未確認、例外理由=Production R0との比較条件同一性)。requested/returned model不一致はSTOP。
- cap **¥20**(根拠: R0実測約¥0.45/call、保守上限¥1.24/call、6 call上限約¥7.4)。`cost_ledger_b3r2_01.jsonl`に追記。超過見込みならSTOP。
- 評価(M10、決定論+Claude側の全文通読):
  1. 制約行への【事実N】付与 = 0(D腕で)
  2. 制約文の記事転記 = 0(制約文と記事の12字以上逐語一致、Fact本文由来を除く。ROOTFIX-01 E9と同定義)
  3. 台帳ID・台帳内部語の漏出 = 0
  4. 音声化禁止記号Gate該当 = 0(`safety.detect_prohibited_symbols`)
  5. タグ整合(使用タグ ⊆ Fact番号集合、`assert_no_tag_leak`)PASS率 = 100%
  6. 数値印の記事反映: 記事に出た数字のうち【周辺数値】由来の数字の数(0が望ましい。周辺数値を書いたらWriter側の違反として件数・内容を報告)、【中核数値】のうち記事に出た割合(報告のみ)、印のない数字の混入(丸め・換算・計算し直しがないか)
  7. central_bank: 「0.25ポイント(パーセントポイント)」が中核として扱われ記事に出るか、書き方が誤っていないか
  8. 印そのもの(【中核数値】【周辺数値】)の記事への漏出 = 0(`assert_no_tag_leak`で検出)
  9. R0全文の通読(Claude側): 制約が事実扱いされていないか、HF-007型「Ledger上では…」の転記、限定表現の反映
- 合格目安: 1・2・3・4・5・8 が満たされ、6で周辺数値を記事に書いた件数が0または説明可能、7が中核扱い。
- ROOTFIX-01のC0/D(E9既存出力)は数値印なしの条件であり、**本E9のD-det v2は条件が異なる(印あり)**。対照との差は「印の有無の効果」を含む(比較は参考)。

## 4. Closeout分類(最終、Trial限定。`VALIDATED`は`APPROVED_FOR_PRODUCTION`ではない)
- D-det v2: 段階1の基準+E9を満たす→`VALIDATED`。段階1不合格/E9重大不合格→`REJECTED`。基準は満たすが論点が残る→`USER_DECISION_REQUIRED`。Production採用はUSER_DECISION_REQUIRED(人間ユーザーのみ)。
- D-plus-single-call=`REJECTED`(Phase 2a機械分類)、Separate-call(Luna)=`REJECTED`(Phase 2a、Sol未実施)、役割宣言のみ=`VALIDATED`(Trial限定・no-harm、採用はPrompt変更を伴うためユーザー判断)。

## 5. U2 / U3(ユーザー判断事項、事前登録への追記)
- **U2** 「number_ranks不整合(LLM腕)の扱い(retry/STOPかfallbackか)」: LLM腕(D-plus・Separate-call)は不採用(REJECTED)のため、**該当なし**。D-det v2はLLMのnumber_ranksを使わないので不整合が発生しない。
- **U3** 「同一callでの構造化が第一候補」というユーザー確定に対し、**決定論方式(D-det)へ切り替える判断はユーザーが行う**。本Trialは判断材料(同一call構造化[D-plus]は応答時間・費用・STOP面で不合格、決定論は¥0で規則一致)を提示するのみで、切り替えは決定しない。

## 6. 逸脱・STOP
- STOP: v2で他テーマに説明不能な差分、既存注記検査FAIL(annotator以外)、E9 cap超過、mainへ戻らず60分、新LLM工程が必要。
- 結果を見ての規則修正・基準変更・再実行はしない(E9の技術retryのみ可)。

## 7. 成果物
`b3r2_rank_02.py`、`b3r2_v2eval_03.py`、`frozen_b3r2_03.json`、`eval_v2/`(v2_eval_results_03.json、diff_v1_v2_03.md、blind_sheet_v2_03.md、m11_v2/)、`e9/`(R0出力・評価)、`cost_ledger_b3r2_01.jsonl`、`RESULT_01.md`、`HUMAN_CHECK_B3R2_02.md`。
