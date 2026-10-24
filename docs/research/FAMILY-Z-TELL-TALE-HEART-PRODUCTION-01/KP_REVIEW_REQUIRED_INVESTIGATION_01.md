# KP_REVIEW_REQUIRED_INVESTIGATION_01(FZTTH 委任_04、API 0、コード変更0、2026-10-24)

## 調査問い
Z runner `er026_family_z_fiction_production_runner_01.py:1712-1713` が `CANONICALIZATION_REVIEW_REQUIRED` を受理する挙動に承認記録はあるか。

## 事実(file:line)
1. 定義: `er003_key_words_canonicalization.py:630-650` — REVIEW_REQUIRED=「構造validator合格かつQAに1件以上FAIL。**自動採用しない。人間確認後に採用可能**」。3状態モデルは `CURRENT_SPEC.md:1964`(DECIDED、ER-003-KP-01→KP-02→KP-02-R1、2026-08-08、commit ae4928c3d)。
2. しかし共有module内の呼出側は当初からREVIEW_REQUIREDを**通過扱い**: `er003_v1_n3_01_scaffold_generate.py:520`(canonicalization結果の処理)・`:780`(X/Z共通の外側retry。INVALIDのみfailure加算)・`:910`(旧A/B/C経路)。`:780`の元は2026-08-17 ER-003-A2-B1-N3-01 (17aa9b211) / 2026-09-02 ER-011-NO18 (521e884f5) 由来で、REVIEW_REQUIREDで止める分岐は存在しない。
3. Z runner: `er026:1712-1713` の判定は「canonicalization無し/OUTER_RETRY_EXHAUSTED/NG_REVIEW_REQUIRED、またはstatusがPASS/REVIEW_REQUIRED以外」で停止。2026-10-12 委任_10 (e9e5d0a3e) の差分は旧 `res.status=="NG_REVIEW_REQUIRED" or not canonicalization`(REVIEW_REQUIREDは元々通過)へ外側retry由来のstatus確認を追加しただけで、**REVIEW_REQUIRED受理は委任_10以前から存在**。コメント「Z限定・暫定の外側retry」は外側retry(OPEN-310回避)の暫定性を指し、REVIEW_REQUIRED受理の承認根拠ではない。
4. X runner: `er019_family_x_audio_production_runner_01.py:350-351` `KP_STAGE_PASS_CANON_STATUSES=("CANONICALIZATION_PASS","CANONICALIZATION_REVIEW_REQUIRED")`(KPMP-03 委任_03、2026-10-22、「Z側と同一リテラル」と明記)。X経路もREVIEW_REQUIREDを受理し、テスト(`er019_family_x_kp_stage_fail_closed_01_test_01.py:56,75`)が「受理」を期待値として固定している。つまりX/Z同形で、Zだけの逸脱ではない。
5. 人間確認の前例: DECISION_LOG:541(USER-TEST-SCRIPT-READABILITY-PROD-01)「REVIEW_REQUIRED2件ユーザー承認」、同9013付近(Free-Address A2 REVIEW_REQUIRED 2/5件)— いずれも個別案件の人間確認であり、「REVIEW_REQUIREDをX/Z Productionで自動受理する」包括承認ではない。`OPEN_ITEMS.md` OPEN-202(KPFT)は`CANONICALIZATION_REVIEW_REQUIRED`率を**量産observation対象**として監視する記述のみ(受理方針の承認ではない)。
6. grep範囲: DECISION_LOG.md・DECISION_LOG_HISTORY.md・OPEN_ITEMS.md・OPEN_ITEMS_HISTORY.md・CURRENT_SPEC.md・PM_GOVERNANCE.md・ER-*_REPORT.md・docs/research を `CANONICALIZATION_REVIEW_REQUIRED` / `REVIEW_REQUIRED`(canonicalization/KP文脈)でgrep。「X/ZでREVIEW_REQUIRED KPを自動受理してよい」というユーザー承認原文・Fable決定は**発見できず**。

## 結論
- **承認記録: なし**。定義(「自動採用しない。人間確認後に採用可能」)と、共有module・X/Z runnerの実挙動(自動受理)が乖離している。経緯は「3状態モデル導入(8/8)後、共有moduleの呼出側が通過扱いで実装(8/17)、X/Zが継承(9月〜10月)」で、意図的な採用判断の記録がない。
- 実害の頻度: 保存済みX/Z最終 `keywords_canonicalized.json`(約320件)中 overall_status=REVIEW_REQUIRED は3件のみ(X: paycheck_personality run_pp_01 a2、Trial 1件[er112 base_c rep2]、Z: melos run_01。本作品の旧Std KPは差替え済み)。低頻度だが、1件でも学習単位として不適切なKP(『vulture's』=QA4項目FAIL)が出荷候補に入り得る。
- 今回の是正: 受理挙動自体は変更せず(Production変更なし)、委任_04の運用で「REVIEW_REQUIREDでQA FAIL含みなら採用しない」を適用(再選定1回目で`vulture's`再選定→不採用、2回目でPASS採用)。
- 分類: **修正へ進む**(新規OPEN-504)。修正案(Fable判断待ち、今回は未実施): 外側retry(`er003_v1_n3_01_scaffold_generate.py:780`)でREVIEW_REQUIREDを「次attemptへ(INVALID同様に除外語を付けて再選定、通算上限内)」とし、上限到達後のREVIEW_REQUIREDのみ`KP_REVIEW_REQUIRED_STOP`相当でHR/停止へ。X/Z共通経路の意味的変更に当たる可能性があるため、実施前に(a)承認済み仕様との整合(品質基準=必要十分)として不具合是正(PM_GOVERNANCE 11-8)か仕様変更(ユーザー判断)かをFableが判定、(b)Opus独立レビュー条件A該当性、(c)X/Z回帰test(er019 fail-closed test:56,75の期待値更新)が必要。
