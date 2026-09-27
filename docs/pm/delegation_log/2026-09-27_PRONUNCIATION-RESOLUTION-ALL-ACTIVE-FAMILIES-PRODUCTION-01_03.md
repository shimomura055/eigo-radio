# 委任文(全文保存) — PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正1回目)

保存日: 2026-09-27。Fableから受領した委任文をそのまま保存する(要約しない)。

---

管理ID: PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正1回目: Opus L2レビューのBLOCKER是正+runtime evidence。ユーザー承認済み=既存Production blockerの是正。PRODUCTION_WIRED判定はFableが後で行う)。一時ファイル `docs/pm/ACTIVE_TASK_PRN3.md` / `docs/pm/RESULT_PACKET_PRN3.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_03.md` へ保存しcommitに含める。

並走: Family X Stage 3c Agentが `er019_family_x_audio_*` を編集・TTS実行中 → **er019_* は Stage 3c完了(`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md` に「§Stage 3c」節が追加され、`git log` に該当commitが出る)まで編集しない**。KP Trial 03(er028_*)・PMルール(docs/pm/PM_*)に触らない。SSOT 3ファイルは編集しない(記載案のみ)。共有module編集は1ファイルずつ最小差分+編集直後import確認。

先に読む: `docs/pm/PM_BRIEF.md`、`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md`、`docs/pm/RESULT_PACKET_PRNG.md`(Gate照合)、そして**Opus L2所見(以下に要点、逐語はFableのhand-backより転記)**。Existing Spec Check: 修正はすべて「Phase 2で新規に開いた穴/既存仕様の未達」の是正であり分類A。新仕様を作らない。

## Opus L2所見(要点。REPORT §14へ逐語相当で転記すること)
- 総合: 現状のままPRODUCTION_WIRED非推奨。BLOCKER-1/2解消+再検証後に判定可。
- **BLOCKER-1**: `er006_pronunciation_ledger_01.py:124` `entry["surface"].lower() in text_lower` の語境界なし部分一致が、Phase 2で初めてTTS prompt生成経路(`er003_v1_repro01_main_generate.py:285-290`)へ接続された。本番Ledgerに ASR Cascade由来の誤entry(surface="plus"/canonical="cascade"/hint "kass-KAYD"/confidence=medium、"main story"→"cascade"、"one voice"→"one voice unknown"、"mini"→"MIN-ee")が注入閾値で存在 → "plus/surplus"を含む英文で誤発音指示が付与され音声破壊→retry→Human Review。low側も`get_low_confidence_entries_for_text`(:130-138)が部分一致で"ganis"→"organisation"等に誤発火し、有料Perplexity再research(`er025...core:264-278`)が無関係記事で毎プロセス走る。修正: (i) 語境界付き一致(非Latin surfaceは別扱い)、(ii) `entity_type=="cascade_unresolved_entity"`をTTS注入対象から除外(ASR Phrase List用途は維持)、またはcanonical_spellingがsurfaceと整合しないentryを除外、(iii) 本番ledger.jsonの誤entry隔離/削除、(iv) 回帰test「"plus"/"surplus"/"minister"を含む英文でhits=0」。
- **BLOCKER-2**: JA読みentryのkeyが`LedgerKey(surface, "ja_reading_katakana", source_context="")`固定=同綴りは全記事で1読みのみ。Dionysiusは史実(ディオニュシオス)と太宰(ディオニス)で割れ、web lookupは史実側を返す可能性大。修正: core/ledgerに`source_context`を通す(既定""で後方互換)、作品固有読みは`resolution_method="work_canon"`/confidence=highで事前seed(出典書誌を`ja_reading_sources`へ)、seed済みならlookupスキップ。EN hint(pronunciation_hint)も同entryにseed可。
- Figma confidence不整合: 原因=evidence実行時のcoreにconfidence鏡写し(`:216-220`)が無く後から追加、cache-hitはupsertしないため自己修復しない → 既存JA entryのbackfill+「cache hit時に不整合検出→再upsert」またはtest追加。
- 後でも可(ただしSSOT文言訂正必須): EN記事単位抽出未配線、`generate_english_component_minimal_instruction`(repro01:477、B1 scaffold/crosslevel/news_tail_fix等が呼ぶ)非適用。「全EN経路」表記を「`generate_narration_snippet_verified_strict`経由のみ」へ訂正、EN未知語初出は未カバーとOPEN起票。
- JA側: 解決読みはTTSへ届かず(Gate解除+ASR期待読みのみ)。resolverとTTSが同方向に誤読すると相関誤ACCEPTの可能性。正直に記述。JA読みをTTSへ届ける方式は**別Phase**(本委任では設計しない)。
- confidence: JAはLLM自己申告、`ja_reading_sources`が1件しか保存されない(`:214`)→sources全件保存。
- retry整合: OK。ただしREGENERATE_APPROVED再生成でLedger cacheが効くため誤読みが再現する→Human Review時にLedger entryを訂正/無効化する運用経路をOPEN起票。Master Audio Store再利用で「直った音声に差し替わらない」ケース→修復時に該当segmentのstore invalidate確認。resolverがHuman Review Lock判定より手前で有料lookupが走りうる(軽微)。
- QCD: negative cache無し(未解決語を毎回再lookup)→未解決entry保存+run単位lookup上限・telemetry。Ledger健全性チェック(canonical_spellingとsurfaceの整合、hint空)。
- テスト: 恒久策=テスト時web lookup禁止スイッチ(例 `ALLOW_PRONUNCIATION_WEB_LOOKUP`、unittest時は必ずskip)+「回帰前後でledger.jsonのhash不変」test。
- DECISION_LOGへJA web lookupの`gpt-5.6-sol`継承(既存r3関数の無改変再利用)を記録。
- 未確認: Family X runnerがsegmentごとにプロセスを分けるか(in-memory cacheの範囲、1記事あたりlookup実回数)。

## 作業(優先順)
1. BLOCKER-1: 上記(i)〜(iv)を実装。`er006_pronunciation_ledger_01.py`/`er006_pronunciation_tts_injection_01.py`/`er025_*core*`。本番 `er006_output/pronunciation_ledger_01/ledger.json` の誤entryは削除ではなく `entity_type`はそのまま・新フィールド `tts_injection_disabled: true`+理由 で隔離(ASR Phrase List用途は維持)。差分をREPORTへ全件列挙。
2. BLOCKER-2: `source_context`対応+seed API(`seed_work_canon_reading(surface, ja_katakana, en_hint, source_context, sources)`)+Family Z用seed手順。**Melos人名seed**: 信頼ソース=太宰治『走れメロス』(青空文庫等の書誌URL)で「メロス/セリヌンティウス/ディオニス」をsource_context="family_z_melos"としてseed(これは一般機構のwork_canon経路であり、Muse型のhardcodeではない)。
3. Figma backfill+不整合検出時再upsert+鏡写しtest。`ja_reading_sources`全件保存。
4. negative cache+run単位lookup上限・telemetry(`er025_output/.../telemetry.jsonl`)。Ledger健全性チェック関数(read-only、報告用)。
5. テスト時web lookup禁止スイッチ+ledger hash不変test。`er006_kp5_canonical_bug_01_test.py`等の無mock直接呼び出しはスイッチで無害化。
6. `generate_english_component_minimal_instruction`経路へresolver適用(BLOCKER-1修正後なら安全)。EN記事単位抽出のProduction配線は**Stage 3c完了後**にFamily X audio runnerのscaffold段へ(`extract_proper_nouns`→cache miss分のみresearch→Ledger、1記事1回)。Family X runnerのプロセス単位(segmentごとか)を確認し、in-memory cacheの範囲と1記事あたりlookup実回数をREPORTへ。
7. REPORT/SSOT記載案の文言訂正(「全EN経路」→実カバレッジ)、OPEN起票案(EN未知語初出未カバー[配線後は解消として記載]、Human Review時のLedger訂正経路、JA読みTTS直接供給=別Phase)、DECISION_LOG記載案(sol継承)。
8. **runtime evidence**(`TTS_EXECUTION_MODE=STANDARD`、合計Guardrail ¥300、¥250で停止):
   - EN-3: 回帰test("plus"等でhits=0)+修正後Ledgerで、Family X既存英文segment(small_bagのtoteme含む)に対する`get_hint_for_text`結果を¥0で列挙(誤注入ゼロを機械確認)。
   - **Stage 3c点検(必須)**: Stage 3c完了後、`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/{small_bag__run_02,hormuz__run_02}/` の全EN segmentについて、使用されたstyle_prefix(audit/tts_generation_results.json等)にPhase 2由来の発音ヒント注入があったか、あった場合はBLOCKER-1の誤注入(plus/mini/main story/one voice/ganis等)かを列挙。誤注入があったsegmentは、修正後コードで再TTS(OK済みの他segmentは再利用)し、Master Audio Storeの該当entryをinvalidateしてから再生成。
   - JA-1(Meta): Stage 3c完了後、`er019_family_x_audio_production_runner_01.py`既存経路で`a2/japanese_title`("Muse")のみ再TTS→検出→lookup発火→confidence→自動使用→TTS成功→Ledger保存→2回目実行でcache hit・追加lookup 0回、A2 Assembly完走(他Gate STOPなら記録)。
   - JA-3(Hormuz): B1B `kp2_japanese`「海からの封鎖」をCandidate E適用の既存経路で再判定→OKならB1B Assembly完走を試みる(Stage 3c後の状態を前提)。
   - JA-4(Melos): seed後、`er026_output/family_z_production_e2e_01/melos/run_01/` のPreview/Comment日本語テキストに対し、共有JA TTS入口(`generate_a2_japanese_with_reading_safety`等の**Production関数**)を直接呼び、Dionysius/Selinuntius/Melosが seed読み(cache hit、lookup 0回)で統一され、TTS+ASRがPASSすることを記録(Family Z runnerのTTS stage実装は別委任。ここでは関数直呼びのevidence)。
   - 各evidenceでmodel_id/routing/費用/latency/lookup回数を記録。
9. 回帰: `run_project_regression.py` をTTS実行と並行させず単独実行(既知pre-existing 5件は除外扱いで記録)。Opus所見との照合表(所見→対応→証跡)をREPORT §15に。

## 報告
REPORT末尾に §14(Opus所見逐語)/§15(照合表)/§16(修正内容・diff)/§17(runtime evidence: EN-3/Stage 3c点検/JA-1/JA-3/JA-4)/§18(回帰)/§19(Gate 3 checklist再評価)/§20(SSOT記載案・OPEN起票案)/§21(残課題: EN記事単位抽出の配線状況、JA読みTTS直接供給=別Phase、Human Review時Ledger訂正経路)。RESULT_PACKET_PRN3.mdに要約。

## STOP条件(ユーザー定義)
信頼できる読み/発音が決定できない・複数候補で自動選択不能・ライセンス/有料API判断・既存Production仕様と衝突・大きなArchitecture変更・ユーザー判断なしで仕様決定不能 → 報告してSTOP。単なる未登録語・辞書追加・実装方法選択はSTOP理由にしない。

## Git
変更/新規ファイル・ledger.json(隔離フラグ・backfill・seed)・出力JSON/audit(wav除く)・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01`。push origin main。`ACTIVE_TASK*`/`RESULT_PACKET*`はcommitしない。reset/amend/rebase/force push禁止。APIキーは環境変数のみ。
