# PART1_WIRING_EVIDENCE_02(Part 1 T1 翻訳工程 runtime evidence・X公開ページ共通builder)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16 / 日付: 2026-10-25 / Status: Z=`WIRED_PENDING_FABLE`(T1込み) / X=`WIRED_PENDING_FABLE`(公開ページ共通builder込み)。PRODUCTION_WIREDはFable受入後。
生ファイル=`part1_wiring_evidence_02/`。前回evidence=`PART1_WIRING_EVIDENCE_01.md`(解説の発火・実測)。T1正確性確認=`PART1_T1_CHECK_01.md`。

## 0. 実行条件・費用
| 項目 | 値 |
|---|---|
| 実費合計 | 約0.66円(T1確認3call 0.0923+ばらつき確認6call 0.171+Z evidence 2run[`_02`0.1507・`_03`0.1391]+X evidence 0.1034)。委任上限15円。再起動0 |
| STOP確認 | 各run-dir前に`tools/stop_scope_check_01.py --managed-id FAMILY-Z-STUDY-TEXT-TRIAL-01`=rc0・stop=false(Z `_02`/`_03`、X `out_run_ev_02`) |
| model | **gpt-6-luna**(最新世代の推奨系=`routing.SUPPORT_MODEL`。旧/下位モデルの使用なし) |
| 実測(1 setの解説+訳) | Z=0.1391円(解説0.0999+訳0.0392)、X=0.1034円(解説0.0728+訳0.0306)。**訳の追加原価=0.031〜0.039円/set**(承認約0.03円と同水準)。70円比0.15〜0.20%。時間: 訳 約3.8〜4.3秒/call(解説8.8〜11.9秒に加算) |

## 1. Z — 複製run(元=告げ口心臓`run_sf_prod_02`、音声・pages含む155MBをコピーしcost_log/launch_log削除)
- `run_p1_evidence_02`: (a)`--stage pages`(Part 1導入前の状態)→**M2でSTOP**(`FAMILY_Z_KP_PART1_NOT_READY: KP_PART1_EXPLANATIONS_MISSING…次の一手: --stage kp --regenerate-stage kp_part1_b1b`、rc=2、`Z_m2_pages_before_stdout.txt`)。(b)`--stage kp`→`kp_part1_b1b`(解説1 call)と`kp_part1_ja_b1b`(**訳1 call**、stage=`kp_part1_ja`)が発火、費用0.1507円(`Z_kp_stdout.txt`)。(c)続けて`--stage pages`を単独起動→**自分で作った複製runが3回目の起動で`FAMILY_Z_RESTART_STORM`を自行発動**し`STOP`を自動作成(複製のみ。解除/削除はしていない=`run_p1_evidence_02/STOP`が残置)。→以後`run_p1_evidence_03`で`--stages kp,pages`を**1起動**で実施。
- `run_p1_evidence_03`(`--stages kp,pages`、1起動、`Z_kp_pages_stdout.txt`): `kp`で解説1 call(0.0999)+訳1 call(0.0392)=0.1391円、続く`pages`でstudy block描画(判断記録`T1`あり)。生成物: `Z_kp_source_sentence_ja.json`(audit: model=gpt-6-luna、process=`KEY_PHRASE_SOURCE_SENTENCE_JA`、prompt_template_sha256=`98b1871c…`、prompt_sha256=`b87f8e0b…`、input_sha256=`1dc0d6ab…`[引用英文3文のみ]、retried_for_parse=false、response_id=`resp_0911c04b…`)、`Z_provenance.json`の`downstream_stages.kp_part1_ja_b1b`、`Z_part1_vocabulary_expressions.{md,json}`(5項全文)。
- **注意(Fable確認): 複製runの`--stage pages`はrunner既定の公開pages_dir(`user_test/family_z_tell_tale_heart_01`)へ書く**。実行後に`index.html`が差し替わっていたため、`git checkout --`で**直ちに復元**した(復元後の`git diff HEAD -- user_test/family_z_tell_tale_heart_01`=空、commit・push前、公開側への反映0。advanced.html/standard.htmlは内容同一)。差し替え時の内容は`Z_index_NOT_PUBLISHED.html`に退避。複製runで`pages`を回す場合は`E2EContext.pages_dir`の分離が必要(今後の手順メモ=OPEN-512)。

### 1-1 Z出力(5項、全文は`Z_part1_vocabulary_expressions.md`)
| 英語表現 | 本文中の意味 | 本文引用英文 | 日本語訳(T1) |
|---|---|---|---|
| sharpen someone's senses | 人の感覚を研ぎ澄ます | My illness sharpened my senses, especially my hearing | 病気になって感覚が鋭くなり、とりわけ聴覚が研ぎ澄まされた。 |
| cloudy film | 濁った膜 | Pale blue, covered by a cloudy film—a vulture's eye | 淡い青色で、曇った膜に覆われた――ハゲワシの目。 |
| never stir | まったく身じろぎしない | I eased the door open so slowly he never stirred, then let one thin ray escape my lantern | 彼が身じろぎひとつしないほどゆっくりとドアを開け、続いてランタンから細い一筋の光を漏らした。 |
解説は各表現の一般的な解説(核の意味→用法→類義)。入力は表現のみ。
観察: 訳「曇った膜」とglossの「濁った膜」は表現が揺れる(訳は引用英文のみから作るため。意味は同一)。

### 1-2 描画HTML(`Z_index_NOT_PUBLISHED.html`の`<section class='study'>`)
`<h3>Vocabulary &amp; Expressions</h3>` + 表現ごとの`<div class='study-item'><h4>表現</h4><dl><dt>本文中の意味</dt><dt>本文の英文</dt><dt>日本語訳</dt><dt>解説</dt></dl></div>`×3。table/h2不使用、禁止パターン(A2/B1/English:等)0、Standard側には出ない(test)。

## 2. X — 複製(source=`er019_output/ig_nobel_2026/run_nws_02`、audio出力=`family_x_audio_production_wiring_01/ig_nobel_2026__run_nws_02`[音声・assembled含む164MB]を`er019_output/p1t1_ev/`へコピー、`--slug p1t1_ev --run run_ev_02 --out-dir …/out_run_ev_02 --level b1b`)
- `--stage player`(Part 1導入前)→**M2でSTOP**(`KP_PART1_NOT_READY…次の一手: --stage study_text`、rc=3、`X_m2_player_before_stdout.txt`)。
- `--stage study_text`(`X_study_text_stdout.txt`): 解説1 call(0.0728円)+**訳1 call(0.0306円)**、reuse=false、retry 0、`kp_part1_ja`のstageタグ(`X_raw_usage_log.jsonl`)。`X_kp_source_sentence_ja.json`(prompt_sha256=`51b3ad08…`、input_sha256=`593977b2…`=引用英文3文のみ、response_id=`resp_0204c702…`)。
- `--stage player`(`X_player_stdout.txt`、rc=0)。
- **公開ページ共通builder経由のページ生成**(`er019_nws2_final_page_01.py --audio-dir … --out er019_output/p1t1_ev/page_out`、非公開dir、API 0、`X_page_stdout.txt`): `<section class='study'>`がAdvanced節の`</details>`直後に1つだけ入り、Standard節には無し、table/h2不使用、禁止パターン0(`X_page_study_fragment.html`)。builder=`er003_kp_general_explanation_01.study_html_for_audio_dir()`、script側の追加は`import`+1呼出+`tail=study_html`の1引数のみ。既存の見た目・構造(タブ・再生UI・表・PASS_WITH_WARNING一覧)は不変。

### 2-1 X出力(5項、全文は`X_part1_vocabulary_expressions.md`)
| 英語表現 | 本文中の意味 | 引用英文 | T1訳 |
|---|---|---|---|
| nutrient-rich crystals | 栄養豊富な結晶 | The Ig Nobel Prize went to research on nutrient-rich crystals that had been published earlier | 栄養豊富な結晶に関する、以前に発表されていた研究にイグ・ノーベル賞が贈られました。 |
| bound to the protein | タンパク質に結びついた | Fats were bound to the protein, and sugars were attached too | 脂肪はタンパク質に結合しており、糖も付着していました。 |
| leap into action | すぐに行動を起こす | At this point, the marketing team might be ready to leap into action, but hold on | この時点で、マーケティングチームはすぐに行動を起こそうとしているかもしれませんが、ちょっと待ってください。 |

## 3. test(自動)
- `er003_kp_source_sentence_ja_01_test_01.py` 53 PASS: Prompt sha固定・入力隔離(gloss/解説/KP文脈が混入すればViolation)・本文逐語照合(課金前STOP)・構造検査(件数/ID/空/英語残り/かな無し/禁止パターン/改行)・技術retry1回→fail-closed・model不一致即STOP・signature(引用英文+Prompt sha+modelのみ、gloss/KP表現で再生成しない)・resume・最新性・解説工程との独立・X公開ページbuilderのfail-closed7種・routing。
- `er003_kp_general_explanation_01_runner_integration_test_01.py` 27 PASS(T1追加分: Z `kp_part1_ja_b1b`別stage・5項描画・訳欠落/不一致でTTS/pagesSTOP[次コマンド付き]・訳失敗時も解説無傷で訳だけ明示再生成・訳入力は引用英文のみ / X 訳の生成・保存・自動再生成の挙動)。
- 回帰結果は`REGRESSION_02.md`。

## 4. 失敗系・既存retry/fallback整合
- 訳callの失敗=技術retry1回→なお構造NGで`KP_PART1_JA_FAILED`(X: `kp_part1_failed.json`+rc=3、Z: `FAMILY_Z_KP_PART1_JA_NOT_OK`でTTS前STOP)。fallback model・空欄続行・旧方式なし。既存の解説retry/Gate/STOP規約に変更なし(解説のsignature・Prompt shaも不変=test固定)。
- 再生成キー: Z=`kp_part1_ja_b1b`(provenance entry・`--regenerate-stage kp_part1_ja_b1b`)、X=自動再生成(引用英文変更時のみ)。
