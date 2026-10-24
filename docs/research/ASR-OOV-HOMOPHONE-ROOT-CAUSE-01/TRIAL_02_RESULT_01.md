# TRIAL_02_RESULT_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02 §4、2026-10-24) E2(v2)の実音声Trial・保存データ再判定

Trial専用(Productionから未import・未配線、`test_not_imported_from_production_modules` PASS)。計測は**F1 ’修正(OPEN-500、commit c120a9d12)の後**に実施。コード: `trial_direct_ledger_phoneme_01.py`(v2)、`trial_run_e2_02_paid.py`(正例18+負例5)、`trial_run_e2_02_neg2.py`(追加負例7)、`trial_run_e2_02_whisper.py`/`trial_run_e2_02_azure_arbiter.py`(切り分け)、`trial_run_e2_02_stored.py`(保存データ、API 0)。結果JSON=`work/trial02*/…result.json`、コンソール=`work/console_trial02_*.txt`。実費=約11.7円(BUDGET_LOG_01.md)。

使用モデル(Production routingと同一、すべて最新世代の推奨系): TTS=`gemini-3.8-flash-lite-tts`(speech_metadata_flash_lite、voice=Aoede、既定英語style)/Primary ASR=`gpt-4o-mini-transcribe`(routing.transcribe, en-US)/Ledger調査=Perplexity `sonar`(research_pronunciations既定)/切り分け用: ローカルfaster-whisper small、Azure Speech STT(PhraseListなし)。旧世代モデル使用なし。

## 1. 正例(合成、Ledger登録→TTS→Primary ASR→判定)  ※Ledgerは共有Ledgerのコピー(Trial用)。共有state変更0(実行前後sha256一致)
語: Lyft/Fyre/Grindr(entity、大文字)、thicc/kewl/skool/luv/phat(小文字)。すべて CMU未収録で、CMUに同じ代表発音の語(lift/fire/grinder/thick/cool/school/love/fat)がある。各1〜2文(Lyft・skoolは同じ語が2回出る文も1つ)=18 clip。

**Ledger登録(既存の正式経路=`_resolve_unresolved_entity_for_review`、gachaを作ったのと同じ関数。供給側G)**
| 語 | Ledger confidence | 登録された読み | 備考 |
|---|---|---|---|
| Lyft / Grindr / thicc / kewl / skool / phat | medium | /lɪft/、/ˈɡraɪndɚ/、/θɪk/、/kjuːl/(有力)+/kuːl/(別候補)、/skuːl/、/fæt/ | evidence_tierは全語 NAME_IN_CITED_PAGE(名称は出典にあるが読みの本人音声は無い=gachaと同じ二次情報) |
| Fyre / luv | **low** | /ˈfaɪɚ/、/lʌv/ | confidence low → E2の受理条件(medium以上)で除外される |
供給側G実費: Perplexity 1語あたり約0.94円(token実測[入力596前後/出力240〜340]+request fee公開価格仮定)。8語=約7.5円。

**18 clipの結果(Primary ASR転写に対する判定)**
| 結果 | 件数 | 内訳 |
|---|---|---|
| ASRが正準語(または正規化一致)と書いた=救済不要(BASE_PASS) | 7 | lyft_2、fyre_1、grindr_1/2、thicc_2、kewl_1/2(固有名詞・引用符付きで書かれると既存判定で通る) |
| 救済が必要(Primaryが同音語に寄せた) | 11 | |
| うちE2が受理(PASS_WITH_WARNING相当) | **6** | lyft_1、thicc_1、skool_1/2、phat_1/2 |
| うちE2が受理しない | 5 | Ledger confidence low 3(fyre_2、luv_1、luv_2。low許容にすれば3件とも受理可)/同じ語が2回出る文 2(lyft_x2、skool_x2: 現行の『差分1件のみ』条件で不受理) |
| 既存M1が受理(M1単独) | **0/11** | M1は期待綴りCMU要件で構造的に比較不能(MULTI_CANDIDATE_NO_MATCH/入口でNOT_UNCERTAIN)=E1/M1では救えないことの再確認 |

**救済率(正例)**: 救済が必要だった11件のうち、**confidence medium以上・差分1件の条件を満たす6件は6/6=100%受理**。11件全体では6/11=54.5%(取りこぼし5件=low 3+複数出現2、いずれも設計条件による不受理で誤受理ではない)。複数出現を許す拡張(OF-OOV-06後続)とlow許容でそれぞれ+2・+3件だが、lowを許すと安全性が下がる(下記負例)。

## 2. 負例(意図的に別の語として読ませた音声、12 clip)
| 読ませた語(正準) | Primary転写 | ローカルWhisper | Azure | E2単独 | E2+Whisper(E2W) | 判定 |
|---|---|---|---|---|---|---|
| scowl(skool) | scout as | Skall | - | 不受理(NO_PHONEME_MATCH) | 不受理 | OK |
| thin(thicc) | thin | thin | - | 不受理 | 不受理 | OK |
| think(thicc) | thank | thank | - | 不受理 | 不受理 | OK |
| sick(thicc) | sick | sick | - | 不受理 | 不受理 | OK |
| call(kewl) | call | call | - | 不受理 | 不受理 | OK |
| cowl(kewl) | cow | cowl | - | 不受理 | 不受理 | OK |
| coal #2(kewl) | "kool" | coal | - | 不受理(F1残差) | 不受理 | OK |
| **coal #1(kewl)** | **cool(誤り)** | coal | **coal** | **受理(誤受理)** | **不受理(矛盾)** | **E2単独は誤受理、E2Wは防止** |
| fact(phat) | phat(正準語) | FAC | - | (BASE_PASS: E2到達前) | - | 既存Primaryの誤PASS(E2無関係) |
| loft(Lyft) | Lyft(正準語) | lift | lift | (BASE_PASS) | - | 無効な負例(下記) |
| left(Lyft) | lift | lift | lift | 受理 | 受理 | 無効な負例(下記) |
| stool(skool) | school | school | school | 受理 | 受理 | 無効な負例(下記) |
- **無効な負例3件(loft/left/stool)**: 3つの独立エンジン(OpenAI・ローカルWhisper・Azure)が全員、同音語側(lift/school)と聞き取った。私は音声を耳確認できないため『TTSが実際に別語を発音していたがASRが文脈で寄せた』か『TTSが同音語を読んだ』かを判別できない。いずれにせよ**ASR証拠だけではE2の受理とE2が防ぎたい誤りを区別できない**=既存の全ASR判定(canonicalが普通の語のときも同じ)と同じ限界で、E2固有の追加リスクとは言えないが、E2が『受理を足す』ので露出は増える。
- **有効な負例(少なくとも1エンジンが同音語と異なる語を聞いた)9件**: E2単独の誤受理 **1件(kewl/coal #1: Primary ASRの単独誤り cool)**、E2Wの誤受理 **0件**。既存Primaryの誤PASS(fact→phat)は E2 到達前の既存挙動。
- 誤受理0を主張できるのは『E2W(Primary受理+独立エンジンが矛盾しない)』のみ。**E2単独は負例に対して誤受理を実測した(Opusが指摘した"独立証拠なし受理"のリスクが実在)。**

## 3. 変種 E2W(E2 + ローカルWhisper非矛盾)の評価
OF-183の枠組み(Secondary転写が手元にあれば矛盾時不受理)を、**無料のローカルfaster-whisper(既存`_connected_speech_equivalence_local_asr_text`と同じ呼び出し、API 0)**へ拡張した変種。判定: Whisper転写がshould_passまたは同じE2で受理できれば一致、protected fail/TRUE_CONTENT_MISMATCHでE2不受理なら矛盾。
- 正例: 6/6 を維持(受理は全件 `e2_accept`=Whisperも同じ同音語に寄せた)。
- 有効な負例: 誤受理 1→0。
- 保存データ(本run Adv part3): attempt 5のAzure転写(you've→you等のAzure固有誤り)で『矛盾』となり不受理(OF-183どおり)。attempt 1・2・8はPrimary段で受理(Secondary不要)。
- コスト: API 0。CPU時間(small、1clipあたり数秒〜十数秒)のみ、E2が受理候補になったときだけ実行すれば足りる。
=> **E2はE2W形(独立エンジンの非矛盾を必須)で採用候補にするのが妥当。** E2単独は推奨しない。

## 4. 保存データ(API 0、`trial_run_e2_02_stored.py`)
| 検査 | 結果 |
|---|---|
| 本run Adv part3 8テイク | **attempt 1・2・5・8が受理**(Phase 1と同じ4/8)。3・4・6・7は gacha以外にも差があり不受理=正しいNG。OF-OOV-01/02の適用で**落ちた正例なし**。Secondary転写を与えた場合: attempt 5は Azure固有誤りで矛盾不受理、attempt 8は一致(native_pass) |
| 110ペア(Ledger読み付きOOVを含む保存の非PASS) | v1の受理3→**v2は2**(gacha×2のみ)。落ちたのは **meink←mink**(confidence low=OF-OOV-02の条件で除外。これはPrimaryが `mink` を書いた実在の誤NG(Troy Meink)で、救済の取りこぼし。low許容にすれば3だが、low許容は安全性を下げる[§2: Fyre/luv相当])。他の内訳: CONFIDENCE_TOO_LOW 64(MelosなどLedger側lowの語)、NOT_SINGLE_REPLACE 23、NOT_1TO1 6 ほか。既存M1が既に受理するものは0=重複なし |
| PASS→NG | 0(受理を足す設計) |
| F1 ’修正の影響 | 本run part3 attempt 1(Primary転写に’あり)は、旧tokenize/修正後tokenizeのどちらでもE2の判定は同じ(attempt 1=受理、attempt 6=NOT_SINGLE_REPLACE)=置換後F1残差0の要求に対し’修正の有無で本件の結果は変わらない(確認済み)。’修正はE2の前提ではないが、置換後判定がF1残差0を要求する以上、’を含む転写で偽残差が出ない状態が望ましい(OPEN-500で解消) |

## 5. 費用・頻度による期待効果(カウンターファクチュアル)
- 本run(Word Gacha)へE2適用: gacha関連segmentの TTS+ASR+Azure 実績38.58円 → 約16.02円(**-22.6円**。Azureは Primary段で受理できたattemptの呼出が不要、TTS再試行も減る)。HR Lock・Local Rewrite・Style Gate・人間承認(委任_02〜04相当の連鎖)も回避。
- **発生頻度**: 保存全データ(5,681行/188 run dir)で E2が実際に効く型は gacha の1件のみ(Ledger読み付きOOV+CMU同音語)。1/188=0.53%(X/Z系62 runのみ分母にしても1.6%、ただしWord Gachaは借用語が主題で偏りあり)。期待値 = 0.53〜1.6% × 約22円 ≈ **0.12〜0.35円/記事**(70円/記事セット目標の0.2〜0.5%)。借用語・造語・スラング主題の記事が増えるほど効く。
- **E2が効く条件の現実**: E2受理組合せの全件(`E2_ACCEPTABLE_PAIRS_01.md`)は現Ledger(43 entry)で **1組(gacha/gotcha)のみ**。Ledgerが固有名詞(entity)中心のため。小文字の一般語(スラング・借用語)をLedgerに載せる供給側Gを入れると広がるが、1語約0.94円(Perplexity)でCMU未収録語を毎記事先行登録すると期待効果(0.1〜0.4円/記事)を上回りかねない=**G先行登録は現時点で非推奨**(reactive登録=最終NGでHR packageを作るときに登録される現行経路で十分)。
- 追加コスト: E2W=API 0(CPUのみ)。Production化の実装コスト=M1内1ルール+test(数十行)。

## 6. Status案(最終判定はFable)
- **VALIDATED_LIMITED(E2W形)** を提案: 正例のうち設計条件を満たす6/6を救済、有効負例の誤受理0(E2W)、保存データPASS→NG 0・落ちた正例=meink(low、設計上の除外)。限定=現Ledgerで効く組合せが1組、有効負例n=9、正例n=11(全て合成)。
- E2**単独**は不採用相当(有効負例で誤受理1件を実測)。
- Production採用はユーザー判断(DESIGN_02.md §4のOF-OOV-05の3点を明記)。
