# DESIGN_01(KP・単語解説・文法 Human Review 正式導入の設計。実装は別委任)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_01 / 日付: 2026-10-25 / Status: DESIGN(APPROVED_FOR_PRODUCTION仕様の設計。Opus条件Aレビュー待ち。Production file変更0・API 0)
根拠: ユーザー指示原文 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`、既存仕様 `EXISTING_SPEC_CHECK_01.md`(同dir)。

## 0. 設計原則(要約)
1. **下流の接続面を変えない**: 確定したKPは従来と同じ `keywords_canonicalized.json`(rank 1..n)へ書く。TTS・Adv解説・Gate・組立・公開ページのKP部は無変更。変えるのは「そのfileが何によって作られるか」だけ。
2. **Human確定の単一正本**: `kp_human_review.json`+確定署名。retry/regeneration/resumeはこの正本を読み、**再選定しない**。
3. **自動確定は明示宣言のみ**: 既定は待機(STOP)。期限による自動切替・環境変数/起動script/`.env`による暗黙ONは作らない。
4. **既存Gateは省略しない**: validate/CMU/canonicalization/gloss/Redundancy/記号を**候補段階で適用**し、不合格は順位から除外して記録。AUTOは合格候補だけを順位順に採用。
5. **共有関数 `sc.run_key_phrases` の既定動作は変えない**(A/B/C・Y Trial無影響。27-7)。新module(`er119_kp_human_review_01.py`、名称は実装時に衝突確認)をX/Z runnerからだけ呼ぶ。
6. **文法(Part 2)は同じ核を `kind="grammar"` で使えるが、Part 2のProduction採用が確認されるまで配線しない**(§k)。

## a. 候補生成(TOP 8)
### a-1. 選定(Prompt 2-R)
- 現行Prompt 2(一字一句固定、sha256 `a12896f4…`、`er105_kp_fulltext_selector_01.py:51-67`)は「3つ選ぶ」。TOP 8には文言変更が必須(判断候補I-2)。**最小差分の案(Prompt 2-R、未凍結・Opus/Fable確認後にsha固定)**:
  - 冒頭「…学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。」→「…を**学習価値の高い順に最大8つ**選んでください。」
  - 条件6「3件選定」→「**最大8件・順位付け**:条件を満たす候補から学習価値の高い順に最大8件を選び、1位から順に並べる。適切な候補が不足する場合のみ8件未満とし、数合わせはしない。」
  - 追記1文「各候補に、選んだ理由を日本語で1文(40字以内)添える。」
  - 条件1〜5と最終確認文は**1字も変えない**(testで`p2r.replace(差分)==p2`をassert)。schemaは`items[{rank, phrase, word_count, reason_ja}]`(件数はローカル検査。strict JSON)。
- **上位3件の品質同等性**: Prompt変更で「8つのTOP3」が旧「3つの選定」より悪化しないことを、保存済みの記事(X/Zの既存run、約12記事レベル)で旧Prompt 2の3件と新TOP3を並べ、既存Validator通過率+Sonnet所見+Fable確認で比較する小規模paid check(推定1円未満、BUDGET_PLAN_01 E-0)を実装前に行う。悪化が見られた場合の代替案(P2: 旧Prompt 2をそのまま1 call目(上位3件)+「4〜8位追加選定」call。順位の一貫性が弱くcall増)も評価対象。
- レベル適合: 現行はStd/Adv別Promptが無く、**各レベル本文に同一Promptを適用**している(EXISTING_SPEC_CHECK_01 §1)。新設のレベル判定Gateは作らない(未規定ルールの独断追加を避ける)。候補にはsource_levelを記録するのみ。
### a-2. 候補単位のGate(既存規則をそのまま、候補ごとに適用)
- 順序(既存と同一): `validate_and_resolve`(連続一致・語数・重複・旧形式)→ CMU(`er108`)→ canonicalization(基本形化・人称一般化)→ gloss再整合 → CMU post-canon → 記号検出 → SRC D1(Zのみ。候補artifactに対して実行し、source_sentenceを確定してから提示)。
- **現行は「1件でも不適合なら選定attempt全体をINVALID→再選定」**(`er105…:225-263`、`run_kp_with_outer_retry`)。8件ではこの規則だと再選定が頻発し費用・時間が悪化する。設計: **item単位で不適合を`dropped`へ移し(理由記録)、有効候補が目標数(KP3/Adv vocab5。shortfall許容は現行と同様に1件以上)に達すればattempt成功**とする。目標未満なら現行の外側retry(上限`KP_OUTER_RETRY_MAX=3`、除外語を累積して次周のnoteへ)。**Gate自体の判定基準は不変**(判定を緩めるのではなく、不適合itemの扱いを「全体NG」から「そのitemだけ除外」にする)。→ Opus論点O-3。
- canonicalizationの3状態: `PASS`=候補として合格 / `REVIEW_REQUIRED`(QA FAILのitem)=`qa_fail`旗付き**AUTO対象外・Human選択可**(承認済み「人間確認後に採用可」の実装。ただしHuman選択時は`--accept-qa-fail <id>`の明示が必要) / `INVALID`(構造不正)=そのitemを除外。応答全体が構造不正のときは現行のcanon gateのretryに従う。
- gloss: 再整合不成立(`FAILED_HUMAN_REVIEW_REQUIRED`)の候補は`gloss_hr_pending`旗。AUTO対象外。Humanは既存`resolve_gloss`後に選択可。
- Redundancy QA: 候補全体(≤8)で**1回**実行して`duplicate_pairs`を候補ファイルへ保存。以後の選択集合検査は**保存済みpairとの照合のみ(API 0)**。Humanが両者を選ぶ→拒否(別候補を促す)。AUTOは順位順に走査し、既採用候補とpairになる候補を飛ばす。
### a-3. `kp_candidates.json`(スキーマ案)
```
{ "schema":"kp_candidates_v1", "level":"b1b|a2", "text_sha256":"…", "prompt_id":"kp_prompt_2r","prompt_sha256":"…",
  "model_requested":"gpt-6-luna","model_id":"…(actual)","generated_at":"…","round":1,
  "candidates":[{"candidate_id":"c1","ai_rank":1,"raw_rank":1,"selection_phrase":"…","used_form":"…","japanese_gloss":"…",
     "source_sentence":"…","source_sentence_id":"…","word_count":3,"reason_ja":"…",
     "gates":{"validate":"PASS","cmu":"PASS","canonicalization":"PASS|REVIEW_REQUIRED","gloss":"ALIGNED|HR_PENDING","symbol":"PASS","src_d1":"PASS|NA"},
     "flags":{"qa_fail":false,"gloss_hr_pending":false,"redundant_with":[]},
     "auto_eligible":true,"human_selectable":true,"item":{…既存keywords_canonicalized.jsonのitemそのもの…}}],
  "dropped":[{"raw_rank":4,"phrase":"…","stage":"validate|cmu|canonicalization|cmu_post_canon|symbol|human_ng","reasons":["…"]}],
  "redundancy_qa":{"status":"…","duplicate_pairs":[…],"model_id":"…"},
  "shortfall":false,"candidates_sha256":"…" }
```
`ai_rank`=Gate通過後の順位(1..n、AUTO/表示の基準)、`raw_rank`=LLM出力順。`candidate_id`は`phrase_key`由来の安定ID(再選定で同じ句が出ても同ID=NG照合に使う)。

## b. Review状態機械と切替
### b-1. `kp_human_review.json`(レベルごと、`<kp_dir>/`)
```
{ "schema":"kp_human_review_v1","level":"…","text_sha256":"…","candidates_sha256":"…",
  "status":"PENDING_REVIEW|REVIEWED|UNREVIEWED_AUTO_ADOPTED|RESELECTION_REQUESTED|STALE",
  "mode_declaration":{"mode":"wait|auto","declared_by":"…","declared_at":"…","reason":"…","source":"cli_runner_arg|declare_absent_cli"}|null,
  "selection":{"kp":["c1","c3","c5"],"vocab":["c1","c2","c3","c5","c7"]},       // Stdはvocab無し。kp⊂vocab
  "accept_ai_default":false,"accepted_qa_fail":["…"],
  "verdicts":{"c1":"SELECTED_KP","c2":"SELECTED_VOCAB","c4":"NG","c6":"NOT_SELECTED","c8":null},   // null=未レビュー
  "ng":[{"candidate_id":"c4","phrase_key":"…","used_form_key":"…","reason":"…","by":"…","at":"…"}],
  "reselect_count":0,"history":[{"at":"…","event":"…","by":"…","detail":{…}}],"selection_signature":"sha256(…)" }
```
- **未レビューとNGの区別**: `verdicts[c]=null`(未レビュー)と`"NG"`(Humanの明示NG)と`"NOT_SELECTED"`(Humanが見たが選ばなかった。NGではない=再選定時も除外しない)を別値で持つ。AUTOでは全`verdict=null`、`status=UNREVIEWED_AUTO_ADOPTED`。
- 状態遷移: `(file無し)`→`PENDING_REVIEW`(候補生成直後、modeが`wait`または未宣言)/ `PENDING_REVIEW`→`REVIEWED`(selectコマンド)/ `PENDING_REVIEW`→`UNREVIEWED_AUTO_ADOPTED`(**`auto`宣言がある場合のみ**)/ `PENDING_REVIEW|REVIEWED|UNREVIEWED_AUTO_ADOPTED`→`RESELECTION_REQUESTED`(reselectコマンド。下流はstale化)/ `RESELECTION_REQUESTED`→(候補再生成)→`PENDING_REVIEW`(`round`+1、旧候補は`kp_candidates.SUPERSEDED_n.json`へ退避)/ `UNREVIEWED_AUTO_ADOPTED`→`REVIEWED`(事後Review。下流stale化。公開済みなら記録のみで自動差替えしない)/ 本文sha変化→`STALE`(退避、候補再生成)。**`REVIEWED`→`UNREVIEWED_AUTO_ADOPTED`への降格遷移は存在しない**。
- 下流が進めるのは`REVIEWED`と`UNREVIEWED_AUTO_ADOPTED`のみ。それ以外(`PENDING_REVIEW`/`RESELECTION_REQUESTED`/`STALE`/ファイル不整合)は全入口でfail-closed。
### b-2. 「判断待ち」と「不在として進める」の区別
- **判断待ち**=`PENDING_REVIEW`でmode宣言なし(または`wait`)。runner は候補生成まで行い、`kp_human_review_request.md`を出力、**rc=4(`KP_REVIEW_PENDING`、失敗ではなく待機)**で停止し次コマンド(review/declare-absent)を表示する。TTS等の有料工程へ進まない。
- **不在として進める**=運用者(Fable/ユーザー側の操作)が**明示的に**宣言する: (i) 起動引数 `--kp-review auto`(その起動の対象runのみ)、または (ii) `declare-absent` CLI(`kp_review_mode.json`をrun dirへ書く。複数run一括可)。宣言は`declared_by/at/reason`と共に`history`へ記録。以降`UNREVIEWED_AUTO_ADOPTED`で継続。
- 既定を自動確定にしない理由: 指示の「誤った自動確定が起きない」「HumanがNGとした候補を自動採用しない」を満たすには、**「Humanが見ていない」と「Humanが不在と宣言した」を機械が取り違えない**必要がある。無宣言=待機とすれば、`auto`が走った事実が必ず運用者の操作に紐づく。**期限付き自動切替(一定時間後にauto)は採用しない**(待機中にHumanが戻る/NGを付ける競合、時刻に依存する非再現な確定、指示に反する誤確定の温床)。
- 「無期限停止しない」の担保: (1) 停止は有料工程の手前(KP候補生成のみ消費)で、1回の宣言(複数run一括可)で全runが再開できる。(2) `status`コマンドで全runの待機一覧。(3) 運用手順: 毎朝の制作開始時にFable/ユーザーが「レビューする/不在宣言」を選ぶ(9記事/日でも宣言は1コマンド)。(4) 不在宣言後でも事後Reviewで差替え可能(公開前)。
- 環境変数・設定dict・`.env`・起動script・関数既定値のいずれからも`auto`にできない(関数の`mode`引数既定=None→待機。CLIの宣言ファイルとrunner引数以外に読取点を作らない=単一読取関数`read_mode_declaration()`)。
### b-3. 選択の検証(select時と確定時の2回、同じ関数)
- `kp`は1〜3件、`vocab`は(Adv)`kp`を含む1〜5件、Stdは`vocab`不可。
- 全て`human_selectable=true`、NG集合と交差しない(`candidate_id`/`phrase_key`/`used_form_key`の3キー照合)、`redundant_with`で互いに競合しない、`qa_fail`は`accepted_qa_fail`明示、`gloss_hr_pending`は`resolve_gloss`済みのみ。
- `--accept-ai`=AI推奨(AUTOと同じ選択規則)をHumanが了承する短縮形。`status=REVIEWED, accept_ai_default=true`(**AUTOとは区別**=人が見て承認した記録)。

## c. 引継ぎ(確定→後続)と再生成耐性
### c-1. 確定(finalize、決定論・API 0)
- 入力=`kp_candidates.json`+`kp_human_review.json`(status∈{REVIEWED, UNREVIEWED_AUTO_ADOPTED})。
- 出力: (1) `keywords_canonicalized.json`=選ばれたKP(`ai_rank`昇順で`rank` 1..n付番。各itemは候補の`item`をそのまま+`candidate_id`/`ai_rank`)。(2) Adv: `vocab_confirmed.json`(`rank` 1..5、`kp`3件を含む。Part 1の入力専用)。(3) `kp_selection_final.json`: `review_status`・選択ID・NG ID・`selection_signature=sha256(text_sha256|candidates_sha256|kp ids|vocab ids|ng ids|status)`・`finalized_at`。
- AUTO規則(決定論): `auto_eligible`かつredundancy pairを持たない候補を`ai_rank`順に走査 → KP=先頭3、vocab=先頭5(Adv)。不足は不足のまま(shortfall、数合わせなし。現行`KP_COUNT_MIN=1`と同じ)。0件は`OUTER_RETRY_EXHAUSTED`(現行と同じSTOP)。
### c-2. 後続への受け渡し(単一アクセサ)
- Part 1の入力取得は新関数`part1_items(kp_dir)`(`vocab_confirmed.json`があればそれ、無ければ従来の`keywords_canonicalized.json`=旧run互換)に一本化する。置換対象の読取点: X `_part1_kp_items`(`er019…runner_01.py:441`)、Z `_kp_items_b1b`(`er026…:1810`)、`er003_kp_general_explanation_01.study_html_for_audio_dir`(`:500-520`、X公開ページ)、Z `stage_pages`/`_assemble_study_rows`。他のKP消費者(TTS・Adv解説`kp_expl_b1b`・gloss gate・SRC gate・Assembly)は`keywords_canonicalized.json`のままで無変更。
- 全消費者の入口で `require_final_consistent(kp_dir)`: (i)`kp_human_review.json`のstatusが前進可、(ii)`selection_signature`再計算が一致、(iii)`keywords_canonicalized.json`のcandidate_id集合=`selection.kp`、(iv)`vocab_confirmed.json`=`selection.vocab`(Adv)、(v)NG交差0。不一致は次コマンド付きSTOP(旧KPが残っても後段が使わない)。呼出点: X=`tts`/`assemble`/`player`入口(`:3177-3195`の既存marker確認と同位置)・scaffold内Part 1前、Z=`load_level_inputs`・`stage_pages`・`stage_page_verify`。
### c-3. retry/fallback/regeneration/resume
| 経路 | 動作 |
|---|---|
| 同一runの再実行(resume) | 候補ファイルの`text_sha256`が一致 → 候補を再利用(**再選定しない・API 0**)。reviewのstatusに応じ、`PENDING_REVIEW`=rc=4待機 / `REVIEWED|AUTO`=finalizeして続行 |
| 外側retry(canon INVALID・CMU NG等) | 候補生成の内部で従来どおり動く。**seed `excluded`にNG集合を入れる**(理由「Human NG」)。確定後は動かない |
| Redundancy NG | 候補段階で`duplicate_pairs`として確定済み。確定後に再選定しない(Human選択は上記b-3で拒否、AUTOはpairを飛ばす) |
| Z `--regenerate-stage kp_<lv>` | status∈{REVIEWED, AUTO}かつsha一致 → **STOP**「Human確定済み。再選定は`reselect`コマンドで」(**従来の黙示的再抽選を止める挙動変更**=運用手順に明記、O-5)。本文shaが変わっていれば`STALE`→候補再生成 |
| X `--scaffold-only kp`(KP再生成1回制限`_kp_already_generated`) | 候補/reviewファイルが有効なら「review再開」経路として許可(`keywords_runtime_metadata.json`等だけの存在で止めない)。確定後の再生成は上と同じ |
| 本文変更(Writer再生成) | `text_sha256`不一致 → `STALE`(旧候補/reviewを`*.SUPERSEDED_n.json`へ退避)。NG registryは**記事ID単位で保持**(本文に同じ句が残っていれば再選定でも除外) |
| 再選定(Human要求) | `reselect --ng …`→`RESELECTION_REQUESTED`→次回起動で候補再生成(NG+既存excludedを`excluded_phrases`へ)。回数上限=`reselect_count≤2/レベル/run`(案。1回の再生成は現行の外側retry枠`KP_OUTER_RETRY_MAX=3`の範囲)。超過はSTOPして報告 |
| 下流の失効 | 確定が変わる(事後Review・reselect)→ Z: `prov.mark_stale_descendants("kp_<lv>")`、X: 既存`er019_family_x_segment_invalidate_01`でKP依存segmentを失効。音声はMaster Audio Storeのphrase単位reuseで差分のみ再生成 |
- **NGの復活防止(多層)**: (1)select/確定validatorで交差拒否 (2)候補再生成時にLLMがNG句を再び返しても`dropped(stage=human_ng)` (3)外側retryのseed excluded (4)`apply_exclusions`(既存) (5)AUTOの走査でNGスキップ (6)`require_final_consistent`で全消費者が再検査。NG判定は`candidate_id`+`phrase_key`+`used_form_key`の3キー(基本形化で表層が変わっても同一視)。
- 署名と既存下流署名の関係: Adv解説`kp_expl_b1b`のsig(used_form+gloss+source)、Part 1の`phrases_signature`(rank昇順の表現)、T1訳は引用英文は、**確定集合が変われば自動で古くなる**(既存機構。Z=STOP→`--regenerate-stage`、X=自動再生成)。新署名はこれに加算(置換でない)。

## d. 一致検証(選定結果=実際に音声化・公開された内容)
- 新関数 `verify_selection_matches_outputs(run_dir)`(決定論・API 0): 確定JSON ↔ (1)`keywords_canonicalized.json` (2)TTS結果(`tts_generation_results.json`のkp component text=`used_form`/gloss/explanation) (3)`study_text/part1.json`の行(vocab 5件) (4)公開ページHTML(KP節・Part 1節の英語表現・意味) (5)Z `pages` manifest。不一致=STOP。
- 組込み: Z=`stage_page_verify`、X=`player`stage末尾+ページ生成script(`er019_nws2_final_page_01.py`)直後の確認、および証跡runner。既存の一致検査(`study_html_for_audio_dir`のsignature/件数/文字列一致=`:511-531`)を**拡張して再利用**(置換ではない)。
- 文法(Part 2)も同関数に`kind`を持つ(§k、Part 2配線時に有効化)。

## e. Family別適用
| Family | 配線点 | 状態 |
|---|---|---|
| X(`er019_family_x_audio_production_runner_01.py`) | `run_theme_scaffold`のKP呼出(`:664`)を `er119.run_kp_with_review(...)`(内部で既存`sc.run_kp_with_outer_retry`を再利用)に差替。両レベルの候補を先に生成→まとめてrc=4で停止(レベル往復を最小化)。Part 1は`part1_items`経由。入口に`require_final_consistent`。CLI: `--kp-review wait|auto`(既定=引数なし=待機) | 実装予定(別委任) |
| Z(`er026_family_z_fiction_production_runner_01.py`) | `stage_kp`の`runner`(`:1693-1722`)内 `w62.run_kp_stage(...)` を差替。b1b/a2両レベルの候補生成後にpendingをまとめて1回raise(Part 1より前)。`_gloss_hr_gate`/`_gloss_person_gate`/`_src_gate`は確定後も従来どおり実行(多層防御) | 実装予定(別委任) |
| Y | 正式入口なし(OPEN-484)。Trial scaffoldは`sc.run_key_phrases`(共有・無変更)を直接呼ぶためHuman Reviewは**効かない**=未配線。OPEN-484へ受入条件(g)「Y正式KP段が`er119.run_kp_with_review`を通る・Y用`part1_items`」を追記して追跡。**PRODUCTION_WIREDとしない** | 追跡のみ |
| A/B/C | 無変更(27-7) | — |

## f. Part 1の件数3→5(単語解説)
- 対象=**Advancedのみ**(承認済みPart 1は非拡張。判断候補I-1)。Std: KP3件のHRのみ。
- 変更点: 入力を`vocab_confirmed.json`(5件)へ。Part 1解説/T1は既に最大5件を受理(`er003_kp_general_explanation_01.py:68`、`er003_kp_source_sentence_ja_01.py:45 MAX_SENTENCES=5`)。X公開ページ(`study_html_for_audio_dir`)・Z pages(`stage_pages`)は件数可変の描画。Adv英語解説(`kp_expl_b1b`、音声)はKP3件のまま。
- 費用(推定、BUDGET_PLAN_01): 解説+T1の入力・出力件数が3→5(+約0.04〜0.08円/set)、候補canonicalization/gloss/Redundancy(3→最大8件)で+約0.5〜1.5円/レベル/set。選定call(出力トークン8件+理由)で+約0.01〜0.03円。**実測は証跡runで差替え**(推定のまま使わない)。時間: 候補Gate+数十秒/レベル、Part 1+数秒。

## g. 簡易運用(本格UIはScope外・将来UIを妨げない)
- 提示: `kp_human_review_request.md`(runが出力)=候補表(AI順位・used_form・本文中の意味・出典文・AI理由・旗[qa_fail/gloss_hr/重複]・推奨[TOP3/TOP5印])+実行コマンド例。将来UIは`kp_candidates.json`/`kp_human_review.json`(スキーマ固定)を読み書きするだけでよい。
- CLI(`er119_kp_human_review_cli_01.py`、決定論・API 0):
  - `status --run <dir>`(全レベルの状態・待機一覧)
  - `show --run <dir> --level b1b`
  - `select --run <dir> --level b1b --kp 1,3,5 --vocab 1,2,3,5,7 [--ng 4:理由] [--accept-qa-fail 6] --by <名前>`(番号=表の`ai_rank`)/ `--accept-ai`(推奨了承)
  - `reselect --run <dir> --level b1b --ng 4,6 [--note …] --by <名前>`
  - `declare-absent --runs <dir>[,<dir>…] --reason … --by …`(不在宣言。明示操作のみ)
  - `--from-json <file>`(JSON編集入力。同一validatorで検証。直接`kp_human_review.json`を手編集すると署名不一致でSTOP)
- 実行環境は既存運用と同じ(コマンドラインのみ)。

## h. 旧ルール整理候補(撤去/改訂/残置)
| 対象 | 扱い |
|---|---|
| `KP_COUNT_MAX=3`(`er105:33`) | 残置(**確定数**の意味)。`KP_CANDIDATE_MAX=8`/`VOCAB_COUNT_MAX=5`を追加。関連assert(`er003_test_kp_fulltext_wiring_01.py:845-851`、`er105…test_01.py:68,267`)は意味を限定して維持 |
| Prompt 2(固定・sha) | X/Zの選定は2-Rへ置換、Prompt 2は旧run互換・A/B/C非関与で残置(撤去は別判断) |
| 「1件でも不適合なら選定attempt全体INVALID」 | 候補段階ではitem単位除外へ改訂(Gate判定基準は不変)。確定後は無関係 |
| Z `--regenerate-stage kp_*`=再抽選 | 確定済みなら`reselect`必須へ(挙動変更・運用手順追記) |
| X `_kp_already_generated`の「1レベル1回」 | review再開を例外許可。確定後再生成禁止は維持 |
| 撤去しない: gloss HR・`REVIEW_REQUIRED`・HR Lock・KP 3-ASR vote・Redundancy QA | 目的が別(§3)。併存 |
旧ルールの残存Grepは実装委任のRESULT_PACKET(4)で実施する(本委任は設計のみ)。

## i. 費用・時間の影響(要約。詳細BUDGET_PLAN_01)
- 追加費用は主に候補canonicalization/gloss/Redundancy(最大8件)。KP段単価は現状約2.2〜2.5円/セット(X)・3.7円(Z失敗retry込み)(`JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md:77-82`)→推定+1〜3円/セット(70円比約1.5〜4%)。品質を守る範囲での最小化案: 候補canonicalizationを`ai_rank`順に必要数+予備のみ(AUTO宣言済みrunは先頭5+予備、Human待ちrunは8)にする遅延方式(切替時に追補が必要=複雑化するためv1は全8件一括を推奨、実測でC改善余地があれば第2段で検討)。
- 時間: Human待ちは新規の待ち時間(有料工程の手前)。不在宣言で解消。

## j. DefaultOffIsolation / Production境界
- 本機能は`APPROVED_FOR_PRODUCTION`済みで**既定ON**(新入口をX/Z正式経路へ配線)。ただし:
  1. `auto`確定は**明示宣言の存在**でのみ起きる。test: 宣言なし→候補生成後に待機、下流API 0・副作用file(`keywords_canonicalized.json`等)0。
  2. `mode`の読取点は`read_mode_declaration()`のみ。test: 環境変数・設定dict・関数既定値・`.env`に`auto`を置いても無効。
  3. 共有関数`sc.run_key_phrases`/Y Trial/A/B/Cは出力不変(既存golden `er109_wiring_golden_test_01.py`等+新test)。
  4. 文法はPart 2採用確認までProduction経路に到達しない(import/配線なし。Grepでassert)。
- 起動script・`.env`で暗黙ONにしない。違反時は11-7の失効規則ではなく**APPROVED_FOR_PRODUCTION仕様の逸脱=不具合(11-8)**として是正する。

## k. 文法(Part 2)の分離構造とHR負担
- 共通核 `er119_kp_human_review_01.py` は `kind`(`"kp"`/`"grammar"`)を持つ汎用の候補・review・署名・NG・遷移を実装。grammar固有は薄い層: `grammar_candidates.json`(≤2、`rank`・クラス・`teaching_value_ja`・出典文・適格根拠)、`grammar_human_review.json`(`choice: top1|top2|reselect|omit`)。AUTO=TOP1(適格のみ。適格0なら**Part 2コーナーなし**=Trial-07の0件規則。ただしProduction承認の根拠はG-1/G-3の確認待ち)。
- **配線の前提(Part 2のProduction配線そのもの)**: Step A''抽出・`eligible7`・`select_tiered`・Step B・Part 2描画・ページ組込みはProductionに存在しない。TOP 2は`select_tiered`の順序の先頭2件(追加LLM callなし、「2位=同一文を除く次の適格」を既定案)。**G-1(Part 2採用の明示承認)が得られるまで文法は実装しない**。得られた後は同じ核+薄い層+Part 2配線を別委任で実装。
- 本委任の構造要件: 核を`kind`非依存に作る / grammarの空実装(層)は作らない(未使用コードをProductionに置かない)、核のunit testだけ`kind="grammar"`の合成fixtureで状態機械を検証する。
- **HR負担見積(推定、未測定)**: 1記事あたりの判断=Std KP(8→3)1回+Adv KP+vocab(8→3+5)1回(+Part 2採用後は文法1回)。1回の判断は表を読み番号を打つ作業で約1〜2分(AI推奨了承`--accept-ai`なら数十秒)。→ 2〜3判断/記事=約3〜6分/記事、**9記事/日で約30〜55分/日**(最大)。軽減策: (1)推奨印+`--accept-ai`、(2)`status`の一覧でまとめて処理、(3)不在宣言で0分、(4)gloss HR/qa_fail旗は該当候補のみ強調して読む対象を絞る。

## 判断を要する点(推測で進めない)
I-1 / I-2 / G-1 / G-2 / G-3 / K-1(EXISTING_SPEC_CHECK_01 §8)。加えて設計パラメータ(Fable了承でOpus前に確定): reselect上限(案2回/レベル/run)、`--accept-ai`をREVIEWED扱いにすること、候補item単位除外(O-3)、`--regenerate-stage kp_*`の挙動変更(O-5)。
