> 注記: 本文は2026-10-17のOpus独立技術レビュー(条件A)subagent transcriptから無改変で逐語抽出(この1行のみ付加)。

## Opus独立技術レビュー結果: RLCT Trial設計(条件A、read-only、ファイル編集・API呼出なし)

読んだもの: TRIAL_DESIGN_01、PRE_ANALYSIS_SEARCH_CAP_01、COST_ESTIMATE_01、ARTICLE_SELECTION_01、ユーザー原文に加え、er019 runner(97-141、274-319)、efam(183-227)、vfl01(228-309)、B3(51-250)、er005_cost_logger(26-87、334-345)、er053 producer(843-919)、RF(166-196)、review_queue(QUEUE_ROOT)、search_cap_analysis_01.json(model欄)。

**総合所見: 条件付きで実装へ進んでよい。** ただし先に設計を修正する必要がある。Blocking 3件はCP1(harness実装)の前に、Major群は有料実行(CP2)の前に反映すること。差し戻すほどの構造欠陥はない。

---

### Blocking

**OF-RLCT-R-01 [Blocking] 設計どおりの関数importでは、上限付きPromptも呼出単位ログも実現できない**
- 該当: TRIAL_DESIGN §4-2(「`efam.run_verification_for_topic`をimportして呼ぶだけ」「呼出計測点(新規)」)、`er012_e_family_entertainment_two_level_runner_01.py:206-226`
- 問題: この関数は内部で`vfl01.build_verification_prompt`を固定で使うため、Promptを差し替える口がない。返り値も平坦化済みの`search_usage`だけで、`response`本体を返さない。このため、上限付きPrompt(M1/M3)も、action.type・呼出順の保存も、importだけでは実装できない。回避策としてモジュール定数`VERIFICATION_PROMPT_TEMPLATE`を実行時に書き換える(monkey-patch)と、同じプロセスでProduction関数の挙動が変わり、隔離として不適切になる。
- 推奨: Trial専用の検証関数を複製して作る(model・reasoning・tools・schema・developer messageは既存と同一、Promptだけ引数で渡す、raw responseから呼出単位ログを取る)。M0'・M1・M2・M3の新規検証はすべて、この同じ複製関数を通す。こうすれば、方式間の差がPrompt末尾の上限文だけになる。monkey-patchは禁止と明記する。
- 修正しない場合のリスク: 実装時にpatchなど場当たりの対応が入り、隔離と比較条件の同一性が崩れる。

**OF-RLCT-R-02 [Blocking] 既存の予算guardはweb_search手数料を数えない**
- 該当: COST_ESTIMATE §5、TRIAL_DESIGN §4-8(記事単位の費用ガード)、er019 runner 308-313行のコメント
- 問題: `efam.compute_cost_jpy_so_far`と`assert_budget_ok`はtoken費用しか集計しない。本Trialの費用の約89%はweb_search手数料なので、この既存guardを流用すると実費の約1割しか見えず、承認額の超過を検知できない。また`cl.install(<er082 path>)`を呼ばないと記録そのものが行われない(`cl.record`の前提)。
- 推奨: 予算guardには、web_search費用を含む`compute_stage_cost_breakdown`と同じ算式を使う。呼出のたびに判定し、承認額を超える見込みの時点でSTOPする。プロセス開始時に`cl.install("er082_output/rlct_trial_01/raw_usage_log.jsonl")`を必ず実行する。dry-runで「web_search 1回が費用に計上される」ことをtestする。
- 修正しない場合のリスク: 予算上限の実効性がなくなる(安全境界の破れ)。

**OF-RLCT-R-03 [Blocking] Fact Lock検査用のproducerが入力dirに書き込む**
- 該当: TRIAL_DESIGN §4-5、`er053_b3_deterministic_producer_01.py:847-852,907-916`
- 問題: `produce_annotated_b3(out_dir)`は`storyline_b3/`配下の注記artifactを削除してから再生成し、`fact_selection_evidence.json`を上書きする。M0の再利用分(Coffeeの既存B3が入っている`er019_output/coffee_prices/run_fxpw_01`、er052のstage_r)に対して直接実行すると、既存の基準成果物を書き換えてしまう。§4-7のsha確認はコードファイルしか対象にしておらず、これを検知できない。
- 推奨: 再利用する入力(draft、ledger、B3)は、すべて`er082_output/.../<method>/`へ複製してから処理する。sha確認の対象を「Productionコード」だけでなく「再利用する既存成果物」にも広げ、実行前後の不変を確認する。Stage 3でRFを走らせる場合は、`rq.save_queue`の既定root(`review_queue/post_en`、repo全体で共用)を使わず、`root=`にer082配下を明示する。
- 修正しない場合のリスク: 比較の基準データが壊れる。あわせて共用Review Queueが汚れる。

### Major

**OF-RLCT-R-04 [Major] M0'(同日・上限なしの再検証)はStage 1に入れるべき(少なくともCoffee・inbound・streaming)**
- 該当: TRIAL_DESIGN §4-1、論点1(a)
- 問題: M0のLedgerは10-08〜10-16時点、新規の検証は本日実行になる。両者の差には、(i)Webの更新、(ii)Verifier自体の確率的なばらつき、(iii)方式の効果、の3つが混ざる。特にCoffeeの主な削減対象F16/F17(USDAの月次版違い)は、Web更新の影響を最も受けやすい。案1の主効果がまさにWeb更新と重なるため、Stage 2(条件付き)のままでは「案1の推奨上限と根拠」(ユーザー§10-1)を説明できない。降格に根拠があるか、不当な昇格が0件かの判定(§7)も、本日のWebを基準にしないと正誤が決まらない。
- 推奨: 上限が効くと予測された3記事(Coffee・inbound・streaming)はM0'をStage 1へ移す。openaiとcentralでは上限3がほぼ効かない予測なので、M1の呼出ログで上限が効かなかったことを確認できれば、M1をM0'の代わりとして扱う(効いた場合だけStage 2で追加する)。判定の基準もM0ではなくM0'にする(M0とM0'の差=Web更新+Verifierのばらつき、M0'とM1の差=上限の効果)。
- 修正しない場合のリスク: 案1のStatusが判別不能になり、追加費用をかけて再Trialすることになる。

**OF-RLCT-R-05 [Major] 方式別の費用表が「Trialの追加支出」になっており、本番換算の費用ではない**
- 該当: COST_ESTIMATE §1(M3のB3が0、Coffee M0が0)
- 問題: 削減率(ユーザー§10-2)は、本番で1記事を作るときの費用(Research+検証+B3+再選定)で比べる必要がある。M3はB3の共有で、Coffee M0は再利用で、それぞれB3費用が0のように見え、削減率が過大または不正確になる。
- 推奨: 表を2本に分ける。①Trialの追加支出(承認額の管理用)。②本番換算費用(Research実測+検証実測+B3実測または推定+再選定。共有・再利用した分も帰属させる)。M3には、共有したM2の初回B3実費を計上する。

**OF-RLCT-R-06 [Major] 案2の再選定入力の仕様が足りず、B3呼出の検証が既存と揃っていない**
- 該当: TRIAL_DESIGN §4-2、§4-3、B3 `:129,155-184,187-245`
- 問題: (a)`_call_once`は検証も技術的retryもしない。M0は`run_storyline_b3_selection`(全IDのテスト網羅チェック+1回の技術retry)を通るので、M2だけ条件が緩くなる。(b)再選定時、本文の台帳にREJECTEDのFactを`[UNVERIFIED]`のまま残し、extra_noteで「不合格」と伝えると、本文と注記が矛盾する。逆に本文から消すと、B3が再選定した場合にUNKNOWN_FACT_IDになる。(c)検証前draftをどの欄で描画するか(Researcherの`ambiguity`・`support_level`を出すか)が決まっていない。これはAMBIGUOUSのFactが中心に選ばれる率に直接影響する。
- 推奨: Trial版の選定関数を、`run_storyline_b3_selection`と同じ検証・retry構造で複製する。ID抽出のregexは`[UNVERIFIED]`を受け付けるように変える。再選定時の本文は、その時点の状態をタグで示す(`[VERIFIED]`/`[AMBIGUOUS - 断定禁止…]`/`[UNVERIFIED]`)。REJECTEDのFactは候補本文から外し、extra_noteに理由と「選定禁止」を明記する。そのうえで、REJECTEDのIDが選ばれたら機械的に検知して技術的失敗として扱う(B3による再評価は維持されるので、ユーザー§4の「機械的に削除しない」には反しない)。draftの描画欄は、本番で検証前に手に入る情報(`build_verified_ledger_text`と同じ欄+Researcherの`ambiguity`)として事前に固定し、記録する。

**OF-RLCT-R-07 [Major] AMBIGUOUSになったFactがStoryline行で断定されたままWriterへ渡る経路がある**
- 該当: TRIAL_DESIGN §4-3(AMBIGUOUSを再選定のトリガーにしない)、producer `:868-876`(`selected_storyline`をそのまま組み立てに使う)
- 問題: 論点3(b)について、AMBIGUOUSをトリガーにしない判断はユーザー指示(REJECTEDが対象、混同しない)と整合しており妥当である。ただし案2では、B3が検証前にStoryline1行を書く。決定論の注記経路は、Fact本文には「この点は確定していない。」を付けるが、Storyline行は原文のまま組み立ててWriterへのテーマ文にする。このため、中心のFactが後でAMBIGUOUSになると、断定を含むテーマ文がWriterへ入り得る。M0では、B3がタグを知ったうえで書くので、この経路は起きない。
- 推奨: 「中心Fact」を事前に定義し(例: Storyline行が言及するFact)、全方式で次の2つを記録する(JPY0、Sonnet+Fableの独立判定)。①Storyline行またはSelected BriefがAMBIGUOUSのFactを断定している件数。②その割合をM0/M0bと比べる。件数が0でなければ、案2の受入条件「Fact Lockの維持」はNGか、再生成ルールの要否としてユーザー判断事項にする。設計段階でAMBIGUOUS時の再生成を加えることは、新仕様の追加になるため推奨しない。

**OF-RLCT-R-08 [Major] 案2では既知欠陥の「検出維持」が定義できない**
- 該当: TRIAL_DESIGN §4-4(誤りの見逃し)、§4-6の1行目
- 問題: 案2では、B3が選ばなかったFactは検証されない。Coffee F12・F07・F16/17などが選ばれなければ、検出の成否そのものが存在しない。さらに見逃しの検出力は、もともとCoffeeとinboundに集中している。
- 推奨: 既知欠陥ごと・方式ごとの結果を、(a)選定され検出、(b)選定され見逃し(=NG)、(c)非選定(検出は対象外。最終台帳とBriefに含まれないことを確認)の3値で記録する。加えて、追加の呼出を増やさない、または少額で済む故障注入プローブを推奨する。M0/M0bで採用された実在Factの数値・scope・日付を1か所だけ改変した複製を2〜3件作り、上限なしと上限付きのVerifierに選定Factとして検証させる。期待結果はREJECTED。B3構成の比較には混ぜず、別の小実験として扱う。費用は検証数回分(推定で記事あたり約JPY5〜10、未試算)。

**OF-RLCT-R-09 [Major] 上限の単位(open_page/findを別枠)が課金の単位とずれている可能性がある**
- 該当: PRE_ANALYSIS §2-3、論点2(c)
- 問題: プロジェクトの費用モデル(er005とcompute_stage_cost_breakdown)は、web_search_callの全件を1件JPY1.6で計上している。open_page/findも同じ課金なら、それらを上限の外に置くと上限が費用を抑えない。OpenAI側の課金単位は未確認。
- 推奨: CP1で公式pricingを確認する。課金されるなら、上限はweb_search_callの全件(課金単位)で定義する。確認できなければ、search/open_page/findを分けて記録し、上限を守れたかと費用への影響をそれぞれ報告する。
- 論点2(a)(b)への回答:
  - (a)ソフト上限は「上限指示Promptという介入」の効果として測っていると言え、測定として正当である。本番でも同じPromptを使う想定なので、比較として妥当。報告では「hard capではない」と明記し、遵守率(ログ上、Fact群あたり3回を超えたと推定される件数)を併記する。なお、呼出からFactへの対応はログを保存しても推定(heuristic)のままであり、§4-2の「Fact別が初めて復元可能」は言い過ぎなので修正する。
  - (b)Fact別にAPIを分割する案は本Trialでは採らない。理由は、方式が別物になる(Fact間の照合が失われる。F16/F17のように同じ文書を共有するFactを別々に検索して、かえって増える恐れ)ことと、tokenが増えること。総呼出上限のパラメータ(Responses APIの`max_tool_calls`相当。存在と挙動は未確認)は、途中で切られると出力が不完全になる危険があるため、主たる比較の条件には入れない。使うとしても、過去の最大値の1.5倍程度を安全柵として置くにとどめる。

**OF-RLCT-R-10 [Major] B3品質の判定方法が具体化されていない**
- 該当: TRIAL_DESIGN §4-4、ユーザー§6の「B3品質: 面白さ、一貫性、事実との整合」
- 問題: 構成差の3段階はあるが、品質の評価尺度がない。自然ばらつきの基準(M0とM0bの差)も、同じブラインド判定にかけるとは書かれていない。
- 推奨: (1)M0とM0bのペアを方式名を伏せて判定対象に混ぜ、同じ評価者・同じ基準で構成差を判定させる。(2)品質は、M0との一対比較(どちらが良いか・同等か)を3観点ごとに行う。絶対点数より安定する。(3)判定ルールを事前に登録する。例:「M0とM0bの差が中程度以上の記事では、方式差が中程度以下なら方式の効果と認めない」。なお、案2の出力にはREJECTEDの痕跡が出ることがあり、完全なブラインドは難しいため、その限界を記録する。

### Minor

**OF-RLCT-R-11 [Minor] RF(Risk Flagger)の検知力については、変化の向きが未確認**
- 該当: TRIAL_DESIGN §4-5、論点3(c)
- 内容: RFは`verified_fact_ledger.txt`の全Factを照合に使う(runner 281行)。案2では台帳が選定Factだけに縮む。W-1が選定Factだけを受け取る前提なら、選定外の情報を含む文は照合できる相手がなくなる。その結果、検知力が「下がる」のか、未裏付けとして「厳しくなる」のかは、RFの判定条件を確認していないため未確認。逆に、選定外のFactを`[UNVERIFIED]`として台帳に混ぜる案は、未検証のFactが裏付けとして扱われるので不可(採らない)。
- 推奨: JPY0の範囲では`parse_ledger_complete`と契約検証にとどめる。実際の影響は、Stage 3で、既存のM0記事(Coffee・inbound)に「全台帳」と「縮小台帳」の両方でRFを実行し、flagの差を見るのが最小コスト。

**OF-RLCT-R-12 [Minor] 共有設計とM0bの扱い(論点1(b)(c))**
- 案2と案1+案2で初回B3を共有するのは、同じ乱数系列を使うペア比較にあたり妥当。本番でも初回段は同じなので、独立性を損なうというより検証段の差を際立たせる設計である。ただしM3のB3構成差はM2と相関するので、報告で明示する。
- 判定上の注意: M2とM3で同じFactの判定が異なる場合、上限の効果とみなすのは、そのFactでM2の呼出数が上限を超えていた場合に限る(それ以外はVerifierのばらつき)。
- M0bの1回追加は最低限の水準。検証前draftを入力にしたB3のばらつきは、M0bでは測れない。余力があれば、Coffeeとinboundに限りM2の初回B3を追加で1回取ることを推奨する(約JPY25、任意)。

**OF-RLCT-R-13 [Minor] 費用見積の過小評価要因**
- (a)B3とVerifierの技術的retry(Trial版regexやschemaの初回不具合)が上限に入っていない。
- (b)inboundでは、M0でREJECTEDだったF05(年間過去最多)がStorylineの中心になり得る。M2の再選定は、全体のREJECTED率(2/125)から見込むより、ほぼ確実に起きると見たほうがよい。
- (c)選定Factだけを検証すると、1Factあたりの検索数が増える可能性がある(比例縮小の仮定は未検証)。
- (d)R-04でM0'を追加すると約JPY40〜60増える。
- 上限JPY860の枠内には概ね収まるが、期待値は上振れ側と見るべき。本日の使用済み額は、`daily_dev_cost_01.py`が0を返したので41.6を採用している。この取りこぼしがあるため、日次1,000円の判定には余裕を持たせる。

**OF-RLCT-R-14 [Minor] 段階実行の順序**
- 案Xの1a(Coffee+inbound)を先に行う順序は妥当。上限の効果が最も大きい記事と、再選定loopが実際に動く記事を先に見られる。
- 補強: 1aの冒頭で、最も安い経路(CoffeeのM2)を1本だけ流してharnessの結合を確認する。1aから1bへ進む条件(例: 上限の遵守率、再選定loopの正常動作、費用の実測と見積の比)を事前に決めておく。
- streamingは、案1で採用VERIFIEDのFact(F04)が喪失する危険の主要例なので、1bの先頭に置く。

**OF-RLCT-R-15 [Minor] 記事の差し替えは不要(論点7)**
- Meta: 基準がgpt-5.6-lunaで、現行のgpt-6-lunaと異なり交絡になるため不可。
- byd: 全VERIFIEDなので、差し替えても検出力は増えない。
- semiconductor: 採用比率が約0.83で、案2での差が出にくく、streamingと役割が重なる。
- openaiとcentralは、誤降格の測定と、上限が効かない記事の費用・構成を確認する役割を持つ。見逃し検出力の不足は、記事の差し替えより、R-08の故障注入プローブで補うほうが効率的。

**OF-RLCT-R-16 [Minor] 使用モデルを固定・記録する**
- 新規の検証では`vfl01.MODEL`(現在は`routing.WRITER_MODEL`=gpt-6-luna)を使う。各呼出の`response.model`(snapshot名)を記録し、基準となるM0の`model_id_actual`と一致することをCP1で確認する。B3は`routing.require_model("FAMILY_X_STORYLINE_B3")`を通し、返却されたmodelも照合する(Productionと同じ)。
- 評価報告への使用モデルの記載(PM_GOVERNANCE 25節)も忘れないこと。

---

### Fableがユーザーへ上げるべき判断事項
1. **費用承認(#104)の金額を改訂して提示すること。** R-04によるM0'のStage 1追加(約+JPY40〜60)と、R-08の故障注入プローブ(任意、推定で数十円規模、未試算)を反映した承認額にする。案Xの1a/1bの分割は維持する。
2. **報告時に追加の判断が必要になる可能性。** R-07の測定で、案2において「AMBIGUOUSのFactがStoryline行で断定される」件数が0でなかった場合、再生成ルールの追加は新仕様にあたるため、Trial後にユーザー判断となる(現時点で設計に入れる必要はない)。
- それ以外(上限の単位の定義、harnessの構造、評価尺度、記事の維持)は技術的な設計の選択であり、Fableの判断範囲と考える。Production採用の可否については、本レビューでは判断していない。
