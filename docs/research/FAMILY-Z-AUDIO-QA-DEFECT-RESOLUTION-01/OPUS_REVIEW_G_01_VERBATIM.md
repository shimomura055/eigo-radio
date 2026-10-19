## Opusレビュー_G(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01、条件A、read-only)

### 総合判定: **GO_WITH_CHANGES**(ただしP1は承認済み仕様の範囲外。ユーザー承認が前提)

P1の技術的な方向は妥当です。音声が同じでもASRの綴りの出方だけで合否が変わる、という問題を一般化した形で解消できます。ただし次の2点から、「既存仕様の整合回復」としてFable判断で実装することはできません。
- CURRENT_SPEC L2798「benign吸収は不受理」(承認済み仕様の本文)と、採用済みBLOCKERであるOF-178(`OPUS_FINDINGS_LEDGER.md:205`)を正面から改訂する変更です。
- 2026-10-13の設計原則§6は「受理を広げるか、厳格化するか」の最終選択をユーザー判断として留保しています(`docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md` L101-104)。

**Fable向けの事実訂正**: 依頼文の「`Melo`はPattern A(`er011:152-168`)で自動PASS」は、`drank`の文脈では誤りです。`Melo drank`がPASSする経路はPattern Aではありません。`protected_check`の`_is_benign_plural_pair`による吸収(`er006_preprod_hardening_01_validation.py:690-696`、固有名詞かどうかに関係なく適用)と、`HIGH_SIMILARITY_SAFE`(L1148、閾値0.98)の組合せです。この経路は**警告なしのPASS**になります(`_PRIMARY_WARNING_BY_CLASSIFICATION`に含まれない、`er006_secondary_asr_01.py:627`)。Sonnet報告§0.2の記載は正しく、依頼文の要約側が混同しています。このため、ユーザーに求める判断はOPEN-330(Pattern Aの受理範囲)とは別の論点になります(末尾参照)。

---

### 論点1: P1の整合性
- **結論**: 2026-10-13原則の「同じ現象には同じ判定」には合致します。一方で、OF-178が意図的に塞いだ受理面を、意図的に再び開く変更です。整合回復ではなく、仕様改訂にあたります。
- **根拠**:
  - OF-178の趣旨は「M1がF1より緩い受理面を作らない」ことです(`er006_m1_multi_candidate_01.py:12-14,407-422`)。`forms_from`は`drop_final_S_or_Z`を文脈に関係なく作ります(L300-301)。そのためbenign吸収を認めると、M1は「音声に語末sが無い」ことを歯擦音の連続による根拠なしに受理してしまいます。
  - 2026-10-13原則が受理の根拠にしているのは連結発音(s+sの融合、原則文L124「現行許容の理由」)です。`Melos drank`には融合の根拠がありません。現在`Melo drank`が通るのは、もともと普通名詞の単複の揺れを想定した規則が、固有名詞の語幹末sにも当たっている副作用です。
  - したがってP1は、その副作用の及ぶ範囲を「ASRがcanonicalからsを除いた綴り(Melo)をそのまま出した場合」から「その綴りのCMU同音綴り(Mello/Mellow)を出した場合」へ広げます。
  - 誤受理の**種類**は増えません。同じ音声に対する判定がASRの綴りに左右されなくなるだけです。ただし、本当に語末sが落ちた音声を受理する**確率**は上がります。
- **HIGH_SIMILARITY_SAFEの文長依存**: P1は`asr2`(置換後の文)で一致率を再計算するため、現行の`Melo`の判定と同じ結果になります。悪化はしません。1文字脱落の場合、正規化後でおよそ26文字以上ならPASSします。それより短い文(例: `Melos left.`)はP1でも不受理のままです。これは既存の不整合で、P1の欠陥ではありません。
- **必須修正**:
  - (M1-a) 受理条件を「should_passなら何でも可」にしないこと。exact以外の置換はすべて「`f1_explained`に含まれる」か「`_is_benign_plural_pair(canonical_word, to)`が真で、かつ`classify(canonical, asr2).should_pass`」のどちらかに限定してください。これで新たに開く受理面がbenign経路だけであることを、コード上で明示できます。
  - (M1-b) audit記録に受理経路を残すこと(例: `acceptance_path="benign_plural_homophone"`)。OF-187の集計で、新しい受理面だけを分けて追跡できるようにします。
  - (M1-c) 文長依存を補う目的で、一致率条件を迂回しないこと(迂回するとP1が現行の判定より広くなります)。
- **任意改善**: 現行の固有名詞benign PASS(警告なし)にも警告を付けて試聴リストへ載せると、確認の網羅性も揃います。ただし既存経路の挙動変更になるため、別の判断事項です。

### 論点2: OPEN-330との関係
- **結論**: P1が前提にしているのは、OPEN-330(Pattern Aの範囲)ではなく、**benign単複吸収を固有名詞の語幹末s・歯擦音が続かない文脈にも適用してよいか**という未記載の論点です。推奨は、(a)を確定したうえでP1を条件付きで採用することです。
- **根拠**:
  - 歯擦音文脈の(a)は、2026-10-13のユーザー合意(`Melos said`→`Melo said`の許容を維持)で実質的に支持済みです。
  - (b)はその合意と衝突します。`Melo said`まで不受理になり、HRが増えます。
  - 実測では、5本の音声すべてに無声・非周期の歯擦音らしい区間(105〜125ms)がありました。同じwavでもOpenAIは呼ぶたびに`Melo`/`Mello`と揺れ、Azureは録音ごとに決まった綴りを返します。つまり、s脱落は**ASRの誤転写が支配的**と考えられます(音響指標は診断用)。
  - `Jones`←`Joan`型の別実在語の誤受理は、P1では「sを除いた綴りがCMUに収録されている場合」に限って起こります。`Hayes`←`Hey`型は、`_singularize_simple`がbenignと判定しないため(`validation.py:634-642`)、P1でも残差扱いで不受理です。
  - 一方、`Rhodes`←`Road`/`Rode`型(`rhode`がCMUに収録されていれば)は受理されます。
- **組合せの形**:
  - (a)+P1(推奨)
  - (c')=P1の新しい経路を「Ledgerに登録済みの語(C2由来の候補)」に限定する。作品単位の人間承認に近い、より狭い形です。ただし現状のLedgerは自動登録と人手登録を区別できず(OPEN-339)、厳密な(c)にはなりません。
  - (b)とP1を組み合わせると、benign経路そのものを固有名詞では閉じることになり、P1は不要になります(非推奨)。
- **必須修正**: 実装前に、**辞書レベルの上限census**(API 0)を取ること。対象は、CMU収録のs終わり固有名詞と一般語の全件で、P1で新たに受理される(c, w)ペアの一覧です。Sonnetのcensus(E21実データ、新規受理1ペア)はMelosに偏った実データで、受理面の上限を示していません。OPEN-330の旧集計(54語中17語、38綴り)はP1とは条件が異なります。

### 論点3: 誤受理の境界
- **結論**: 一般化して記述できます。独立証拠の追加は不要で、PASS_WITH_WARNINGと試聴リストで足ります。
- **新たに受理される集合**(次の4条件をすべて満たす場合):
  1. M1の入口条件(UNCERTAIN・保護差なし・F1残差が内容語でない)は不変。
  2. ASR語`w`がCMUに収録されている。
  3. `w`が、canonical語`c`の期待綴り`s`(`expected_spellings`、CMU収録)とCMU上で同音である。
  4. その音素列が、ASRに依存しないcanonical側の凍結候補のdrop/add_s形と一致し、`w`→`s`に置換した文がF1残差0、かつ`(c, s)`がbenignの単複対で既存判定でshould_pass。

  言い換えると「既存の判定がこの文で受理している綴りの、CMU同音綴り」です。add_s方向(例: `Mark`←`Marx`)も含まれます。
- **独立証拠を不要とする理由**: 現行の`Melo drank`は独立証拠なし・警告なしでPASSしています。新しい綴りにだけSecondaryとの一致を課すと、原則文L125の「新表記のみ別基準にしない」に反します。canonical側の候補への音素一致はP1でも維持されるので、ASRに依存しない根拠は残ります。
- **必須Regression**(記事非依存。偽のCMU辞書とLedgerを注入した架空語で辞書非依存にする):
  - 受理すべき例:
    - (+1) 長文でのbenign同音綴り。同じ文で、sを除いた綴りそのもの(`Zento`型)のnative判定と結果が一致すること。
    - (+2) add_s方向。
  - 受理すべきでない例:
    - (−1) 短文(一致率0.98未満): native・P1とも不受理。文長依存を固定する。
    - (−2) 母音差。
    - (−3) 語幹置換(`Hayes`←`Hey`型)。
    - (−4) ASR語がCMU未収録(`Mellows`型)。
    - (−5) 他の内容語差。
    - (−6) 数値・否定差。
    - (−7) Secondaryの矛盾(OF-183)。
    - (−8) `-ed`脱落で歯擦音が続かない。
    - (−9) C1の一般語`bus→buzz`型が影響を受けない。
  - 特性固定: (C) `Jones`←`Joan`型(sを除いた綴りがCMU収録の別実在語)が**受理される**ことを、意図した受理リスクとして固定する。
- **任意改善**: Primary側のM1は`secondary_text=None`で呼ばれています(`er006_secondary_asr_01.py:896-897`)。Tier3がすでにAzure転写を取得してcacheしている場合は、それを渡せばOF-183の矛盾拒否を追加費用0で効かせられます(安全側に絞る方向)。

### 論点4: 音響指標
- **結論**: 合否の根拠にしない方針を維持するのが妥当です。
- **根拠**: 負例(sの無い録音)の音響対照がありません。既存知見ではAUC0.74で、単独のgateには使えないと判定済みです(DECISION_LOG L20795付近)。語境界の精度も約20msと粗く、受理根拠に使えば新しい受理基準の新設になります。
- **任意改善**: P1の新経路で受理した分について、音響指標を診断用telemetryとして蓄積し、将来の較正データにする(合否には使わない)。

### 論点5: ②③との三者整合
- **結論**: 大きな矛盾はありません。ただし抜けが1点あります(必須)。
- **根拠と影響**:
  - P1は判定段階だけの変更なので、録音2は2回目のTTSでPASSし、LR/HRには到達しません。
  - ②(両ASR合意条件の削除)によって、ASRの誤認によるNGはHRではなく**Rewrite**(Melos→Heのような内容劣化)に進むようになります。旧CURRENT_SPEC L2818の「エンジンごとに転写が異なる場合は書き換えずHR」という防波堤が無くなるため、誤NGの代償が大きくなり、P1の価値は上がります。逆に、P1の対象外(ASR語がCMU未収録の`Mellows`単独型)は今後Rewriteへ流れます。②の運用観察項目に入れてください。
- **必須修正**: (M5) ③でcanonicalが書換え後の文に変わると、`_m1_frozen_for`はcanonical_textをkeyにして新たに凍結します(`er006_secondary_asr_01.py:198-211`)。このとき`segment_started_at`が現在時刻になるため、同じsegmentの中でそれ以前に更新されたLedgerエントリが候補に入る可能性があり、OF-179違反になります。LR後の凍結では元のsegment開始時刻を引き継ぐか、変更のない語の凍結候補を再利用してください。あわせてtestで次を固定します。
  - LR後の減速前後の判定が、新canonicalの凍結物で行われること。
  - Ledger更新時刻の境界の扱い。

### 論点6: 実装範囲
- **結論**: 変更は`_post_check`の1箇所で済みます。M1の呼出元は2箇所で、Primaryが`er006_secondary_asr_01.py:896`、Secondaryの許容集合が`:946`です。統一judgeは、減速前後・retry・fallback・forced-secondaryのいずれでもこれを経由します。Production側で他に`m1_multi_candidate_judge`を呼ぶ箇所はありません(Grep確認。他の呼出はresearch/eval/testのみ)。
- **必須修正**:
  - (M6-a) `_post_check`内の`classify`は、native判定と同じ呼び方にすること。現状のM1は`classify_fn`省略時に`segment_id`なしで呼んでおり、Tier1のrole gateが効かない点が判定のずれの源になります。どちらに統一するかを明示し、testで固定してください。
  - (M6-b) 既存のOF-178 test(`er006_m1_multi_candidate_01_test_01.py:162-169`)は文が短いため、P1後も**一致率不足で偶然PASSし続けます**。変更が隠れるので、長文版と短文版に分けて期待値を意図的に書き換えてください。`CHANGED_BY_OF178`(L195)も見直しが必要です。
  - (M6-c) KP英語phrase経路がM1に到達するかを確認し、影響範囲をユーザーへの報告に明記すること。
  - DefaultOffIsolation型のtestは不要です(既存関数の仕様変更で、ユーザー承認後に実装するため)。

---

### ユーザー判断が必要な事項
**P1は承認済み範囲外の仕様変更です。** CURRENT_SPEC L2798の本文と、OF-178(採用済みBLOCKER)の改訂を伴います。OPEN-330とは別論点として、次のように問うのが正確です。

**問い**: 固有名詞の語末s/zが歯擦音の続かない文脈で落ちた転写(例: `Melos drank`→`Melo`/`Mello`/`Mellow drank`)を、現在`Melo`だけ警告なしでPASSさせている挙動に揃えて、同音綴り(`Mello`/`Mellow`)もPASS_WITH_WARNINGで受理するか。

- **選択肢A(推奨)**: (a)を確定し、P1を条件付きで採用する(必須修正M1-a〜c・M5・M6、事前の辞書レベルcensus)。
  - 品質: 同じ音声が同じ判定になります。増えるリスクは「TTSが本当に語末sを落とし、かつASRが同音綴りで書いた場合」に限られ、試聴リストで事後確認されます。
  - HR率・速度: Melos型の名前を含むclipのNG(約6%、約0.8回/記事、推定)が減ります。②の施行後に起こりうる不要なRewrite(固有名詞→代名詞)も減ります。
  - 費用: 実装・test費用0円。再生成(各2〜5円)とHR作業が減ります。
- **選択肢A'**: Aの新経路を、Ledgerに登録済みの語に限定する(より狭い形。自動登録と人手登録の区別はOPEN-339で未解決)。
- **選択肢B**: 逆方向に揃え、固有名詞の語幹末sにはbenign吸収を適用しない(`Melo drank`もNGにする)。HRとRewriteが増え、2026-10-13合意とも部分的に衝突します。非推奨です。
- **選択肢C**: 現状維持。綴りの出方次第でPASS/NGが分かれる状態が続きます。②の施行後は、誤NGがRewriteに直結します。

P2(ASRのCMU未収録語の屈折音素導出、語末S/Zの有声性許容)は採らない、というSonnetの判断に同意します(UDR #52の「綴りだけを根拠にしない」と衝突し、ASR誤転写を受理する規則の新設になるため)。

### 関連ファイル
- `C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01.py`(L293-310、L356-422、L485-526)
- `C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py`(L634-651、L687-696、L1137-1176)
- `C:\Users\tensh\eigo-radio\er011_b1_connected_speech_validator_01.py`(L153-166、L224-289)
- `C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py`(L198-247、L627、L800-952)
- `C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01_test_01.py`(L161-195)
- `C:\Users\tensh\eigo-radio\docs\pm\design_principles\connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`(L16-34、L101-127)
- `C:\Users\tensh\eigo-radio\OPEN_ITEMS.md` L833(OPEN-330)、`C:\Users\tensh\eigo-radio\CURRENT_SPEC.md` L2794-2818