# TRIAL_PREP_REPORT_01(FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01 準備報告 全文)

> 本文は委任_01 sonnet-workerの最終報告(2026-10-17)を無改変で転記。Opusレビュー前。採用判断はユーザー

RLCT 委任_01 完了報告(Phase A、JPY0・API呼出0・Production無変更)。Status=TRIAL_PLAN_READY_COST_APPROVAL_PENDING。commit 17b1625a2 を origin/main へ push 済み(スクリプトとJSONとdelegation_logのみ)。

# 0. 先に読むこと(逸脱3点)
1. md成果物4点(ASSET_INVENTORY/PRE_ANALYSIS/ARTICLE_SELECTION/TRIAL_DESIGN/COST_ESTIMATE)はファイル化していない。私の実行環境に「レポート・分析のmdを書かない、本文で返す」という制約があり、RLCO委任_01と同じ扱いにした。本文は下の§2〜§6にある。ファイル化は Fable が行う(保存先は委任文どおり docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/)。再現可能な数値は commit 済みの .py/.json に入っている。
2. SSOT(DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/USER_DECISION_REGISTER)は編集していない。md設計書が存在しない状態で参照を書くと Dangling Reference になるため。追記文案は§8。ACTIVE_TASK.md(gitignore)の固定ヘッダだけ更新した。
3. 委任文の保存(T-0)は、「ユーザー指示(原文)」節を別ファイル_USER.mdに一字一句保存し、委任_01.mdではその節を見出しの記録に置換した。他節も一部要約している。T-0補足(a)の「要約不可」からの逸脱なので、必要なら Fable が原本で上書きしてほしい。
- T-0: check_delegation_prompt = PASS(reasons=[]、warning1件=TTS予算言及、本委任はTTSなし)。
- _USER.md: 4,038文字、8,829バイト、sha256=e6bc729b1f197c8201ec8feecd9c2e90bab728286fe4cfc79b30c07ebaf96b0c(LF、保存前の作業コピー値。gitのCRLF変換前)。
- STOP確認: stop_scope_check rc=0(非停止、applicable=[])。

# 1. 5記事×4方式の比較表(ユーザー§10の最初の項目)。ここは実行前の計画値であり実測はない
新規API費用(JPY、期待/上限)。出典=cost_estimate_01.json(manual_substitution)。上限は「全記事で再選定2回」を積み上げた最悪値で、現実の見込みではない。

| 記事 | Fact数(B3可視)/B3採用 | 従来 | 案1 | 案2 | 案1+案2 |
|---|---|---|---|---|---|
| Coffee fxpw_01 | 17/4 | 0/0(既存B3がsol6.1) | 34.0/42.0 | 18.0/58.3 | 6.8/45.2 |
| openai_copyright | 8/5 | 9.1/10.9 | 18.1/21.3 | 15.9/47.5 | 6.7/36.6 |
| inbound_tourism | 13(draft15)/4 | 12.0/14.4 | 38.1/46.9 | 21.9/67.6 | 9.5/53.2 |
| streaming_price | 7/6 | 10.2/12.2 | 19.8/26.9 | 22.6/55.0 | 11.0/42.7 |
| central_bank_mortgage | 11/6 | 11.3/13.6 | 18.7/22.1 | 16.9/53.3 | 5.6/39.8 |
| 合計 | | 42.7/51.2 | 128.8/159.3 | 95.2/281.8 | 39.6/217.4 |

- 総合計(Stage 1の4方式): 期待約JPY306、上限約JPY710。
- 案1+案2の初回B3は案2と共有する設計にしたので、案1+案2の表の値にはB3が入っていない。
- 従来のB3は、Coffee以外の4記事で再実行が必要(§3-3)。
- 品質欄(B3構成差、Fact品質など)は有料実行後にしか埋まらない。

# 2. 案1の事前分析(PRE_ANALYSIS_SEARCH_CAP_01相当)
対象は12 run。search_cap_analysis_01.json に全Fact表がある。run は Coffee fxpw_01、l3_01、Meta sol61_01、Meta b3_wiring run_01、er052 stage_r の6記事(byd、central_bank、inbound_tourism、openai_copyright、semiconductor、streaming)、gpt6_wiring run_01、run_02。

## 2-1 結論: Fact単位の呼出回数は復元不能
- 根拠は2つ。
  - verification_full_record.json の search_usage は、web_search_call_count(総数)と queries(文字列の並び)の2項目だけ。
  - 保存関数 `er002_ja_web_research_r3.py:65-81` は、response.output の web_search_call を数え、action.queries か action.query の文字列を平坦化している。action.type(search / open_page / find)と、どの呼出がどのクエリを持つかを捨てている。
- 実測の呼出数/クエリ数の比が一定でないのは、この平坦化のため。
  - Coffee fxpw 14/24(0.58)、streaming 7/23(0.30)、openai 5/11(0.45)。
  - Meta 7/6(1.17)。ここは呼出がクエリより多く、open_page / find の混在を示す。
- 次の3つは復元できない。復元不能と明記し、推測では埋めていない。
  - 各呼出の種別。
  - クエリからFactへの対応(ログに無い)。
  - 「何回目で裏付けに到達したか」。判定は応答末尾にしか出ず、中間状態は未保存。
- Ledgerは全Factを1回のAPI呼出で検証している(`er012_e_family_entertainment_two_level_runner_01.py:206-226`、`er019_family_x_entertainment_production_runner_01.py:97-141`)。そのため「Fact当たり3回」は、API側で強制できず、Promptでの依頼になる(ソフト上限)。厳密に強制する手段は2つあるが、どちらも要確認。
  - Fact別にAPI呼出を分ける。この場合、下書き全文を毎回再送するトークン増がある。
  - 総呼出数の上限パラメータを使う。Fact単位ではなく、API仕様は未確認。

## 2-2 代替指標(クエリ→Fact推定、heuristic)
- 方法: クエリ中の数値と固有語を、Factのclaim・numeric_value・source・verification_notes との一致で照合した。同じ文書を共有するFact群(例 F16+F17)は群として扱った。
- 割当率は低い。fxpw は24クエリ中、一意9、曖昧12、弱3。上限なしの削減額は下限側に偏る。
- 打切り削減額(JPY、下限寄り)。クエリ単位で上限N、Fact群は N×群サイズ。

| run | 上限2 | 上限3 | 上限5 | 喪失リスク候補(上限3) |
|---|---|---|---|---|
| Coffee fxpw | 4.07 | 2.03 | 0 | F16・F17(両方AMBIGUOUS) |
| Coffee l3 | 3.66 | 2.44 | 0 | COFFEE-013(VERIFIED、非採用) |
| inbound | 5.37 | 2.15 | 0 | F11(VERIFIED、非採用)。上限2ではF01(採用、VERIFIED)も候補 |
| streaming | 4.25 | 3.18 | 2.12 | **F04(VERIFIED・採用)が9クエリ**。上限5でも候補のまま |
| semiconductor | 1.96 | 1.31 | 0 | F1(AMBIGUOUS・採用) |
| openai | 0.79 | 0 | 0 | |
| その他6 run | 0 | 0 | 0 | |

- 呼出単位で上限N(比率換算)にすると、ほとんどの run で上限3は拘束しない(l3 は0.87、inbound は0.13、その他は0)。
- RLCOの手計算では fxpw が上限3で約5.1円だった。heuristic は 2.03 円で、これは下限側。真値はこの間にあるが、確定できない。
- 「VERIFIEDだったFactが打切りでAMBIGUOUSに落ちるか」は、上のFact数は上限であって予測ではない。判定が変わるかは再実行しないと分からない。
- RLCOの「無駄はF16/F17型の反復」は、fxpw では裏付けられる。ただし他11 run では目立った集中が少ない。つまり案1の効果は記事依存で、Coffeeは大きい側の例外。

## 2-3 「上限3回」の妥当性
- 明らかに不適切とは言えない。STOPしない。
- 論点は「厳しすぎる」より「効かない記事が多い」。呼出単位なら多くの run で拘束せず、削減はほぼ0〜2円。
- クエリ単位の上限3なら、streaming F04 のような採用VERIFIED Factが打切り対象になり得る。
- 推奨: 暫定上限は3のままとする。ただしTrial harnessで、呼出単位のログ(action.type、queries、順序)を新規に保存する(§4-2)。単位が確定すれば、上限の評価がFact単位で可能になる。ユーザー指示の「3回」は、呼出単位かクエリ単位かが未定義なので、Trialでは「web_search_call単位で3、ただしopen_page / findは別枠でログのみ」と定義する案(Fable確認事項、B区分)。

## 2-4 案1b(版・発行年月・出典内該当箇所の引継ぎ)
- 測定可否: 既存データでは不可。
- 根拠: 12 runのfact_ledger_draft.jsonに現れるキーは15種(fact_id、claim、subject、date_or_period、scope、conditions、numeric_value、numeric_scope、causal_strength、source_title、source_url、source_type、support_level、ambiguity、notes_for_writer)で、版・発行月・該当箇所の欄が無い。
- 補完にはResearcherの再実行が要る(新規Research 1記事あたり約JPY14〜29)。これは「既存データから取得できない情報を新たな有料Researchで補完しない」に反するので行わない。
- 必要性の実例(5記事中2記事に出ている)。
  - fxpw F16 / F17: USDAのURLが最新版の別名を指し、2025年12月版が返った。
  - inbound F05 / F06: 推計値42,683,600と確定値42,683,301の差。F05は「確定発表」というラベル誤りでREJECTED。
- 案1bはこのTrialでは効果測定不可と記録し、上限制御の効果とは混ぜない。

# 3. 棚卸し(ASSET_INVENTORY_01相当)と5記事選定
## 3-1 Family X経路で保存済みResearch下書き(draft)を持つ記事
- 全て `er019_family_x_entertainment_production_runner_01.py` 経由(entry_point.json で確認)。er052 stage_r の6記事は stop_after=storyline_b3 で、Research・Ledger・B3が揃っている(ja_writerは無い)。
- Researcher・Verifier Promptは全runで同一(静的部分のhashが一致)。Researcher draftと既存Ledgerは、比較基準として再利用できる。

| 記事 | run | Fact数 | VERIFIED/AMBIG/REJECTED | B3採用 | Ledger検索 | 作成日・Ledger model | B3 model |
|---|---|---|---|---|---|---|---|
| Coffee | er019 coffee_prices/run_fxpw_01 | 17 | 13/4/0 | 4 | 14回 JPY25.13 | 10-16 gpt-6-luna | gpt-6.1-sol(JPY10.94) |
| Coffee | run_l3_01 | 19 | 18/1/0 | 5 | 14回 | 10-10 gpt-6-luna | sol系 |
| Meta(AI) | meta/run_sol61_01、family_x_b3_production_wiring_01/run_01 ほか(同draft・複製) | 15 | 15/0/0 | 3 | 7回 JPY14.27 | 09-26 gpt-5.6-luna(旧) | sol6.1(JPY6.96) |
| AI(Broadcom決算) | er052 stage_r/semiconductor_earnings | 6 | 5/1/0 | 5 | 3回 JPY5.58 | 10-08 gpt-6-luna | gpt-6-luna |
| AI(訴訟) | stage_r/openai_copyright | 8 | 8/0/0 | 5 | 5回 JPY9.01 | 10-08 | gpt-6-luna |
| 社会(訪日客統計) | stage_r/inbound_tourism | 15(B3可視13) | 11/2/2 | 4 | 16回 JPY28.26 | 10-08 | gpt-6-luna |
| 社会/制度(Fed) | stage_r/central_bank_mortgage | 11 | 11/0/0 | 6 | 4回 JPY7.38 | 10-08 | gpt-6-luna |
| 消費(Disney+) | stage_r/streaming_price | 7 | 5/2/0 | 6 | 7回 JPY12.78 | 10-08 | gpt-6-luna |
| 複数出来事 | stage_r/byd_recall | 11 | 11/0/0 | 5 | 3回 JPY5.55 | 10-08 | gpt-6-luna |
| 小物(ミニバッグ) | er052 gpt6_wiring_e2e_01/run_02 | 6 | 6/0/0 | 3 | 4回 | 10-08 | |

- 参照のみ(使わない):
  - Hormuz系(er019 diversity/refresh/an3): 保存は verified_fact_ledger.txt のみ。draft欠落。
  - Family A/B/C/他系(er003、er012 sewer、er017)の verification_full_record.json: 形式は同じ(同じ関数が出力)だが、Prompt・経路が別。改修・利用はしない。
  - open233 after_pprime: Meta複製。
- **重要な発見**: stage_r の6記事のB3は gpt-6-luna(JPY約0.5)で実行されている。現行Production(2026-10-11以降)のB3は gpt-6.1-sol(JPY約7〜11)。つまり、Coffee以外では既存B3を従来方式の基準に使えない。従来方式として gpt-6.1-sol のB3を新規に1回走らせる必要がある(§5に含めた)。
- もう一つ: 既存Ledgerは10-08〜10-16の時点のWebに対する結果。Trialでの再検証は本日のWebに対して行うので、情報更新やURLの別名の指す先が変わることによる差が、方式差に混ざる。この切り分けが§4-4の統制(同日・上限なしの再検証)である。

## 3-2 5記事選定(確定案)。新規Researchは不要、テーマ選定をユーザーに求める必要もなし
保存済みのテーマを比較素材として再利用するもので、新規記事の生成ではない(PM_GOVERNANCE 13節の対象外と判断。反対意見があればFableで判断)。

| # | タイプ | 記事 | 選定理由・検証難度の特徴 |
|---|---|---|---|
| 1 | 統計・価格 | Coffee fxpw_01 | 17 Fact、採用4(比率24%、案2が最も効く)。版違い(USDA 7月/12月)、季節調整ラベル誤り(F12)、曖昧4、因果(F05/F09)、時系列。基準B3(sol6.1)あり |
| 2 | AI・テクノロジー | openai_copyright | 8 Fact。訴状提出段階と判決の区別(断定禁止)、14原告、Reuters報道とコメント状況。全VERIFIED(易)。代替=semiconductor_earnings(6 Factで採用5、案2の効果が出にくい)、Meta(15 Fact、旧モデル) |
| 3 | 社会・制度 | inbound_tourism | 公的統計(JNTO・観光庁)。推計vs確定の版違い(F05/F06)、REJECTED 2(F05、F12)、AMBIGUOUS 2(F04、F06)。時系列比較(2019年比)。**自然にREJECTEDが出る唯一の記事で、案2の再選定loopが実際に動き得る**。F05(年間過去最多)は物語の中心になり得る |
| 4 | 生活・消費 | streaming_price | Disney+値上げ。適用時期の二段階(9/23新規、10/21既存)、「最新」「主要」の範囲が曖昧(F01 AMBIGUOUS)、理由が未確認(F07)。7 Factで採用6(比率86%)。案2の効果が小さい側の例外。streaming F04は9クエリ |
| 5 | 複数出来事・出典 | central_bank_mortgage | FOMC決定(9/16)、議事要旨・SEP(予測)、Freddie Mac金利、AP報道、セントルイス連銀解説の複数出来事・出典。因果(政策金利→住宅ローン金利)と予測/実績の区別。全VERIFIED(検証は易)。代替=byd_recall(二本の召回公告、全VERIFIED) |

- 難度の分散: 統計と版違い(1、3)、曖昧(1、3、4)、時系列(1、3、5)、因果(1、5)、断定禁止/段階(2、4)。REJECTEDを持つのは3のみ。
- 採用比率: 0.24、0.62、0.31、0.86、0.55。Fact数と採用比率が案2の削減幅に効くので、傾向と例外が出せる。
- 検証難度の偏り: 5記事のうち全VERIFIEDが2(openai、central)あり、重大Factの見逃しを検出する力は弱い。見逃し検出はinbound・Coffeeに依存する(受入条件7の限界として明記)。

# 4. Trial設計書(TRIAL_DESIGN_01相当、**Opusレビュー前**)
## 4-1 4方式の定義と再利用
共通: Research draftは全方式で共用(再実行しない)。以下は新規実行が必要な段。
- 従来方式(M0): 既存Ledgerを再利用。B3は、既存B3がsol6.1の記事(Coffee)なら再利用、他4記事は gpt-6.1-sol で新規1回(既存Ledger入力)。
- 案1(M1): 全Factに対しLedger検証を上限付きPromptで再実行 → その結果でB3(sol6.1)を新規1回。
- 案2(M2): 検証前のdraft全Factを渡す試験版B3(初回)→ 選定Factだけをtrial版Verifierで検証 → REJECTEDなら再選定loop(最大2回)。
- 案1+案2(M3): M2の初回B3選定を**共有**(同一入力なので、新規B3は呼ばない。選定の確率差を取り除く)→ 選定Factだけを、上限付きPromptで検証。REJECTEDが出ればM3専用の再選定。
- 統制(Stage 1に含める): M0b = 従来方式のB3を各記事で追加1回(自然な生成ばらつきの基準)。約JPY54。
- 統制(Stage 2、条件付き): 同日・上限なしのLedger再検証(M0')。Webの更新・版違いによる差と、上限による差を切り分ける。1〜2記事で約JPY16、全5記事で約JPY83。

## 4-2 harness構成(Production runnerは無変更)
- Trial専用script `er082_rlct_trial_01_run.py`(案)。既存関数を import して呼ぶだけ(`efam.run_verification_for_topic`、`b3._call_once`、`vfl01.build_verified_ledger_text`)。Productionのファイルは触らない。
- 出力先は `er082_output/rlct_trial_01/<article>/<method>/`。Production runnerの出力dirとは別。Productionのhash(runner、B3、vfl01、routing)をrun前後に記録し、不変を確認する。
- 上限付きVerifier: 既存 `VERIFICATION_PROMPT_TEMPLATE`(`er003_v1_en_direct_vfl_01_generate.py:228-250`)の末尾に、「各Factで確認のためのWeb検索はweb_search呼出3回まで。3回以内で確認できなければAMBIGUOUSとし、理由を記載(既存の曖昧Factを無理に確定しない規約=`:282-292` と整合)」の指示を追加した試験版Promptを使う(Prompt本体は複製し、Productionは編集しない)。
- 呼出計測点(新規): response.output の web_search_call を1件ずつ保存する。action.type、action.queries/query、順序、取得URL(あれば)。これで「Fact別・呼出別」が初めて復元可能になる。
- 案2のB3試験版:
  - 既存の `USER_PROMPT_TEMPLATE`(`er019_family_x_storyline_b3_fact_selection_01.py:51-80`)は「独立検証済み」と書かれ、`FACT_ID_LINE_RE`(`:129`)は `[VERIFIED]` / `[AMBIGUOUS` 始まりの行しか拾わない。検証前draftは `[UNVERIFIED]` タグ付きで渡すため、試験版Promptと試験版ID抽出関数が必要(複製)。
  - 違いは「検証済み」の語と、タグだけに限る(Prompt差による交絡を最小化)。
  - 再選定の入力口: `_call_once` に `extra_note` 引数があり、本文末尾へ文字列を追加できる。ここに不合格理由と既存検証結果を渡す(本体の改修は不要)。
- 検証結果の再利用: 検証済みFact(fact_id × draft sha256 をキー)は再検索しない。

## 4-3 案2の再選定loop(ユーザー§4の8手順を忠実に)
1. Research候補全体を渡して初回B3。
2. 選定Factだけを独立検証。
3. REJECTEDがあれば、**機械的に削除せず**、B3へ(不合格Factのid・verdict・verification_notes、既に検証済みの他Factのverdictとnotes、未検証の候補一覧)を extra_note で返す。
4. B3がStorylineを再評価。REJECTEDを使わずに成立するか、別Factの追加が必要かをB3が決める。
5. 新規に選ばれたFactだけを検証。
6. 最大2回の再選定。上限に達した、または検証済みFactで成立しない場合は**未成立として記録**し、品質を犠牲にして確定しない(確定ファイルを出さない)。
- AMBIGUOUS: 再選定のトリガーにしない(ユーザー指示はREJECTED)。ただしAMBIGUOUSが中心Factになった割合を指標として記録する(B3が未検証で選ぶため、断定禁止タグを知らないで選ぶ構造的な差)。
- 最終Ledger(`verified_fact_ledger.txt`)は選定Factの検証済み分だけを `vfl01.build_verified_ledger_text` で組み立て直す。その関数は検証結果が無いFactをAMBIGUOUS扱いにするので、未検証の非選定Factを混ぜない。

## 4-4 評価手順
- 記録項目(§6の全項目): LLM/検索費用別、呼出数・クエリ数(新規計測)、Fact verdictの遷移(VERIFIED維持/AMBIGUOUS化/REJECTED/昇格)、B3の採用Fact・主題・展開・結論、再選定回数・追加費用・未成立。
- B3構成差の判定: 機械指標(採用Fact ID のJaccard、storyline文の差)+3段階の人手ルーブリック(軽微=同じ主張・骨格、中程度=焦点・展開の変化、重大=主題・結論・骨格の変化)。方式名を伏せて判定する(ブラインド)。構成差の大きさと品質の良し悪しは別列で判定する。
- 判定者: 机上=Sonnet、独立=Fable、重大判定または不一致のときだけOpus。
- ばらつき切り分け: 従来B3を各記事で2回(M0とM0b)取り、その差を「自然なばらつき」の基準とする。方式間の差が基準の範囲を超えたら方式効果と見る。重大差が出て判別できないときだけ、Stage 2(追加費用ゲート内)で追加再現を検討。
- 誤りの見逃し: 既存の人手確認済みの欠陥(Coffee F12ラベル誤り、F07部分欠落、F16/F17版違い、inbound F05確定ラベル誤り・F12時期誤り、streaming F07)を既知の正解として、各方式が検出し続けるかを見る。ただし5記事では低頻度の重大誤りを統計的に否定できない(ユーザー§7どおり)。

## 4-5 Fact Lock / RFとの整合(JPY0で実施可能)
- 各方式のTrial出力dir(`research_ledger/verified_fact_ledger.txt`、`storyline_b3/selected_brief.md`、`fact_selection_evidence.json`)に対し、`er053_b3_deterministic_producer_01.annot.produce_annotated_b3`(LLM 0 call)と `er053_b3_annotation_contract_01.validate_annotated_b3` を実行する。契約検証がPASSすれば、W-1のFact Lock入力として成立する(入力パスは `er053_b3_deterministic_producer_01.py:844-845` で確認)。
- RFは `parse_ledger_complete`(`er053_risk_flagger_production_01.py:169-194`)で台帳の完全性を検査するだけなら、JPY0で台帳形式の整合を確認できる。記事を伴うRF本実行(Writer W-1が約JPY14/記事+RF)はStage 3(追加費用、本見積に含めない)。
- 案2の台帳は選定Factのみに縮むので、RFが「選定外Factに触れた文」を検知する力が下がる可能性がある。これは構造的な論点としてOpusレビューへ。

## 4-6 受入条件判定表(ユーザー§7)
| 条件 | 判定方法 |
|---|---|
| 採用Factに重大誤りが残らない | 既知欠陥の検出維持+Sonnet/Fable独立確認。残れば当該方式NG |
| VERIFIED降格は根拠付き | 降格したFact全件にverification_notesの根拠と元verdictの対照 |
| 不確実なFactをVERIFIEDに昇格させない | AMBIGUOUS/REJECTED→VERIFIED遷移の件数が0 |
| B3ストーリー品質維持 | 構成差3段階+品質の別判定、M0bとの比較 |
| 実測総費用で削減 | 再選定・追加検証・統制を含む実測合計 vs 従来方式 |
| Fact Lock・RF整合 | 契約検証PASS(§4-5) |
| 5記事の傾向と例外 | 記事別表+Fact数・採用比率との関係 |

## 4-7 隔離(11-7)
- Production既定動作は不変。Trial scriptのみ。`CURRENT_SPEC.md` に未採用案を書かない。新方式はProductionに配線しない。出力は `er082_output/` のみ。
- 隔離test(DefaultOffIsolation型)ではなく、「Production関連ファイルのsha不変+Trial scriptがProduction pathに書かない」を事前検査する(新機能flagは作らないため11-7の例外は不要で、純粋なOffline Trial)。

## 4-8 実行順序・STOP条件・CP
- CP0: ユーザー費用承認(#104)とOpus条件Aレビュー(Fable)。
- CP1: harness実装とJPY0 dry-run(保存済み出力を使った stub test、Prompt組立、契約検証。API呼出なし)。
- CP2: Coffee(M0b、M1、M2、M3)→ Fable確認。
- CP3: inbound(再選定loopが自然に動き得る記事)→ Fable確認。
- CP4: streaming、openai、central → 集計。
- CP5: 集計・構成差判定・Fableレビュー・Status分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)→ STOP報告。
- STOP条件: 累計実費が承認額に達する、承認前に有料呼出、STOP_NOTICE、外部停止、Production関連ファイルのsha変化、原因不明rc≠0が2回、再選定上限到達時に確定させようとする動作。
- 実行は1記事ずつ。記事単位で費用ガードを置く(承認額の記事按分)。

# 5. 費用見積(COST_ESTIMATE_01相当)
出典: 各runの raw_usage_log.jsonl 実測+pricing_snapshot.json(検索 $10/1,000、gpt-6-luna 入0.1/出0.5、gpt-6.1-sol 入2.0/出10.0 USD/1M)、USD_JPY=160。再現= cost_estimate_calc_01.py → cost_estimate_01.json。手法は manual_substitution(実測単価×想定呼出)。

- 主な仮定:
  - 検索1回=JPY1.6+検索本文token約9,000(約JPY0.14)。
  - 案2のLedger呼出数=max(2, 既存呼出×採用Fact/Fact数)。上限=min(既存, 2×期待+1)。
  - B3(sol)の費用は、非solのB3 token実測をsol単価に換算した。出力token数が同等という仮定。
  - REJECTED率=2/125(全標本)。選定k件に1件以上出る確率=1-(1-p)^k。inbound型(2/15)なら大きく外れる。
  - 再選定1回=B3'(入力+10%)+新規2Fact検証。
- 方式別合計(新規API): §1の表。
  - Stage 1(4方式): 期待約JPY306、上限約JPY710。
  - Stage 1に追加する統制M0b(従来B3の追加1回、5記事): 約JPY54。
  - Stage 1合計: 期待約JPY360、上限約JPY775。
  - Stage 2(条件付き。同日・上限なしLedger再検証): 約JPY16(最安2記事)〜83(全5記事)。
  - 全体: 期待約JPY376〜443、上限約JPY860。
- 再利用で削れる額: Research 5記事分の再実行 約JPY107(19.85+22.82+28.56+21.68+14.95)、従来方式のLedger 5記事分 約JPY82.6、Coffeeの既存B3 約JPY10.9。仮に全て新規にやれば合計約JPY200が増える。
- 本日(2026-10-17 JST)の使用済み: 約JPY41.6(SJS4: TTS実測31.33+ASR推定10.3、REPORT_LEDGER L346)。`docs/pm/tools/daily_dev_cost_01.py --date 2026-10-17` は0を返した(Gemini TTSの cost_actual を拾わない)ので、採用値は41.6(取得できた最大値)。他の2026-10-17の費用記録は見つからず(未捕捉の可能性はあり)。日次残額=1,000-41.6=約JPY958。
- 7-7 / 7-9との関係: 期待・上限とも100円を超えるので、**7-7(2)により、ユーザー承認なしでは有料実行に進めない**。日次は 41.6+上限860=約902で、1,000以内。つまり7-9のSTOPは該当しないが、費用承認(#104)は要る。
- 承認案(Fableが提示用に整理):
  - 案X(推奨): Stage 1を段階実行。1a=Coffee+inbound(期待約JPY140、上限約JPY328)→ 結果を見て1b=残り3記事(期待約JPY166+統制)。
  - 案Y: Stage 1全体を一括(上限承認JPY450案、実費がそれに達したら停止)。
  - Stage 2(統制)は別ゲート(約JPY16〜83)。
- RLCOの「案1 3記事150〜200、案2 3記事55〜60」は機械的に当てはめていない。差の理由: RLCOは案1のLedger再実行3本のみ、本Trialは5記事×4方式+B3 sol再実行+統制。

# 6. 案1+案2の相乗効果(事前の机上所見、実測は後)
- 事前分析からの示唆: 案1が削る反復(fxpw F16/F17)は、B3が採用しないFactで起きており、案2で既に検証対象外になる。つまり案1+案2の追加削減は小さい(数円未満〜約2円)見込み。相乗効果は低いとの予想。ただし選定Factに採用VERIFIEDの反復があれば(streaming F04型)案1の効果が案2の後でも残る。これはTrialで測る。
- 70円目標: RLCO提案書のText工程JPY72.64(Coffee)が基準。案2で約JPY53〜60(推定)。音声工程は未実測で、audio+scaffold計画は約JPY27.8。Research/Ledger改善だけでは70円に届かない見込みという所見は維持(実測音声費用が出るまで判定しない)。

# 7. 既存のAPPROVED未配線で本範囲に影響するもの
なし。OPEN_ITEMSのGrep(APPROVED_FOR_PRODUCTION)ヒット行を概読し、Research/Ledger/B3に直接関係するAPPROVED未配線は見つからなかった。OPEN-399(K2代替音声)・OPEN-401(A2 sha CRLF警告)・OPEN-402(送信Prompt SHA)は音声・証拠性の別件で無関係。Family X承認仕様は2026-10-16にPRODUCTION_WIRED。

# 8. SSOT追記文案(未編集。Fableがmd保存後に適用)
- DECISION_LOG(`SJS4|STYLE-TRIAL-04` 最終出現=L21734付近の後に追加): 「## 2026-10-17 FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01: ユーザー指示(原文=docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md、4,038文字、sha256=e6bc729b…c96b0c)によるTrial準備(JPY0・API呼出0)。成果=search_cap_analysis_01(.py/.json)、cost_estimate_calc_01(.py)/cost_estimate_01.json、md設計書群。Status=TRIAL_PLAN_READY_COST_APPROVAL_PENDING。発見=(a)Ledgerの呼出単位ログ無し(Fact別呼出数・到達回は復元不能)(b)従来B3の基準は10-08のstage_r 6記事でgpt-6-lunaのため、現行sol6.1での再実行が必要(c)案1b(版情報引継ぎ)は既存draftに該当欄が無く効果測定不可。見積=期待約JPY376〜443/上限約JPY860(>JPY100、7-7によりユーザー費用承認#104待ち)。有料実行はユーザー費用承認+Opus条件Aレビュー後。Production・CURRENT_SPEC不変。」
- OPEN_ITEMS OPEN-403行末(区分/棚卸しの前): 「→ Trial管理ID RLCT(FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01)、準備完了(2026-10-17)、費用承認#104待ち」(新規OPENは作らない)。
- REPORT_LEDGER行: 「2026-10-17 | FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01(Trial準備、JPY0、commit 17b1625a2、Status=TRIAL_PLAN_READY_COST_APPROVAL_PENDING)」。
- USER_DECISION_REGISTER: #101/#102に「2026-10-17 ユーザー指示でTrial方針承認(金額は別途承認)」。新規「#104 RLCT有料実行の費用承認(見積確定後)」UDR-blocking候補(期待約JPY376〜443/上限約JPY860、段階実行案X推奨)。

# 9. commit / push
- commit 17b1625a2 → origin/main へpush済み(eigo-radio-crbn経由、ff-only成功)。主dirも origin/main と一致。
- 含むファイル: docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/{search_cap_analysis_01.py, search_cap_analysis_01.json, cost_estimate_calc_01.py, cost_estimate_01.json}、docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_{USER.md, 委任_01.md, 委任_01.md_check.json}。
- secret scan: hits=0(ただしscanned_files=0と表示され、スキャン範囲は未確認)。
- raw URL:
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/search_cap_analysis_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/search_cap_analysis_01.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/cost_estimate_calc_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/cost_estimate_01.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md

# 10. RESULT_PACKET 4行と判定整合
1. 既存仕様整合: er019 runner:60-66,97-141,147-175; er012 efam:183-226; er003 vfl01:228-250,282-292; er002_r3:65-81; er019 B3 module:38-131,144-250; er053 producer:6-17,844-845; er053 RF:169-194; PM_GOVERNANCE 7-7(L854)/7-9(L875)/27-7; OPEN_ITEMS OPEN-403(L912)、UDR #101/#102(L244-245)。
2. Production到達経路の未承認機能の既定値: 変更なし。Production関連ファイル・Prompt・設定は未編集(git差分に含まれるのは新規ファイルのみ)。新方式・flagは作っていない。
3. 最終成果物: 上記commitのscript/JSONと本報告本文。目的(Trial前の準備: 棚卸し、事前分析、記事選定、設計、見積)に対し、内容は揃っているがmd設計書は未ファイル化(§0-1)。有料実行は未着手でユーザー費用承認待ち。事前分析の限界(呼出単位ログ無し、クエリ→Fact割当はheuristic)は成果に明記済み。
4. 撤去・残置: なし。旧ルール・検査・testの撤去も残置もない。
- 判定整合: 重大NG=なし / 主因=Ledger検索ログの粒度不足(Fact別呼出数・到達回の復元不能)と見積>JPY100 / 是正対象=なし(Trial harnessで計測点を追加する設計) / STOP理由=費用承認待ち(7-7)・Opus条件Aレビュー未実施 / 提示=可

# 11. 判断候補(区分付き)
- #104 RLCT有料実行の費用承認 — **D**(真に新しい)。根拠: 見積が7-7の100円超(期待約JPY376〜443、上限約JPY860)。ユーザー原文§8「金額未確定の無制限許可ではない」。案X(段階実行)を推奨。
- 「上限3回」の単位(web_search_call単位か、クエリ単位か) — **B**(承認範囲内で自己解決可、Fable確認)。ユーザー原文§3は暫定上限を「Fact当たりWeb検索ツール呼出3回」と明記しており、call単位が既判断(原文§3)。Trialで新規計測した上で報告する。
- 従来B3の基準モデル(gpt-6-lunaでなくsol6.1で再実行) — **B**。Production現行(2026-10-11)に合わせるための自己解決。費用は見積に含めた。
- 案1b(版情報引継ぎ)の測定 — **B**(今回は測定不可と記録して終了)。測定するには新規Research(約JPY14〜29/記事)が要り、ユーザー原文§3が禁じている。
- 5記事のテーマ選定 — **C**(現タスクと独立): 保存済みテーマの再利用でありPM_GOVERNANCE 13節の新規記事ではない。代替候補(semiconductor_earnings、byd_recall、Meta)はあるが、ユーザー選定は不要と判断。異論があればFableで判断。

# 12. 再計画用ブロック(QDC材料)
- 原因仮説: 案1の効果は「反復が特定Factに集中する記事」でだけ出る(fxpw、streaming、l3)。Fact当たり3回は呼出単位では多くの記事で拘束しない。案2の効果は採用比率(0.24〜0.86)に強く依存する。
- 根拠値: search_cap_analysis_01.json(streaming F04=9クエリ・VERIFIED・採用、fxpw F16/F17群=8クエリ、呼出/クエリ比0.30〜1.17)。cost_estimate_01.json(Stage 1期待306/上限710)。
- 前回(RLCO)との差分: RLCOの案1削減5.1円(手計算)は、heuristicの下限2.0円と幅がある。案2の純削減は記事依存(Coffeeで約JPY18の削減相当、streamingでは削減ほぼ0)。
- 次の一手の候補: (1)ユーザーに#104を段階案Xで提示(改善見込み=高) (2)Opus条件Aレビュー(harness設計) (3)CP1のJPY0 dry-run実装。