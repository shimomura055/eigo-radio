# OPUS_REVIEW_A1_CONDC_01: A-1 Production配線設計(WIRING_DESIGN_01)に対するOpus独立技術レビュー(条件C)本文(逐語)

出典: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-aabcc38e75d54c8b1.jsonl` 147行目(0始まりindex 146)、assistant SubagentHandback tool_use の message。timestamp=2026-10-23T09:19:21.994Z、uuid=e6bf1977-716e-40b2-a9ef-8ab1091e597a。主セッション側の受信記録=a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl index 12869(uuid 1b582bfc-ce96-4be3-8110-aa4bec104f3e)。依頼文マーカー=FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-OPUS-REVIEW-COND-C-WIRING-20261023。復元は委任_24(2026-10-24)。以下は無加工の逐語。

---

## Opus独立技術レビュー(条件C) A-1 Production配線設計(WIRING_DESIGN_01)

### 総合判定
**必須修正後に実装可。** 再設計は不要。

- 配線経路の主要部分は正しい。X/Zとも`n3 scaffold :485/:499`の共通経路を通る。fulltext専用enumにのみ追加する点、reasonゲートの変更が:502の1箇所で足りる点、`_PERSON_DEPENDENT_TO_GENERIC`表を拡張しない点も妥当。
- ただし、次の4点を直さずに実装すると、回帰が失敗するか、品質ガードが設計書の記述どおりに働かない。
  - template内の`the`の扱いが不整合(W-01)
  - CMU判定関数の置き場所が既存の隔離testに違反(W-02)
  - 「置換しない」条件の一部をvalidatorが実際には却下しない(W-03)
  - test計画に漏れがある(W-04)

### 必須修正

**OF-KPGM-W-01 [必須] `the`の扱いがtemplateとvalidatorで不整合**
- 根拠: validatorは`{a, an}`のみを許可し、`draw the line←draw that line`を否定ケースにしている(ITERATION_LOG #1、WIRING付録A)。一方、Trialのtemplate差分`er112_kp_gm_trial_01.py:127`(qa (e)の文)と`:132`(reason説明)は「this/that→a/an/the」のままである。今回の依頼文にも「[慣用句見出し形がtheならthe]」とあり、これは既に撤回されたOPUS_REVIEW_01 OF-03(1)の記述。
- 影響: そのまま移植すると、PromptがLLMに`the`を促し、validatorが却下し、canonicalization全体がINVALIDになる。外側retryを消費し、最悪は`OUTER_RETRY_EXHAUSTED`(fail-closed)に至る。
- 修正案:
  - T5/T7の文言はa/anのみにする。
  - template内容testに`assertNotIn("a/an/the")`を追加する。
  - SSOT・委任文の仕様記述も「a/anのみ(theは不可)」に統一する。

**OF-KPGM-W-02 [必須] CMU判定をkcへ置く案は既存の隔離testに違反する**
- 根拠:
  - `er108_kp_cmu_lexicon_gate_01_test_01.py:320`は、er108をimportしてよいファイルを`{er105, er003_v1_n3_01_scaffold_generate}`に限定している。目的はA/B/CでCMUを使わないこと。
  - kc(`er003_key_words_canonicalization.py`)はA/B/C共有moduleである。
  - er108は登録の有無(bool)しか公開しておらず(`:45-48`)、音素を返すAPIがない。
- 修正案:
  - `reference_pair_ok`はer105に置く。er105はfulltext専用で、既にer108をimportしている。K5も同じファイル内で完結する。
  - 音素判定helper(例: `first_phone_is_vowel`、`pronouncing.phones_for_word`を使用)はer108に追加する。er108のimport許可set(`:118`)の範囲内で収まる。
  - kcの変更はenum(:120)とreasonゲート(:502)だけにする。
  - CMU辞書にない語は`False`(不許可)とする。理由は、M2の`cmu_post_canon`がKP全語のCMU登録を要求するため、er112の綴り簡易規則は本番では効かない上に安全でもないから。辞書が使えない例外は送出する(fail-closed)。
  - 複数発音がある語は「いずれかの発音が一致すれば可」とする。

**OF-KPGM-W-03 [必須] 「置換しない」条件の一部をvalidatorが決定論で却下しない**
- 根拠: er112の`_ref_pair_ok`(:238-259)と`_DEM_FOLLOW_BLOCK`/`_UNCOUNTABLE`(:188-200)をそのまま移植すると、次のケースが受理される(コードを読んでの判定)。
  - `not that bad→not a bad`: `bad`がブロック語にない。
  - `between you and me→between someone and someone`: youは既存の人称表、meは新規ルールで通る。
  - `this year / week / month / weekend / evening…→a year`: 時間名詞の多くがブロック語にない。
  - `that same/other/very X`: ブロック語にない。
  - `take that good advice→take a good advice`: 不可算名詞の判定が直後1語だけ。
- 付録Aは「固定表現…validator却下を合成で確認」と書いているが、現状ではそのtestは落ちる。受入条件「過剰な一般化を防ぐ条件を維持」を決定論で担保できていない。
- 修正案(いずれも受理範囲を狭めるだけで、Trialの肯定ケースは維持される。`ValidatorDev.CASES`で確認すること):
  - (a) 直前の語が`not/all/quite/just/only`や否定縮約形のときは`that`の置換を不可にする。
  - (b) ブロック語に時間名詞(week/month/year/weekend/evening/afternoon/season/四季/decade/century/minute/hour)と`same/other/very/exact/whole/only`を追加する。
  - (c) 不可算名詞の判定を「key内でthat以降のいずれかの語」に広げる。
  - (d) templateの固定表現列挙と同じ閉じた語彙リストを持ち、その範囲内では参照語の置換を却下する。me系(excuse me/beats me/lucky me等)も含める。
  - template側の文字列と、validatorが却下することの両方をtestする。

**OF-KPGM-W-04 [必須] test計画の漏れと、回帰の対象範囲**
- (1) `er003_test_kp_fulltext_wiring_01.py:216-219`(`set(enum)-{"lemma_normalization"} == set(NORMALIZATION_REASONS)`)は、enum追加で必ず落ちる。計画に記載がない。
- (2) er112のtestは:176以外にも落ちる。
  - `PROD_SRC_HASH`(:20-33)のうち`_is_valid_fulltext_normalization`・`is_valid_inflection_normalization`・`person_generalization_pairs`が変わる。
  - 本番が旧挙動であることを前提にしたassert(:62-63, :66, :69-70, :84)。
  - template anchorが1回だけ存在する前提のassert(:138。置換後は0回になる)。
  - 本番enumにreasonがないことのassert(:151)。
  - 加えて、`install_dev_patches`がtemplateの変化で`RuntimeError`を出し、enumも二重追加になるため、er112は使えなくなる。
  - 修正案: er112はTrialとして凍結する(Trial系classは「A-1 wired at <commit>」理由でskip)。`test_no_production_module_imports_er112`はer0*系のtestへ移す。A-3の追加Trialが今後必要になった場合はer112の改修が必要になることを記録しておく。
- (3) 既定の回帰patternは`er0*_test_*.py`(`run_project_regression.py:40`)で、er105/er108/er112のtestを含まない。K5はer105を変更するため、配線委任で`--pattern "er1*_test_*.py"`(または3ファイル明示)を必ず実行し、F6基準もpatternを揃えて比較すること。

### 推奨

**OF-KPGM-W-05 [推奨] 設計§3「INVALIDは減る方向」はTrial実績と矛盾する**
- 根拠(TRIAL_RESULT_01:27,43): unit単位のINVALIDはbase_c 1/38に対しA-1 3/42。`bound→bind`はbase 4/6に対しA-1 6/6。retryが起きたunitは3から4に増えた。
- 修正案:
  - 記述を「リスク(OPEN-476と相互作用あり)」に改める。
  - 証拠runでは`outer_retry_log`の試行数をbaselineと比較する。
  - A-1が原因の`OUTER_RETRY_EXHAUSTED`が出た場合は停止して報告する。
  - OPEN-476はDEFERREDのためtemplateは変えない。

**OF-KPGM-W-06 [推奨] 証拠計画の補強**
- (1) `--scaffold-only kp`は選定からやり直す(er019:388「選定+canonicalization+redundancy QA」)。`draw that line`が再び選ばれる保証はない。
- (2) er019:427-431の「KP再生成は1レベル1回まで」との関係を整理する。証拠runは別out-dirの証拠専用であり、記事BのKP再生成回数には数えないことを委任文に明記する。
- (3) 発火の判定はreasonラベルではなくトークン差分(this/that→a/an、him/her/me/us→someone)で行う。reasonゲートは3種のどれでも同じvalidatorを通すため。
- (4) 発火とは別に「配線されたこと」の証拠を取る。保存される`canonicalization_prompt.txt`(n3:487)に規則5が含まれることを確認する。`_canon_meta`(n3:501-508)にtemplateのsha256を記録すると安価で確実。
- (5) 2回試して発火しなければ「配線証拠あり・発火未観測」とし、PRODUCTION_WIREDは保留する。次の自然な本番runを証拠に充てる。
- (6) Xでは変更後のused_formについてKP音声とKP3Vも採取する(+0.3〜0.4円程度)。`a`が弱く発音されたときの照合安定性(§4)は、KP段だけの再実行では未検証のまま残るため。

**OF-KPGM-W-07 [推奨] 記事B(OPEN-467)への影響を事前に共有する**
- KP段を再実行すると3件すべてが選び直されるため、`draw that line→draw a line`だけが変わるとは限らない。
- 日本語意味、説明(5件一括再生成)、KP音声、KP3V、ページがすべて変わりうることを、最終版再提出の前にユーザーへ伝えるべき。
- canonicalizationだけを再実行する既存経路はない。作る場合は新しい経路になる。

**OF-KPGM-W-08 [推奨] A-3は別commitで配線する**
- A-1とA-3は同じ委任内でcommitを分け、証拠runは1回で両方を確認する。回帰の切り分けに有利なため。
- A-3を不採用にする場合、本設計で変わる点はない。
- 採用する場合の追加作業は`_header_for`、PROMPT_SHA256、`er019_..._structure_wiring_01_test_01.py:71/77/155/251`の更新。PROMPT_SHA256が変わるため、全X記事の説明cacheが次回runで無効になる点も記録する。

### 情報(設計どおりで問題なし)

**W-09 reasonゲートを緩く(3種のどれでも可)する設計は妥当。**
- 既存のP-02(4)の思想と一致する。
- QA自己申告値の上書きはtraceable項目だけ(:510)。
- gloss側の人称チェックはトークン基準(`indefinite_person_tokens` :564、`person_reference_mismatch` :205)なので、reasonの付け間違いでは回避されない。
- fulltext itemは常にgloss生成の対象になる(`is_fulltext_gloss_missing`)。
- 任意: `is_person_generalized`(:224)にも新しいペア判定を入れると整合が取れる。

**W-10 人称表を拡張しない構造は妥当。**
- `_CONCRETE_PERSON_EN`(:167)、`_is_valid_person_generalization`(A/B/C経路の:512/:571)は変わらない。
- `lose her job`は`_OBJ_HER_FOLLOW`で拒否される。
- `someone`は`_GENERIC_TOKENS`、a/anは冠詞除外によって`_extra_tokens`(:133-138)から外れるため、`added_content_words`への影響はない。
- G1(`person_generalization_pairs`)は全Family共有なので、W-02と同じ判定関数を使うか、fulltext itemに限定する。実際の影響はほぼ0。

**W-11 A/B/C凍結(§27-3)は既存testでほぼ担保されている。**
- 既存pin: :212-213(schemaとenumのsha)、:292(旧templateのblob sha)。
- K3/K5の変更点にはfulltextのときしか到達しない(:516, :575)。
- 追加推奨: 「A/B/Cのitemでは`draw a line←draw that line`がINVALIDのまま」を確認するtestを1件。

**W-12 Z側のreuse_keyは安全。**
- `er063_family_z_audio_01.py:726-733`は本文textのsha256を鍵にしているため、文言が変われば新しい鍵になり、古い音声が誤って再利用されることはない。
- 説明cacheもused_form基準。
- Xの音声Storeは、runtimeで測る前にコードを読んで確認することを推奨。

**W-13 template規則1(:9)と規則5の関係。** 規則1は句の先頭・末尾の`that`を「除去」としており、`that X`で始まる句では除去と置換の両方が成り立ちうる。Trial済みの文面を崩さないため、変更せず記録のみとする。

**W-14 SSOTへの記録。** JRE 委任_02の決定(目的格は残す、および:261のtest)がA-1で置き換わったことをDECISION_LOGに明記する。配線後にGrepで旧文「列挙外の置換は決定論検証で却下」が規則3の文脈以外に残っていないことを確認する。

### 受入条件1〜6との対応
| 条件 | 判定 |
|---|---|
| 1. X/Z双方の正式経路への反映 | 対応済み |
| 2. retry/fallback/regeneration/resumeとの整合 | W-05で補強が必要 |
| 3. Trial依存がないこと | W-04(2)の対応が必要 |
| 4. Validator・回帰・統合test | W-03とW-04の対応が必要 |
| 5. 正式runtimeでの発火証拠 | W-06で補強が必要 |
| 6. SSOT・Git反映 | W-14 |

費用: 運用+0.05円/記事セットは妥当。証拠runは10円以下に音声分0.4円程度が加わる。いずれも自律実行できる範囲。

### Claude案との一致点・対立点
- **一致**: X/Z共通の経路、fulltext専用enum、reasonゲート1箇所、人称表を拡張しない、外側retryは変えない、`bound→bind`は拒否のまま(OPEN-476 DEFERRED)、PROMPT_SHA256はA-1単独では変わらない。
- **対立・修正**:
  - `reference_pair_ok`の置き場所はkcではなくer105(W-02)。
  - 綴りの簡易規則は使わない(W-02)。
  - 固定表現は「LLMとtemplateに任せる」ではなく、validatorでも却下する(W-03)。
  - er112 testの扱いは:176だけでは足りない(W-04)。
  - 「INVALIDは減る」という見立ては撤回する(W-05)。
  - KP段だけの再実行では音声側と記事Bへの影響を確認しきれない(W-06/W-07)。

Production採用の判断は行っていません(A-1は既にユーザー承認済み。今回のレビューは実装の安全性のみを対象)。
