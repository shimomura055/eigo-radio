# PREREGISTERED_CRITERIA_06(Trial-06 事前登録。有料生成の前にcommit)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11 / 登録日: 2026-10-25(Step A'' 有料生成の前) / 根拠: `OPUS_REVIEW_04.md`(条件B)(b)1〜6・(c)・必須修正1〜4、Fable判断(委任_11)
Status: DEV/Trial専用。Production採用・配線は未承認。この文書は生成前に固定し、生成結果を見て変更しない(変更が必要な場合は「事後変更」と明記して追記し、合否判定には本書の事前登録版を使う)。
置換関係: `PREREGISTERED_CRITERIA_05.md` §1(許容集合)・§3(安定の定義)・§5((B)多数決)を本書で置換する。Part 2のStep B品質(04 §2-1・2-6)は04のまま有効。

## 0. 実行構成(固定)
- モデル=gpt-6-luna(最新世代の推奨系。Trial-01〜05と同一)。temperature・seed・reasoningは未指定(provider default)。
- Step A''(全文タグ付け)のみ: 6作品 × N=3 = 18 call(標本ID r1〜r3)。各callは`max_output_tokens=13000`を付ける(出力費の上限を保証し、費用ガードの予約額に実効性を持たせる)。
- 費用ガード(Opus必須修正1): 1 call開始前に「実費確定済み累計 + 実行中callの最大見込み額 + 当該callの最大見込み額 <= 上限」を満たすときだけ開始し、満たさなければ他callの完了を待ち、単独でも満たさなければ拒否する。上限=Step A''は12.6円、Step B込みの全体は14円(本委任上限)。自動再試行なし。原因不明のcall失敗が2回で新規call停止。
- Step B(合格時のみ): 各作品r1の選定について(選定0件なら固定文のみでcallなし)、Trial-04と同一Promptで最大6 call。
- Part 1・3・4は本Trialの対象外(Part 2のみ)。

## 1. 規則(主規則。優先順位と2段クラス。固定)
1. 優先順位: **INV > CLEFT > CMP > FRONT > HEAVY > POSTMOD > SPEC > ELL > APPOS**。OTHERは自動選定の対象外(記録のみ)。
2. 強クラス = INV・CLEFT・CMP。中クラス = FRONT・HEAVY・POSTMOD・SPEC・ELL・APPOS。
3. 適格 = 本文に解決でき重複でない かつ `basic_only=false` かつ 分類がOTHERでない かつ 材料欄(construct_ja・points_ja・context_ja)が揃う。さらに **中クラスは `misread_target`∈{SUBJECT,VERB,MODIFIEE,OMITTED} かつ `misread_quote`が選定文に逐語で含まれる** 場合のみ適格(強クラスは追加条件なし)。
4. 選定 = 適格を(クラス優先順, 段落番号, 出現順)に並べ、**同じクラスの2件目と同じ段落の2件目は選ばない**、最大2件。適格が0なら0件(0件を既定にはしない)。
5. `tier`・`rank`欄は廃止。`basic_only`は残す。`subject_span`/`main_verb`は記録欄(規則に使わない)。
6. 分類の定義(Prompt): SPECは形式目的語it・目的語が長い・wish+目的語+形容詞/副詞等に限り、使役/知覚動詞+目的語+原形/分詞とkeep/make/find+目的語+補語の基本形は基礎へ。ELLは前の部分から動詞・主語・比較の基準を補わないと構造が取れない省略に限り、会話の断片・間投詞・一語返答は基礎へ。APPOSの伝達部(said X等)に付くものは基礎へ。INVの伝達部倒置は除外(既存)。
7. 比較用規則(オフライン適用のみ。合否に使わない): (O)元のwhat-if規則=基礎のみ除外・misread_ja非空・クラス優先順で上位2件(同一クラス制約・追加条件なし) / (N)主規則の適格条件のまま同一クラス・同一段落の制約を外した版。

## 2. 許容集合(Step A'' 実行前に登録。本文を読んで作成。目印語句は本文の逐語。選定文が目印語句を含み段落が一致すれば一致)
「許容集合」=「中核 ∪ どちらでも可」。厳格側の副指標として「選定⊆中核」の率も併記する(合否には使わない)。

| 作品(区分) | 中核(核となる難所) | どちらでも可 |
|---|---|---|
| 開いた窓(既存) | P21 `Across the quiet garden came a young voice:` | P29 `Inventing convincing stories at a moment’s notice was Vera’s speciality.` |
| イグ・ノーベル賞2026(既存) | P4 `what you got was a map of molecules` / P5 `more than three times as much energy as the same weight of milk` / P8 `What’s more interesting is` / P9 `there should be a sign` | P2 `research on nutrient-rich crystals that had been published earlier` / P3 `protein crystals containing nutrients from the gut of the unborn young` / P11 `Rather than seeing this as a possible breakfast for people` |
| 賢者の贈り物(既存) | P4 `handed down from his grandfather to his father` / P22 `Inside were the tortoise-shell combs` / P30 `sat two foolish young people whose love made them the wisest` | P12 `Nothing showy, nothing unnecessary.` / P29 `Each had sold their greatest treasure to buy the other a gift.` |
| 猿の手(**開発用へ変更**。Trial-05で本文を見て学習済み) | P24 `Then came a soft knock.` | P2 `a retired sergeant-major home from India` / P8 `Enough to pay off the house!` / **P18 `Wish him alive again!`(追加)** / P19 `I’m afraid of what might come back.` / P22 `I wish Herbert alive again.` / P32 `The street lamp opposite shone on a quiet, deserted road.` |
| 告げ口心臓(**新ホールドアウト**。Listen Carefully) | P8 `From the bed came a small groan of terror.` / P15 `At four in the morning came a knock.` | P2 `that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold`(長い主語+挿入)/ P4 `Always closed.` / P10 `Wide open.`(前の部分から補う省略)/ P5 `He hated the eye, not the man.`(省略)/ P11 `Then he heard it: a low, quick beating, like a watch wrapped in cotton.`(コロン後の同格)/ P11 `Faster it beat, and louder.`(比較級の前置)/ P17 `Calm and confident, he sat directly above the hidden body.`(形容詞句の前置) |
| 二十年後(**平易な本文**。The Promise) | なし | P23 `Twenty years can change a man, but not the shape of his nose.`(`can change`を補う省略)のみ |

除外(許容集合に入れない)の例: 命令文+and、動名詞主語の単純形、`the`+形容詞、伝達部の倒置・同格(`said X`/`he explained`)、分詞構文・付帯状況のwithの基本形、`whose`の基本用法、会話の断片(`Not for years.`/`Here, beneath my feet!`)、`I recognized your face as the man wanted in Chicago.`(分詞の基本用法=基礎)。
作品選定理由(1行ずつ): 開いた窓・イグ・賢者=Trial-03〜05で継続使用の3作品(比較の連続性) / 猿の手=Trial-05のホールドアウト(今回は学習済みとして開発用) / 告げ口心臓=Family Z既存完成記事(`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/writer/r2.md`)でTrial-01〜05に未使用、倒置(P8・P15)・前置・省略・長い主語を含む22段落 / 二十年後=Family Z既存完成記事(同`after_twenty_years`)で口語会話中心・倒置や長い修飾が基本無く、埋め草化と0件経路の検証に適する。
注記: 許容集合は主観を含む(迷う文は「どちらでも可」に入れた)。告げ口心臓・二十年後は設計で一度も見ていない本文(Sonnetが生成前に作成、Fableが事後に照合)。

## 3. 合格条件(作品別。Step A'' 18標本の機械的当てはめ+基礎のみ判定の目視)
- **難所のある作品(開いた窓・イグ・賢者・猿の手・告げ口心臓)**: 3標本すべてで (1) 選定された文がすべて許容集合内 (2) 0件の標本が1つもない (3) 基礎だけの選定が0(construct_ja・points_jaと選定文が、`PREREGISTERED_CRITERIA_05.md` §2の基礎項目の説明のみでない。Sonnetが目視で判定し、迷う場合は判定保留としてFableへ)。
- **平易な作品(二十年後)**: 3標本すべてで、選定された文が許容集合の外にない(0件も可)。
- **Part 2成立(Step A''段)= 6作品すべて合格**(全18標本が取得できていること、parse失敗0)。標本が欠けた作品は不合格として扱う。告げ口心臓が不合格なら「過剰適合」とみなす。
- **Step B品質(合格時のみ実行。各作品r1)**: Part 2節(`## Part 2`以降全体)に`PREREGISTERED_CRITERIA_04.md` §2-1の開発者向け語が0件 / `check_quotes_04.py`相当の逐語照合で本文にない引用(比較用除く)0件・前後文の引用は逐語 / 本文にない事実なし(判定保留可) / 各選定に日本語訳・仕組み・意味の3節以上があり(比較は任意)、選定0件の作品は固定文のみ。
- **Trial終了判断(後付け禁止)**: Step A''全作品合格かつStep B品質合格 → 追加の磨き込みをせずTrial終了(Status候補: Part 2=VALIDATED候補、最終はFable。Production採用は人間のみ)。

## 4. 終了条件(Opus条件B・Fable判断。固定)
**不合格なら4回目は行わない。** Prompt微調整・規則の再調整・追加Trialを行わず、撤退案(03d一括 / 0件許容 / Part 2保留)をQCD付きで整理してFableへ報告し、`USER_DECISION_REQUIRED`へ進む。Step A''が不合格の場合はStep Bを実行しない。

## 5. 追加の測定(合否外・EVAL_06に記録)
- 比較用規則(O)(N)の選定と許容集合との関係、主規則との差。
- 登録済み文の分類コードの標本間一致(分類は安定か)。
- 中クラス追加条件で落ちた候補(`mid_cond_rejected`)。
- 平易な作品の適格数(埋め草の余地)。`sentence_replaced_by_body`・resolve失敗・未カバー段落・材料欄欠落。
- 基礎のみの選定(目視)・語彙誤読の混入(目視、判定保留可)。

## 6. 費用(固定)
本委任上限14円(Step A'' 実費見込み約10円[上限12.6円]、Step B約1.2円)。案件累計上限はFable権限で20円→35円へ引き上げ(2026-10-25、理由=Opus条件B推奨の3回目実施、BUDGET_LOG_01.mdに記録)。日次1,000円(JST)内。

## 7. 事前に予測している点(結果と照合するため記録)
- 難所のある作品の主規則は、強クラス(INV/CLEFT/CMP)が実際に挙がる作品では全標本で強クラスが1件目になり、揺れは2件目(中クラス)に限られる見込み。
- 告げ口心臓はP8・P15がINVとして挙がり、同一クラス制約で1件のみ選ばれ、2件目は中クラス(P11・P17等)になる見込み。許容集合外の中クラス(例: P1の挿入)が混ざるかが焦点。
- 二十年後は適格が0〜1件で、0件または`P23`のみになる見込み。許容集合外(例: P28・P19のwith構文・P20の並列)を選ぶと不合格。
- 費用: Step A'' 約0.5〜0.7円/call。
