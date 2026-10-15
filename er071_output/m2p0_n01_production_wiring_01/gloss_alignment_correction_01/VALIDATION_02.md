# VALIDATION_02 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02、2026-10-15)

**Trial Closeout Status: `USER_DECISION_REQUIRED`**(`VALIDATED`/`REJECTED`のどちらでもない。理由は6節)。`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`ではない。Production既定は`legacy`(現行挙動)のまま、量産runは凍結(承認前はKP段を含む量産runを出さない)。
全結果はDEV/Trial専用mode=correctedの結果。費用の合計はJPY2.4947(上限JPY10、日次1,000円の約0.25%)。

## 0. 事前調査(Opus未確認事項)
### 0-1 gloss消費元の全数(`rg "japanese_gloss_tts|japanese_gloss\b|ja_gloss" --glob "*.py" -l` -> 約150ファイル。Production系のみ分類)
| 呼出元 | 用途 | 関所 | 備考 |
|---|---|---|---|
| `er019_family_x_audio_production_runner_01.py` L898(`_resolve_kp_explanations_text`) | B1解説LLM入力 | `_generate_key_phrase_segments_b1`冒頭のHR待ち早期return(解説LLM 0 call) | T3 p |
| 同 L994(`expl_r["display_gloss"]`) | B1表示用 | 同上の早期return後は到達しない | |
| 同 L1248-1270(A2 `meaning_{i}.wav`・`ja_gloss_tts`) | A2 KP日本語TTS | `_generate_key_phrase_segments_a2`冒頭のHR待ち早期return(TTS 0 call) | T3 i-A2 |
| 同 L1890(`_row_info_family_x`のpage表示) | page/player | assemble summary=OKのlevelだけ到達+`_build_level_table`に多重防御 | T3 q |
| `er019_family_x_kp_explanation_01.py` L147-155 | B1解説プロンプト | 呼出元が上のX/Z(関所の後) | |
| `er026_family_z_fiction_production_runner_01.py` L1195(`runner_ex`)・L1218(`load_level_inputs`) | Z解説入力/TTS・Gate・Assembly共有入力 | `stage_kp`のHR gate(解説stageより前でFamilyZE2EStop)+`load_level_inputs`の関所 | T3 j/m/l-Z |
| `er063_family_z_audio_01.py` L487(`build_level_plan`の`ja_gloss_tts`) | Z KP日本語TTS plan | `load_level_inputs`経由のみ(関所の先) | |
| `er057_coffee_final_v3/v4/v5_page_01.py`等 | 完成済みCoffee用の個別page builder | **関所なし**。ただしProduction runnerではなく完成済みartifactを読むoffline script。corrected modeで作られたartifactはまだ存在しない | 対象外(一覧のみ) |
| `er003_v1_n3_01_tts_generate.py` L1060/L1207ほか、Legacy A/B/C(`er003_v1_*`/`er011_*`/`er012_*`/`er013_*`/`er014_*`等) | 旧Family A/B/C等のTTS/表示 | **corrected modeを受け取らない**(`sc.run_key_phrases`既定=legacy)ため、HR待ちstatusのartifactは生成されない | 対象外(一覧のみ) |

結論: Production Family X/Zの経路に関所を経由しない呼出元は無い(素通りなし、STOP条件に該当せず)。corrected artifactを読むoffline page scriptが今後作られる場合は関所の追加が必要(現時点で該当なし)。

### 0-2 page/player生成の順序
X: `--stage player`(`build_player_html`)はassemble(Gate+新チェック通過)後の`run_summary_assemble.json status=OK`のlevelだけtableを作る(未完了は「Assembly未完了。table省略」)。Z: `stage_pages`は`assemble`後。いずれもGate/関所より後でしか実行されない。

### 0-3 `tts_generation_results.json`欠落
`verify_episode_audio_validation_gate`は欠落時に即return(既存fail-open、無変更)。corrected artifactについては`stage_assemble_family_x_*`が**Gateより前に**`_assert_no_gloss_alignment_hr`で拒否する(T3 o: Gate素通り=True、新チェックが`EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT`)。Gate自体は変更していない。

### 0-4 `w62.ensure_stage`
出力+provenance entryが無ければrunnerを再実行(runner内の例外では保存されない)=**Zは再開時に選定から再実行される**(Opus推定の確認)。→ HR停止時にKP段結果のsnapshotを保存し、解消後の再開は復元(選定非再実行)にした(T3 l-Z)。

## 1. オフライン(JPY0、決定論)
### 1-1 unit test(O3): `er003_test_key_words_gloss_alignment.py` 70/70 PASS(旧34件は無変更+新規36件)
新規: mode分離(既定legacy・envでは切替えない・Production runnerはmodeを渡さない・証跡scriptが参照するlegacy記号が残る)/追加内容語算出(機能語除外)/span対応(合格・span不実在[幻覚]・記号のみ・欠落・多対一・語幹・NFKC+空白除去)/item検証(『～』は合否に使わない、真⇔不変の矛盾、正規化は空白と～/〜のみで採用値はcurrent原文、記号チェック維持、mapping gate)/item単位retry(2回目は未解決のみ送信、各itemは最初の有効出力採用、技術失敗/JSON不正も消費、KPを候補へ戻さない)/課題指示文(矛盾文削除・OF-KGDC (b)文・承認規則sha不変)/HR報告書(必須項目・再読検証・fail-closed・古い報告書除去・queue/Lock不使用)/`resolve_gloss`(記号違反は書込まず拒否・HR待ち以外は書換えない)/scaffold統合(corrected成功・失敗でartifactにHR状態・legacyのcall形不変・最終artifactに対して1回event)。

### 1-2 O1/O2/relabel(`OFFLINE_AUDIT_02.json`、`er071_gloss_alignment_correction_01_offline_audit_02.py`)
- **O1: 226 record / 1,129 item、対象7(0.6%)、対象外1,122 itemのmerged差分 0、対象外itemがLLM入力に載った数 0、対象0件recordでのLLM呼出 0(mergedは同一object)、LLMが「整合」と答えた対象itemのgloss/KP変更 0。PASS**。(fakeがgloss=Noneの対象1件を空glossで返したため再試行が1回発生=呼出8回。実害なし。APIは呼んでいない)
- O2: 追加内容語の機械算出: `based on interviews`→interviews / `raw-bean prices`→prices / `bring in a human helper`→human,helper / `close around me`→me(aroundは機能語で除外) / `urge to watch`→watch / `locked into a narrow view`→narrow,view 等、既知8ユニークすべて算出。
- **census「『～』あり」29件の再点検(OF-KGDC-07)**: 旧「28/29が正当」は訂正。`put solo travel at`(承認規則15行の数値穴埋め型=期待NG)1、STALE_OMISSION(`urge to watch`)1、REVIEW_NEEDED 3(`draw on`『〜のデータを利用する』[過剰具体化の疑い]/`stay on`『～に向けたままでいる』/`account for`『〜を説明する要因となる』)、範囲表記(`moderate-to-vigorous activity`)1、機械推定の辞書的な正当23。**目視は上記6件のみ(Sonnet、ユーザー未確認)、残る23は機械推定**。

### 1-3 T3 mock統合(`trial_t3/T3_RESULTS.json`、27/27 PASS、実API・実TTS呼出0、`TTS_EXECUTION_MODE=STANDARD`明示)
(a)API例外2回/(b)JSON不正2回/(c)不正gloss2回→HR待ち+報告書+event+専用stdout / (d)mapping欠落: gate判定=HR待ち、record-only=採用+machine_check不合格を並記 / (e)1回目失敗→2回目成功=HR無し / (f)2回失敗: 必須項目(article/level/rank/英語KP/現gloss/失敗理由/全attempt/再生成候補[提案gloss・欠落語・参考候補+旧gloss+「人間判断でのみ採用」・KP再生成])+event+stdout、**queue/Lock/attempt_history/Master Store/telemetry/cost_summaryのsha不変**(r) / (g)batch内一部成立・一部失敗(item単位) / (h)報告の書込失敗(json/md)・再読検証失敗→`GlossAlignmentNotificationError`(fail-closed、X・Z両方) / (i-A2)(p)B1: 当該level KP segment全体が`STOPPED_GLOSS_ALIGNMENT_FAILED`・TTS/解説LLM/解説TTS 0 call・Gateが`EPISODE_BLOCKED_BY_AUDIO_VALIDATION` / (o)results欠落 / (q)page / (j)Z `FamilyZE2EStop`(assets未配備・stage結果未保存・TTS 0 call) / (m)tts段単独実行でも保留(assets不在=例外、HR待ちartifactコピーでも`load_level_inputs`が停止) / (l-X)(l-Z)解消→再開(Zはkp_fn呼出が増えない=選定非再実行、解説sigにgloss、snapshot消費) / (n)(n2)外側redundancy retry後にHR孤児なし・最終attemptのみ報告 / (k)legacy既定の挙動がHEAD版と同一(4シナリオ+flag OFF)・X legacy FAILEDは従来どおり素通り(挙動不変)・Z既定ctxはlegacy / (t)独立level継続 / (v)scaffoldのmode受渡し / (exit)別プロセス実行でZ=FamilyZE2EStopで非0終了、X=Gate拒否で非0終了(条件③) / (api0)。

## 2. Regression(legacy既定、`regression/`)
| suite | 結果 |
|---|---|
| `er003_test_key_words*` | 402/402(旧366+新規36) |
| `er003_v1_n3_01*_test*` | 55/55 |
| `er019*_test_*` | 421/421 |
| `er030*_test*` | 108/108 |
| `er063*_test_*` | 59/59 |
| `er008_audio_validation_gate_05_test.py` | pytest 10/10(`run_project_regression`は関数形式testのため0件収集=既存仕様) |
| `er003*_test_*`(全体) | 1655/1659(既存failure 4、HEAD以前から) |
| `er011*_test_*` | 289/292(既存failure 3) |
| `er026*_test_*` | 79/86(既存failure 7、HEAD版に差替えても同一7件) |

**新規failure 0**(`regression/PREEXISTING_FAILURES_CHECK.md`に切り分け根拠。実装中に`__defaults__[-1]`固定testが落ちた件はkeyword-only化で是正済み)。

## 3. 有料Trial(fresh、gpt-6-luna、high、mode=corrected。STOP確認後に実行、rc=0)
- **使用モデル**: 要求=応答とも`gpt-6-luna`(現行SUPPORT_MODEL=本番ラインと同一)。最新世代の最上位/推奨系の現行ラインとして採用(開発評価用最新モデル原則に従い旧/下位モデル・下位effortは不使用)。**最新性の外部再確認は本Trialでは実施していない**(前回VALIDATION_01の記載に依拠)。
- 承認規則: 実行時抽出、sha256 `447e07cb…`(不変)。mapping gate=OFF(record-only+gate判定並記)。
- **費用**: T1(P1〜P5+P7一括、14 call、retry 0)JPY1.8653(うちP7相当 約0.35[12/64 eval按分])/ T2(6 call)JPY0.6294 / **合計JPY2.4947**(上限10、日次1,000円の0.25%)。実行時間: T1 51秒(7並列)、T2 18秒。usage合計: T1 in 21,222/out 20,977/cached 10,590 tok、T2 in 8,882/out 6,890/cached 4,432 tok。batch単価: T1平均0.133(旧replay high 0.114の+17%、新スキーマ`added_word_mappings`分)、T2平均0.105。
- 証跡: `trial_t1/results_P1_P2_P3_P4_P4b_P5_P6_P7.json`、`trial_t2/results_T2.json`(全行・全attempt・usage・cost・machine_check・mapping)。

### 3-1 率(item単位、n=eval数。95%上限=Clopper-Pearson片側)
| 指標 | T1(64 eval) | T2(24 eval) | 合算(88) |
|---|---|---|---|
| 1回目attempt INVALID率 | 0/64 (0%、上限4.6%) | 0/24 (0%、上限11.7%) | 0/88 (上限3.3%) |
| 2回とも失敗した率(=HR到達相当) | 0/64 (0%、上限4.6%) | 0/24 (0%、上限11.7%) | **0/88 (0%、上限3.3%)** |
注意: 実LLMで**2回目のretry経路は一度も発火していない**(14+6 call全てが1回で全item成立)。retry/HR経路の動作はmock(T3)でのみ確認。

### 3-2 パターン別結果
| パターン | eval | 結果(自動近似+全出力の目視) |
|---|---|---|
| P1 拡張KP・既知不整合 | 12 | 12/12で欠落語が反映(`インタビューをもとにした`/`焙煎前のコーヒー豆の価格`/`人間の助っ人を連れてくる`/`私を取り囲むように迫ってくる`/`見たい衝動` 等)。『～』『〜』2表記ともinterviewsを反映。最終不整合0(目視) |
| P2 整合済み | 4 | 不変 4/4、書換 0 |
| P3 『～』正当表現(対象へ強制投入) | 16 | 不変 12/16、**書換 4/16 (25%、上限48.4%)**: `fall into`『～に落ちる』→『～に陥る』、`speak for`『～の代わりに話す』→『～を代表して話す』(2 rep共に同じ2件)。意味は近いが不必要な書換え。他6表現(point to/answer for/keep up with/turn out not to be/be associated with/put good odds on)は不変。これらは本番ではLLMに渡らない(O1)強制投入のストレス |
| P4 具体語欠落の注入 | 12 | 12/12で欠落語が反映。**直訳気味1件**: `run out of fresh water`rep1が『新鮮な水がなくなる』(rep2は『真水がなくなる』で自然)。自動keywordは「水」を許容したため機械では検出されず目視で指摘 |
| P4b 規則15行型(`put solo travel at`)観察のみ | 2 | rep1『ソロ旅行を～とする』(％を落とすが数値スロットは残る)、rep2は『ソロ旅行を～％とする』を整合と判定して不変。**再整合段は規則15行違反(選定段の責務)を検出しない**=想定どおり。合否には使わない |
| P5 人称・主語語 | 6 | 6/6反映(`私に迫ってくる`/`時間をかける`/`息を整える`) |
| P7 追加語あり×自然な慣用的訳 | 12 | **不変 12/12、record-only誤NG 0/12 (上限22.1%)、gate判定の追加誤NG 0/12**。LLMは慣用句を1span/多対一で対応させた(例: `make ends meet`→meet=やりくりする、`bring in a human helper`→human=人/helper=手[人の手を借りる]) |
| T2 span実在・意味違い注入 | 24 | **検出 24/24 (誤PASS 0/24、上限11.7%)**: ニュース→インタビュー、量→価格、彼ら→私、機械→人、利益→費用、大→小、結果→原因、外国→地元、塩→真水、意味反転、直訳(豆をこぼす→秘密をばらす/氷を割る→場の緊張をほぐす)をすべて不一致と判定し修正。gate判定が捕捉できてrecord-onlyで採用された件=0 |

### 3-3 record-only vs gate判定(機械検査の採否材料)
- gate判定(`machine_check_pass_gate=False`)になった件: T1 0/64、T2 0/24。= gate化しても今回の標本では誤NG追加0・追加の誤PASS捕捉0。
- 機械検査が効く場面(T3 d): LLMが`added_word_mappings`を欠落/不正で返した場合のみgateがHR待ちにする。意味が誤ったspan(prices→量)は機械では通る(Opus (e)のとおり)ので、T2の検出はLLM判定が担った。
- 結論(Trial標本の範囲): gate化の効果は**実LLMでは未観測**(今回は常にmappingが埋まった)。有効性の判断材料としては弱い。gate化はユーザー判断(Production品質条件の追加)。

### 3-4 直訳化・既存glossへの副作用(目視、Sonnet、ユーザー未確認)
- 直訳化: P1/P4/P5/T2の最終glossは平易で自然。軽微な指摘は`新鮮な水がなくなる`(1/2)のみ。P7(慣用句)は全件不変で直訳化への圧力は観測されず。
- 既存gloss副作用: 本番経路では対象外itemは不変(O1差分0)。対象itemに強制投入した場合の不必要書換えは、P2 0/4・P7 0/12・P3 4/16。

## 4. KPI provenance
T1/P7/T2の率・合否: fresh(本委任の実API)。O1/O3/T3/Regression: synthetic/mock(決定論)。census由来(対象7・0.6%・1,129 item・29件relabel): reuse(census_01.json)+Sonnet目視。E2E自己確認: No(fresh Production初回pathは含まない。Trial専用modeでの関数レベル実行+mock統合)。

## 5. 追加量産費・実行時間・HR見込み頻度(推定、出典付き)
- 単価: 5 item/batch 1 callの実測平均 0.125(T1+T2: 2.4947/20 call)。`cost_01.json`の旧単価0.1137に対し約+10%。旧見積り(通常0.014〜0.08、最悪0.57、絶対最悪1.7/記事セット)を同率でスケールすると 通常0.015〜0.09、最悪0.63、絶対最悪1.9(推定)。**1〜2円級の恒久増にはならない**(70円/記事セットの約0.02〜0.13%)。
- 時間: 1 call 約15〜25秒(7並列実行時の壁時計から)。対象itemがある記事のlevelに限り+15〜50秒(1〜2 attempt)。対象は全itemの0.6%・記事の約7%。
- HR見込み頻度: 実測の「2回とも失敗」0/88(上限3.3%)。記事levelあたり対象約1件と仮定すると、HR到達は**点推定0、上限は約0.23%/記事level**(= 3.3% × 対象記事率約7%)。ただし実LLMでretry経路が未発火で、上限は標本88件に依存する。

## 6. 判定: USER_DECISION_REQUIRED(理由)
TRIAL_PLAN_02の基準に照らす:
- REJECTED条件: 該当なし((a)最終不整合0、(b)(c)(d)(e)はT3/O1/Regressionで問題なし、(f)費用はGuardrail内)。
- VALIDATED条件のうち**未達が1つ**: 「P2/P3の書換・誤FAIL 0」→ P3の強制投入で4/16書換(P2は0/4、P7は0/12)。計画の分類基準どおり**許容度判断をユーザーに仰ぐ**(`USER_DECISION_REQUIRED`)。それ以外(O1差分0・呼出0、O3/T3全PASS、P1/P4/P5最終不整合0[直訳気味1件を除く]、P7 record-only誤NG 0、T2誤PASS 0)は達成。
- 選択肢(Production採用ではない): (a)許容(本番では対象外itemがLLMに渡らずO1差分0。対象item内でも整合済みglossの書換えはP2/P7で0)(b)課題指示文に「意味が一致していれば自然さ目的の言い換えをしない」旨を足して再Trial(承認規則本文は不変、指示文のみ。要承認・追加Trial費用は数円)。**本委任では(b)を独断実施していない**。

## 7. 本当にユーザー判断が必要な事項(承認境界)
1. Production採用そのもの(corrected modeの既定化、Human Review例外対応の正式化)。現状は`APPROVED_FOR_PRODUCTION`なし・既定legacy・量産run凍結。
2. 機械検査(追加語→span対応)のgate化(今回の標本では追加の捕捉0・追加の誤NG 0。意味誤りspanは検出できない)。
3. P3型の不必要書換え4/16の許容度、または課題指示文の追加1文(上記6(b))。
4. 既定ON/OFF(別UDR)。
5. OF-KGDC-11(Family X `NG_REVIEW_REQUIRED`素通りの疑い)の扱い(別OPEN、未実装)。

## 8. 注意・限界
- 実LLMでretry/HR経路が未発火(全itemが1回目で成立)。retry・HRの動作はmock統合のみで確認。
- P3等の目視ラベル・直訳評価はSonnet(ユーザー未確認)。標本は小(T1 64、T2 24、ユニーク約30)で、上限値を併記。
- `.env`: 有料Trialの認証は既存の`ga.make_alignment_fn`(内部で`load_dotenv()`)経由。.envの内容は読み書きしていない。
- 本Trialのgate判定はrecord-only既定で集計しただけで、Productionに品質条件を追加していない。
