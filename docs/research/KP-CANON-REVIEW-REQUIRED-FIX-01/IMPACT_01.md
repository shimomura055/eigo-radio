# IMPACT_01(KP-CANON-REVIEW-REQUIRED-FIX-01 委任_01、影響分析gate、API 0、2026-10-25)

目的: OPEN-504(X/ZがKP正規化 `CANONICALIZATION_REVIEW_REQUIRED` を自動受理)を、承認済み3状態モデル
(`CURRENT_SPEC.md:1964-1966`「REVIEW_REQUIREDは自動採用しない・人間確認後に採用可」、`er003_key_words_canonicalization.py:630-650`)へ整合させる不具合是正(PM_GOVERNANCE 11-8、新仕様ではない)。

## 1. 受理箇所の全列挙(`CANONICALIZATION_REVIEW_REQUIRED` を通過扱いにする production系コード)
| # | 箇所 | 役割 | 経路 | 今回 |
|---|---|---|---|---|
| 1 | `er003_v1_n3_01_scaffold_generate.py` 外側retry(`run_kp_with_outer_retry`、旧:780) | X/Z共通の外側retry | X・Z・Y trial(`kp_backend=fulltext_p2`) | **変更**(REVIEW_REQUIREDもfailure加算+除外語付き再選定、上限到達でOUTER_RETRY_EXHAUSTED) |
| 2 | 同 `run_key_phrase_canonicalization`(:520) | 1回分のcanonicalization結果の処理(mergedを書く) | X/Z/A/B/C共通の部品 | **無変更**(部品の戻り値。採否判断は呼出側=#1/#3) |
| 3 | 同 `_run_key_phrases_impl`(旧:910) | A/B/C(strategy_l/db_hybrid) | **A/B/C凍結ライン** | **無変更**(Family A/B/C凍結。27-7) |
| 4 | `er019_family_x_audio_production_runner_01.py` `KP_STAGE_PASS_CANON_STATUSES` | X stage fail-closed | X | **変更**(PASSのみ。多層防御) |
| 5 | `er026_family_z_fiction_production_runner_01.py` `stage_kp`(:1712-1713) | Z stage停止判定 | Z | **変更**(PASSのみ) |
| 6 | `er003_key_words_canonicalization.py:795` `run_canonicalization_gate` | 内側gate(INVALIDのみ再試行) | 全Family共通 | **無変更**(「自動retryなし=canonicalization(Luna)自体は再試行しない」という仕様記述のとおり) |
| 7 | その他 `er011_*`/`er012_*`/`er013_*`/`er014_*`/`er017`/`er064`/`er005` 等の過去Trial・A/B/C・手動スクリプト約30ファイル | 過去Trial/凍結ライン | A/B/C・Trial | **無変更**(grep結果は下記。Family X/Z/将来Yの経路を通らない) |

grep: `grep -rn CANONICALIZATION_REVIEW_REQUIRED --include=*.py`。X/Zが実際に通るのは #1(共有)+#4/#5(runnerのstage判定)の3点のみ。

## 2. 各Family経路の到達性
- X: `er019 run_theme_scaffold`→`sc.run_key_phrases(kp_backend=fulltext_p2)`→`run_kp_with_outer_retry`(#1)→戻り値を`kp_stage_failure_status`(#4)。到達=あり(変更対象)。
- Z: `er026 stage_kp`→`w62.run_kp_stage`→`run_kp_with_outer_retry_fulltext`→`sc.run_kp_with_outer_retry`(#1)→`stage_kp`の判定(#5)。到達=あり(変更対象)。
- 将来Y: Y trial(`er110_*`)は`sc.run_key_phrases(kp_backend=fulltext_p2)`を使うため#1を通る。Yは「採用はPASSのみ」となり仕様どおり(DEV/Trial経路・副作用なし)。
- A/B/C: `kp_backend`既定`strategy_l`/`db_hybrid`→`_run_key_phrases_impl`(#3)。`run_kp_with_outer_retry`を通らない。**無影響**(Gate・prompt・閾値・コード無変更。`er073_*`等の過去Z移行run scriptは`w62.run_kp_with_outer_retry`を呼ぶが、歴史的Trial scriptで再実行されない)。
- 新flag・Prompt・閾値の変更: **なし**(selection promptは`excluded_phrases`の既存除外note機構[`er105.build_exclusion_note`]を再利用)。

## 3. 保存済みX/Z最終KPでREVIEW_REQUIREDだった件の扱い
走査(`keywords_canonicalized.json`、X/Z最終成果+Trial、`overall_status`):
- X: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/a2/key_phrases/keywords_canonicalized.json`(REVIEW_REQUIRED)
- Trial: `er112_output/kp_gm_trial_01/runs/base_c/rep2/.../keywords_canonicalized.json`(Trial。REVIEW_REQUIREDだった1件。kp_gm_trial_04はTrial内の別件)
- Z: `er026_output/family_z_production_e2e_01/melos/run_01/key_phrases/keywords_canonicalized.json`(『メロス』REVIEW_REQUIRED)
- 母数: X/Z最終キー`PASS`198+`CANONICALIZATION_PASS`12+REVIEW_REQUIRED 2(走査範囲) ≒ 調査書の約320ファイル中3件。
- **扱い: 再処理しない・記録のみ**。理由: (a) 公開済み/ユーザー確認済みの作品で、KPを変えると既存のTTS clip・解説・公開ページとの整合が崩れる(再生成=費用+公開物変更はScope外。OPEN-490同様に記録のみ)。(b) 今回は「今後のrun」を仕様どおりにする是正で、過去成果物の遡及改変は委任範囲外。(c) 3件は低頻度(約1%)で、いずれもユーザー最終試聴/公開前確認を経ている。残存は`OPEN_ITEMS.md` OPEN-504に事実として記録する。

## 4. 修正後のHR停止頻度の見積
- 過去頻度 REVIEW_REQUIRED ≈ 3/320 ≈ 0.9%/KP段(attempt単位)。再選定1回で解消する確率は高い(FZTTH 委任_04の『vulture's』は2回目でPASS)。
- 通算3回(`KP_OUTER_RETRY_MAX`、INVALIDと共有)すべてREVIEW_REQUIREDまたはINVALIDになる確率は、attempt間独立と仮定して ≲ 0.9%^2〜^3 ≒ 0.01%未満(桁見積。記事間独立でない場合でも1%未満)。よってHR停止は「記事あたり0.1%未満」〜「数百記事に1回」。停止時は`OUTER_RETRY_EXHAUSTED`で既存のKP停止(Xは`KP_STAGE_FAILED`、Zは`FamilyZE2EStop`)へ入り、人間確認を求める(自動採用しない)。

## 5. retry回数上限と費用影響
- 上限: 外側retryの`failures`(選定失敗・INVALID・CMU・今回のREVIEW_REQUIRED)の通算`max_outer=3`は不変。REVIEW_REQUIREDは新たにこの予算を消費する(上限を増やさない)。Redundancy NG用の別カウント(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)も不変。最大周回数は従来どおり。
- 費用: REVIEW_REQUIRED発生時のみ再選定1周追加 ≒ 1.4円(選定+canonicalization+gloss alignment)。頻度0.9%/KP段 → 期待追加費用 ≒ 0.013円/KP段(A2+B1 or Std+Adv で約0.03円/記事)。量産単価70円/記事セットへの影響は無視できる(<0.05%)。品質(QA FAIL KPの出荷防止)に対する費用として妥当。
- 副作用: REVIEW_REQUIREDのattemptでもcanonicalization内でgloss alignment(Luna)が1回走って費用が発生する(従来も同じ)。共有部品(#2)を変えるとA/B/Cへ影響するため今回は変えない(OPEN化しない軽微な無駄)。

## 6. 仕様解釈の注記(Fable向け)
CURRENT_SPECの「human review条件: …自動retryなし、人間承認で採用可」の「自動retryなし」は、canonicalization(Luna)出力のQA FAILに対し**同じ入力で再試行しない**(内側gate、無変更)という意味に読める。今回の外側の**除外語付き再選定**は別の層(選定の再実施)であり、FZTTH 委任_04で手動実施した運用と同じ。Fable指示(再選定→上限後HR)に従いこの解釈で実装した。この解釈が不適切なら撤退=revert(Production変更は単独commit)。
