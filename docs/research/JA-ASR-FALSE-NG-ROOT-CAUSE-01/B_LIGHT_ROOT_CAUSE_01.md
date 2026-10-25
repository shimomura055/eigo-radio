# B_LIGHT_ROOT_CAUSE_01(②B-light 原因究明、JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B、2026-10-25。API 0・Production変更0・費用0円)
結論(先に): **Azure(Secondary)は月題の値を正しく書くが、Productionの仕組みでは構造的に救済できない。理由は3つが重なる**: (1) Secondary受理は`classify_ja_asr_match`が`EXACT`/`NORMALIZED`のときだけで、Azureの転写は**読み(しわ→詩は/市は/氏は)と桁区切り`,`**で必ず`TRUE_CONTENT_MISMATCH`になる、(2) Primaryの値がDIFF(8000900等)だと**P1がAzureを呼ぶ前に`NG_PROTECTED`で打ち切る**(=Azureが値を支持しても使われない)、(3) 仕様L2865は『Secondary受理に値等価正規化後の一致を含む』と書くが、実装の`_secondary_accept`にはその層が無い(R4)。さらに実測で、**Azure自身の読みも原稿と一致しない転写が多い**(月野市/杉野氏/越え)ため、『Azureの値+Azureの読み』で救う道は、2026-10-11のユーザー安全条件(Secondary側のPHONETIC/助詞差を採用しない)に触れる。使えるのは『Azureの値』だけで、読みは別の根拠が要る。

## 1. 使った保存転写(すべて既存。新規API 0)
| 区分 | 出典 | 内容 |
|---|---|---|
| A1 Azure | `phase3_run/usage_log.jsonl` stage=A1_azure_moon | attempt1=`月野市は8900本越え`、attempt3=`杉野氏は8900本超` |
| A3 Azure | 同 A3_azure_flip(attempt2) | `月の詩は8900本超`(attempt2の保存Azureと同一) |
| A2 OpenAI×3 | 同 A2_openai_moon_x3 | attempt1=`月野詩は8,900本超え`×2/`好きの詩は8000900本超え`、attempt2=`月の島は千九百本超`×3、attempt3=`月野氏は八千九百本超`/`月の詩は八千九百本長`/`月のシワ、8000九百本超` |
| 保存Primary | `er019_output/.../japanese_title_attempt{1,2,3}*.json` asr_text | `月野詩は8000句800本超え`/`月の死は八千九百本超`/`月の氏は8000900本超`(attempt2の保存Azureは`月の詩は8900本超`) |
canonical=`月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密`。判定の再現は`eval_b_light_api0_01.py`(pin commit `89b630bd1`のProduction)。

## 2. Azure転写の逐語トレース(Secondary許容集合でなぜ落ちるか)
`classify_ja_asr_match(canonical, azure_text)`(Resolver OFF)の実測と、`_secondary_accept`(`er007_ja_secondary_asr_01.py:643`、受理=`SCG_PASS_CLASSIFICATIONS`[`:83`]=`EXACT_MATCH`/`NORMALIZED_MATCH`)の結果:
| Azure転写 | 値ガード(原稿vs転写) | classification | content_diffs(canonical→asr) | 受理? | 落ちる理由 |
|---|---|---|---|---|---|
| a1 `月野市は8900本越え` | EQUAL | TRUE_CONTENT_MISMATCH | `のしわ→野市は` / `,`→`` / `超→越え` | 不受理 | ①読み`月野市は`(読みは`つきのしわ`と発音等価)が文字として不一致 ②桁区切り`,`脱落(R3) ③`超`⇔`越え`(読み`ちょう`≠`こえ`) |
| a3 `杉野氏は8900本超` | EQUAL | TRUE_CONTENT_MISMATCH | `月のしわ→杉野氏は` / `,`→`` | 不受理 | `杉野`は`すぎの`≠`つきの`(**Azure自身の読み違い**)+`,` |
| a2 `月の詩は8900本超` | EQUAL | TRUE_CONTENT_MISMATCH | `しわ→詩は` / `,`→`` | 不受理 | 読み`詩は`=`しわ`(助詞は=わ)だが文字不一致+`,` |
→ **3転写とも値は正しく(EQUAL)、不受理の主因は『読み(同音異字・助詞)+桁区切り』**。値が原因ではない。Azureの値一致だけを理由に救済すると、a3の`杉野氏`(読みが違う)まで通ってしまう=**『Azureが数字を正しく認識しただけで無条件にPASS』になり、ユーザー条件に反する**。したがって読みの根拠は別に要る。

## 3. Primary転写の逐語トレース(P1・最終ゲート・Secondary到達)
(実測。base=pin時点Production、+v2=A案Primary層[VALIDATED(限定)]、+F=+F1+F2[07Aが適用中のOPEN-517])
| Primary転写 | 値ガード | base | +v2 | +F(F1+F2) | 経路と理由 |
|---|---|---|---|---|---|
| 保存a1 `月野詩は8000句800本超え` | DIFF | NG | NG | NG | **P1 `p1_value_diff`でAzure不呼出**(`er078_asr_unified_judge_01.py:567-568`)。8000+800=8800で原稿値(8900)に復号もできない=真の値崩れ |
| a1再転写 `月野詩は8,900本超え`×2 | EQUAL | NG | NG | NG | 値は正しい。**読み`月野詩`=`つきのうたわ`≠`つきのしわ`**(Primary読み不一致)でv2も不可。Azure(`月野市は…越え`)は`越え`≠`超` |
| a1再転写 `好きの詩は8000900本超え` | DIFF | NG | NG | NG | P1。読みも`すきの`≠`つきの` |
| 保存a2 `月の死は八千九百本超` | EQUAL | NG(Secondary不受理: `詩は`≠`しわ`) | **PASS**(v2: 値atom化+助詞読み`死は`=`しわ`) | PASS | 保存時の転写は漢数字で値が正しく、v2が救済 |
| a2再転写 `月の島は千九百本超`×3 | DIFF | NG | NG | NG | P1。**千九百=1900(八が欠落)**。原稿値8900との2エンジン矛盾(Azure=8900)。読み`月の島`=`しま`≠`し`もPrimary読みで不一致 |
| 保存a3 `月の氏は8000900本超` | DIFF | NG | NG | NG | P1でAzure不呼出。**読み`氏は`=`しわ`は一致、値だけが崩れ**(8000+900=8900と復号できる位取り断片の連結) |
| a3再転写 `月野氏は八千九百本超` | EQUAL | NG | PASS | PASS | v2で救済 |
| a3再転写 `月の詩は八千九百本長` | EQUAL | PASS(PHONETIC_MATCH) | PASS | PASS | 長/超は同音。既存PHONETICで通る |
| a3再転写 `月のシワ、8000九百本超` | DIFF | **PASS(PHONETIC_MATCHが値ゲートをskip)** | PASS | **NG(`final_gate_value_diff`)** | **F1(READING_MATCHの最終値ゲートskip撤去)で新たにNG化**。値`8000九百`は8000+900=8900に復号できるが、現行には説明手段がない |
- 要点(事実): **F1適用後は『読みが一致し数詞だけ崩れた正常音声』(a3再転写#2型)が新たにNGになる**。F1自体は承認済み安全条件(値の最終確認)の是正で妥当だが、その副作用として誤NGが増える(月題12転写中1件。07AのP-4/未知データ評価では出ていない=頻度は低い)。B-lightはこの型を救う手段の候補になる。

## 4. 根本原因(R-B1〜R-B5)
| ID | 原因 | 確信度 | 根拠 |
|---|---|---|---|
| R-B1 | Secondary許容集合が文字一致(`EXACT`/`NORMALIZED`)のみで、桁区切り`,`・同音異字・助詞に対して値等価も読み等価も持たない | 高(実測) | §2表。`er007_ja_secondary_asr_01.py:83,643` |
| R-B2 | P1が『Primary値DIFF=即`NG_PROTECTED`』で、Azureが独立に値を支持しても使わない(ASRの数詞整形崩れと真の値違いを区別できない) | 高 | `er078_asr_unified_judge_01.py:567-568`。JAのP1発火は全1,217 attemptで月題の2件のみ(ROOT_CAUSE_01 R2) |
| R-B3 | **Azure自身の読みも原稿とは限らない**(月野市/杉野氏/越え)。Secondaryの読みを根拠にすると誤救済(杉野氏)が混じる | 高 | §2。2026-10-11ユーザー安全条件『Secondary側PHONETIC自動PASS/助詞差を採用しない』(`DECISION_LOG.md:20663`、`delegation_log/2026-10-11_OPEN-258-...01.md:10`) |
| R-B4 | OpenAI Primaryの数詞崩れは**同一音声でも転写ごとに変わり**(a1: 8,900/8,900/8000900、a2: 千九百×3、a3: 八千九百/八千九百/8000九百)、型は『断片連結』『桁欠落』『復号不能』の3種 | 高(実測) | §1・§3 |
| R-B5 | **2エンジンが異なる値を出す(Primary `千九百`/Azure `8900`)場合、どちらが正しいかはテキストだけでは決められない**。安全側はNGであり、救済には第3の独立証拠が必要 | 高(論理+実測) | ローカルWhisper medium は3音声とも`8,900`と転写(`whisper_local_3wav_01.json`)=第3証拠があれば決まる |

## 5. UDR #136の承認条件(逐語)と、B-lightが接触する条件
出典: `docs/pm/delegation_log/2026-10-22_ASR-THREE-WAY-COMPARISON-TRIAL-01_DECISION_USER.md`(`DECISION_LOG.md:21995-22003`に逐語、751文字、sha256 `810d3c74…`)。逐語§1: 「1. Primary：OpenAI `gpt-4o-mini-transcribe` を維持。 2. Secondary：Azure Speech STTを維持。 3. ローカルWhisperのProduction導入は不採用。運用複雑化を避ける。 4. Primary／Secondaryの入替は行わない。 5. 今回の比較Trialに基づく追加精度検証（Store 333件へのAzure追加検証等）は実施しない。」逐語§2: 「Key PhraseはPrimary／Secondaryの両方PASSを必須とする方針。…」(§2は後に`APPROVED_FOR_PRODUCTION`化[UDR #139])。逐語§3: 「既存Productionコード・モデル構成は変更しない。」
| UDR #136の条件 | B-light案β(推奨) | 案γ(第3エンジン) | 案δ(Secondary読み受理=A4(b)) |
|---|---|---|---|
| 1 Primary維持 | 非接触(Primaryはそのまま) | 非接触 | 非接触 |
| 2 Secondary(Azure STT)維持 | **非接触**(Azureは維持。役割は『Primary NG時の確認』のまま、使うのは転写の値だけ) | 非接触 | 非接触(ただし受理集合が変わる) |
| 3 ローカルWhisperのProduction導入は不採用 | 非接触(Whisperを使わない) | **接触=変更が要る**(JAへのWhisper導入。KP英語のみ2026-10-22に別承認済み[KP3V]) | 非接触 |
| 4 入替なし | 非接触 | 非接触 | 非接触 |
| 5 追加精度検証(Store 333件Azure等)は実施しない | 非接触(保存済み転写のみで評価、Store 333件へのAzure追加検証は行わない) | 非接触(ただしWhisper導入時の評価計画が別途要る) | 非接触 |
| §3 既存Productionコード・モデル構成は変更しない | 当時のTrial指示であり恒久禁止ではない。**ただしβのProduction配線は別途ユーザー採用が要る**(下記) | 同左 | 同左 |
| (UDR #136外) 2026-10-11安全条件: Secondary側PHONETIC/助詞差を採用しない・Whisper 2-of-3なし | **非接触**(Secondaryの読みは使わない。値のみ) | **接触**(Whisper 2-of-3) | **接触**(Secondaryの読み・助詞差) |
| (外) CURRENT_SPEC L2179/L2856: JA Secondary受理=EXACT/NORMALIZEDのみ(L2865に値等価を含む) | **接触(新しい受理クラスの追加)**。ただし『値等価』を認める原文(L2865)の範囲に沿う設計(Primary読み+Secondary値の組合せ) | 接触 | 接触 |
**判定**: β/αは**UDR #136の承認条件の変更を要しない(既存条件内)**。根拠=UDR #136が固定したのはProvider構成(1・2・4)・Whisper不採用(3)・追加検証の不実施(5)で、βは構成を変えずWhisperも使わない。ただし**βのProduction採用は新しい受理クラスの追加**であり、`APPROVED_FOR_PRODUCTION`を人間ユーザーだけが与える通常の採用手続きが別に要る(自動開始しない)。γ・δは上表のとおり#136または2026-10-11条件の変更を要するため、本タスクでは採用提案せず『判断候補』として整理する(`B_LIGHT_DESIGN_01.md`§5)。
