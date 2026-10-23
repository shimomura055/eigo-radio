MARKER: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02 (2026-10-24, Fable→sonnet-worker)

# 管理ID: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02(Opus必須レビュー反映→案C実装→test/replay/全回帰→X/Z Production反映(共通module)→runtime evidence→SSOT/Git。OPEN-482の2件を解決)
# Fable判断: 案C採用。Opus(§Zに逐語)の判定「条件付きで実装へ進んでよい」に従い、**必須修正OF-TN-01〜06を全て反映**。論点2(年号語形↔桁連結がNG側に倒れる件)はOpus見解どおり「ユーザー指示②-2の一般化・安全側・本文経路では従来からNG」としてユーザー事前判断は不要、ただし完了報告とOPEN_ITEMSに明示(OF-TN-06)。範囲外所見X-2・24時間表記・分00〜09は別OPEN。F-1は下記Hのとおり。

## 0. 前提
- 委任_01成果 `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/{DESIGN_01,ROOT_CAUSE_01,STRUCTURE_01,TEST_MATRIX_01,PRODUCTION_PLAN_01,CANDIDATE_C_01.diff,README_REPLAY_01.md,replay_*_01.py,pairs_01.jsonl}`、委任文 `docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_01.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-24_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER_02.md` §1-②〜§5(完了条件1〜8)。
- **最初に§Zを `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/OPUS_REVIEW_01.md` へ逐語保存**。
- 実行は `.venv\Scripts\python.exe`(依存あり環境)。費用上限 **10円**(新規TTSは原則0。必要時のみX 1clip・Z 1clip 各≤3円、理由を記録)。ACTIVE_TASKの本管理ID行を更新(有料run発生時は進行中→終了)。
- 検証中の副作用防止: `classify_asr_match` の telemetry 自動追記(`er021_output/.../telemetry.jsonl`、追跡対象)を検証scriptではno-op化(委任_01 `judge_sim_01.py` の方法)。回帰後に `git status` で追跡ファイルの意図しない変更がないか確認し、あれば内容を確認のうえ報告(他agentの追記を破棄しないよう `git checkout` で無造作に復元しない。復元が必要ならFableへ)。

## 1. 実装(er021 `_tier1_atoms` + `_try_clock_pair`。X/Z/A/B/C共通moduleで1箇所)
- CANDIDATE_C_01.diffを基礎に、次を反映:
  - **OF-TN-01**: 分の直後が `percent`/`per cent`/`_CURRENCY_WORDS` なら時刻にしない(Noneを返す)→ `10 twenty-dollar bills`↔`10 $20 bills` EQ維持、`2 fifteen percent`↔`2 15%` EQ維持。
  - **OF-TN-02**: am/pm(a.m./p.m.含む)が直後に続く場合に限り、分に2桁数字(10〜59)も受け付け両側をtime atom(meridiem付き)に揃える→ `At 10 thirty pm`↔`At 10 30 pm` EQ、`ten thirty pm`↔`10 30 pm` EQ、am/pm違いはNE。
  - **OF-TN-03**: 直前語 `and` の除外は、その直前が数詞語・scale語・数字のときだけ→ `between 9 and 10 thirty`↔`between nine and ten-thirty` EQ、`and ten thirty`↔`and 1030` NE、`one hundred and ten`↔`110` EQ維持。
  - 分の範囲10〜59は共通定数化し、3層(er006境界分割/`_clock_pair` 0〜24/案C 1〜12)の時の範囲が異なる理由をコメントで明記(推奨採用)。
  - `thirty 5` 分岐はF-1の部分救済として残し、その旨コメント。
- **OF-TN-04**: X/Z scope ON(er109同音救済を含む正式経路)で TEST_MATRIX #21/22/42/67/68 がRESCUEされないことを固定test化。#66(数字 `1030`↔`10:30` のer109承認規則)はPIN。**#22(`At 1030`↔`At ten thirty`)がRESCUEされる場合は実装を止めてFableへ報告**(既存承認規則とユーザー指示②-2の衝突)。
- test追加(新規 `er021_time_numeral_test_01.py` 等。Opus列挙の全ケースを転記):
  - `At 10 thirty pm`↔`At 10 30 pm` EQ / `At ten thirty pm`↔`At 10 30 pm` EQ / `At ten thirty pm`↔`At 10 30 am` NE
  - `10 twenty-dollar bills`↔`10 $20 bills` EQ / `2 fifteen percent`↔`2 15%` EQ / `3 twenty euros`↔`3 €20` EQ / `twelve fifty dollars`↔`$12.50` NE
  - `between 9 and 10 thirty`↔`between nine and ten-thirty` EQ / `between nine and ten thirty`↔`between nine and 1030` NE / `one hundred and ten`↔`110` EQ
  - 非Tier1 role(KP): `ten thirty`↔`1030` NE / `ten thirty`↔`10:30` EQ / `ten thirty`↔`10 30` EQ
  - X/Z scope全経路: #21/22/42/67/68 NE、#66 PIN(RESCUE)
  - Secondary: canon `At 10 thirty`/`At ten thirty`、Primary `10:13`→P1 PIN / Primary NG(他要因)→Secondary `10 30` でTier1 PASS EQ
  - 年号: `in 1215`↔`in twelve fifteen` NE(PIN・開示) / `in 2010`↔`in twenty ten` EQ / `in 1066`↔`in ten sixty six` EQ / `in 1905`↔`in nineteen oh five` PIN
  - 名詞後続: `the 10 thirty bus`↔`the 10:30 bus` EQ / `the eleven fifteen train`↔`the 11:15 train` EQ
  - 複数時刻: `from 9 fifteen to 10 thirty`↔`from 9:15 to 10:30` EQ / `at 9 fifteen, 10 thirty`↔`at 9:15, 10:30` EQ(SequenceMatcherのreplace block結合で`_clock_pair`が成立しない懸念を実測)
  - `ten thirty-five`↔`10:35` EQ / `ten-thirty a.m.`↔`10:30 a.m.` EQ / `one fifteen`↔`1:15` EQ / `one fifteen`↔`fifteen` PIN / `ten oh five`↔`10:05` PIN / `ten o'clock`↔`10 o'clock` EQ
  - c8実対は2表記とも(`At 10 thirty`×`At ten-thirty`、`At ten thirty`×`At 10:30`)、出所(slot/attempt)を明記。
- TEST_MATRIX_02.md: 上記を追加した拡張セットで修正前/後を実測(誤NG/誤PASS 0、PIN不変)。

## 2. 検証(OF-TN-05、Production反映前の必須条件)
- pairs再抽出→replay(修正前/後): judge PASS→NG 0、分類層PASS→NG 0、value_guard PASS→NG 0、NG→PASSは内訳(時刻起因のみ)。結果を `REPLAY_02.md`。
- 全回帰 `run_project_regression.py`: 自分起因の失敗0(既知3件[er003_test_bad/er019/er020]は記載)。
- A/B/C Legacy(§27-3): 判定変化がないことをreplayのFamily別内訳で示す(A/B/C entryにPASS→NGが0)。

## 3. Production反映・runtime evidence(完了条件4〜6)
- 共通moduleのため実装commitがX/Z(およびA/B/C)全経路の配線。retry/fallback/regeneration/resume/再利用/引継ぎで同じ関数が呼ばれることをコード(関数・行)で示す(`WIRING_EVIDENCE_01.md`)。flag不要・既定ON(不具合修正)。
- runtime evidence `RUNTIME_EVIDENCE_01.md`: 既存X/Zの保存entry(Zは『二十年後』c8の実対2表記、Xは時刻/数値を含む既存entry数件)を `rejudge_with_current_judge`/`guard_entry` で修正前後に再判定し、判定・basis・atom列を記録。新規TTSなし。X/Z双方の適用を確認。
- 完成作品への影響: 既存完成記事の再生成はしない。『二十年後』は承認済みで再処理不要(ユーザー決定)。

## 4. SSOT(完了条件7)
- `CURRENT_SPEC.md`: 値ガード/数値正規化の既存記載(l.2834-2835付近、er109時刻規則 l.2970付近)に「隣接数詞語の時刻形統一(時1〜12+分10〜59、am/pm付きは分2桁数字可、percent/通貨後続は除外、年号語形↔桁連結は不一致側)」を既存書式で追記。新規節は作らない。
- `OPEN_ITEMS.md`: OPEN-482を解決(2件の原因・修正・証跡・残存の開示[`in 1215`↔`twelve fifteen` NE側、#72/73 `10 thirty 5`↔`10:35` はF-1由来で残存]、PRODUCTION_WIRED判定はFable受入後)。新規OPEN: F-1(`thirty five`→`thirty 5` 部分数字化で `35 people` 誤NG、時刻#72/73含む、修正第一候補=er006/er021で「十の位の語+1桁数字」を合成数として読む)、X-2(`one hundred thirty people`↔`1:30 people` PASS、UNKNOWN非阻止)、24時間表記・分00〜09未対応、telemetry自動追記→`git checkout`復元の運用事象(委任_01)。
- `DECISION_LOG.md`: Fable判断(案C採用・Opus条件A/B反映・年号帰結の開示)。
- 並行編集中の他agent(KP②配線/『賢者の贈り物』)があるため、commit前に `git diff -- OPEN_ITEMS.md DECISION_LOG.md CURRENT_SPEC.md` で自分以外のhunkを確認(含まれる場合は数分待って再確認、残る場合は報告に明記)。

## 5. Git・報告
- 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_02.md`(先頭MARKER一致、0始まり)。
- commit(実装+test=1 commit[単一commitでrevert可能]、docs/SSOT=別commit可。変更ファイル明示、`git diff --cached --name-status`、`git commit --only -- <paths>`、secret grep 0件、`git add -A/-u/-f`禁止)→`git push origin HEAD:main`。
- 報告 `docs/pm/RESULT_PACKET_ATN2.md`: 完了条件1〜8のチェック表、OF-TN-01〜06の反映表、TEST_MATRIX_02/REPLAY_02要約、全回帰、runtime evidence要約(X/Z)、残存の開示、F-1の扱い(H)、費用、commit hash・raw URL、4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)、判定整合行、使用モデル(LLM呼出0の見込み)。

## H. F-1の扱い(案C完了・commit後に実施、別commit)
- F-1(`tts_safe_number_words_en` が `thirty five` の `five` だけ数字化→canon `thirty 5`→分類層が `30 5` と読む)について、Opus推奨の「er006/er021の両方で『十の位の語+1桁数字』を合成数として読む」修正を、**同じ影響分析gate(replay PASS→NG 0・合成負例NG維持・各層1関数1ブロック以内)**で評価。gate通過かつ差分が小さければ実装・test・replay・commit(別commit)。通過しない/差分が大きい場合は新規OPENに評価結果を記録して止める(er003側のTTS入力変更はProduction挙動変更のため本委任では行わない)。

## §Z OPUS_REVIEW_01(逐語保存用)
## ASR-TIME-NUMERAL-EQUIVALENCE-01 OPUS_REVIEW_01(条件A+B)レビュー結果

### 判定: 条件付き(必須修正 OF-TN-01〜06 を満たせば実装へ進んでよい)
案C(隣接する数詞語2語の読みを、atom化[数値を比較用の部品に分ける処理]の1点で時刻形に揃える)は、根本原因に対する構造的な解消になっています。理由は次の3点です。
- 同じ発音を、どの層でも同じatomにする方針である。
- 正しい読みは数字化後のcanon(`10 thirty`→num10,num30)に合わせており、既存の`_clock_pair`をそのまま再利用している。
- 案A(多義展開)・案B(文脈語辞書)を不採用とした論理も妥当。

ただし、scratch差分(CANDIDATE_C_01.diff)にはコードを読んで見つけた退行(PASS→NG)が2件あります。matrixにもreplayにも出てこない型なので、修正が必要です。

### 必須修正
- **OF-TN-01(後続語の処理が抜ける退行)**: `_try_clock_pair`は分のatomに`_apply_suffixes`を適用しません。分の直後のpercent/per cent/通貨語がliteralとして残ります。
  - 例: canon `10 twenty-dollar bills`(er003がtenを数字化した形)↔ASR `10 $20 bills`。修正前はTier1でEQUAL、案CではDIFFになり誤NG。`2 fifteen percent`↔`2 15%`も同型。
  - 修正: 分の直後が`percent`/`per cent`/`_CURRENCY_WORDS`ならNoneを返す(時刻ではない)。X系の金額題材(coffee_prices等)で実際に起こり得ます。
- **OF-TN-02(am/pmが付く場合の退行)**: canon `At 10 thirty pm`↔ASR `At 10 30 pm` は、修正前は両側[10,30,lit pm]でPASSでした。案Cではcanonだけがtime(pm)になり、vgの`_clock_pair`はam/pm付きを対象外としているため、DIFFで誤NGになります。
  - 修正: am/pmが直後に続く場合に限り、分に2桁数字(10〜59)も受け付け、両側をtime atomに揃える。`ten thirty pm`↔`10 30 pm`(現行でも誤NG)も同時に解消します。
- **OF-TN-03(and直後の除外が広すぎる)**: 直前語チェックが`and`(`_NUMBER_VOCAB`に含まれる)でも除外するため、`between 9 and 10 thirty`↔`between nine and ten-thirty`が従来の年読みに戻ります。数字化側との不一致で誤NGが残り、`and ten thirty`↔`and 1030`の誤PASSも残ります。
  - 修正: `and`は、その直前が数詞語・scale語・数字のときだけ除外する。
- **OF-TN-04(er109を含めた全経路での確認)**: TEST_MATRIXは`judge_sim`(Primary 1本)で、er109(同音救済)のX/Z scopeを通していません。案Cで、これまでTier1 PASSだった#21/22/42/67/68はvgでDIFFになり、初めてer109が評価される経路に入ります。
  - X/Z scopeをONにした正式経路で、これらがRESCUEされないことを固定testにする。特に#22(`At 1030`↔`At ten thirty`)は、er109の承認規則`1030`↔`10:30`(両方を「ten thirty」と読む)と隣り合うため要注意。
  - もしRESCUEされる場合は、既存承認規則とユーザー指示②-2の衝突になるので、実装を止めてFableへ報告する。
- **OF-TN-05(回帰の確認)**: 依存のある環境で`run_project_regression.py`を全件PASSさせる。pairsを再抽出してreplayをやり直し、judge PASS→NGと分類層PASS→NGがともに0であることを確認する。いずれも実装・Production配線の前の必須条件。
- **OF-TN-06(残る誤NGの開示)**: 次の2点を完了報告・OPEN_ITEMSに明記する。
  - 論点2の帰結(後述)。
  - matrix #72/73(`At 10 thirty 5`↔`At 10:35`)。F-1由来で、案C後も時刻の誤NGとして残る。「2件解決」と報告するときに、時刻の誤NGがゼロになったと誤解されないようにする。

### 論点別
1. **正当性: 承認**。3層の時の範囲が違う点(er006=境界分割/`_clock_pair`=0〜24/案C=1〜12)は意図的な差として許容してよいです。`_clock_pair`が相手にする数字の2atomには24時間表記があり得ますが、語形の側は年号を守るため1〜12に絞る必要があります。値の共通化は不要です。ただし分の範囲10〜59は共通定数にし、各箇所に理由をコメントすることを推奨します(必須ではありません)。
2. **年号: ユーザーの事前判断は不要。完了報告での明示は必須(OF-TN-06)**。理由は次のとおりです。
   - (a) 範囲を狭める案(時10〜12を除外)は、ユーザー例`ten thirty`(時10)そのものを再び壊すため採用できない。文脈を使わない規則で②-2を満たす限り、`twelve fifteen`↔`1215`は`ten thirty`↔`1030`と同じ扱いにするしかない。②-2をそのまま一般化した帰結であり、AIが独自に基準を変えるものではない。
   - (b) 本文canonでは、er003がten/eleven/twelveを数字化する(`12 fifteen`)。そのため本文経路では、語形↔桁連結の組は**修正前から既にDIFF→NG**だった(#23と同型)。案Cは、KP英語と純語形の経路をこれに揃えるだけ。
   - (c) 方向は安全側(誤NG→次slot/HR。誤PASSは生じない)。replayでは該当0件。
   - 実害がわずかに残るのは、canonが数字の年号`1215`で、ASRが語形`twelve fifteen`を返すケースです。報告では、救済したい場合は「年号文脈の例外を設ける選択肢があるが、案Bと同じく辞書型の例外になる」と添えてください。
3. **誤PASS: 新規の誤PASSは見当たらない(上記修正後)**。確認した内容は次のとおりです。
   - 時刻同士: `ten thirteen`/`two thirty`/`seven fifteen`↔取り違えた時刻はいずれも値の差でDIFF。am/pmの違いはmeridiemの差でDIFF。`one`のsoft_one化は、修正前のliteral oneと結果が同じ。
   - `one fifty`↔`1:50`(金額)や`chapter eleven fifty`↔`11:50`はEQUALになるが、どちらも同じ発音で、修正前もUNKNOWNでPASSだったため悪化ではない。
   - `10 thirty`↔`1030`はvgでDIFF、er109の救済対象は数字の`1030`だけ(OF-TN-04で確認)。
   - X-2の誤PASS(`one hundred thirty people`↔`1:30 people`)は現行のまま残る。
4. **Secondary・retry: 承認**。全経路が同じ`_tier1_atoms`/`_en_sequence`を通るので、再実行しても結果は変わりません。`ten thirty`↔`10:13`がP1になり、Secondary呼出の機会がなくなるのはD/C(納期・費用)の損失で、品質は下がりません。数字化canon(本文の大半)では既に同じ扱いなので、むしろ揃います。保存entryの再判定で結果が反転し得るのは`ten thirty`↔`1030`型だけで、これは意図どおりです。Secondary転写でTier1 PASSになる経路のtestを追加してください。
5. **範囲外所見: 別OPENとすることに同意**。
   - X-2: vgのUNKNOWN(kind_mismatch)をDIFFに引き上げるのは最終Gateの作用変更で、影響範囲が広い。本修正には含めない。
   - 24時間表記・分00〜09: 救済の追加にあたるため別件。
   - F-1: 根本原因が別(er003のTTS入力が`thirty five`の`five`だけ数字化する問題/分類層の読み)で、時刻に限らない。ただし時刻の誤NGとして残る(#72/73)ので、優先度を上げて並行着手を推奨する。修正の第一候補は、er006/er021の両方で「十の位の語+1桁数字」を合成数として読むこと(保存entryにも効く)。er003側の修正はTTS入力の変更になる。
   - 案Cの`thirty 5`分岐は、時刻の位置でだけF-1を部分的に救済する形です。そのまま残してよいですが、F-1の修正時に統合してください。
6. **検証: 現状では不十分**。OF-TN-01〜03の型がmatrixにもreplay(時刻の実対4件)にも無いためです。下の追加testと、OF-TN-04/05が揃えば十分と判断します。
   - runtime evidence計画は妥当です(`rejudge_with_current_judge`/`guard_entry`で既存entryを修正前後に再判定、新規TTSなし)。
   - c8の実対の記述が資料間で食い違っています。ROOT_CAUSEは`At 10 thirty`×`At ten-thirty`、PRODUCTION_PLANは`At ten thirty`×`At 10:30`です。両方を対象に含め、出所(slotとattempt)を明記してください。
7. **X/Z/A/B/Cへの波及: 承認**。er109_xz_scopeは同音救済のscopeであり、atom化の適用範囲は制限しないという理解で正しいです。
8. **見落とし**: 日本語側(`_guard_ja`)は`_tier1_atoms`を使わないので影響はありません。

### 追加すべきtest(実装委任へ転記用。期待 EQ=PASS系/NE=PASS不可/PIN=現行挙動を固定)
- `At 10 thirty pm`↔`At 10 30 pm` EQ、`At ten thirty pm`↔`At 10 30 pm` EQ、`At ten thirty pm`↔`At 10 30 am` NE(OF-TN-02)
- `10 twenty-dollar bills`↔`10 $20 bills` EQ、`2 fifteen percent`↔`2 15%` EQ、`3 twenty euros`↔`3 €20` EQ、`twelve fifty dollars`↔`$12.50` NE(OF-TN-01)
- `between 9 and 10 thirty`↔`between nine and ten-thirty` EQ、`between nine and ten thirty`↔`between nine and 1030` NE、`one hundred and ten`↔`110` EQ(OF-TN-03)
- 非Tier1 role(KP): `ten thirty`↔`1030` NE、`ten thirty`↔`10:30` EQ、`ten thirty`↔`10 30` EQ
- X/Z scopeでer109を含む全経路: #21/22/42/67/68 NE、#66 PIN(RESCUE)(OF-TN-04)
- Secondary: canon `At 10 thirty`/`At ten thirty`、Primary `10:13`→P1 PIN。Primary NG(他要因)→Secondary `10 30`でTier1 PASS EQ
- 年号の向き(b): `in 1215`↔`in twelve fifteen` NE(PIN、OF-TN-06で開示)、`in 2010`↔`in twenty ten` EQ、`in 1066`↔`in ten sixty six` EQ、`in 1905`↔`in nineteen oh five` PIN
- 後ろに名詞が続く形: `the 10 thirty bus`↔`the 10:30 bus` EQ、`the eleven fifteen train`↔`the 11:15 train` EQ(`_en_unit`が単位とみなさないことの確認)
- 1文に複数の時刻: `from 9 fifteen to 10 thirty`↔`from 9:15 to 10:30` EQ、`at 9 fifteen, 10 thirty`↔`at 9:15, 10:30` EQ(SequenceMatcherが2つの時刻を1つのreplace blockにまとめると`_clock_pair`が成立しない懸念)
- `ten thirty-five`↔`10:35` EQ、`ten-thirty a.m.`↔`10:30 a.m.` EQ、`one fifteen`↔`1:15` EQ、`one fifteen`↔`fifteen` PIN
- `ten oh five`↔`10:05` PIN、`ten o'clock`↔`10 o'clock` EQ

### 読んだファイル
- docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/{OPUS_REVIEW_REQUEST_01,DESIGN_01,ROOT_CAUSE_01,STRUCTURE_01,TEST_MATRIX_01,CANDIDATE_C_01.diff,PRODUCTION_PLAN_01}
- er021_en_asr_semantic_equivalence_production_01.py(l.60-136, 150-489)、er078_asr_value_guard_01.py(l.330-549)
未読: CURRENT_SPEC.md 2834-2835/2970、er078_asr_unified_judge_01.py、er006_preprod_hardening_01_validation.py、er109本体。OF-TN-04は、er109本体を読まずに残した確認事項です。