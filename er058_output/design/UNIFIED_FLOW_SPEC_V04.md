# UNIFIED_FLOW_SPEC_V04: 日英共通フロー設計案 v04(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_05B、2026-10-12。v03は`UNIFIED_FLOW_SPEC_V03.md`として残す)

状態: **設計案(Trial/設計限定)**。Production未承認。`APPROVED_FOR_PRODUCTION`は人間ユーザーのみ。Production code/Prompt/Validator/Routing/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSは変更していない(SSOT記録は統合委任で)。
前提: ユーザー確定方針(2026-10-12)と`RECONCILIATION_REPORT_02.md` 5・6・9・10・11章。確定=コード・ログで確認、推測=その旨を明記。
使用モデル(本書の根拠調査): コード読解と保存済み転写の再判定のみ(API 0円)。本書自体にモデル評価は含まない(Trial DとJA LR Trialは別書に記載)。

### v04での変更(Opus総合レビュー2026-10-12の必須修正M1〜M5の反映。委任_05B。いずれも設計案の修正であり、Production変更ではない)
| ID | 修正 | 該当箇所 |
|---|---|---|
| M1 | Secondary PASS集合の不一致を明記(英語Trial B/C=4ラベル、日本語SCG=2ラベル、v03本文=2ラベル)。保存済み転写を2ラベルでオフライン再判定(0円)し併記。「英語4/日本語2」の非対称を選択肢化 | 2-3、9-1 |
| M2 | 数値安全条件S1の穴を訂正(「数値・否定37/37ブロック」は誤り=否定26/26、数値11/15)。日本語S1が`\d+`のみで漢数字を見ない点、表記差(二/2、20%/20パーセント)で発火し正しい音声が3回NG->HRになる点を明記し、S1は「値の不一致」で判定する方針へ | 2-2、2-2b、9-2 |
| M3 | PASS_WITH_WARNINGの試聴リスト連動を共通フロー導入の前提条件に格上げ(連動実装前は有効化しない、または警告をNG扱い) | 2-3、2-6 |
| M4 | force_secondary(minimal経由)撤去で見出し・LR後原稿の保護が外れる点を、ユーザー判断事項として追加(実例: Coffee part2 LR後 `raw bean->robbing`、見出しはminimal文言を通常Styleで使用) | 2-7 |
| M5 | (a) cool-down廃止の効果を「最大約10分/segment」から訂正 (b) 1章の技術失敗/無音の矛盾を統一 (c) Trial D「V4でK2効果が薄れた」を「区別不能(n=1、差0.1〜0.2秒)」へ(KP書v04) | 0、1、2-5、7 |
| C-6強化 | script版あたり3回にすると費用ガード・累積上限・`attempt_history`の計数が変わる点と、LR再TTS未計数(Coffee記録4/実際5)の是正を必須改修として明記。D6(Tier3/CS層とAzureの二重呼出)を費用見積に加算 | 5章C-6、7章 |
| 0円追加確認 | KP 2段目救済実績、LR再TTS関数の中身、Master Storeのminimal混入、日本語minimal leakage、400エラー再試行実績、minimalが残る経路 | 9章(再現: `er058_05b_zero_yen_checks_01.py`) |

---

## 0. 結論(先に・ユーザー判断材料)

| 問い | 結論 | 根拠・条件 |
|---|---|---|
| 共通フローは日英・各roleで成立するか | **成立する(設計上)**。ただし日本語のLocal Rewriteは**未成立**(機械流用不可、別書`JA_LOCAL_REWRITE_APPLICABILITY_01.md`)。日本語はLR無し(3回不合格で直接Human Review)で開始するのが安全 | 5 role(Full Story/Preview/Comment/In One Line/Topic Intro)+Key Phrase(英語Phrase・日本語意味)の全てで「TTS→Primary→Secondary→再生成(同一条件)」は同じ状態遷移で書ける(2章)。差が出るのは(i)Secondary不呼出の安全条件の判定関数(言語別実装)、(ii)LR可否(英語のみ) |
| Key Phraseは4回構成を3回単一Promptに変更できるか | **変更できる(設計上)**。ただし「単一Promptの中身」が未決(現行Minimal / 現行English Lock統合 / K2統合の3案)で、これは新規仕様判断。現行4回構成=ユーザー正式決定(2026-09-01)の変更になる | 3章。Trial D(`KP_K2_VS_EXISTING_COUNTERMEASURES_01.md`)では8語x4版が全てPrimary PASS・非ラテン0・反復0。Prompt全文が長い版は短い版より挙動がK2から離れた(n=1、傾向のみ) |
| LRは最小変更で運用可能か | **英語は現行実装で運用可能(ただし位置づけ変更の改修あり)**。日本語は機械流用すると**必ず失敗する箇所が複数**ある(Gate 7が日本語で常に0.0、NG span特定が日本語で未動作)。日本語は適用範囲・Gate再設計が要る | 4章、`JA_LOCAL_REWRITE_APPLICABILITY_01.md` |
| minimal fallback撤去 | 撤去可能。最初に壊れるのはLR再TTS(L383)とA2/B1/JAの既定引数(2+1=3定数)・静的監査/回帰テスト | `MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_01.md` |
| QCD | Q: 再生成が同一Prompt+Secondary確認になり偽NGが減る(英語。日本語は既にSCGあり)。C: ASR呼出は旧Cascade4段->最大2段に減る一方、Azure呼出は英語で増える。LRは最大1回/segment。D: cool-down(600秒)は**3回目到達時(旧フロー外挿で全callの約5〜8%)にしか発火しない**ため、廃止しても平均では**数十秒/segment**の短縮(最大の600秒は該当segmentのみ)。**導入理由(一時的な不調の回避)を外した場合の対照データは無い**(5章C-7、7章) | 7章 |

---

## 1. 用語と共有カウンタ

| 用語 | 定義 |
|---|---|
| segment | 1つの出力音声単位(例: full_story_part1、comment_2、kp3_en、meaning_3)。`segment_key=(theme, level, segment_id)` |
| script版 | LRで原稿が変わるたびに増える版。`v0`=承認原稿、`v1`=LR後(最大1つだけ) |
| attempt | **音声が返り、評価の対象になったTTS 1回**(無音・無発話区間なし・異常長の音声も「音声不良」としてattemptを消費する。**TTSが音声を返せなかった技術失敗(400/空応答/5xx/429/timeout)だけ**がattemptを消費しない。2-5)。上限: 1 script版につき3回 |
| ASR呼出 | Primary(OpenAI)/Secondary(Azure)。attemptではない(上限なし、ただしASR障害再試行は上限付き) |

### 共有カウンタ(1 segmentで1組、`attempt_history`/Review Lockで永続化)
```
tts_attempts_v0 : 0..3     # 原稿v0でのTTS attempt
tts_attempts_v1 : 0..3     # LR後(v1)でのTTS attempt。LR未発火なら常に0
lr_used         : 0 or 1   # Local Rewriteは最大1回。2回目は禁止
tts_tech_retries_slot : 0..2   # 現在のattempt枠でのTTS技術失敗再試行(attemptを消費しない)
asr_api_retries_audio : 0..2   # 同一音声に対するASR API失敗再試行
tts_total = tts_attempts_v0 + tts_attempts_v1  <= 6   # PASSした時点で終了
```
- **日英・全role共通**(Primary/Secondaryの別でカウンタを持たない)。Primary NG->Secondary呼出は同一attempt内の第2検証であり、attemptを増やさない。
- 現行`PRODUCTION_MAX_TTS_ATTEMPTS=3`(SSOT、CURRENT_SPEC L1692)は「3 = 1 script版あたり」と**再定義が必要**(衝突、5章 C-6)。
- **技術失敗**(TTS 400/空応答/5xx/429/timeout、すなわち音声が得られなかった)・ASR API失敗はattempt外(U-10(a)案、上限付き)。**無音・無発話区間なし・異常長は「音声は得られたが不良」としてattempt消費**(M4反映)。v03は技術失敗の列挙に「無音・無発話区間なし」を含めており、直後の文と矛盾していたため、v04で上記へ統一した(Production現行`generate_*`の`trimmed is None`[発話区間検出失敗]は現状は技術失敗と同じ分岐で処理されているため、実装時は区別して記録する必要がある=新規改修)。

---

## 2. 状態遷移(role/言語共通の骨格)

```
[START v0] -> TTS(slot k=1)
TTS --(tech fail: 400/空/5xx/429/timeout)--> TECH_RETRY(<=2 per slot, attempt非消費) --> TTS(同じslot)
                                             \--(上限超過)--> HR_TECH  (音声不良ではなく技術障害として記録)
TTS --(OK)--> DELIVERY_AUDIO  = trim(+必要なら6%減速 = 案B'。以降の全検証はこの最終音声のみ)
DELIVERY_AUDIO --> SAFETY_QA   (length異常 / 言い淀み・部分反復QA / Repetition QA / 異常長)
SAFETY_QA NG --> ATTEMPT_FAIL(Secondaryは呼ばない: 別扱い。再生成へ)
SAFETY_QA OK --> PRIMARY(OpenAI)    [ASR失敗=asr_api_retries<=2。尽きたらHR_TECH]
PRIMARY PASS --> ADOPT(PASS or PASS_WITH_WARNING)    # Secondary不要
PRIMARY NG --> SECONDARY_GATE
SECONDARY_GATE: 不呼出条件(安全条件、2-2)に該当 --> ATTEMPT_FAIL
                該当しない --> SECONDARY(Azure、Phrase Listなし・原稿を与えない)
SECONDARY PASS集合(2-3) --> ADOPT(PASS or PASS_WITH_WARNING)
SECONDARY NG (両NG) --> ATTEMPT_FAIL
ATTEMPT_FAIL --> k<3: 原稿・Prompt・モデル・Voice・速度を不変のまま再生成(slot k+1) -> TTS
              --> k==3: STAGE_EXHAUSTED(v)
STAGE_EXHAUSTED(v0) --> LR_GATE    # v0で3回全不合格のときのみ
STAGE_EXHAUSTED(v1) --> HR         # LR後も3回不合格 = Human Review(2回目のLRは禁止)
LR_GATE: role in 5 role かつ lr_used==0 かつ 言語で対応済み(英語のみ現状) かつ NG spanを特定できる
         --> LR(最小範囲、4章) -> 原稿v1 -> START(slot1, 同じ共通ループ) ; 条件不成立 --> HR
```
上の流れで**全attemptに同じPrompt/model/voice/速度**を使う。差はLR後の原稿v1のみ(原稿が変わるが他は不変)。最大TTS 6回(3+3)、PASSした時点で即終了。

### 2-1. role x 言語の適用表(提案)
| role | 英語 | 日本語 | LR | Secondary不呼出条件の判定関数 | 備考 |
|---|---|---|---|---|---|
| Full Story(part1〜3・point_one/two) | 共通フロー | (日本語Full Storyは現状なし/要確認) | 英語のみ可(現行5 role) | EN validator(数値・否定・length・disfluency・Repetition QA) | Tier3/CS層(Connected Speech等価)は共通Secondary転写を共有(D6) |
| Preview | 共通 | 共通(Standard日本語) | 英語可、日本語は未対応=HRへ | EN/JA別 | |
| Comment(comment_1〜4) | 共通 | 共通 | 同上 | 同上 | |
| In One Line | 共通 | 共通(要確認) | 同上 | 同上 | |
| Topic Intro | 共通 | (英語中心) | 英語可 | EN | |
| Key Phrase 英語Phrase | **3回共通**(3章) | - | **なし** | EN(非ラテン文字時は特殊扱い、2-2) | 既存対策①②③維持 |
| Key Phrase 日本語意味 | - | **3回共通** | **なし** | JA(SCG吸収) | 現行は標準2+minimal1。minimal撤去で同一Prompt 3回に変わる |
| Heading readout(point_one/two_heading) | 共通(LRなし=現行どおり非適用) | - | なし | EN | `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`の使用箇所(11章D2) |

※「(要確認)」はlevel別の言語割当がコード上で一意に確認できていない箇所。設計に影響しない(フローは言語に対して対称)。

### 2-2. Secondary呼出条件(Primary NG時)
**原則: Primary NGなら呼ぶ**(種別によるSecondary省略は原則廃止=ユーザー方針)。**呼ばない(別扱い)**のは安全条件として最小限の次のみ。
| # | 不呼出条件(Primary NGの種別) | 理由 | 呼ばないときの扱い | 現行との差 |
|---|---|---|---|---|
| S1 | 数値の**値**の不一致(アラビア数字・漢数字・数詞語。表記差だけでは発火しない=2-2b) | 「原稿へ寄せる」自動補正リスク(Secondary側で数値が原稿に寄る)が未測定。誤PASSは致命 | ATTEMPT_FAIL(再生成) | 日英とも現行は維持。**ただし現行のS1相当判定には穴がある(2-2b)**: 英語は`N%`付き数値の変更を見逃す(合成15件中4件=警告止まり)、日本語は`\d+`のみで漢数字の変更を見逃し、逆に表記差(二/2等)では正しい音声でも発火する |
| S2 | 否定差 | 同上。g12型(縛られず->縛られる)は両ASRとも同じ誤り | ATTEMPT_FAIL | 現行維持(英語の合成否定26/26ブロック)。否定マーカー補強(推奨4)は新規仕様候補・未承認 |
| S3 | length異常(超過・極端な不足)/ 異常長 | 幻覚追加文・脱落の疑い | ATTEMPT_FAIL | 現行維持(JA `length_ok`、EN `max_extra_chars`) |
| S4 | 言い淀み・部分反復QA NG(disfluency / Repetition QA) | 音声そのものの欠陥(ASR一致でも不良) | ATTEMPT_FAIL | 現行は「Primary PASS後にANDで落とす」。順序は同じ(PASS後でもQA NGなら不採用) |
| S5 | 言語ドリフト(**TTS側**が別言語で発話した証拠: Secondary(Azure、言語固定)の転写でも対象言語にならない) | TTS不良 | ATTEMPT_FAIL | **細部に注意**: Key Phrase英語の「Primary(OpenAI)が日本語/中国語へ翻訳的書起こし」は**ASR側の誤り**で、Secondaryを呼んで確認するのが既存対策(`enable_non_latin_cascade`)。したがって「Primary転写が非ラテン文字」だけでは**呼ばない理由にしない**(逆にSecondary呼出のトリガーにする)。TTS側ドリフトの判定はSecondary転写で行う |
| S6 | ASR障害(Primary転写None/API失敗) | 音声の良否が不明 | ASR再試行(<=2、attempt外)。尽きたらHR_TECH | 現行はPrimary転写NoneがTTS_FAILURE扱いで音声不良と区別されない(確定)。区別して記録 |
| (削除) | 類似度<0.4(TTS異常疑い)での一律不呼出 | 現行はg7「湿度->死図塔」で誤って救済機会を失った(標本1) | 呼ぶ(Secondaryが正解を返せば採用) | 新規閾値は未採用。短文には適用しないTrialが必要 |
| (削除) | C1(entity_like/辞書読み/ラテン文字)の粗い除外、C2以外 | g8で救済できなかった。誤PASS実績なし | 呼ぶ。固有名詞のPASS扱いはS7(下)で別途ガード | 例外は「具体的な誤PASS事例+共通ルールで防げない理由」が必要(ユーザー方針) |
| S7 | 固有名詞・entity差(**Secondary一致でもPASSにしない**: PASS集合側の制約) | OPEN-257 Muse事例(3系統が同じ誤聴) | Secondary一致でもPASS_WITH_WARNING+最終試聴、辞書/Ledger/CMU確定語のみ自動PASS(U-17) | 日英非対称(英語=Secondary一致でPASS、日本語=C1除外)の統一案。**これは「Secondaryを呼ばない」ではなく「PASS集合の厳格化」** |

C2(同形異音語ガード)は2026-10-11にユーザーが採用した例外であり、ユーザー方針の「C1等の粗い除外ルールは廃止方向」の対象外として**維持する**(明示的に変える場合のみユーザー判断。5章 C-10)。

### 2-2b. S1(数値)の実測と是正方針(M2、委任_05Bの0円確認)
**(1) 訂正**: v03・Trial C報告の「数値・否定37/37ブロック」は不正確。正しくは**否定は全件(26/26=削除12+追加14)、数値は11/15**。数値の残り4件は安全条件に止まらず「警告(最終試聴連動)」扱いで、Primary NG後のSecondaryに進める。
**(2) 英語で穴になった4件の型**(`trial_c_results_01.json`の合成行、`sample_C_01.json`の原稿で再現。再現script=`er058_05b_zero_yen_checks_01.py`、出力`er058_output/trial_abc/zero_yen_checks_05B/zero_yen_checks_05B.json`): すべて**パーセント記号付き数値**の変更(S03:`25%`->`26%`、S17:`20%`->`21%`、S25:`20%`->`21%`、S30:`20%`->`21%`)。Validatorが`25%`を1語(内部表現`25xpercentx`)として扱い、`number_mismatches`ではなく内容語差分(最小対扱い=警告)として処理するため、数値ゲートに掛からない。素のアラビア数字・年号・日付の変更(11件)はブロックされた。
**(3) 日本語**: `er007_ja_asr_validator_01.py` L67 `_DIGIT_RE=\d+`で**アラビア数字だけ**を比較する。現行関数での確認(0円):
| 原稿 | ASR | 判定 | S1 | 意味 |
|---|---|---|---|---|
| 三人で行きました。 | 四人で行きました。 | TRUE_CONTENT_MISMATCH | **発火しない**(number_mismatches空) | **漢数字の実際の値変更を見逃す**(Secondaryが原稿へ寄せたら誤PASS余地) |
| 三十人が来ました。 | 四十人が来ました。 | TRUE_CONTENT_MISMATCH | **発火しない** | 同上 |
| 二人で行きました。 | 2人で行きました。 | TRUE_CONTENT_MISMATCH | **発火する**(Secondary不呼出) | 表記差だけ。TTSが正しくても再生成3回->HR(LRは日本語未対応) |
| 三十人が来ました。 | 30人が来ました。 | TRUE_CONTENT_MISMATCH | **発火する** | 同上 |
| 十分待ちました。 | 10分待ちました。 | TRUE_CONTENT_MISMATCH | **発火する** | 同上 |
| 100円でした。 | 百円でした。 | TRUE_CONTENT_MISMATCH | **発火する** | 同上 |
| 20％の人が来ました。 | 20パーセントの人が来ました。 | TRUE_CONTENT_MISMATCH | 発火しないがSecondaryもPASS集合外(PHONETIC等)で**NG** | 同上(Secondary呼出費用も無駄) |
| 2026年に始まります。 | 二千二十六年に始まります。 | NORMALIZED_MATCH(PASS) | - | 例外的に通る(桁の読み替えが正規化に入っている) |
**(4) 是正方針(設計案、実装は別。ユーザー判断)**: S1は**「値の不一致」で判定**し、**表記差(二/2、％/パーセント、100/百、漢数字/算用数字)だけでは発火させない**。具体案: 数値を正規化関数(漢数字・数詞語・`N%`/`N percent`・`N人`等の助数詞付きを**同一の値**へ)に通してから比較し、値が同じなら**NORMALIZED_MATCH相当へ引き上げる**(=Secondary PASS集合の2ラベルに入る)。値が違えば従来どおり発火。
**(5) PHONETIC_MATCHの一括許容は不可**: Trial Bで、Azure/localの`PHONETIC_MATCH`を許容すると`ゆうき->雪`(ja_len3)・`いった->言った`(ja_hom1)が誤PASSになる(厳格集合なら防げた)。表記差の救済は「個別の正規化ルール(数値・単位・記号)」で行い、PHONETICの一括許容にしない。
**(6) 影響**: 表記差の正規化を入れない場合、日英の長文(数値・単位・年号を含む)で「TTSは正しいのにS1またはSecondary非PASSで3回NG->HR(英語はLR発火)」が構造的に残る。LR発火条件に「表記差のみのNG」が入ると正しい原稿を書き換える(g21・g36、04D既報)。

### 2-3. PASS集合(ラベル判定、`should_pass`ではなくclassificationラベルで判定=D10)
- **Primary PASS(現行どおり)**: EXACT_MATCH / NORMALIZED_MATCH / TRANSCRIPT_STYLE_NORMALIZED_MATCH / NUMERIC_EQUIVALENCE_MATCH(Tier1) / HIGH_SIMILARITY_SAFE / CONNECTED_SPEECH_ACCEPT系 等。長さ・言い淀み・Repetition QAのANDは維持。
- **Secondary PASS(新規・日英共通・厳格)**: **EXACT_MATCH / NORMALIZED_MATCH のみ**(日本語`SCG_PASS_CLASSIFICATIONS`と同じ。PHONETIC_MATCH・HIGH_SIMILARITY_SAFE・TRANSCRIPT_STYLE等はSecondary単独のPASSには含めない。U-3は(a)暫定、最小対Trial後に(c)を再検討)。
  - **M1(v04): 現状の不一致を明記**。(i)本書v03本文=2ラベル、(ii)日本語SCG(`er007_ja_secondary_asr_01.py` L78)=2ラベル、(iii)**英語のTrial B(`er058_trial_b_analyze_01.py`)とTrial C(`er058_trial_c_en_asr_compare_01.py` L41 `STRICT`)は4ラベル**(EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE)。v03/Trial報告の数値は4ラベル版だった。
  - **2ラベル版へのオフライン再判定(0円、保存済み転写のみ、`er058_05b_two_label_rejudge_01.py`、出力`er058_output/trial_abc/two_label_rejudge_05B/`)**:
    | 指標 | 4ラベル版(報告済み) | 2ラベル版(v04) | 差 |
    |---|---|---|---|
    | Trial C 英語救済(Primary NG系22件) | 4/22 | 4/22 | 0(Azureが救済4件とも厳格2ラベルで通っている) |
    | Trial C 合意誤読11件の誤PASS | 0 | 0 | 0 |
    | Trial C 対照(Primary PASS)6件をSecondary単独で判定した偽NG | 0/6 | **2/6**(S25・S30=`20%`と`20 percent`の`NUMERIC_EQUIVALENCE_MATCH`) | +2(Primary PASSならSecondaryを呼ばないため現行フローの採用結果は不変。**Secondary単独の判定にした場合・Primary NGの偽NGをSecondaryで救う場合は、表記差で通らなくなる**) |
    | Trial B 対照29件の統一フロー不採用 | 0/29 | 0/29 | 0(Azureの転写に`TRANSCRIPT_STYLE`/`NUMERIC_EQUIVALENCE`ラベルが出た例が無い=短文clipでは差が出ない) |
    | Trial B 確認済み誤読30件の誤採用 | 3/30(うちSecondary起因1) | 3/30(同1) | 0 |
    | Trial A 日本語Phase 0(25音声) | 統一フロー10/15採用 | 10/15(Trial A日本語は元から2ラベル) | 0 |
    | Trial A 英語(他NG 20本) | local whisperの合否のみ(ラベル別でない) | 再判定不能(ラベル未保存) | - |
    → **この標本では2ラベル化で救済・誤PASSの数は変わらない**。ただし標本は短文または少数で、`NUMERIC_EQUIVALENCE`(`20%`/`20 percent`)・`TRANSCRIPT_STYLE`は**長文の英語で表記差を吸収する役割**がある(Trial C S25/S30)。2ラベルだと日本語と同様に表記差で再生成になる。
  - **非対称の選択肢(ユーザー判断、9-1)**: (a)英語4ラベル・日本語2ラベルのまま(言語ごとにValidatorが違う現状維持) (b)日英とも2ラベルに揃え、表記差は2-2bの個別正規化でNORMALIZED相当へ引き上げる(推奨度中) (c)日英とも4ラベルに揃える(日本語の`TRANSCRIPT_STYLE_NORMALIZED_MATCH`/`NUMERIC_EQUIVALENCE_MATCH`相当の日本語実装が必要。新規)。
- **PASS_WITH_WARNING**: 最小対・形態素型差分(CONNECTED_SPEECH_PASS_WITH_WARNING等)およびS7(固有名詞のSecondary一致)。**最終試聴リストへ自動連動**(ユーザーが耳で確認)。PASS_WITH_WARNINGは再生成しない(安全≠成功原則に従い、最終試聴で未確認のまま公開しない運用が前提。連動の実装場所=最終試聴ページ生成工程は新規改修)。**M3(v04): この連動の実装は共通フロー有効化の前提条件**(2-6)。

### 2-4. A2 6%減速後検証の一本化(案B')
- 生成->(必要なら)stretch->**最終納品音声に対してのみ**S4/Primary/Secondaryを実行。減速前の検証はしない。
- 外側ループ(`generate_a2_segment_with_slowdown`が内側関数を最大3回呼ぶ)は廃止。1 attemptの定義を「TTS+trim+stretch」とする。OPEN-270(Coffee: TTS総5回、理論最大12)の構造原因が解消する(14-1)。
- stretchは決定論的処理なので、失敗は技術失敗(attempt外)として扱う。
- 影響: Review Lockの「RESOLVEDはブロックしない」特例(6%減速retry用)が根拠を失い孤立(D5)。

### 2-5. 技術失敗のattempt外扱い(上限)
- TTS 400("Model tried to generate text"含む)・空応答・5xx/429/timeout: **同一slotで最大2回再試行**(attempt消費なし)。2回超でHR_TECH。
- 400"Model tried to generate text": **v03は「決定論的で同一Prompt再試行は無意味」としたが、保存ログの集計では支持されない**(v04訂正、委任_05Bの0円確認、9-5)。保存audit JSON 59ファイル(2026-07〜09-13、主にgemini-2.5-pro-preview-tts期)の400事象138件のうち、後続の同一instruction_typeのattemptがあった91件で、**51件(56%)は同一Promptの次attemptで音声が得られ(うち39件がASR検証まで合格)、37件(41%)は再び400、3件が他の失敗**。したがって400は**非決定的(確率的)な拒否**で、同一Prompt再試行は有効。決定論的と言えるのは「その原稿・Promptの組で必ず落ちる」型だけで、ログからは区別できない。Flash-Lite期(`speech_metadata`方式)の400実績は保存ログに無い(未確認)。
  - 帰結: 「(d)隔離経路で救済する」必要性は低い。**同一slot再試行(attempt外、最大2回)で足りる可能性が高い**(U-4(d)は不採用寄りの根拠が増えた)。再試行後も400が続く原稿は、Style不変のままHR_TECHへ(別Promptへ切替えない)。
- 総ガード: segmentあたり技術失敗再試行の累計<=6(無限ループ防止)。

### 2-6. 導入の前提条件と順序(M3、v04新設)
共通フローは**Secondary PASS(特に固有名詞・最小対・表記差)をPASS_WITH_WARNINGで受け、最終試聴リストへ自動連動する**ことで安全性を成立させている(Trial B: 14/44クリップは全ASRが原稿形で転写=ASRでは区別不能、型別例外は「ASR PASSでも確定しない型」)。連動が無い状態で共通フローを有効化すると、「Secondaryが原稿に寄せた/ASRが丸めた」誤読がPASSのまま公開される。したがって:
1. **試聴リスト連動の実装・runtime evidence(PASS_WITH_WARNINGがリストに載り、人間が確認するまで公開に進まない)が先**。
2. その後に共通フロー(Secondary確認・Cascade 4段廃止・force_secondary廃止)を有効化する。
3. 連動が間に合わない場合の暫定: **PASS_WITH_WARNINGをNG扱い(再生成/HR)にする**(偽NGは増えるが誤PASSは増えない)。
4. 順序の根拠: 安全≠成功原則(PASS_WITH_WARNING=自動確定しない)。連動の実装が無いのに警告を増やす設計は成立しない。

### 2-7. force_secondary撤去で外れる見出し・LR後原稿の保護(M4、v04新設。ユーザー判断事項)
- 現行: **A2のminimal fallback経由の音声(LR後の再TTSを含む)**は**force_secondary**(Primary PASSでもAzure確認必須)で守られる(ER-008 Part C、`crosslevel` L341)。共通フローでminimalと`force_secondary`を撤去すると、この**追加の確認層が外れる**(LR後原稿v1が最も影響を受ける)。
- **見出し(Heading readout)**: `er003_v1_sing01_point_headings_aoede.py` L77〜100は、`max_attempts=3`(`PRODUCTION_MAX_TTS_ATTEMPTS`)のとき`minimal_after=max(1,3//2)=1`で**attempt 2・3が`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`/`MINIMAL_INSTRUCTION_PREFIX`(minimal系)**を通常Styleとして使う(標準1+minimal2)。見出しは短く、point_one_heading誤PASS事故(ER-008)の対象。**確認結果(コード、L126-128): 見出し経路は`evaluate_attempt_with_cascade`を`force_secondary`なしで呼ぶ**(cascadeのみ)ため、見出しのminimal attempt(2・3回目)は**元から`force_secondary`で守られていない**=v03/Opusレビューの「force_secondary撤去で見出し保護が外れる」は、見出しについては**厳密には撤去で外れる保護が無い**(`force_secondary=True`を渡すのはA2の`_run_a2_minimal_fallback_attempt` L341のみ)。ただし論点は残る: **見出しが標準Promptではなくminimal系文言を通常Styleとして2回使う**点と、**Primary PASSなら見出しはSecondary確認されない**点(point_one_heading誤PASS事故の再発余地)。共通フローで見出しを標準Prompt3回にすれば前者は解消するが、後者はPASS_WITH_WARNING/Secondary確認の判断が要る。
- **LR後の原稿v1**: LR後は元の原稿が書換わるためASR PASSの意味が変わる。実例: Coffee part2 #5(LR後最終音声)は**Primary PASS**(`raw bean`と転写)だが、**Azure forced・local smallが`raw bean->robbing`**と転写(4系統中2系統)。force_secondary(Azure)は現状これを**止めた**(HR行き)。共通フロー(Primary PASSならSecondaryを呼ばない)では**このクリップは採用される**(Trial A #5)。
- ユーザー判断事項(9-4): (A)**見出しとLR後v1は、Primary PASSでもSecondary確認する**(Secondary 1回、費用+Azure約2円/件)。(B)**少なくともPASS_WITH_WARNINGとして最終試聴リストに入れる**(Secondary呼出は不要、試聴負荷増)。(C)対策なし(共通ルールのみ)。推奨: (B)を最低限、(A)は見出し・LR後のみ(対象が少ないため費用影響小)。
- 試聴で確認する対象(`user_test/asr_misread_listen_01/`): Coffee #5(`raw bean`)、#2(`showed`)ほか(委任_05B)。

---

## 3. Key Phrase 3回単一Prompt構成

### 3-1. フロー(英語Phrase・日本語意味とも)
```
attempt 1: TTS(単一Prompt P) -> Primary -> NGならSecondary -> PASSなら採用
attempt 2: 同一P・同一原稿・同一model/voice/速度 で再生成 -> 同様に検証
attempt 3: 同上
3回とも両NG -> Human Review(Local Rewriteなし、Prompt途中切替なし)
```
- Std/Adv共通仕様。Master Store再利用維持(key=language/voice/model/canonical_text/style_instruction_id/version)。**Promptを変更するなら`KEY_PHRASE_TRIM_POLICY_VERSION`または`style_instruction_version`を更新**(さもないと旧Prompt音声が再利用される/逆に更新で既存音声が再利用不可)。
- 現行の「Minimal 2回->English Lock 2回」は`generate_key_phrase_component_verified`内の2段呼出で、`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS=2`/`ENGLISH_LOCK_MAX_ATTEMPTS=2`/`TOTAL=4`が定数。3回構成ではこの2段を1段(max_attempts=3)に畳む。

### 3-2. 単一Prompt Pの選択肢(**ユーザー判断**、本書では選ばない)
| 案 | P | 位置づけ | Trial D結果(n=1、8語) |
|---|---|---|---|
| P-a | 現行Minimal(=Primary段のPrompt) | 変更最小。ただしEnglish Lockが無くなる(翻訳的書起こしの対策はASR側①のみに依存)。**2段目(English Lock)による救済実績は少数ながら有る**(9-1: 2026-09-01以降のKP英語294 call中、3〜4回目で合格=4件(1.4%)、保存attempt音声で確認できた3件はいずれもMinimal 2回NG後にEnglish Lock段で合格)。P-aにすると、この型(Minimal 2回NG)の約1.4%が『Minimal 3回目』で通るかが未検証 | 8/8 PASS。ただしraw beanはlocal whisperが「Robin」に聞こえ、「A catch?」とASRが疑問形 |
| P-b | 現行English Lock(Minimal+Lock、=Fallback段のPrompt)を3回すべてに使う | 既存承認文言の逐語使用のみ(新文言なし)。English Lockを初回から常用 | V4相当(K2ベースの完全版)は8/8 PASS。本Trialでは現行English Lock単体は未生成(V4はK2+現行2文) |
| P-c | K2統合(簡潔版/完全版) | 新規Prompt。Trial/ユーザー採否必須(K2正式変更は禁止) | 簡潔版V3: 8/8 PASS、K2に近い挙動(長めのまとまりある発話) |
詳細・逐語比較・長さ: `KP_K2_VS_EXISTING_COUNTERMEASURES_01.md`。
- 既存KP専用対策は全案で維持: ①ASR対策(逐語ASR指示`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`、非ラテン時再確認`non_latin_cascade`)=ASR側なのでPrompt Pに依存せず維持、②TTS Prompt対策(語末子音保持・冠詞/機能語弱形・一体感・過剰強調/反復防止)=Pに含める(P-aは含む、P-cはK2に不足があり統合が必要)、③生成後QA(部分反復・言い直し検知)=`disfluency_qa=True`を維持。

### 3-3. 日本語意味(KP JA)
- 現行: `generate_a2_japanese_with_fallback`系(標準2+minimal1)。3回構成化=minimal(`_generate_a2_japanese_minimal_instruction`)を撤去し標準Prompt 3回。Master Store key(`charon_japanese_fixed_shell`系とは別のKP意味キー)の再利用は維持。
- SCGの吸収(D8): `_scg_exclusion_reason`は2-2の安全条件(S1〜S7)へ再編し、C1(g8のentity_like除外)を共通ルールで置換(U-1/U-17)。

---

## 4. Local Rewriteの位置づけ(通常role)
- **発火条件**: v0で3回全不合格(Primary NG かつ Secondary NG/不呼出)、**かつ role in {Full Story, Preview, Comment, In One Line, Topic Intro}、かつ lr_used==0**。KP・Heading readoutは非適用(現行`NON_APPLICABLE_SEGMENT_IDS`/`KEY_PHRASE`と一致、変更なし)。
- **内容**: NG spanを最小範囲で書き換え。意味・Fact・役割・構成・文脈・自然さ保持。既存の品質Gate(Luna 5 Gate QA[意味/役割/Fact矛盾なし/文脈接続/自然さ]+全文性/局所性Gate 6・7+span整合+数値保持=OPEN-256)を**維持**。
- **LR後**: v1でTTS最大3回(各回Primary->Secondary)。不合格はHR(2回目のLRは禁止)。最大TTS 6回、PASS時点で終了。
- **報告項目(LR発火時、Human Review/最終報告へ必ず含める)**: ①発火理由(v0 3回全NGの各Primary/Secondary結果) ②書換え箇所(span before/after) ③前後の文面(原稿前後・context) ④最小限と判断した根拠(unchanged_ratio・Gate結果・changed_span) ⑤v1の再生成・ASR結果(attempt別)。
- **改修点(現行との差)**: (1)**A2経路(`er003_v1_crosslevel_audio_02_common.py` L383-)のLR再TTSだけ**が`_run_a2_minimal_fallback_attempt`(minimal Prompt+force_secondary)を呼ぶ=「Style不変」の原則に反する。**B1/Charon経路(`er003_v1_sing01_voice01_generate.py` L359)とNews経路(`er003_v1_sing01_news_tail_fix.py` L368)のLR再TTSはminimalを使わず**、それぞれ`generate_charon_english.__wrapped__(max_attempts=1, style_prefix_override=…)`/`generate_news_narration_wide_margin.__wrapped__(max_attempts=1, …)`=**標準Promptの1 attempt**(委任_05Bで確認、9-2)。どちらも`attempts_log`を連結して累積計数へ反映する(voice01 L394、news_tail_fix L371-)が、A2経路だけ`resolved`にretts分のattempt logを足していない(下記C-6)。LR後の再生成上限は現状**1回**(共通フロー案は3回)。LR再TTSは**標準経路と同じPrompt/model/voice/速度の共通ループ**に置換(OPEN-274、D1)。(2)NG span選択はNGを出した**ASR転写基準**(OPEN-274)。(3)cool-down 600秒の位置(U-6)。(4)日本語は未対応のまま=HRへ。
- **日本語**: 機械流用は不可(`JA_LOCAL_REWRITE_APPLICABILITY_01.md`の5実例:`identify_ng_span`が日本語で未動作、Gate 7が常に0.0、KP系短語はそもそも対象role外)。日本語は当面LRなし(3回不合格->HR)とし、適用はTrial結果を見てユーザーが判断。

---

## 5. 既存承認仕様との衝突一覧と変更点・影響
(C-n。各項目: 現行承認仕様 / 本設計の変更 / 影響。いずれも**Production採用はユーザー承認が前提**)

| ID | 現行承認仕様(出典) | 本設計の変更 | 影響・注意 |
|---|---|---|---|
| C-1 | UNCERTAIN(entity/濁点差のみ)->**Human Review直行**(2026-08-25 U、CS:1997/1998、`stop_retrying`は「Cascadeを尽くした印」) | UNCERTAINもPrimary NG扱い->Secondary->両NGなら**再生成**(HR直行を廃止) | `stop_retrying`の意味再定義、`CASCADE_CONFIG_JA`(Primary#2/Azure#1/#2)の廃止。**例外案**: 両ASRが同じ誤りで一致した場合のみ即HR(U-2(c))は本設計の基本形には含めない(要判断) |
| C-2 | ER-011-25/26: 標準2+minimal1(合計3、minimalは最終attempt)。26で「25の標準2固定を撤回、TOTAL3に統一」 | minimal撤去、**標準Prompt 3回**(合計3は維持) | 定数`PRODUCTION_STANDARD_TTS_ATTEMPTS=2`/`MINIMAL=1`とassert(`er011` L102-104)を日英同時に変更(D3)。25/26のコメントも更新要 |
| C-3 | PHONETIC_MATCHをSecondary単独PASSにしない(日本語SCG、`SCG_PASS_CLASSIFICATIONS`、2026-10-11 U)。英語Secondary一致は`should_pass`で緩い | Secondary PASSを両言語で厳格集合(EXACT/NORMALIZED)に統一 | 英語はPASS拡大ではなく**縮小**(HIGH_SIMILARITY_SAFE等を除外)=偽NG増の可能性。U-3 |
| C-4 | Key Phrase英語 **4回構成(Minimal2+English Lock2)**(2026-09-01 U、ER-010-NO9-...-22、`KEY_PHRASE_TOTAL_MAX_ATTEMPTS=4`は「TOTAL3の明示的例外」) | **3回単一Prompt**に変更(例外Aの撤廃) | 4->3で上限が下がる(KP 77 callの96%は1回目合格=影響小)。単一Promptの選択(3-2)が新規仕様。Master Store versionの更新要 |
| C-5 | OPEN-76: 6%減速は減速後音声を検証、再生成3回(外側ループ許容) | 案B'(最終音声のみ検証、外側ループ廃止) | OPEN-76の「減速後音声を検証」には忠実。「3回」は1 attempt=TTS+stretchで3回。Review Lock特例の撤去(D5) |
| C-6 | CS:1692「TTS生成の同一segment総試行3回」(`PRODUCTION_MAX_TTS_ATTEMPTS=3`がSSOT)。委任_05Aで「通算3回共有」の遵守明確化済み(OPEN-270 CLOSED) | **script版あたり3回**、LR発火時は最大6回(3+3) | SSOTの意味変更。**必須改修(v04、M5追記)**: (1)`er011_human_review_lock_01.py`の`MAX_CUMULATIVE_TTS_ATTEMPTS=15`・`MAX_CUMULATIVE_ASR_CALLS=60`(L68-69、複数callを跨ぐ累積の費用ガード)は「1 call=最大3回+LR1回」を前提にした値。**1 call設計上限が6回(ASRはPrimary+Secondaryで最大12+Tier3/CS層)**になると、累積15は2.5 call相当で発火する=ガードの意味が変わるため再計算が必要。(2)`record_outcome`の`tts_attempts_this_call`は`attempts_log`+`fallback_attempts_log`の長さの和。**A2経路のLR再TTSは`resolved`へ追記されない**ため、Coffeeで**記録4回/実際5回**となった(確定、委任_04A/OPEN-270の一部)。**LR再TTS分を`attempts_log`へ加算する改修が共通フロー導入の必須条件**(上限6回の計数を実態に合わせる)。(3)HR判定しきい値・`attempt_history`のschema(v0/v1別カウンタ)も要再設計 |
| C-7 | LR位置づけ: 標準2->10分cool-down->minimal1->LR(OPEN-256/274、2026-09〜10-11)。委任_05Aでcool-downは「通算3回目直前のみ」に是正 | v0 3回後に最大1回、LR後3回 | cool-down位置(U-6)。LR再TTSの経路置換(D1、A2経路のみ)。OPEN-259(短文誤拒否)・OPEN-256(全文性)は維持。**cool-downを廃止した場合の効果と、導入理由(一時的なAPI不調・レート制限の回避)を外した場合の悪影響は、対照データが無く測れていない**(7章) |
| C-8 | force_secondary(minimal経由はPrimary PASSでもAzure必須、ER-008-FALLBACK-TRIGGER-MITIGATION Part C) | 廃止(minimal自体を撤去するため) | 関連テスト(`er006_secondary_asr_01_test.py`等6ファイル)の更新。point_one_heading誤PASS事故の根本原因は未決(追跡要) |
| C-9 | Primary#2/Azure#2(旧Cascade4段) | 廃止(転写同一で独立性なし) | ASR呼出4->2、費用減。日本語HR 8件は全て同一転写(確定) |
| C-10 | 日本語SCG除外: C1(entity_like等、Fable採用・ユーザー個別承認の逐語なし)、C2(同形異音語、ユーザー採用)、推奨4(否定マーカー、ユーザー採用) | C1は廃止方向(粗い除外)。C2/推奨4は**維持**(例外は誤PASS事例+理由が要る) | `er007_ja_scg_phase0_regression_test_01.py` L239(g8除外固定)を意図的に更新 |
| C-11 | 固有名詞(entity)のPASS: 英語=Secondary一致でPASS、日本語=C1除外 | S7: Secondary一致でもPASS_WITH_WARNING+最終試聴(辞書/Ledger/CMUのみ自動PASS) | 日英非対称の解消。最終試聴連動の新規実装(U-17/U-18) |
| C-12 | Master Store再利用(キー: language/voice/model/canonical_text/style_instruction_id/version) | 不変(Key Phrase Prompt変更時のみversion更新) | Prompt変更=既存KP音声は再利用不可(再生成コスト)。`_generate_or_reuse`にfingerprint追加は新規仕様 |
| C-13 | 技術的fallback(B1B: TTS400時のminimal)・`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`の`welcome`殻使用 | 「到達不能にする」のみ。定数・`welcome`殻の用途は残す | 名称と用途のズレ(D2) |
| C-14 | 費用: Azure Secondary費用が集計に入っていない(OPEN-271/275) | 共通フローで英語Azure呼出が増える前に計上修正が望ましい | 別件(U-15/U-19) |

**ユーザー方針との関係**: C-1/C-2/C-4/C-6/C-7は**承認済み仕様の明示的変更**で、ユーザー確定方針(2026-10-12)は設計の前提だが、Production採用は別途`APPROVED_FOR_PRODUCTION`が必要。

---

## 6. 日英・各roleで成立するか(確認結果)
| 観点 | 結果 |
|---|---|
| 状態遷移が言語非依存か | 成立。言語依存は(i)Primary/Secondary検証関数、(ii)S1〜S7の判定実装、(iii)LR可否のみ |
| 日本語の障害 | (1)LR未対応 (2)Primary NG種別の判定(`_scg_exclusion_reason`)をS1〜S7へ再編 (3)数値判定が`\d+`のみ(漢数字・数詞語)の穴(X1) |
| 英語の障害 | (1)Secondary(Azure)呼出がnon-KP英語に新規追加(現行: TCM時のTier3/CS層のみ) (2)Tier3/CS層とのAzure二重呼出(D6)→Secondary転写の共有改修 |
| Key Phrase | 英語・日本語とも3回単一Promptで成立。LRなし |
| A2減速 | B'で成立(最終音声のみ検証) |
| 未検証(Trial要) | S1(数値)での「Secondaryへ寄る」自動補正の有無、共通Secondary厳格集合での偽NG率(最小対Trial 8-3-A)。本委任では未実施 |

## 7. QCD(見込み。標本が小さい項目は推測)
| 項目 | 変化 | 根拠/注意 |
|---|---|---|
| 品質Q | 偽NGによる不要な再生成と本文書換え(LR)が減る(英語)。日本語は既にSCGあり=変化小。誤PASSは厳格集合(EXACT/NORMALIZED)+安全条件S1〜S7で抑える | 誤PASS率の定量は未測定(合成のみ) |
| コストC | ASR: 旧Cascade(Primary#2+Azure#1/#2)->(Primary+Secondary)で呼出減(日本語)。英語はAzure追加(約+0.2〜0.3円/segment見込み)。**D6(v04で加算): Tier3/CS層(`evaluate_attempt_with_cascade_detail`内)が同じ音声に対して別にAzureを呼ぶため、Secondary確認を追加すると1音声に最大2回のAzure(英語Azure約1.8〜2.2円/40秒音声)。Secondary転写を共有する改修をしない場合、Secondary呼出対象(Primary NG音声。割合は標本により異なり、旧フローで標準2回内に完了しなかったcallは約7%)の分だけ+約2円/件が上乗せ**(共有する場合は追加0)。TTS: PASS時の再生成減。LR最大1回/segment(LLM+TTS3回) | 英語Azure単価約2.2円/回(報告02の見込み、Trial Cで平均10.4秒/回・約1.1円/本[40秒換算約1.8円]を実測)。Secondaryは1回のTTS再生成(約0.135円)の約13倍(Trial C 4章)=**費用だけで見るとSecondaryは割に合わない**。主眼は「Cascade廃止・同一Prompt継続」 |
| 時間D | cool-down(600秒)の待ちは**通算3回目に到達したsegment(旧フロー外挿で全callの約5〜8%)にしか発生しない**。廃止の効果は**平均で5〜8%x600秒=約30〜48秒/segment**(最大600秒は該当segmentのみ)。v03の「最大約10分/segment短縮」は最大値であり平均ではない。**導入理由(一時的なAPI不調・レート制限の回避)を外した場合の悪影響は、対照データが無く不明**(OPEN-270の通算判定是正後の発火頻度は未再測定) | U-6 |
| 運用 | 技術失敗がattempt外になり一時障害でattemptを失わない。HR報告にLR発火詳細が付く | |

### 7-2. Secondaryの選択肢(v04追記): local whisper medium案と「言語ごとにSecondaryを変える」案
| 案 | 内容 | 長所 | リスク |
|---|---|---|---|
| S-A | 日英ともAzure(Phrase Listなし)(Trial B/C、日本語SCGと同じ) | 独立した商用ASR、日本語は既存SCGと整合 | 英語は費用増(D6含む)、Azureも日本語固有名詞で誤聴 |
| S-B | **英語=ローカルwhisper medium(0円)、日本語=Azure(現行SCG維持)**(言語ごとに変える) | 英語のSecondary費用0円。Trial C: NG系22件でmediumの厳格PASSは5件(偽NG判定3/4・曖昧2/7・合意誤読0/11)でAzure(4件)と同程度 | **mediumは単独の最終権威にできない**: 局所脱落(`People`脱落、FREE_VERIFICATION 4-2)、Primary PASS音声を32.5%NGにする(FREE_VERIFICATION 4-8)ため偽NG源になる。ローカル実行環境(GPU/CPU時間)が本番側にあるか未確認。言語でSecondaryが違うと挙動の比較・保守が二重になる。**日英の独立性が等しいか未検証** |
| S-C | 英語=Azure+local medium併用(両方PASSで採用) | 誤PASS抑制 | 費用・時間増、偽NG増 |
結論: 費用面ではS-Bが有利だが、**mediumの偽NG(32.5%)・局所脱落の評価がPrimary NG救済用途(今回の標本)とPrimary PASS検査用途で別**であり、本Trialでは救済用途のみ測れた。採否はユーザー判断(9-6)。

---

## 8. 残る判断事項(ユーザー)
1. 共通フロー全体を承認(日英同時か、段階導入か)。段階導入するなら(a)日本語先行 (b)英語先行 (c)Full Storyのみ先行。
2. KP 3回単一Prompt: Pを a/b/c のどれにするか(3-2)。
3. UNCERTAIN->HR直行の廃止(C-1)と例外案Cの要否。
4. PHONETIC等の許容範囲(C-3、U-3)。
5. LRの日本語適用をどうするか(Trial結果を見て)。
6. cool-down(U-6)、決定論的技術失敗(400)の扱い(2-5、U-4(d))。
7. C1の廃止(g8の13/14受入の最終確認、U-1)・C2維持。
8. 最小対Trial(8-3-A、約15〜20円)の実施可否。

(v04: 上記8章は04D時点の項目。統合した最終版は`RECONCILIATION_FINAL_REPORT_01.md` 8章を正とする)

---

## 9. 委任_05B 0円追加確認の結果(Opus R4対応、保存ログ・コード・manifestのみ。API 0円)

### 9-1. KP現行4回構成の2段目(English Lock)による救済実績
- **集計1(attempt_history、`er011_output/attempt_history.jsonl`)**: `segment_id`が`kp[1-5]_en`、2026-09-01以降(4回構成のユーザー正式決定日以降)、重複行除外で294 call。内訳: **1回目合格272(92.5%)**、2回目合格12(4.1%)、**3回目合格3・4回目合格1=English Lock段での救済4(1.4%)**、STOPPED(Human Review)3、TTS 0回でロック済みHR 3。English Lock段に入った7callのうち4が救済、3がHR。(`kp_1`/`kp_1_probe`等のtest segmentは対象外。実運用とtestのthemeは区別不能のため、**試験的実行を含む**。)
- **集計2(保存attempt音声、`**/attempts/kp[1-5]_en_attempt*.json`、244 segment群)**: Minimal(`custom_bd5c8f46`)2回NG後にEnglish Lock(`custom_31eb2f72`)で合格した事例**3件**: ①2026-09-17 b1_2v kp5_en(TTS_FAILURE->TRUE_CONTENT_MISMATCH->TTS_FAILURE->NORMALIZED、4回目で合格、gemini-2.5-pro-preview-tts)、②2026-09-25 meta kp4_en(TRUE_CONTENT_MISMATCH x2->NORMALIZED、3回目、2.5-pro)、③2026-09-28 hormuz run_06 kp5_en(TTS_FAILURE `Said a lot.`->TRUE_CONTENT_MISMATCH->NORMALIZED、3回目、**gemini-3.8-flash-lite-tts=Production現行**)。
- **結論**: **ゼロではない**。実績の主旨: P-a(現行Minimal維持)のとき、旧2段目が救った1.4%(Flash-Liteで確認できた分は1件)が、Minimalの3回目で通るかは**未検証**(Minimal 3回目でも通る可能性はあるが、English Lockの効果とMinimal再試行の確率的合格は**区別できない**)。Master Store再利用はP-aなら維持(9-3)。追加Trial最小設計(9-7)で測る。
- Minimalのみ(P-a)で「残る約4%」(1回目不合格)は、HR確定が3〜6件/294(1〜2%)。

### 9-2. LR再TTS関数の中身(`news_tail_fix` L368、`voice01` L359、`crosslevel` L383)
| 経路 | `_retts_fn`の実体 | minimal使用 | 再TTS回数 | 累積計数への反映 |
|---|---|---|---|---|
| A2(`crosslevel` L392-) | `_run_a2_minimal_fallback_attempt`(minimal Prompt、`force_secondary=True`) | **使う** | 1 | **反映されない**(`resolved`へ`attempts_log`を足さない。Coffee 記録4/実際5) |
| B1/Charon(`voice01` L359) | `generate_charon_english.__wrapped__(max_attempts=1, style_prefix_override=…, tts_backend=…)` | 使わない(標準Prompt。ただし関数内にTTS 400時の技術的fallback L170〜200=minimal系は有る) | 1 | 反映(`main_loop_attempts_log + retts attempts_log`連結、L394) |
| News(`news_tail_fix` L368) | `generate_news_narration_wide_margin.__wrapped__(max_attempts=1, …)` | 使わない(標準Prompt) | 1 | 反映(L371-連結) |
→ 「LR再TTSがminimal依存」は**A2経路のみ**。共通フロー化の置換対象はA2の1関数。

### 9-3. Master Store内のminimal由来音声(`er006_output/master_audio_store_01/manifest.json`、378件)
- 全378件の`key.instruction_path`は`primary`のみ(fallback/minimalの印は**記録されない**)。キー内訳: key_phrase_english_component(v2_margin030 241件[2.5-pro 210+Flash-Lite 31]、v1 99件)、charon_english_fixed_shell(35件)、charon_japanese_fixed_shell(3件)。
- **minimal由来が標準キーで保存されているか: manifestだけでは判定不能**(キーにstage情報が無い。`ensure_key_phrase_english_component`は`generate_key_phrase_component_verified`の結果をそのまま同じキーで保存=Minimal段でもEnglish Lock段でも同一キー)。混入しうる経路は(a)KPの2段目(English Lock、minimalではない)=救済率約1.4%、(b)B1/Charon固定殻の技術的fallback(TTS 400/発話区間検出失敗時のみ、頻度不明)。A2 narrationのminimal fallback音声はMaster Storeに入らない(固定殻/KP/数字のみが対象)。
- **影響**: P-aならKP再利用は無変更。P-b/P-cなら`style_instruction_version`(`KEY_PHRASE_TRIM_POLICY_VERSION`)更新が必要(既存241件が再利用不可=再生成コスト)。`_generate_or_reuse`にfingerprint(stage)を足すのは新規仕様。

### 9-4. 日本語minimalの導入理由(instruction leakage)のFlash-Lite期の再発率
- 導入理由(ER-003-N3-ROOT-FIX-01、2026-08-17): 長い`JAPANESE_STYLE_PREFIX`(約1800文字)で指示文を読み上げる事例が高頻度(Health B1で5回中5回)。
- 保存attempt JSON(日本語、`gemini-3.8-flash-lite-tts`)の集計: **Production現行backend(`speech_metadata_flash_lite`)は日本語87 attempt(標準86+minimal 1)中、指示文読み上げ(ASR転写に「翻訳・言い換えせず…読み上げてください」等の混入、または`length_ok=False`)0件**。一方、leakageが起きたのは**`tts_gemini_3_8_flash_lite_ab_trial_01/b`(backend印なし=指示文をpromptへ含める旧方式のB群)のみ**で、標準8 attempt中7件、minimal 5 attempt中3件がleak。つまり**Flash-Lite+`speech_metadata`方式では再発0/87(Wilson95%上限約4%)、旧方式(指示文同居)では高頻度**。結論: **Flash-Lite期のProduction方式では、日本語minimalを「leakage対策」として残す必要性を示す事例は無い**(標本87、短文KP意味・見出しに限らない)。ただし指示文同居の経路(Structured Separation/AB trial)が残るなら話は別。

### 9-5. 決定論的400エラー("Model tried to generate text")
2-5を参照。保存audit JSON 59ファイル・400事象138件、後続の同一instruction_type attemptのある91件で**同一Prompt再試行成功51件(56%、ASR合格39件)・再び400が37件(41%)・他3件**。**決定論的ではなく確率的**。標本はpro-preview期(2026-07〜09-13)で、Flash-Liteの400実績は保存ログに無い。

### 9-6. minimalが残る経路の一覧(`MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_V04.md` 10章にも記載)
| 経路 | 場所 | 通常の内容NG再試行か | 共通フロー化後の扱い |
|---|---|---|---|
| A2英語(標準2+minimal1) | `crosslevel` L181/L292、LR再TTS L383 | はい | **撤去対象** |
| 日本語(標準2+minimal1) | `n3` L532、`voice01` L557 | はい | 撤去対象 |
| B1/Charon英語の技術的fallback(`trimmed is None`時) | `voice01` L170-200、`news_tail_fix` L175 | **いいえ**(TTS 400/発話区間検出失敗時) | 「到達不能にする」か隔離か(U-4(d))。400が確率的なので再試行で足りる可能性(9-5) |
| **Point見出し(英語、attempt 2・3がminimal)** | `point_headings_aoede` L77-100 | **はい**(`max_attempts=3`のとき標準1+minimal2=v03が見落とした通常Style選択) | 見出しのStyleをどうするか要判断(2-7) |
| legacy label(`voice01_labels_fix` L63-66) | Family A/B legacy個別script | 内容NG再試行(後半half=minimal) | legacy。再実行しないなら無害 |
| Key Phrase専用Minimal(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`) | repro01 L685 | KP初回Prompt | **撤去しない**(別物) |
| 汎用定数`MINIMAL_INSTRUCTION_PREFIX`/`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` | repro01 L495、`er033` L61 | - | 残す(`welcome`殻で通常使用) |

### 9-7. KP単一Prompt決定のための追加Trial最小設計(**未実施**、ユーザー承認が前提)
- 目的: P-a(Minimal 3回)・P-b(English Lock常用)・P-c(V3簡潔統合)の**初回合格率と聴感**を、English Lock救済実績(約1.4%)の有無が問題になる語で測る。
- 設計: V1(現行Minimal)・V3(簡潔統合)のみ、**8〜10語 x 各3回生成**(Production同一TTS、Aoede、Standard同期)。語はKP救済実績語(raw bean、new normal、default、cashless、work-life balance、push prices up、a catch、price tag)を継続使用。評価: ①自動(Primary PASS率、非ラテン、反復、語数)、②**Blind試聴(版名を隠し順序ランダム)でユーザーが1語ずつ自然さ・語尾・冠詞を採点**。費用目安: TTS 48〜60 call x 約0.03円(Trial Dの実績: 35 callで約1.1円)+ASR約1円=**数円(約3〜5円)**。所要: 生成20分+試聴10分。
