# PRE_ANALYSIS_SEARCH_CAP_01(委任_01報告 §2 抜粋)

> 本文は委任_01 sonnet-workerの最終報告(2026-10-17)を無改変で転記。Opusレビュー前。採用判断はユーザー(正本=TRIAL_PREP_REPORT_01.md)

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
- **[訂正注記 2026-10-17 委任_03、OF-RLCT-R-09]** 上記「単位が確定すれば、上限の評価がFact単位で可能になる」は言い過ぎ。呼出単位ログ(action.type・queries・順序)を保存しても、呼出→Factの対応は推定(heuristic)のままであり、改善されるのは推定精度である。なお、TRIAL_DESIGN_01の「Fact別・呼出別が初めて復元可能」も同様にTRIAL_DESIGN_02で「呼出単位ログにより推定精度が上がる(Fact対応は依然heuristic)」へ訂正済み。また課金単位がweb_search_call全件の場合、open_page/findを上限の外に置くと費用を抑えない(CP1で公式pricingを確認し、課金単位で上限を定義する)。

## 2-4 案1b(版・発行年月・出典内該当箇所の引継ぎ)
- 測定可否: 既存データでは不可。
- 根拠: 12 runのfact_ledger_draft.jsonに現れるキーは15種(fact_id、claim、subject、date_or_period、scope、conditions、numeric_value、numeric_scope、causal_strength、source_title、source_url、source_type、support_level、ambiguity、notes_for_writer)で、版・発行月・該当箇所の欄が無い。
- 補完にはResearcherの再実行が要る(新規Research 1記事あたり約JPY14〜29)。これは「既存データから取得できない情報を新たな有料Researchで補完しない」に反するので行わない。
- 必要性の実例(5記事中2記事に出ている)。
  - fxpw F16 / F17: USDAのURLが最新版の別名を指し、2025年12月版が返った。
  - inbound F05 / F06: 推計値42,683,600と確定値42,683,301の差。F05は「確定発表」というラベル誤りでREJECTED。
- 案1bはこのTrialでは効果測定不可と記録し、上限制御の効果とは混ぜない。
