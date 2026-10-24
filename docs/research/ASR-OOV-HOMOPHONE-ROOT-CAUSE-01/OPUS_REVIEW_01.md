# OPUS_REVIEW_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 Phase 1 条件A独立レビュー、逐語)

出典: 委任_02の委任文末尾【Opusレビュー】(opus-consultantの報告を逐語。`docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_DELEGATION_02.md`)。

【Opusレビュー】、逐語)をFableが照合し、E2方針を承認、必須修正OF-OOV-01〜04を全て採用してPhase 2へ進む。到達上限VALIDATED。Production採用はユーザー判断(採用申請時にOF-OOV-05の3点を明記)。予算: Phase 2 合計上限40円(日次10-24把握分約618円+本委任≤40円<1,000円)。並行agent(極短clip速度Gate配線=er063系)あり、競合ファイルに触れない。

## 0. 記録(0円)
- Opusレビュー全文を `docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/OPUS_REVIEW_01.md` に逐語保存。Fable判断(同ファイル末尾): 「Claude案とOpusが実質一致。OF-OOV-01〜04採用、F1 ’修正は11-8の自律修正として別commit・別Regressionで先行、Phase 2はTrial専用コードのみ(Productionからimport 0)。E2のProduction形式(M1内の1ルール)はDESIGNに反映し、配線はユーザー判断後」。

## 1. F1 `tokenize` の ’(U+2019)修正(既存承認仕様の整合是正、Production共有file、別commit)
- `er011_b1_connected_speech_validator_01.py:103` 付近の `tokenize()` が ’ を語構成文字として扱うよう1行修正(他層 er006:497,1022 / er006_m1:60,331 と同じ正規化)。
- 影響分析gate: M1/Eq層のtest PASS、保存5,604行(F1 residual)の再判定でPASS→NG 0・NG→PASS 0(過去影響0件の確認を数値で)、全回帰(REGRESSION_BASELINE_2026-10-24比で自分起因の新規失敗0)、X/Z golden不変。
- `IMPL_F1_APOSTROPHE_01.md` に記録。OPEN新規(分類=修正へ進む→FIXED)。**単独commit**(message「ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02: F1 tokenize ’正規化…」)。E2 Trialの計測はこの修正後に行う。

## 2. E2 Trial module(Trial専用、Production未import)
- 既存 `trial_direct_ledger_phoneme_01.py` を改修(OF-OOV-01/02):
  - 置換は揃えた位置の1か所のみ(全出現置換を廃止)。
  - 置換後判定= classify should_pass **かつ** F1残差0(’修正後)。
  - Secondary転写が手元にある経路(forced-secondary、LR v1、A2 fallback)ではOF-183同様に矛盾時は不受理。
  - 最終ANDゲート(値・否定)を元転写と置換後転写の両方に適用。
  - 受理条件固定: Ledger confidence medium以上(low除外)/ASR語はCMU代表発音のみ・1:1置換のみ/対象roleはM1/Tier3と同じ範囲(KP・見出し・JAは対象外)/一致音素列は3音素以上。
  - 設計書 `DESIGN_02.md`: Production化の形式=M1内の1ルール(理由コード別、凍結候補・audit・`aggregate_by_ledger_key`・OF-183共有)、D-2'の拡張が必要な点、TRUE_CONTENT_MISMATCH→PASS_WITH_WARNINGの初経路である点(OF-OOV-05)、US/UKラベルのaudit残置(任意)。
- 単体test: 負例14件+境界(3音素、confidence low、複数出現、2語差、KP role)+凍結契約+「Productionからimportされない」test。

## 3. OF-OOV-03 全件リスト(API 0)
- 条件を満たすLedger全エントリのC2候補と、代表発音が完全一致するCMU語の組を全件列挙 → `E2_ACCEPTABLE_PAIRS_01.md`(Fable精査用。ledger_key・読み・US/UK・confidence・evidence_tier・一致CMU語・誤受理リスクの所感)。Ledger増加時の再生成手順を記載(script化)。
- OF-OOV-06の先行確認: OF-180(調査入力にASR転写を使わない契約)が `cascade_unresolved_entity` を書く経路まで含むかをコードで確認し、含まれなければそのentity_typeをE2対象外にする(記録)。

## 4. 検証(OF-OOV-04、合成正例・負例、上限40円)
- 正例: 「CMU未収録で、CMUに同じ発音の語がある」語から5〜8語(候補: Lyft/lift、Flickr/flicker、Tumblr/tumbler、thicc/thick、kewl/cool、boi/boy、skool/school。選定前にCMU未収録とLedger有無を確認。Ledgerに無い語は**既存の正式Ledger経路**で読みを登録=供給側Gの1語あたり実費も計測)。小文字語とentity(大文字)を両方含める。各1〜2文を既存Production TTS(本番モデル)→Primary ASR→E2判定。同じ語が2回出る文も含め「1件のみ」条件の取りこぼしを計測。
- 音声レベル負例3〜4件: 意図的に別の語として読ませた音声(例: 正準"Lyft"に対し音声は"loft")で、E2が受理しないこと。
- 既存保存データ: 110ペア再判定(OF-OOV-01/02適用後の受理件数変化、落ちる正例の有無)、本run Adv part3 8テイク。
- 指標: 救済率(正例)、誤受理0(負例)、TTS再試行・Azure呼出・費用の本run適用時の削減(カウンターファクチュアル)、1語あたりLedger登録費用、発生頻度に基づく70円/記事セットへの期待効果。`TRIAL_02_RESULT_01.md`、`BUDGET_LOG_01.md` 追記(callごと、cost logger必須=委任_01の概算を繰り返さない)。
- 使用モデル: Production routingと同一(TTS=本番TTS、ASR=gpt-4o-mini-transcribe)。旧世代モデルを使う場合は理由明記。

## 5. Status案・記録・Git
- agentはVALIDATED候補/不採用の事前判定を書く(最終はFable)。`OPEN_ITEMS.md` OPEN-498更新、DECISION_LOGは触らない(Fable評価後)。
- Git: F1修正は単独commit、Trial成果物は別commit。`git status`→`git commit --only`→`git push origin HEAD:main`(他agent差分を巻き込まない=一時index、禁止操作なし、secret grep 0件、wav不追跡)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_DELEGATION_02.md`(Nは先頭「ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02」を含むAgent呼出の0始まり通番、直近474以降)。

## 6. handback(ユーザー原文§6-B): 根本原因(要約)/既存仕様が機能しなかった理由/候補比較/Trial実測(正例救済率・負例誤受理・保存データ)/誤NG・誤PASS・Azure呼出・TTS再生成・費用への影響(本run適用時と頻度ベースの期待値)/X/Z/Y適用範囲/F1修正の結果/E2全件リストの要約/Status案/Production採用に必要なユーザー判断(OF-OOV-05の3点+D-2'拡張+配線形式)/費用/commit hash/raw URL。RESULT_PACKET 4行。

【Opusレビュー】
(以下、opus-consultantの報告を逐語)
## Opus独立レビュー: ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 Phase 1(条件A、読み取り専用)

### 結論
E2(Ledgerの出典付き読みとASR語の発音の完全一致)を推奨案とする方向は妥当です。同じ効果をもっと単純に得る案はありません。ただし、Phase 2の実装前に直すべき点が4つあり(下記OF-OOV-01〜04)、報告の書き方で1点訂正が要ります(OF-OOV-05)。
- **E2の判定ロジックは、実際に動くところまで確認しました。** M1の凍結候補を作る処理は本当に「期待綴りのCMU発音」しか見ていないため、M1ではgachaを救えません。
- **Phase 2で予定している正例の語(bento/karaoke/sudoku/emoji)では、E2がほとんど一度も発火しない可能性が高いです。** E2が働くには「CMUに同じ発音の別の語がある」必要がありますが、これらの語にはそれがありません。
- **報告の訂正:** 「M1・Tier3と同じ性質」という説明は正確ではありません。E2は、承認済み仕様の中で初めて「TRUE_CONTENT_MISMATCH(内容の不一致)をPrimaryの判定だけでPASS_WITH_WARNINGに変える」経路になります。

### 論点ごとの判定

**1. UDR #52・P2との整合 → 問題なし(採用の申請時に記載を追加)**
- 受理の根拠は出典付きのLedger読みと音素の完全一致であり、「綴りだけ」ではありません。ASR語の発音は観測値として使うだけで、候補を後から作ることはしません。このやり方はM1の`avs`と同じです。
- P2(ASR側のOOV)との違いは「ASR語がCMUに収録されていること」で、機械的に判別できます。
- E2が使うLedger読みは、Tier3(cascade)の調査で作られた読みです(gachaは`cascade_unresolved_entity`)。CURRENT_SPECのD-2'(Tier3の情報を自動PASSの根拠にしてよいのは「M1に限る」)をE2にも広げる必要があります。これはユーザー判断事項なので、採用の申請時に明記してください。

**2. reactive lookupで作られたLedger読みを根拠にしてよいか → 要修正**
- confidenceの下限はmediumで妥当です。M1はlowでも受理しています(Melos)が、E2のほうが受理の範囲が広いので、M1より厳しくするのが筋です。
- evidence_tierの条件は追加しません。厳しくするとgachaが外れます。また、出典にCambridgeの発音ページが含まれている以上、条件を足しても精度向上の根拠になりません。
- 代わりにOF-OOV-03(E2が受理しうる組合せの全件リスト)とOF-OOV-06(調査経路がASR転写を見ていないことの確認)を必須にします。
- confidenceはLLMが自分で付けた値なので、単独では信用しません。

**3. 処理順序と、独立証拠なしでの受理 → 要修正(順序はこのままでよい)**
- 「Primary NG→M1→E2→Secondary」の順序は正しいです。理由は3つあります。
  - Secondary(Azure)はgacha部分について情報を持ちません。PhraseListなしならgotcha、ありならgachaと書くだけです。
  - 置換した語以外の部分はPrimaryが既に一致を確認しており、これは通常の「Primary PASSならSecondary不要」と同じ基準です。
  - M1も既にPrimary#1の段階でSecondaryなしに受理しています。
- ただし、M1と同じ性質ではありません。M1はUNCERTAINからしか入らず、F1による説明が必要です。Tier3はSecondaryの裏付けが必要です。E2はTRUE_CONTENT_MISMATCHから入ります。ユーザー向けの報告ではこの点を明示してください(OF-OOV-05)。
- 誤PASSになりうる具体例は次の3つです。
  - (a) Ledgerの読みそのものが誤っていて、TTSも同じように誤って読む場合(英語風に崩した読みなど)。
  - (b) Ledgerを作る調査がASR転写の影響を受けた場合の自己強化ループ。gachaの読みはASRがNGを出した後のcascade調査で作られ、`pronunciation_hint`が"GOT-chuh"になっています。
  - (c) Trialコードが置換した語を全出現箇所で置き換えていること(`trial_direct_ledger_phoneme_01.py:40`)。現状は直後の再判定で安全側に倒れますが、契約としては不正確です。
- これを塞ぐ最小の追加条件はOF-OOV-01〜03(下記)です。

**4. US/UK複数読み → 問題なし**
- 「どれか1つの読みと一致すれば受理」は、ユーザー承認済みの原則(2026-10-13、#52)そのものです。
- UKUS機構は英米の綴りの対応表で、CMU収録語が対象です。E2はCMU未収録語だけが対象なので、両者は重ならず干渉しません。
- 学習者に1つの読みを保証するのはTTS・Ledger側の役割で、ASR受理の役割ではありません。
- 一致した読みのラベル(US/UK)をauditに残し、TTSのvoiceのアクセントと事後に照合するのはTrial後の任意項目です。

**5. Phase 2の検証設計 → 要修正(OF-OOV-04)**
- 保存データでPASS→NGが0件になるのは、E2が受理を足すだけの設計なので当然です。精度を示す証拠にはなりません。
- 負例14件は文字列レベルでロジックを試すtestであり、精度の証拠ではありません。
- 採用判断の主な証拠は、OF-OOV-03の全件リスト(API費用0)にするべきです。

**6. 供給側G(プラン段階でのLedger先行登録) → 問題なし(E2の結果を見てからでよい)**
- Gを入れるとLedgerの範囲が「entity」から「小文字の一般語」に広がり、E2が受理しうる範囲も同時に広がります。別のScope判断として扱うべきです。
- Phase 2では1語あたりの費用の実測だけ行えば足ります。Gを採用する場合は、OF-OOV-03の全件リストを作り直してください。

**7. E2が最も単純で十分か → 問題なし**
- E1(M1入口の緩和)では救えません。入口を通っても、gachaでは`_enumerate_subs`の`spell_prons`が空になるためです。コードで確認しました。
- A-1(a)フラグをONにしても救えません。分類がUNCERTAINに変わるだけでM1は一致せず、すべてのLedger語の分類を変えてしまう副作用もあります。
- er109の音素の出典にLedgerを足す案も考えられますが、純関数・凍結(OF-179)という前提を崩すため劣ります。
- **Production設計への提案:** E2は独立した並列モジュールではなく、M1の中の1ルールとして実装するのがよいです。理由コードは別にし、凍結候補・audit・`aggregate_by_ledger_key`・OF-183(Secondaryとの矛盾時は不受理)を共有します。こうすると受理経路のガード条件が食い違いません。

**8. F1 `tokenize`の’修正 → 問題なし(条件付き)**
- 既存の承認仕様の不具合修正(11-8)なので、AI側で自律的に直してよい範囲です。
- E2のTrialコードとは混ぜず、別のcommitと別のRegressionで行ってください(M1/Eq層のtestと保存5,604行)。
- E2の計測は修正後のF1で行いたいので、Phase 2の計測より前に終えるのが望ましいです。ProductionとTrialの証跡を分けておくためです。

### Phase 2実装前の必須修正
- **OF-OOV-01(受理判定の後処理をM1と揃える):**
  - 置換は、揃えた位置の1か所だけにします(全出現箇所は置換しない)。
  - 置換後の判定は、classifyのshould_pass「かつ」F1の残差0(’修正後)とし、M1の「F1の内側で動作」と揃えます。
  - Secondary転写が手元にある経路(forced-secondary、LR v1、A2 fallback)では、OF-183と同じく矛盾があれば不受理にします。
  - 最終ANDゲート(値・否定のチェック)は、元の転写と置換後の転写の両方にかけます。
  - これで落ちる正例があるかは計測してください。
- **OF-OOV-02(受理条件を固定する):**
  - Ledgerのconfidenceはmedium以上(lowは除外)。
  - ASR語はCMUの代表発音だけで比較し、1:1置換に限る。
  - 対象のroleはM1/Tier3と同じ範囲とし、KP・見出し・JAは対象外。
  - 一致する音素列は3音素以上とする(短い読み・IPA変換の副作用への安価な防御)。影響する件数を計測します。
- **OF-OOV-03(E2が受理しうる組合せの全件リスト、API費用0):** 条件を満たすLedger全エントリのC2候補と、それに代表発音が完全一致するCMU語の組を全件列挙します。Fableが精査し、これを精度の主な証拠にします。Ledgerが増えたときに作り直す手順も定めます。
- **OF-OOV-04(正例の選び直し):**
  - 正例は「CMU未収録で、CMUに同じ発音の語がある」語から選び直します。例: Lyft/lift、Flickr/flicker、Tumblr/tumbler、thicc/thick、kewl/cool、boi/boy、skool/school。CMUに未収録であることとLedgerの有無は、選ぶ前に確認します。
  - 小文字の語と大文字の語(entity)を両方含めます。
  - 音声レベルの負例を3〜4件足します。意図的に別の語として読ませ、ASRが同じ発音の語に寄せないことを確認します。
  - 同じ語が2回出る場合も含め、現行の「1件のみ」条件で救済を取りこぼすかを見ます。
  - 予算40円以内で足りる見込みです。

### 報告時の訂正(Phase 2の実装は止めない)
- **OF-OOV-05:** 採用の申請・ユーザー向けの報告では、次の3点を明記してください。
  - E2はTRUE_CONTENT_MISMATCHをPrimaryの判定だけでPASS_WITH_WARNINGにする初めての経路であり、M1・Tier3とは性質が違うこと。
  - D-2'(Tier3情報を自動PASSに使ってよい範囲)を広げる必要があること。
  - 統一判定のフローを変更すること。

### Trial後に見ればよい事項
- **OF-OOV-06(Production配線前の必須条件):** OF-180(調査の入力にASR転写を使わない、というtest上の約束)が、`cascade_unresolved_entity`を書き込む経路(gachaのエントリを作った経路)まで含んでいるかをコードで確認します。含まれていなければ、含まれるまでそのentity_typeをE2の対象から外します。Trial計測はこの確認の前に始めてよいです。
- 同じ語が複数回出る場合(同一の正準語と同一のASR語の組がk件)に受理を広げるかどうか。
- auditにUS/UKのラベルを残し、voiceのアクセントと事後照合するかどうか。
- 受理されたLedgerエントリのevidence_tier・confidenceの分布と、ledger_key別の集計。
- OPEN-339(Ledgerの自動登録エントリと人手登録エントリを区別するフィールド)との関係。
- G(先行登録)の採否。
- 発生頻度に基づいて、70円/記事セットへの効果の期待値を出すこと。
- Production化の形式(11-7の既定OFF・単一flag読取関数か、VALIDATEDで止めるか)。

### 要ユーザー判断
Phase 2の段階ではありません。E2をProductionに採用する時点で、D-2'の拡張と、TRUE_CONTENT_MISMATCHから受理に入る経路の追加をまとめて判断してもらいます。

---
## Fable判断(委任_02 §0の記載、逐語)
「Claude案とOpusが実質一致。OF-OOV-01〜04採用、F1 ’修正は11-8の自律修正として別commit・別Regressionで先行、Phase 2はTrial専用コードのみ(Productionからimport 0)。E2のProduction形式(M1内の1ルール)はDESIGNに反映し、配線はユーザー判断後」。
