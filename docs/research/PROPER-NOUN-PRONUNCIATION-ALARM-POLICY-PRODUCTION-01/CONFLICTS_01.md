# CONFLICTS_01: 新方針(固有名詞発音アラーム)と既存承認済み品質条件・既存機構の衝突調査(委任_01、API 0・JPY0)

前提: ユーザー承認(2026-10-22)で緩和されるのは「固有名詞の発音不一致**だけ**による停止・Human Review」。KPの発音検査(Primary/Secondary両PASS)・一般英単語の誤発音・文意を変える重大な読み間違い・音声欠落/構造不良は従来どおり(原文§4)。以下、各ケースの「現行挙動 / 新方針適用時の案 / 選択肢 / 判断要否」。判断要否は`PM_GOVERNANCE 27-3`の A既判断 / B承認範囲内で自己解決 / C現タスクと独立 / D真に新しい判断。**D(ユーザー判断が本当に必要)に該当するものは本調査では無し**(下記末尾に整理)。

## (a) Key Phraseに固有名詞が含まれる場合
- 現行: KP英語phraseは`dual_required`(Primary・Secondary両方PASS必須、OPEN-440)。統一judgeは`dual_primary_not_pass`等でNG→再生成(slot4回構成)→最終HR。entity_like差でも救済しない(`er006_secondary_asr_01.py:1050`のcascade_eligibleはPrimary救済のみで、dual時はAzure救済をPrimaryPASSにしない[`er078_asr_unified_judge_01.py`の`primary_rescued_by_secondary`])。
- 実態: 保存した実run 132 distinct KP英語phraseのうち大文字を含むのは2件(`take off an AI costume`=略語AI、`Behind the Scenes`=題名調)で、固有名詞phraseは**0件**(`tts_generation_results.json`のkey_phrases[*].english.text 全走査、2026-10-22)。例として挙がっていたbyUsはKP phraseではなく記事内の商品名(KPは`take part`/`think up`/`blurt`等の一般表現)。
- 新方針適用案: **KP phrase(`dual_required`・role=KEY_PHRASE・`kp\d+_(en|ja)`)はアラーム受理の対象外**(`er103_proper_noun_alarm_policy_01.evaluate_alarm_eligibility`のG0で`R_DUAL`/`R_ROLE`)。KP解説文(`kp*_en`のexplanation、role=KEY_PHRASE)も同様に対象外。
- 選択肢: ①対象外のまま従来どおり(推奨。原文§4の「独断で緩和しない」に一致、頻度0/132で運用影響なし) ②KP phrase中の固有名詞だけ受理し、アラームは併記(KP条件の緩和になるため承認が別途必要)。
- アラーム併記: KPがHRに回る場合のHR package(Stage 1の調査結果)は現行のまま。アラーム記録は作らない(HRと二重通知にしない)。
- 判断要否: **B**(原文§4の維持側に倒す=承認範囲内)。

## (b) 日本語segmentの固有名詞(メロス→メオス等)
- 現行: JA経路は別adapter(`er007_ja_secondary_asr_01.py`)・別判定器(`javal`)。`entity_like`差はHR温存(`:366-372`、`is_entity_like_mismatch_ja`)。JA HR queue全12行(`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`): ASR_VALIDATION_UNCERTAIN 8(2026-08〜09)、TRUE_CONTENT_MISMATCH 4(2026-10、台風期/タイフーン機等=固有名詞ではなく読み差)。2026-10のJA固有名詞UNCERTAINは0件。
- Stage 2 Trial・Stage 1・本方針の根拠データはすべて**英語TTS/英語ASR**。JA読み(katakana)はLedgerで`ja_reading_katakana`として別管理(`EXCLUDED_ENTITY_TYPES`、TTS供給の対象外)。
- 新方針適用案: **本委任の設計・実装は英語経路のみ**。JAは`R_LANG`で不受理(従来どおり)。
- 選択肢: ①英語のみ(推奨。JA固有名詞UNCERTAINは実測で月数件以下、別判定器の境界校正が別途必要で、同一承認文の「Trialで検証した方式」はEN限定) ②JAも同方針を適用(JA判定器用に境界・供給[読みのカタカナ供給]を別設計・別校正する後続委任)。
- 判断要否: **B**(承認文は「Stage 2 Trialで検証した方式」の採用と明記。JAは検証対象外のため、範囲内で英語から実施)。ただし「対象：Family X/Z共通」の文言との差分なので、Fableが受入記録に「JAは未対象(後続候補)」と明記すること。

## (c) Family Zの対話文での人物名(Melos/Selinuntius)のアラーム多発見込み
- 現行(保存queue): Melos実イベント11件(2026-10-12〜19)。M1(2026-10-14配線)後の実イベントは3件。
- 新方針適用(受理判定をAPI 0で再適用): 11件中**8件がアラーム受理**、3件は不受理(いずれも同一clip「…held out for the chains. His friend…」でSecondaryが`Melos drank`を`mellow strength`と聞く=隣接語まで別語)。不受理3件は従来どおりHR。
- 多発見込み: Z記事1本でMelosを含むclipは約8(現行TTS take1で8 segment、HR 4)。新方針後の1記事あたりアラームは**Melosのみで概算0〜4件**(同一固有名詞は記事内の別clipで別alarm_id、集計はnoun単位で「Melos×k clip」と1行にまとめて表示する設計: DESIGN §6-3)。1日15作品全体の頻度は未検証(原文§3-3)。
- 選択肢: ①clip単位record+報告ではnoun単位に集約(推奨) ②clip単位のまま全列挙(件数増で報告が冗長)。
- 判断要否: **B**(表示集約は報告フォーマット設計)。

## (d) 数値・否定を含むsegment内の固有名詞
- 現行: 数値/否定差は`protected_check`で`TRUE_CONTENT_MISMATCH`、統一judge P1で`NG_PROTECTED`(Secondary不呼出)。
- 新方針: 受理条件のG1(judgeが`NG_BOTH/secondary_not_accepted`)とG2(Primaryが`ASR_VALIDATION_UNCERTAIN`のentity_like diffのみ)により、**数値/否定差が1つでもあれば入口で不受理**。固有名詞が含まれていても同一segmentの数値誤読は従来どおり止まる(再生成・HR)。ASR側のspanが数値/否定語を含む場合も`R_ASR_HAS_NUMBER_OR_NEG`で不受理。
- 実データ: 保存HR queue「24 hours and 48 minutes」系3行はPrimaryが数値差で不受理(受理判定で確認)。
- 判断要否: **A**(原文§4「文意を変える重大な読み間違い」維持)。

## (e) 音声欠落(語の脱落)と「固有名詞の脱落」の区別
- 現行: 固有名詞語がASRに出ない(脱落)場合、canonical側のみ内容語でentity_like=Trueのdiffになり得る(`val:734`)。つまり**音声欠落(読み飛ばし)と、ASRが固有名詞を書き落とした事象は判定器上は区別できない**。
- 新方針: 受理条件G5で「canonical語・ASR語とも非空の置換のみ」。**語の脱落(ASR側が空)は不受理**(`R_DELETION`(`WORD_DELETION_OR_NO_ASR_TOKEN`))。保存queueでは9イベントが該当(`## Main Story`見出し、`One Voice:`ラベル、`Amazon … plus`等=固有名詞ではない語/ラベルの脱落)。固有名詞を読み飛ばした音声欠落は従来どおり再生成・HR。
- 副作用: 固有名詞が本当に落ちたケースも(区別できないので)アラームではなくHRに残る=安全側。
- 選択肢: ①脱落は不受理(推奨、fail-closed) ②脱落もアラーム受理(音声欠落を見逃すため§4に反する→不可)。
- 判断要否: **A**(原文§4「音声欠落」維持)。

## (f) Secondary(Azure)Phrase Listとの関係
- 現行: Ledger登録surfaceはAzure Phrase List(weight 2.0)としてSecondaryに渡る(`azure_phrase_list`、`er006:1094,1105`相当、`ledger_phrases`)。Phrase Listにより登録語はAzureが綴りで書き取りやすい。
- 新方針: Phrase ListはLedgerの**登録有無**で決まり、`ledger_disabled`以外は階層に関係なく渡る(PLIR1)。TTS供給(綴り置換)とは独立した層(Phrase Listは判定側、置換はTTS入力側)。
- 衝突点: 供給で綴り置換したsurface(例 Khaite→Kate)がcanonical側から消えるため、Phrase Listのsurface(Khaite)がcanonicalに現れない。Phrase Listに置換後の語(Kate)を渡す必要はなく(一般語)、**Phrase Listは原surface(Khaite)のまま渡す**(ASRが原綴りKhaiteと書く場合のsecondary acceptを助けるため)。受理判定側は`supply_map`で「Kate=Khaite」を固有名詞扱い(DESIGN §2-5)。
- 判断要否: **B**。

## (g) OPEN-371(技術STOP→HR Lock)との関係
- OPEN-371の事実: Secondary障害のみのclipはHR queueへ入れず技術STOP(承認不要・再実行で再開)にしたが、leaf内`record_outcome`がHUMAN_REVIEW_REQUIREDをLockするため、再実行時に`HUMAN_REVIEW_LOCKED`で0 APIのまま止まる問題が未解決(OPEN-371は未実装・未承認のUSER_DECISION_REQUIRED)。
- 新方針との関係: アラーム受理は**Secondaryが取得できた場合のみ**(`R_SECONDARY_MISSING`/`NG_SECONDARY_UNAVAILABLE`は不受理)。技術STOP経路は無変更。アラーム受理は`status=OK`でleafに返るためHR Lockの対象外。つまりOPEN-371の問題を新方針は**悪化も解消もしない**(独立)。
- 判断要否: **C**(OPEN-371は現タスクと独立)。

## 発見分(委任文に無かった衝突・注意点)
### (h) 共有adapterの適用範囲 — Family A/B/C への波及
- `evaluate_attempt_with_cascade_detail`はFamily A/B/C(legacy)の共有leafからも呼ばれる(`er003_v1_*`)。ここへ無条件に受理分岐を入れると、**承認範囲(X/Z)外のFamily A/B/Cの挙動も変わる**(27-7: 委任文に明示がなければA/B/Cを開発対象にしない)。
- 案: 新flagに加えて**run scope**(X runner/Z runnerのmain冒頭で`er103…enter_scope("X"|"Z")`、既存`secondary_run_scope`と同型)を要求し、`is_active_for_run()`=flag∧scope∈{X,Z}(`er103_proper_noun_alarm_policy_01.enter_scope`)のときだけ受理分岐が有効。scope未設定(A/B/C・単体呼出)は従来と完全に同じ。選択肢: ①scope限定(推奨、承認範囲に正確) ②全Family共有(AUW統一judge/M1/Stage 1の前例と同じだが、承認文は「Family X/Z」)。
- 判断要否: **B**。

### (i) 文頭の大文字語・一般語の固有名詞誤分類リスク
- `capitalized_flags`は文頭の大文字語(`_STOPWORDS`以外)を固有名詞候補にする(`val:468-492`)。"Retail sales fell."の`Retail`が`entity_like`になるため、判定器の`entity_like`だけで受理すると一般語の誤読を許容してしまう。
- 案: 受理側で追加検査(DESIGN §2-3): (1)句の全tokenが一般語(CMU収録∧zipf>=4.0)なら不受理(`mini→many`を除外した実績) (2)文頭の大文字だけでは根拠にせず、CMU未収録・Ledger登録・文中の大文字・孤立ALLCAPSのいずれかを要求 (3)イニシャル`L. Mimoun`の`.`は文末扱いしない。
- 残るリスク: 文頭にあるCMU収録のブランド名(Meta/Apple/Amazon等)は、Ledger未登録だと不受理=HR残(fail-closed、受理の取りこぼしであって誤受理ではない)。
- 判断要否: **B**。

### (j) Ledgerに`human_approved`/`tts_respelling`が保存されない
- `er006_pronunciation_ledger_01.upsert`は`human_approved`・`tts_respelling`を保存しない(任意キー3つのみ)。承認文「B階層は人間承認済みの場合のみ登録・供給」を成立させるには、**Ledgerスキーマにadditiveキー2つ(+承認者・承認日時)を追加し、運営者が承認する小CLI**が必要。実Ledger38件は`evidence_tier`未保存のため、初期状態で自動供給対象は0件(効果は将来の調査・承認から)。
- 判断要否: **B**(承認文の実装に必須の付随変更)。

### (k) 既存PASS_WITH_WARNING節が公開ページに出ている
- 事実(INVESTIGATION §4): 既存の事後試聴リストは公開index.htmlの補助節。アラームを同じ構成に載せない(別ファイル`audit/pronunciation_alarms.json`・`audit/operator_alarm_report.md`のみ)。既存のPASS_WITH_WARNING節(SECONDARY_CONFIRMED等)は無変更。
- 判断要否: **B**。

### (l) 再利用(Store/resume)時の再判定
- 検査: INVESTIGATION §1-2。`rejudge_with_current_judge`が元stateを`PASS`/`PASS_WITH_WARNING`のみ継承(`validation_inheritance:236,305,323`)。アラームstateを許容集合に加えないと継承NG→不要な再生成になる。配線で3箇所の許容集合に`PASS_WITH_PRONUNCIATION_ALARM`を追加し、保存済みrecordを再利用する(再判定は値/否定ガードのみ)。
- 判断要否: **B**。

### (m) A2の6%減速後の再判定
- 減速後wavも`_post_slowdown_unified_judge`(`er003_v1_n3_01_tts_generate.py:122`)で同adapterを通る。減速前に受理したアラームは、減速後の再判定で再度受理される(alarm_idはwav sha含むため別id)。採用音声は減速後なので、run層deriveは採用entry(減速後)のrecordだけを報告に載せる。共有ログ`pronunciation_alarms.jsonl`は履歴(superseded含む)で、報告の正はrun層`audit/pronunciation_alarms.json`。
- 判断要否: **B**。

## 判断候補(ユーザー判断が本当に必要なもの)
**なし**。(a)(b)(h)は承認範囲内の安全側選択(維持/EN限定/X・Z限定)で自己解決でき、承認原文§4・§1の範囲を広げない。Fableが受入記録へ明記すべき前提: KP固有名詞=対象外、JA=未対象、Family A/B/C=未対象。これらを「広げたい」場合のみ別途ユーザー判断(新Scope)になる。
