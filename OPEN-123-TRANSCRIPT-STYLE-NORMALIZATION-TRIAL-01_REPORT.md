# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01

管理ID: OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01
種別: 隔離Trial(Lane A、ユーザー承認2026-09-07、新規仕様候補)
Status上限: VALIDATED(Production Validator変更・正規化カテゴリの正式追加・
Key Phraseへの展開はいずれも未実施、提案のみ)
Git: 未実施(Fableが統合)

コード: `er011_transcript_style_normalization_trial_01.py`(root)
出力: `er011_output/transcript_style_normalization_trial_01/`
　- 実測manifest: `er011_output/transcript_style_normalization_trial_01/results/manifest.json`
　- 試聴player(file:///): `file:///C:/Users/tensh/eigo-radio/er011_output/transcript_style_normalization_trial_01/player.html`
　- cost log: `er011_output/transcript_style_normalization_trial_01/audit/raw_usage_log.jsonl`
cost実測: **¥22.97**(上限¥500、未到達)

---

## 1. 既存normalization仕様(原文・箇所)

`er006_preprod_hardening_01_validation.py`(Production、HEAD版、本Trialでは
一切変更せずimportのみ)の`normalize_text()`(393-422行)は以下を実施済み:

- Unicode上付き数字/指数のマーカー化、発音区別符号除去(`strip_diacritics`)
- 英米綴り差(`BR_AM_SPELLING_PAIRS`)
- em dash(—)・en dash(–)→ハイフンへの統一
- curly quote(’‘“”)→straight(' ")への統一
- 数字正規化(`normalize_numeric`、cardinal/ordinal/通貨/percent/小数点等)
- 通り種別略語展開(`_STREET_SUFFIX_RES`)
- **`re.sub(r"[^a-z0-9]+", " ", t)`(420行)で、カンマ・em dash・ハイフン・
  アポストロフィを含む「英数字以外の全ての記号」を空白へ置換**してから
  空白区切りでtoken化

`tokenize()`(435-436行)はこの`normalize_text()`の結果を`.split()`した
もの。`classify_asr_match()`(712-829行)はtoken列が完全一致すれば
`NORMALIZED_MATCH`(should_pass=True)とする。

`_STOPWORDS`(487-507行)には、"they're"→"they"+"re"のように短縮形が
アポストロフィ除去で分裂した際の残骸"re"(are由来)のみ吸収済みだが、
**同コード中のコメント(497-506行)に「will/haveの短縮形('ll'/'ve')は
同じ対策では直らず、より広い契約形(contraction)対応の設計が別途必要
(本修正の対象外、実データでの発生は未確認のため見送り)」と明記**されて
おり、これが本Trialが検証したギャップの既存の認識である。

## 2. 今回不足していた差分

上記420行の正規表現により、**punctuation・comma・em dash・hyphen・
curly quoteの差は既に吸収済み**であることを実データで確認した(§4参照)。
唯一の実証済みギャップは、**アポストロフィを含む標準contraction**
("do not"⇔"don't"等)。アポストロフィも420行の正規表現で空白に置換される
ため、"don't"は"don"+"t"という2つの無意味なtokenに分裂し、canonical側の
"do"+"not"とは語数・語形とも一致しない(`negation_mismatches`により
`TRUE_CONTENT_MISMATCH`)。加えて、"want to"⇔"wanna"のような**2語→1語の
口語的縮約**(OPEN-122で個別発見済み、本Trialのスコープ)も同様に
未吸収。

## 3. do not↔don't結果

実例(Trial-08 p3 Voice B、`er012_output/editorial_b_voices_trial_08_audio/
p3/b1b/audit/stopped_audio_evidence/point_two_result.json`、3回とも
STOPPED)を本Trialで再解析した:

| attempt | 既存Validator(baseline) | 提案(contraction_expansion適用後) |
|---|---|---|
| 1 | TRUE_CONTENT_MISMATCH | TRANSCRIPT_STYLE_NORMALIZED_MATCH |
| 2 | TRUE_CONTENT_MISMATCH | TRANSCRIPT_STYLE_NORMALIZED_MATCH |
| 3 | TRUE_CONTENT_MISMATCH | TRANSCRIPT_STYLE_NORMALIZED_MATCH |

3回とも実際の不一致は"do not"↔"don't"のみ(後述の通りコンマ・em dashは
既に無関係と判明)であり、標準contraction展開(`do not`⇔`don't`等、
否定を保持したまま展開する安全な閉じた集合)を両テキストへ適用したうえで
既存`classify_asr_match()`を再実行すると3回とも一致した。新規Standard
TTS実測(A_contraction_negation、4件: does not/doesn't・are not/aren't・
will not/won't・cannot/can't相当の文)では、今回のTTS発話は4件とも
Primary/Secondary/LocalすべてEXACT_MATCH(自然発生のfalse rejectは
再現せず、確率的事象であることの追加確認)。同時に、Regression fixture
(§8)側で"they're↔they are"・"we're↔we are"の実データ2件が
`ASR_VALIDATION_UNCERTAIN`(should_retry=Falseだが未PASS)から
`TRANSCRIPT_STYLE_NORMALIZED_MATCH`(should_pass=True)へ改善することも
確認した。

## 4. punctuation/comma/em dash結果

**既存Validatorで既に完全に吸収済み(新規対応不要)**。Trial-08実例の
コンマ差("uncomfortable or"→"uncomfortable, or")、em dash差
("need—or"→"need or")を個別に`tokenize()`へ通したところ、両方とも
`NORMALIZED_MATCH`で正しく吸収されることを確認した(トークン列が
完全一致)。新規TTS実測(A_punctuation_em_dash 1件、A_punctuation_comma
1件、A_tokenization_hyphen 1件)でも、Primary/Secondary/Local全経路で
EXACT_MATCHまたはNORMALIZED_MATCHとなり、追加のnormalizationが不要
であることを確認した。**Trial-08 STOPPEDの真因はcomma/em dashではなく
"do not"↔"don't"単独**であったと結論づけられる。

## 5. tokenization結果

ハイフン複合語("well-known")は既存420行の正規表現とdespace比較
(736-739行、冠詞除去済みdespace比較753-759行)により既に吸収済み。
新規実測(a13)でもPrimary/Secondary/Local全てEXACT_MATCH/NORMALIZED_MATCH
相当。追加のtokenization対応は不要と判断する。

## 6. want to↔wanna結果

実例(OPEN-122 Trial-01、P6_dont_you、canonical="Don't you want to come
with us?"、Primary="Don't you wanna come with us?"、Secondary/Local=
canonical通り)を再利用した:

| 方式 | 判定 |
|---|---|
| baseline(既存Validator) | TRUE_CONTENT_MISMATCH |
| wanna_mode=b(適用しない、既定) | TRUE_CONTENT_MISMATCH(変化なし) |
| wanna_mode=a(無条件適用) | TRANSCRIPT_STYLE_NORMALIZED_MATCH |
| wanna_mode=c(Secondary/local corroboration必須) | TRANSCRIPT_STYLE_NORMALIZED_MATCH(Secondary・local両方がcanonical側"want to"を支持) |

新規TTS実測(B、5件: want to×2・going to×1・got to×1・"wanna"を台本に
直接使う逆方向確認×1)では、自然発生のPrimary側"wanna"化は今回は
再現しなかった(b01/b02とも3経路ともEXACT_MATCH)。一方、b05
(台本自体を"I wanna check..."とした逆方向確認)で、**Secondary/Local
側が台本の口語形を勝手に正書法"want to"へ書き換える非対称性**を新たに
確認した(Primary=台本通りEXACT_MATCH、Secondary/Local=
TRUE_CONTENT_MISMATCH→mode_aのみ救済、mode_cはこの自己参照的な比較
構成では救済されない、詳細は§8の限界を参照)。口語的縮約は
2語→1語というtoken数変化を伴い、標準contractionより性質が異なるため、
**単純な同一視(mode_a)はfalse accept riskが相対的に高いと判断し、
corroboration必須方式(mode_c)を安全側の候補として推奨**する
(§13参照)。

## 7. asked↔asks等Negative結果(否定反転含む)

**false accept 0件**(全方式・全テストで確認)。

- 実例再利用(OPEN-122 Trial-01、P1_asked_them・N3_asks_not_asked、
  "asked"⇔"asks"): baseline・mode_a・mode_c いずれも
  `TRUE_CONTENT_MISMATCH`のまま(正しく非救済、動詞屈折形は本Trialの
  対象外の別failure mode)。
- 新規Negative Control 6件(C_negative_tense_inflection×2、
  C_negative_content_word_swap×2、**C_negative_negation_reversal×2
  [can↔can't、will↔won't]**)を実際にTTS音声化し、意図的に異なる
  テキストを発話させたうえでPrimary/Secondary/Local ASR実測。
  6件×3経路×3方式=54通り全てで`TRUE_CONTENT_MISMATCH`のまま
  (`style_normalized_should_pass=False`)、**false accept 0/54**。
  特にcan↔can't・will↔won't(意味反転)は、本Trialのcontraction
  展開テーブルに「否定を保持したまま展開するペアのみ」を採用した
  設計(cannot⇔can't・will not⇔won't等、"can"単体⇔"can't"は
  テーブルに存在しない)により構造的に安全であることを実証した。

## 8. false accept/false reject(方式×テスト表)

| テストセット | 件数 | baseline false reject/false accept | contraction_expansion(mode共通) | wanna_mode=b | wanna_mode=a | wanna_mode=c |
|---|---|---|---|---|---|---|
| 既存Regression fixture(POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28) | 59 | fixture設計通り(NEGATIVE 28件は意図的mismatch) | **NEGATIVE 28/28 非救済(false accept 0)**、POSITIVE中2件(they're/we're)を追加救済 | 同左 | 同左(wannaは59件中出現なし) | 同左 |
| 実例1: Trial-08 p3 Voice B(do not/don't) | 3 | 3/3 false reject(STOPPED) | **3/3 救済** | 3/3 救済 | 3/3 救済 | 3/3 救済 |
| 実例2: OPEN-122 wanna(P6) | 1 | 1/1 false reject | 非該当(wanna単独では非救済) | 非救済(1/1) | **救済(1/1)** | **救済(1/1)** |
| 実例2: OPEN-122 asked/asks(Negative) | 2 | 2/2 正しくmismatch維持 | 2/2 非救済(正しい) | 同左 | 同左 | 同左 |
| 新規TTS A(標準contraction+punctuation) | 13 | 13/13 baseline既にPASS(自然発生false reject再現せず) | 該当なし(元々PASS) | 同左 | 同左 | 同左 |
| 新規TTS B(colloquial) | 5 | 4/5 baseline PASS、b05はSecondary/Local側で新規false reject 1件発見 | 非該当 | b05非救済 | **b05救済**(Secondary/Local) | b05非救済(自己参照的な比較構成のため、詳細は下記限界参照) |
| 新規TTS C(Negative Control、can/can't・will/won'tの否定反転含む) | 6×3経路×3方式=54 | 全てTRUE_CONTENT_MISMATCH(意図通り) | 非該当 | **false accept 0/54** | **false accept 0/54** | **false accept 0/54** |

**総括**: contraction_expansion(標準contraction展開)は、実証済みの
false reject全件(fixture 2件+Trial-08 3件=5件)を安全に救済し、
false accept増加は0件(fixture NEGATIVE 28件+新規Negative 54通り、
計82通りで確認)。wanna系は、mode_a(無条件)がfalse reject救済範囲は
広いが、b05で見つかった「Secondary/Local側が口語形を正書法へ書き換える
非対称性」のような**未知の逆方向ケースでの誤救済リスクが理論上残る**
(今回は偶然、意味内容自体は変わらないケースだったため実害なし)。
mode_c(corroboration必須)はより保守的で、実例2(P6)の正しい構成
(Primary=対象、Secondary/Local=独立裏付け源)では正しく機能したが、
**本Trialのテスト用ハーネスの実装上、Secondary/Local自身を評価対象と
した場合の自己参照的な比較(b05)には対応していない**(下記「限界」
参照、本番経路ではPrimaryのみが分類対象のため実害はないと考えられる
が、未検証)。

**限界(正直な記載)**: 新規TTS実測で自然発生したfalse reject新規例は
b05の1件のみで、これはPrimaryではなくSecondary/Local側の書き起こし
非対称性という、当初想定(Primaryのみが口語化する)とは逆方向の現象
だった。母集団が小さいため(新規24件)、Primary側での自然発生wanna化の
再現率は依然として実測1件(OPEN-122のP6のみ)にとどまる。

## 9. A2/B1本文への適用可能性

- **contraction_expansion**: A2/B1本文はいずれも通常のセンテンス構造
  (Key Phraseのような短句と異なり文脈が十分にある)で、既存NEGATIVE
  fixture 28件・新規Negative Control 54通りいずれもfalse acceptが
  発生しなかったことから、**本文segment(A2 full_story・B1
  comment/point等)への適用は安全側に倒れると評価**する。Key Phrase等の
  短句(§後述、非対象)とは性質が異なる。
- **wanna系**: 適用するとしてもmode_c(corroboration必須)に限定すべき
  で、mode_a(無条件)はb05のような未知の逆方向ケースの誤救済リスクが
  残る。
- **Key Phraseへの展開はしない**(タスク仕様§4で明示的に除外、理由:
  Key Phraseは短句で文脈情報が乏しく、"do not"のような2語以上の
  contractionパターンが単独で出現する可能性が本文より低い一方、
  1語の誤りが占める割合が本文より大きいため、本Trialのfixtureは全て
  文単位のcontent[Malmö文・wide-scale hyphen等本文/Key Phrase混在]で
  検証しており、Key Phrase固有のfalse accept riskは未検証)。

## 10. QCD

- **Quality(品質)**: false accept 0/82(fixture NEGATIVE 28+新規
  Negative Control 54)、false reject救済 5/5(実証済み既知事例)。
  ただし新規TTS陽性セット(A/B、計18件)では自然発生false rejectが
  1件(b05、非典型)しか再現せず、rescue効果の母集団規模は限定的。
- **Cost**: 実測¥22.97(上限¥500の4.6%)。ローカル文字列処理
  (`expand_contractions`/`expand_colloquial`)自体は追加API課金なし。
- **Delivery(実装コスト/保守性)**: Production側の
  `normalize_text`/`tokenize`/`classify_asr_match`は無変更のまま
  「外側から包む」設計のため、Production統合時の変更範囲は小さい
  (新規関数の追加のみ、既存関数の書き換え不要)。曖昧性('s/'dの
  is/has・would/had解釈)は「両側が完全一致した場合のみ採用」という
  安全設計により実害化しないことを構造的に保証している(§本文参照)。

## 11. Trial status(方式別)

| 方式 | Status |
|---|---|
| (i) 標準contraction展開(否定保持のみ、can/can't等の反転は含まない) | **VALIDATED**(false accept 0、false reject救済5/5、Regression無回帰) |
| (ii) punctuation/dash/apostrophe正規化 | 対応不要と判明(既存で吸収済み、追加実装なし) |
| (iii) tokenization統一 | 対応不要と判明(既存で吸収済み、追加実装なし) |
| (iv)-a wanna等の無条件同一視 | VALIDATED止まり(false accept 0だが、b05で理論上のリスクを確認、Production採用は非推奨) |
| (iv)-c wanna等のcorroboration必須同一視 | VALIDATED(実例1件で正しく機能、テストカバレッジ小、ハーネスの自己参照上の限界あり) |
| (iv)-b wanna等を正規化しない(現状維持) | 現状維持(安全側、Production変更なし) |

## 12. USER_DECISION_REQUIRED

1. 標準contraction展開(方式i)をProduction採用候補として次段階
   (正式配線Trial/実装)へ進めるか。
2. wanna系(方式iv)について、(a)本文へ一切適用しない(現状維持)、
   (b)mode_c(corroboration必須)のみ限定的に採用検討、のいずれを
   選ぶか。
3. Key Phrase経路への展開要否(本Trialでは意図的に未検証、必要なら
   別Trialとして起票するか)。
4. 's/'d等の曖昧なcontraction(is/has、would/had)をテーブルに含めた
   まま採用するか、明示的に除外するか(構造的安全性は確認済みだが、
   除外すればより保守的になる)。
5. b05で見つかったSecondary/Local側の書き起こし非対称性(口語台本を
   正書法へ書き換える現象)を、独立の調査対象として扱うか
   (本Trialのスコープ外、実害は未確認)。

いずれもユーザー承認なしに実装しない。

## 13. Production採用候補(最小・安全)

最小・安全な候補として、**方式(i)標準contraction展開のみ**(否定を
保持する閉じた集合、can/can't等の反転を含まない、wanna系は含まない)を
提案する。理由: (a) false accept 0/82で実証済み、(b) 実証済み既知
false reject(Trial-08 3回STOPPED、fixture 2件)を全て救済、(c)
Production `normalize_text`/`tokenize`は無変更、(d) 曖昧性があっても
「両側完全一致時のみ採用」という設計により構造的に安全、(e) 追加API
課金なし(ローカル文字列処理のみ)。wanna系(方式iv)はいずれのmodeも
今回のTrial単独ではProduction採用候補として推奨しない(母集団小・
b05の非対称性など未解明点あり)。

## 14. SSOT登録案(提案文言、本Trialでは未反映)

OPEN_ITEMS.md OPEN-123行への追記案(反映はFableまたはユーザー判断):
「OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01(2026-09-07、ユーザー
承認済み隔離Trial、Production未配線)実施。標準contraction展開
(否定保持のみの安全集合)はfalse accept 0/82・実証済みfalse reject
5/5救済・既存Regression fixture 59/59無回帰(VALIDATED)。
punctuation/comma/em dash/hyphen/tokenization差は既存Validatorで
既に吸収済みと判明(追加対応不要)。"want to"↔"wanna"等の口語的縮約は
corroboration必須方式(mode_c)でのみ限定的にVALIDATED、無条件同一視
(mode_a)は理論上のfalse accept riskを1件確認(b05、Secondary/Local
側の非対称的な書き起こし)し非推奨。"asked"↔"asks"型・can/can't・
will/won'tの否定反転はいずれも正しく非救済(false accept 0)を確認。
Production採用可否・Key Phrase展開要否はUSER_DECISION_REQUIRED。
根拠: 本Report。」DECISION_LOG.mdへの追記も同様の要約で提案する
(反映は本Trialの範囲外)。
