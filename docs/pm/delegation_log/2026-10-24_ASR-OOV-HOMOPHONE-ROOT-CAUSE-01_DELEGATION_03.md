管理ID: ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_03 — Phase 3: Opus条件Cレビュー(OF-OOV-07〜11)の反映。**Trial専用・Production変更0・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/USER_DECISION_REGISTER)編集0・ACTIVE_TASK.md編集0**(別agentが並行して同ファイル群を編集中。SSOT反映はFableが後続委任で行う)。上限10円(OF-OOV-11のTTSのみ有料。他はAPI 0)。

## 背景
Phase 2(`docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/TRIAL_02_RESULT_01.md`、`DESIGN_02.md`、`trial_direct_ledger_phoneme_01.py` v2)に対し、Opus条件Cレビューで採用申請前の必須修正5点が出た。レビュー全文は本委任文末尾に貼る。まず `OPUS_REVIEW_02.md` として同ディレクトリへ逐語保存(先頭に「Opus条件Cレビュー、2026-10-24、Fable経由受領」と記載)。

## 作業
1. **OF-OOV-07(fail-closed化)**: `trial_direct_ledger_phoneme_01.py` のE2W判定を修正。独立エンジン(ローカルfaster-whisper)の転写がNone/失敗→不受理。`uncertain_no_agreement`→不受理。受理条件=「揃えた正準語の位置でWhisperが正準語を書いた、または同じLedger読みと一致するCMU語を書いた」の**正の一致**のみ。単体testを更新(None→不受理、不一致→不受理、正の一致→受理)。
2. **OF-OOV-08(1語位置での一致判定+本run長segment再評価、API 0)**: 一致判定を文全体の`classify_asr_match`ではなく、揃えた正準語位置の1語範囲で行うよう変更。そのうえで保存済み本run(『英単語ガチャ』`er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/` のAdv full_story_part3 8テイク等、gachaを含む全NGテイク)にローカルWhisper(既存Production利用と同じ `er006_secondary_asr_01.py:541-551` 付近の経路・同モデル)を当て、E2Wの救済件数を再計算。Ledger登録(gacha entryの作成時刻、`ROOT_CAUSE_01.md:17`)の時系列を踏まえ、「各語の最初の発生は救えない」前提で -22.6円 を再計算(最初のsegmentの救済を含めない)。長segmentで救済がほぼ0なら、その事実を明記(Fableが(B)へ切替判断)。
3. **OF-OOV-11(負例追加、上限10円)**: Trial用Ledger語に対し1音素違いの近い語の負例約20件(例: thick→tick、school→scold、fat→vat/fit、cool→cull、fire→fair、lift→laughed)+正例約10件(X/Z本番voiceを1つ以上含め、Aoedeのみにしない)。既存Trialと同じTTS経路・cost logger `install`を**必ず**実行(前回の忘れを繰り返さない)。TTS直列化flagを尊重(他agentがJA clip TTSを並行実行中)、同一run起動間隔150秒、RESTART_STORM回避。E2単独/E2W(修正後)それぞれの誤受理数・救済数を集計。ローカルWhisperがNoneを返すtest(API 0)も追加。
4. **OF-OOV-09(申請文の訂正)**: `ADOPTION_NOTE_01.md`(新規、申請文草案)に: er109(2026-10-23承認、X/Zのみ、`er006_secondary_asr_01.py:1135`)がPrimary判定のみでTRUE_CONTENT_MISMATCHを受理する先例であり、E2の新規性は「Tier3調査由来のLedger読み(二次情報)を根拠にする点」に訂正/E2はOF-184で保留された方式の再導入であり測った需要=1/188 run/配線案=er109ブロック直後(1131-1142行)に置き`ortho_scope.is_active_for_run()`のX/Z範囲判定を再利用、M1 moduleに判定ロジック配置、rollback flagはer109と同形/独立確認=ローカルWhisper(新規Production依存ではない根拠を明記)/無効負例3件の限界(3エンジン一致時は判別不能、WhisperはPrimaryと同系統で完全独立ではない)/E2受理にWarningラベル+最初N件の事後試聴を選択肢として記載/各語の最初の発生は救えない。
5. **OF-OOV-10(Store再利用制限の設計のみ、実装0)**: Master Audio Storeで、E2受理テイクを範囲外(A/B/C・rollback後)で再利用しない、該当Ledger entryが無効化・更新されたら再利用をブロック、auditにledger_keyを残す設計を、er109の`OUT_OF_SCOPE_BLOCK_REASON`の形に倣い `DESIGN_03.md` に記載。
6. `TRIAL_03_RESULT_01.md`: 修正後E2Wの正例/負例/本run長segment結果/再計算した費用効果/頻度/Family X・Z・Y適用範囲/限界/Status案(VALIDATED_LIMITED or 採用価値なし→(B)相当)を事前基準どおり記載。`BUDGET_LOG_01.md`に追記。
7. commit/push: 自分が変更・作成したファイルのみ `git add <path>`→`git diff --cached --name-status`確認→`git commit --only -- <path…>`→`git push origin HEAD:main`。index lockがあれば待って再試行。wav/mp3/raw_usage_logは追跡しない。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret grep 0件。
8. 委任文を `docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_DELEGATION_03.md` に逐語保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新> --out <path>`、先頭行一致を確認)。報告は `docs/pm/RESULT_PACKET_AOHR3.md`(RESULT_PACKET.mdは使わない)。

## 制約
`.venv\Scripts\python.exe`を使う。他プロセス終了禁止。Production file(`er006_*`, `er109_*`, `er011_*`等)は読むだけ。公開物・本run成果物は読むだけ(コピーで作業)。費用10円超過見込みなら起動前に停止して報告。

## Opusレビュー全文(逐語保存用)
<<<
## Opus 条件Cレビュー: ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 Phase 2(読み取り専用・API 0・ファイル作成なし)

### 結論
- E2W(E2に加えて、別のASRエンジンが矛盾しないことを必須にする方式)の方向性は正しいです。ただし、採用申請に出す前に直すべき点が5つあります(OF-OOV-07〜11)。
- 最も重要なのは**OF-OOV-08**です。正例6/6の救済と「本run適用時-22.6円」は、短い合成clip(1〜2文)での結果です。本番のような47〜50秒の長いsegmentでは、E2Wで同じように救済できるかがまだ確かめられていません。ローカルWhisperの文全体の転写を判定にかけているため、gacha以外の箇所の小さな誤りでも「矛盾」と扱われ、救済が消える可能性があります。Azureのattempt 5で、実際にこれが起きています。
- **私の推奨は条件付きの(A)です。** OF-OOV-07〜11を直したうえで、保存済みの本run(長いsegment)でもE2Wの救済が残る場合に限り、X/Zに範囲を限定した正式採用をユーザーに申請します。救済が残らない場合は(B)にします。11-7の既定OFF経路(承認前のコードを既定OFFで本番に置く限定例外)は勧めません。効果ゼロのまま仕組みだけが増え、ONにする判断がもう一度必要になるためです。

### 論点別

**1. E2Wで誤PASSを十分に防げているか / 独立エンジンに何を使うか → 要修正(OF-OOV-07、08)**
- 現在のTrialコードは、安全側に倒れない(fail-open)箇所が2つあります(`trial_direct_ledger_phoneme_01.py`)。
  - 102〜103行目: 確認用の転写が無いと`not_provided`のまま受理します。E2Wでは、ローカルWhisperが失敗(None)したら不受理にすべきです。既存の`_connected_speech_equivalence_local_asr_text`は、失敗時にNoneを返す設計です。
  - 114〜115行目: `uncertain_no_agreement`(矛盾はしないが一致もしない)を受理しています。E2Wで独立した証拠はWhisperだけなので、受理条件は「矛盾しない」ではなく「一致する」にすべきです。具体的には、Whisperがその位置に正準語を書いた場合か、同じLedger読みと一致するCMU語を書いた場合です。Trialの正例6件はすべて`e2_accept`だったので、この変更で失う正例はありません。
- 一致の判定は、文全体の`classify_asr_match`ではなく、**揃えた正準語の位置(1語の範囲)だけ**で行うべきです(OF-OOV-08)。置換した語以外はPrimaryがすでに一致を確認済みです。この形にすると、対象の語は厳しく確認しつつ、長いsegmentでも救済が消えにくくなります。
- 独立エンジンの候補:
  - (i) ローカルfaster-whisper small(推奨)。**新しい本番依存ではありません。** 連結音同値層(2026-09-07承認)とKPの3票判定で、すでに本番で使っています。API費用0で、E2候補になったときだけ実行します。長いsegmentではCPUで数十秒かかりえますが、発生頻度が低いので許容範囲です。注意点として、OpenAIのPrimaryと同じWhisper系統なので、事前知識による誤り方が似ており、完全に独立とは言えません(論点5)。
  - (ii) Azure(非推奨)。PhraseListありだと、正準語のほうへ書き寄せるため、確認の証拠になりません。PhraseListなしだと、2〜3円/回の費用が増えて目的(Azure削減)に反し、全文判定が崩れやすい問題もそのまま残ります。すでにAzureの転写が手元にある経路で、OF-183どおり矛盾時に不受理とする使い方だけで十分です。
  - (iii) Azureを語の周辺だけの短い区間で使う案も考えられますが、費用と仕組みが増えるので(i)に劣ります。

**2. kewl/coalの誤受理の意味 → 要ユーザー判断(開示)。E2固有の穴ではありません**
- これは別の経路で起きた誤りではなく、E2の判定根拠そのものの限界です。E2は「ASRが書いたCMU語の発音」を音の観測値として使います。そのため、実際の音声は近い別語(coal)なのに、ASRがよく使われる同音語(cool)へ寄せた場合と、本当に正しく読まれた場合を区別できません。gacha→gotchaの誤認と同じ仕組みが、誤って受理する方向に働いた例です。
- これは辞書にある語でも同じです。正準語がcoolで音声がcoalでも、Primaryがcoolと書けば既存判定でそのまま通ります(負例のfact→phatがBASE_PASSになった件も同じ型)。E2単独は「辞書外の語を、辞書にある語と同じ扱いにする」もので、E2Wはそれより厳しい形です。
- 「1:1置換」と「音素完全一致」の条件そのものに穴はありません。補足すると、kewlの誤受理はLedgerの**別候補の読み**(/kuːl/)を経由して起きています。また、Ledgerが有力とした/kjuːl/はおそらく誤りで、Ledgerの品質の問題でもあります。別候補の読みでの受理を禁止するのは、承認済み原則#52(複数の読みのどれかに一致すれば受理)の変更になるので、今は必須にせず、採用後の集計項目にします。
- 不採用の理由とは別に、**OF-OOV-05の訂正が必要です(OF-OOV-09)。** er109(表記違い同音の同値判定、2026-10-23承認、X/Zのみ)が、すでにPrimaryの判定だけでTRUE_CONTENT_MISMATCHを受理しています(`er006_secondary_asr_01.py:1135`、独立エンジンなし)。したがって、Phase 1で私が書いた「初めての経路」は今では不正確です。正しくは「同じ種類の経路はer109(CMU辞書の発音による同値判定)に先例がある。E2で新しいのは、Tier3調査で作った二次情報のLedger読みを根拠にする点」です。

**3. 構造変更の複雑さに見合う価値があるか → 要ユーザー判断(判断材料の補正が必要)**
- 価値は費用ではなく、時間(D)とユーザーの手間にあります。記事の中心語が「辞書外で、かつ辞書にある同音語を持つ」とき、全segmentでTTS再試行・Azure・LR・HR・人間承認の連鎖が起きる、という深刻な場面を防ぎます。一方、費用の効果(0.12〜0.35円/記事)は小さいです。
- 申請文に必ず加える点:
  - E2はOF-184で「直接音素置換は範囲外。需要はtelemetryで測る」として**保留された方式の再導入**です。測った需要は1/188 run(約0.5%)です。ユーザー原文§3の「過去に不採用とした方式を無断で再導入しない」にあたるため、明記が必要です。
  - Ledgerは、ASRがNGを出した後に調査して登録する仕組み(reactive)です。そのため**各語の最初の発生は救えません**。gachaのLedger登録はtopic_introのcascade(18:06)で作られました。-22.6円が最初のsegmentの救済を含んでいないか、時系列で検算してください(OF-OOV-08に含めます)。
- 複雑さを抑える配線案: E2の判定ロジックは、M1のmoduleに置きます(凍結候補・audit・`aggregate_by_ledger_key`を共有)。呼び出す場所は、**er109ブロック(1131〜1142行)の直後**で、既存の`ortho_scope.is_active_for_run()`と同じX/Zの範囲判定を再利用します。こうすると、Family A/B/Cの処理は変わらず、新しい範囲管理の仕組みも不要です。追加の分量は、コード数十行とtestにとどまります。
- 代替案「HR連鎖を短絡する運用」は、**既存仕様の範囲内の手当てではありません**。HRと人間承認の流れの変更なので、それ自体がユーザー承認事項であり、E2Wより品質リスクが高いため勧めません。(B)の実質は「現状維持+telemetryで再検討のきっかけを決めること」です。

**4. 正例の母数 → 要修正(OF-OOV-11、上限10円)**
- PASS→NG=0は受理を足すだけの設計なので当然であり、安全性の証拠は負例です。有効な負例9件は少なすぎます。
- 最小の追加案(約0.15円/clip、計10円以内):
  - Trial用Ledgerの語について、1音素だけ違う近い語の負例を約20件(例: thick→tick、school→scold、fat→vat/fit、cool→cull、fire→fair、lift→laughed)。
  - 正例を約10件。X/Zの本番voiceを1つ以上含め、Aoedeだけにしない。
  - ローカルWhisperの失敗(None)をわざと起こすtest(API 0)。
- 加えて、OF-OOV-08の本run長segmentでのE2W再評価(API 0)のほうが、合成正例を増やすことより優先です。

**5. 無効負例3件の開示 → 要修正(申請文に記載)**
- 申請文に書くべき内容:
  - 3つのエンジンがそろって同音語側に書いた音声は、ASRの証拠だけでは正しい読みか誤りかを判別できない。
  - Whisperは、Primary(OpenAI)とモデル系統が近く、完全に独立した証拠ではない。E2Wが防げるのは、エンジンごとに異なる単独の誤りであり、全エンジンに共通する事前知識による誤りは防げない。
  - この限界は辞書にある語の既存判定と同じだが、E2は受理を足すので、誤PASSにさらされる機会が増える。
- 安全網として、E2で受理したものにWarningラベルを付け、事後試聴の対象にする(最初のN件など)ことを、申請の選択肢に含めてください。

**6. F1 ’修正(Production)の受入 → 問題なし**
- 保存5,604行で`should_pass`の変化が0、最終ラベルの変化2件はどちらもPASS系同士でした。逆方向の変化4件もF1の診断ラベルだけです。関連testはPASSしています。
- golden 3件の失敗は、HEADの清浄なworktreeでも同じように再現しており、自分起因ではありません。ただし、別のOPENとして原因の帰属調査は必要です。
- 受入は妥当です。

**7. ユーザー判断の選択肢とQCD記述 → 要修正**
- (A)に含めるべき内容: 範囲(X/Z、Yは配線時に再判定)/独立確認=ローカルWhisperで対象語の位置の一致を必須にし、失敗時は不受理/D-2'(Tier3情報を自動PASSに使ってよい範囲)の拡張/OF-184の再導入であること/訂正後のOF-OOV-05/rollback用flag(er109と同じ形)/Store再利用の制限(OF-OOV-10)/各語の最初の発生は救えないこと/実際に測った頻度と期待効果。
- (B)に含めるべき内容: 再検討のきっかけ。例えば、`E2_ACCEPTABLE_PAIRS`が増えた場合や、gacha型(Ledger読みのある辞書外語×辞書の同音語)がtelemetryで複数のrunに出た場合。HR短絡は(B)の中身に含めない。
- (C)はこのままでかまいません。

### 採用申請前の必須修正
- **OF-OOV-07**: E2Wを安全側に倒す。Whisperの失敗やNoneは不受理、`uncertain_no_agreement`も不受理にし、正の一致を必須にする。
- **OF-OOV-08**: 独立エンジンとの一致は、揃えた正準語の位置(1語)だけで判定する。そのうえで、保存済みの本run(Adv part3の8テイクなど長いsegment)にローカルWhisperを当ててE2Wを再評価し(API 0)、救済件数と-22.6円を、Ledger登録の時系列も含めて計算し直す。救済がほぼ0なら(B)に切り替える。
- **OF-OOV-09**: 申請文を訂正する。er109という先例があること、OF-184の再導入であること、呼出点をer109の直後に置きX/Zの範囲判定を再利用することを書く。
- **OF-OOV-10**: Master Audio Storeの再利用を制限する。E2で受理したテイクを範囲外(A/B/Cやrollback後)で再利用しないこと、該当Ledger entryが無効化・更新されたら再利用をブロックすることを、er109の`OUT_OF_SCOPE_BLOCK_REASON`と同じ形で入れ、auditにledger_keyを残す。
- **OF-OOV-11**: 負例を追加する(上限10円、論点4)。

### 採用後に見ればよい事項
- 別候補の読み経由の受理の件数(kewl型)と、別候補を除外するかどうか(#52の変更になるのでユーザー判断)。
- 同じ語の複数回出現への拡張、confidence lowの許容(meink型)、US/UKラベル。
- Ledgerに登録するたびに`E2_ACCEPTABLE_PAIRS`を自動で作り直すこと。
- 最初のN件の事後試聴の結果。
- 別件として、ROOT_CAUSEで見つかった「Azureが全文単位で判定するため崩れやすい」問題。Primaryで非PASSになった68行のうち31行がNG_BOTHで、語ごとに見ればどちらかのエンジンが合っていた行が多いです。Azure削減の効果はE2よりずっと大きい可能性があり、別の管理IDとして検討する価値があります。

### 参照ファイル
- docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_direct_ledger_phoneme_01.py(102〜103行目、114〜115行目)
- er006_secondary_asr_01.py(541〜551行目: ローカルWhisperの本番での既存利用/1110〜1142行目: M1とer109の呼出点)
- er109_xz_scope_01.py / er109_asr_orthographic_equivalence_01.py(先例と範囲判定)
- docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/ROOT_CAUSE_01.md(17行目: Ledgerの作成時刻/44・59行目: Azure全文判定の問題)
>>>