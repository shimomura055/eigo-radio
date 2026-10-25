# PREREGISTERED_CRITERIA_07(Trial-07 事前登録。有料生成の前にcommit)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12(Part 2 Trial-07) / 登録日: 2026-10-25(Step A'' 有料生成の前) / 根拠: ユーザー統合指示(`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md` §3・§4)、`EVAL_06.md`(Trial-06不合格の原因)
Status: DEV/Trial専用。合格しても到達上限はVALIDATED(Production採用・配線は禁止。正式採用は別途ユーザー判断)。この文書は生成前に固定し、生成結果を見て変更しない(変更が必要な場合は「事後変更」と明記して追記し、合否判定には本書の事前登録版を使う)。
置換関係: `PREREGISTERED_CRITERIA_06.md` §1(規則)・§3(合格条件)・§4(終了条件)を本書で置換する。許容集合(06 §2)は継承し、2作品を追加する。Part 2のStep B品質(04 §2-1・2-6、06 §3のStep B品質)は有効。

## 0. ユーザー承認済み方針の反映(固定)
- 文法解説は**最大1件。解説する価値のある英文がなければ0件**。件数を満たすための選定をしない。2件目の選定ロジックは廃止(`select_one`は適格の先頭1件のみ)。
- 「最も難しい文」を機械的に選ぶだけでなく、**学習価値を確認**する(`teaching_value`=HIGH/LOWと`teaching_value_ja`=身につけられる読み方1句。HIGHかつ`teaching_value_ja`非空でなければ適格にならない)。
- 承認済みの品質基準は変更しない(Step Bの4点解説・学習者向け表記・開発者語禁止・逐語引用は04のまま)。

## 1. 規則(固定)
1. 分類・優先順位は06から継承: **INV > CLEFT > CMP > FRONT > HEAVY > POSTMOD > SPEC > ELL > APPOS**。OTHERは自動選定の対象外。強クラス=INV・CLEFT・CMP。中クラス=FRONT・HEAVY・POSTMOD・SPEC・ELL・APPOS。
2. **FRONTの採否条件(前置と基礎項目の矛盾の解消。Trial-06の主因)**: LLMはFRONTの文に`front_kind`を付ける。
   - 不適格(基礎): `CLAUSE_SIMPLE`(文頭がbefore/after/when/if/because/although/while等の単純な副詞節)、`PHRASE_SHORT`(短い副詞・前置詞句・時や場所の語句)。すなわち`Before A, B`/`After A, B`のように**文頭に従属節や句が置かれているだけでは難文扱いしない**。
   - 適格: `PARTICIPLE`(分詞句)・`ADJECTIVE`(形容詞句)・`AS_THOUGH`(as/though倒置の前置)・`NESTED_OR_LONG`(おおむね10語以上で内部に節や修飾が入る長い文頭要素)・`OBJECT_OR_COMPLEMENT`(目的語・補語の前置)。文頭要素が複雑な構造・解釈上の難しさを生んでいる場合は一律除外しない。
   - PromptはFRONT定義と基礎項目を整合させる(基礎項目に「単純な副詞節」を明記し、FRONTの定義から「副詞節」を例示として外す)。コードは`front_kind`が`FRONT_OK`集合の外(空・CLAUSE_SIMPLE・PHRASE_SHORT)のFRONTを適格にしない。
3. 適格 = 本文に解決でき重複でなく、**単一段落内の逐語spanである検証(`verify_single_span`)に合格**し、`basic_only=false`、分類がOTHERでなく、材料欄(construct_ja・points_ja・context_ja)が揃い、**`teaching_value=HIGH`かつ`teaching_value_ja`非空**。
   - 中クラスはさらに`misread_target`∈{SUBJECT,VERB,MODIFIEE,OMITTED}かつ`misread_quote`が選定文に逐語で含まれる。FRONTは上記2のとおり。**ELLはさらに`omitted_words`非空**(同じ主語が続く並列・省略された関係代名詞・会話の断片はELLにしないとPromptで明記)。
4. 選定 = 適格を(クラス優先順, 段落番号, 出現順)に並べ**先頭1件**。適格が0なら0件。
5. 引用文連結対策(別対策。文法選定とは独立):
   - 原因(Trial-06 開いた窓r2、`OUTPUT_06_open_window_r2_STEPA_DEV.json`のP21): P21=`Across the quiet garden came a young voice:`(コロンで終わる)、P22=`“Bertie, why do you bound?”`(次の段落の引用)。LLMが両段落を連結した文を返し、`resolve_verbatim`/`resolve6`は主張段落(P21)内に無いため失敗(連結は出力されず安全側に落ちたが、featureがP21ごと脱落=中核の拾い漏れ)。
   - 対策: (a) Promptに「sentenceは1つの段落内の1文。段落をまたぐ連結をしない(コロンで終わる文は次段落の引用を含めずコロンまで)」を明記。(b) `resolve7`: resolve6が失敗したときに限り、返却語列が「主張段落の末尾+直後(最大3段落)の先頭に連続」または「直前の段落の末尾+主張段落の先頭に連続」に**厳密に一致**する場合だけ、主張段落側のspanに限定して再解決し`cross_para_flag`を記録する(一致しなければ従来どおり失敗。誤修復しない)。(c) `verify_single_span`: 解決後の文が主張段落1つの中の連続した逐語spanで改行を含まないことを検査し、不合格なら適格にしない。
   - 回帰テスト(`test_trial_07.py`/`run_trial_07.py selftest`): Trial-06の実出力の返却値を固定データとして再現し、(1) resolve6が失敗する(根本原因の固定)、(2) resolve7がP21のspanへ復元しflagが付く、(3) 連結文そのものはverify_single_spanに不合格、(4) 実出力のfeatures全体をparseしてP21が脱落しない、(5) 逆向き・境界でない連結・別語は復元せず失敗のまま、(6) 通常の文・引用符付きの既存動作が不変、を確認する。
6. 比較用規則はTrial-07では設けない(06の(O)(N)は2件目選定の比較であり廃止)。

## 2. 作品と許容集合(Step A'' 実行前に登録。目印語句は本文の逐語。選定文が目印語句を含み段落が一致すれば一致)
「許容集合」=「中核 ∪ どちらでも可」。厳格側の副指標として「選定⊆中核」の率も併記する(合否には使わない)。
**継承(06 §2と同一)**: 開いた窓・イグ・ノーベル・賢者の贈り物・猿の手・告げ口心臓・二十年後は`analyze_06.py`の`CORE`/`EITHER`と同一の語句(`analyze_07.py`が06から読み込み、変更しない)。作品の位置づけは06の「開発用/ホールドアウト」から「**Trial-06の既存6作品(Trial-07では全て既見の比較用)**」に変わる。
**二十年後の扱い**: 中核なし・どちらでも可=P23`Twenty years can change a man, but not the shape of his nose.`のみ。「0件が正解」の作品として扱うが、06から継承した許容集合のP23は許容内(合格)とし、P23以外の選定は不合格。P23を選んだ標本は別記録する(0件ではない=厳格な「0件が正解」からの逸脱として注記)。

**新ホールドアウト(いずれも既存本文。新規生成なし。本文を読んで生成前に作成。Trial-01〜06で未使用)**

| 作品(区分) | 出典 | 中核(核となる難所) | どちらでも可 |
|---|---|---|---|
| 退屈と攻撃性 `boredom`(**難所あり**。Family Xの解説記事Advanced本文。`## In one line`以降は対象外) | `er019_output/boredom_aggression/run_bape_01/b1b/article.md`(11段落) | P5 `were more likely to reduce the other person’s reward after watching the stone video than after watching the magician video`(長い主語+than after…の比較) / P7 `those who watched the stone video were more likely to reduce another person’s reward than those in the other conditions`(regardless of how…の長い文頭要素+than those…の比較) | P2 `either a five-minute video of a stone, where nothing happened, or a video of a magician`(either…or+関係節) / P8 `Along with “what kind of person someone is,” there’s also “what they can do in that situation.”`(along withの文頭要素+there’s also) |
| 走れメロス `melos`(**平易・0件が正解**。Family Z完成記事 Before the Last Light) | `er026_output/family_z_production_e2e_01/melos/run_e2e_06/writer/r2.md`(29段落。同一内容のr2.mdが他14 runに存在) | なし | **なし(許容集合=∅。選定があれば不合格)** |

メロスの除外理由(許容集合∅の根拠。06で基礎とした扱いと同じ): `Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.`(分詞の基本用法・付帯状況の基本形)、`Melos turned to his friend, but before he could speak, his friend held out…`(単純な副詞節)、`Above his friend, the sword was already raised.`(場所句の前置+受動態。主語・動詞の倒置なし)、`Then he remembered the hands held out for the chains.`(分詞の基本用法)、`Before dawn on the third day, he left for the city.`(短い前置詞句)、`For the first time, he waited for an answer instead of ordering one.`(基本)。会話の断片・間投詞・一語返答は基礎。

除外(許容集合に入れない)の例(継承): 命令文+and、動名詞主語の単純形、`the`+形容詞、伝達部の倒置・同格、分詞構文・付帯状況のwithの基本形、`whose`の基本用法、会話の断片、`I recognized your face as the man wanted in Chicago.`。
作品選定理由: 既存6作品=Trial-06との比較可能性(同一本文・同一許容集合) / 退屈と攻撃性=Family X Advanced既存本文でTrial未使用、比較(than)と長い文頭要素を含み、FRONT条件(NESTED_OR_LONG)とCMPの双方を検証できる / 走れメロス=Family Z完成記事でTrial未使用、会話と短文中心で難所がなく、0件経路の検証に適する。
注記: 許容集合は主観を含む(迷う文は「どちらでも可」に入れた)。新ホールドアウト2作品は設計(Prompt・規則)の決定時に本文を見ていない(Prompt例の本文非含有はdry-run/selftestで6作品+2作品に対し逐語照合assert)。ただし許容集合は生成前にSonnetが本文を読んで作成し、Fableが事後照合する。

## 3. 標本数と費用配分(固定)
- モデル=gpt-6-luna(最新世代の推奨系。Trial-01〜06と同一)。temperature・seed・reasoningは未指定(provider default)。各callは`max_output_tokens=13000`。
- **Step A'' 18 call**: 開いた窓 N=3 / 賢者の贈り物 N=3 / イグ・猿の手・告げ口心臓・二十年後・退屈と攻撃性・走れメロス N=2。
  配分理由: 本委任の追加API上限は12円。Trial-06の実績(平均0.49円/call)から22 call(既存6×3+新規2×2)は約10.8円+Step B約1.2円=約12円で上限に余裕がないため、**Trial-06で不合格・脱落が出た開いた窓(連結不具合)と賢者の贈り物(強クラス拾い漏れ)をN=3に維持し、他はN=2**とした。N=2でも作品内の選定一致率(安定性)を測れる。新ホールドアウトを削らず、既存4作品をN=3→2とした(既見のため)。
- **Step B(合格時のみ)**: 各作品r1で選定1件があれば4点解説(Trial-04と同一Prompt。最大6 call、選定0件は固定文のみでcallなし)。
- 費用ガード: 予約方式(06の`Budget`)。上限=Step A'' 10.8円、全体12.0円(本委任上限)。「実費確定済み累計+実行中callの最大見込み額+当該callの最大見込み額<=上限」を満たすときだけ開始。自動再試行なし。原因不明のcall失敗が2回で新規call停止。予約合計が上限を超える起動はしない。案件累計上限はFable権限で35円→50円へ引き上げ済み(`BUDGET_LOG_01.md`)。

## 4. 合格条件(Step A'' 18標本の機械的当てはめ+目視)
全標本で次をすべて満たす:
1. **選定が許容集合内(中核または可)、または正しく0件**。許容集合外の選定が0。
2. **0件が正解の作品での選定0**: 走れメロスで選定0(標本2/2が0件)。二十年後はP23以外の選定0。
3. **中核がある作品での0件(見落とし)0**: 開いた窓・イグ・賢者・猿の手・告げ口心臓・退屈と攻撃性の全標本で選定が1件ある(0件の標本が0)。
4. **引用連結・改変0**: 全標本のfeatures(解決できたもの)について`cross_para_flag`の発生数と、選定された文が`verify_single_span`に合格することを記録し、**選定された文は全て単一段落内の逐語span**(不合格0)。連結が検出されて復元された場合は「検出・再解決成功」として記録(合格に数える)。復元できず脱落したfeatureが中核であれば、その標本を見落としとして判定に含める(条件3)。
5. 全18標本取得(call失敗0・parse失敗0)。標本が欠けた作品は不合格。
6. 基礎だけの選定(construct_ja・points_jaが`PREREGISTERED_CRITERIA_05.md` §2の基礎項目の説明のみ)0(Sonnet目視、迷えば判定保留をFableへ)。
安定性(判定補助・合否に使わない): 同一作品内の標本間の選定一致率(同一段落一致/同一分類一致)。
- **Step A''合格 = 上記1〜6を全作品で満たす。**
- **Step B品質(Step A''合格時のみ。各作品r1)**: Part 2節(`## Part 2`以降全体)に`PREREGISTERED_CRITERIA_04.md` §2-1の開発者向け語が0件 / `check_quotes_04.py`相当の逐語照合で本文にない引用(比較用除く)0件・前後文の引用は逐語 / 本文にない事実なし(判定保留可) / 各選定に日本語訳・仕組み・意味の3節以上があり(比較は任意)、選定0件の作品は固定文のみ。
- Trial終了判断(後付け禁止): Step A''全作品合格かつStep B品質合格 → 追加の磨き込みをせずTrial終了(Status候補=Part 2 VALIDATED。Production配線は禁止、正式採用は別途ユーザー判断)。

## 5. 終了条件(固定)
**不合格でも追加Trialを自動実施しない。** Prompt微調整・規則の再調整・追加Trialを行わず、原因と改善見込みを分析してFableへ報告する(`USER_DECISION_REQUIRED`候補)。Step A''が不合格ならStep Bを実行しない。予算超過見込み・重大な品質問題・仕様変更/Production変更が必要になった場合はSTOP。

## 6. 追加の測定(合否外・EVAL_07に記録)
- 作品別の選定英文(逐語)・理由(分類・front_kind・teaching_value_ja)・許容集合との関係。0件標本は理由(適格数と脱落理由の内訳)。
- 学習価値の低い文の誤選定、学習価値の高い文の見落とし(許容集合との照合+目視)。
- FRONT採否条件の効果: `front_kind`の分布、`CLAUSE_SIMPLE`/`PHRASE_SHORT`で落ちたFRONT数、Trial-06で選ばれた許容集合外のFRONT 10件相当(Before/After節)が再発したか。
- `teaching_value`=LOWで落ちた候補数(強クラス/中クラス別)、`omitted_words`空で落ちたELL数、中クラス追加条件で落ちた候補。
- 引用文連結: `cross_para_flag`発生数、resolve失敗数、`sentence_replaced_by_body`、未カバー段落。Trial-06からの改善(開いた窓r2相当の脱落の有無)。
- 登録済み文の分類コードの標本間一致。
- 量産単価の根拠: Step A'' 1 call実費+Step B 1 call実費(円/セット)。

## 7. 事前に予測している点(結果と照合するため記録)
- 強クラス(INV/CLEFT/CMP)を持つ作品では全標本で強クラスの先頭1件が選ばれ、許容集合外の選定は出ない見込み(Trial-06の許容集合外14件は全て中クラスの2件目だったため、1件化で構造的に消える)。
- 見落としリスクが残るのは、(1)賢者の贈り物のようにLLMのfeatures列挙が少ない標本、(2)`teaching_value`をLLMがLOWとした強クラス(例: `Then came a soft knock.`のような短い倒置)。後者は設計上の新しいリスクで、結果で観測する。
- 走れメロスは適格が0〜2件で、0件になる見込み(FRONT条件とteaching_valueで基礎文が落ちるかが焦点)。二十年後は0件またはP23のみの見込み。
- 退屈と攻撃性はP5/P7のCMPが選ばれる見込み(CMPと判定されない場合はHEAVY/FRONT(NESTED_OR_LONG)になり、P7はFRONTでも許容集合内)。
- 費用: Step A'' 約0.45〜0.55円/call、18 callで約8〜10円。

## 8. 変更履歴
- (なし。生成前に固定)
