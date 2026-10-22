FABLE-DELEGATION-MARKER: KPFT-委任_02-20261022

管理ID: KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_02(OPEN-454)。Opus条件Aレビュー結果の反映→Family X/Z Production配線→旧経路撤去→回帰→SSOT。**本日(2026-10-22 JST)は有料API呼出0円で進め、runtime evidence(有料)は実施しない**(本日の開発費残が不足。runtime evidenceは翌日10-23の別委任で行う)。

## 0. 最初に読む
- `docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET_KPFT1.md`
- ユーザー原文(逐語): `docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md`
- 委任_01成果: `docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/{INVESTIGATION_01,LEVEL_SPEC_CHECK_01,IMPLEMENTATION_DESIGN_01}.md`、`er105_kp_fulltext_selector_01.py`(+test)
- `.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 8節(並列・共有ファイル手順)・26節・27-7

## 1. 先行処理(コード変更前)
1-1. T-0保存: 本委任promptを `docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_委任_02.md` へ逐語保存。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`。Nは末尾から探索し、本文先頭の `FABLE-DELEGATION-MARKER: KPFT-委任_02-20261022` 一致で確定(直近index≈290前後)。
1-2. ユーザー追加指示の逐語保存: ユーザーは本件に対し「### 追加指示：Prompt 2のProduction適用時の調整について」という見出しの追加指示(Prompt 2の微調整=レベル別条件・入出力形式・既存工程接続は、基本条件5点維持・一般化は後段のみ・各レベル品質維持の範囲で自律実施可。範囲超はユーザー承認。実際に行ったPrompt変更は変更内容・理由・既存仕様との対応を最終報告で明示。都度承認不要でPRODUCTION_WIREDまで)を出している。`_USER.md` に既に含まれているか確認し、含まれていなければ同jsonlのrole=userメッセージからその見出しで始まる本文を逐語抽出して `docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_PROMPT-ADJUST_USER.md` に保存(抽出ツールがrole=userに対応しない場合はjsonlを直接json解析して保存。要約・改変禁止。文字数とsha256を報告)。
1-3. Opusレビューの保存: 下記§6のOpusレビュー全文を `docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md` へ逐語保存(冒頭にFable判定§2を付記)。
1-4. `docs/pm/OPUS_FINDINGS_LEDGER.md` に OF-KPFT-P-01〜P-14 を登録(既存書式に従う。処置列はFable決定§2のとおり)。

## 2. Fable(PM)決定(Opusレビューの採否)
- 総合: **条件付きGOを採用。must-fix P-01〜P-06は配線前に必須。recommended P-07〜P-10, P-12, P-14は配線時に実施。P-11はOpus案を採用(下記)。P-13はFable決定済み(下記)。ユーザー判断事項なし。**
- **P-11(撤去順序)**: Sonnet設計の「commit 2=Gate 3後」を変更し、**旧経路撤去commitをruntime evidenceの前に行う**(evidenceが最終コードを検証するため)。rollbackは`git revert`で足りる。ただし撤去前に全回帰PASSを確認。
- **P-12(KP3Vとの順序)**: KPFT側のtestは判定フィールド名(`kp_dual_check`/`kp_vote_check`)に依存させない。順序依存は無いが、同一ファイル(`er019`、`er063`、`er026`)はPNAP/KP3V agentが並行編集中。共有ファイル手順厳守: 編集直前に`git status`→該当行を再Grep→自分の行だけ編集→ファイル単位で即`git add <file>`+commit(index.lockは30s待ち再試行)。他agentの未commit差分を混ぜない。
- **P-13(旧template:15「数値を補わないと意味が成立しない句・glossは選ばない」)**: Fable照合の結果、**CURRENT_SPEC:470-472「(2) 数値placeholder型の回避」として承認済みProduction品質条件**である。Prompt 2は逐語固定で変更しない。代わりに (i) gloss生成の規則抽出対象に旧template:15を含める、(ii) 選定後の決定論precheckとして「数値・％・placeholder記号(～,…,〜等)を含む、または数値を補わないと成立しない形のspan」を拒否しretry noteに理由を載せる、の2点で維持する。既存placeholder gateは現状維持。
- **3点の開示(質問ではなく事実としてCloseout/SSOTに記録)**: X/ZでTopic枠(4+1)廃止/原形化から語順整理が外れ範囲縮小/X/ZのRule7に基本形化例外(人称一般化と同型)。
- **単価見積**: Opus指摘どおり「-4.8円/セット」は過大。SSOT/報告は「推定-1.5〜-3.5円/セット、runtime evidenceのraw_usage_log stage別集計で置換」とする。
- **レベル整合**: Sonnet判定(案ア=Prompt 2を両レベル逐語適用、UDR不要)をOpusが支持。採用。runtime evidenceでStandardの3件を並べて示す(10-23委任)。

## 3. 実装(費用0)
3-1. must-fix: P-01(merge引継ぎ+統合test)、P-02(fulltext専用schema/enum、`_qa_field_effective_verdict`、連続範囲+基本形化の受理、同時発生の受理)、P-03(Adv解説の対象=`used_form`、Z解説sigも)、P-04(validator誤受理防止: 位置制約・除外表・不規則表)、P-05(legacy `--stage keyphrase`撤去=明示エラー)、P-06(`selection_resolution_method`改名)。
3-2. recommended: P-07(2回目選定に機械診断note後置、技術失敗時sleep、選定INVALIDも外側retry予算に含める)、P-08(X外側retryは入れ子にしない構造・Zと共有化・各周STOPセンチネル確認・Z側コメント更新)、P-09(`_merge_checkpoint`刈り込みはreuse_key不一致で、`only_clips`経路のkey照合追加、残存kp4/kp5 wavの扱いを決めて記録)、P-10(schema 400は即停止、attempt生出力保存、文境界不一致の理由区別)、P-14(`kp_backend_used`を完成報告に表示)。
3-3. 配線: `sc.run_key_phrase_selection`に`fulltext_p2` backend追加、X既定値切替(`er019`)、Z `stage_kp`(`er026`/`er062`)切替、設計§のC/R/D/V 29箇所の処置、A/B/C(`kp_backend`既定)出力バイト同一test、1・2・3件fixture test、Dangling Reference Grep。Prompt 2本文は一字も変えない(sha `a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a` 固定のassert維持)。
3-4. 撤去commit(P-11): 旧DB Hybrid/M2P0、Strategy L fallback、m2_fallback報告、cap判定、旧test(設計§7一覧)。残置は旧selection template(gloss規則抽出元)、`build_sentence_units`、A/B/C旧経路(27-7)。
3-5. 回帰: `run_project_regression.py` 全件PASS、新規test `-W error`。secret_scan `--staged` hits=0。commitはファイル単位・意味単位で複数回に分け、`git push origin HEAD:main`。`git add -A/-u/-f`禁止。
3-6. 禁止: 有料API呼出(本日0円厳守)、PNAP/KP3V agentのprocess停止・待機、STOP/HR Lock迂回、他agentの未commit差分のcommit。

## 4. SSOT(コード完了後)
- `CURRENT_SPEC.md`: 該当行(委任_01 RESULT_PACKET §10文案)を更新。3件化、Prompt 2 sha、Rule7のX/Z例外、Topic枠廃止(X/Z)、語順整理の縮小、gloss kill switch=X/Zでは実質停止スイッチ、`qa_listening_blocker_value_preserved`の読み替え、cap撤去、legacy撤去、P-13維持方法。A/B/Cへの影響なしを明記。
- `DECISION_LOG.md`: 採用決定(ユーザー承認2026-10-22、Opus条件A、Fable決定)。
- `OPEN_ITEMS.md` OPEN-454: Status=`WIRED_CODE_PENDING_RUNTIME_EVIDENCE`(**PRODUCTION_WIREDとは書かない**。runtime evidence未取得)。
- `docs/pm/REPORT_LEDGER.md` 1行。`ACTIVE_TASK.md`固定ヘッダ更新、`docs/pm/RESULT_PACKET_KPFT2.md`に報告(4行=既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去・残置、判定整合行)。

## 5. 報告に含めること
- must-fix 6件の対応箇所(file:行)とtest名、recommended各件の対応/未対応理由
- Prompt 2に対する「入出力形式」調整の実内容(構造化schema、本文区切り、note後置等)と「本文無変更」の証拠(sha assert)
- 5件前提29箇所の処置結果と残存Grep(`5件|five|x5|5 Key Phrases|PRODUCTION_ITEM_COUNT`等、X/Z到達経路で0件)
- 旧経路撤去一覧と残置理由
- 回帰結果、commit hash列、raw URL
- 10-23 runtime evidence委任への引継ぎ(X: coffee_prices新run dir、Z: melos新run dir、見積、STOPセンチネル確認手順、合同evidenceでKP3V/PNAPの発火記録も同時収集する案)
- 失敗終了時は「目的の基本要件を欠く成果物を残さない」(配線途中なら既定値を旧経路に戻してcommitし、状態を明記)

## 6. Opusレビュー全文(逐語。1-3で保存)
---
KPFT-OPUS-COND-A-REVIEW-20261022 / KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01(OPEN-454) Opus独立技術レビュー(条件A)。読み取りのみで、ファイル編集・テスト実行・API呼出はしていない。

## 1. 総合判定: 条件付きGO(must-fix 6件)

方針そのもの(選定段だけ`er105`に置き換え、後段は既存を再利用、旧経路は撤去)は妥当。ただし、コードを突き合わせたところ、設計書にもテストにも出ていない配線上の欠陥が3件見つかった(OF-KPFT-P-01・P-03・P-06)。どれも、このまま配線するとStd/Advの品質に実害が出る。

## 2. 各論点の判定

**Q1 原形化validator → 条件付きGO(P-02・P-04が条件)**
- Rule7の目的は「source_spanに無い辞書形を勝手に作らない」。旧経路では選定Prompt(`b1_p2_keywords_l_prompt_template.txt:7`)が基本形化を担い、Rule7は「display_phraseと同じなら安全」として間接的にそれを守っていた。
- 基本形化の担い手を後段に移し、閉じた語形変化の対応表だけで判定する決定論validatorで縛るのは、最小限の内部調整と言える。ユーザーの「原形化工程を維持」「一般化は後段のみ」とも整合する。
- 代替案(Prompt 2に基本形で出力させる)はNO。基本条件1の「本文に連続して出現する表現を逐語で」に反する。
- 旧方式より範囲は狭くなる。語順の整理(例: took off players → take a player off)はできない。これは品質基準の変更ではなく安全側への縮小なので、Closeoutで開示すれば足りる。
- CURRENT_SPECには「X/Z限定のRule7例外(人称一般化と同じ型)」として記録すること。

**Q2 先頭出現の採用 → GO(P-01・P-06が前提)**
- D1の目的は、LLMが自由に書いた出典文を推測で補完しないこと。本件の語句は機械照合で確定済みなので、状況が違う。
- D1 gateはそのまま残り、`source_sentence`が文単位の全文なので`exact`で通る(`er026_family_z_src_posthoc_01.py:49-51`で確認)。D1を骨抜きにはしない。
- 残るリスクは、同じ文が本文に2回出る場合だけ。このときD1は曖昧と判定してSTOPする。fail-closedなので許容できる。

**Q3 構造化出力 → GO**
- Prompt本文は1字も変わらず、送信直前のassertもある。出力形式の調整はユーザー委任の範囲内。
- 注意点は1つ。strictモードのschemaで`minItems`/`maxItems`が受け付けられない場合、2回とも技術失敗になってstageが止まる。対策はOF-KPFT-P-10。

**Q4 有限助動詞のprecheck → GO(OF-KPFT-P-07を推奨)**
- ルールを変えずにprecheckで弾く方式は妥当。
- ただし、同じmessageでの再試行は効率が悪い。保存データから見積もると、語句ごとの不適合率は約4.3%(本文不一致1/70+有限助動詞2/70)。1レベル1回あたり約12%が不適合になる。
- Zは選定失敗を外側retryしないので、記事単位で約3%がstage停止になる見込み。

**Q5 fallback撤去(Luna失敗時はfail-closed) → GO**
- ユーザーがLunaを固定しており、旧Strategy Lは5件・4+1構成なので、代わりのfallback先は存在しない。
- 技術失敗時に待ち時間なしで即再試行している点は直したほうがよい(OF-KPFT-P-07)。canonicalizationには`sleep_fn(2)`がある。

**Q6 gloss生成の拡張 → 条件付きGO(P-01が必須)**
- `align_glosses`が対象にするのは`merge_canonicalization_result`の出力。一方、merge時に引き継がれるフィールドは`er003_key_words_canonicalization.py:770-771`の固定タプルだけで、`fulltext_source_ref`はそこに無い。
- このため、設計どおりの対象選定(`it.get("fulltext_source_ref") and not it.get("japanese_gloss")`)も、消費側STOPも一度も発火しない。結果としてStdの日本語意味もAdv解説への入力glossも空のまま後段へ進む。
- Sonnetのテスト(`er105_..._test_01.py:169-182`)はmerge後のマーカー保持を確認していない。
- 補足: kill switch(`EIGO_KP_GLOSS_ALIGNMENT=0`)をOFFにすると、X/Zは実質的に停止スイッチになる。SSOTに明記すること。

**Q7 fulltext版template → GO(条件付き)**
- template側に次の3点を入れること。
  1. `lemma_normalization`の範囲: 動詞の原形化と、自然な場合の複数→単数のみ。語順の変更はしない。
  2. 時制・単複を基本形にすることは、`qa_meaning_or_usage_unchanged`のFAIL理由にしない。
  3. `qa_listening_blocker_value_preserved`は「学習価値を保っているか」と読み替える。この読み替えをSSOTに記録する。

**Q8 Xにも外側retryを新設 → GO(OF-KPFT-P-08を推奨)**
- Zはカウンタを入れ子にしていない。canonicalization失敗3回とRedundancy NG 2回を別々に数えるので、最大5周で終わる。
- Xを`_run_key_phrases_impl`の中で入れ子に実装すると最大9周になり、Zと挙動がずれる。

**F1 レベル整合 → Sonnetの論理は正しい。実質的な衝突は無い**
- 旧選定Promptは冒頭が「以下のB1英語記事本文から…」で、A2にもそのまま使われていた。Standard専用の選定基準は存在しない(CURRENT_SPEC:596でも確認)。
- 承認済みのStandard品質基準を個別に照合した結果:
  - 本文レベル(:839の6,000語ライン): 本文は変わらない。そこには「KP側で学習補助」とあり、Prompt 2で本文中の難しめの表現が選ばれるのはこの方針と矛盾しない。
  - gloss規則: 実行時に旧templateから抽出して再利用するので変わらない。
  - 再生順序(Std=英→日本語意味→英): 変わらない。
- 残る懸念は経験的なもの(「易しい表現の除外」でStandardの件数が足りなくなる可能性)。保存データでは0/7単位だった。runtime evidenceでStdの3件を並べて示せば十分。USER_DECISION_REQUIREDは不要。

**F2 4+1(Topic枠) → 再質問なしで進めてよい**
- 4+1は「5枠」の内訳そのものなので、5件前提に含まれる。Prompt 2は逐語固定でrole出力が無いため、残す手段も無い。
- Topic枠をPrompt側で維持しようとすると、選定基準の追加になり、ユーザーが認めた微調整の範囲を超える。
- ただし質問ではなく事実として、Closeoutの残存事項とSSOTに「X/ZではTopic枠が廃止された」と明記すること。

**F3 契約キー → 他の誤発火経路は見つからなかった。ただし欠落・衝突・不整合が3件ある**
- 確認した経路はすべて問題なし。
  - KP source gate: `source_span`の本文実在だけを見ており、原文スライスなので必ず満たす。
  - Z D1: gate後に`source_reference_contract`=LABELを書き戻すが、canonicalizationへは戻らない。
  - `select_alignment_targets`: 判定キーは`kp_extends_beyond_candidate`(False)。基本形化したitemは`kp_adds_words_beyond_display`で対象になるが、どのみち全件が対象なので無害。
  - Store key・試聴ページ: rankにも件数にも依存しない。
- 代わりに見つかったのは次の3件(must-fix)。
  - (P-01) fulltext用フィールドがmergeで消える。
  - (P-06) er105の`resolution_method`を、D1が`exact`で上書きする。
  - (P-03) Adv解説が`display_phrase`(本文の表層形)に対して生成される。根拠は`er019_family_x_kp_explanation_01.py:152,306`と`er026:1541`。一方、音声と試聴ページは`used_form`(基本形)を使う(`er019:2178`)。結果として「push prices up → (解説)made prices go up → push prices up」のような時制のずれが毎回起きる。

**F4 retry階層の最悪ケース → 無限ループ・二重課金・HR迂回は無い。上限見積は過小**
- 各段の上限はすべて定数で、HRは外側retryの対象外。Xの`--scaffold-only kp`の1回制限も維持されている。
- 「3.6円/レベル」は選定の呼出しか数えていない。canonicalization・gloss(reasoning high、item毎retry)・Redundancyを含めると、最悪は1周約10呼出×5周=約50呼出、つまり約10〜15円/レベル。
- それでも上限が定数で決まっているので、cap判定コードの撤去は安全。
- KP stageの中ではSTOP_ALLセンチネルを確認していない。これは既存からの状態だが、呼出数が増えるので外側retryの各周で確認すること(OF-KPFT-P-08)。

**F5 並行作業(KP3V・PNAP)との衝突 → 領域分離の主張は正しい**
- コード上は重ならない。KP3Vは`er019`:726-770、`generate_or_reuse_z`、Store field。KPFTはscaffold部、`_merge_checkpoint`、`provision_shell_assets`。PNAPはtts stageの入口。
- 重なるのはテストfixtureのほう。KPFTが追加予定の「下流rank駆動test(dual audit等)」は、KP3Vが改名する`kp_dual_check`に依存しうる。
- 順序の必須依存は無い。ただし、KP3Vを先に配線する(またはKPFTのテストを判定フィールド名に依存させない)と手戻りが減る。両方を同日に配線するなら、Family X/Zそれぞれ1回の合同runtime evidenceにまとめるのが費用・時間の両面で最適(OF-KPFT-P-12)。

**F6 stale退避と`_merge_checkpoint`の刈り込み → 既存5件記事への副作用は無い**
- 再利用は`generate_or_reuse_z`がtext sha込みのreuse_keyで判定している(`er063:722`)。結果はplan(rank1..n)からその都度組み立てるので、旧rank4・5は新しいresultに入らない。刈り込みは無害だが、効果も小さい。
- 実在する穴は別の場所にある。`only_clips`経路(`er063:1164-1167`)は、cachedをkey照合なしで流用する。同じrun dirでKPを再生成した後に部分再生成すると、旧語句の音声が混入しうる。rank集合ではなく、reuse_key(本文)の不一致で刈り込むこと。
- legacy `--stage keyphrase`(`er026:866-891`)は、process=NoneでSol系の既定モデルを使い、A2の1レベルだけ・Strategy L・5件で動く。D1・外側retry・gloss関所をすべて迂回するので、付け替えではなく撤去すること(呼ばれたら明示エラー)。

## 3. 指摘事項

### must-fix(配線前に必須)

**OF-KPFT-P-01【Major】merge時にfulltext用フィールドが消える**
- 対応: `merge_canonicalization_result`の引き継ぎ対象に、`fulltext_source_ref`・`source_sentence_id`・`occurrence_count`・`occurrence_sentence_ids`・選定時の解決方式を追加する。存在する場合だけ引き継ぐので、A/B/Cの出力は変わらない。
- テスト: 選定→merge→`select_generation_targets`/`select_consumer_unevaluated`を通しで確認する統合testを必須にする。

**OF-KPFT-P-02【Major】Q1を配線するための付帯修正**
1. `lemma_normalization`はfulltext経路専用のschema/enumで扱う。共有の`NORMALIZATION_REASONS`に足すと、A/B/Cへ送るschemaの中身が変わり、「A/B/Cはバイト同一」の条件が崩れる。
2. `_qa_field_effective_verdict`で、validatorが合格した基本形化に限り`qa_traceable_contiguous_span`をPASSとして扱う。これが無いと、動詞を含むitemの大半がREVIEW_REQUIREDになる。
3. 「display中の連続した語の範囲+1対1の基本形化/人称一般化」の組合せを受理する。例: gave back some gains → give back。既存Rule7の「部分文字列ならOK」と同じ考え方。これが無いとINVALIDが続いてstageが止まる。
4. 基本形化と人称一般化が同時に起きる場合は、どちらのreasonでも受理する。

**OF-KPFT-P-03【Major】Adv解説の対象を音声と揃える**
- fulltext itemでは、解説の入力phraseと`by_phrase`照合キーを`used_form`(音声・試聴ページで実際に使う形)にする。Zの解説sigも合わせる。
- `display_phrase`は選定の証跡として残す。

**OF-KPFT-P-04【Minor】基本形化validatorの誤受理を防ぐ**
- 現状の接尾辞規則だと、mixed feelings→mix feelings、heated debate→heat debate、news→new、goods→good、means→meanのような意味を変える変換も通ってしまう。
- 対応:
  - 動詞の活用形(-ed/-ing/不規則形/三単現)の変換は、先頭トークンかtoの直後に限る。
  - 複数→単数は、閉じた除外表(news/goods/means/arms/glasses/savings/earnings/odds/terms/clothes/series/species/headquarters/belongings等)に当たるものを拒否する。
  - 旧template:7の「be + 過去分詞」見出し形と揃えるため、is/are/was/were/been→be、has/had→have、does/did→doを不規則表に追加する。

**OF-KPFT-P-05【Minor】legacy `--stage keyphrase`の扱い**
- 付け替えではなく撤去する(呼ばれたら明示エラー)。5件・Sol系モデルでProductionに届く経路を残さない。

**OF-KPFT-P-06【Minor】解決方式フィールドの名前衝突**
- er105の`resolution_method`を`selection_resolution_method`等に改名する。Z D1が同名フィールドを`exact`で上書きするため。

### recommended(配線時に対応)

**OF-KPFT-P-07【Major・速度】選定retryの改善**
- 2回目の選定に機械診断noteを付ける。中身は不適合だった語句と理由で、置き場所は本文の後ろ(Redundancy noteと同じ方式)。
- 技術失敗時は待ち時間を入れてから再試行する。
- 選定INVALIDも外側retryの予算に含めることを検討する。

**OF-KPFT-P-08【Minor】X外側retryの実装**
- Zと同じく、カウンタを入れ子にしない構造にする。実装はできれば共有化する。
- 各周の開始時にSTOPセンチネルを確認する。Z側に残る「Z限定・暫定」というコメントも更新する。

**OF-KPFT-P-09【Minor】`_merge_checkpoint`と`only_clips`経路**
- 刈り込みはreuse_key(本文)の不一致で行う。
- `only_clips`経路のkey照合なし流用を塞ぐ。
- 同じrun dirに残るkp4/kp5のwavを扱う方針を決める。

**OF-KPFT-P-10【Minor】構造化出力まわり**
- APIがschemaを拒否した場合(400)は、retryせず設定エラーとして即停止する。schemaから`minItems`/`maxItems`を外し、件数はローカル検証だけに任せる案もある。
- attemptごとの生出力を監査用に保存する。
- 文単位の境界をまたいで不一致になった場合は、理由を区別して記録する。

**OF-KPFT-P-11【Minor】撤去の順序**
- 2つ目のcommit(旧経路撤去)を、Gate 3のruntime evidenceの前に行うことを推奨する。そうすればevidenceが最終コードを検証したことになる。
- DB Hybridへの切り戻しはユーザー決定に反するので、旧コードを残してもrollback価値は低い。緊急時は`git revert`で足りる。

**OF-KPFT-P-12【Minor】KP3Vとの順序と合同evidence**
- KP3Vを先に配線するか、KPFTのテストを判定フィールド名に依存させない。
- 同日に配線できるなら、Family X/Zそれぞれ1回の合同runtime evidenceにまとめる。

**OF-KPFT-P-13【Minor】旧template:15の「数値を補わないと意味が成立しない句は選ばない」規則**
- Prompt 2では落ち、gloss規則の抽出対象にも入っていない。
- Fableが、これが「承認済みのProduction品質条件」に当たるかを照合する。当たる場合は、決定論precheckか解説/gloss規則として残す。

**OF-KPFT-P-14【Minor】旧方式のKP成果物の扱い**
- 配線後に旧5件のKPを再利用した場合(`ensure_stage`、HR snapshotの復元)は、完成報告で`kp_backend_used`を表示して区別する。
- Gate 3のevidenceは新しいrun dirで取る(設計どおり)。

## 4. ユーザー判断が必要な事項: なし

ただし次の3点は、質問ではなく事実としてCloseoutとSSOTに開示すること。
- X/ZでTopic枠(4+1)を廃止したこと。
- 原形化から語順の整理が外れ、範囲が狭くなったこと。
- X/ZではRule7に基本形化の例外を追加したこと(人称一般化と同じ型)。

## 5. 量産単価・品質・速度への影響

- **量産単価**: 方向は正しいが、約-4.8円/セットという額は過大と見る。
  - 音声分の約-3.9円は、KPが占める「呼出数」の比率(42%)で計算している。実際のTTS/ASRは文字数・秒数で課金され、KPの音声は短い。費用で見たKPの比率は呼出数の比率よりかなり小さい。
  - 一方、gloss生成はreasoning highで全件に回るので、+0.1円より増える可能性がある。
  - 現実的な見込みは約-1.5〜-3.5円/セット。runtime evidenceの`raw_usage_log`をstage別に集計した実測値で置き換えること。KP3Vが入るとKP 1件あたりのASR回数が増えるので、3件化による削減幅はその分大きくなる。
- **品質**: must-fixを反映すれば、維持かやや改善。本文一致・語数・件数を機械で保証でき、基本形化も決定論で縛れる。P-01・P-03を入れないまま配線すると、Stdの日本語意味が欠落し、Adv解説と音声の形がずれるので劣化する。
- **速度**: ほぼ変わらないか、やや速くなる。M2の照会(Wiktionary検索・shortlist構築)が無くなる。代わりにgloss生成の呼出が1レベル1回増える。P-07を入れないと、記事単位で約3%がstage停止になり、手戻りによる遅延が出る。

主な参照ファイル:
- er003_key_words_canonicalization.py(:487-535, :458-465, :102-121, :707-778)
- er003_key_words_gloss_alignment.py(:147-150, :253-275, :573-613, :755-792)
- er105_kp_fulltext_selector_01.py(:206-265, :420-464)
- er019_family_x_kp_explanation_01.py(:145-158, :303-315)
- er019_family_x_audio_production_runner_01.py(:2175-2183)
- er026_family_z_src_posthoc_01.py(:42-64, :98-143)
- er026_family_z_fiction_production_runner_01.py(:866-891, :1470-1550)
- er063_family_z_audio_01.py(:716-746, :1094-1114, :1160-1174)
- er062_family_z_writer_01.py(:1055-1114)
- er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt(:7, :15)
---