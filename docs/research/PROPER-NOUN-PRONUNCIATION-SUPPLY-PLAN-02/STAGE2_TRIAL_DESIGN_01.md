# STAGE2_TRIAL_DESIGN_01: 固有名詞発音 Stage 2 Trial 第1巡 設計・開始前チェック

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07 / 2026-10-22 / 性質: Trial(Trial専用経路。Production・正式Ledger・Validator・Prompt・モデル構成・Phrase List 無変更) / 到達Status: `TRIAL_R1_DONE_PENDING_FABLE`
ユーザー原文: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE2-TRIAL-GO_USER.md`(本文文字数2900、sha256 `f0d954c9940182f4d6181796ba35932844edb7c8fbb6e747107a99533786dc4a`)

## 1. 開始前チェック(ユーザー§2〜§7の要求と、満たす場所)

| ユーザー要求 | 本設計での満たし方 | 成果物 |
|---|---|---|
| §2-1 正しい発音をネットから取得(公式/実使用/信頼できる辞書) | O1(無料源HTTP)+R0抽出器(IPA・綴り読み・引用語読みを近傍抽出、出典URL・引用文脈・取得時刻・本文sha256を保存) | `er100_..._o1.py` `..._r0.py` / `o1_free_sources.json` `r0_extractions.json` |
| §2-2 取得不能時の合理的推定(G2P・低コストLLM・複数比較) | E2=`g2p_en`(決定論)、E3=`gpt-6-luna`(web無し)。v4どおり独立2推定の共通部分のみ受理(V4)。Trial内比較として取得根拠を加えたEXT、診断用の和集合DIAG_UNIONも比較 | `..._est.py` `..._replay.py` |
| §2-3 取得・推定発音での自動判定、既存HR音声で検証、正しい発音を不当NGにしない、明確な誤発音をPASSさせない、根拠区分維持 | 保存ASR転写+保存attempt音声86本+ローカルWhisper small/medium へreplay。根拠区分(OFFICIAL/ACTUAL_USE/ESTIMATED)とidentity注記を保持。誤PASSは負例(制御読みの実TTS)で検証 | `..._replay.py` `..._attempts_replay.py` `..._p2.py` |
| §2 末尾 推定発音と音声の一致だけで無条件に正解としない | v4の`ESTIMATED/WARN`区分維持、PASS_WITH_WARNINGは「誤発音の機械検出」であり正解の保証ではない旨を結果に明記。OOVのASR語はCMU無しのため判定不能=HR維持(近似しない) | RESULT §3-4 |
| §3 対象7語、保存データ再利用、必須測定(母数・HR到達件数・発音不良/ASR誤認識の区別・取得/推定語数・自動PASS件数・誤PASS・改善前後HR・量産単価)、延べlookupと独立音声の混同禁止 | O0で「HR事象(segment)/延べlookup/独立音声(保存最終wav・attempt wav)」を別カウント。区別は機械的な候補ラベル(確定は人の耳) | `o0_population.json` RESULT §2 |
| §3 試聴ページ | `user_test/pnps_stage2_hr7_listen_01/index.html`(音声はコピー、再生しない文字だけの表示はしない) | ページ+Playwright再生検証 |
| §4 改善ループ(初回効果が小さくても終了しない) | 本巡はStep A(語×音声単位の原因分類+証拠)まで。Step B(Opus)・Step CはFableが手配。改善見込みの高い代替案を事実から最大3つ | RESULT §5 |
| §5 費用 累計300円、O0最大活用、並列、少額ごとの承認不要 | 有料はE3(約0.3円)とP2(実TTS+ASR、数円)のみ。`paid_calls.jsonl`に単価出典付きで記録 | `paid_calls.jsonl` RESULT §6 |
| §6 STOP: 誤PASS 0/虚偽登録0/Production無断変更0/正式Ledger登録0 | 正式Ledger(`ledger.json`)は読み取りのみ・書込0。Trial成果は`er100_output/`のみ。Production module編集0 | git diff範囲 |
| §7 最終報告順 | RESULTを§1〜8順(5はStep Aまで、7・8はFable欄) | `STAGE2_TRIAL_RESULT_01.md` |

## 2. 構成と順序

1. O0(0円): HR queue 113行から、辞書外7語の延べlookupを持つ行を抽出(`pronunciation_lookups`のキー)。独立音声=保存最終wav(sha256別)+保存attempt wav(ER-011保持、sha256別)。保存ASR(Primary/Secondary)に加え、ローカルWhisper small/mediumを追加転写。
2. 環境: `.venv\Scripts\python.exe -m pip install g2p_en`(Trial専用。Production importに入れない)。
3. O1(0円): 7語×(Wiktionary/Wikipedia/Wikidata/既存調査履歴の出典URL)をGETのみ(`er097.default_fetch`再利用: サイズ上限・タイムアウト・redirect毎検査・読み取り専用)。
4. 推定: E1は明示的境界を持つ語が無くN/A。E2(G2P)・E3(`gpt-6-luna`)。
5. replay(0円): 各ASR観測の対象語spanをdifflib整列→CMU(異読すべて・ストレス除去)→許可集合との完全一致で判定。複数観測は「Production ASR(Primary+Secondary)が全てMATCH/EXACT」でPASS_WITH_WARNING、1つでもMISMATCH(かつOOVなし)でNG、それ以外はHR維持。別世代のWhisperは判定に使わない(参考)。
6. P2(有料・少額): (a)綴りどおり×2サンプル(7語)、(b)制御読み(合理的1+明確な誤発音2)×3語、いずれも実TTS(Gemini 3.8 flash-lite TTS、Family X現行style、STANDARD同期)→Primary/Azure/Whisperで転写→同じ判定。
7. 試聴ページ・Gate 7再生検証・RESULT・SSOT。

## 3. 判定arm(Trial内比較のみ。承認済み条件は変更しない)

- **V4**: v4の受理条件そのまま。E2(G2P)∩E3(LLM)の共通部分(音素列完全一致、ストレス除去後)。
- **EXT**(Trial内の拡張比較): V4に、(i)許可リスト源(Wikipedia/Wiktionary/Cambridge)で同定が確認できた発音、(ii)同定確認済みの独立2ドメイン以上が一致した媒体ガイドの発音、(iii)単一サイトの発音がE2/E3のいずれかと一致、を加える。許可リストの拡張・媒体合意の扱いは承認済み仕様(出典階層)の変更案であり、**採用はユーザー判断**。
- **DIAG_UNION**: 全候補の和集合。誤PASS余力の診断のみ(採用候補ではない)。

## 4. 既存仕様との整合・撤去
- 照合: `PLAN_SUMMARY_01.md`v4節(受理条件・ESTIMATED/WARN・非独立性の開示)、`PLAN_01.md` v4-1〜v4-6、`CURRENT_SPEC.md:1837(B)`(Ledger情報は自動PASSの根拠にしない=本Trialは変更せず比較のみ)。
- Production経路へのimport: `er097`の`default_fetch`/`html_to_text`/`_words`(読み取り純関数)、`er006_m1_multi_candidate_01`の`ipa_to_arpa`/`default_cmu`(純関数)のみ。`er098_kp_six_model_trial_01_common`は費用計算・API呼出の部品(Trial module)。書込は`er100_output/`のみ。
- 撤去する旧規則: なし(新設のみ)。
