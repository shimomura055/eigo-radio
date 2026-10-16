## Opus独立技術レビュー: AUW A3(length NG)の是正設計D1(11-3 条件A、実装前、read-only、費用JPY 0)

### 総評
D1の方向(A3による事前除外の撤廃、Secondary転写でのlength再評価、呼出元ANDの置換)は、A-2太字(Secondaryの正当なPASSを拒否しない)と#7(数値・否定・独立QAの維持)の両方に整合します。**条件付きで同意**します。ただし、IMPLEMENTATION_11 §3-3のD1をそのまま実装すると、次の3点で安全性または仕様整合に穴が残ります。
- **(i) EN 6箇所にmax_lenを渡す設計がない**(A3R-01)
- **(ii) 「Primary内容PASS+length NG」がSecondaryへ回らない**(A3R-02)
- **(iii) 呼出元を1箇所でも直し忘れると、現状より悪化する**(A3R-03)

以下の修正を入れれば、実装に進んでよいと判断します。ユーザー判断が新たに必要になる事項はありません(Q6)。

### Q1. A-2 #7との整合と、守るべき失敗モード
- 整合します。`length_ok`はPrimary転写の文字数から計算した値です(例: `er003_v1_crosslevel_audio_02_common.py:348`)。音声そのものを調べる独立QAではありません(U1R-04で確認済み)。#7の「独立音声品質QA」に当たるのは、次の3つです。
  - `dq18.apply_disfluency_gate`(言いよどみ検査)
  - `repetition_qa.apply_repetition_qa_gate`(繰返し検査)
  - `safety.detect_duration_anomaly`(音声長異常の検出、`er003_audio_tts_asr_safety.py:189`)
  - 前の2つは呼出元で`verified`へANDされています(例: `er003_v1_repro01_main_generate.py:367-374`、`news_tail_fix:213-219`)。length項の置換後も、これらを順序どおり残すことが条件です。
- **lengthが守っているのは「上限超過」だけです。** 判定は`len(asr) <= max_len`なので、捕捉できるのは余分な発話(指示文の読み上げ、繰返し、生成の暴走)です。**途中切れはlengthでは捕捉できず、内容Validatorの担当です。** OPEN-388の「過短/過長」という記述は「過長」に訂正すべきです(MINOR)。
- 修正後の捕捉力
  - Azureは連続認識で音声全体を転写します(`er006_secondary_asr_01.py:132`)。部分転写はerror扱いで、合格の根拠になりません(`:115-147`)。
  - そのため、音声に実際に余分な発話があれば、Azure転写も長くなってNG_BOTHになるか、許容集合判定で不受理になります。救われるのは主に、Primary(OpenAI)が無音・ノイズから作った幻覚の尾部(実際には発話されていない文末の定型句)です。これはA-2が想定する正当な救済です。
- **残るリスク(JA中心)**: 言葉にならない雑音や崩れた発話を、OpenAIは文字化し、Azureは無視することがあります。この場合、lengthも内容判定も通ります。ここを最後に受け止めるのは、`detect_duration_anomaly`(上限は粗い)とWARNING試聴リスト(A-2 #4)です。JAには繰返しQAがありません。
  - 推奨: Secondaryで救済した際にPrimaryの超過が大きい場合は、additiveなwarning label(例: `PRIMARY_LENGTH_EXCESS`)を付け、試聴担当者に注意を促す。受理の判定条件は変えません(MINOR)。

### Q2. 呼出元10箇所の見落とし経路
- **[MAJOR] EN 6箇所はlength_okもmax_lenもjudgeへ渡していません。**
  - 対象: crosslevel:361、repro01:355、news_tail_fix:206、point_headings、voice01:255系、FamilyB:557。
  - ENのctxは`actx.get("length_ok", True)`です(`er006:920`)。
  - **このためENでは、今すでに「Secondaryを呼んだ(費用発生)のに呼出元ANDでNG」が起きうる状態です。** 是正の実益はむしろENにあります。
  - D1の「JA 4箇所はmax_lenも渡す」だけでは、ENでSecondary転写の長さを計算できません。**EN 6箇所もattempt_ctx経由でmax_lenを渡すことが必須です。**
- **[MAJOR] max_lenは呼出元ごとに異なります。** 余裕文字数`max_extra_chars`が10/15/20/30/40/60と違います(repro01:199,808,822、n3:303,661,786,1221-1307、crosslevel:81)。judge内で`len(text)+15`のように再計算してはいけません。**呼出元のmax_lenをそのまま渡します。** Local Rewrite後(v1)は、書き換え後の文で計算した`retts_max_len`(crosslevel:408)が渡ることを確認してください。
- **緩む方向の経路(fail-open、安全側が緩む失敗)**: helper `final_length_ok`は次の形で**fail-closed(不明なら厳しい側に倒す)**にしてください。
  - Primary由来のlengthを置き換えてよいのは、次の4条件をすべて満たすときだけ: `asr_judgement`が存在する/stateがPASSING/`audit["length"]["adopted_from"]=="secondary"`/`adopted_ok is True`
  - それ以外(cascade無効でrecordなし、Primary ASR失敗、旧経路、detail欠落)は、Primaryのlength_okを返す。
- 経路別の注意点

  | 経路 | 注意点 |
  |---|---|
  | 初回・減速後(repro01:366/388、voice01:255/527) | 一般形。置換はlength項のみとし、disfluency/repetitionのANDは不変 |
  | minimal fallback(crosslevel:368、n3:734、voice01:579) | crosslevelは`force_secondary=True`。A3R-02の降格と組み合わさったときの扱いに注意 |
  | Local Rewrite後v1 | max_lenは書き換え後の文で計算した値を使う |
  | KP(max_extra_chars=10、`adopted_text`経路あり) | Primary PASSの根拠が別転写のとき、lengthもその転写(`gate_text`、judge:365)で測るのが06c原則と整合。現状は呼出元がOpenAI転写長でANDしており不整合 |
  | narrator(news_tail_fix) | `force_secondary`なし(U1R-06既知)で通常形 |
  | JA全般 | `er007_ja_secondary_asr_01.py:664-665`の診断文「length_not_ok…不実行」はA3撤廃後に誤記録になるため要更新 |
- 記録: 各attempt logの`length_ok`(Primary)は残し、`final_length_ok`を追加してください。「length_ok:falseなのにverified:true」が説明なしに並ぶ状態を避けるためです。

### Q3. 再計算の基準
- **EN/JAとも、呼出元のmax_lenを使った同じ生文字数式**(`len(stext) <= max_len`)を推奨します。Primaryと基準を揃えるためです。正規化した長さへの変更は閾値の意味を変えるため、今回は行いません。
- 偽NG(本当は問題ないのにNGになること)の懸念
  - ENのAzure表示形式は数詞を数字に変える(ITN)ため、短くなる方向です。
  - JAは英単語のカタカナ化や読点で長くなりえます。ただしPrimaryも同じ性質を持ち、偽NGになっても結果は再生成です。現状(Secondaryを呼ばず再生成)より悪化はしません(Secondaryの費用増のみ)。
- 対策: audit `length`に`primary_len / secondary_len / max_len / surface_len(正規化後の参考値)`を記録し、偽NGが出るかを観測できるようにします(判定には使わない)。

### Q4. 段階実装
- **推奨は(a)一括10箇所です。ただし「max_lenを渡された場合のみ新挙動」という安全ラッチを付けます。** judgeは`ctx.max_len is None`なら従来どおりA3除外(JA)/従来挙動(EN)とし、max_lenがあるときだけA3を外して再評価します。
  - 利点: 直し忘れた呼出元は自動的に旧挙動のままになり、悪化しません(A3R-03を解消)。
  - 補完: 10箇所すべてがmax_lenを渡し、`verified_content and length_ok`が残っていないことを静的testで保証します。
- (b) 部分先行: ラッチがない状態で行うと、未修正のJA呼出元で「Secondaryを呼んだ後にNG」(s4が指摘した悪化)が起きます。ラッチ付きなら技術的には可能です。しかしEN/JAの不整合期間ができるため推奨しません。
- (c) judge側で`length_ok=True`に上書き: **不採用。**
  - 呼出元のローカル変数は外から書き換えられないため、結局呼出元の修正が必要です(D2と同じ問題)。
  - 文字どおり「True上書き」にすると、Secondary転写が長い場合のチェックが消えて安全側が緩みます。
  - 「再計算した値を返す」形にするなら、それはD1そのものです。
- A3ルールは表から削除せず、module定数(env/flagではない)で無効化しておくと、U1と同様にrollbackしやすくなります(MINOR)。
- 工数見込み90〜120分は、呼出元ごとのunit testと静的testを含めるとやや楽観的です。120〜180分程度と見込むのが妥当です。

### Q5. 必要十分なtest/evidence
- API 0のunit(judge単体、EN/JA両方)
  1. 内容NG+length NG、Secondary受理+length OK → PASS_WITH_WARNING。audit `adopted_from=secondary`
  2. Secondary受理+length NG → NG_BOTH(`secondary_length_ng`)
  3. Secondary不受理 → NG_BOTH(従来どおり)
  4. length NGでも数値差/否定差 → NG_PROTECTED、Secondary不呼出(P1優先)
  5. length NGでもA4/A7 → NG_EXCLUDED(登録読み保護A7は不変)
  6. Primary PASS+length OK → PASS、Secondary不呼出
  7. Primary PASS+length NG → 降格してSecondaryへ(A3R-02)
  8. force_secondary+length NGで両エンジン合意 → PASS_WITH_WARNING(`force_secondary_agreed`の無警告PASSにしない)
  9. length NGからSecondary障害 → NG_SECONDARY_UNAVAILABLE(A-6の挙動は不変)
  10. `max_len=None` → 旧挙動
  11. helperのfail-closed(detail欠落・cascade無効・Primary ASR失敗)
- 呼出元レベル(mock): 10箇所それぞれで「Primary長い/Secondary短く受理 → verified True」を確認。さらにdisfluency/repetitionのgateをFalseにmockし、final Falseになること(#7の維持)を確認。max_lenが呼出元の値(v1は書き換え後の文)と一致すること。
- 静的test: Production 10箇所に`and length_ok`が残っていないこと、max_lenを渡していること。legacy/Trial scriptは明示的な除外listで管理。
- 試聴リスト: 新経路のPASS_WITH_WARNINGが、segment最上位の`asr_judgement`から導出されること(`er078_pass_with_warning_registry_01.py:24`)。
- 実音声(最小2 clip、Azureのみ、TTS生成なし、JPY 1未満)
  - (正例) 既存の合格wavに、Primary転写を「原稿+max_len超の尾部」へ差し替えるmockを当て、実Azureで受理+length OKを確認。
  - (負例) 既存wavを2本ローカルで連結した音声に、片方の原稿を当て、実AzureでNG_BOTHになること(長さまたは不受理)を確認。安全側の実証として必須です。
  - JA/ENのどちらか片方でも可。余力があれば両方。

### Q6. 新たなUSER_DECISION_REQUIRED
- **生じません。** A-2 #2・太字・A-3「等」・U1R-04・OPEN-388の範囲内の実装修正です。Primary PASS+length NGの降格もA-2 #2の適用です。
- ただし次の拡張をする場合は新仕様になり、ユーザー判断が必要です: 音声長と転写文字数の比による新たな不合格gate、length閾値の意味の変更(正規化長への切替)、HR Lock/A-6挙動の変更。
- 付記: 最終slotでNG_BOTH(`secondary_length_ng`)になると、wrapperが`human_review_required=True`を立てます(`er006:996`)。これは既存の「両方NGの最終slot」と同じ意味なので、Lock変更には当たりません。

### 指摘一覧
| ID | 重大度 | 内容 |
|---|---|---|
| A3R-01 | MAJOR | EN 6箇所はlength_ok/max_lenをjudgeへ渡していない(`er006:920`)。ENでは今すでに「Secondaryを呼んだ後に呼出元ANDでNG」が起きうる。EN含め全10箇所で、呼出元のmax_len(10〜60で異なる)をctxへ渡すこと。judge内で+15を固定再計算しない |
| A3R-02 | MAJOR | D1は「Primary内容PASS+length NG」を従来どおりPrimary lengthでNGとし、Secondaryへ回さない。A-2 #2と不整合。judgeでP3へ降格(`primary_length_ng`、AMBIGUOUS降格と同じ形)し、合意時はPASS_WITH_WARNINGにする。Primary length計測は`gate_text`(adopted_text)基準 |
| A3R-03 | MAJOR | 呼出元の直し忘れが悪化に直結する構造。`ctx.max_len`の有無を新挙動のラッチにし、静的testで10箇所を保証。helperはfail-closed |
| A3R-04 | MINOR | (c)案は不採用(呼出元修正は不可避、True上書きはSecondary転写長のチェックを失わせ安全側が緩む) |
| A3R-05 | MINOR | `er007_ja_secondary_asr_01.py:664-665`の`length_not_ok`診断文と、length_ok引数のdocstring(:538)の意味を更新。A3除外を前提にした既存test(旧挙動固定)の棚卸し |
| A3R-06 | MINOR | attempt logに`final_length_ok`とaudit `length{primary_len,secondary_len,max_len,adopted_from,adopted_ok}`を追加。Primaryの`length_ok`は残す |
| A3R-07 | MINOR | Secondary救済時にPrimary超過が大きい場合、試聴用warning label(`PRIMARY_LENGTH_EXCESS`等)を付与(受理条件は不変)。JAの非語彙的な雑音リスクの事後捕捉用 |
| A3R-08 | MINOR | OPEN-388の「過短/過長」を「過長(上限のみ)」に訂正。途中切れは内容Validatorの担当 |
| A3R-09 | MINOR | A3除外の撤廃によりSecondaryへ回る件数が増え、Secondary障害への露出がわずかに増える(A-6の挙動は不変、記録のみ)。工数見込みは120〜180分が妥当 |

### 確認した証拠(file:line)
- `C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py`
  - 121、138(A3)
  - 222(`AttemptCtx.length_ok`、max_lenなし)
  - 365(gate_text=adopted_text)
  - 386-392(AMBIGUOUS降格・force_secondaryの前例)
  - 405-408(P2除外)
  - 489-497(Secondary受理からPASS/PASS_WITH_WARNING)
- `C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py`
  - 132-147(連続認識・部分転写の扱い)
  - 917-922(EN ctx、length_ok既定True)
  - 935-951(許容集合判定)
  - 971-1015(verified・HR・asr_judgement)
- `C:\Users\tensh\eigo-radio\er007_ja_secondary_asr_01.py`: 538-539、612、661-666、739-749
- `C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py`: 81、166、343-381、408
- `C:\Users\tensh\eigo-radio\er003_v1_repro01_main_generate.py`: 199、292、346-390、808、822
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py`: 716-748
- `C:\Users\tensh\eigo-radio\er003_v1_sing01_news_tail_fix.py`: 137、160-219
- `C:\Users\tensh\eigo-radio\er003_v1_sing01_voice01_generate.py`: 482、505-583
- `C:\Users\tensh\eigo-radio\er003_audio_tts_asr_safety.py`: 189-203
- `C:\Users\tensh\eigo-radio\er078_pass_with_warning_registry_01.py`: 24-32
- `C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\IMPLEMENTATION_11.md`: §3(29-53)
- `C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\OPUS_REVIEW_C2_U1_VERBATIM.md`: 28-29、72
- `C:\Users\tensh\eigo-radio\OPEN_ITEMS.md`: 897(OPEN-388)
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`: 45-78、117-141

### 確認範囲の注記
- point_headings:120-135とFamilyB:540-560は、Grep結果の行だけで確認しました(`verified_content and length_ok`の形とmax_len=+15の定義)。
- n3:630の`detect_duration_anomaly`がJAのminimal fallback(n3:720、voice01:567)にも効いているかは未確認です。実装時に確認してください。効いていない場合、A3R-07の優先度が上がります。