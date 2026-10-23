# PERPLEXITY-401-INVESTIGATION-01 調査報告(OPEN-473)
Status: ROOT_CAUSE_CONFIRMED(Perplexity側クレジット残高切れ=insufficient_quota)。コード不具合なし。復旧にはユーザー操作(課金/クレジット追加)が必要。秘密情報は本書に含まない(キーは長さ・prefixのみ)。調査日: 2026-10-23(JST)。

## 結論(先頭)
- 401の原因は**認証不正ではなくクレジット不足**。最小疎通呼出1回(2026-10-23 08:50 GMT、sonar、max_tokens=5、費用ほぼ0円)のレスポンス本文は `{"error":{"message":"You exceeded your current quota, add credits at https://console.perplexity.ai/project/billing.","type":"insufficient_quota","code":401}}`(HTTP 401)。PerplexityはクレジットなしをHTTP 401で返す。
- コード・設定の不具合は無い: キー形式正常(prefix `pplx-`、53文字、空白/非ASCIIなし)、`.env`のmtimeは2026-10-10 13:38 JSTで、その後の2026-10-12 04:17 UTCに同一キーで200成功(`er063_output/family_z_audio_01/smoke_01/cost_log.jsonl`)。エンドポイント`https://api.perplexity.ai/chat/completions`、`Authorization: Bearer`、model=`sonar`はコード(`er006_pronunciation_research_01.py:92-110`)どおりで、残高が戻れば同コードで動く見込み。process/User/Machine環境変数には同名変数なし(.envのみが唯一の供給源=別キーの上書きなし)。
- **ユーザー操作が必要**: Perplexityコンソールでクレジット追加(自動チャージ設定を含む)。Claude側ではキー再発行・課金・設定書換えをしない(禁止事項)。

## 1. Production利用実態
- 呼出点は1関数 `er006_pronunciation_research_01.py:92 research_pronunciations()`(sonar、1 topic 1 request)。呼ぶ経路は次の3つのみ(Grep実測):
  1. 事後Ledger登録/Human Review用発音情報(ASR Cascade最終NG後): `er006_secondary_asr_01.py:372`(旧`_legacy_resolve_unresolved_entity_for_review`)および同`:457`(PNPS Stage 1経路、`er097_pronunciation_supply_stage1_01.py`が分類)。
  2. TTS前のlow-confidence Ledger entry再research: `er025_entity_pronunciation_resolver_core_01.py:503`(`MAX_EN_WEB_LOOKUP_CALLS_PER_RUN`上限あり)。
  3. 事前投入の証跡runner(`er025_output_en2_evidence_run.py:45`、量産経路ではない)。
- 対象はEN音声(Family X・Z。Family A/B/Cは調査対象外)。flagで切る経路ではなく、固有名詞が最終NGまたはlow-confidence entryのときだけ発火する条件付き経路。`PERPLEXITY_API_KEY`未設定なら`CREDENTIAL_REQUIRED`で即戻る(`:96-97`)。
- runtime証拠(全`*.jsonl`の`provider=perplexity, api=pronunciation_research`行を集計): 計84行、200成功32 / 401失敗52。直近の成功は2026-09-27(er025 phase2、X small_bag、hormuz)、2026-10-10 16:27 UTC(X meta regen)、**最終成功=2026-10-12 04:17:58 UTC(Z smoke_01)**。成功時の費用: usage logは`input/output/total_tokens`のみ記録(円換算列なし)。1呼出あたりの量は小さく、成功32回が約2か月分=利用頻度は低い(1runで数回以下)。

## 2. 今回の401(時系列)
| 日時(UTC) | run | 回数 |
|---|---|---|
| 2026-10-22 01:18:20-32 | er097 pnps_stage1_wiring runtime_paid | 2 |
| 2026-10-22 09:03:58 | X small_bag run_jre_01 | 1 |
| 2026-10-22 21:47-22:00 | Z the_open_window run_e2e_01 | 22 |
| 2026-10-23 03:12-04:25 | Z the_open_window run_sf_prod_01 | 27 |
- **初回401=2026-10-22 01:18:20 UTC**(最終成功の約10日後)。以降は全件401(200は0件)。Xはsmall_bag run_jre_01の1件のみ、melosは2026-10-22以降の呼出記録なし。記録のある呼出は全て401。残高切れ前のどの時点かの特定は不可(10-12〜10-22は呼出自体が無かった)。
- 『開いた窓』tts_a2の17 callは、HR対象語(Bertie等)ごとの`research_pronunciations`呼出(PHASE4_RESULT_01.md:43)。レスポンス本文は当時ログに保存されない(`cost_log`は`http_status`のみ、`er006_pronunciation_research_01.py:112-118`)ため、対象語別の内訳はcost logからは取れない。
- 401後の挙動: `status=FAILED`を返し、呼出側は`status!=OK`で何も登録せず戻る(`er006_secondary_asr_01.py:382`、`er025...:507-508`)。Stage 1では401を`TRANSIENT`扱いとし否定記録を保存しない(`er097_pronunciation_supply_stage1_01.py:108-119`)。処理は**止まらず継続**(音声生成・Gate判定は不変)。副作用として、同語は次回も再調査し毎回401(無料だが無駄呼出)。

## 3. 原因切り分け
| 項目 | 結果 |
|---|---|
| 環境変数名 | `.env`に`PERPLEXITY_API_KEY`あり(1件)。コードの読取名と一致(`:95`)。process/User/Machine env未設定 |
| .env読込経路 | `er006_secondary_asr_01.py:90-95 load_dotenv()`(上書きなし)。`research_pronunciations`は`os.getenv`のみ |
| キー形式 | 53文字、prefix `pplx-`、空白/非ASCIIなし(sha256先頭8桁 40fc5c46は同一性確認用、キー復元不可) |
| 仕様一致 | URL/Bearer/model=sonar/json_schema response_formatはコード既定。今回の最小呼出(response_formatなし)も同一401 |
| 再現 | 1回再現(HTTP 401、`insufficient_quota`)。本文でキー無効ではなくクレジット不足と特定 |
| 成功/失敗の境界 | 同一`.env`(mtime 10-10)で10-12に200、10-22以降401 |
- Claude側で直せる不具合ではない。ユーザー操作: Perplexity Console > Billing でクレジット追加(自動チャージ有効化を推奨)。確認はClaude側で1回の最小呼出(≤1円)で可能。

## 4. 代替手段と品質評価
- Perplexity不通時の現行フォールバック: 事後Ledger登録が行われない=Human Review packageの「発音調査結果」欄が空になるだけで、**自動PASS/NG判定・retry・fallbackは変わらない**(Stage 1の戻り値はHR packageのみで、PASS/NGは読まない: `er025...`コメント/`er097`設計)。
- 影響が出るのは、Ledgerに無い初見固有名詞(『開いた窓』のBertie等)で、(a) PNAP(`er103_proper_noun_alarm_policy_01.py:104,167-179`)の固有名詞根拠が`ledger`でなく`capitalized`/`cmu_oov`に限られ、CMU収録語の文頭等は`NO_PROPER_NOUN_EVIDENCE`でHR確定(PHASE4_RESULT_01.mdの`Birdie`事例)、(b) Human Reviewで人が発音を決める際の調査支援が無い、の2点。品質を下げる方向(誤PASS)には働かない=安全側(HR増)。
- 既存のLedger登録済み語(過去の成功32回分)は引き続きcache hitで動く(401の影響を受けない)。新規語が多い記事ほどHRが増える。
- 承認済みのOPEN-472包括対策(①RET、Run Entity Table)は本経路に依存しない設計(OPEN-473記載)で、採用後は本文実体表で代替できる。したがって**クレジットが戻るまでの暫定影響は「新規固有名詞のHR増・調査支援欠如」に限定**され、承認済み発音品質(誤PASSなし)は維持される。自動処理の完全無人性は新規固有名詞で一部低下。
- 別providerへの置換(例: OpenAI web_search)は新経路=仕様変更のため本調査では実装しない。必要ならFableが仕様候補として扱う(判断候補: 通常はクレジット追加が最短で、仕様変更不要)。

## 5. ユーザー操作(必要)
- 理由: Perplexityアカウントのクレジット残高切れ(課金はユーザー領域)。
- 操作: https://console.perplexity.ai/project/billing でクレジット追加。以後の枯渇防止に自動チャージ設定を推奨。APIキーの再発行は不要の見込み(キーは有効、残高のみ)。
- 放置時の影響: 新規固有名詞のHR増・調査支援欠如のみ(上記4)。既存Ledger登録語と承認済みGateは不変。X/Zの量産は止まらない。追加費用0。

## 6. 本調査の実施事項
- API: Perplexity最小疎通1回(費用ほぼ0円、401のため課金なし)。他API 0。コード・Prompt・閾値・flag変更0。キー値は出力・保存していない。

## 7. 復旧確認(委任_02、2026-10-23)
- ユーザーが$10追加チャージ済み。最小疎通(sonar、`api.perplexity.ai/chat/completions`、Bearer): max_tokens=5は入力エラー(HTTP 400「max_tokens must be at least 16」=認証・残高は通過)、max_tokens=16で**HTTP 200**。復旧確認。
- 正式関数 `research_pronunciations()` を1 topic(Bertie)で1回: status=OK、items 1件(hint=BUR-tee、confidence=low)、citations 10、usage total_cost $0.0052(約0.8円)。cost_logはsuccess=true/http_status=200で記録(`er006_output/perplexity_recovery_check_02/cost_log.jsonl`、Production cost logへは書いていない)。本関数は調査結果を返すのみで、Ledger登録は呼出側(`er006_secondary_asr_01.py:372,457`等)の責務。今回は呼出側を実行していないため、Ledger本体・Production成果物への副作用は0。
- 費用合計: 約2円(疎通2回[400入力エラーは課金なしの見込み]+正式関数1回+関数のcost_log失敗前の1回[logger未初期化のRuntimeErrorで結果破棄、API課金済み])。コード変更0、キー値の出力・保存0。
- 復旧後の運用注意: (1)Perplexity ConsoleのBillingで残高を定期確認し、自動チャージ(auto top-up)を有効化する(今回の枯渇は10-12最終成功〜10-22初回401の間に発生)。(2)401(insufficient_quota)が出たら`cost_log.jsonl`のhttp_status=401の連続をアラート条件にする。(3)Perplexityはクレジット不足を401で返すため、401=キー不正とは限らず、本文の`type`を最初に確認する。(4)401期間中に否定記録は保存されていない(`er097:108-119`でTRANSIENT扱い)ため、復旧後に再researchされ、再処理は不要。
- OPEN-473 = CLOSED(2026-10-23)。
