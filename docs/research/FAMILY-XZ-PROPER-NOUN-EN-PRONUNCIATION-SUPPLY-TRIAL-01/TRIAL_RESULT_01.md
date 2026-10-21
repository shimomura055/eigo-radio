# TRIAL_RESULT_01: 固有名詞の英語発音供給 Offline Trial 結果

管理ID: FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_02(実行)。実行日: 2026-10-21。
Status(Sonnet所見・暫定。最終ラベルはFable): **`TRIAL_DONE_PENDING_FABLE`**。ラベル案=`USER_DECISION_REQUIRED`(K1が`UNCONFIRMED_SAFE`=安全終了・要件未達。事前固定ラベル5-6「K1がUNCONFIRMED_SAFEで要求未達 → USER_DECISION_REQUIRED」に該当)。`REJECTED`条件(誤登録・誤PASS増・既存Ledger悪化・Production影響)には**該当なし**。Production採用はユーザーのみ。
設計書=`TRIAL_DESIGN_01.md`(v01+v02追記)。harness=`er089_proper_noun_en_pronunciation_trial_01_{lib,run,eval,test}.py`(Trial専用、Production無配線)。証跡=`er089_output/proper_noun_en_pronunciation_trial_01/`(下記)。
固定した前提: ①(判定関数の是正)は`01fdd3a2c`(fix)・`272dbe33b`(Fable判定PRODUCTION_WIRED記録)がorigin/mainに到達済み。本Trialの全判定はこの版(HEAD=`d2cff4bea`の親系列に含まれる)で実行。使用モデル(25節): 検出=gpt-6.1-sol(本命)+gpt-6-luna(比較)、研究腕A=gpt-6.1-sol+web_search(effort=medium)、腕B=Perplexity sonar(現行資産)。

## 0. 一行結論
- 検出(D1∪D2)は必須名を100%拾い、誤登録は0、既存Ledger/判定は不変(悪化0)。ただし**byUsには公式の英語発音情報が存在せず(日本語公式の読み「バイアス」のみ)、Ledger登録は安全側で0件**(K1=安全終了・要件未達)。登録できたのはVera(辞書・medium)1件のみ。
- 「Ledger登録→PL(重み2.0)」の機構自体は実行証拠で確認(speech.context dgi.Items==期待値 ∧ bias=2.0 が全8 PL呼出で一致)。登録を介さず綴りだけをPLに入れた場合(腕M)の効果は、Azure転写の多語化`Buy Us`が1/3例で消えNG→PASS(再現2/2)、残り2例(`by us`)は変わらず。一方で**Azureが`Lion Manga`と書いた箇所を`LINE Manga`へ寄せる副作用**も1例観測し、その箇所は独立2エンジンが`Lion`と聞いていた(要試聴)。
- 費用実測 **JPY113.10**(Cap200内、見積中央100〜125に合致)。設計外のAPI呼出0。

## 1. 記事B実例の再現(必須ケース表 K1〜K6/Z1/Z2)
| ID | 結果 | 根拠(file) |
|---|---|---|
| K1 byUs 検出→根拠確認→登録→PL | **安全終了(`UNCONFIRMED_SAFE`、登録0)=要件未達**。検出=成功(D1:`R_CAMEL/R_QUOTED/R_FACT/R_LEDGER_JA_KATAKANA_LATIN/R_JA_GATE_UNKNOWN_LATIN`、D2:sol/luna両方)。未登録判定=調査対象(JA entryのみ)。研究=腕A 2呼出(通常+英語情報源特化)とも`UNCONFIRMED`(公式発表PR TIMESは「byUs（バイアス）」=日本語読みのみ[V2違反で登録不可]、英語公式[WEBTOON IR等]はbyUsを使うが発音の記載なし)。登録0・PL空のまま=§3-7適合の安全側 | `s3_detect_results.json`、`s3_research_raw.json`、`s3_research_extra_raw.json`、`s3_register_results.json`、`j7_evidence.json` |
| K2 byUs→Bias単独 | PASS(`HOMOPHONE_EQUIVALENT`/layers=`cmu_alternate`)。Ledger無/trial/hypoで同一 | `s3_identity_results.json` |
| K3 byUs→Bias+story-making→storymaking | **PASS**(①反映後: part1 att1の既存Primary転写=`HOMOPHONE_EQUIVALENT`/`cmu_alternate`、Ledger無/有で同一)。実ASR再転写(新規1回)でも判定PASS(`NORMALIZED_MATCH`) | `s3_k3asr_results.json`(①commit到達後に実行) |
| K4 LINE | 検出=成功(D1:`R_ALLCAPS/R_FACT`、D2:`LINE Manga`句)。研究=腕A 2呼出とも`UNCONFIRMED`(公式英語ページに発音記載なし、Cambridgeは一般語lineの`/laɪn/`)。登録0・PL空。CMU層(L AY1 N)で足りるため**登録不要案が本命(R-05)** | 同上 |
| K5 LINE→Lion | (ii)決定的: `LINE Manga`x`Lion Manga`は**PASSにならない**(`ASR_VALIDATION_UNCERTAIN`、verified=False。Ledger無/trial/hypo[LINE登録済み仮定]で同一)。(i)実音声: 第1部att2の2か所目`LINE Manga`は Primary=LINE / Azure(PL無)=Lion / whisper medium(ローカル)=Lion → **`AUDIO_LIKELY_MISPRONOUNCED`(2/3)=要試聴**。att1・att3は`AUDIO_LIKELY_CORRECT`。腕Nは実施せず(TTS禁止) | `k5_votes.json`、`s3_identity_results.json` |
| K6 two works→20 works | NG維持(part3 att2 Primary転写に`20 works`、verified=False。Ledger無/trial/hypoで同一) | `s3_identity_results.json` |
| Z1 Melos等 | 検出再現率100%(EN narration本文に出る必須名=`Melos`)。研究=腕A `UNCONFIRMED`(NHKの公式英語audiobookはパスコード必須で音声確認不能)。**Z側は実Ledgerの`melos`(cascade_unresolved_entity,low)で既にPL=`["Melos"]`**のため、供給有無でPL内容が同一(Azure呼出を省略)。判定変化16ケース中0件、M1のC2音素候補集合(hypo仮定でも)16/16不変 | `s3_azure_results.json`(z_skipped)、`s3_identity_results.json` |
| Z2 Open Window | 検出=EN narration本文のFramton Nuttel 100%(D1:`R_CAP_PHRASE/R_FACT`、D2 sol/luna)。Sappleton/Veraは**narration本文に出現せずseed要約にのみ出現**(seed要約ではD1が3名とも100%)。研究=腕A: Vera=CONFIRMED(Oxford Learner's、medium、V1'で本文一致確認)→**Trial Ledgerへ登録1件**、Framton Nuttel/Sappleton=`UNCONFIRMED`(Forvo音声のみ=テキスト検証不能)。PL(Trial Ledger)=narration本文では`[]`、seed要約では`["Vera"]`。ASR A/Bは音声未生成のためN/A | `s2_free_results.json`、`s3_register_results.json`、`results_summary.json`(Z2) |
| 設計の必須名Dionysius/Selinuntius | **EN narration本文(run_e2e_06)に出現しない**(speaker IDとJA側のみ)=EN検出の対象外。設計時の前提(EN本文に出る)は誤りだった | `s2_free_results.json`の`_note_names_not_in_en_text` |
| 擬似造語Zorbleflux | 腕Aで`UNCONFIRMED`(出典なし)→`UNCONFIRMED_SAFE`、登録0(誤登録0)。V1'単体testでも架空URL/架空quoteは落ちる | `s3_register_results.json`、test `test_v1p_pseudo_word_zorbleflux_falls` |

## 2. 検出・公式発音確認・Ledger登録・PL投入・重み2.0の証拠
- **検出(5-1)**: D1 再現率 B=100%(byUs,LINE)、Melos=100%(Melos)、OW narration=100%(Framton Nuttel)、OW seed要約=100%(3名)。D2は記事単位1回: sol/luna ともbyUs・Melos・Framton Nuttelを検出。LINEは両モデルとも`LINE Manga`句として検出(単独語ではない=句内包含)。D1∪D2=100%。候補数(D1、誤検出含む再現率優先)=B 37 / Melos 10 / OW 22。D2は一般名(Japan, Osamu Dazai等)を追加するが、いずれも研究対象外にできる。
- **公式発音確認(5-1)**: 研究7名(byUs, LINE, Melos, Framton Nuttel, Sappleton, Vera, Zorbleflux)x腕A→CONFIRMED 1(Vera)/UNCONFIRMED 6。腕B(Perplexity)は**`HTTP 401 insufficient_quota`で実行不能**(アカウントの利用枠切れ。呼出1回のみ、再試行せず)。公式docsに「Sonar Chat Completionsのサポートは2026-09-27に終了、新規はAgent API」と明記。→ Production資産の`research_pronunciations`(Perplexity)は現状このアカウントでは使えない(下記9章の判断候補)。
- **V1'(R-04)**: Veraはsource URLを実HTTP取得しquote(`/ˈvɪərə/ /ˈvɪrə/`)の本文一致を確認(`V1p_detail.quote_found=true`)。Japanese-only(PR TIMES)は取得・quote存在は確認(`j7_evidence.json: quote_found=true`)だがV2で不可。
- **Ledger登録(5-1)**: Trial Ledger差分=追加1件(Vera)・既存38件のentryは不変(`existing_entries_unchanged=true`)。実Ledgerのsha256は開始/終了で不変(`real_ledger_unchanged=true`)。Trial Ledger=`ledger_trial_copy/ledger.json`(sha256 `results_summary.json`参照)。
- **PL投入・重み2.0(5-1の「実投入証拠」)**: Production関数`get_full_text_via_azure_stt_with_phrase_list`を実呼出し、SDK診断ログ(`Speech_LogFilename`)の`speech.context`から`dgi.Items`/`bias`を呼出ごとに1行記録(`phrase_list_evidence.jsonl`、18行)。**PLありの全8呼出で`dgi.Items==期待PL ∧ bias==[2.0]`が一致、PLなしの全10呼出に`dgi`なし**。引用(1行目): `"phrases_expected":["byUs","LINE"],"dgi_items":["byUs","LINE"],"bias":[2.0],"match":true`(wav=full_story_part1_attempt1)。この8呼出のPLは「**テスト用フィクスチャLedger(byUs/LINE登録を仮定)→Production `get_hint_for_text`→`phrases`引数**」で構築した腕M(後述)であり、K1が未達のため**実際のEvidence付き登録を経由したPLではない**(機構の証拠であって要件達成ではない)。生ログ(認証情報を含み得る)は抽出後に削除、repoに残していない。

## 3. ASR・同音判定への効果(R-08: 仮説=「Azureの多語化`Buy Us/by us`をbyUsへ寄せられるか」)
条件: baseline=現行Production相当(実LedgerでPL空)/ 腕M=綴りのみ直接供給(`["byUs","LINE"]`または`["byUs"]`、重み2.0、**Ledger登録を介さない=Production関数経由のLedger供給ではない**ラベル)。Azureは各条件1回+差異wav(2本)の2回目+決定性確認(2本)。計18呼出、JPY40.22。
| wav | baseline(PL無)のbyUs/LINE箇所 | 腕M | 判定(Secondary許容集合式) |
|---|---|---|---|
| part1 att1 | `Buy Us`(多語化)+`bias` | `byUs`+`bias`(単語化) | **NG→PASS**(`TRUE_CONTENT_MISMATCH`→`NORMALIZED_MATCH`)。2回目も同結果(再現2/2) |
| part1 att2 | `bias`x2、LINE箇所: `LINE`/`Lion` | LINE箇所: `LINE`/`LINE` | 変化なし(NG維持、他の差分で不一致)。`Lion→LINE`(再現2/2) |
| part1 att3 | `bias`x2 | 同 | 変化なし |
| part3 att1 | `by us`(多語化) | `by us`のまま | 変化なし(PLでも多語化が残る) |
| part3 att2 | `by us` | `by us`のまま | 変化なし |
| part3 att3 | `bias` | 同 | 変化なし(元からPASS) |
- 多語化(`Buy Us/by us`)が見られた3例のうち消えたのは1例(33%)。NG→PASS 1件・PASS→NG 0件・変化なし5件。決定性: pass2を取った6呼出はすべて転写一致(Azureはこの条件で再現的)。
- **誤PASSリスク(要注意の観測)**: att2の2か所目`LINE Manga`は、PL無のAzureとlocal whisper mediumが`Lion`と転写、Primaryのみ`LINE`。つまり音声が実際に`Lion`寄りに発音されている可能性が高い(独立2/3)箇所で、PL(`LINE`)が転写を`LINE`へ寄せた。この例は他の差分で判定自体はNGのままで誤PASSは発生していないが、**「PLが実発音の誤りを転写上で隠す」経路が実在する**ことを示す(§6.2「実音声の誤りをASRでPASSさせない」への示唆)。PLを使う運用では、Lion型のTTS誤発音をPL有Azureの結果だけで救済しないこと(PL有は独立証拠として使わない=R-09)が必要。
- 悪化(PASS→NG)0件・誤PASSの判定反転0件は事前基準を満たす。ただし「効果」は6例中1例のみ(Z重みTrialの効果限定と同傾向)。part2対照(byUs/LINE無)はPL内容が同一(空)のためAzure呼出を省略(同一入力で出力分布が変わらないため)。
- Z: baseline PL(実Ledger)=`["Melos"]`、Trial Ledger由来PL=`["Melos"]`(登録できた名前にMelosがない)で同一。**Z側は既存の汚染entry(`melos` cascade)経由で既にPLが入っている**ため、本供給仕様が追加でPLを変える余地は現時点ではない。

## 4. 同一性検証(判定基準を動かしていない: R-02)
`evaluate_attempt_with_cascade`(M1有効)に既存Primary/Azure転写を注入(実ASR・実Azure=0)、条件ごとにM1 cache resetと`LEDGER_PATH`切替、26ケース(X:10[実attempt 7+合成3]、Z:16)x3条件(base=実Ledgerコピー/trial=実際に登録できた分/hypo=byUs・LINE・Melos・Framton・Nuttel・Sappletonを登録した場合を仮定するテスト用フィクスチャ[事実主張ではない])。
- X 10ケース: base対trial 差分 **0**、base対hypo 差分 **0**(verified/final_status/classification/judge_state/layers のいずれも不変)。
- Z1 16ケース: 判定変化 **0**(trial/hypo とも)。M1のC2音素候補集合はhypoでも16/16不変(`candidate_set_hash`は時刻を含み毎回変わるため、時刻を除いた`stable_candidates_hash`の変化は`also_from`の出典記録のみ)。
- 注意: hypoのフィクスチャIPAは既存`melos` cascade entryの候補と同じ音素列になるため候補集合が不変だった。実際に登録されるIPAが異なれば候補は増え得る(M1の発動範囲が広がるかは、実登録IPA次第=Opus最大グレー点は本データでは顕在化せず、ただし未反証ではない)。
- 共存時の記録(R-06): byUsは`ja_reading_katakana`(高confidence・hint空)と、Melosは`ja_reading_katakana`+`cascade_unresolved_entity`(low・汚染hint「MEE-lahs（英国寄りなら MEE-loss）」)と共存。拒否権は品質基準を満たすEN entryのみ(これらは拒否権なし=V5判定に使わない)。同一性の結論は上記のとおり差分0。

## 5. 漏れ件数(R-05、費用0)
過去run全EN segment本文 1,406ユニークに対し`get_hint_for_text(min_confidence="low")`を再計算。
| 名前(登録した場合の発火) | ホーム記事 | ホーム以外 |
|---|---|---|
| byUs | 11 | **0** |
| LINE | 6 | **34**(一般語lineを含む無関係テキスト。例: `er003_output/...`) |
| Melos | 45 | 2 |
| Dionysius/Selinuntius/Framton Nuttel/Nuttel/Framton/Sappleton/Vera | 0 | 0 |
- 実際に登録できたVeraの漏れ=0件。**LINEは登録すると無関係34テキストでPLに`LINE`が入る**(大文字小文字を区別しない一致のため)→「CMU収録語で公式発音=CMU代表発音の語は登録不要(CMU層で足りる)」案が妥当(本命)。
- 参考(J5、既存問題の定量化): 実Ledgerの`us`(cascade_unresolved_entity, canonical=`unknown`, low)は過去EN本文76ユニークテキストでPLに`unknown`を入れる(語`us`を含むだけで発火)。

## 6. 費用・時間・量産影響(5-5)
| 項目 | 実測 | 出典 |
|---|---|---|
| 総額 | **JPY113.10**(Cap200)。D2検出 1.82(sol 3呼出1.57+luna 3呼出0.25)/ 研究腕A 70.45(2呼出: 通常7名37.90+英語情報源特化2名32.55)/ 腕B 0.20(失敗呼出の最小仮置き)/ Azure 40.22(18呼出、1呼出平均2.2)/ K3 ASR 0.41 | `paid_calls.jsonl`、`results_summary.json` |
| 呼出数 | 28(D2:6、腕A:2、腕B:1[失敗]、Azure:18、ASR:1) | 同 |
| 設計外API呼出 | **0**(`isolated/unexpected_calls.jsonl` 0行、各stage出力の`unexpected_calls`すべて空、`paid_calls.jsonl`の種別は計画上の5種のみ) | 同 |
| 日次 | 開始時JPY303.75 + 本Trial約113 = 約417/1,000 | `daily_dev_cost_01.py`、上記 |
| 時間 | 研究腕A 64秒/44秒、D2 4〜11秒/呼出、Azure 1呼出約25秒(約50秒音声)、Trial全体約2.5時間 | `paid_calls.jsonl` |
- 70円/記事セットへの影響(Sonnet所見): 検出(D2 sol)は記事単位1呼出で**約0.5〜0.6円/記事**(luna約0.1円)で安い。一方、**研究(web_search)は7名一括で約38円(約5.4円/名)、英語情報源特化の追加検索で約32.6円**と高く、今回は7名中登録できたのは1名(Vera)のみ。登録できない名前(公式英語発音が無いbyUs型、固有名詞として発音情報が音声のみのFramton Nuttel型)に毎回研究費を払う運用は**原価悪化**になりやすい(1記事に未登録名2〜3語で約11〜16円/記事、2記事目以降は同名ならLedger cacheで0円)。今回測れた削減効果は、byUs由来の再試行1組(約5.16円+10分)をPL(腕M)で回避できた可能性が1例(6例中)のみ。**費用対効果は現状プラスと言えない**(最終判断はFable/ユーザー、J2/J7とセット)。
- 安いルート案(判断材料): (a)CMU収録語(LINE/Vera型)は研究せず登録しない、(b)D2検出(約0.5円)でCamelCase等の候補を出し、**綴りだけをPLへ供給(J2)**するなら追加の研究費0で腕Mの効果が得られる(ただし§3-7との緊張とLion型の隠蔽リスク)。

## 7. Opus Go条件4点の反映証拠(Fable評価用)
| 条件 | 反映 | 証拠 |
|---|---|---|
| R-01 研究API stub化+隔離+test固定 | `TrialIsolation`(lib.py:126-)が`research_pronunciations`を腕Bコンテキスト外でstub化(記録して失敗返却)、Azure関数を注入stub化、HR queue・attempt_history・er025/er021 telemetry・cost loggerをTrial dirへ。Trial LedgerコピーのみにLEDGER_PATH差替え、実Ledgerへの書込は`register_entry`が拒否 | test `IsolationTest`(5本)・`DefaultOffIsolationTest`・`IdentityHarnessTest`(20本中、API 0でPASS)、`isolated/unexpected_calls.jsonl`=0行、`results_summary.json:unexpected_calls.count=0`、実Ledger sha256不変 |
| R-02 同一性検証の経路 | `evaluate_attempt_with_cascade`(M1有効)経由、既存転写注入、条件切替ごとに`_reset_m1_freeze_cache()`+`LEDGER_PATH`切替(`run.py:eval_case`)、`stable_candidates_hash`とM1 candidate_set_hash記録、Z1は変化集計へ分離 | `s3_identity_results.json`(X差分0、Z1変化0) |
| R-04 V1' | `verify_quote_in_source`(lib.py:823-)、`UNCONFIRMED_SAFE[source_unverifiable]`。音声/動画源は`media_source_quote_not_text_verifiable`で不可 | test `test_v1p_pseudo_word_zorbleflux_falls`/`test_v1p_quote_not_in_page`、Vera実HTTP取得でquote一致 |
| R-06 V5拒否権の限定 | `en_pron_info_qualifies`(lib.py:410-)が拒否権の条件、low/汚染hint/ja_reading_katakana/cascade_unresolved/sources空は拒否権なし。共存M1候補集合を記録 | test `test_v5_veto_limited_to_qualifying_entries`、`s3_identity_results.json:frozen_candidate_set` |

## 8. その他の採用所見の反映
- R-05(漏れ測定): §5。 R-08: §3(仮説の絞り込み、腕Mラベル)。 R-09: `k5_votes.json`(投票者=Primary/Azure PL無/whisper medium、Azure PL有は除外、AMBIGUOUS=試聴要否報告)。 R-10: Azure 18呼出に圧縮(当初見積44呼出)。 R-11: (a)複数語surface`Framton Nuttel`はPL=句全体/M1=語ごと(M1はsurfaceに空白を含むentryをC2から除外)、(b)CMU収録: dionysius/vera、未収録: melos/selinuntius/framton/nuttel/sappleton、(d)所有格`Melos's`はD1で語幹処理しZ1に含む。 R-12: D1に`R_LEDGER_JA_KATAKANA_LATIN`・`R_JA_GATE_UNKNOWN_LATIN`を追加、D2は記事単位1回。
- R-07の別件(本Trial範囲外・事実のみ): 記事B本文"It is pronounced 'bias.'"の元になった可能性のあるFact。Research Ledger `er019_output/manga_ai_chat_byus/run_byus_01/research_ledger/verified_fact_ledger.txt:1`(F01)に「LINE Digital Frontierは、LINEマンガでAIストーリーチャットサービス「byUs（バイアス）」をリリースしたと発表した」とあり、**日本語の読み「バイアス」がFactに含まれる**。英文の"pronounced bias"はこの日本語読み(カタカナ)からWriterが英語読みを推定した可能性がある(英語公式の発音記載は今回の英語情報源調査でも見つからず)。J7に関係。
- 腕Nは実施せず(TTS生成禁止)。K5(ii)は決定的出力+実音声3エンジン多数決のみ。

## 9. 判断候補(Sonnetは付与せず、27-3の A/B/C/D 案のみ)
| ID | 内容 | 分類案 | 根拠 |
|---|---|---|---|
| J6 | PL/M1用の取り消し手段+自動/人手entry区別(OPEN-339)=採用前提条件 | D(DEFERRED) | 委任文 |
| J7 | 権利者の公式な日本語読みが英単語と一意対応する場合(byUs→「バイアス」→bias)の登録可否 | D | K1安全終了の唯一の代替。証拠: PR TIMES原文の該当箇所は`j7_evidence.json`(quote_found=true)、英語情報源(WEBTOON IR等)にはbyUsの発音記載なし(`s3_research_extra_raw.json`) |
| J2 | 読み未確定語のPL供給(綴りのみ)の是非 | D | 腕Mで6例中1例NG→PASS・Lion隠蔽1例。§3-7との緊張 |
| J3 | 判定基準の拡張の必要性の測定結果(測定のみ・不実装) | 情報 | 多語化`Buy Us/by us`が見られたPL無Azure転写3例(part1 att1, part3 att1, part3 att2)について、転写側の`Buy Us/by us`を`Bias`に置換した反実仮想で既存の許容集合式を通すと**2/3がPASSになる**(part1 att1、part3 att1。part3 att2は`20 works`等の他要因で不通過)。判定関数は変更していない(`results_summary.json:J3_counterfactual_multiword`)。辞書外綴り(Baias/BAYAS/FAYAS)は今回の再転写(Azure)では再出現せず測定対象外。要否は採用時のユーザー判断 |
| 新規 | Perplexity利用枠切れ(`401 insufficient_quota`)。Production資産`research_pronunciations`が現状動かない可能性 | B/Cの境界(外部課金の復旧はユーザー側) | 腕B実行ログ。docsではSonar Chat Completions終了(2026-09-27) |
| 新規 | EN研究費(約5.4円/名、追加調査で約16円/名)が70円目標に対して高い。登録対象を絞る運用(CMU収録語は研究しない等)の要否 | D | §6 |
| J5 | 既存汚染entry`us`が76テキストでPLに`unknown`を入れる(定量化) | B | §5 |
