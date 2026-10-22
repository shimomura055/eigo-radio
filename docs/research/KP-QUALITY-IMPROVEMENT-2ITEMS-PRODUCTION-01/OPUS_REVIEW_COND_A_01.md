# OPUS_REVIEW_COND_A_01(逐語保存。委任_02 §6より。2026-10-22)

## Opus独立レビュー KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01(OPEN-458)条件A

### 1. 総合判定: 条件付きGO
設計の骨格は妥当です。判定はjudgeとer104の1箇所に集約されてX/Z両方に効き、Store再利用での判定は単調(旧PASS⊆新PASS)、②は選定段とcanonicalization後の2段で確認します。ただし次のMajor 2件を配線前に直す必要があります。
- OF-KPQ-P-01: G9をlabelで判定すると、A/B/CのKP英語の保護まで外れる。
- OF-KPQ-P-02: M2でNGになった後、不適合なKPファイルがディスクに残る。

もう1点、項目①を実装しても「a2型」の停止(coffee a2最終wav)は残ります。これは①の範囲外の仕様追加なので、ユーザー判断事項として報告に明記してください(§4)。

### 2. 各論点の判定

**Q1(AMBIGUOUS降格の維持)— GO**
- AMBIGUOUSは「数値の不一致」ではなく、1票ごとのPASS/NG分類の一部です(S票はsame_surfaceを要求、Whisperは`ambiguous_blocks`)。多数決より優先してNGにする効き方ではないため、ユーザー文言には抵触しません。
- 保存データでもA=Bでした。SSOTには「AMBIGUOUSは票の分類として維持(保護解除の対象外)」と明記してください。

**Q2(Primary自身の保護差による短絡も解除)— GO**
- 「NG/PASS→Whisper」の行を例外なく適用するには必要です。
- 追加されるAzure呼出は、Primary NGかつ自身に保護差がある稀なケースに限られます。非保護のPrimary NGは従来からP3でAzureを呼んでいるので、増分はこのケースだけです。
- 注意: P1を外すと、該当ケースでP2除外(`_exclusion_hit`)が評価されるようになります。これは数値・否定の保護ではないので維持で正しい扱いです。testに1件加えてください。

**Q3(er104へ折り込み・version `kp_vote_check_v1`据え置き)— GO**
- reuseは毎回現行judgeで判定し直します(`kp_vote_reuse_ok`)。古い証跡を新規則で誤受理する経路はありません。
- `secondary.protected_diff`を読むProductionコードは`vote_check_from_audit`:411だけでした(Grepで確認)。
- `guard_lifted`と`guard_lifted_version`を加算形式で残せば区別できます。stagingの`CHECK_VERSION="kp_vote_check_v2_noguard"`は折り込み時に`guard_lifted_version`へ移してください。

**Q4(G9のKP skipをlabel判定1関数で行う)— NO(代替が必要)→ OF-KPQ-P-01**
- Store呼出(`er006_master_audio_store_01.py:130`)のlabelは`"master:"+style_instruction_id`です。A/B/Cの`shared.ensure_key_phrase_english_component`(`er003_v1_n3_01_tts_generate.py:1170`ほか)も同じ`style_instruction_id="key_phrase_english_component"`で、reuse_gateはありません。labelでskipすると、vote gateが後に続かないA/B/CのKP英語再利用から保護が完全に外れます。
- vote無効時(rollback)も同じで、K2のStoreは`reuse_gate=None`になります(`er019_family_x_kp_en_k2_store_01.py:86,116`)。
- 代替: `guard_entry`に明示引数(例: `kp_vote_gate_follows: bool`)を足し、4つの呼出元から渡します。
  - Store: `reuse_gate is not None`
  - X前回results: `role=="english" and kp_vote.vote_enabled()`
  - X引継ぎ: `kp_vote_required`
  - Z: `spec.kind=="kp_en" and kp_vote.vote_enabled()`
- 呼出元の変更は各1行です。「呼出元は無改修」という前提は捨ててください。
- 追加test: A/B/C keyのentryでPrimaryに値DIFF→引き続きblocked。vote無効でも引き続きblocked。`reuse_blocked`のmarkは引き続き尊重。

**Q5(CMU照合の正規化)— 条件付きGO**
- R3(ハイフン分解): TTS入力も`tts_safe_kp_en`でハイフンを空白にするため、語単位照合と整合します。GO。
- アクセントと語形変化を救済しない判断: 原文の「推測・外部辞書で代替しない」に忠実です。GO。
- R4(縮約・所有格のclitic分解): 句読点等による誤除外の防止として解釈できます。ただし規則による分解なので、SSOTに明示してください。census(調査で集計した保存KP全数)でのR4発火は0件(whole 1425/stripped 3/hyphen 2)で、実害は小さいです。辞書照合だけで説明できる形が望ましいので、clitic側(`'s`等)もCMU登録エントリであることを`lookup`で確認する形を推奨します(OF-KPQ-P-07)。

**Q6(最終attemptでの除外確定と、canonicalization後NGの非対称)— GO**
- 2回目でLunaにCMU不適合を明示したうえでの除外です。数は埋めず、件数は既存の1〜3件可変の範囲に収まり、rankも`build_original_items`で1..nに振り直されます。
- M2は後段(gloss・Redundancy前)のため、除外ではなくINVALIDとする方が単純で安全です。保存2,130件で発火は0件でした。
- ただしM2側の配線にOF-KPQ-P-02の修正が必要です。

**Q7(S+W行=Primary NG・Azure PASS・Whisper PASSの増加と事後試聴リスト運用)— GO**
- 偽PASSになるには、AzureとWhisperの両方が正解側へ聞き違える必要があり、確率は低いです。
- 事後試聴リストの行に`observed_protected_diff`を表示して優先確認できるようにすることを推奨します。
- 合成の誤転写データは数値系が9件しかありません。数字同士(2↔3)、序数、`1's`などの数値ケースをtestに追加してください(費用0、OF-KPQ-P-10)。

**F1(a2型の残存とAzure lexical形の利用)— ①の範囲外で、ユーザー承認が必要な仕様追加と判断**
- ユーザーが述べた停止のしくみ(「1's→保護差→Whisper不呼出」)は①で消えます。b1b最終wavのHR原因は解消します。
- a2最終wav(N1#4)は、Primaryも`'s`を落としてNGです。両NG=NGはユーザー自身の真理値表どおりなので、①で救済すれば承認内容を超えます。
- 技術評価(C1: Azureの判定にlexical形も使う):
  - 方法: `OutputFormat.Detailed`の`NBest[0].Lexical`を取得し、期待KPに数字が無いときに限り、S票を「表示形と同じ受理判定でPASS、またはlexical形でPASS」とします。
  - 追加API: 0(同じAzure呼出の出力形式だけ変える)。
  - 偽PASSリスク: lexical形はITN前の認識結果そのものなので、表示形と同程度で低いです。ただし数字の読み下し、略語(`u s`)、`mister`などで表記が変わるので、OR結合と数字なしの条件が必要です。
  - 規模: er006のrecognizer設定とoutcome、cacheの値、judgeの受理判定、監査、testで数十行程度。Store内の旧証跡にはlexical形が無く、表示形のまま判定されます(単調なので問題なし)。
  - 共有影響: `evt.result.text`は変わらないため、非KPへの影響は「取得するだけ」に限られます。
  - 実効性の確認: coffee wavで本当に`one's`が返るかを1回のTrial(約1円)で確かめる必要があります。
- 区分: 承認済みのASR判定の入力定義を変えるので、AZURE_ITN_IMPACT_01の分類どおりユーザー承認が必要です。DEV経路でVALIDATEDまで進めてから採用を判断する流れになります。
- ①のPRODUCTION_WIREDはこれを待たずに進めて構いません。

**F2(撤去範囲の漏れ・過剰)— 条件付き**
- G1〜G9でほぼ網羅しています。`er078.NG_PROTECTED`を残すのは正しいです。
- Z(`er063`)、X前回results、X引継ぎはいずれもvote_requiredの統一judgeとG9を通るので、P-01を直せば保護解除が効きます。
- 漏れ1: `er104_kp_vote_wiring_test_01.py:309`の`kp3v.NG_PROTECTED`(judgeとdecideの一致test)が更新一覧にありません。
- 漏れ2: `er019_family_x_validation_inheritance_01.rebuild_state(rejudge_f1)`:461は、KP英語のlabelもvoteなしのjudgeで判定し直すため、S+W行を拒否し得ます。KP3Vで整理した再利用6点の外にある既存のすき間です。Production経路として扱うかを決め、扱うならvote reuseを通すか、対象外とSSOTに記録してください(Minor)。
- 漏れ3: `er078_auw_reuse_bulk_rejudge_06c.py`を再実行すると、KPのS+Wのentryに`reuse_blocked`が付き得ます。運用注記で足ります。

**F3(Store再利用とWhisper失敗時の挙動)— GO**
- `+vote1`はPASSしか保存せず、P PASS/S NGのものは`PASS_VOTE_2OF3`で、保存済みのWhisper転写があります。したがって保存音声にローカルWhisperを走らせるのは、主にS1(証跡なし)の場合に限られます。
- Whisperが失敗すると`ACTION_TECHNICAL_STOP`になり、再利用も再生成もしません。再生成ループは発生しません。
- coffeeのentryはstatusがOKでないため、そもそも再利用経路に入りません。HR Lockも自動では解除されません。①-R2は「本番関数による再生」と位置づけるのが正確です。
- 既存の軽微な問題: Storeは、Whisperが原因の技術STOPでも`TECHNICAL_STOP_SECONDARY_UNAVAILABLE`と表示します(:153)。

**F4(②の挿入点M1/M2)— 条件付き → OF-KPQ-P-02**
- noteはPrompt本文の後ろに置かれ、`prompt_prefix_intact`のassertで本文不変が保たれます。
- ループはer105で2回、外側で通算3回が上限で、無限ループはありません。空のKPは、M1では`min_keep=1`、残り0件ならINVALIDで防がれます。Z D1 gate、gloss、解説への影響はKP件数が可変になる点だけで、既存仕様の範囲内です。
- 問題: M2でNGになったとき、canon_fnがPASSとして書いた`keywords_canonicalized.json`(CMU未登録のused_formを含む)が本名のまま残ります。`_kp_retire_stale_artifact`で退避されるのは上限到達時だけです。次の周の冒頭でSTOPセンチネルを確認した時点、あるいはクラッシュで止まると、X TTS段の再開時(runner:933/:1340)がそのファイルを読みます。
- 対処: M2でNGになった時点で即座に退避し、次の周のnote用変数(cmu_note)もNGごとに作り直してください。
- scaffold再実行時の再開条件は、委任_02での確認ではなく配線前に確定させてください。

**F5(runtime evidence計画)— 条件付き**
- 線引き(mockによる再生はtestの証拠でありruntime evidenceではない)は妥当です。
- ただし自然発火しない可能性が高いので、次の2点を加えることを推奨します(OF-KPQ-P-08)。
  - (a) 正式runの全KP vote記録に`guard_lifted`、全選定metadataに`cmu_gate`が付いていることを、配線の証拠として集計する。
  - (b) ①について、正式入口(X)で`pump one's fist`のKP英語を新しいout_dirで実際に生成する。Azureは8/8で`1's`を返しており、Storeにもentryが無いため、自然発火が見込めます。費用は数円です。

### 3. must-fix / recommended
- **OF-KPQ-P-01 Major**: G9のskipを、呼出元が渡す明示引数(vote gateが後続するか)に変える。A/B/C、rollback、Z/Xの非KP labelでは保護を維持するtestを付ける。
- **OF-KPQ-P-02 Major**: M2でNGになったら`keywords_canonicalized.json`を即座に退避し、CMU noteを次の周へ確実に渡す。再開経路を配線前に確定する。
- OF-KPQ-P-03 Minor: 撤去対象とtest更新一覧に`er104_kp_vote_wiring_test_01.py:309`を追加する。er107ページの説明文が古くなることも注記する。
- OF-KPQ-P-04 Minor: label判定を残す場合は完全一致にする(`kp\d+_en`の前方一致は使わない。`kp1_explanation_en`等と区別するため)。P-01を採ればこの点は不要になる。
- OF-KPQ-P-05 Minor: KP段の開始時にCMU辞書のpreflightを1回行い、API支出の前に辞書不備で止める。`lexicon_info()`(cmudict 1.1.3、エントリ数)をmetadataに記録し、versionを固定する。
- OF-KPQ-P-06 Minor: P1を外したことでP2除外が評価されるケースのtestを足す。
- OF-KPQ-P-07 Minor: R4(clitic分解)をSSOTに明記し、clitic側もCMUエントリで確認する形を推奨。
- OF-KPQ-P-08 Minor: runtime evidenceにF5の(a)(b)を追加する。
- OF-KPQ-P-09 Minor: `rebuild_state(rejudge_f1)`のKP英語の扱いを決めて記録する。bulk rejudge scriptの運用注記も入れる。
- OF-KPQ-P-10 Minor: 事後試聴リストに`observed_protected_diff`を表示する。数値系の合成誤転写testを拡充する。

### 4. ユーザー判断が必要な事項
- **1件**: a2型(Primaryが`'s`を落とし、AzureがITNで`1's`→両NG)の残存への対処。推奨はC1(Azure lexical形をOR結合で併用、期待KPに数字が無いときだけ、API追加0、Trial約1円)です。
- 技術的には「①の実装詳細」ではなく、承認済みASR判定の入力定義の変更にあたるため、ユーザー承認が必要です。
- ①・②のPRODUCTION_WIREDはこれを待たずに進めてよいと考えます。最終報告では「b1b型は解消、a2型は残存」と明記してください。

### 5. 品質・速度・単価への影響見積の妥当性
- ①: 偽PASSの増加0は保存84件で裏付けがありますが、数値系の母数は小さいです(数値を含むKP 11句、合成9件)。追加費用は、Azureが稀なケースで1回/件、Whisperはローカル(CPU数秒)で、ほぼ0円です。HRは減る方向で、この見積は妥当です。
- ②: 未登録率2.9%/句、追加のLuna呼出0.08回/レベル(約0.2円)は妥当です。品質面では、最終attemptでの除外によってKPが3件未満になるケースが一部出ます(推定8%弱のレベルでCMUに該当し、その大半は2回目で解消)。件数は既存の可変仕様の範囲内です。M2による外側retryは、canonicalizationとglossを再実行するため1回あたりは高めですが、頻度はほぼ0です。
- runtime evidenceの40円以下は、F5(b)を加えても数円の増加で、範囲内に収まります。
---