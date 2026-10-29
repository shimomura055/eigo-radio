# Opus独立レビュー(条件A、2026-10-29、逐語。transcript抽出)
## Opus独立レビュー: HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01(条件A)

**結論: 条件付きで実装に進んでよい。** 設計の骨格(仕様①は除外とbackfillで対応、仕様②は判定を残して停止箇所だけ外す、判定器の故障時はfail-closed、旧経路A/B/Cは変更しない)は妥当。ただし、下記のM1〜M9は実装前に設計へ反映してほしい。M3はY記事Stdへの適用手順を直接壊す。

### 必須の修正(M1〜M9)

**M1【異論・論点5】gloss_hr_pendingを据え置くと、選んだ後に差し戻す運用が残る(原文§2-4に反する)**
- フォームでは「仮訳・未確定」の候補も選べる(form_logic.js:107,111。選択の制限はない)。
- 一方、確定時には次の2か所で拒否される。
  - validate_selection(er119_kp_human_review_01.py:557-558)
  - cmd_from_formの`ja_gloss_status != "official"`判定(er128:1492-1493)
- 拒否されるのはgloss_hr_pendingの候補に限らない。exporterの`gloss_status`(export_form_data_01.py:94-105)がofficialにならない候補はすべて拒否される(例: 救済候補でgloss再整合がFAILEDのもの)。
- 修正案: `presentable_candidates`の条件を「提示された候補は単独で確定できる」にそろえる。具体的には `human_selectable ∧ ¬qa_fail ∧ ¬gloss_hr_pending ∧ gloss_status==official` とし、外れた候補はqa_failと同じく除外してbackfillで補う。
- 先に既存の正式P7W5 docでgloss_hr_pendingの発生頻度を確認しておくこと。
- 原文§2-3の「等」にはこれが含まれると読むのが自然。「提示前に人がresolve-glossを行う」案はQCDが重いので推奨しない。

**M2【漏れ】提示集合を定義している箇所が3つ目にある: er134の`presented_pool`(er134_nuance_explanation_01.py:280-289)**
- これはexporterとのparityをtestで固定している。また`pool_identity_sha_of`/`presented_ids_of`(:992-999)を通じて、ニュアンス確定の検証(er128:1739-1746のpool同一性と被覆の照合)に使われている。
- 設計A-1-3が挙げる利用先(render_request_md / exporter / auto_select)にこれが入っていない。exporterだけ絞ると、parity testが壊れ、pool shaもずれる。
- 修正案: presented_poolも`presentable_candidates`を通す(cap判定はその後に行う)。
- 旧docへ遡って適用すると、「ニュアンス仕様マークあり、かつqa_fail候補ありで、まだ確定していないrun」はpool shaが変わりISSUEになる。実装前に該当runを棚卸しする(0件なら遡及してよい)。

**M3【阻害】Y Stdで`old-fashioned`へ差し替えると種類が「単語」に変わり、ユーザーが選んだ「perhaps」が提示集合から落ちる**
- a2の候補docは単語5件で、すでに上限いっぱい: adopted / relative / bothered / thankful / perhaps(ai_rank 7〜11)。
- `old-fashioned`は1語なので、`bf.kind_of_phrase`(er119_kp_backfill_01.py:36-38)で種類が単語になる。
- すると「ai_rank順に単語先頭5件」というcap(exporterとer134:287)により、ai_rank 11の**perhaps(ユーザーが選んだ本文意味)が提示集合から外れる**。readableの復元・確定が成り立たず、原文§6「その他の選定は維持」に反する。
- 取りうる道は3つ。
  - (a) kindを"phrase"のまま残す: R-1の種類規則に反する。
  - (b) このdocだけcapを6にする: 承認済み上限(7+5)の例外になる。
  - (c) フォームを経由しない確定経路を使う: 文法の確定経路を別に用意する必要がある。
- 判断: どれも承認済み規則に触れる。Fableが「上限はAI候補の生成数の上限であり、人間が選んだ集合には適用しない」と解釈できる根拠(SSOT)を確認すること。確認できなければ、ユーザー判断事項として扱う。

**M4【条件付き・論点4】`op_requalify_candidate`はゲートの通し方が不足しており、汎用のopにすると新しい受理面になる**
- 次のゲートをすべて通し直すこと。
  - `kc.validate_canonicalization_item`(全文選定用の引数。左端guardを含む。er003:576-637)
  - `cmu.canonicalized_check`、記号検出、`match_ng`/`ng_match_originals`
  - `ft._recompute_item_fields`、word_count、kindとcap(M3)
  - `force_gloss_realign`(承認済みのgloss規則。er125:468)
  - `qa_rejudge`の12項目すべてPASS(er125:503)
  - 候補単位の`redundant_with`の再計算、またはrank5の旗が古いままであることの明記
- 「本文に連続して一致するか+QA+gloss」だけでは、承認済みゲートを迂回したことになる。
- 汎用のCLI/本番opにすると「人が任意に正規形を指定する」という未承認の機能になる。修正案: このrun・このcandidate_id・`old-fashioned`だけに限定した使い捨てtoolにする。中身はProduction関数を再利用し、review_lockとsha更新もそこで行う。決定はDECISION_LOGへ「ユーザー原文§2の機械的転記」として記録する。
- 確定レコードについて:
  - cmd_from_formが固定で書く`attestation="form_submit"`(er128:1524)は事実と異なる。「ユーザー指示の転記」であることと、由来(旧readableのsha、旧d6→新d6、差分はrank5のtermだけ)を記録する引数を追加すること。
  - actorはACTOR_USERとする。EVIDENCE_RUNは誤り。
  - `_form_source_problems`(:543-552)と整合させるため、payloadの原本は保存すること。
- これらを満たせば、残りの検証(op_select / 文法 / ニュアンス / term・glossがofficialか)はすべて通るので、迂回には当たらない。

**M5【実装上のバグの予兆】設計B-2 #5の「`_run_final_qa`の中でNGをALARMへ改名する」はAUTO分岐を壊す**
- AUTO分岐は`status=="REDUNDANCY_PASS"`と`fq["ng_pairs"]`を使っている(er119_kp_human_review_01.py:1019,1023)。
- 修正案:
  - `_run_final_qa`は変更しない(判定値はNG/PASSのまま)。
  - 人間選定の分岐(:1034-1043)でだけ`final_qa`をALARM形に変換して保存する。
  - キャッシュ条件(:1013)は「keyが一致し、かつ(statusがPASS、またはstatusがALARMでreviewがAUTOでない)」とする。
- これでALARM確定後のresumeや`_try_refinalize`(er128:2251、redundancy_fn=None)は有料API 0回で通る。

**M6【漏れ】本文意味(③ meaning_display)がアラームの対象外になっている**
- `review.selection`に入るのはkpとvocab(=①+②)だけ(er128:1501-1502)。③は`unconsumed`に入る。
- このため、ユーザー原文§3に例として挙がっている`give something up`(③)が、op_selectの時点の`redundancy_alarms`にも確定集合QAにも出てこない。
- 修正案:
  - `redundancy_alarms`は確定レコードのitems+unconsumed(③)を対象にし、候補docのduplicate_pairsから計算する(API 0)。
  - 計算する場所はcmd_from_form(groupsがある)とfinalizeにする。
  - 確定集合QA(kp/vocab)は今のまま。

**M7【漏れ・Dangling】RECONFIRM状態と、それによる停止**
- `on_final_redundancy_ng`を撤去すると、`STATE_RECONFIRM`を作る箇所がなくなる。
- それでも消費側には次が残る。
  - 消費者入口G1のISSUE停止(er128:579-582)
  - 状態の分岐(:682)とコメント(:80,:279)
- 新しいdataでは到達しないが、既存レコードを読むために残すか撤去するかを決め、ディスク上に`reconfirm_required`のレコードが0件であることを確認すること(私のGrepはタイムアウトして未確認)。
- `ensure_kp_review`のfinalize時の`except KpReviewPending`(:1466-1470)は、finalize側から送出されなくなるので死にコードになる。撤去するか、意図して残すと明記するか決めること。
- Danglingの照合リストに`STATE_RECONFIRM`、`reconfirm_required`、`raise_issue_nowait`を追加すること。

**M8【条件・論点2関連】救済候補で、検査未了またはgloss失敗のもの**
- 救済候補でQA再判定が`NOT_REJUDGED`のものは、`qa_overall_status`が救済前のkeyに対する値のまま残る(er125:572-574)。そのため設計A-1の判定(REVIEW_REQUIREDなら除外)をすり抜け、救済後のkeyについては検査していない候補が提示される。
- これはB-4の「未検査の候補は提示しない」と矛盾する。
- 修正案: `rescue.canonicalization`があり、かつ`rescue.qa.status != PASS`または`rescue.gloss.status != REALIGNED`の候補は除外する(fail-closed)。
- 救済の承認済み仕様は「人間だけが採用可」としていたので、仕様①による置換である旨をSSOTに追記すること。

**M9【条件】「qa_overall_statusが欠落していたら除外する」fail-closedの前提確認**
- 正式な生成経路(通常・救済・backfill)では必ず値が入っていることを、直近の正式docの棚卸しで確認すること。入っていない経路があると候補が大量に除外される。

### 設計D節の8論点
1. **INVALIDをfail-closedのまま残す: 同意。** これは判定器の故障であり、「重複アラーム」ではない(原文§3-5の既存の安全条件)。条件: 停止メッセージに「重複判定ではなく判定器の故障」と明示すること。resumeで再試行できること(キャッシュされない)をtestで固定すること。
2. **backfillとの連携・候補不足: 同意。** `bf.rejected_entries(excluded, dropped)`(er119_kp_candidates_01.py:567)を通じて、除外した句がbackfillの除外入力に入るので、同じ句が再び選ばれることはない。KPの最小数は1(SLOT_RULES:64)なので、候補が不足しても人間は選べる。U2で「除外した句がbackfillの除外入力に入っていること」をassertすること。
3. **旧docへの遡及: 条件付き同意。** M2の棚卸しが条件。
4. **`--accept-qa-fail`を残す: 同意。** 撤去時期を決める判断材料(旧docのrun数)をOPEN_ITEMSへ記録すること。
5. **gloss_hr_pending: 異論。** M1のとおり。
6. **AUTOの重複回避を維持: 条件付き同意。** 原文§3-1の対象は「人間が選んだ表現」なので、AUTOは範囲外と読める。ただし、AUTOで候補が尽きたときのSTOP(:1029,:1031)は、重複だけを理由にした停止として残る。SSOTに「範囲外として意図的に残す既存動作」と明記し、残課題として報告すること。
7. **案β(再canonical化)を別承認にする: 同意。** Promptへの入力を変えるので新しい仕様にあたる。
8. **アラームの掲載範囲: 同意。** user_testの事後確認節+runnerの完了報告+run監査に載せ、一般公開ページには出さない。加えて、confirmのCLI出力にもアラームを出すこと(Fableが完了報告へ転記できるように)。

### 停止箇所の洗い出し(観点2)
- 撤去対象の3か所は妥当: validate_selectionのpair検査(実際の行は:564-567)、finalizeでのPENDINGへの巻戻し(実際は:1034-1042)、`on_final_redundancy_ng`。
- 漏れはM7の2点(G1の:579と、ensure_kp_reviewのexcept)。
- runner側に停止がないことは確認した。`_shape_final`はcanonicalizationをPASS固定で返し、statusを`final_qa`から決めていない(er119_kp_wiring_01.py:43-56)。Xの`kp_stage_failure_status`(er019:487)は`final_qa`を見ていない。`REDUNDANCY_NG`を分岐条件にしているのは旧A/B/C系とTrial系のscriptだけ。
- キャッシュの副作用はM5のとおり。

### 失敗したときの最終状態(観点5)
- QA検査の例外→FAILED/OUTER_RETRY、アラームの派生ファイル書込み失敗→確定を続行、resume→API 0回: いずれも目的要件を満たす。
- 再選定でアラームを引き継がないことも妥当。
- 未定義の箇所が1つある。REBOUND(本文変更で再バインド)のとき、キャッシュkeyは選定IDだけでcandidates_shaを含まない。itemの文面が変わってもアラームが再利用される。既存の挙動と同じなので許容してよいが、明記すること。

### test計画(観点7)に追加すべきもの
- 提示可能な全候補について、各候補を単独で選んだときにvalidate_selectionとcmd_from_formの候補単位の検査を通ること(原文§2-4の性質test。M1の証明になる)。
- er134の`presented_pool`/`pool_identity_sha_of`と`presentable_candidates`のparity(M2)。
- AUTO分岐での`_run_final_qa`の意味が変わっていないこと、ALARMがAUTOではキャッシュされないこと(M5)。
- ③本文意味を含むアラーム(Y Advの3表現を再現するfixture、M6)。
- 差替えtool: kind/cap、全ゲート、Std a2のcap衝突の再現(M3、M4)。
- 救済候補のNOT_REJUDGEDとgloss FAILEDの除外(M8)。
- 既存レコードがRECONFIRMのときの扱い(M7)。
- I1は`candidate_doc_from_items`(er119_kp_candidates_01.py:667。test専用で`_gate_chain`を通らない)ではなく、canon_fnをmockして`_gate_chain`を実際に通すこと。

**runtime evidenceの「発火証拠」について**
- R1(保存済みのqaを再判定するだけ)は、仕様①の発火証拠にならない。
- 候補を生成するたびにtelemetryを出すこと: QA検査した件数、`canonicalization_qa`で除外した件数、提示可能な件数、`presentable_filter`の版。0件でも記録する。
- finalizeについても同様に、`final_qa`のstatus、アラーム件数、`nonblocking=true`、到達した後続stageを記録すること。
- そのうえで、X/Y/Z×Std/Advの6組合せそれぞれについて、正式経路で実際に候補を生成した記録を1件以上得ること。copy-runの場合はテキストを固定し、実LLMで生成する。費用見積は別途必要。これがユーザー原文§4と§7-2を満たす最低限。
- 重複が実際に発生する分岐(ALARMの分岐)は、Y Advの実記事と、X/Zのmockで代替してよい。

### 実装に進む条件
1. M1: 提示集合を「単独で確定できる」にそろえる。gloss_hr_pendingとofficialでない訳を含める。
2. M2: er134の`presented_pool`を同じ関数で通し、影響runを棚卸しする。
3. M3: Y Stdのcap衝突の解決方針を確定する(解決できなければユーザー判断)。Y Stdの適用はこれが決まってから行う。Advは①②の実装後すぐに進めてよい。
4. M4: 差替えはこの記事限定の使い捨てtoolにし、全ゲートを再適用し、attestationを正しく記録する。
5. M5: `_run_final_qa`は変更しない。人間選定の分岐でだけALARMに変換する。キャッシュ条件はAUTOを除外する。
6. M6: アラームの対象に③本文意味を含める。
7. M7: RECONFIRM、G1:579、`except KpReviewPending`の扱いを決め、Dangling照合リストに追加する。
8. M8とM9: 救済で未検査の候補の除外と、qa_overall_status欠落の棚卸し。
9. 上記に対応するtestを追加し、telemetryベースのruntime evidenceの定義をTEST_PLANに反映する。

### 参照ファイル
- C:\Users\tensh\eigo-radio\er119_kp_human_review_01.py
- C:\Users\tensh\eigo-radio\er119_kp_candidates_01.py
- C:\Users\tensh\eigo-radio\er128_kp_confirmed_content_01.py
- C:\Users\tensh\eigo-radio\er134_nuance_explanation_01.py
- C:\Users\tensh\eigo-radio\er125_kp_rescue_production_01.py
- C:\Users\tensh\eigo-radio\er119_kp_wiring_01.py
- C:\Users\tensh\eigo-radio\docs\research\KP-GATE-DROP-BACKFILL-PRODUCTION-01\tools\export_form_data_01.py
- C:\Users\tensh\eigo-radio\er121_output\family_y_production_01\surname_choice\run_02\key_phrases\a2\kp_candidates.json
- C:\Users\tensh\eigo-radio\er121_output\family_y_production_01\surname_choice\run_02\hr\readable_a2.txt
