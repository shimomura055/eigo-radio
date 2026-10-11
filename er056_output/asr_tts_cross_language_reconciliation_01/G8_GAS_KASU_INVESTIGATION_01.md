# G8_GAS_KASU_INVESTIGATION_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01、2026-10-11)

対象: Phase 0 Trial g8 `kp4_ja_charon` attempt1(原稿「熟すと出るガス」)。SCG(OPEN-258、PRODUCTION_WIRED)で「ガス->カス」のため救済対象外になった件。
方法: 保存済みrun記録・Phase 0 Trial記録・SCG回帰test・現行コードをオフラインで照合。有料API未使用(API未使用)。Productionコード無変更(monkeypatchによる仮想実行のみ)。
「確定」=コード/ログで確認、「推測」=確認できていない解釈。結論は最後の(e)。

## 事実の整理(確定)

| 項目 | 内容 | 根拠 |
|---|---|---|
| 音声 | `er011_output/household_unified_final_candidate_01/b1b/narration/attempts/kp4_ja_charon_attempt1_standard.wav`(2.28秒、Charon、gemini-3.1-flash-tts-preview) | attempt json、`results_01.jsonl` |
| 原稿 | 熟すと出るガス | 同上(sha256照合で確定原稿) |
| Primary(gpt-4o-mini-transcribe) | 「じくすと出るカス。」 | attempt json |
| Azure Secondary(Phase 0、Phrase Listなし、約1.0秒) | 「熟すと出るガス。」(NORMALIZED_MATCH) | `results_01.jsonl` |
| whisper small / medium(ローカル補助、原稿非提示) | 「ジュクスト出るガス」/「ジュクスと出るガス」(「ガス」は2モデルとも濁音、「熟す」の読み「ジュクス」も一致) | `whisper_aux_01.json`、manifest |
| 実際の運用結果(2026-09-09、SCG導入前) | attempt1=NG(TCM)->再生成attempt2=「熟すと出るガス。」でNORMALIZED_MATCH合格。再生成1回 | `kp4_ja_charon_attempt2_standard.json` |
| 現行コード(SCG有効)でのg8 | `scg_result=NOT_APPLIED`、`exclusion_reason=entity_like_diff:ガ->カ`、Azure呼出0回、`verified=False`、TCM維持=再生成 | 下記「実行確認」、`er007_ja_scg_phase0_regression_test_01.py` `test_g8_excluded_by_implementation_not_fixture`(L239) |

実行確認(今回、オフライン): `evaluate_attempt_ja_with_cascade_detail`をAzure STTだけmock(保存済みPhase 0転写を返す)で実呼出し。
- 現行そのまま: `verified=False / final_status=TRUE_CONTENT_MISMATCH / scg_result=NOT_APPLIED / reason=entity_like_diff:ガ->カ / azure_calls=0`
- C1のentity_likeだけ外した仮想(monkeypatch、Production無変更): `verified=True / final_status=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG / scg_result=PASS / azure_calls=1 / Secondary=NORMALIZED_MATCH`
- `er007_ja_scg_phase0_regression_test_01.py` 12件PASS(再実行、現行HEAD)。

## (a) PrimaryがNGとなった理由(確定)

現行`classify_ja_asr_match`(Reading Resolver OFF)でTRUE_CONTENT_MISMATCH(類似度0.667)。差分(content_diffs)は2つ:

| # | 原稿 | Primary | entity_like | phonetic_uncertain | cascade_eligible |
|---|---|---|---|---|---|
| 1 | 熟 | じく | False | False | **False** |
| 2 | ガ | カ | True | True | True |

- **NGの直接原因は#1**(「熟す」を「じくす」と転写)。読みは原稿`じゅくす`、Primary`じくす`(「ゅ」欠落、pykakasi)で、読みが一致しない非cascade diff。VAL L406-489のとおりTCMになる。
- #2「ガス->カス」は単独ならUNCERTAIN(cascade対象、VAL L491-498)の濁点差。カタカナ同士のreplaceなので`entity_like=True`にもなる(VAL L307)。
- 判定コード: `TRUE_CONTENT_MISMATCH`。差分種別: 漢字->ひらがな(読み欠落)+カタカナ濁点差。数字・否定差なし。
- 付記(確定): #1が無く#2だけなら、旧Cascade(Primary#2->Azure#1->Azure#2)がAzureを呼ぶ(合成確認: 「出るガス」/「出るカス」=UNCERTAIN)。つまり**ガス/カス単独ならSecondary確認が走る**。

## (b) Secondary確認を実施しなかった正確な条件(確定)

1. Primary=TCMなので`SEC L399`のSCGブロックに入る。
2. `_scg_exclusion_reason`(SEC L183-210)が順に評価: 分類=TCM(L189)、数字差なし(L191)、否定差なし(L193)、類似度0.667>=0.4(L195)。
3. `for d in content_diffs`(L197-205)で、#1(熟->じく)は全フラグFalseで通過。**#2(ガ->カ)で`d.get("entity_like")`がTrue -> `return "entity_like_diff:ガ->カ"`(L200-201)**。
4. `evaluate_attempt_ja_with_cascade_detail`は`exclusion is not None`なので`scg_info={"scg_applied": False, "scg_result": "NOT_APPLIED", "exclusion_reason": ...}`(L405-406)を作りAzureを呼ばず、L424-425で`cls.scg_info`だけ付けてTCMのまま返す(=TTS再生成/fallback/STOPへ)。
5. ログ: 上記の実行確認のほか、Production条件のPhase 0回帰test(`er007_ja_scg_phase0_regression_test_01.py` L163「executed 21 = 24 - g8(C1除外) - g12(推奨4) - g5(C2)」、L230-241)。**g8を実際にSCG導入後のProduction runで流した記録はない**(g8は保存済み音声のoffline回帰のみ)。

## (c) 固有名詞除外ルールの目的と承認根拠

目的(確定、記録どおり): Opus独立レビュー必須1(C1)「固有名詞除外の欠落」。`OPUS_REVIEW_01.md` L6、`OPUS_REVIEW_FOLLOWUP_01.md` §1。意図は「Azureが正しい固有名詞読みと偶然一致して誤PASSするのを防ぐ」(SEC L183-188 docstring)。
承認根拠:
- Opus必須1->Fable照合で採用。ユーザーのSCG V1採用(2026-10-11)・安全条件の中に「重大差分を救済しない」はあるが、**C1(entity_like/辞書読み/ラテン文字)をg8の13/14と引き換えに採用するというユーザー逐語決定は記録にない**(DL L20550)。
- DL L20550のFable Gate 3判定は「Phase 0救済は13/14(g8はC1除外、誤PASSではない)」とし、「g8を救済しない13/14のまま受入するかのユーザー最終確認」を`USER_DECISION_REQUIRED`に残している。OPEN_ITEMS L760も同旨。
- 関連する承認済み原則: 「ASR consensus ≠ pronunciation verification」(SPEC L1693、2026-08-28 `APPROVED_FOR_PRODUCTION`。英語の固有名詞でASR同士の収束だけでは自動PASSしない、CMU辞書/Human Review)。これは**固有名詞=発音の正解が一意でない語**を前提とした原則で、日本語の一般カタカナ語(ガス/ゴミ等)まで広げたとはSSOTに書かれていない(推測: C1はこの原則の延長として入れた可能性が高いが、記録なし)。
- 実装上の問題(確定): C1の`entity_like`は意味上の固有名詞判定ではなく「replaceで両spanのカタカナ率>=0.5または英字2字以上」(VAL L127-137、L307)。**「ガス」のような一般名詞のカタカナ語も、「ガ->カ」の1文字濁点差も、固有名詞扱いになる**。一方、カタカナの挿入/脱落(メタ->メタン)はVAL L320-322で`entity_like=False`となりC1除外にならない(合成確認、SCGは実行される)。ラベルと実挙動が一致していない。
- 旧承認との不整合(確定): 2026-08-25にユーザー承認された日本語ASR-first Retry Policy(SPEC L1998)は「entity-like mismatch検出時のみAzure Secondary」へ送る方針。SCGのC1は、同じentity_like差分でも**他に非cascade diffがある場合にはSecondaryに送らない**ため、旧承認の方針と逆の向きになる。

## (d) Secondaryに確認させた場合の誤PASSリスク

前提(確定): SCG PASSは「Azureの転写が**原稿全文**とEXACT/NORMALIZED一致」のみ(SEC L78、L320)。Azureは原稿を知らない(Phrase Listなし、SEC L284-286)。

| 論点 | 評価 | 根拠 |
|---|---|---|
| g8自体 | 3系統(Azure、whisper small、whisper medium)が「ガス」と転写。Primary(gpt-4o-mini-transcribe)だけが「カス」。**g8は真の誤読ではなくPrimary誤認の可能性が高い**(推測。ground truthは試聴のみ) | `results_01.jsonl`、`whisper_aux_01.json`。試聴音声: `https://shimomura055.github.io/eigo-radio/user_test/open258_phase0_listen_01/g8-kp4-ja-charon-a1.mp3`(Phase 0当日HTTP 200確認、今回未再確認) |
| Phase 0 C群(真のTTS誤り代理)の誤PASS | 0/5(Azureは原稿へ寄らず「縛られる」「体内どこ」「証拠が?と」「名称を…料亭」「形に始める」と逐語転写) | RESULT_01(2)、今回の再計算(JA_OFFLINE_COMPARISON_01.md) |
| 「カス」が真の誤読だった場合にAzureが「ガス」と転写して誤PASSするか | **実測0件(濁点/半濁点のTTS誤りを含むサンプルがC群に無い)ため確定できない**。構造的には、AzureがPhrase Listなしで音声だけから転写する限り、音声が「カス」なら「カス」と転写する可能性が高い(g12等でAzureは原稿寄りに丸めていない)。ただし高頻度語へのLM prior偏り(「社会/社外」型)は否定できない | 下記「LM prior偏りの実例」 |
| 濁点/半濁点のASR感度 | 既存SSOT上は「濁点/半濁点の有無だけの差」は`phonetic_uncertain`=ASR表記の不確実性(「頃/ころ」のkakasi読み限界)として扱い、TTS再生成でなくCascade(Azure確認)へ送る設計(ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01、`ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01_report.md` L12/L138、DL L149、SPEC L1993) | 同左 |
| TTS側の濁点誤りの実績 | JA attempt記録630件で`ASR_VALIDATION_UNCERTAIN`は1件のみ(TCM 76件)、濁点差のみの実例は「ころ/頃」2/96件(A2 preview、ASR表記でありTTS誤りではない)。TTSが濁点を取り違えた確認例は**今回の記録中に0件**。TTS誤りの典型は読み誤り(縛られず)、モーラ脱落(形になり始める)、別語化(旅程->旅亭) | JA attempt json 630件の再集計、`ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01_report.md` L209 |
| Primary側の不安定さ | 同一Primary(gpt-4o-mini-transcribe)がg8以外でも短い語で誤転写(肉/リクス<-理屈、買いせまい<-焙煎前、死図塔<-湿度)。25音声すべてでPrimaryはNG。Primaryの1文字単位の濁点判断は短い断片では信頼しにくい | `results_01.jsonl` |
| 偽陽性側(Azure PASSが誤り)の最悪ケース | Azureが高頻度語へ丸めて誤PASSした場合、音声に誤読が残る(ユーザーが最終Assemble後にしか気付けない)。ガス/カスは意味が近い範囲で影響は小さいが、害の大きい例は名前・企業名(濁点で別人/別社名) | 推測(影響評価) |

LM prior偏りの実例(確定): `er007_output/ja_asr_cascade_01/human_review_queue.jsonl`の「社外に漏れる」: Primary#1/#2もAzure#1/#2も「社会に漏れる」(4回全て同一)。しゃがい/しゃかいの濁点差で、**2エンジンが一致しても高頻度語(社会)へ偏った可能性があり、TTSが「しゃがい」と正しく言ったのか「しゃかい」と誤ったのかはASR転写だけでは確定できない**(推測)。SCGで言えば、ここで「Secondaryが原稿(社外)と一致」しない=NGに戻る側なので誤PASSは起きないが、逆向き(原稿が高頻度語、音声が低頻度語)なら誤PASSしうる。g8の場合、原稿「ガス」(高頻度)に対し音声が「カス」だった場合が該当する。

## (e) この除外が品質上必要か過度に保守的か

評価: **B(統一可能)、ただし固有名詞の一部は残す**(暫定、C寄りのB)。

理由:
1. **旧承認との矛盾**: 同じ`entity_like`差分が、単独のときは旧Cascade経由でAzure確認に進み(PHONETIC_MATCHもPASS、より緩い)、他diffと混在すると確認されない。「混在のほうが厳しい」には、それを正当化する誤PASS実績が見当たらない(g8は誤PASSでなく救済機会の喪失)。
2. **C1が守りたい本質は、全文一致だけでは発音の正否を判定できない語**(名前、社名、外来語の綴り-読み多対多)であって、「カタカナの濁点差」全般ではない。ラベルが粗いため、一般カタカナ語(ガス)も、1文字濁点差も巻き込む一方、挿入/脱落(メタ->メタン)は取りこぼす。
3. **g8のSCG PASSで失うリスクは小さい**: SCG PASSには`熟すと出るガス`全体とのEXACT/NORMALIZED一致が必要。一部(ガ/カ)だけのAzure丸めで誤PASSが起きるのは「音声がカスで、AzureがガスにLM偏りした」場合のみ。実測0件(濁点誤りの実績0、C群0/5)。
4. **費用/時間**: g8型の救済は再生成1回(約0.1円、120〜170秒)を回避。SCG呼出は約0.13円・1.4秒。金額ではなく、再生成による他のStyle/Voice揺れを避けられる点が主な便益。便益は小さい(Phase 0で14群中1群)。
5. **ただし完全に撤廃するのは推奨しない**: 真の固有名詞(人名・社名・地名・製品名)では「ASR consensus ≠ pronunciation verification」(SPEC L1693、2026-08-28承認)が日本語でも妥当で、原稿のカタカナ語がPrimary/Secondaryの偏りで揃うリスクがある。区別するには「辞書語/固有名詞リスト/NER」等の別の手段が必要で、今回は実装しない(提案のみ)。

選択肢(提案のみ、採用しない):
- 案1: C1の`entity_like`を「mixed diffでも、entity_like diffがcascade_eligibleかつ濁点差のみ(phonetic_uncertain=True)ならSCGを許す」へ限定(g8が救済、メタ->メタン型の取りこぼしは別途)。
- 案2: 旧Cascadeと同じ扱いに統一(entity_like diffがあってもSecondaryを呼ぶ。ただしSecondary PASSはEXACT/NORMALIZEDのみ)。
- 案3: 現行維持(g8は救済しない、ユーザー受入)。
- 案4: 追加Trial(下記)でAzure/Primaryの濁点感度を実測してから決定。

追加Trial案(実行せずSTOP、ユーザー/Fable判断):
- 目的: 「真のTTS濁点誤読をAzureが原稿語へ丸めて誤PASSするか」「Primaryの濁点誤認率」の実測。
- 設計: 濁点/半濁点の最小対(ガス/カス、ゴミ/コミ、デパート/テパート等)を高頻度側/低頻度側で20対、各2方向(原稿語を正しく読んだ音声、濁点を取り違えた音声[表記を変えた別テキストでTTS合成])=40クリップ。Production TTS経路と同一(`gemini-3.1-flash-tts-preview`、または現行Production標準。最新モデル原則の例外として「測定対象がProduction経路」と明記)、Primary=gpt-4o-mini-transcribe、Azure=Speech STT ja-JP。判定は構成上のground truthあり(試聴不要)。
- 費用見積: TTS 40クリップ約4円+Primary ASR約1円未満+Azure約3.6円(40x2秒x0.0444円/秒)=合計約9〜10円。モデルの最新性: TTSは現行Production(最新かは別途確認要)、ASRはProduction固定。
- 判断者: ユーザー(費用10円以下の少額API。メモリ方針「少額APIは確認不要」だが、新規Trialは別途Fable経由で承認を得る)。

## 結論

- g8の不救済は、**Primary NGの直接原因(熟->じく)とSCG除外の原因(ガ->カのentity_like判定)が別**で起きた副作用。誤PASS防止の実績はなく、実測では誤PASS 0。
- 現行ルールの理由づけ(固有名詞だから)は、コードの実挙動(カタカナ率ヒューリスティック)と整合せず、旧承認方針(SPEC L1998)とも逆。
- 品質上の必要性は「真の固有名詞」では認められるが、「ガス->カス」のような一般カタカナ語・濁点単独差まで除外する根拠は薄い -> 評価B(統一可能)、最終はUSER_DECISION_REQUIRED(g8 13/14受入の既存確認事項と同一)。
