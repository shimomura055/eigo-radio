# ER-003-CROSSLEVEL-AUDIO-03 実行報告(A2音声・英文品質再監査 + Cross-level音声仕様改善)

**管理ID: ER-003-CROSSLEVEL-AUDIO-03**
**実施日: 2026-08-10**
**ステータス: `PHASE 1-2 COMPLETE`(監査+小規模試作のみ。完成音声の全面再assembleは未実施)**

指示どおり、Phase 1(監査)・Phase 2(小規模試作)のみを実施した。A01/A02/ADD03の
完成音声は全面再assembleしていない。試作クリップの比較は
[Artifactプレーヤー](https://claude.ai/code/artifact/83ed1162-bd31-4e8c-952d-2d16f76bcdbd)
で試聴できる。

## 1. Come onの本文上の意味

A01 Point Two: **"Striker Lautaro Martínez came on in his place."**
サッカー用語で「途中出場する(交代選手として入る)」の意味。日常会話の
「こっち来い/急げ」という掛け声・命令の意味ではない。

## 2. Go aheadの本文上の意味

A01 Full Story Part 1: **"England went ahead in the 55th minute."**
サッカー用語で「得点してリードする」の意味。「(先に)どうぞ」という
許可・譲歩の意味ではない。

## 3. 現行音声が別prosodyになった原因仮説

**分類: 意味文脈の欠落(TTSへ単独フレーズしか渡していない)。**
ハルシネーション・language routing誤り・日本語pipeline混入ではない
(ASR内容はいずれも正しく"Go ahead."/"Come on."と転記されている)。

Come on・Go aheadは、いずれもTTSへ本文から切り離した2語だけを渡して
おり、意味を確定させる文脈情報が一切ない。この状態でモデルは、
最も一般的で頻度の高い口語義(Go ahead=許可、Come on=掛け声・命令)を
デフォルトのprosody(強勢・イントネーション)として選んだ可能性が高い。

補強証拠: Go aheadの現行採用版(語末音素試作版)は標準版より発話時間が
長い(1.011秒 vs 0.791秒)。語末音素試作instructionは「語末まで言い切る」
ことのみを指示しており意味文脈を含まないため、意味の誤りは解決せず、
むしろより強調された(=より命令調に近い)prosodyになった可能性がある。
これは「語末音素対策と意味prosody対策は別軸である」ことの具体例。

## 4. context-aware発音候補の比較

新規instruction(本文中の実際の意味・品詞・用法を明示し、「命令・招待
ではなく、スポーツニュースの淡々とした事実描写として話す」よう指定)で
試作生成した。

| | 現行(標準) | 現行(語末音素試作、Go aheadのみ採用中) | 試作(文脈グラウンディング) |
|---|---|---|---|
| Come on | 0.751秒 | (試作対象外) | 0.711秒 |
| Go ahead | 0.791秒 | 1.011秒 | 0.731秒 |

いずれも試作版が最短(=より落ち着いた、命令調でない発話である状況証拠)。
ASR内容はすべて正しい。**ただし発話時間だけではprosodyの正しさを証明
できない。最終判断はユーザー試聴。**

## 5. 語末音素QAとの違い

今後、Key Phrase品質を2つの独立した軸で管理する(Decision候補として記録):

| 軸 | 内容 | 例 |
|---|---|---|
| **Segmental accuracy**(既存) | 音素そのものが脱落・誤発音していないか | feedの/d/、optの/t/ |
| **Contextual prosody**(新規) | 意味・用法に合った強勢・イントネーション・リズムか | Come on、Go ahead |

一方のPASSが他方を保証しない実例: Go aheadは語末音素上は問題なし
(語末子音脱落リスクなしと判定してもよいはずだが、実際には語末破裂音
/d/を含むため語末音素試作の対象になっていた)にもかかわらず、意味
prosodyには別の問題があった。両軸は独立して評価する必要がある。

## 6. Brent crude oil / oil調査結果

`oil`単体・`crude oil`単体・`Brent crude oil`(3回再生成)を生成し比較した。

| 対象 | 結果 | duration |
|---|---|---|
| oil単体 | "Oil." | 0.591秒 |
| crude oil単体 | "Crude oil." | 1.051秒 |
| Brent crude oil(1回目) | "Brent crude oil." | 1.431秒 |
| Brent crude oil(2回目) | "Brent crude oil." | 1.591秒 |
| Brent crude oil(3回目) | "Brent crude oil." | 1.411秒 |
| 文脈グラウンディング試作版 | "Brent crude oil." | 1.491秒 |

3回とも内容は完全に正確(hallucinationなし)。durationのばらつき
(1.41〜1.59秒)は通常のTTS生成揺らぎの範囲内で、明確な機械的欠陥は
見つからなかった。文脈グラウンディング版もdurationに大きな違いは
見られなかった。**oil単体で生じている現象と断定できる客観的証拠は
得られておらず、3節・4節と同じ「孤立フレーズ生成によるprosody不安定」
の一種である可能性が高いが未確定。** 最終判断はユーザー試聴。

## 7. In One LineのTTS routing調査

**結論: language routing誤りではない。** 英語TTSモデル
(gemini-2.5-pro-preview-tts)で正しく生成されていた。

原因は、全ての英語ナレーション生成で共通利用している指示文
(`er002_common.py`の`COMMON_BASE_INSTRUCTION`と`POINT_LABEL_FIDELITY_RULE`)
に、以下の指示が**重複して2箇所**含まれていること:

> Clearly say "In One Line" before reading the final section.

この指示は、元々B1のような「記事全体を1回のTTS callで生成し、
"## In One Line"という見出しテキスト自体が入力に実在する」設計向けに
書かれたもの。A2はセグメント単位で生成し、In One Lineセグメントには
見出しテキスト自体を含めていない(3文の本文のみを渡している)。その
ため、モデルがこの指示に忠実に反応し、入力にない見出し
"In One Line"を幻覚的に発話することがある。

**ASR証拠**: ADD03のIn One Line音声で実際に発生(ja-JP ASR:
「インワンライン」、en-US ASR:「ING 19」という転記で検出)。A01・A02
では発生しなかった(**確率的な現象**、既出の"opt out"・"Now the full
story."のhallucinationと同種のパターン)。ASRのstrict検証(部分一致+
長さ上限)は、この余分な発話が短いため長さ上限をすり抜けてしまい、
検出できていなかった。

## 8. language routing一般化案

**再分類: 「language routing」ではなく「instruction scope漏れ
(body-level指示のsegment-level再利用による幻覚見出し)」。**

修正候補として、A2のsegment単位生成専用に、以下の指示を追加する
(既存の`COMMON_BASE_INSTRUCTION`等の共有・凍結モジュールは変更しない):

> Important: only speak a title, heading, or label such as "Point One,"
> "Point Two," or "In One Line" if that exact text is already written in
> the passage below. Do not announce, introduce, or add any heading or
> label that is not literally present in the text you are asked to read.

ADD03のIn One Lineテキストで3回再生成し、**3回とも幻覚見出しが再現
されないことを確認済み**(Point One/Two側は見出しテキストが実際に
本文に含まれているため、この追加指示があっても動作に影響しない=
副作用なし)。

この追加指示は、A2のFull Story/Points/In One Lineの全segment生成へ
一般適用できる候補として記録する(`ER-003-LANGUAGE-ROUTING`)。

## 9. `added more time`の自然さ評価

**現行**: "The referee then added more time."
文法的に正しく意味も通じるが、放送・ニュース英語としてはやや一般的
すぎる表現。

| 候補 | 評価 |
|---|---|
| "The referee added extra time." | **不採用推奨**。"extra time"はサッカーでは公式に「延長戦」を指す別概念(ロスタイムとは別物)であり、意味が変わってしまうリスクがある |
| "The game went into added time." | 採用候補。"added time"はロスタイム/アディショナルタイムを指す標準的な放送用語で、意味的に正確 |
| "The referee then allowed added time." | 採用候補。原文の構造(the referee主語)を保ちながら、より正確な用語へ差し替え |

A2としての平易さも考慮すると、"added time"という用語自体は"stoppage
time"より短く分かりやすいため、A2適性を損なわない。**修正案として
記録するのみで、本文へは反映していない**(ユーザー判断待ち)。

## 10. A2全文script監査結果

A01/A02/ADD03の最新A2本文(Full Story・Points・In One Line)を、
Grammar/Idiomaticity/News narration/Meaning preservation/A2
suitability/Spoken-firstの6観点で確認した。大半の文はPASS。
SHOULD_REVISE 5件、OPTIONAL_IMPROVEMENT 6件を検出。

## 11. SHOULD_REVISE一覧

| Article | Current | Suggested | Reason | Difficulty impact |
|---|---|---|---|---|
| A01 | "Rogers sent the ball across the front of goal." | "Rogers crossed the ball into the box." | Idiomaticity/News narration — サッカー実況として非慣用的な言い回し | 影響なし(crossed/boxは平易) |
| A01 | "Messi sent the ball across goal from the right." | "Messi crossed the ball from the right." | 上と同一パターンの繰り返し(系統的な問題) | 影響なし |
| A01 | "The referee then added more time." | "The referee then allowed added time." (9節参照) | News narration — 用語としてやや一般的すぎる | 影響なし |
| A02 | "During that time, apps under the plan would not open at first." | "During that time, apps under the plan would be switched off by default." | Meaning preservation — 「最初は開かない」と誤読されるリスク(意図は「既定でオフ」) | 影響なし(default概念は直後で説明済み) |
| ADD03 | "Oil prices fell after Trump dropped the plan... The day before, Brent crude oil rose..." (段落全体) | 時系列を7/13→7/14の順に並べ替える、または日付参照をより明示的にする | Spoken-first — 「値下がりした」の直後に「前日は値上がりしていた」という回想構造は、音声のみで追うと時系列が混乱しやすい | 影響なし(構成の並べ替えのみ) |

## 12. OPTIONAL改善一覧

| Article | Current | Suggested | Reason |
|---|---|---|---|
| A01 | "He helped Enzo by finding him in a good place." | "He helped Enzo by finding him in space." | やや冗長 |
| A01 | "Lautaro Martínez put it into the goal with his head." | "Lautaro Martínez headed it into the goal." | より簡潔・慣用的 |
| A01 | "It can win two World Cup titles in a row." | "It could win back-to-back World Cup titles." | 助動詞のニュアンス・語順がやや不自然 |
| A01 | "It moved more players near its own goal." | "It pulled more players back to defend." | やや直訳的 |
| A02 | "The apps would also stop feeds that pick posts for each person." | (現状維持でも可) | 軽微な冗長さのみ |
| ADD03 | "A full Very Large Crude Carrier is a very big oil tanker." | (現状維持でも可) | 技術用語+直後の言い換えで許容範囲 |

**いずれも本文へは反映していない。** 難易度を上げる方向の修正(idiom復活・
B2語彙復活・長文化)は含めていない。

## 13. 過去の音声速度仕様監査

リポジトリ全体を、以下5分類で調査した。

| 分類 | 内容 | 結果 |
|---|---|---|
| A. 明示的TTS speed parameter | speaking_rate等のAPI引数 | **存在しない**。使用中のGeminiクライアント(`er002_gemini_client.py`)の`SpeechConfig`にも速度パラメータは実装されていない |
| B. prompt/style速度指示 | "natural pace"等の自然文指示 | COMMON_BASE_INSTRUCTIONに「物語の展開に応じてpaceを上下させる」という趣旨の記述のみ。数値指定は`assert_no_wpm_specification()`で明示的にガードされ禁止されている |
| C. post-processing time-stretch | 音声生成後の速度変更処理 | **実装なし**(該当モジュールなし) |
| D. 文書上のみに存在するtarget | 数値目標が仕様書等にのみ存在 | `levels.py`(`generate_test.py`/`tts_test.py`という**別の無関係なレガシー番組専用**の設定)に、CEFR別wpm目安表(A2: 105-115wpm)が存在する。これは以前の監査(ER-003-A2-00、2026年8月)で「English Your Wayの正式A2仕様として採用された事実は一度もない」と明記済みの既知の混同リスクであり、ユーザーが記憶している「狙いの速度」はこの数値を指している可能性がある |
| E. 実測WPM | 過去に実測された記録 | 見当たらない(今回15節で初めて実測) |

## 14. B1/B2/A2現在のspeed制御実態

**B1・B2・A2のすべてで、明示的な速度制御は一切行われていない。** 3レベルとも
同一のTTSモデル・同一の指示文(pace言及はあるが数値指定なし)を使用しており、
現状では「レベルごとに異なる速度」という仕組み自体が存在しない。

## 15. 現行A2実測WPM

| 記事 | 英語語数 | 音声長 | WPM |
|---|---:|---:|---:|
| A01 | 369語 | 142.2秒 | **155.7** |
| A02 | 377語 | 150.8秒 | **150.0** |
| ADD03 | 410語 | 171.0秒 | **143.8** |
| **A2平均** | | | **約150** |

(Full Story Part1/2・Point One/Two・In One Lineの英語部分のみを集計。
Comment・Preview等の日本語部分は含まない)

## 16. B1との比較

| 記事 | B1語数 | B1音声長 | B1 WPM |
|---|---:|---:|---:|
| A02 | 377語 | 166.4秒 | **135.9** |
| ADD03 | 389語 | 168.2秒 | **138.7** |
| **B1平均** | | | **約137** |

**重要な発見**: A2(平均約150 WPM)は、B1(平均約137 WPM)より**速く**
読み上げられている。A2の文が短く簡単になった一方で、区切られたセグメント
単位で生成しているため呼吸・間の取り方が変わり、結果としてB1より速い
ペースになっている可能性がある。文法・語彙が易しいレベルの方が音声は
速いという、直感に反する逆転現象が起きている。

**0.9倍の意味**: 現行A2平均WPM(約150)を0.9倍すると約135 WPMとなり、
これはB1の現行速度(約137 WPM)にほぼ一致する。つまりユーザーが提案した
「0.9倍」という数値は、恣意的な値ではなく、**A2をB1と同程度の自然な
速度へ揃える**という合理的な目安になっている。

## 17. A2 0.9x候補の生成方法

優先順位に従って検討した。

1. **TTS modelが自然にspeed controlできる正式手段**: 調査の結果、
   使用中のGemini TTSクライアントには話速パラメータが実装されておらず、
   **利用不可**と判断した。
2. **style/promptで安定制御可能か比較**: 試作した(18節)。方向性は
   機能したが、精密な制御は困難だった。
3. **高品質なtime-stretch**: 未実施(2の結果を踏まえ次回検討)。

## 18. A2速度比較音声

A02のFull Story Part 1(108語・現行48.0秒・134.9 WPM、目標0.9x=121 WPM)で
減速instruction("noticeably slower... genuinely slower, not just with
added pauses")を追加生成した。

| | duration | WPM | 対現行倍率 |
|---|---:|---:|---:|
| 現行 | 48.0秒 | 134.9 | 1.0x |
| 目標(0.9x) | 53.4秒 | 121.4 | 0.9x |
| 試作版(実測) | 77.4秒 | 83.7 | **約1.61x(狙いより大幅に遅い)** |

**結果**: promptによる減速指示は方向性としては機能した(数値指定なしでも
実際に遅くできることを確認)が、狙いの0.9倍を大きく超えて減速してしまい、
精密な制御ができなかった。**この指示文のままでは採用できない。** 次回は
より弱い表現("just a little slower"等)での再試作、またはtime-stretch
との比較が必要。

## 19. Pause 0.8秒変更案

Point One→Point Two、In One Line→Outroのポーズを、現行0.5秒から0.8秒
(+0.3秒)へ変更する案を、**次回assembleの候補として記録した**。
今回は実際の完成音声への反映(=全面再assemble)は行っていない。

## 20. Outro追加減衰量

CROSSLEVEL-AUDIO-01/02で採用したv2版(Introの調整後RMSへ一致させた上で
振幅×0.6903を適用済み)から、**さらに**同じ考え方(心理音響上の目安
「10dBの増減で知覚音量が倍/半分」)で追加減衰量を算出した。

- 追加減衰: `10 × log2(0.8) ≈ -3.22dB`、振幅倍率 `10^(-3.22/20) ≈ 0.6903`
  (v2版に対してさらに乗じる)
- Introを基準とした複合の知覚音量比: 0.8×0.8 = **0.64**(約-6.44dB、
  振幅×0.4765)

単純な振幅0.8倍ではなく、v2版と同じ心理音響ベースの計算式を再利用した
(新しい計算式は設計していない)。

## 21. Outro比較候補

A01完成音声のOutro区間(6.144秒)を切り出し、v2版とv3版(さらに減衰)を
[Artifactプレーヤー](https://claude.ai/code/artifact/83ed1162-bd31-4e8c-952d-2d16f76bcdbd)
で比較試聴できるようにした。

## 22. Cross-level / A2固有の分類

| 課題 | 分類 | Source of Truth ID |
|---|---|---|
| Key Phraseのcontextual prosody(Come on/Go ahead/Brent crude oil) | Cross-level候補(A2/B1/B2共通、Key Phraseを持つ全レベルに適用可能) | `ER-003-PRON-CONTEXT` |
| In One Line幻覚見出し(instruction scope漏れ) | Cross-level候補(全レベルのsegment単位英語生成に共通のリスク) | `ER-003-LANGUAGE-ROUTING` |
| A2英文のnaturalness(added more time等) | A2固有(A2化に伴う簡略化が原因) | `ER-003-A2-SCRIPT-QA` |
| Pause 0.8秒(Point One→Two、In One Line→Outro) | Cross-level候補 | 既存`OPEN-25`を拡張 |
| Outro追加減衰(体感0.64) | Cross-level候補 | 既存`OPEN-26`を拡張 |
| A2速度0.9x | A2固有(B1/B2は現状維持と明示決定済み) | `ER-003-A2-SPEED` |

## 23. OPEN_ITEMS更新

新規4件(OPEN-29〜32)を追加した。詳細は[OPEN_ITEMS.md](OPEN_ITEMS.md)参照。
いずれも`CANDIDATE`/`UNDER_INVESTIGATION`止まりで、`DECIDED`への昇格は
行っていない。

## 24. 作成・変更ファイル

- 新規: `er003_output/crosslevel_audio_03/investigation/`以下の調査・試作音声とJSON結果
  (`brent_oil/`, `context_aware_kp/`, `in_one_line_fix/`, `speed_test/`, `outro_further_attenuation/`)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)
- A01/A02/ADD03の既存完成音声・組立スクリプト・B1/B2既存資産・共有凍結
  モジュール(`er002_common.py`等)はすべて無変更

## 25. テスト結果

コード変更を伴わない調査・試作段階のため、新規テストコードの追加・実行は
行っていない(既存の`generate_key_phrase_component_verified`等、確立済み
関数の再利用のみ)。

## 26. Git status

音声ファイル(`.wav`/`.mp3`)は`.gitignore`により追跡対象外。調査結果JSON・
レポート・OPEN_ITEMS更新のみをcommit対象とする。

## 27. commit

コミット済み(詳細はcommitログ参照)。

## 28. push未実行確認

**pushは実行していません。**

## 参照元

[OPEN_ITEMS.md](OPEN_ITEMS.md)、[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)(過去速度仕様監査の一次情報源)
