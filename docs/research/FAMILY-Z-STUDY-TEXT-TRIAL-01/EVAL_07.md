# EVAL_07(Trial-07 Step A'' 結果と事前登録基準の機械的当てはめ。Fable評価待ち)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12 / 日付: 2026-10-25 / 基準: `PREREGISTERED_CRITERIA_07.md`(生成前commit 88cc40f1b) / 集計: `analysis_07.json`(`analyze_07.py`)/ 生データ: `OUTPUT_07_<work>_r<n>_STEPA_DEV.json`・`usage_07_*.json`・`_raw_07_*.txt`・`batch_07a_result.json`
モデル: gpt-6-luna(全18 callでresponse.model一致、全status=completed。最新世代の推奨系。Trial-01〜06と同一。temperature/seed/reasoning未指定)。
Status: DEV/Trial専用。判定はSonnetが事前登録基準を機械的に当てはめた所見(最終判定はFable)。合格しても到達上限はVALIDATED、Production配線は禁止。

## 1. 結論(事前登録基準)
**Step A'' = 不合格(8作品中7作品が合格、1作品[走れメロス]のみ不合格)。** 不合格の唯一の原因は、「0件が正解」の走れメロス r1が、許容集合∅に反して1件(P11 POSTMOD)を選定したこと(r2は正しく0件)。
`PREREGISTERED_CRITERIA_07.md` §5の終了条件に従い、**Step Bは実行せず、追加Trialは自動実施しない。** 原因と改善見込みを`ADOPTION_NOTE_07.md`に記す。
- 18標本すべて取得(call失敗0・parse失敗0・incomplete 0・再起動0)。0件標本は、難所のある作品6作品で0(見落とし0)。0件は二十年後2/2・メロス1/2。
- **Trial-06不合格の主因は解消**: 許容集合外の選定は Trial-06の14件(12標本)→ Trial-07は**1件(メロスr1)**。Before/After+節のFRONTによる許容集合外の選定は0(`front_rejected`=0。LLMがCLAUSE_SIMPLE/PHRASE_SHORTのFRONTを1件も出力しなかった=Prompt整合の効果)。ELL・APPOSの許容集合外も0。
- 強クラスの拾い漏れ(Trial-06の賢者r2の少features)は再発せず(賢者3/3標本でP22 INV)。引用連結は、Trial-07の実行では発生せず(`cross_para_flag`=0)、対策は**固定データの回帰テスト**でのみ実証(§4)。

## 2. 作品別の選定(英文は本文側の逐語。[core]=中核/[either]=どちらでも可/[outside]=許容集合外)

### 開いた窓 (`open_window`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P21 INV [core] `Across the quiet garden came a young voice:` | 場所を表す句が文頭に出ると、動詞が主語より前に置かれることがある。 | 2/3 | 0.3757 |
| r2 | P21 INV [core] `Across the quiet garden came a young voice:` | 場所を表す句の後では、動詞が主語より前に置かれることがあると見分ける。 | 2/3 | 0.3373 |
| r3 | P21 INV [core] `Across the quiet garden came a young voice:` | 場所を表す句の後で動詞が主語より先に置かれ、その後に主語が続く語順を見抜く。 | 2/3 | 0.3885 |

Trial-06(2件選定)の参考: r1: P21 INV[core] / P12 FRONT[outside]; r2: P12 FRONT[outside] / P29 HEAVY[either]; r3: P21 INV[core] / P12 FRONT[outside] → 許容集合外 3件

### イグ・ノーベル賞2026 (`ig_nobel`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P4 CLEFT [core] `If you were expecting a fancy latte, what you got was a map of molecules.` | Whatで始まる節が文の主語になり、be動詞の後にその内容が示される構造を読む。 | 5/5 | 0.4783 |
| r2 | P4 CLEFT [core] `If you were expecting a fancy latte, what you got was a map of molecules.` | Whatで始まる節が主語となり、be動詞の後ろに焦点となる内容が置かれる型を読む。 | 6/6 | 0.523 |

Trial-06(2件選定)の参考: r1: P4 CLEFT[core] / P5 CMP[core]; r2: P8 CLEFT[core] / P5 CMP[core]; r3: P4 CLEFT[core] / P5 CMP[core] → 許容集合外 0件

### 賢者の贈り物 (`gift`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P22 INV [core] `Inside were the tortoise-shell combs she had so often admired in a shop window.` | 場所を表す語句が文頭に出ると、動詞の後ろに主語が置かれることがある。 | 2/2 | 0.3475 |
| r2 | P22 INV [core] `Inside were the tortoise-shell combs she had so often admired in a shop window.` | 場所を表す語句が文頭に出る倒置では、動詞の後ろに主語が置かれることがある。 | 2/2 | 0.2256 |
| r3 | P22 INV [core] `Inside were the tortoise-shell combs she had so often admired in a shop window.` | 場所を表す語句が文頭に出たあと、動詞が主語より先に置かれる倒置がある。 | 3/3 | 0.3368 |

Trial-06(2件選定)の参考: r1: P22 INV[core] / P5 FRONT[outside]; r2: P4 POSTMOD[core] / P1 ELL[outside]; r3: P22 INV[core] / P2 ELL[outside] → 許容集合外 3件

### 猿の手(開発用・Trial-06から既見) (`paw`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P24 INV [core] `Then came a soft knock.` | Thenのような副詞が文頭に出ると、動詞の後ろに主語が置かれることがある。 | 1/2 | 0.252 |
| r2 | P24 INV [core] `Then came a soft knock.` | Thenのような文頭の副詞の後で、動詞が主語より前に置かれることがあると読む。 | 3/5 | 0.4221 |

Trial-06(2件選定)の参考: r1: P24 INV[core] / P1 FRONT[outside]; r2: P24 INV[core] / P8 FRONT[outside]; r3: P24 INV[core] / P8 FRONT[outside] → 許容集合外 3件

### 告げ口心臓(Trial-06の新ホールドアウト→Trial-07では既見) (`tth`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P8 INV [core] `From the bed came a small groan of terror.` | 場所を表す句の後で動詞が主語より先に置かれる語順を見分けられる。 | 5/5 | 0.4168 |
| r2 | P8 INV [core] `From the bed came a small groan of terror.` | 場所を表す句が文頭に出ると、主語と動詞が通常と逆の順になることがある。 | 2/4 | 0.3883 |

Trial-06(2件選定)の参考: r1: P8 INV[core] / P17 FRONT[either]; r2: P8 INV[core] / P17 FRONT[either]; r3: P8 INV[core] / P17 FRONT[either] → 許容集合外 0件

### 二十年後(平易な本文) (`promise`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | **0件** | (適格0) | 0/0 | 0.1873 |
| r2 | **0件** | (適格0) | 0/0 | 0.213 |

Trial-06(2件選定)の参考: r1: P8 FRONT[outside] / P23 ELL[either]; r2: P8 FRONT[outside] / P15 ELL[outside]; r3: P8 FRONT[outside] / P1 POSTMOD[outside] → 許容集合外 5件

### 退屈と攻撃性(新ホールドアウト・難所あり) (`boredom`) 判定=**合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P7 FRONT/NESTED_OR_LONG [core] `This time, regardless of how strongly participants were inclined to enjoy seeing others suffer, those who watched the stone video were more likely to reduce another person’s reward than those in the other conditions.` | 節を含む長い文頭要素の終わりを見極め、主節の主語と動詞を探す。 | 2/4 | 0.3515 |
| r2 | P5 HEAVY [core] `Participants who were strongly inclined to enjoy seeing others suffer were more likely to reduce the other person’s reward after watching the stone video than after watching the magician video.` | 関係節を含む長い主語では、主語の中心語と主節の動詞を確認する。 | 1/4 | 0.3495 |

### 走れメロス(新ホールドアウト・平易) (`melos`) 判定=**不合格**

| 標本 | Trial-07の選定(0/1件。段落・分類・許容集合との関係・英文逐語) | 学習価値(`teaching_value_ja`) | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P11 POSTMOD [outside] `Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.` | 目的語の後の前置詞句が動詞と名詞句のどちらを修飾するか、意味上の関係から見分ける。 | 1/1 | 0.2792 |
| r2 | **0件** | (適格0) | 0/0 | 0.1116 |

## 3. 誤選定・見落とし
- **見落とし(中核がある作品での0件)**: 0件。開いた窓3/3・賢者3/3・猿の手2/2・告げ口心臓2/2・イグ2/2・退屈と攻撃性2/2で中核が選ばれた(全て[core]、`strict_core_all`=True)。`teaching_value`のLOW判定で強クラスが落ちたのは告げ口心臓r2の1件のみ(同標本はP8 INVが選ばれ影響なし)。
- **誤選定(許容集合外)**: 1件のみ。走れメロスr1 P11 `Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.`(POSTMOD/MODIFIEE、`teaching_value_ja`=「目的語の後の前置詞句が動詞と名詞句のどちらを修飾するか、意味上の関係から見分ける」)。これは事前登録で除外した文(分詞の基本用法・付帯状況の基本形)であり、機械的には不合格。ただし文自体は`with his walking stick`が`struck`と`the man holding it`のどちらにかかるか取り違えうる実際の構造上の曖昧さを含む(Sonnet所見、学習価値の判断はFable。登録の変更は事後変更になるため合否には使わない)。r2は同じ文を選ばず0件で、標本間で揺れた。
- 基礎だけの選定(目視): 0件(選定された英文は全て分類コードの特徴を持つ。構文名・要点が基礎項目の説明のみの選定はなし)。語彙誤読の混入: なし。
- 退屈と攻撃性r2: P7(中核)のfeatureが`resolve_error`で脱落(LLMがsentenceの`another person’s reward`を`another participant’s reward`に**改変**して返した。既存の逐語照合が検出し安全側に落とした[改変0=選定された文は全て本文の逐語])。同標本ではP5(中核、HEAVY)が選ばれ合格。

## 4. 引用文連結不具合の対策結果
- 原因: `DESIGN_07.md` §2。Trial-06 開いた窓r2のP21(コロンで終わる)にP22の引用を連結して返し、既存の`resolve_verbatim`は主張段落内に無いため失敗→中核P21がfeatureごと脱落。
- 対策の実証(API 0、`test_trial_07.py`/`run_trial_07.py selftest` PASS): Trial-06実出力の固定データ(`OUTPUT_06_open_window_r2_STEPA_DEV.json`のP21の返却値)で (1) `resolve6`が失敗(根本原因の固定)、(2) `resolve7`が`Across the quiet garden came a young voice:`へ復元しflag=`cross_para_trimmed_tail`、(3) 連結文は`verify_single_span`に不合格、(4) 実出力features全体のparseでP21が脱落しない、(5) 逆向き連結を復元、境界でない連結・別語の連結は復元せず失敗のまま(誤修復なし)、(6) 通常の文・引用符付き・複数文段落末尾+次段落先頭の既存動作が不変、(7) mock LLMのend-to-endでP21が選定される、を確認。
- 本番(有料)実行: 18標本で`cross_para_flag`=0(開いた窓3標本ともPromptの禁止文によりLLMが連結せず、P21はr1〜r3すべてで解決)。**よってresolve7の本番での発火は未観測**(回帰テストでのみ実証)。選定された18標本中の選定文は全て`verify_single_span`合格(単一段落内の逐語span、改行なし)。
- 参考: 退屈と攻撃性r2で観測した「LLMによる語の置換」は連結とは別種の改変で、既存の逐語照合が検出・排除した(対策の対象外・追加対策は行っていない)。

## 5. Trial-06からの改善
| 指標 | Trial-06(2件選定・6作品18標本) | Trial-07(1件選定・8作品18標本) |
|---|---|---|
| 許容集合外の選定 | 14件(12標本、4作品不合格) | **1件**(1標本、1作品不合格) |
| 内訳 | FRONT(Before/After+節) 10 / ELL 3 / POSTMOD 1 | POSTMOD 1(走れメロス。FRONT 0・ELL 0) |
| 中核の脱落(0件標本) | 開いた窓r2(連結でP21脱落)・賢者r2 | 0(難所のある6作品の全標本で中核を選定) |
| 平易作品(二十年後) | 3/3で許容集合外(FRONT/ELL/POSTMOD)を選定 | 2/2で0件(正しい) |
| 引用連結・改変 | 連結1件(P21脱落)・改変の検出なし | 連結の発生0(回帰テストで対策実証)・語の置換改変1件を既存照合が検出 |
| 費用 | 8.855円/18 call(0.492円/call) | 5.984円/18 call(0.332円/call) |

## 6. 追加の測定(合否外)
- 選定の安定性(同一作品内の選定段落の一致率、`analysis_07.json`の`agree_para`): 開いた窓1.0・イグ1.0・賢者1.0・猿の手1.0・告げ口心臓1.0・二十年後1.0・退屈と攻撃性0.5(P7 FRONT/P5 HEAVY=ともに中核。r2はP7の語置換で脱落)・走れメロス0.5(POSTMOD選定/0件)。同一段落内でも分類コードが標本間で変わる例: 退屈P5=HEAVY/CMP、P7=FRONT/CMP(同一文が複数featureとして挙がる)。
- FRONTの`front_kind`分布: ADJECTIVE 2(告げ口心臓P17[either])、NESTED_OR_LONG 2(退屈P7)。CLAUSE_SIMPLE・PHRASE_SHORTのFRONT出力は0(LLMが文頭の単純な副詞節・短い句をFRONTとして出さなかった)。コードの`front_ok`条件で落ちたFRONTは0件(条件のコード側の効果は未観測、Promptの整合が効いた)。
- `teaching_value`=LOWで落ちた候補: 強クラス1件(告げ口心臓r2)・中クラス3件(猿の手r1・r2、告げ口心臓r2)。ELLで`omitted_words`空により落ちた候補0。中クラス追加条件で落ちた候補0。
- 適格数: 難所のある作品は1〜6件、二十年後0・メロス0〜1。二十年後はfeatures自体が0件(2標本とも、登録したP23を含め分類対象なし)。
- 全文カバレッジ: `uncovered_paras`は全18標本で空。`sentence_replaced_by_body`=0。resolve失敗は退屈r2の2件(P7の同一文2 feature、上記語置換)のみ。
- 費用: 18 call合計**5.984円**(平均0.332円/call、0.112〜0.523円)。入力平均3,584 token・出力平均3,797 token(最大6,466、`max_output_tokens=13000`に未到達)。予約方式ガード: 最大予約合計10.49円(Step A'' 上限10.8円内)、上限超過0。所要: 全体104.8秒、1 call最大53.3秒。本委任上限12円の49.9%、Step B未実行のため残6.02円は未使用。
- 出力トークンがTrial-06(平均5,930)から約36%減(欄の削減[correct_structure_ja/subject_span/main_verb/other_desc]と features 数の減少)。

## 7. 事前予測との照合
- 「強クラスを持つ作品で全標本の先頭1件が強クラス・許容集合外が出ない」: 的中(6作品で強クラスまたは中核が選定、退屈のみ中クラスFRONT/HEAVYが中核)。
- 「賢者の少features・`teaching_value`LOWによる強クラス脱落」: 脱落は観測せず(的中せず=懸念が顕在化せず)。
- 「走れメロスは0件」: 1/2で外れ(r1がP11を選定=不合格の原因)。「二十年後は0件またはP23のみ」: 的中(2/2が0件)。
- 「退屈はP5/P7のCMPが選ばれる」: 部分的中(選ばれたのは中核だが分類はFRONT/HEAVY。CMPとしても同じ文が別featureで挙がる)。
- 「費用0.45〜0.55円/call」: 外れ(0.33円/call、見込みより安い)。
