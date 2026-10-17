# M1「Melos said.」受理のオフライン監査 (FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15 W6, Opus R-C6)

- 性質: JPY0・API呼出0・Production非接続(読み取りのみ)。script=`m1_melos_said_audit_01.py`、結果=`m1_melos_said_audit_01.json`。
- 対象: `er026_post_slowdown_cascade_rescue_01_test_01.py:61-67,217-221`・`er026_cs_audit_regression_01_test_01.py:149-152` の入力(canonical「Melos said.」、Primary「Mello said.」、Azure「Mellow said.」/「Melo said.」)が、既存FAIL 7件でM1に受理される理由。

## 取得した受理経路(live Ledger snapshot、M1 ON)
| 項目 | 値 |
|---|---|
| 判定 | `M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING)。Primary「Mello said.」・「Mellow said.」とも受理 |
| 一致候補の出典クラス | `C2_ledger_alt`(Ledgerのalternate_pronunciations、confidence=low) |
| 一致候補音素 | M EH L OW S(`/ˈmɛloʊs/`) |
| 適用規則 | `drop_final_S_or_Z`(Pattern A: 語末sの脱落。次語 said の語頭Sと融合) / 置換 mello->melo(canonical_word=melos、entity_like=true) |
| ledger_key | `ec716e185835dba3`(surface=melos、entity_type=`cascade_unresolved_entity`、canonical_spelling=Melos、sources=Cambridge/Wiktionary/Collins/Dictionary.com等10 URL、updated_at=2026-10-12T13:17:58) |
| F1説明 | `_post_check`: 置換後文でF1残差0、かつ置換(melos,melo)がF1 `f1_explained`(Pattern A)に含まれる。F1のbenign(規則単複)で吸収された置換は不受理 |
| CMU | `melos`はCMU未収録(C1候補なし)。`mello`/`mellow`は同一音素 M EH L OW |
| ASR由来の値か | **否**。候補はLedger(pronunciation research由来のIPA、URL出典あり)だけ。ASR転写は候補に入らない(M1設計: C3・ASR後付け候補は存在しない) |

## 再現性(testがFAILした直接原因)
- Ledgerのmelos entry(`ec716e185835dba3`)は**HEAD(commit済み)の`er006_output/pronunciation_ledger_01/ledger.json`に存在しない**(`git show HEAD:...ledger.json | grep -c ec716e185835dba3` = 0)。作業ツリーの未commit追記(2026-10-12のZ E2Eで本番cascadeの`_resolve_unresolved_entity_for_review`が追記)により存在する。
- 空Ledger(M1 ON・CMUのみ)では `MULTI_CANDIDATE_NO_MATCH(no_candidates_for_canonical_word)` で不受理=旧testの期待値(STOPPED/UNCERTAIN)と一致。つまり旧testは「M1導入前の承認済み境界」を記録しており、結果が作業ツリーのLedger状態に依存して変わるのは再現性の欠陥だった。

## 判定: (α) 承認範囲内
- M1は2026-10-13にユーザーが承認済み(ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01: CMU未収録語の複数の合理的な発音候補[Ledger由来C2]のいずれか1つで音韻整合しF1で説明できればPASS可。`er006_m1_multi_candidate_01.py:1-16`)。今回の受理はその設計どおり(Ledger C2候補+F1 Pattern A[語末s+語頭sの融合]で説明可能、出典あり、segment開始前に作成済み、ASR由来でない)。safety問題ではない。
- 注意点(Fableへの判断材料。判断候補ではなく事実): (1) 候補のconfidenceは`low`で、alternate IPA `/ˈmɛloʊs/`の出典文言は「音楽用語・一般名詞としての英語の別読み」(ギリシャ人名Melosの読みではない)。M1の仕様上は許可(confidence下限の規定なし、audit記録あり)。(2) 実際にTTSが「Mello said」と読んだ(sを落とした)場合と、「Melos said」で語末sが次語頭sと融合した場合は音韻上区別できない。これはM1+F1 Pattern A承認の本質的な性質。(3) Phase 3でStd part1_c5「Melos said.」がM1ON+Ledger entry保持で`M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING)になり得る(HR発火予想が外れる可能性)。Ledger entryは作業ツリー未commit追記のため、Phase 3実走前にentryの保持(commitするか)をFableが決める必要がある。
- 是正(実施済み): 旧7件のFAILはLedgerを固定fixtureにしたM1 ON/OFF 2系統へ期待値更新(M1 OFF=旧testの期待値を既定で維持、M1 ON=`M1_LEDGER_FIXTURE`[上のentry相当]を`pronun_ledger._load`のmockで注入)。更新したtest: er026_post_slowdown_cascade_rescue_01_test_01(module setUpでM1 OFF既定、`m1_on()`追加3test)、er026_cs_audit_regression_01_test_01(同、追加4test)。Productionコード・M1は無変更。
