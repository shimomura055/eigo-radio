# DESIGN_01 FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-02 委任_01(2026-10-13、設計・見積のみ。TTS/LLM/ASR呼出なし、費用JPY0、Production無変更、生成未実施)

目的: 前回8way Trialでユーザーが高評価したH Take1の声質(明るさ・明瞭さ・抑揚・自然なつながり)を保ち、話速を少し抑え、take間の速度ばらつきを小さくする。現行v5比較も継続。Status到達可能: VALIDATED/REJECTED/UDR。

## 1. 背景の実測(MEASUREMENTS_02.md)
- H: Std T1 157.3/T2 169.0、Adv T1 166.9/T2 187.5 WPM。Adv T差20.6、Std T2はASR警告(said→says/organisation=TRUE_CONTENT_MISMATCH判定、聴感確認対象)。
- 速度が速すぎる系: E(Adv 196-202)、D(Adv T2 200.9)。安定系: C Std(T差0.6)、D Std(0.4)。A(unhurried重複)は文末無音が多く(Adv平均654/576ms)現行v5に近い間増加。
- 現行v5参考: Std 145.5 / Adv 166.9 WPM。Hは現行v5より速い。目標はHの速度をv5〜H T1の範囲(Std約150-160/Adv約165-175)に収め、180を目的にしない。

## 2. 設計原則
- 各候補はPrompt全体を一から簡潔に書き直し(H0を部分文字列に含まない: assert済)。追記・言い換え重複なし。速度の制御方法のみを変える。語数は短く明確を優先し20-37語(推奨40-55語の下限未満だが、指示の重複を避けた結果。H5は最小性が設計意図のため例外)。
- 全候補共通の声質核: warm/clear/credible/smile in the voice(H0の良い特性)。H0〜H5に`unhurried`/`slowly`は含まない(自動検知=全てFalse)。

## 3. H0〜H5 Prompt全文

| ID | 語数 | 文数 | sha256(先頭12) | 速度制御方式 |
|---|---|---|---|---|
| H0 | 37 | 2 | 49af7437080d | 速度指示なし(息継ぎ指示のみ) |
| H1 | 37 | 2 | 254f038bafe4 | 名詞句で速度基準を明示(natural, steady news-broadcast pace) |
| H2 | 32 | 2 | 0d1ca2881b60 | テンポ語1つ(calm conversational tempo)+流れの接続1つ(flow into the next) |
| H3 | 34 | 2 | ea4e95c46d8a | 否定形の緩い抑制1つ(without rushing) |
| H4 | 34 | 2 | f25beb1e27e5 | リズム一定の指示1つ(one even rhythm) |
| H5 | 20 | 1 | e0200b75c0df | 速度指示なし(persona の『composed』のみが示唆) |

### H0: 前回H完全同一(Baseline、Take1/2再利用+Take3新規)
- Prompt全文(逐語): `A warm, composed daytime radio news presenter telling a human-interest story: clear, credible and approachable, with a smile in the voice. Group words into meaningful phrases, keep the phrasing smooth and connected, and breathe naturally between ideas.`
- 語数37/252字、sha256 `49af7437080d2d216d854f316f7820ec0a9ec74ada52fd99f00c079b6dd60dd7`
- 設計意図: 前回高評価Take1の再現基準。速度指示なし、『breathe naturally』のみ。
- 想定副作用: 前回実測: Adv T差20.6、Std T2 ASR警告。速度ばらつきが課題。

### H1: 自然なニュース朗読速度を明示
- Prompt全文(逐語): `A warm daytime radio news presenter sharing a human-interest story, clear, credible and approachable, with a smile in the voice. Read at a natural, steady news-broadcast pace, grouping words into meaningful phrases and breathing only between ideas.`
- 語数37/248字、sha256 `254f038bafe4a7b82aeff22e46d197440588cd71060147cc3b6548f70f7eae8f`
- 設計意図: 速度の基準を『報道の標準朗読速度』という既知の話し方に固定し、Hの声質文は短縮のみで維持。
- 想定副作用: 報道調が硬さを増し明るさ低下の恐れ。news paceが元々速い基準で速度が下がらない可能性。

### H2: 落ち着いた会話テンポ
- Prompt全文(逐語): `A bright, friendly radio presenter telling a human-interest story to one listener in a calm conversational tempo. Keep the voice clear, credible and smiling, and let each phrase flow into the next.`
- 語数32/197字、sha256 `0d1ca2881b6097122cdd4e5ec10801b7528e8e2702342709dd8ee51876d7962d`
- 設計意図: キャスター像を『1人のリスナーへの会話』に置換し、テンポをcalm conversationalで指定。8wayでC/G(会話系)のStdのT差が小さかった点を根拠にする。
- 想定副作用: 会話調になり報道の信頼感(Hの核)が薄れる恐れ。Gのように熱量不足の懸念。

### H3: 急がず、意味の変わり目でのみ間
- Prompt全文(逐語): `A warm radio news presenter with a smile in the voice, clear and credible. Tell this human-interest story without rushing, linking each phrase smoothly to the next and pausing only where the meaning changes.`
- 語数34/207字、sha256 `ea4e95c46d8a6c596a30349c9c2cb65c7000cf00d6629514d0368d9f156cfe50`
- 設計意図: 速度を否定形1語(without rushing)で穏やかに抑え、間は肯定形『meaning changesでのみ』に限定。A(unhurried重複で間増加)の轍を避け、減速語は1回のみ。
- 想定副作用: 8wayでAのunhurried系が文中/文末無音を増やした前例。単発でも間増加・語尾の伸びの恐れ(リスク最大候補、検知対象)。

### H4: 文章全体のリズム均一化(take間ばらつき対策)
- Prompt全文(逐語): `A warm radio news presenter telling a human-interest story, clear, credible and smiling. Hold one even rhythm from the first sentence to the last, with phrases grouped by meaning and breaths only between ideas.`
- 語数34/210字、sha256 `f25beb1e27e549570283af9cfe4d13164b8909b1dd62524cf5052ad3e5544b36`
- 設計意図: 速度の絶対値ではなく『最初から最後まで一定のリズム』を指定し、文ごとの加速・減速(take間差の主因と推定)を抑える。
- 想定副作用: 平板・機械的に聞こえる恐れ(抑揚低下)。速度の絶対値は動かず、全体が速いまま均一化するだけの可能性。

### H5: 最小限(速度指示なしでTTSに委ねる)
- Prompt全文(逐語): `A warm, composed radio news presenter telling a human-interest story: clear, credible and approachable, with a smile in the voice.`
- 語数20/130字、sha256 `e0200b75c0dffe33522f04cda7a8d31f9debb5dd55c8415719914492a8bdf988`
- 設計意図: H0から語句構造指示(Group words/phrasing/breathe)を全て外し、声質像のみ。速度・間はモデルの自然な読みに委ねる(D最短の知見の再検証、ただし声質像を維持)。
- 想定副作用: 8wayのD(最短)はAdv T差19.5で不安定。H0と同等以上に速い/ばらつく可能性。語数は40未満(短さ優先の例外)。

## 4. 自己点検表(重複・矛盾・冗長)

| 候補 | 速度指示の数 | 間の指示との矛盾 | Hの声質要素 |
|---|---|---|---|
| H1 | 1つ(natural, steady news-broadcast pace) | 矛盾なし(息継ぎ=ideas間のみ) | warm/clear/credible/approachable/smile 全保持 |
| H2 | 1つ(calm conversational tempo)。flow は接続指示で速度語ではない | 矛盾なし | bright/friendly/clear/credible/smile。warmはfriendlyで代替、approachable脱落(会話像で含意) |
| H3 | 1つ(without rushing) | 矛盾なし(pause only where meaning changes は意味上の間を残す) | warm/clear/credible/smile。approachable脱落 |
| H4 | 0〜1(one even rhythm=リズム均一、絶対速度語なし) | 矛盾なし | warm/clear/credible/smiling。approachable脱落 |
| H5 | 0(速度指示なし) | 間の指示なし(矛盾なし) | warm/composed/clear/credible/approachable/smile 全保持 |

- H0: 前回H逐語(自己点検対象外、Baseline)。冗長・重複・追記なし。
- 冗長チェック: 各候補とも同一目的の指示は1つ(声質=1文、速度/リズム=1句、間=1句以内)。`slowly/unhurried`重複なし。

語彙Jaccard(類似度、token):

| 組 | Jaccard | 組 | Jaccard |
|---|---|---|---|
| H0-H1 | 0.558 | H0-H2 | 0.319 |
| H0-H3 | 0.333 | H0-H4 | 0.354 |
| H0-H5 | 0.576 | H1-H2 | 0.26 |
| H1-H3 | 0.354 | H1-H4 | 0.347 |
| H1-H5 | 0.472 | H2-H3 | 0.364 |
| H2-H4 | 0.298 | H2-H5 | 0.371 |
| H3-H4 | 0.34 | H3-H5 | 0.471 |
| H4-H5 | 0.378 |  |  |

- H0との類似: H1 0.558 / H5 0.576(声質核を共有するため高め。H1は速度句の有無、H5は構造指示の有無で別設計)、H2 0.319 / H3 0.333 / H4 0.354。H1-H5間最大 0.472(H1-H5, H3-H5)。8wayは最大0.253だったが、本Trialは『同じHの声質核を維持しつつ速度制御だけ変える』ため、全組0.60未満を許容範囲とした(複製=末尾差し替えではない。文構造・語順は各々別)。

## 5. 生成計画
- 6候補×3 take×Std/Adv=36音声。再利用4(H0 Take1/2、Std/Adv。sha: Std T1 final 1a31805e1b29、Std T2 a1d93c4c7f59、Adv T1 1d2dd8480ab7、Adv T2 1c24820700ff、いずれ`er057_output/coffee_tts_style_8way_01/attempts/`、style sha 49af7437、tts_input sha Std 13740eca9a44/Adv 627f1c7f7771)。新規32 call(H1-H5×3×2=30+H0 Take3×2)。
- 条件: gemini-3.8-flash-lite-tts(最新世代、前回と同一でWPM比較の同一条件性のため据置)、Aoede、speech_metadata、同一原稿(Coffee Part1、tts_input shaを前回一致assert)、Std 6%減速適用(減速前wav保存)、無音カット・キャップなし、Primary ASR 1回(NGでも再生成せず警告)、既存異音検知、並列8、技術failure retry合計4まで、STOP/STOP_ALL確認、予算JPY60ハードストップ。
- 所要見込み: 約1分(8way 32call/並列8で50秒実績)+測定(local whisper)数分+ページ生成。直列化理由なし(全call独立)。1回起動、監督ループ・自動再試行ラッパなし。
- コード: `er057_coffee_tts_style_h_speed_02_{gen,measure,page,...}.py`(8way版を流用、委任_02で作成)。

## 6. 費用見積(上限JPY60)
- 8way実績JPY39.55/32 call(TTS 32.42+ASR推定7.13、出典`er057_output/coffee_tts_style_8way_01/cost_02.json`)→本Trial 32 callで中央JPY39.55、+20%でJPY47.46、技術retry 4 call分込みJPY53.39。
- 保守側(8way設計時の見積 high+retry)JPY57.55でも上限JPY60内。Promptは8wayのA(65語)より短く入力tokenは同等以下。出力token(音声長)が支配的でWPM増減で多少変動。詳細`cost_estimate_01.json`。

## 7. 評価設計
- ①速度: 各takeのWPM(ref語数Std117/Adv131÷尺)、候補×Lvの平均・最小・最大・最大差、最速takeの評価。基準=現行v5(Std145.5/Adv166.9)とH0 Take1(Std157.3/Adv166.9)。180 WPM達成のために現行より速くしない。目標目安: H0平均(Std163.2/Adv177.2)より低く、最大差を10未満。
- ②安定性: take間差、ASR警告、異音、末尾一致、3take中の外れ値。
- ③声質: H0 T1基準で明るさ・明瞭さ・抑揚維持。機械指標(RMS、F0レンジ/変動、発話WPM)は参考のみ。平坦/暗い/機械的/文末の伸ばし・語尾欠落は機械検知+ユーザー聴感が最終判断。
- ④不要な間: 文中・文末無音(-40dBFS/50ms以上)の本数・平均・最大・800ms超長無音、H0 T1とv5を基準。『間を減らす代わりに早口』を避けるため速度と無音をセットで判定。
- 足切りせず機械指標は参考表示。選抜はユーザー試聴。

## 8. 試聴ページ設計 `user_test/coffee_style_h_speed_02/index.html`
- 上部: 比較基準(現行v5 Std/Adv、前回H Take1 Std/Adv)の音声とWPM。
- 候補H0〜H5をカード表示。各カード: Prompt全文・語数・設計意図・速度制御方式。Std/Adv別に Take1(主表示、大)とTake2/3(再現性確認用、折畳み)。
- takeごとにWPM、文末/文中無音指標、警告(ASR/異音/末尾)。候補×Lvの平均・最大差サマリ表。スマホ簡素構成(縦1列、audio controls、折畳みdetails)。H0 Take1/2は前回と同一音声である旨を明記。生成後にPlaywrightで全音声再生evidence取得(8way踏襲)。

## 9. 停止点
- 本委任_01は設計のみ。生成は行わずSTOP。Fable確認(Opus条件の要否判断含む)後に委任_02。Production無変更、採用判断なし。
