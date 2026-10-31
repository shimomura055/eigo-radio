# KP-N5-PHRASE-COVERAGE-AUDIT-01 AUDIT_01 (OPEN-631、2026-10-31)

対象: Family X `family_x_untidiness_family_resource_01` Advanced(b1b)。ユーザー原文=`docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md` §3(:70-127。目的=「N5を含む現行Productionの候補抽出・選定工程で適切に評価されているかの把握」、評価ポイント:102-109、「N5が概ね適切に拾えているなら追加改善は不要」:115、「新仕様のProduction採用はユーザー判断」:117、報告形式:119-127)。
Status=**調査完了・Production変更0**。N5 Prompt・判定Gate・選定基準・コードは無変更(本監査の変更はdocs配下のみ)。改善案は全て判断候補(§8)。証跡=`ev01/`。費用 **¥7.44 / 個別Cap ¥15**(`ev01/cost_summary.json`)。

## 0. 結論(先に)

- **5表現の追跡一覧は§2。** 公開済みAdvancedの実際の選定UI候補(旧方式、N5配線前)に5表現は**1つも無かった**。N5現行方式(同一本文のM10再実行)では `in the way` ★ が最終候補12件に入ったが、`put away` ★・`force away`・`leave out`・`in sight` は入らなかった。
- N5の**一般化・意味判定(SEL→GEN5→VER5→CHK5)そのものは5表現を誤って落としていない**: 強制投入すると、`force away` を除く4表現はSELで塊(cls=C)かつkeep、L3も全件SAME(意味保存)。`force away` は3/3回F(字義どおりの動詞+目的語)で、除外は妥当。
- 取りこぼしの主因は**N5より手前の「候補抽出」と、N5内の「pick(上限7件)」**: ①抽出(P7/B1)が5表現を拾わない(P7 0/5、B1 `in sight` 1/4のみ)。抽出Promptの条件5「易しい表現の除外」を外した診断では `in the way`(P7 2/3・B1 3/3)・`in sight`(B1 2/3)が出るが、`put away`・`leave out`・`force away` は0/6のまま。②適格(keep)になっても、難易度順→入力順で上位7件に入れず落ちる(§5-4)。
- **判定: 「改善候補あり」**(N5本体の一般化・意味判定は変更不要)。改善候補3+副次1件は§8。いずれも承認済み仕様・Gateの変更を伴うため実装せず判断候補。

## 1. 参照した記録の区別(旧方式 vs N5現行)

| 記録 | 場所 | 生成時刻 | 方式 |
|---|---|---|---|
| 公開記事の実際のKP候補・HR選定 | `er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01/b1b/key_phrases/kp_candidates.json`(`generated_at`=2026-10-29T21:47:39+09:00、`text_sha256`=937862fe…)。HR提示=`docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/HR_REQUEST_01.md:43-44`。選定=同dirの`confirmed_selection.json`(KP=turn into an interrogation / hear it out / prosecutor、単語=clutter / verdict) | N5配線(commit 3d404cfc6、2026-10-30 23:41)**より前** | **旧方式**(P7+W5'+canonicalization+Gate救済+補完)。`n5`/`generalization`欄は0件 |
| N5現行の実run(同一本文) | `docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03/m10/untidi_b1b/result.json`(M10 untidi_b1b、`generated_at`=2026-10-31T01:15:31+09:00、¥7.85) | J2是正(728d80d60、01:03)後。以降のer119変更55d613a48(01:27)は人称整合時のgloss同期のみ(N5判定は不変) | **N5現行** |
| 本監査の追加実行 | `ev01/` | 2026-10-31 | N5現行部品(er138 `select`/`pick`/`run_l3`・P7/B1 Prompt、無変更)に5表現等を強制投入 |

**同一性の確認(API 0)**: M10の入力本文(`fixtures/n5_trial_replay_fixture_01.json` cases.untidi_b1b.text)のsha256 = 937862fe9e6e705e1f58943d9e12c2f3368a327f37eff75a237b3a1160992790 = 公開記事の旧KP記録`text_sha256`と一致(本文は同一)。P7 Prompt sha=2e93019300f9…(旧・M10同一)。よって「旧方式 vs N5現行」は**同じ本文・同じP7 Promptでの方式差+LLM揺れ**として比較できる。再評価に記事・音声の再生成はなし(既存M10を再利用)。

## 2. 5表現の追跡一覧(報告形式)

用語: 「初期抽出」=P7/B1/補完P7の抽出段、「N5判定」=SEL(塊価値)→L3(GEN5/VER5/CHK5)、「最終候補」=選定UIに供給される12件(フレーズ7+単語5)。サンプル数は§3。

| Phrase | 本文中の意味 | 初期抽出 | N5判定 | 最終候補 | 選定・除外理由 |
|---|---|---|---|---|---|
| `put away` ★ | しまう・片づける(Story 4文[s008,s012,s020,s034]+Comment2[s019]+In One Line[s048 `putting something away`]、計6箇所。分離形 `put it away`/`put that away`を含む) | 旧方式=✕(P7 7件に無い)。N5現行M10=✕(P7 6・B1 14・補完P7に無し)。追加サンプルP7 0/3・B1 0/3 | 強制投入: SEL cls=C(phrasal_verb)・difficulty=easy。代表形のみkeep(単独評価では`putting something away`のみkeep、`put away`系3形は同一用法の重複でkeep=False。プール内では`put away`がkeep)。L3: `put something away`「物を所定の場所にしまう」SAME | ✕(旧・N5現行とも) | **抽出段で未抽出**(P7/B1とも0/9)。抽出Promptの条件5を外した診断でも0/6=条件5だけでは説明できない。N5に入った場合は適格(keep)だが難易度easyのためpickで末尾→上限7で落ちる(§5-4)。 |
| `in the way` ★ | 邪魔になっている(Story Part2 s020「something in the way」1箇所) | 旧方式=✕。**N5現行M10=○**(補完P7の2件目、`doc.backfill.added[1]`・ai_rank12)。追加サンプルP7 0/3・B1 0/3 | M10: SEL cls=C・fixed_phrase・easy・keep(`generalization.attempts[0].l1[1].judged`)、L3 SAME。強制投入3/3でkeep | **○(N5現行M10の最終12件の12番目=補完枠)**。公開済みの実HR提示には無かった | N5現行では**除外されていない**。ただし到達は補完P7(Gate除外2件で空いた2枠)経由の1回のみで再現性は低い(通常P7 0/5・B1 0/4)。条件5を外すとP7 2/3・B1 3/3で抽出される=抽出段の条件5が主因。 |
| `force away` | 力ずくで遠ざける(s024 `force it away` 1箇所) | ✕(旧・M10・追加サンプル0/9) | 強制投入: **cls=F**(字義どおりの動詞+目的語、定着した塊でない)3/3、keep=False | ✕ | **N5の意味判定で除外される想定=妥当**(辞書見出しの句動詞でなく自由な組合せ)。抽出も条件5除去後を含め0/6。選定させる必要のない項目。 |
| `leave out` | 出しっぱなしにする(題名・s007 `Left out`・Preview s001・s033・s036 `leave it out`・Comment4 s044、計6箇所) | 旧方式=✕。N5現行M10=✕(B1が文脈付き名詞句`working things left out`を返しSELでF)。追加サンプル: P7 0/3、B1は`working things left out`が2/3(いずれもF) | 強制投入: `leave it out` cls=C・phrasal_verb・keep 3/3(`Left out`は同一用法の重複でkeep=False)。L3: `leave something out`「〜を外に出したままにする」SAME(flag PRONOUN_SLOT) | ✕ | **抽出段**で`leave out`単体は拾われず(条件5除去後も0/6)、拾われた形(`working things left out`)はN5 SELで「文脈依存の描写的名詞句(F)」。単体で入れば適格(keep)だがpick上限の対象。 |
| `in sight` | 目に見える場所にある(s014・Comment2 s018・s030・s037・In One Line s047、計5箇所) | 旧方式=✕。N5現行M10=✕。追加サンプル: P7 0/3、**B1 1/3**(`in sight`) | 強制投入: cls=C・fixed_phrase・keep 3/3(difficulty easy/easy/upper)。L3: `in sight`「見えるところにある」SAME | ✕ | **抽出段**でまれにしか拾われない(B1全体1/4)。条件5を外すとB1 2/3。拾われればN5はkeep。順位・上限次第で落ち得る(§5-4)。 |

「★」はユーザー原文§3の印(単語単独から意味を推測しにくい表現)。実際の公開記事の選定UIに出た候補(旧方式、`HR_REQUEST_01.md:43-44`): KP=`apply to every household`★/`turn into an interrogation`★/`hear it out`★/`the participant's own explanation`/`what it helps with`/`demand its removal`/`Now in Session`、単語=clutter/verdict/prosecutor/contribution/dismiss。使用箇所の全文引用は`ev01/occurrences_stdout.txt`・`occurrences.json`(分離形含む、API 0)。

## 3. 追加で実施した再評価(Cap ¥15内、¥7.44、記事・音声の再生成なし)

方針: M10(N5現行、同一本文)が既にあるため全工程の再run(約¥7.9)は行わず、既存記録に無い情報だけを現行N5部品(無変更)で取得した。

| 実行 | script / 結果 | 費用 |
|---|---|---|
| 抽出段の再現性: P7(call1・現行Production Prompt、同一sha)×3、B1過剰生成(`n5.prompt_B1`)×3 | `ev01/run_extraction_sampling.py` → `extraction_sampling_result.json` | ¥0.94 |
| N5判定の強制投入: SELを単独14スパン×1回、およびM10の16スパンpool+強制9スパンを同一プールにして×2回(難易度順pick・上限7を再現)。SELでkeepになった強制候補8件にrun_l3(GEN5→VER5→CHK5) | `ev01/run_forced_eval.py` → `forced_eval_sel.json`/`forced_eval_result.json` | ¥4.31 |
| `put away`のL3(上記の上限8件に届かなかった★を1件追加) | `ev01/run_l3_put_away.py` → `l3_put_away_result.json` | ¥1.11 |
| 補足: 追加定型表現のSEL、`gets heated`の救済QA再判定の公式関数replay | `ev01/run_supplement.py`/`run_supplement_qa.py` → `supplement_result_part2_sel.json`/`supplement_result_part1_qa.json` | ¥0.28 |
| 診断(非Production・仕様候補ではない): 抽出Promptの条件5だけを取り除いた変種でP7相当×3・B1相当×3 | `ev01/run_diag_no_easy_exclusion.py` → `diag_no_easy_exclusion_result.json` | ¥0.80 |

使用モデルはProduction既定のまま(B1/SEL/GEN5=gpt-6-luna、VER5=gemini-3.8-flash、CHK5=gpt-6.1-sol。`forced_eval_result.json`の`models`=ルーティングが返した現行モデル)。評価目的で旧/下位モデルは使っていない。

**抽出段のサンプル集計(同一本文)**

| 表現 | P7 call1(旧1+M10 1+新3=5) | 補完P7(旧1+M10 1=2) | B1(M10 1+新3=4) | 診断: 条件5除去 P7v(3)/B1v(3) |
|---|---|---|---|---|
| put away | 0/5 | 0/2 | 0/4 | 0/3 / 0/3 |
| in the way | 0/5 | **1/2**(M10) | 0/4 | 2/3 / 3/3(`something in the way`) |
| force away | 0/5 | 0/2 | 0/4 | 0/3 / 0/3 |
| leave out(単体) | 0/5 | 0/2 | 0/4(`working things left out`は3/4) | 0/3 / 0/3 |
| in sight | 0/5 | 0/2 | 1/4 | 0/3 / 2/3 |

**SEL強制投入の結果**(`forced_eval_sel.json`。isolated=強制スパンのみ、r1/r2=M10の16スパンと同一プール)

| 表現 | isolated | in-pool r1 | in-pool r2 | pick上限7での結果(r1 / r2) |
|---|---|---|---|---|
| put away | C・easy・keep=False(代表は`putting something away`でkeep) | C・easy・keep | C・easy・keep | 落ちる / 落ちる |
| in the way | C・easy・keep | C・upper・keep | C・easy・keep | **採用(7番目)** / 落ちる(easy) |
| force it away | **F** | **F** | **F** | 対象外 |
| leave it out | C・easy・keep | C・upper・keep | C・upper・keep | 落ちる(8番目以降) / **採用** |
| in sight | C・easy・keep | C・upper・keep | C・easy・keep | 落ちる / 落ちる |
| working things left out | — | F | F | 対象外 |

keep総数はr1=13・r2=14で上限7を超える。難易度ラベルは同一表現でも実行ごとに揺れる(`in the way` easy/upper/easy、`turn into an interrogation` upper→easy)。M10の実プールではkeepがちょうど7件でpick上限は効いていなかった(`n_keep`=7=`n_picked`)。

## 4. 他の句動詞・定型表現(対象記事の範囲、手順4)

機械列挙=`ev01/occurrences.py`→`mech_enum.json`(動詞+小辞・前置詞+名詞・既知定型のパターン58件。公開Advanced全文[Story/Comment/Preview/In One Line/題名]対象)+人手確認。各段の候補集合と突合した結果:

| 表現(本文) | 抽出(旧/N5現行/追加サンプル) | N5判定(強制SEL・L3) | 最終候補 | 評価 |
|---|---|---|---|---|
| `gets heated`(s023) | **旧=補完P7で抽出→落ち / M10=B1で抽出→落ち**。B1 4/4・補完P7 1/2 | SEL C・collocation・upper・keep。**落ちたのは既存Gateの救済QA再判定(`rescue_unverified`)** | ✕(旧・M10とも同一理由) | **構造的な取りこぼし(N5ではなく既存Gate救済)**。§4-1 |
| `No wonder`(s023) | ✕(診断P7vで1/3) | C・fixed_phrase・easy・keep 3/3、L3 SAME「〜なのも不思議ではない」 | ✕ | 条件5で落ちる系(基本語の定型表現)。学習価値は人の判断 |
| `bringing out`(s042) | ✕ | C・phrasal_verb・easy/upper・keep、L3 SAME(`bring something out`) | ✕ | 同上 |
| `relied on`(s025) | B1 3/3(新サンプル)。M10ではNOT_SEEN | C・upper・keep 3/3、L3 SAME(`rely on`) | ✕ | B1は拾うがpool順の後ろでpick上限の影響を受ける |
| `Not so fast`(s009) | ✕(診断P7vで1/3・B1vで1/3) | C・easy・keep | ✕ | 条件5で落ちる系。同記事のA2では候補化(M10 untidi_a2) |
| `In other words`/`in a way`(s013/s014) | ✕ | C・fixed_phrase・easy・keep(isolatedのみ評価) | ✕ | 談話標識。条件5で落ちる系 |
| `without question`(s041) | B1 1/3(新サンプル) | C・upper・keep | ✕ | 上限・順位 |
| `turn into an interrogation`/`hear it out`/`end up -ing`/`take up space`/`on the job` | 拾われている(P7/B1) | C・keep(L3で turn into / hear someone out / take up space / on the job に一般化) | ○(旧またはM10の最終候補) | 問題なし |
| `make life work`/`It's not so simple`/`support daily life`/`demands its removal` | 拾われる/拾われない | F(通常の語の組合せ)・keep=False | ✕ | N5判定で妥当に除外 |

### 4-1. `gets heated`(N5配線とは別の既存Gateによる取りこぼし)

- 独立2回の実runで同一理由に落ちた: 旧方式=`kp_candidates.json` `dropped[].stage=canonicalization_qa`・`blocker_codes=[rescue_unverified]`・理由「救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)」、N5現行M10=同(`m10/untidi_b1b/result.json` `dropped[3]`)。
- 機序: canonicalizationのLLMが見出し形`get heated`を返す→validatorがRule7(source_span内に無い別の辞書形を禁止)で不合格→救済`REVERT_SURFACE`(`er125_kp_rescue_production_01.py:42`、活用形が原形化不可の場合に表層形`gets heated`へ戻す)→救済済み項目のQA再判定(`qa_rejudge`)でLLMが再び`get heated`を返す→`_norm_lc(key)`不一致(`er125…:526`)→`NOT_REJUDGED`(`:527`)→`er119_kp_human_review_01.py:540`のfail-closedで提示しない。
- **第3の再現(`ev01/supplement_result_part1_qa.json`)**: 公式`qa_rejudge`に`gets heated`を渡すと(実API 1 call ¥0.13)LLM応答 key_phrase=`get heated`(lemma_normalization)→`{'status': 'NOT_REJUDGED', 'error': 'key_mismatch_or_invalid_fields'}`。3/3で再現。
- 範囲の目安: origin/mainの4つのFamily X KP記録で`rescue_unverified`落ちが5件(`counted as having failed`・`limited the search to`・`gets heated`×2・`relied`)。いずれも活用形の表層形(`gets heated`以外の機序同一性は未検証)。

## 5. 分類(原文「評価のポイント」4区分)

| Phrase | 区分 |
|---|---|
| put away ★ | **抽出段で未抽出**(条件5以外の要因もあり原因は未特定)+ N5に入っても「適格だが難易度/順位/上限で非選定」になりやすい |
| in the way ★ | **N5現行では最終候補に到達**(補完P7経由・再現性低)。通常P7/B1では抽出段で拾われない(条件5が主因と診断で確認) |
| force away | **N5の意味判定で除外される想定(妥当)**。抽出もされない |
| leave out | **抽出段で単体は未抽出**。拾われた名詞句形は**N5意味判定でF除外**。単体なら適格 |
| in sight | **抽出段でまれにしか拾われない**(B1 1/4)。拾われればN5はkeep(順位・上限で落ち得る) |

1. 「難易度が低いため適切に除外」: 抽出段の条件5(ユーザー指定の固定Prompt由来=`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md:69`、`er105_kp_fulltext_selector_01.py:61`、B1側`er138_kp_n5_generalization_01.py:308-310`逐語維持)は仕様どおり易しい表現を落とす。`in the way`・`in sight`はこの条件を外すと抽出される(診断)ので**仕様どおりの除外**。一方SELはこれらを「塊(C)」と判定し、`er138…:354`は「易しいことを理由にkeepを下げない(難易度は並び順にだけ使う)」と定める=**抽出段の条件5とSELの方針が噛み合っていない**(§8 J1)。
2. 「候補抽出が表現を認識できず未抽出」: `put away`・`leave out`は条件5を外しても抽出されない(各0/6)ため、条件5以外の要因(原因は未特定、追加仮説の検証は行っていない)。
3. 「N5の一般化・意味判定で除外」: 5表現では`force away`(F)と`working things left out`(F)のみ。他の4表現は一般化・意味保存(SAME)ともに通過。
4. 「適格だが相対評価で非選定」: `pick`(`er138…:950`)はkeep済みを**難易度(advanced→upper→easy)順、同順位は入力順**で並べて上限`PHRASE_PICK_CAP=7`(`:47`)まで。B1由来はP7候補の後ろに連結される(`collect_pool`)ため同難易度ならP7由来が優先され、難易度ラベルは実行ごとに揺れ、B1由来の上限超過は`dropped`一覧に出ず監査recordのみ(`er138…:1307`)。強制投入のr1ではkeep13件中、`put away`・`leave it out`・`in sight`・`bringing out`・`relied on`・`No wonder`の6件が位置と難易度ラベルだけで落ちた(M10の実プールは7件でpick上限は未発動)。

## 6. 判定: 現行方式は「改善候補あり」

根拠:
1. N5本体(SEL・GEN5・VER5・CHK5)は5表現と他の定型表現を妥当に評価した(適格はC・SAME、不適格は`force away`等のF)。**N5の一般化・意味判定は変更不要**。
2. 一方、ユーザーが価値を見た表現のうち4つは、実際の公開記事の選定UIに供給されなかった(旧方式)。N5現行でも再現性の高い供給経路が無い(`in the way`は補完枠で1回到達しただけ。P7 0/5・B1 0/4)。原因は「N5より手前の抽出Prompt(条件5)」と「N5内のpick(難易度→入力順→上限7)」の構造。
3. `gets heated`のように、N5と無関係の既存Gate(救済QA再判定)が活用形の定型表現を決定論的に落とす不具合が確認できた(3/3再現)。
4. 反対に「改善不要」と見る余地: 条件5はユーザー指定の承認済み仕様で、Advancedで易しい表現を除外するのは意図どおり。`put away`のSEL難易度はeasy。5表現を必ず選定させることは目的ではない(原文§3)。**この点はユーザー判断**(§8 J1)。

## 7. 限界(過大評価の防止)

- 1記事×1レベル(Advanced)。サンプルは各3〜5回で、LLM揺れの統計的頻度は推定できない(「0/5」は「この条件で出なかった」の記録)。
- 強制投入は「抽出されたと仮定した場合」のN5判定であり、実運用のプール構成(B1が返すsentence付きスパン)とは近似(`_fill_sentence`で文を補完)。プール順は実運用同様にP7→B1→強制の順。
- `put away`・`leave out`が条件5除去でも出ない原因は未特定。「学習価値の高さ」自体の正解はなく、ユーザー判断が基準。
- Standardは対象外(原文どおりAdvancedに限定)。

## 8. 判断候補(実装なし)

**J1(抽出入口の条件5と、SELの「易しい塊も残す」方針の整合)** 【分類D: 新仕様(承認済みP7/B1 Promptの条件変更)】
- 現状: 抽出段は条件5で易しい表現を除外、SELは易しい塊でもkeepとし難易度は並び順のみ。両者が噛み合わず、SELの方針は入口で効かない(`in the way`/`in sight`で確認)。
- 案A: 現状維持(承認済み仕様どおり、Advancedは易しい表現を出さない)。案B: 条件5を「基本語だけでも辞書見出しの句動詞・固定表現(C)は除外しない」に限定緩和(要Offline Trial→VALIDATED→ユーザー採用)。案C: 条件5は維持しStandardだけ別設定(要設計)。
- QCD(案B): Q=取りこぼし減/易しい項目増でHRの選択肢が希釈されるリスク(難易度表示は既存のkp_difficulty_v2で分かる)。C=P7/B1のプロンプト長は同等、SEL pool増で+約¥0.1〜0.3/記事、L3はpick上限で頭打ち(実質+0)=70円目標への影響は軽微。D=Trial 1回(4記事×2level想定¥3〜5)で検証可。推奨: 案BをOffline Trialで検証してからユーザー判断(本監査は採用提案をしない)。
- 停止根拠: ユーザー原文§3「新仕様のProduction採用はユーザー判断」(`…TRIO-01_USER.md:117`)、承認済みPrompt変更。

**J2(pick: 難易度→入力順→上限7の決め方)** 【分類D: 選定基準の変更】
- 案: 上限超過の適格(keep)を監査recordに残す(B1由来も)/同順位でP7・B1を公平化/易しい適格塊を追加枠として末尾に残す(HR提示数は現行12件上限との整合が要確認)。QCD: C=0(LLM追加なし)、D=小。Q=安定性向上。
- 停止根拠: N5方式(2026-10-30ユーザー正式決定)の選定基準変更=ユーザー判断。

**J3(救済QA再判定の不具合 `gets heated`型)** 【分類: 不具合(PM_GOVERNANCE 11-8)=`修正へ進む`。ただしGate挙動の変更のため、Fable判断→Opus条件A相当レビュー後】
- 案: `REVERT_SURFACE`救済のQA再判定で、LLMが再び原形化したkeyを返しても、表層形を固定したrejudge(promptで`key_phrase`を指定、または比較をlemma_normalizationに限り許容)にする。QCD: C=0〜(救済発動1件あたり既存の¥0.1程度)、Q=活用形の定型表現の取りこぼし解消、D=小。確認済みの範囲: `gets heated`(3/3再現)。
- 次委任案: `KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01`(再現fixture=本監査の`ev01/supplement_result_part1_qa.json`、影響範囲=4記録で5件)。本監査では実装しない。

**J4(副次所見・N5と無関係)** 【分類: 修正へ進む(OPEN-630 JA-GLOSS-NUANCE-01の調査対象へ追加する次委任案)】
- 公開Advancedの`Comment 4`(adv_19-s044「things left out with care」)の日本語訳が「省かれたもの」(`user_test/family_x_untidiness_family_resource_01/enduser/data/article.json` adv_19 `ja`)で、本文が示す語義(出しっぱなし)と食い違う(生成Commentの訳)。N5・KP抽出とは別系統。

## 9. 証跡(`ev01/`)

`occurrences.py`/`occurrences.json`/`occurrences_stdout.txt`/`mech_enum.json`(手順1・4、API 0)、`run_extraction_sampling.py`/`extraction_sampling_result.json`、`run_forced_eval.py`/`forced_eval_sel.json`/`forced_eval_result.json`、`run_l3_put_away.py`/`l3_put_away_result.json`、`run_supplement.py`/`run_supplement_qa.py`/`supplement_result*.json`、`run_diag_no_easy_exclusion.py`/`diag_no_easy_exclusion_result.json`、`cost_log_*.jsonl`/`cost_summary.json`、`console_*.log`、`stop_check_*.json`(開始時と各有料run前にrc 0)。再利用した既存記録: `docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03/m10/untidi_b1b/`・`fixtures/n5_trial_replay_fixture_01.json`。

注: 初回の`run_forced_eval.py`起動と`run_supplement.py`のQA部分は、worktreeをsparse checkoutにした際の資材不足(import先のデータファイル/テンプレート)でAPI呼出前に停止(費用0)。資材を追加して再実行した(同一原因の連続rc≠0ではなく別原因・API前停止)。`run_supplement_qa.py`は(1)のみを実行する別ファイルで、(2)は初回に完了済み。環境注意: C:ドライブ空き約0.8GB(`git worktree add`のフル展開がENOSPCで失敗したためsparse checkoutを使用)。
