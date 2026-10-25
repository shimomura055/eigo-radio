管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A(③既存誤PASS是正=OPEN-517 F1+F2、OPEN-523/524 のProduction適用。API 0・有料run 0。**Production code変更あり**=ユーザー承認の範囲内: 2026-10-25ユーザー指示「既存の承認済み安全条件が正しく機能するよう修正する」「現行Productionの既知不具合の原因究明・修正・検証は自律的に進める」「Productionへ反映する際は、承認済み不具合修正の範囲か、新しい合格条件の導入かを区別する」)。並行して委任_07B(別agent)が②B-lightの設計・Trialを担当(docs/proto中心)。**ファイル所有**: 07A=`er078_asr_unified_judge_01.py`、`er078_asr_value_guard_01.py`、`er007_ja_secondary_asr_01.py`(コメント)、関連test、`er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md`(L65)、`CURRENT_SPEC.md`(該当節のみ)、DECISION_LOG(1件)、OPEN-517/523/524、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_APPLY_RESULT_01.md`。07Bは`B_LIGHT_*`docs・proto・OPEN-515/525+を所有。

## 0. 最初に: ユーザー原文の逐語保存
jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl`末尾付近のuser行で「日本語ASR誤判定の包括的根本対策｜①v2・②B-light・③既存誤PASS是正」を含む行を`<pasted_content>`ごと無改変で`docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md`へ保存(文字化けなら`_RAW_JSONL`退避+要旨版)。要旨: ①v2はAPI 0再評価→改善・追加検証は承認済み予算内で自律/②B-light原因究明・設計・Trial承認(UDR #136整合確認、変更は別途承認)/③既存誤PASS: 原因究明・設計・Trial承認、承認済み安全条件が正しく機能するよう修正、数値重大不一致・固有名詞/読み不一致を重視、過剰修正回避、既知不具合の修正・検証は自律、Production反映時は不具合修正か新合格条件かを区別/自律改善ループ(Trialごとの承認不要)/受入: 8,900↔89,000区別・しわ↔すわ区別・みっか↔さんにち必要に応じ区別・既存負例に悪影響なし・正常月題の救済・正しい音声を不要にNGにしない・Gate/retry/resume整合・X/Y/Z共通・Regression PASS/予算: 日次は承認済み枠(本日1,500円)、他案件予算の流用禁止/Status上限VALIDATED、VALIDATEDでもProduction採用自動開始なし、**純粋な実装不具合修正は新仕様採用と区別**/報告12項目。

## 1. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{OPEN517_DESIGN_02,OPEN517_APPLY_PLAN_01,OPEN517_EVAL_02,OPEN517_PREREGISTERED_02,OPUS_REVIEW_01_OPEN517,OPEN517_PUBLIC_AUDIT_01}.md`、`proto_value_gate_fix_04.py`(+test)、`eval_open517_api0_04.py`、`sweep_open517_04.py`、OPEN-517/522/523/524の行、`er078_asr_unified_judge_01.py`、`er078_asr_value_guard_01.py`、`er078_reuse_value_guard_01.py`、`er007_ja_secondary_asr_01.py:407`、`er066_..._trial.py:186-279`(`_cands`)、既存test `er078_asr_unified_ja_wiring_test_01.py`等、`CURRENT_SPEC.md`(L2850/2855/2865付近Grep)。

## 2. Fable判断(転記・適用の根拠)
- F1(READING_MATCH PASSにも最終ANDゲートの値ガードDIFF・否定差を適用)=承認済み安全条件(CURRENT_SPEC:2855・ユーザー原文L97)への回復。追補L65の「読み一致を再否定しない」はFable採用(OF-AUW-01)でユーザー個別承認なし→撤回。11-8 T1不具合是正。合格範囲は狭まるのみ(F1+F2のPASS集合⊂現行PASS集合)=**新しい合格条件の導入ではない**(区別を報告に明記)。
- F2(期待読みによるかな数詞の表記統一、v4=M-2〜M-5反映済み)はF1に伴う誤NG防止の技術部分。
- OPEN-524(KANA_NUMERALSの語境界欠如: `4日↔にじゅうよっか`がEQUAL)、OPEN-523(弱いかな数詞 なのか/ようか/とお のUNKNOWN素通し)は同じ不具合是正の範囲で、**合格範囲を狭める方向のみ**なら同時適用(それぞれ正常attemptのNG化0を条件。満たさなければ適用せずOPEN継続)。OPEN-522(助数詞表外)は適用しない(既知の限界)。
- Opus条件Cレビュー済み(M-1〜M-5・R-1〜R-7反映済み)。適用後に初回run集計(R-3)。

## 3. 作業
A. APPLY_PLAN_01どおりにProduction適用: judge `APPROVED_EQUIVALENCE_BASES`から`READING_MATCH`除去/`_protected`に明示引数`kana_unify`(READING_MATCH PASSのPrimary最終ゲートのみTrue、Primary NG・SecondaryはFalse)/`negation_diff`は置換前テキスト/期待読み表を値ガードへ移設(`er066 _cands`からの意図差分=弱い読み除外・一意でない読み除外をparity testで固定)/`unify_kana_numerals`(v4の M-2(a)(b)・M-3境界/最長一致・単調性ガード)/1行rollback用module定数(env/flag禁止)/`er007:407`コメント更新/reason文字列変更(`primary_pass_approved_equivalence:READING_MATCH`→`primary_pass`)の下流(test・er109研究script)更新/`er078_reuse_value_guard_01.py`との整合確認。
B. OPEN-524/523の是正を同じ値ガード内で実装(語境界確認・弱い読みの扱い)。各々について正常attemptのNG化0をAPI 0で確認できた場合のみ有効化。
C. test: 既存2箇所更新+新規11群(APPLY_PLAN)+基準7合成負例24件をProduction関数で再実行+OPEN-523/524負例+rollback定数の復元test。回帰: er078/er007/er066系・JA ASR cascade・X/Z runnerのASR関連・`er109`・Family Y(er121 audio/runner)の該当test。全体回帰はネットワーク遮断harness(`netblock_harness_01/sitecustomize.py`)+`.venv`で実行、外部接続0。
D. API 0再評価をProduction関数で実施(`eval_open517_api0_prod_01.py`): 既存771+未知493+合成の全件で、proto v4と**完全一致**(差分0)を証明。正常143件NG化0、既知負例9/9遮断、8,900↔89,000・しわ↔すわ(N3-07はCandidate E=OPEN-333のため本是正では遮断されない事実を明記)・みっか↔さんにち(N3-21)の結果を表に。2回実行で決定的。
E. SSOT: ADDENDUM L65から「読み一致」を外しOPEN-517で上書きの旨+元の理由(誤NG防止)+F2が手当てである旨を付記/CURRENT_SPECの該当節(READING_MATCH skipの記述があれば)を是正内容に更新(L2855は不変)/DECISION_LOGに「OF-AUW-01撤回・F1+F2適用・不具合是正区分」1件/OPEN-517=APPLIED(初回run集計待ち)、523/524=APPLIEDまたは継続、522=既知の限界/`OPEN517_APPLY_RESULT_01.md`(変更一覧・差分・再評価・回帰・R-3集計手順・rollback手順)。OPEN_ITEMS/DECISION_LOGは直前再Read・最小Edit・バックアップ(07B・KP HR evidence・Family Y agentが並行編集中)。
F. Git: 対象pathのみ(`git commit --only`または一時index)→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。**Production適用commitは、C/Dがすべて緑であることを確認してから1つのcommitで行う**(途中状態をpushしない)。
G. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <上記jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_07A.md`(Nは599前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A」を592〜640で走査)。

## 4. 禁止
有料API。B-light/Azure併用の実装(07B)。助数詞表の拡張(OPEN-522)。合格範囲を広げる変更。Candidate E(OPEN-333)の変更。公開物・`er0XX_output/`の変更(再判定はしない=遡及なし)。

## 5. 報告(RESULT_PACKET_JAASR7A.md+口頭要約)
変更一覧(Production差分の行数・関数)、proto v4との一致証明、受入項目(8,900↔89,000/しわ↔すわ/みっか↔さんにち/正常NG化0/負例/回帰)の結果表、OPEN-523/524の適用有無と根拠、SSOT更新、R-3初回run集計手順、rollback手順、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。