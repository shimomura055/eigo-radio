# 委任文(逐語全文) — KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01(修正1回目)

受領日: 2026-09-28
受領者: Sonnet 5(sandwich実行層)

---

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01(Sonnet修正1回目=Opus L2所見反映。**¥0、API呼び出し禁止**(残予算¥9.6)、決定論的修正+既存生応答/shortlistでのオフライン再検証のみ)。一時ファイル `docs/pm/ACTIVE_TASK_KPC2.md` / `docs/pm/RESULT_PACKET_KPC2.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_02.md` に保存しcommitに含める。他Agent(Flash-Lite 02: er003_v1_*/er033_*/er019_*/requirements/SSOT)と衝突するファイルは編集しない。SSOT編集直前に `git status` で未commit差分を確認(SSOT 3点に差分があれば最大10分待ち、解消しなければ記載案をRESULT_PACKETへ)。

## 前提
REPORT `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_REPORT.md` に §「Opus L2所見(逐語)」を追記(本委任文のdelegation_logに全文を添付、そこから転記)。Opus結論: BLOCKER 0、PRODUCTION_WIRED判定へ進んで可、ただしSF-1/SF-2は同一IDで閉じることを強く推奨。Fable判定: SF-1〜SF-7を本修正で反映してからGate 3確定。

## 修正(すべて¥0)
- **SF-1(最優先)**: `restore_source_fields` の `surface_form`(最頻表層)と `context_sentence_id`(変異形のいずれかが最初にヒットした文)が独立に決まるため、復元した `source_span` が `source_sentence` に含まれない場合がある(単数導入→複数反復の典型パターンで発生)。対応: (b) 既実装の `audit_shortlist_source_span_consistency` を **API呼び出し前**に `run_db_hybrid_selection` へ配線し、不整合候補は補正(その文に実在する最長の `observed_surface_variants` を `source_span` に採る)+telemetry記録、補正不能なら候補ID表から除外+記録。(a) `restore_source_fields` 側にも同じ補正を防御的に実装。(c) core側 `context_sentence_id` 補正は行わない(er028無変更)。test: meta_a2 実データ候補(`contract worker`/`contract workers`)を反転させたfixture、既存evidence 11ケースの生応答+shortlistで**オフライン再復元**し全件PASS維持を確認する。
- **SF-2**: `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py::test_shortlist_too_small_raises_before_any_api_call` のmock対象を `db_hybrid.src_ref_contract.make_instrumented_selector_factory` へ差し替え(死んだガードの復活)。
- **SF-3**: CURRENT_SPEC文言「`surface_echo` はschema上必須(strict mode制約)、判定上は非ブロッキング・真実源にしない」へ明確化(コード不変)。
- **SF-4**: `candidate_mismatch_suspected` の算出に `display_phrase` と復元候補のlemma許容の弱い一致比較を追加(非ブロッキング、telemetryのみ)。
- **SF-5**: `surface_form` 欠落時の `source_span` fallbackを削除し `unresolved`(fail-closed)へ。
- **SF-6**: 同一 `source_candidate_id` の重複選択件数を `restore_telemetry` へ記録(非ブロッキング)。
- **SF-7**: `run_db_hybrid_selection` 冒頭で `_check_family_profile_supported` を呼ぶ(Wiktionary lookup前にfail-closed)。
- 項目15の軽微: fallback telemetry行に `attempted_source_reference_contract` を追加。
- N2: CURRENT_SPECに「Family Z配線時は `er030_key_phrase_db_hybrid_source_reference_contract_01` 経由が**必須**(規範)」を明記。N5/N6: OPEN-202へ「`source_sentence` が見出し行になる系統的バイアス(Redundancy QA文脈)」「canonicalization Rule 7の復元余地縮小→`REVIEW_REQUIRED` 率を継続監視」を追記。N4: 新規OPEN「`run_project_regression.py` DEFAULT_PATTERNが `_NN_test.py` 形式(29モジュール、Production中核test含む)を収集しない+実API test/guard testの棚卸しが必要」+「test infraのmock-drift恒久対策(ネットワーク遮断fixture等)」をPM追跡で登録。N11: REPORT/REPORT_LEDGERのevidenceパスを実体 `er030_output/family_x_kp_source_reference_contract_evidence_01/` に是正。N1: DECISION_LOGに「実際の復元を守っているのは surface_form優先の復元規則であり、Stage 1整理は防御の二重化」を明記。
- **別ID分の反映(同Agentで実施、別commit)**: `docs/pm/RESULT_PACKET_PRN9.md` に用意済みの Phase 4(PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01)の OPEN_ITEMS 記載案(OPEN-207追記+新規OPEN-208 Ledger条件再検討)を適用し、トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01` で単独commit。

## 検証
新規/更新test全PASS(¥0)、本IDのtest群(27+32件)は手動実行(regression未収集のため)、`run_project_regression.py`(既知baseline以外なし)。REPORT §「修正1回目」: Opus所見照合表(SF-1〜7/N1〜11: 対応/OPEN/対象外)、オフライン再復元結果、Gate 3表最終化(Opus L2=実施済み、PRODUCTION_WIRED=Fable判定待ち)。SSOT: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER。

Git: path指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。本ID commitのトレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETにcommit hash群・変更ファイル・照合表要約・Gate 3表を記載。

---

## 注記(Sonnet、受領時)

本ファイルは、Fableから本Sonnetへ送付された委任文(上記「管理ID」〜
「Git:」まで)をそのまま保存したものである。上記「前提」節が指す
「Opus L2所見(逐語)」は、Fableが実際のOpus L2レビュー結果を読み、
SF-1〜SF-7・N1・N2・N4・N5・N6・N11として構造化・要約した所見であり、
本ファイルがその内容の記録先(delegation_log)である。REPORT側
(§10「Opus L2所見(逐語)」)は、本ファイルの「前提」「修正」「検証」
節をそのまま転記したものである。
