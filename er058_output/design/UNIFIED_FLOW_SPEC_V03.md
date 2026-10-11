# UNIFIED_FLOW_SPEC_V03: 日英共通フロー設計案 v03(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04D、2026-10-12)

状態: **設計案(Trial/設計限定)**。Production未承認。`APPROVED_FOR_PRODUCTION`は人間ユーザーのみ。Production code/Prompt/Validator/Routing/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSは変更していない(SSOT記録は統合委任で)。
前提: ユーザー確定方針(2026-10-12)と`RECONCILIATION_REPORT_02.md` 5・6・9・10・11章。確定=コード・ログで確認、推測=その旨を明記。
使用モデル(本書の根拠調査): コード読解のみ(API 0円)。本書自体にモデル評価は含まない(Trial DとJA LR Trialは別書に記載)。

---

## 0. 結論(先に・ユーザー判断材料)

| 問い | 結論 | 根拠・条件 |
|---|---|---|
| 共通フローは日英・各roleで成立するか | **成立する(設計上)**。ただし日本語のLocal Rewriteは**未成立**(機械流用不可、別書`JA_LOCAL_REWRITE_APPLICABILITY_01.md`)。日本語はLR無し(3回不合格で直接Human Review)で開始するのが安全 | 5 role(Full Story/Preview/Comment/In One Line/Topic Intro)+Key Phrase(英語Phrase・日本語意味)の全てで「TTS→Primary→Secondary→再生成(同一条件)」は同じ状態遷移で書ける(2章)。差が出るのは(i)Secondary不呼出の安全条件の判定関数(言語別実装)、(ii)LR可否(英語のみ) |
| Key Phraseは4回構成を3回単一Promptに変更できるか | **変更できる(設計上)**。ただし「単一Promptの中身」が未決(現行Minimal / 現行English Lock統合 / K2統合の3案)で、これは新規仕様判断。現行4回構成=ユーザー正式決定(2026-09-01)の変更になる | 3章。Trial D(`KP_K2_VS_EXISTING_COUNTERMEASURES_01.md`)では8語x4版が全てPrimary PASS・非ラテン0・反復0。Prompt全文が長い版は短い版より挙動がK2から離れた(n=1、傾向のみ) |
| LRは最小変更で運用可能か | **英語は現行実装で運用可能(ただし位置づけ変更の改修あり)**。日本語は機械流用すると**必ず失敗する箇所が複数**ある(Gate 7が日本語で常に0.0、NG span特定が日本語で未動作)。日本語は適用範囲・Gate再設計が要る | 4章、`JA_LOCAL_REWRITE_APPLICABILITY_01.md` |
| minimal fallback撤去 | 撤去可能。最初に壊れるのはLR再TTS(L383)とA2/B1/JAの既定引数(2+1=3定数)・静的監査/回帰テスト | `MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_01.md` |
| QCD | Q: 再生成が同一Prompt+Secondary確認になり偽NGが減る(英語。日本語は既にSCGあり)。C: ASR呼出は旧Cascade4段->最大2段に減る一方、Azure呼出は英語で増える。LRは最大1回/segment。D: cool-down(600秒)の扱い次第で最大約10分/segment短縮 | 7章 |

---

## 1. 用語と共有カウンタ

| 用語 | 定義 |
|---|---|
| segment | 1つの出力音声単位(例: full_story_part1、comment_2、kp3_en、meaning_3)。`segment_key=(theme, level, segment_id)` |
| script版 | LRで原稿が変わるたびに増える版。`v0`=承認原稿、`v1`=LR後(最大1つだけ) |
| attempt | **有効な音声が得られたTTS 1回**(技術失敗は含めない、2-5)。上限: 1 script版につき3回 |
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
- 技術失敗(TTS 400/空応答/無音・無発話区間なし)・ASR API失敗はattempt外(U-10(a)案、上限付き)。無音・異常長は音声不良としてattempt消費(M4反映)。

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
| S1 | 数値差(アラビア数字・漢数字・数詞語の不一致) | 「原稿へ寄せる」自動補正リスク(Secondary側で数値が原稿に寄る)が未測定。誤PASSは致命 | ATTEMPT_FAIL(再生成) | 日英とも現行は維持。日本語の数値判定が`\d+`のみ(X1)の問題は別途(漢数字/数詞語を追加するかは別判断) |
| S2 | 否定差 | 同上。g12型(縛られず->縛られる)は両ASRとも同じ誤り | ATTEMPT_FAIL | 現行維持。否定マーカー補強(推奨4)は新規仕様候補・未承認 |
| S3 | length異常(超過・極端な不足)/ 異常長 | 幻覚追加文・脱落の疑い | ATTEMPT_FAIL | 現行維持(JA `length_ok`、EN `max_extra_chars`) |
| S4 | 言い淀み・部分反復QA NG(disfluency / Repetition QA) | 音声そのものの欠陥(ASR一致でも不良) | ATTEMPT_FAIL | 現行は「Primary PASS後にANDで落とす」。順序は同じ(PASS後でもQA NGなら不採用) |
| S5 | 言語ドリフト(**TTS側**が別言語で発話した証拠: Secondary(Azure、言語固定)の転写でも対象言語にならない) | TTS不良 | ATTEMPT_FAIL | **細部に注意**: Key Phrase英語の「Primary(OpenAI)が日本語/中国語へ翻訳的書起こし」は**ASR側の誤り**で、Secondaryを呼んで確認するのが既存対策(`enable_non_latin_cascade`)。したがって「Primary転写が非ラテン文字」だけでは**呼ばない理由にしない**(逆にSecondary呼出のトリガーにする)。TTS側ドリフトの判定はSecondary転写で行う |
| S6 | ASR障害(Primary転写None/API失敗) | 音声の良否が不明 | ASR再試行(<=2、attempt外)。尽きたらHR_TECH | 現行はPrimary転写NoneがTTS_FAILURE扱いで音声不良と区別されない(確定)。区別して記録 |
| (削除) | 類似度<0.4(TTS異常疑い)での一律不呼出 | 現行はg7「湿度->死図塔」で誤って救済機会を失った(標本1) | 呼ぶ(Secondaryが正解を返せば採用) | 新規閾値は未採用。短文には適用しないTrialが必要 |
| (削除) | C1(entity_like/辞書読み/ラテン文字)の粗い除外、C2以外 | g8で救済できなかった。誤PASS実績なし | 呼ぶ。固有名詞のPASS扱いはS7(下)で別途ガード | 例外は「具体的な誤PASS事例+共通ルールで防げない理由」が必要(ユーザー方針) |
| S7 | 固有名詞・entity差(**Secondary一致でもPASSにしない**: PASS集合側の制約) | OPEN-257 Muse事例(3系統が同じ誤聴) | Secondary一致でもPASS_WITH_WARNING+最終試聴、辞書/Ledger/CMU確定語のみ自動PASS(U-17) | 日英非対称(英語=Secondary一致でPASS、日本語=C1除外)の統一案。**これは「Secondaryを呼ばない」ではなく「PASS集合の厳格化」** |

C2(同形異音語ガード)は2026-10-11にユーザーが採用した例外であり、ユーザー方針の「C1等の粗い除外ルールは廃止方向」の対象外として**維持する**(明示的に変える場合のみユーザー判断。5章 C-10)。

### 2-3. PASS集合(ラベル判定、`should_pass`ではなくclassificationラベルで判定=D10)
- **Primary PASS(現行どおり)**: EXACT_MATCH / NORMALIZED_MATCH / TRANSCRIPT_STYLE_NORMALIZED_MATCH / NUMERIC_EQUIVALENCE_MATCH(Tier1) / HIGH_SIMILARITY_SAFE / CONNECTED_SPEECH_ACCEPT系 等。長さ・言い淀み・Repetition QAのANDは維持。
- **Secondary PASS(新規・日英共通・厳格)**: **EXACT_MATCH / NORMALIZED_MATCH のみ**(日本語`SCG_PASS_CLASSIFICATIONS`と同じ。PHONETIC_MATCH・HIGH_SIMILARITY_SAFE・TRANSCRIPT_STYLE等はSecondary単独のPASSには含めない。U-3は(a)暫定、最小対Trial後に(c)を再検討)。
- **PASS_WITH_WARNING**: 最小対・形態素型差分(CONNECTED_SPEECH_PASS_WITH_WARNING等)およびS7(固有名詞のSecondary一致)。**最終試聴リストへ自動連動**(ユーザーが耳で確認)。PASS_WITH_WARNINGは再生成しない(安全≠成功原則に従い、最終試聴で未確認のまま公開しない運用が前提。連動の実装場所=最終試聴ページ生成工程は新規改修)。

### 2-4. A2 6%減速後検証の一本化(案B')
- 生成->(必要なら)stretch->**最終納品音声に対してのみ**S4/Primary/Secondaryを実行。減速前の検証はしない。
- 外側ループ(`generate_a2_segment_with_slowdown`が内側関数を最大3回呼ぶ)は廃止。1 attemptの定義を「TTS+trim+stretch」とする。OPEN-270(Coffee: TTS総5回、理論最大12)の構造原因が解消する(14-1)。
- stretchは決定論的処理なので、失敗は技術失敗(attempt外)として扱う。
- 影響: Review Lockの「RESOLVEDはブロックしない」特例(6%減速retry用)が根拠を失い孤立(D5)。

### 2-5. 技術失敗のattempt外扱い(上限)
- TTS 400("Model tried to generate text"含む)・空応答・5xx/429/timeout: **同一slotで最大2回再試行**(attempt消費なし)。2回超でHR_TECH。
- 400"Model tried to generate text"のような**決定論的**失敗を同一Promptで再試行しても無意味(同一入力で同じ結果)。この種だけ「1回で打ち切りHR_TECH」とするか、従来のminimal fallbackを隔離経路として残すか(U-4(d))はユーザー判断。**本設計は(d)を採用しない前提で、再試行上限2回+HR_TECHを基本形とする**(要判断)。
- 総ガード: segmentあたり技術失敗再試行の累計<=6(無限ループ防止)。

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
| P-a | 現行Minimal(=Primary段のPrompt) | 変更最小。ただしEnglish Lockが無くなる(翻訳的書起こしの対策はASR側①のみに依存) | 8/8 PASS。ただしraw beanはlocal whisperが「Robin」に聞こえ、「A catch?」とASRが疑問形 |
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
- **改修点(現行との差)**: (1)LR再TTSが`_run_a2_minimal_fallback_attempt`(minimal Prompt+force_secondary)を呼ぶ=「Style不変」の原則に反する。LR再TTSは**標準経路と同じPrompt/model/voice/速度の共通ループ**に置換(OPEN-274、D1)。(2)NG span選択はNGを出した**ASR転写基準**(OPEN-274)。(3)cool-down 600秒の位置(U-6)。(4)日本語は未対応のまま=HRへ。
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
| C-6 | CS:1692「TTS生成の同一segment総試行3回」(`PRODUCTION_MAX_TTS_ATTEMPTS=3`がSSOT) | **script版あたり3回**、LR発火時は最大6回(3+3) | SSOTの意味変更。Review Lockの`cumulative_tts_attempts`・`attempt_history`・HR判定のしきい値・費用ガードの上限計算(最大TTS call数が倍)を要確認 |
| C-7 | LR位置づけ: 標準2->10分cool-down->minimal1->LR(OPEN-256/274、2026-09〜10-11) | v0 3回後に最大1回、LR後3回 | cool-down位置(U-6)。LR再TTSの経路置換(D1)。OPEN-259(短文誤拒否)・OPEN-256(全文性)は維持 |
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
| コストC | ASR: 旧Cascade(Primary#2+Azure#1/#2)->(Primary+Secondary)で呼出減(日本語)。英語はAzure追加(約+0.2〜0.3円/segment見込み)。TTS: PASS時の再生成減。LR最大1回/segment(LLM+TTS3回) | 英語Azure単価約2.2円/回(報告02の見込み)。実測は最小対Trial要 |
| 時間D | cool-down(600秒)を廃止すれば最大約10分/segment短縮。維持なら不変 | U-6(効果の対照データなし) |
| 運用 | 技術失敗がattempt外になり一時障害でattemptを失わない。HR報告にLR発火詳細が付く | |

## 8. 残る判断事項(ユーザー)
1. 共通フロー全体を承認(日英同時か、段階導入か)。段階導入するなら(a)日本語先行 (b)英語先行 (c)Full Storyのみ先行。
2. KP 3回単一Prompt: Pを a/b/c のどれにするか(3-2)。
3. UNCERTAIN->HR直行の廃止(C-1)と例外案Cの要否。
4. PHONETIC等の許容範囲(C-3、U-3)。
5. LRの日本語適用をどうするか(Trial結果を見て)。
6. cool-down(U-6)、決定論的技術失敗(400)の扱い(2-5、U-4(d))。
7. C1の廃止(g8の13/14受入の最終確認、U-1)・C2維持。
8. 最小対Trial(8-3-A、約15〜20円)の実施可否。
