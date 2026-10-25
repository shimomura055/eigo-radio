# DESIGN_02(Opus条件Aレビュー反映後。実装はこの設計に従う)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02 / 日付: 2026-10-25 / Status: DESIGN確定→KP側(X/Z共通核)実装済み・単体test PASS(IMPLEMENTED_PENDING_EVIDENCE。実API run=R1〜R4は翌日JST 10/26以降の別委任)
根拠: ユーザー指示原文 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`、`DESIGN_01.md`(未変更部分はそのまま有効)、`OPUS_REVIEW_01.md`(Opus条件Aレビュー、逐語保存)、委任_02(Fable判断。`docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_02.md`)。
この文書は**DESIGN_01との差分と、Fable判断で確定した事項**を述べる。DESIGN_01の原則(§0)・状態機械・署名・簡易運用はそのまま維持する。

## 1. DESIGN_01 → DESIGN_02 差分表
| # | 項目 | DESIGN_01 | DESIGN_02(確定) | 出所 |
|---|---|---|---|---|
| 1 | 選定Prompt | Prompt 2-R(Prompt 2を最大8件へ改変、E-0で上位3件同等性を事前確認) | **R-1採用: 2 call構成**。1 call目=**Prompt 2を無変更**(sha `a12896f4…3dc9a`固定)で上位3件、2 call目=新Prompt 2-V(上位3件を除く最大5件+日本語1文の理由)。E-0(同等性確認)は不要→削除 | Opus R-1、Fable採用 |
| 2 | 候補生成の置き場 | `kp_dir`直下(確定物と同じ場所) | **`<kp_dir>/kp_candidates/round_<n>/work/`で実行**。`keywords_canonicalized.json`/`vocab_confirmed.json`/`kp_selection_final.json`を書けるのは**finalizeだけ** | M-1 |
| 3 | Z gloss HR snapshot | 本文shaだけで復元 | snapshotに`selection_signature`を保持、不一致なら退避(`INVALIDATED`)。select/reselect/ng/unng/resolve-glossでも未消費snapshotを失効 | M-2 |
| 4 | Z `kp_<lv>`のinput_sha | 本文のみ | `sha(text|selection_signature)`。`_sync_kp_result`/`_result_gloss_diff`の照合キーを`candidate_id`(無ければused_form)へ。署名不一致なら同期しない | M-3(a)(c) |
| 5 | `--regenerate-stage kp_<lv>` | 確定済みならSTOP | **現在のreviewからの再finalize(再選定なし)+子孫stale化**。再選定は`reselect` CLIだけ。既存STOP文言の「--regenerate-stage kp_*」案内は「再選定」の意味を外した | M-3(b) |
| 6 | X再開 | 規定なし | review/候補が有効(本文sha一致)なら通常のscaffold/allでも**support(有料)を再生成せずKPはfinalizeのみ**。support成果物が無ければSTOP。rc=4には正確な再開コマンドを1つだけ表示 | M-4 |
| 7 | NG registry | 記事ID単位(run dir名を含むIDで実装すると新run dirで消える) | **`family+slug+level`キー、run dirの外の共有store**(`er119_output/kp_human_review_store_01/`)。run内に参照とコピー | M-5 |
| 8 | 不在宣言 | runに1つのmode file | **round/`candidates_sha256`に結びつけ、Humanの操作(select/reselect/ng/unng/resolve-gloss)で失効**。`declared_by`と出所を必須。AIが宣言する場合は`user_ref`(ユーザー発言の参照)必須。期限付き/範囲付き(family・日付)の宣言は**不採用**(ユーザー決定2026-10-25。委任_03でCLI・核・testから撤去。次のrunにも不在を宣言するなら起動ごとに宣言/`--kp-review auto`) | M-6、R-7(撤去) |
| 9 | item単位除外 | 「目標数未満ならretry」と「shortfall許容」が混在 | (a)canonicalization INVALIDは`item_reasons`のあるitemを除外し**残りで再実行、全体PASSのみ受理** (b)SRC D1(Z)・人称整合(Z)は候補単位に写す(不成立=`dropped(src_d1)`/`gloss_hr_pending`) (c)**外側retryは「AUTO採用可能な有効件数が3未満、かつGate除外が発生」した場合のみ**。retryは候補list全体を置換、vocabの4〜5件目不足はshortfallとして受容 | M-7 |
| 10 | Redundancy QA | 候補全体(≤8)の1回のみ | 候補全体は**提示用の旗**として残し、加えて**finalizeで確定KP集合(Advはvocab集合も)へ1回再適用**(費用約0.02〜0.1円/レベル)。NGはAUTO=次候補へ繰り上げて再判定、Human=PENDINGへ戻る | M-8 |
| 11 | `part1_items` | vocab欠落時は3件へfallback | **reviewが存在するなら`vocab_confirmed.json`必須(fail-closed)**。fallbackは`kp_human_review.json`の無い旧runだけ。`require_final_consistent`でvocab itemにも既存の消費側検査(`collect_unresolved`/`select_consumer_unevaluated`/Z `has_contract`)を適用。Part 1はvocabの連番rankで結合(KP側rankで結合しない) | M-9 |
| 12 | NG照合 | candidate_id/phrase_key/used_form_key | `used_form_key`は所有格代名詞(one's/your/his/her/their/my)をプレースホルダへ正規化。NG句を含む/含まれる句は`similar_to_ng`旗(AUTO対象外・Human選択可)。NG解除は`unng`(理由・記録必須)のみ | R-2 |
| 13 | 同時実行 | 未規定 | `O_EXCL`ロックファイル+版番号比較更新(`revision`+`candidates_sha256`)+`os.replace`。runnerのfinalizeも同じロック | R-3 |
| 14 | RESTART_STORM | 論点 | **安全機構は変更しない**。運用で間隔を明記(OPERATIONS_01)、testで発火条件を固定 | R-4 |
| 15 | 公開後の事後Review | 未規定 | `published_selection_signature`を別保存(`mark-published`)。一致検証の比較対象を公開版/確定版に分け、差は表示のみ(自動差替えしない) | R-5 |
| 16 | `--accept-ai` | 未規定 | REVIEWED扱い。表示した`candidates_sha256`を必須とし、未表示候補への了承は拒否 | R-6 |
| 17 | 再選定上限 | 案2回 | **2回/レベル/run**(確定) | Fable |
| 18 | 文法(Part 2) | 核はkind非依存 | 同じ(grammar層は実装しない。`kind="grammar"`の合成fixtureでの状態機械testのみ)。NG registryと`part1_items`もY入口で共有する旨をOPEN-484(g)へ追記 | C-6 |

## 2. 実装構成(KP側。コード=`er119_*`、Production runnerは最小限の差し替え)
| ファイル | 役割 |
|---|---|
| `er119_kp_human_review_01.py` | 共通核(`kind`非依存): state machine(PENDING_REVIEW/REVIEWED/UNREVIEWED_AUTO_ADOPTED/RESELECTION_REQUESTED/STALE)、review/候補/署名、ロック(R-3)、共有NG store(M-5)、宣言(`add_declaration`/`read_mode_declaration`=自動確定の単一読取点)、`validate_selection`/`auto_select`、`op_select/reselect/ng/unng/resolve_gloss/mark_published`、`finalize_kp`(idempotent)、`require_final_consistent`、`part1_items`、`verify_selection_matches_outputs`、`render_request_md`、`ensure_kp_review` |
| `er119_kp_prompt_2v_01.py` | Prompt 2-V(sha `e1d5349c…f5ec`固定。Prompt 2との差は冒頭文と条件6のみ。schemaは`phrase,reason_ja,word_count`の順)、`parse_selection`、`make_vocab_selector_fn` |
| `er119_kp_candidates_01.py` | 候補生成(call1=既存`ft`のselector・Prompt 2無変更/call2=2-V)、Gate(validate→CMU→canon→gloss→CMU post→記号→人称整合[Z]→SRC D1[Z])を候補単位に適用、外側retry(M-7c)、canonicalization INVALID再実行(M-7a)、確定集合Redundancy QA関数(M-8) |
| `er119_kp_wiring_01.py` | X/Z共通の入口`run_kp_with_review`(戻り値は`sc.run_key_phrases`互換+`kp_review`)、`review_resume_valid`(M-4)、`declare_from_runner_args`、`pending_banner` |
| `er119_kp_human_review_cli_01.py` | CLI: status/show/select/reselect/ng/unng/resolve-gloss/mark-published/declare-absent(`--accept-ai`・`--from-json`対応。拒否はrc=2) |
| `er019_family_x_audio_production_runner_01.py`(変更) | `run_theme_scaffold`のKP呼出を`run_kp_with_review`へ(`kp_backend=="fulltext_p2"`のみ。他は従来)、M-4再開、`_kp_already_generated`のreview例外、`_part1_kp_items`(M-9)、`--kp-review wait|auto`(auto引数のときだけ宣言を書く)、PENDINGならrc=4、tts/assemble/player等の入口でNotConfirmed=rc4/Inconsistent=rc3、player後の`verify_selection_matches_outputs` |
| `er026_family_z_fiction_production_runner_01.py`(変更) | `stage_kp`を「両レベルの候補生成→1回だけ待機(`FamilyZKpReviewPending`)→finalize」へ、M-2(snapshot署名)、M-3(a)(b)(c)、`_part1_items_b1b`、`load_level_inputs`/`stage_pages`の消費側検査、`stage_page_verify`の一致検証、mock/dry-runは確定集合Redundancy QAを実APIへ出さず決定論PASS、`--kp-review*` |
| **無変更** | `sc.run_key_phrases`(共有関数。source shaをtestで固定)、Prompt 2、A/B/C、Y Trial scaffold |

## 3. 状態遷移(要約)
```
候補生成(round n、work dir) -> PENDING_REVIEW --select/--accept-ai--> REVIEWED --finalize--> 確定物3点
                                    |  宣言(round n・candidates_sha一致・有効)             \--(確定集合Redundancy NG, Human)--> PENDING_REVIEW
                                    +--AUTO------> UNREVIEWED_AUTO_ADOPTED --finalize--> 確定物3点
                                    |                                       \--(確定集合Redundancy NG, AUTO)--> 次候補へ繰り上げ
REVIEWED/AUTO --reselect(NG付与可、上限2回)--> RESELECTION_REQUESTED --次回起動で新round生成--> PENDING_REVIEW(宣言は失効)
本文sha変更 --> STALE(確定物退避、NGは保持)
```
- **idempotent finalize**: `selection_signature`が同じなら本名ファイルを書き直さない(後段のgloss修復・`resolve_gloss`の編集を壊さない)。
- **旧run互換**: review無し・KP result+provenance entryがある旧runは従来どおり再利用(再選定しない・待機しない)。

## 4. Production到達経路と既定動作
- X(`er019_family_x_audio_production_runner_01.py`)・Z(`er026_family_z_fiction_production_runner_01.py`)の正式入口が`er119`経由。**宣言なし=候補生成後に待機(rc=4)が既定**(`APPROVED_FOR_PRODUCTION`仕様。DefaultOffではなく既定ONの待機)。
- 自動確定(UNREVIEWED_AUTO_ADOPTED)は**宣言ファイルがある場合だけ**。環境変数・hooks・設定dict・関数既定値・`.env`・起動scriptからは読まない(`read_mode_declaration`が単一読取点、testで固定)。
- **rc=4の衝突**: Zでは`RUN_LOCK`保持(二重起動拒否)もrc=4。区別はstdoutの`[KP_REVIEW_PENDING]`マーカー(判断候補・分類B=承認範囲内で自己解決)。
- XにはRESTART_STORM機構が無い(grep確認)。Zは5分間に3起動で`<run>/STOP`を自動作成(解除は`--clear-stop`)。運用手順は`OPERATIONS_01.md`。

## 5. 残課題(実装に含めず記録)
1. 公開済みXの**post-publication segment失効**(事後Reviewで確定が変わったときのsegment invalidate)はX側未実装。現状は`mark-published`+差の表示まで(Zは`mark_stale_descendants`の既存機構)。→ 次委任案(R1で必要性を確認)。
2. 実API run(R1〜R4)は翌日JST 10/26以降。mockでは実LLMの出力品質(8件のcanonicalization・Gate除外率・Human負担)は未検証。
3. ~~Part 2文法層はScope外~~ → 委任_03で統合済み(下記「委任_03追記」)。Y入口はScope外(OPEN-484(g)・OPEN-520で追跡、PRODUCTION_WIREDにしない)。

## 6. 委任_03追記(2026-10-25): 文法(Part 2)の統合・R-7撤去
- **R-7撤去(ユーザー決定: 不採用)**: 期限付き/範囲付きの不在宣言は作らない。残すのは(i)宣言なし=待機 (ii)明示宣言は候補sha・roundに結びつく (iii)Human操作で以後のroundの宣言は失効 (iv)`declared_by`・出所必須、AI宣言は`user_ref`必須だけ。`add_declaration`から`scope`/`until`、CLIから`--scope-family/--scope-date/--until`、核から`scoped_declarations_dir`/`_today_jst`を削除(残存Grep=0はRESULT_PACKET_KPHR3.md)。
- **文法のHuman Review統合**: er119共通核を`kind="grammar"`で使う(`er119_grammar_review_01.py`)。状態機械・NG registry(`family+slug+level`、文法は別file)・排他lock・revision CAS・単一読取点`read_mode_declaration`(KPと文法で同じ宣言を共有)はKPと同一。待機は**1回**: 統合依頼書`<run>/review_request.md`+`[KP_REVIEW_PENDING]`1つ+rc=4(Z=`FamilyZKpReviewPending`)。
- **er120 DESIGN_02 §3の6要望との対応**: ①確定statusの受理集合=`REVIEWED`/`UNREVIEWED_AUTO_ADOPTED`/`NO_CANDIDATE_UNREVIEWED`(`FORWARD_STATUSES_BY_KIND["grammar"]`) ②`finalize_review_record`が確定署名`selection_signature`を作り、Zの`part2_b1b`のinput shaと使う側の入口(`require_fresh_part2`)が同じ署名を検証 ③候補docのNG再適用(新NGで候補が変われば新review) ④`NO_CANDIDATE_UNREVIEWED`=待たずに確定・レビュー済みに数えない ⑤KP+文法の統合依頼書・rc=4を1回 ⑥事後Review=`grammar-select`で変更→署名変化→Z=`part2_b1b`が親sha不一致でSTOP→`--stage kp --regenerate-stage part2_b1b`(再finalizeのみ・再抽出なし)/X=`--stage study_text`。
- **Z来歴**: `part2_cand_b1b`(入力=本文sha+label)、`part2_b1b`(入力=sha(本文sha|label|文法の確定署名))。いずれも`ensure_stage`を通り、有料呼出の前に同じ規則のpre-checkを行う。`DEPENDENTS`は`r2→part2_cand_b1b→part2_b1b`のみ(`kp_b1b→part2_b1b`は**置かない**: Part 2の確定はKP選定に依存せず、Part 1の訳は参考訳でしかない)。
- **X**: Step A''はb1b scaffoldの先頭(support・KPより前)。未確定は文法/KPのどちらでもPart 1・Step Bを呼ばずrc=4。確定後の同じコマンド再実行でStep B(+Part 1)。失敗は`part2_failed.json`+rc=3、案内は`--stage study_text`の1つ(`--stage scaffold`/`all`は案内しない)。
- **ページ**: Part 2はAdvancedだけ(X=player.html、Z=index.htmlのAdvancedの節。standard/advanced.htmlの開発確認ページには出さない)。描画は`compose_page_html`(=`g.compose_study_html`)の1関数。X公開ページ用の`er120_part2_wiring_01.public_study_html`が同じ関数を通り、Part 1の入力は`part1_items`(vocab_confirmed.json、最大5件)。`study_html_for_audio_dir`は従来経路(items未指定)を無改変で残し、`items=`を渡す呼出だけがvocab5件を使う。
- **0件の表示**: DESIGN_01 §kの旧記述『Part 2コーナーなし』を撤去し、Trialの実出力どおり`ZERO_P2`(固定文面)をページ・md・htmlに載せる(適格0件=`NO_CANDIDATE_UNREVIEWED`、または全候補NG後にHumanが`omit`)。
- **W1**: `STUDY_TEXT_GRAMMAR_EXTRACT`/`STUDY_TEXT_GRAMMAR_EXPLAIN`をer006の`PROCESS_MODEL_MAP`へ登録(SUPPORT_MODEL=gpt-6-luna。登録前のfail-closed testはP1[登録済み+応答モデル不一致でSTOP]へ置換)。
