# DESIGN_02 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02) E2のProduction化の形式案とユーザー判断事項

実測=`TRIAL_02_RESULT_01.md`。Opus条件Aレビュー=`OPUS_REVIEW_01.md`(OF-OOV-01〜06)。Trial module=`trial_direct_ledger_phoneme_01.py`(v2、Production未import)。**本書は設計であり、Production変更・配線はしない(到達上限=VALIDATED)。**

## 1. Trial v2で固定した受理条件(OF-OOV-01/02の実装)
1. 差分が『正準1語→ASR1語』のreplace 1件のみ。置換は揃えた位置の**1か所のみ**(全出現置換は廃止)。
2. 正準語はCMU未収録でM1凍結候補(OF-179: segment開始前、OF-181: sources非空・disabled無・canonical_spelling==surface)のC2候補を持つ。**Ledger confidence=medium以上**(lowは除外)。
3. ASR語はCMU収録で、**代表発音(rank0)のみ**で候補と完全一致。一致音素列は**3音素以上**。
4. 対象role=Tier3と同じ5 role(FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE)。KP・見出し・日本語・未分類は対象外。
5. 置換後判定=既存`classify_asr_match`が should_pass **かつ** F1残差0。最終ANDゲート(値・否定)を元転写・置換後転写の両方に適用。
6. Secondary転写が手元にある経路(forced-secondary、LR v1、A2 fallback)では、OF-183同様、矛盾(protected fail、E2不受理のTRUE_CONTENT_MISMATCH/TTS_FAILURE)で不受理。
7. 追加(Trial実測で必要と判明): **独立エンジンの非矛盾を必須にする(E2W)**。Primary ASR単独の誤り(coal→cool)を受理した実例があるため(`TRIAL_02_RESULT_01.md` §2)。無料のローカルfaster-whisper(既存の同一呼び出し)の転写を『Secondary転写』として渡し、矛盾なら不受理。

## 2. Production化の形式(推奨)
- **M1内の1ルール**(Opus提案どおり)。理由コードは別(例 `M1_LEDGER_DIRECT_PHONEME_ACCEPT`)とし、凍結候補・audit(ledger_key/updated_at/ipa_raw/confidence/candidate_set_hash)・`aggregate_by_ledger_key`・OF-183を共有。独立並列モジュールにしない(ガード条件の食い違い防止)。
- 配線上の注意(実コード確認): 現行の呼出点は `er006_secondary_asr_01.py` の `cascade_eligible = is_entity_like_mismatch or is_homophone_candidate_mismatch` ブロック内(`_m1_try`)。gacha型(小文字のTRUE_CONTENT_MISMATCH)は `cascade_eligible` を満たさずM1自体が呼ばれない。**新しい呼出点が必要**(M1の入口 `_entry_gate` をUNCERTAIN限定のまま、E2ルール専用の別入口を設ける)。Secondary側の `_secondary_accept` にも同様のE2呼出(Secondary転写がTRUE_CONTENT_MISMATCHのとき)は不要(Primary段で受理できればSecondaryを呼ばない=Azure削減が目的)。
- 既存の再試行/fallback/3回上限/LR/HR Lock/Style Gate/Secondary 1回+cache/Primary#2廃止/PhraseList重みは不変。PASS→NG変化なし(受理を足すだけ)。
- **11-7限定例外で入れる場合**(ユーザー承認後のみ): 新コード経路+単一flag読取関数、既定OFF、起動script/.envでONにしない、DefaultOffIsolation型test(flag未設定でAPI呼出0・出力不変・副作用ファイル0)、OPEN_ITEMSへ『承認前・既定OFF』記録、PRODUCTION_WIREDと呼ばない。**Opus条件Cレビューを採用申請前に実施**(重要変更のProduction採用提案前=11-3条件C)。

## 3. 評価(QCD)
- Q: 設計条件を満たす正例は6/6救済、有効負例の誤受理=E2W 0件(E2単独は1件)。残リスク: Ledger読み自体が誤り(二次情報・NAME_IN_CITED_PAGE)かつTTSも同じ誤読をする場合、およびASRの複数エンジンが文脈で同じ同音語に寄せる場合(無効な負例3件が示す、既存全ASR判定と共通の限界)。
- D: gacha型の連鎖(TTS 8回・Azure 8呼出・LR・HR Lock・Style Gate・人間承認)を回避。
- C: 本runで-22.6円。ただし発生頻度は保存データで1/188 run(0.5%) → 期待 0.12〜0.35円/記事(70円目標の0.2〜0.5%)。実装コスト小・追加API 0。**単独の原価インパクトは小さい。主価値はHR Lock/人間承認の連鎖(D・ユーザー手間)の回避。**
- 供給側G(先行登録)は1語約0.94円で、毎記事のCMU未収録語を先行登録すると期待効果を上回りかねない → 非推奨(Gを採るなら E2_ACCEPTABLE_PAIRS_01 を作り直し、別Scope判断)。

## 4. ユーザー判断が必要な点(OF-OOV-05。採用申請時に3点を必ず明記)
1. **E2はTRUE_CONTENT_MISMATCHをPrimaryの判定だけでPASS_WITH_WARNINGにする初めての経路**。M1(UNCERTAINからのみ・F1説明必須)やTier3(Secondary裏付け必須)とは性質が違う。独立証拠はE2Wのローカル非矛盾のみ。
2. **D-2'(Tier3の情報を自動PASSの根拠にしてよい範囲=M1に限る)の拡張が必要**: E2が使うLedger読みは cascade_unresolved_entity(Tier3/HR packageの調査由来)。
3. **統一判定フローの変更**(新しいPrimary層の追加)。
- 加えて: US/UKラベル(一致した読みのUS/UK)をauditに残し、voiceのアクセントと事後照合するか(任意、gachaはUS /ɑ/ に一致)。複数出現(同一正準語×同一ASR語のk件)を受理に広げるか。low confidence許容の可否(meink型の救済 vs 安全性)。OPEN-339(自動登録/人手登録の区別フィールド)との関係。
- **OF-OOV-06**: 確認済み(§5)。

## 5. OF-OOV-06(OF-180の範囲確認、コードで確認)
- `cascade_unresolved_entity` を書く唯一の経路は `er006_secondary_asr_01._resolve_unresolved_entity_for_review`(Stage1/legacy)→`_research`/`research_pronunciations` で、入力dictは `{surface, entity_type="unknown", risk_reason=固定文字列}` のみ。`surface` は `_unresolved_entity_spans(cls)` の `d["canonical"]`(正準側)と PNAP経路の `smap` 変換(正準側)。**ASR転写は調査入力に入らない**。
- OF-180の契約test `er006_m1_multi_candidate_01_test_01.py::test_research_input_is_canonical_side_only` は `er006_secondary_asr_01.py` と `er025_entity_pronunciation_resolver_core_01.py` の `risk_reason` を持つ全dictをAST検査し、(a)キーが surface/entity_type/risk_reason のみ、(b) risk_reason が定数文字列、を強制する。上記書込経路はこの検査の範囲内 → **cascade_unresolved_entity は OF-180 の範囲に含まれる。E2対象からのentity_type除外は不要。**
- 残る選択バイアス(記録): 『どの語を調査するか』はASRが失敗した語に依存する(調査内容[読み]はASR非依存)。自己強化ループの懸念(Opus 3(b))は、読みの内容にASR転写が入らないことで構造的に抑えられている。
