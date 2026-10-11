# JA_SPEC_SURVEY_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01、日本語側、2026-10-11)

read-only調査。有料API未使用(API未使用)。Productionコード・Prompt・SSOT無変更。
行番号は2026-10-11時点の作業ツリー。略記: VAL=`er007_ja_asr_validator_01.py`、SEC=`er007_ja_secondary_asr_01.py`、LOCK=`er011_human_review_lock_01.py`、N3=`er003_v1_n3_01_tts_generate.py`、V01=`er003_v1_sing01_voice01_generate.py`、R01=`er003_v1_repro01_main_generate.py`、SPEC=`CURRENT_SPEC.md`、DL=`DECISION_LOG.md`。
DL行番号の注: DLの`[履歴]`見出し行(L58/59/66/132/148/149/166/167)は見出しだけの履歴チェーン行で、本文は`DECISION_LOG_HISTORY.md`側にある。承認日は見出しと関連コードコメントで確認した。

## 凡例
- 承認: U=ユーザー正式承認(`APPROVED_FOR_PRODUCTION`または逐語決定)、F=Fable/Opusレビュー判断で実装(ユーザー個別承認の逐語記録なし)、T=Trialのみ(未承認)。
- 配線: P=Production正式経路で配線済み、T=Trial/DEVのみ、部分=一部の経路・用途にだけ反映。
- 「確定」はコード行/ログ/SSOT行で確認した事実、「推測」は確認できていない解釈。

## 1) Primary ASRの判定条件

| ID | ルール | なぜ存在するか | 承認(DL/SPEC) | 配線(コード) |
|---|---|---|---|---|
| J-01 | Primary ASR=OpenAI `gpt-4o-mini-transcribe`(ja-JP)。`FEATURE_FLAG_JA_PRIMARY_OPENAI=True`でCascade有効 | 旧「文頭prefix一致+文字数」方式を、英語と同じ思想の全文Validatorへ置換(2026-08-25) | U(2026-08-25、SEC L28-33コメント「ユーザーがProduction配線を明示承認」)。DL L148(履歴見出し)、SPEC L1945/L1993/L2359 | P。SEC L28、R01 L363、N3 L540、V01 L515/L563 |
| J-02 | `EXACT_MATCH`(strip後完全一致)/`NORMALIZED_MATCH`(`normalize_ja`後一致)=PASS | 句読点・全角半角・引用符・「…」・助数詞前の単独漢数字(一〜九)は発話内容を変えない非発話/表記差 | U(OPEN-199是正、VAL L50-58コメント) | P。VAL L349-359、`normalize_ja` L95-124(`_PUNCT_RE` L55、助数詞漢数字L123) |
| J-03 | 文字単位`SequenceMatcher`のopcode毎にprotected check。数字差・否定差が1件でもあれば保護失敗=`TRUE_CONTENT_MISMATCH`(TCM) | 数量・肯否の反転は意味が逆転する重大差分 | U(2026-08-25) | P。VAL L256-268、L365-389。否定マーカー`_NEGATION_MARKERS_JA=("ない","じゃない","ではない","でない","せず","未","非","無","なく")`(`er003_audio_tts_asr_safety.py` L454) |
| J-04 | 数字のみの保護落ちに限り、variant layer(漢数字位取り等)で救済。否定差を伴う場合は救済しない | 「十件/10件」等の表記ゆれでTCM化するのを防ぐ | U(OPEN-145、2026-09-12`APPROVED_FOR_PRODUCTION`、SPEC L2010) | P。VAL L381-386、`er011_ja_asr_variant_layer_01.py` |
| J-05 | 読み(pykakasi、diff span前後4文字を文脈として付加)が一致する差=許容(PHONETIC_MATCH=PASS) | 漢字/かな/同音別表記のASR表記差はTTS誤りではない | U(2026-08-25) | P。VAL L273-283、L500-504 |
| J-06 | 辞書登録トークン(`expected_readings`)単体のdiffは確定読みと照合。不一致=`reading_dictionary_mismatch`(cascade対象外) | 辞書で読みが確定している語(例Meta=メタ)がCascadeの偶然一致で無条件PASSする欠落の修正(NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b) | U(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase 2) | P。VAL L202-239、L285-305 |
| J-07 | `entity_like`=replaceのcanonical/ASR両spanが「カタカナ率>=0.5または英字2字以上」。`phonetic_uncertain`=濁点/半濁点の有無だけが異なる読み。いずれもreplaceのみ(delete/insertは対象外、L320-322)。`cascade_eligible=entity_like or phonetic_uncertain` | 固有名詞/略語・濁点ゆれ(「頃」のkakasi読み限界等)は「TTSは正しいがASR表記が不確実」の可能性が高く、即TTS再生成の対象にしない | U(2026-08-25、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01、DL L149、SPEC L1993/L1998) | P。VAL L307-328 |
| J-08 | 非cascade diffが残る場合、(a)全文読み一致ならPHONETIC_MATCH(PASS)/全文濁点差のみならUNCERTAIN (b)variant layer救済 (c)Reading Resolver(辞書候補+限定LLM選択、`resolved_match`厳密TrueのみPASS=`READING_RESOLVED_MATCH`) (d)ratio<0.4=TCM(「TTS異常/hallucination疑い」ラベル)、それ以外TCM | 局所opcode分断による偽陰性の回避、A2の接続発話読み | U(ER-011-NO18-...-08、DL L66、flag VAL L48=True。OPEN-145 2026-09-12) | P。VAL L406-489 |
| J-09 | `ASR_VALIDATION_UNCERTAIN`(UNCERTAIN)は全diffが`cascade_eligible`の場合のみ(`should_pass=False, should_retry=False`) | retryで解決しない可能性が高い差をregenに回さない | U(2026-08-25) | P。VAL L491-498、L507-517 |
| J-10 | `length_ok`=ASR文字数<=原稿文字数+`max_extra_chars`(R01既定15、N3既定40)。`verified = verified_content and length_ok` | 末尾の余計な内容(hallucination)の検出 | U(既存) | P。R01 L331、N3 L537、V01 L236/L509/L562 |

## 2) Secondary ASR(SCG)の発火条件

| ID | ルール | なぜ | 承認 | 配線 |
|---|---|---|---|---|
| J-20 | Primary=`TRUE_CONTENT_MISMATCH`(`should_pass=False`)かつ`cascade_enabled`のときだけSCGを評価。UNCERTAIN経路は無変更(旧Cascadeのまま) | Primary NG時、TTS再生成の前にTTS誤りかASR誤認かを独立エンジンで切り分け | U(2026-10-11、SCG V1採用、DL L20550、SPEC L1994) | P。SEC L399 |
| J-21 | SCG不実行(NOT_APPLIED)条件: (1)数字差 (2)否定差(`negation_mismatches`) (3)類似度<0.4 (4)`reading_dictionary_mismatch` (5)`entity_like` (6)原稿側diffにラテン文字 (7)同形異音語候補(C2) (8)否定マーカー差(推奨4) (9)`length_ok=False` | (1)-(3)=Phase 0設計の既存除外。(4)(5)(6)=Opus必須1(C1)。(7)=C2。(8)=推奨4。(9)=推奨6(Azure無駄呼出防止) | (1)-(3)(7)(8)=U(2026-10-11 DL L20550「C2・推奨4も採用」)。**(4)(5)(6)=F(Opus必須1をFableが採用、ユーザー個別承認の逐語なし。DL L20550は「g8 13/14受入=ユーザー最終確認待ち」)**。(9)=F(推奨6) | P。SEC L183-210、L401-402 |
| J-22 | 実行=Azure Speech STT ja-JP連続認識、Phrase Listなし、1音声1回。SCG専用ラッパー`_azure_stt_strict`(途中Errorキャンセル=UNAVAILABLE) | Azure共通関数は途中cancelでも部分転写をerror=Noneで返すため | F(Opus必須2)。SCG全体はU | P。SEC L213-265、L289-328 |
| J-23 | Feature Flag `FEATURE_FLAG_JA_SCG_ENABLED=True`。環境変数`JA_SCG_ENABLED=0/false/off/no`で即停止。`cascade_enabled=False`でも不実行 | 緊急停止 | U | P。SEC L83-95、L403-404 |
| J-24 | SCG費用: 1回平均約0.16円(登録単価$1/h x 160円、秒切上げ見積)、遅延平均1.4秒。Azure実請求は未確認 | - | Phase 0 RESULT_01(5) | 見積のみ(scg_info.est_cost_jpy) |

## 3) Primary/Secondary一致・不一致時の最終判定

| ケース | 結果 | 根拠 |
|---|---|---|
| Primary PASS(EXACT/NORMALIZED/PHONETIC/READING_RESOLVED) | PASS、Secondaryなし | VAL L349-359/L440/L477/L502 |
| Primary TCM、SCG適用、Secondary=EXACT/NORMALIZED | PASS(`final_status=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`、attemptを消費しない) | SEC L416-423 |
| Primary TCM、SCG適用、Secondary NG(PHONETIC_MATCH含む)/UNAVAILABLE | TCM維持=再生成/fallback/STOP(attempt消費) | SEC L320-327、L424-425 |
| Primary TCM、SCG除外 | TCM維持=再生成 | SEC L405-406、L424-425 |
| Primary UNCERTAIN(entity_like/濁点差のみ) | 旧Cascade 4step: Primary#2->Azure#1->Azure#2。いずれかが`should_pass`(PHONETIC_MATCH含む)ならPASS。または2エンジン以上が`ORTHOGRAPHIC_VARIANT_CONFIRMED`。全不一致=Human Review(**TTS再生成しない**) | SEC L427-500 |

注(確定): 同じ「Primary不一致->Azure確認」でも、UNCERTAIN経路のAzureはPHONETIC_MATCHをPASSにする(SEC L473/L489は`cls.should_pass`)が、SCGのAzureはEXACT/NORMALIZEDのみ(SEC L78)。かつUNCERTAIN経路は非strictの共通関数(`p4.get_full_text_via_azure_stt_continuous`、SEC L467/L483)でAzure途中cancelを区別しない。SCGだけ厳格という非対称がある。

## 4) 固有名詞・一般語・数字・否定・時制・同音異義語等の特別扱い

| 対象 | 現行の扱い | 根拠 |
|---|---|---|
| 数字 | 差があればTCM。SCG不実行 | VAL L256-261、SEC L191-192 |
| 否定 | `_NEGATION_MARKERS_JA`のいずれかがdiff spanに片側のみ含まれればTCM。SCGは追加で形態素解析の否定助動詞(ず/ぬ/ん/ざる/まい)の片側差を除外 | VAL L263-268、SEC L102-165、L206-209 |
| 否定の既知ギャップ(確定、合成確認) | 「来なかった」->「来た」はdiff span「なかっ」に上記マーカーが含まれず、SCG推奨4の形態素規則も「ない」系(助動詞-ナイ)を対象外。TCMのままSCGが**実行される**(安全弁はAzureが実際に「来た」と転写してNGになること) | `er056_ja_scg_offline_replay_01.py`の合成確認(JA_OFFLINE_COMPARISON_01.md 付録) |
| 固有名詞(カナ/英字略語、置換のみ) | 単独ならUNCERTAIN=旧Cascade。他の非cascade diffと混在するとTCM+SCG除外(C1) | VAL L307-328、SEC L200-201 |
| 固有名詞(カナ挿入/脱落: メタ->メタン) | delete/insertはentity_like=False(VAL L320-322)。TCM+**SCG実行**(C1除外にならない)。辞書登録(`expected_readings`)があれば`reading_dictionary_mismatch`で除外 | 合成確認 |
| 固有名詞(漢字、同読み) | PHONETIC_MATCHでPrimary PASS | VAL L500-504、合成確認(李/里) |
| 一般語(漢字近音: 出演/出現) | TCM。SCG適用(OPEN-258の動機) | OPEN_ITEMS L760 |
| 濁点/半濁点(ガス/カス) | 単独=UNCERTAIN=旧Cascade。他diffと混在=TCM+C1除外 | VAL L315、SEC L200 |
| 時制/活用(終わった/終わる) | 特別扱いなし。TCM+SCG適用 | 合成確認 |
| 同音異義語(漢字違いで読み一致) | PHONETIC_MATCHでPrimary PASS(正しい漢字かは検査しない) | VAL L500-504 |
| 同形異音語(原稿側漢字の別読み候補) | SCGのみC2: 原稿側spanの辞書上の読み候補にPrimary転写側の読みが含まれればSCG不実行。辞書欠落(例:「行った」[おこなった]=候補なし)は除外されない(OPEN-263) | SEC L168-180、OPEN_ITEMS L766 |
| ラテン文字 | 原稿側diffにラテンが含まれればSCG不実行(C1) | SEC L202-203 |
| 長音(コーヒ/コーヒー) | NORMALIZED_MATCH(variant layer C、4文字以上) | SPEC L2010、SEC推奨8注記 |

## 5) TTS再生成の条件と回数上限

- 同一segment総試行回数=3(初回含む。`PRODUCTION_MAX_TTS_ATTEMPTS=3`)。SSOT: LOCK L80、SPEC L1692。ユーザー正式決定(2026-09-04 ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25/FINAL-26、DL L58/L59、ER-008-...-15 DL L167)。各JA生成関数が`min(max_attempts, 3)`でクランプ(N3 L512、V01 L475)。
- 内訳=標準経路2回(`PRODUCTION_STANDARD_TTS_ATTEMPTS`)+minimal instruction fallback1回(`PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS`)。LOCK L102-104。
- 再生成が起きる条件: attemptが`verified=False`かつ`stop_retrying=False`(=TCM、またはTTS/ASR失敗、またはlength_ok=False)。UNCERTAINで`stop_retrying`が立つとregenせずHuman Review。
- 累積Budget Guard: segment累積TTS>15回、ASR>60回でHuman Review強制(LOCK L68-69、L285)。
- SCGはattemptを消費しない(Primary NG後の追加確認)。SCG NG/UNAVAILABLE時に従来どおり次attemptへ。

## 6) fallback(JA minimal)・Local Rewriteの発火条件

- JA minimal instruction fallback: 標準経路が`status==OK`でも`HUMAN_REVIEW_LOCKED`でもないとき、残り予算`max_attempts - len(attempts_log)`(既定1回)を発火。N3 `generate_a2_japanese_with_fallback`(L473-)、V01 `generate_charon_japanese`(L434-)。fallback自体にもASR+Cascade+SCGが走る(N3 L540、V01 L563)。
- fallbackの中身: `_A2_JA_MINIMAL_INSTRUCTION_PREFIX`(A2)/`MINIMAL_INSTRUCTION_PREFIX_JA`(B1、V01 L395-398)。**Role Style(J3)の`style_prefix_override`を渡さない**(標準経路にのみ転送。N3 L532(fallback呼出にstyle引数なし)、L516(標準経路のみ転送)、L406-412コメント)。Voice(Charon/Aoede)・モデル・テキストは同じ。ユーザー確定仕様「JA minimalは既存テキスト流用」(FAMILY-X-02 D-1、2026-09-28、N3コメントに記載。DLへの逐語記録は未確認)。導入理由は短いA2日本語フレーズのinstruction leakage対策(ER-003-N3-ROOT-FIX-01、DL L132)。
- Local Rewrite: **日本語は未配線**。Local Rewrite Recovery(cool-down 600秒+Luna局所書換+7 Gate)は英語TTS role専用(SPEC L1971、OPEN-260=OPEN候補・未承認、OPEN_ITEMS L762)。JAにはcool-downもない。

## 7) Human Review移行条件

| 条件 | 動作 | 根拠 |
|---|---|---|
| 3 attempt後も`status != OK`(STOPPED) | `record_outcome`が`HUMAN_REVIEW_REQUIRED`ロック。以後`check_before_generation`が`REGENERATE_APPROVED`なしの再生成をブロック | LOCK L255-310、L199-250 |
| UNCERTAINで旧Cascade 4step全不一致(`human_review_required`) | `_log_human_review`でキュー`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`(英語は`er006_output/audio_retry_cascade_prod_01/...`で別パス)へ。TTS再生成せず`status=ASR_VALIDATION_UNCERTAIN`を返却->同ロック | SEC L39-55、L498-517、N3 fallback loop |
| Budget Guard(累積TTS>15/ASR>60) | ロック | LOCK L68-69、L285、L301-304 |
| SCG | **新規のHuman Review投入なし**(安全条件) | DL L20550 |

## 8) 初回・retry・fallback・regeneration・resume間の仕様差

| 経路 | ASR判定 | SCG | 旧Cascade | Style | 差・注意 |
|---|---|---|---|---|---|
| 初回(標準1) | 全部 | 有 | 有(UNCERTAIN時) | role style(Family X: `_role_style_ja()`=J3) | - |
| retry(標準2、同Prompt) | 同上 | 有 | 有 | 同じ | 同一Prompt固定 |
| fallback(minimal、3回目) | 同上 | 有(N3 L540) | 有 | **minimal(J3を喪失)** | style不連続。導入理由はleakage対策 |
| Local Rewrite | - | - | - | - | **JA無し** |
| resume(Human Review後) | 通常 | 有 | 有 | 通常 | ロック中は0 API(`check_before_generation`)。`REGENERATE_APPROVED`を消費して再開。canonical変更でロック無効 |
| Azure取得 | SCG=strict(部分cancel=UNAVAILABLE) | | 旧Cascade=共通関数(部分転写をerror=Noneで返しうる) | | 非対称(Opus必須2は共通関数を変えない判断) |

## 9) Family・role別の適用範囲と例外

- 呼出元(Production、`evaluate_attempt_ja_with_cascade`の呼出): R01 L363(A02汎用strict loop、language=="ja")、N3 L540(A2日本語fallback loop。標準経路はR01を経由)、V01 L515(標準)/L563(fallback)(B1 Charon)。SCGは4箇所で同じ(`length_ok`転送済み、推奨6)。全数調査は`er053_output/open258_scg_production_wiring_01/CALLPATH_01.md`。
- Family X: japanese_title/preview/comment_1-4/Standard KP日本語意味が`generate_a2_japanese_with_reading_safety`->`with_fallback`を通り、J3 style(TTS-VARIABLE-SPOKEN-ROLE-STYLE、PRODUCTION_WIRED)を標準経路にのみ適用(`er019_family_x_audio_production_runner_01.py` L941-961、L1045)。J2_BRIGHT(Tone Trial、2026-10-11 approved-but-unwired、`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_X_INVENTORY_01.md` L85)は未配線。Family ZはTTS/Assembly未配線(OPEN-185)で対象外。
- 例外: 英語segmentの`enable_connected_speech_equivalence_layer`等は日本語に影響しない。日本語ではroleによるCascade可否の切替は無く、全JA segmentが同一Validator+SCG。

## 「承認根拠なし/Trial専用/部分反映」一覧(明示)

1. **C1除外(entity_like/辞書読み/ラテン)**: Opus必須1->Fable採用。ユーザー逐語の個別承認なし。DL L20550は「g8 13/14の受入=ユーザー最終確認待ち(USER_DECISION_REQUIRED)」。未承認寄りの例外。
2. **否定の形態素規則の対象範囲**: 推奨4としてU採用だが、「ない」系の活用を含まない(承認範囲の問題ではなく未対応のギャップ)。
3. **SCGのPHONETIC_MATCH非PASS**: ユーザーの安全条件(DL L20550)。ただしPrimary/旧Cascadeは同じPHONETIC_MATCHをPASSにしており非対称(論点としてC)。
4. **Trial専用に留まるもの**: PHONETIC自動PASS、Whisper 2-of-3、Phrase List、助詞/漢数字の追加除外(Phase 0 RESULT_01)。Productionに無い。
5. **部分反映**: Azure strict化はSCG内のみ(旧Cascade未適用)。SCG証跡はmaster store manifestに記録されるがHuman Reviewキューには入らない。J3 styleはfallbackに反映されない。
6. **未配線/未承認**: Local Rewrite(JA)=OPEN-260。同形異音語辞書補強=OPEN-263(未承認)。J2_BRIGHT=approved-but-unwired。
7. **SSOT側に逐語記録を確認できなかったもの**: FAMILY-X-02 D-1「JA minimalは既存テキスト流用」(コードコメントのみ)。
