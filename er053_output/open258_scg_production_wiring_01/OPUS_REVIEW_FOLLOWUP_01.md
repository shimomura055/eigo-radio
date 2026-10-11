# OPUS_REVIEW_FOLLOWUP_01 (是正内容とユーザー判断事項)

## 1. 是正内容(実装済み、branch `feature/scg-ja-secondary-01`)
| 項目 | 変更 | 場所 |
|---|---|---|
| 必須1(C1) | SCG除外に追加: content_diffsに`reading_dictionary_mismatch` / `entity_like` / 原稿側ラテン文字がある場合はNOT_APPLIED(理由code: `reading_dictionary_mismatch:`/`entity_like_diff:`/`latin_in_canonical_diff:`) | `er007_ja_secondary_asr_01._scg_exclusion_reason` |
| 必須2 | SCG専用`_azure_stt_strict`を新設。`canceled`イベントで`cancellation_details.reason==Error`(または詳細取得不能=保守側)ならtext=None+error=UNAVAILABLE(従来動作へ戻す)。EndOfStream=正常。共通関数`p4.get_full_text_via_azure_stt_continuous`は無変更(従来のCascade/他経路も無変更) | 同上 |
| 必須3 | 本番条件のPhase 0回帰`ProductionConditionRegression`(Resolver ON+LLM mock、expected_readings指定、除外は実装関数で算出、25行) | `er007_ja_scg_phase0_regression_test_01.py` |
| 推奨5 | `classify_ja_asr_match(allow_reading_resolver=True)`追加引数(既定True=従来)。SCGのSecondary判定のみFalse | `er007_ja_asr_validator_01.py` |
| 推奨6 | `evaluate_attempt_ja_with_cascade[_detail](length_ok=True)`追加(既定True=後方互換)。呼出元4か所が`length_ok=length_ok`を渡し、False時はSCG NOT_APPLIED(`length_not_ok`)でAzure不呼出 | secondary_asr / repro01 / n3 / voice01 |
| 推奨7 | master store manifestに`audio_classification`・`scg_result`を追加(既存キー不変) | `er006_master_audio_store_01.py` |
| 推奨8 | 下記注記 | 本ファイル/RUNTIME_EVIDENCE_01.md/RESULT_PACKET |

### 推奨8の注記(必読)
SCG PASSの「NORMALIZED_MATCH」には、`classify_ja_asr_match`の既存承認済み正規化(`normalize_ja`、variant layer Candidate C: カタカナ語末長音省略[4文字以上]、D-1: 位取り漢数字の算用数字化 等)による一致が含まれる。SCGはこれらを新規に緩和しておらず、Secondary(Azure)の転写が既存のEXACT/NORMALIZED判定を満たした場合のみPASSとする(PHONETIC_MATCHは自動PASSに含めない)。

### 是正で判明した副作用(Fable要確認)
- Phase 0の救済14件のうち **g8(「熟すと出るガス」、Primary「じくすと出るカス」)がC1(entity_like: ガス->カスのカタカナ同士差分)でSCG対象外になり、本番条件の救済は14件->13件**。C群NG 5件は不変(誤PASS 0)。g8は従来どおり再生成へ戻る(誤PASSなし、救済機会のみ減)。除外の絞り込み(例: 濁点のみ差のentity_likeは対象に残す等)は新しい仕様判断のため実装していない。
- Phase 0の他の13件はC1後もSCG PASSのまま。

## 2. ユーザー判断待ち(未実装)
### C2: 同形異音語ガード
- 何を厳しくするか(設計案): 原稿とSecondary転写が一致していても、原稿側に「同形異音語(例: 行った/行った[おこなった・いった]、日(ひ/にち)、生(なま/せい)等)」の読み曖昧語が含まれる差分位置では、表記一致だけでPASSとせず、Azureの読み(あれば)または既存読み辞書で読みが原稿の期待読みと一致することを追加確認し、確認不能ならNG(従来の再生成)へ戻す。
- 影響: 誤PASS(文字は合うが読みが違うTTS)をさらに減らせる。救済は同形異音語を含む差分のみ減る(Phase 0の救済13件で同形異音語差分があるのは要確認、現時点の実測なし)。実装は読み辞書(`er008_asr_variant_hardening_15_ja_kanji_readings`)の利用が中心で、追加のAPI費用は不要(¥0見込み)、実装規模は中。
- 判断事項: 採用/不採用。採用する場合は別管理IDでの設計・Phase 0再回帰が必要。

### 推奨4: SCG除外への否定マーカー追加
- 何を厳しくするか: 現行の否定差分除外(`protected_check_ja`の`negation_mismatches`)は「縛られず->縛られる」の「ず」を検出しない(Phase 0実測)。SCG除外にのみ、Primaryと原稿の差分周辺に否定マーカー(ず/ません/ぬ/ざる/まい)が片方だけにある場合はSCG不実行とする。
- 影響: g12型(「縛られず自由に」を「縛られる」と読む)はSCG自体が実行されなくなる(現状はAzureが「縛られる」と返してNG=結果は同じだが、無駄なAzure呼出約0.2円/回が省ける)。Secondaryが原稿寄りに丸める最後の砦が否定検出のみという残余リスクを減らす。Phase 0 fixture 25行をマーカー差(原稿とPrimaryで有無が異なる)で照合した実測: 該当は g12(NG)と g23(NG、Primaryに「まい」が混入)のみで、救済13件には該当なし=救済数は不変(g23はAzure呼出が省ける)。
- 費用: 実装は無課金test。Azure呼出は減る方向。
- 判断事項: 採用/不採用(既存の否定検出自体の変更はスコープ外、SCG除外にのみ追加)。
