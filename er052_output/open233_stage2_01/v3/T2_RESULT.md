# T2_RESULT(OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_03、2026-10-08)
位置づけ: Trial/検証(DEV)。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、SSOT未編集、git未実施。②(`OPEN233_STAGE2_READER_BELIEF`)はOFFのまま。
事前登録: `docs/pm/checker_action_policy_01/preregistration_T2.md`(2026-10-08 00:42、replay前。ライン不変で適用)。
証跡: 本ディレクトリ `runs/`(21試行JSON)、`eval_v3.json`、`logs/replay.log`・`logs/eval.txt`、`entity_class_cache/`、`cost_v3.json`、再現スクリプト `rewrite_v3.py`・`eval_v3.py`。

## 1. 結論(機械適用): PASS(6ライン全て)
| ライン | 結果 | 判定 |
|---|---|---|
| 1 規則違反0件 | 受理20件をv3規則で独立再監査(`eval_v3.py`)=違反0。目視でも主体・極性・数値の違反変化なし | PASS |
| 2 構造要素由来STOP≤1/21 | **1件**(t3 rep0: in_one_lineの限定語直しが**極性照合**で6回却下=段階2のv2でも同じ対象・同じ理由でSTOP) | PASS |
| 3 盲点2種の解消 | 単体fixtureで却下(`The AI makes the call.→The human makes the call.`=class_cross:human、`# I Followed...→# AI Phone Agent Test Put Humans on the Line`=frame[i]消失)。実replayの受理20件に再発**0**(t6 hook 3/3が`The AI sometimes makes the call.`、t5 title 3/3が`I`枠を保持) | PASS |
| 4 AI→Muse型の誤却下0 | 単体fixtureで許可。実replay: t2 hook(`If you ask AI...`→`If you ask Muse...`)3/3受理、AI→Museで却下された試行は0。**境界例(定義外)**: t4 hookで`Japan→Matsuyama`が`unregistered_entity:matsuyama`で却下(2/3試行、再生成で回復)。Matsuyamaは台帳(日本語)に英字で登録されておらず、元にJapan(固有名詞)があるため「一般名詞→台帳登録の具体例」の定義に当たらない | PASS(注あり) |
| 5 削除文0 | 0(Hook最終手段削除の発動も0) | PASS |
| 6 費用≤¥25 | **¥17.75**(Rewrite+再生成+Recheck+型付けLLM ¥0.51[台帳4件]) | PASS |

## 2. v2(段階2保存値)との比較(同じ7対象×3反復=21試行)
同じv3規則で監査(v2出力はv3の観点では再監査のみ。APIはv3のみ実行)。
| 指標 | v2(段階2、規則=1) | v3(規則=2) |
|---|---|---|
| 受理 / STOP(ladder枯渇) | 14 / 7 | **20 / 1** |
| v3規則での違反(受理出力) | 4(t5 rep0 一人称枠消失、t6 rep0・rep2 `The human makes the call.`、t6 rep1 `The AI or sometimes a human...`) | **0** |
| 削除文 | 0 | 0 |
| Recheck(受理後): COMPLIANT / DEVIATION | 3 / 11 | 5 / 15 |
| 再生成call | 22 | 14 |
| 費用(21試行) | ¥11.67(型付け無し) | ¥17.75 |
STOPが7→1に減った主因: v2はAI→Museの具体化(t2 hook 3/3、t3 rep2、t5 rep1・rep2)を主体部分集合で却下していた。v3は台帳登録の具体例を許可し、盲点2種は却下する。

## 3. Checker由来の新規NG(目視、受理20件)
- 主体・極性・数値の逸脱なし。表現の変化は限定語の言い換え(`without proper disclosure`/`adequately telling users`、極性は不変)、限定の追加(`in some areas`、`sometimes`)、`Japan`の削除(部分集合)、Museへの具体化(t2 3/3、台帳にMuseあり)。
- 注意すべき変化: t2 rep1 `it may hand some calls over to trained human agents during testing`(台帳の人間契約スタッフ=意味は近いが語は`agents`)。t5 rep0 `I Read About ...`(`Followed`→`Read`。枠は保持、行為の語が変わる)。t2 rep0/rep2 `someone/a person talks`(元の`it`から不定代名詞へ。台帳の「一部は人間」と整合、v3の辞書・代名詞照合は`someone`を捕捉しない=規則上の穴)。
- Recheck(受理後)DEVIATION 15件の内訳(目視): 同記事の他の要素(`# An Unexpected Helper...: A Human`等の見出し、`The AI makes the call.`が残る隣接Hook)への再検出が大半。t5はタイトルの`I Followed`(語り手の枠)を`Ledgerにない書き手の行為`として毎回DEVIATIONとする=②/M2が無効のため、枠を守ると再検出されるトレードオフ。t6 rep0・rep1は`The AI sometimes makes the call.`が決定論の極性検査で`negation_polarity_mismatch`として戻された(Recheck側の既存検査)。

## 4. 実装要点(`OPEN233_STRUCTURAL_REWRITE_RULES`: 0=OFF、1=v2のまま、2=v3)
- 役割クラス: human/ai/org/public/other。一般名詞は小辞書(`_ROLE_WORDS`)、台帳実体は語彙(`proper_noun_vocab`)を台帳ごとに1回だけLLM型付け(`entity_class_cache/<ledger_sha>.json`、失敗時は辞書のみ=未登録の固有名詞は却下のfail-closed)。
- 照合1(v3): 出力の一般名詞クラス⊆元のクラス、新規の固有名詞は台帳登録済み**かつ**そのクラスが元にあるときだけ許可、辞書に無い一般名詞(主語スロットの近似検出)・新規代名詞は却下。ハイフン複合語は構成語で見る。
- 照合1b: タイトル・Hookは元のI/you/we等の代名詞・`?`が出力に残ること。2〜4(極性・数値・形式)はv2と同じ。
- 再生成1回(v3専用の指示文)→不通過ならそのlevelは却下→ladder全levelで尽きれば元のまま+`kept_original_quality_record`+既存の構造要素STOP経路(BLOCKING未修正の新しい出口は無し=M4)。level 6(全文書換え)も同じv3照合。
- テスト: 新規29件(`er052_open233_checker_action_policy_stage2_v3_test_01.py`)。`er052_open233*test*`全体**1071件PASS**(着手前1042+29)。②はコード不変・スイッチOFF。

## 5. 限界・Fable判断が要る点
1. N小(7対象×3反復)で有意差は主張しない。replayは保存済みStage1指摘を固定したcycle1の書換えのみ(cycle連鎖は未再現)。
2. 「辞書に無い一般名詞の新規導入」は構文解析ではなく近似(文頭の限定詞直後の名詞/文頭の複数形)。従属節内の主語(`someone`等の不定代名詞、`it→someone`)は捕捉しない。小辞書に無い役割語(例: `volunteers`は辞書にあるが`crowd`は辞書外)は未知名詞として却下側。
3. 台帳(日本語)に英字で登録されない固有名詞(`Matsuyama`)は未登録扱いで却下される(再生成で回復したが、台帳の日本語実体名→英字表記の写像が無い)。同クラス内の別固有名詞への置換(Meta→Reuters型、同じorg)は許可される(クラス比較の設計上の許容)。
4. LLM型付けの誤りは規則の精度に直結する(例: `reuters`=other、`united`/`states`=org)。キャッシュ後は決定論だが、型誤りは固定される。
5. 極性照合(v2から不変)がin_one_lineの限定語直し(`without clearly telling users`→`without proper disclosure`)を却下して残るSTOP(t3 rep0)は、v3の対象外の既存規則の挙動。
6. 語り枠を守るとRecheck側(M2無効)がタイトルを再検出する。②を打ち止めにしたまま解消する手段は本委任の範囲外。
7. 面白さの非劣性は未確認(ユーザー盲検読み比べが必要)。Production採用判断はしていない。
