# B_LIGHT_DESIGN_02(②B-light 設計改訂。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08、2026-10-25。設計のみ・API 0・Production変更0・未配線)
`B_LIGHT_DESIGN_01.md`(案β本体・観点7点・候補比較・フック3点・UDR #136整合)は**変更しない**。本書はOpus条件Aレビュー(`OPUS_REVIEW_01_BLIGHT.md`)のM-1〜M-3・R-1〜R-8の反映分だけを書く。proto=`b_light_proto_02.py`(sha256 `d041b1ca439a878f88b85dd1e590c8371569c740e01e663b6fcaa6c542c1aead`、v1は`5b715f8e…`で凍結・無変更)、test=`b_light_proto_02_test_01.py`(100 passed)、事前登録=`B_LIGHT_PREREGISTERED_02.md`、結果=`B_LIGHT_EVAL_02.md`。

## 1. 採用承認の対象範囲(M-1。要約で狭めない)
**βのProduction採用を承認するとは、次の3つ全部を承認することである。**
1. 新受理クラス `JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE`(PASS_WITH_WARNING)の追加(CURRENT_SPEC L2179/L2856のJA Secondary受理=EXACT/NORMALIZEDのみ、への例外)。
2. **v2の読み規則の採用**(`proto_reading_compare_02.pron_hira`=助詞『は→わ』『へ→え』のみの発音一致、`c2_blocked`=同形異音の阻止)。βは読み判定にこれを使う。base+F1F2(=07A後Production)のPrimary層はこの同音異字(例`月の氏は`/`月の死は`=`しわ`)を受理しないため、**βを採用することは、Secondary値の裏付けがある範囲に限って、Primary読みの受理範囲をv2相当まで広げること**と同じである(`B_LIGHT_EVAL_02.md`: 月題の増分4件のうち3件がこの規則に依存、1件のみProduction既存の読みクラス[PHONETIC_MATCH]で成立)。
3. 試聴必須の運用(下記§4): composite受理は全て事後試聴リストに載り、garble説明・Secondary読み食い違い・発音等価のいずれかがある場合は『試聴必須』扱い。
v2読み規則に依存しない縮小版を望む場合は、読み規則を『Production既存の読みクラス(EXACT/NORMALIZED/PHONETIC_MATCH)のみ』にする別案(月題の増分は4→1件)を、Fableの指示で別protoとして凍結・評価する(本委任では未実施。proto v2の`reading_rule="strict"`は`normalize_ja`完全一致のみで、さらに狭い参考列)。
列の定義(M-1是正): 評価の比較基準は『base+F1F2』(v2のPrimary層・A4(a)を含まない)。旧v1評価の『+F』『+B』は参考列(`v2F12`/`v2F12B`)に降格。v1の数字(F後3→β5、増分+2)は**Productionにない基準**だったため、以後引用しない。

## 2. 再利用時の隔離(M-2。配線は別委任・本委任は設計+protoの純関数のみ)
問題: `er078_reuse_value_guard_01.py:104-114`は保護差でないNG再判定では再利用を止めない。composite受理音声はPrimary単独の再判定ではNG(例`final_gate_value_diff`)になるが保護差ではないため、**flag OFF時やA/B/C(Master Audio Store共有)へ再利用で漏れる**。
設計(er109/RET/UKUS前例`er078_reuse_value_guard_01.py:62-80`と同形):
1. **寄与印**: `composite_contributed(aj)` = `asr_judgement`/`asr_judgement_inherited`の**両方**に対し、ラベル`JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE`・警告`JA_COMPOSITE_*`・auditキー`composite_contributed`のいずれかがあれば真(fail-closed。印のないentryには作用しない)。
2. **先にblock**(再判定より前、`kp_vote_gate_follows`早期returnより前): 寄与印あり ∧(flag OFF ∨ scope∉{X,Y,Z})→ `COMPOSITE_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF`で再利用しない(再生成へ回る。flag OFF rollback時は再生成費用が出る=既存前例と同じ)。
3. **scope内**: 保存entryの`asr_judgement.composite`(audit)から**保存S転写・engine・wav sha256・Primary転写・原稿**を取り出し`composite_judge`を再実行(API 0・Azure新規呼出0)。NGなら**保護差でなくてもblock**(`COMPOSITE_REJUDGE_NG`。UKUS/RETと同じ『境界を厳しくした後に古い受理を黙って通さない』)。
4. **fail-closed**: 保存S転写・engine・wav shaのいずれかが無い、または`composite`auditが壊れている → block(`COMPOSITE_PROVENANCE_MISSING`)。`composite_judge`自体も`secondary_meta`(engine・wav_sha256)が無ければ`secondary_provenance_missing`でNG。**S転写・engine・model_id・wav shaの保存を配線の前提条件**とする(`R5_MEASUREMENT_SPEC_01.md`)。
5. proto実装=`composite_contributed`/`composite_reuse_decision`(純関数)+test7件(scope外A/B/C/None・flag OFF・scope内再判定・provenance欠落各キー・再判定NG・非composite不干渉・inherited)。**配線時の追加test**: 実`reuse_check`が上記順序で呼ぶこと(静的test)、A/B/Cの`is_active_for_run()`相当がFalseであること、`APPROVED_EQUIVALENCE_BASES`に入れないこと。

## 3. 複数atom(M-3)
- 実測: `value_guard`(Production)は**位置照合**(順序入替でDIFF、個数過不足でDIFF、同助数詞反復も位置で対応)。set照合ではない(`test_value_guard_is_positional_not_set_based`、`eval`§F)。
- それでも**二重化**: protoは原稿・Secondaryの値atom列(値・単位)を位置・個数・順序で比較し、不一致は`secondary_atom_sequence_mismatch`(protected)。Primary側はatomごとに助数詞直前のrunを**カーソル前進**で照合(同助数詞反復でも各atomを別runに対応づける)。Primaryの余剰数値・順序入替・欠落は、値atom除去後の残りの読み比較でNG(`primary_reading`)またはMISSING。
- 負例(基準を緩めず追加): 1個目EXPLAINED+2個目矛盾・逆・断片和不一致・Secondary順序入替/値不足/値過剰/重複/2個目値違い・Primary順序入替/余剰数値/2個目欠落・同助数詞反復(2個目/1個目garble誤り・Primary欠落・Secondary不足・値違い)=**17件**が全てNG。正例: 両EXPLAINED・EXPLAINED+EQUAL・反復の両garbleは`PASS_WITH_WARNING`+試聴必須。

## 4. Secondary読み食い違い・garble説明の扱い(R-1/R-2)
- R-1: Secondaryの『値atomを除いた残り』を`normalize_ja`し、原稿残りと(完全一致でも`pron_hira`一致でもなく)食い違うとき(a3『杉野氏』型)は警告`JA_COMPOSITE_SECONDARY_READING_CONFLICT`+`JA_COMPOSITE_LISTEN_REQUIRED`。**既定=警告+試聴必須**、`secondary_reading_conflict="veto"`でNG。月題の増分はwarn=4件、veto=1件(a2保存転写のみ)。**vetoにすると効果の大半が消える**ため、既定warnは『Primary読みを正とし、Secondary読みを使わない』(2026-10-11条件)と整合する一方、試聴必須の運用負荷が増す。どちらにするかは採用承認時のユーザー判断材料(§11)。
- R-2: 断片説明(`JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED`)は`JA_COMPOSITE_LISTEN_REQUIRED`を付ける(TTSが数字の途中で不自然な間を入れた可能性。値が正しくても音の品質問題が残りうる)。
- `JA_PRON_EQUIVALENT`(v2発音等価)も試聴必須理由に含める。全て無い(Primary値EQUAL・読み完全一致・Secondary読み一致)なら試聴必須なし(composite PASS_WITH_WARNINGの基本警告`JA_COMPOSITE_VALUE_FROM_SECONDARY`のみ)。
- 『試聴必須』の運用実体=既存の事後試聴リスト再導出(HR/attempt/fallbackは不変)に、必須フラグを付けて載せる(配線時の仕様。新しいGateは作らない)。

## 5. F-Aの観測形限定(R-3)
断片説明は**観測形のみ**: 数字のみrunは**2断片**で前断片が`[1-9]0+`(`8000`のようなd×10^k)・後断片は先頭0なし・総和==原稿値・位取りが重ならない。F-B(数字+漢数字)も前断片は同形。**3断片は実例が出るまで無効**。`12000|300`・`100|200|300`・`80|九百`は説明不成立(test`test_explain_garble_boundaries_r3`)。観測形=月題の`8000900`/`8000九百`のみ。新しい観測形が現れたら実音声証跡とともに追加(事前登録を更新)。

## 6. Secondary値atomの表記限定(R-4)
Secondary値ガードの既知不具合(OPEN-523/524)を引き継がないため、composite条件を追加: **原稿・Secondaryの全値atomが『数字・漢数字表記+助数詞』**(`num`種別、助数詞あり、接頭がASCII/漢数字のみ)。かな数詞(`さんびき`/`みっつ`)・あいまい語(`十分`/`一月`)・分数・単位なしはNG(`R4_atom_notation`、Secondary側は保護扱い)。OPEN-523/524を先に直す案は採らない(別件)。

## 7. 監査記録(R-7)
`composite_judge`成立時の`audit`: `composite_contributed=true`, `reading_source="primary"`, `value_source="secondary"`, `reading_rule`(v2/strict)、`explained_spans`(原稿atom・Primary run・断片内訳)、`secondary_reading_conflict`、`secondary_engine`、`secondary_wav_sha256`、`secondary_model_id`、`secondary_transcript`、`primary_transcript`、`canonical_text`、`atom_count`、`allow_explained_garble`。配線時は`asr_judgement.composite`に格納(§2の再利用判定が読む)。

## 8. フック①事前判定の流用禁止(R-8)
フック①(P1緩和)の事前判定は`precheck_composite(canon, primary)`(S:=原稿)。戻り型は`PrecheckResult(may_call_secondary, why, blocked_by)`で**`.equal`/`.label`/`.warnings`/`.audit`を持たない**ため最終判定の代用にできない。`composite_judge`は`secondary_meta.precheck=True`を拒否(`precheck_not_final`)し、meta欠落はfail-closed。事前判定が真でも実Secondaryの値が違えば最終NG(test`test_r8_precheck_true_but_actual_secondary_wrong_is_still_ng`)。**配線test(固定項目)**: (a)P1緩和で事前判定が真→P3へ進むだけで`state`/`label`/`warnings`に事前判定結果を書かない (b)Azure呼出失敗・空転写・値違いでは従来どおり`NG_PROTECTED`(`p1_value_diff`)へ戻る (c)事前判定の真偽がattempt消費・retry・HR Lockに影響しない。

## 9. 別件: CURRENT_SPEC L2865と実装の不一致(R-6)
仕様L2865は『Secondary受理に値等価正規化後の一致を含む』と書くが、実装の`_secondary_accept`(`er007_ja_secondary_asr_01.py:643-650`)に値等価層が無い(R4)。**これはβ承認に混ぜない**(承認済み仕様からの乖離=不具合[11-8]として別に扱う。OPEN-515に既記、分類=修正へ進む)。βの採用可否はL2865の是正とは独立に判断する。

## 10. Opus C-1〜C-7の確認(承認所見への対応)
C-1 独立性(Azureはフレーズリスト不使用で台本と独立)=維持。C-2 最終ANDゲート常時=本関数はPASS候補を返すだけ、`APPROVED_EQUIVALENCE_BASES`に入れない。C-3 矛盾型NG維持=§3・EVAL_02。C-4 ε/F1側救済/F2拡張の却下=維持(γ・δも時期尚早/設計要件外)。C-5 UDR #136非接触・新受理クラスはL2179/L2856の変更=ユーザー採用承認=§1。C-6 HR/attempt/fallback不変=変更なし。C-7 決定性=2回実行で出力一致。

## 11. ユーザー確認事項(Fableが提示する場合の文言材料)
βのProduction採用承認は、§1の3点(新受理クラス・v2読み規則・試聴必須運用)を**含む**ことを明示して求める。選択肢: (i)v2読み規則を含むβ(月題増分4/12)、(ii)Secondary読み食い違いをvetoにするβ(増分1/12・試聴負荷小)、(iii)Production既存の読みクラスのみのβ-lite(別proto・増分は約1/12)、(iv)採用せず低優先候補として保持(R-5実測後に再判断)。推奨はEVAL_02の効果の狭さとOpus所見(iii)に沿い(iv)。
