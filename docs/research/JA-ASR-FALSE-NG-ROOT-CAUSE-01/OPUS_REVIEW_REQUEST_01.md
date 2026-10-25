# OPUS_REVIEW_REQUEST_01(条件A=新しい処理の設計。1ページ。依頼先=Fable経由のOpus独立レビュー)

目的: 日本語ASRで「正常音声が文字の選び方の違いだけでNG→再生成/HR」になる問題への対策設計(`DESIGN_01.md`案A+案B-light)の独立検証。根拠=`ROOT_CAUSE_01.md`。

## レビュー論点
1. **誤PASSリスク**: 案Aの“値atom化+残り発音一致”(厳格、濁点許容・候補総当たり・LLMなし)が、どの真の誤発音を通しうるか。想定外の通過経路(形態素解析の誤分割で別語が同読み、助詞境界、`へ/え`、数詞の不規則読み`三日=みっか/さんにち`)。`DESIGN_01.md`の誤PASS表は網羅か。Phase 3の負例設計(N-1≧120/N-2/N-3 16)で足りるか。
2. **数値保護の整合**: 値ガードEQUAL/NO_VALUESのみ通す設計が、承認済みP1(`CURRENT_SPEC.md` L2852)・`_numeric_value_equivalence`・中核数値v4/J2(Writer段)と矛盾しないか。特に(a)Secondaryにも値等価を適用する是正(仕様L2865と実装のずれ)、(b)桁区切り3桁限定のstrip、(c)範囲値`42から46メートル`(値ガードUNKNOWN)の扱いを今回含めない判断。
3. **案B-light(JA P1の見直し)**: 「Primaryだけが値DIFF、Azureが原稿と値・発音一致」でPASS_WITH_WARNINGにする設計の誤PASS確率。独立2エンジンの支持を条件にする点は十分か。ローカルWhisperを第3票にするか(UDR #136との関係)。KP英語3-ASR投票(KP3V)との整合・再利用。
4. **別方式**: (a)JAのPrimary/Secondary入替(Azure primary)、(b)位取り断片の復号、(c)OpenAI以外の数詞整形に強いモデル、(d)canonical側で読みを決めて照合(辞書読み)など、より安全・安価な方法があるか。特に実測の根拠(Azure救済24件は全て原稿同一表層)が選択バイアスを含む点。
5. **既存機構との整合**: retry/fallback/HR(通算3回)、A4同形異音・A7登録読み除外の維持、X/Z限定配線(`er109_xz_scope_01`型)か全JA共通か、旧検査の整理方針。
6. **Phase 3の合格基準**(`PREREGISTERED_CRITERIA_01.md`)の妥当性: 誤PASS0/136の統計的意味、推定正例の扱い、“基準緩和禁止”の運用。

## 提示物
`ROOT_CAUSE_01.md`/`DESIGN_01.md`/`EXISTING_SPEC_CHECK_01.md`/`PREREGISTERED_CRITERIA_01.md`、プロトタイプ`proto_reading_compare_01.py`、再現`trace_moon_classify_01.out.txt`/`adversarial_panel_01.out.txt`/`marginal_flip_eval_01.out.txt`/`mock_secondary_gap_01.out.txt`、Whisper参考`whisper_local_3wav_01.json`。
## 期待する出力
必須修正/推奨修正/不要の3区分。誤PASSを増やす経路があれば具体的な反例文(canonical, ASR転写)で。
