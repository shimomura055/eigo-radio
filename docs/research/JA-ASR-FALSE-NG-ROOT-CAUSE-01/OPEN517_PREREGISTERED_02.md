# OPEN517_PREREGISTERED_02(OPEN-517是正案 v4 の事前登録。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06、2026-10-25)
前版=`OPEN517_PREREGISTERED_01.md`(§0〜§6、F2 v1〜v3。凍結・変更なし)。本書はOpus条件Cレビュー(`OPUS_REVIEW_01_OPEN517.md`)の必須M-1〜M-5・R-1を反映して**F2定義をv4へ更新し、基準7〜9を追加**する。基準1〜6は変更・緩和なし(基準3は下記のとおり追加で厳格化)。
## 0. 凍結(評価script実行より前に固定)
- `proto_value_gate_fix_04.py` sha256 `19aea160aa4bb4b45ec4e8094cc7eac5c58a9bfc8e3bd866208dd75fc4fa4dfa`、`proto_value_gate_fix_04_test_01.py` sha256 `b7dbcbcf12a9447f208193b8ca04cc438da9b10d66b31a35445b0304eb0b7ef6`(19 test PASS。**§4の改訂1回後の最終凍結**。初版sha `bc53efe5…`/`11a60868…`は§4参照)。補助スイープ`sweep_open517_04.py` sha `d0864cd2…`、評価`eval_open517_api0_04.py` sha `b49a0eaa…`、収集`collect_unknown_pool_02.py` sha `e234e6cd…`、`unknown_pool_02.json` sha `21d1baf3…`(収集時点で固定、評価で変更なし)。v1〜v3 protoは変更なし(v3 sha `00c8c133…631`)。
- 評価データ=(i)既存771件(`open517_api0_eval_03.out.json`のrows。N1 151・P4 421・N3 30系・月題・正例対照47・P3 NG pool)、(ii)**未知データ**(R-1)=上記771件の(canon,Primary転写)キーに含まれない保存済みJA転写。列挙は`collect_unknown_pool_02.py`のみで機械的に行う(S1=tts_generation_results*.json attempts_log、S2=attempts/*.json、S3=human_review_queue.jsonlのopenai_asr step、S4=docs/research・er*_output配下のjson(l)で`canonical系`+`asr_text系`キーを持つ日本語record)。**件数は選別せず全件**。件数・内訳はEVAL_02に記載(選別・後出しの除外はしない)。新規ASR/TTS/LLM 0=有料API 0・実費0円(socket guard)。
- Production file(`er078_*`/`er007_*`/`er066_*`)は無変更(`git status`で確認)。
## 1. F2 v4 の定義(評価対象。v3との差分のみ)
- V4-1(M-2a): 期待読みから`WEAK_KANA_NUMERALS`(なのか/ようか/とお)の読みを除外。同unit内で値が一意でない読みも除外。
- V4-2(M-2b): かな統一の対象は、F2前のguardで『相手atomが未対応(drop)または別のかな数詞atomと誤対応していた』ものに限る。統一後に『F2前の非EQUAL pair(置換に対応するpairを除く)』が同じ(src,hyp,verdict)で全て残らなければ、F2前の結果を採用(whole fallback)。
- V4-3(M-3): 一致したかな列が同一unitのより大きい数詞の読みの一部(直前/直後8文字までの連結が別値の読み、または直後が拗音小字)なら置換しない。
- V4-4(M-4): F2は明示引数`kana_unify=True`のときだけ。READING_MATCH PASSのPrimary最終ゲートのみ。`negation_diff`は置換前の元テキスト。Primary NG(P1)とSecondary gateではF2無効。
- F1・警告保全(V3-1)はv3と同一。
## 2. 追加する合格基準(基準1〜6は`OPEN517_PREREGISTERED_01.md`§3のまま。緩和禁止・厳格化可)
7. **合成負例一式=全件PASS以外**(M-5): `proto_value_gate_fix_04_test_01.py`の`M2_NEG`(弱い読み5件。うち3件はv3で実際にPASSした反例)・`M3_NEG`(長いかな数詞の前半/後半: 10人↔さんじゅうにん、百円↔にひゃくえん、十代↔にじゅうだい、2時↔にじゅうじ、他4件)・`SOKU_NEG`(誤った音便/連濁: さんほん/さんふん/はちほん他5件)・`TWIN_NEG`(同値atom並び4件)・`NEGATION_NEG`(否定語近接3件)が全てNG_PROTECTEDまたはDEMOTE_P3、かつ正例(さんぼん・みっかかん等)はPASS。さらにF2無効の固定(`negation_diff`の元テキスト判定・Primary NG 6件不変・monotonic guardを他層無効化でも作動)。**1件でもPASSなら不合格**。
   - 注記(F2無関与の既存の穴): 原稿`4日`↔転写`にじゅうよっか`/`さんじゅうよっか`は、Production `KANA_NUMERALS`正規表現に語境界がなく『よっか』を4日atomと拾うため、**F2前から**EQUAL(現行Productionも同じ)。F2は発動せずF2前の結果と同一(悪化させない)ことのみをtestで固定し、F1/F2の是正対象外として別OPEN候補にする(`OPEN517_APPLY_PLAN_01.md` §7)。
8. **未知データ**(R-1): 未知データ集合に`apply_in_process()`(F1+F2 v4)をjudge全経路で適用し、現行との判定変化を**全件**表にして1件ずつ目視確認する。合格=(a)変化は『READING_MATCH PASS→NG_PROTECTED/DEMOTE(F1)』『PASS→PASS_WITH_WARNING(F2警告追加)』のみ、(b) F1由来の変化は**全件が値/否定の真の差**(値が実際に異なる、または原稿数値が転写から脱落)であること(値が同一の正常転写の誤NG=不合格)、(c) NG→PASS=0・非READING_MATCH PASSの変化=0・警告喪失=0。未知データでの判定変化が0件のときは『未知データでの反証機会が無かった』と明記し、合格の根拠を既存771件側に限定する(未知データが十分であるとは書かない)。
9. **F2発動の全件一覧と値同一確認**: 既存771件+未知データのF2発動(`fired=True`)全件を一覧し(原稿・転写・置換したかな列・partner atom・F2前/後のguard)、(a)置換後のpartner atom表層が置換前のpartner atomと同一であること、(b)置換したかな列が`_cands`逆引き(unit内、n=1..20000)で**当該値にのみ**対応すること、(c)F2後の対象pairがEQUALであること、を機械確認し、全件を目視する。正常143件(P4 READING_MATCH PASS 133+正例10)のうちF2発動件数を報告。monotonic guardによるF2前結果への巻戻し(fallback)件数も報告。
10. **開示(基準ではない)**: (i)`一分↔いちふん`のDEMOTEはSecondary(Azure)stub結果であり、実運用の最終結果はAzure転写次第(PASSならPASS_WITH_WARNING、NGならNG_BOTH)。評価の`NG_SECONDARY_UNAVAILABLE`表示はstubによる。(ii)v3→v4の差分表(既存771件)を提示する。(iii)v1〜v4は同一既存コーパスで不合格を見て再設計した履歴(汎化は未知データで検証。未知データは基準8)。
## 3. 事前登録写像
- 基準1〜5・7〜9を全て満たす → 「是正案F1+F2 v4=API 0検証PASS」。Production適用はFable判断+ユーザー報告後(本委任はProduction変更0)。
- 基準7が1件でも不合格 → v4のF2規則を再設計(差分を本書に追記・再凍結)。
- 基準8(b)で値同一の正常転写の誤NGが出たら不合格。F2の対象拡大/変更を追記して再凍結。
- 到達上限=DEV/proto検証。
## 4. 改訂記録(評価結果の判定前に行った、v4初版の欠陥修正。基準1〜10は変更・緩和なし)
- 経緯: v4初版(proto sha `bc53efe5…`、test 18件PASS)で`eval_open517_api0_04.py`を実行(13件変化=v3と同一、未知データ変化0、F2発動7件)。その後、実コーパスにかな数詞が乏しいため補助として**系統スイープ**(`sweep_open517_04.py`: 助数詞29種×値46個×正誤読み×向き、約1.5万ケース)を追加実行したところ、v4初版に1件の欠陥を検出: 原稿`5日間`↔転写`いつかかん`が誤NG(`いつか`=曖昧かな数詞atom[kind=amb]は吸収対象外にしていたため。v3はPASS)。
- 修正=V4-5: 置換候補が内包する既存atomの吸収対象を`kind in (num, amb)`へ拡張(v3と同等)。1語の変更。testに`test_ambiguous_kana_numeral_absorbed`を追加(19件)。修正後に**全評価(771+未知493)・スイープを再実行**し、これを最終結果とする(初版結果は13件変化・F2発動7件で同一。差は上記1ケースのみ)。基準は評価結果を見ての緩和ではない(厳格化方向の修正のみ)。
- スイープは基準ではなく**開示**(誤PASSは既存の弱いかな数詞UNKNOWN素通し[F2無関与・v3/現行と同数]のみで、F2起因の誤PASSは0であることを確認する目的)。
