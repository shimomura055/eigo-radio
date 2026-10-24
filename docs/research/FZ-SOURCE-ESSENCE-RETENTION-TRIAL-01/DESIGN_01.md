# DESIGN_01: Family Z「原作の語り口・本質」を上流で守る設計案(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_01 Phase 0)

作成: 2026-10-25 / Status: **設計案(Opus条件Aレビュー待ち・Trial実装前)** / API 0・コード変更0・Production変更0
根拠: `ROOT_CAUSE_01.md`(同ディレクトリ)。ユーザー原文§4(新たなCheck/Validator追加は基本不採用。上流で「そもそも損なう文章が生成されない」設計)に準拠。
`APPROVED_FOR_PRODUCTION`/`VALIDATED`/`PRODUCTION_WIRED`ではない。Trial成功時もProductionへ自動配線しない。

## 1. 要約(推奨1案)
**案A: 語り口を`source_essentials`の1欄(`narration_voice`)として構造化し、既存のessentials伝達経路(R0/R1/R2/Std調整の全段へ同一文字列を渡す機構)でそのまま運ぶ。同時にR1/R2の固定文言"in third person"を、essentialsがある作品に限りその欄への参照へ置換する。**
- 新規LLM呼出・Validator・Gate・retry・Human Reviewは追加しない(追加Prompt文は各段1行≒40 token)。
- 原作分析(Seed記入)の段で「語り口(人称・語り手の立場・聞き手との関係・語りの質)」を1文で記録→全段に同じ文が渡る→時間尺・語彙・構文を変えても語り口は動かさない契約になる。
- 語り口以外の「心理の質」(自己陶酔・恐怖を楽しむ心理・聞き手への呼びかけ)も、同じ1文で表現する(欄を増やさない)。

## 2. 案の比較
| 案 | 内容 | 上流性 | 汎用性 | 副作用 | 量産単価 | 評価 |
|---|---|---|---|---|---|---|
| **A(推奨)** | essentialsに`narration_voice`(1文)を追加→全段Must-keepに描画。REVISEの固定"in third person"は欄がある作品でのみ「Must-keepの語り口に従う」へ置換 | Seed(原作分析)→Writer契約→レベル別生成まで同一経路で伝達 | 全Z作品共通(三人称作品は"Third-person, close on X"等を1文書くだけ) | Prompt +約40 token/段。三人称作品は挙動不変が期待(Phase 2で確認) | ≒+0円(<0.05円/記事) | **採用提案** |
| B | `REVISE_USER_TMPL`から"in third person"を全作品で削除(語り口は前段本文から自然継承) | R1/R2のみ | 全Z共通 | 欄が無いので語り口の質(呼びかけ・自己陶酔)は守られない。Stdは無策のまま(偶然頼み)。既存全作品のR1/R2 Promptが変わる | 0 | 部分対策。Aの一部(固定文言除去)と重複するため単独採用せず |
| C | 人称判定Validator+不一致時retry/regenerate | 事後検出 | 汎用 | LLM/retry増・費用増・「作品ごとの例外」化しやすい | 増 | **不採用**(ユーザー原文§4) |
| D | conversion_plan(Seed全文)をR1/R2/Stdにも渡す | 経路新設 | 汎用 | 修正版Bで意図的に避けたアンカリング(自由度低下)・入力token増(R1入力≒1.4k→約3k)・essentialsと情報重複 | +約1円/記事 | 不採用(重複する仕組みを増やすため) |
| E | 一人称独白作品ではR1/R2をスキップしR0をAdvにする | 工程変更 | 作品別例外 | 「作品ごとの例外ルール」の増殖、R1/R2の他の効用(読み味改善)を捨てる | −約6円 | 不採用(ユーザー原文§4) |

## 3. 案Aの具体設計(Trialは全てDEV経路。Production file無変更)
### 3-1 Seedの記入規則(原作分析段の改善)
`seed.json`の`source_essentials`に**`narration_voice`(文字列、1〜2文、必須)**を追加。記入する内容は次の3点のみ(欄は増やさない):
1. 人称と視点(例: first-person / third-person close on X / omniscient)
2. 語り手の立場(聞き手への呼びかけの有無、語り手が物語内人物か、信頼できない語り手か、論評する語り手か)
3. 語りの質のうち「その作品の面白さそのもの」である1点(例: 狂気を帯びた過信と自己陶酔、冷静な皮肉、語り手の直接の論評)
- カウント: 維持必須要素の上限5件(`ESSENTIALS_MAX_ITEMS`)には**数えない**(語り口は枠であり、筋の要素ではない)。
- 記入の整合規則: `conversion_plan`の人称記述は`narration_voice`と一致させる(Seed作成手順の1行。人称の固定語句を含む既存`_CONVERSION_SUBSTITUTIONS`[`er062_family_z_writer_01.py:130-135`、"third-person English"という語句の置換]は人称を変えないが、一人称作品のSeedにこの語句を流用しないこと)。
- 例(『告げ口心臓』、案): 「First-person monologue by the unnamed narrator, who keeps addressing the listener as 'you'; his calm, proud, over-confident voice -- relishing his own cunning and the old man's terror while insisting he is sane -- is where the horror comes from. Keep the 'I' voice and the direct address; do not retell it in the third person.」
- 例(『賢者の贈り物』、Phase 2用の案): 「Third-person narration close on Della and Jim, with a warm, gently ironic narrator who comments on events.」(※完成版は変更しない。Phase 2のDEVコピーでのみ使用)

### 3-2 Writer契約(全段へ同一文字列)
`_render_essentials_block`(`er062_family_z_writer_01.py:403-433`)の思想どおり、全段のMust-keepブロックに1行追加:
`- Narration (keep exactly as in the original; do not change the person, the point of view or the narrator's stance, even when shortening or simplifying): <narration_voice>`
- mode=`full`(R0/R1/R2)・`std`(Std調整)の両方に描画。
- R1/R2の固定文言: `REVISE_USER_TMPL`(139-142行)の`in third person, `を、`narration_voice`が有る作品のみ`in the narration described in the Must-keep section below, `へ置換(既存の`_REVISE_NAME_SENT_KEEP`置換と同型の差し替え。assertで文字列の存在を確認)。欄が無い作品(Melos=essentials自体が無い)は従来とbyte同一。
- Std調整(`STD_PROMPT_TAIL`): 人称指示は元から無いので文言変更不要。Must-keep行の追加だけで、入力の語り口に依存せずStdも語り口を保つ(今回Stdが一人称に戻ったのは偶然)。

### 3-3 レベル別生成(時間尺・語彙・構文の調整)との関係
語り口は「枠」としてMust-keepで固定され、`free_to_cut`(圧縮可の枝葉)と衝突しない。『告げ口心臓』Seedの`free_to_cut`「narrator's repeated arguments that he is wise and cunning」は、語りの質(自己陶酔)の源泉になっているため、Seed記入の見直し(Phase 1のDEV Seedコピー)で「arguments(論の繰り返し)は圧縮可、ただし自信満々の語り口の1〜2例は残す」旨を`narration_voice`側へ寄せる(`free_to_cut`の語句は変更しない=1か所の記述にする)。

### 3-4 CPチェックリスト(確認の入口)
`build_cp_checklist`(817行)が生成する機械チェックリストに、`narration_voice`から**1行**(深刻度=重大、項目=narration、内容=`narration_voice`文、各stage本文の人称・呼びかけの引用欄)を追加。記入はFable CP(従来どおり)。自動判定・LLM検査・retryは追加しない。これは検出機構でなく、既存確認作業の入口の欠落補修。

### 3-5 fail-closed(Seed承認時)
`validate_source_essentials`(447-491行)に「`narration_voice`が非空文字列」を1項目追加(Seed記入規則の検査であり本文Validatorではない=`ESSENTIALS_EXEMPT_STORIES`と同型)。既存4作品(猿の手・開いた窓・二十年後・賢者の贈り物)のSeedへは**採用時に1行のdata追加**が必要(完成版・公開音声は再生成しない限り不変)。Trial中は既存Seedのコピーに追記して使う。

## 4. 影響範囲(採用時の判断材料。本Trialでは公開版不変)
- Production変更が必要になる箇所(採用承認後のみ): `er062_family_z_writer_01.py`の`_render_essentials_block`/`build_revise_prompt`(`REVISE_USER_TMPL`)/`validate_source_essentials`/`build_cp_checklist`、既存4作品のseed.json(1行追加)、`er062_family_z_source_essentials_test_01.py`・`er062_family_z_writer_01_test_01.py`・各story registry test(Seed fixtureの更新)。
- 既存の承認済みProduction Prompt(R1/R2の固定文言)の直接編集を含むため、PM_GOVERNANCE 11-7の限定例外の対象外=Offline Trial→VALIDATED→ユーザー正式採用→Production実装の順(`APPROVED_FOR_PRODUCTION`はユーザーのみ)。
- X/Y波及: `er062_family_z_writer_01.py`はZ専用(import元は`er026_family_z_*`・`er062_*`・Z関連testのみ。Xの`er003_*`はKP関連のtestでの参照)。X/Yの本文生成には波及しない。
- 既存Z作品の再生成: 不要(採用しても過去の完成版・公開音声は不変)。ただし今後同作品を再生成する際は、`narration_voice`未記入でfail-closedになるため、Seedへ1行追加が必要。再生成するかは別判断。

## 5. 評価計画
### 5-1 Phase 1(『告げ口心臓』Advanced、テキスト中心)
1a. **因果の再現確認(安価・A/B)**: 既存`r0.md`(一人称)を固定入力として、R1だけを2条件で各1回生成。(i)現行Production文言("in third person"あり)=反転の再現、(ii)案A=一人称維持。同一入力・R1のみのため、人称反転の原因がPrompt文言であることの切り分けになる(`ROOT_CAUSE_01.md`§6の反証の実行)。
1b. **全段チェーン**(r0→r1→r2→std、案A)を2サンプル生成(DEV出力dir)。Adv(Std併記)を評価。
1c. 合格ならAdvのみ音声化(TTS・gate・pages、既存の正式経路を再実行しない=本文だけ差し替えたDEV出力dir)。音声は文字での人手評価が良かった場合のみ。

決定論で測る項目(基準は事前固定):
| 指標 | 一人称作品の合格 | 三人称作品の合格 |
|---|---|---|
| M1 人称一致(ダイアログ除外の一人称語/三人称語、`you`の数) | Advの一人称語≥30かつ`you`≥2、Stdも同様(Adv/Std同一人称) | 一人称語≤2(ダイアログ除外)、Std/Adv同一 |
| M2 語数・テンポ | 330-470語(既存ACCEPT範囲)、平均文長・段落数が基準本文(現行Std/Adv)±ノイズ帯内 | 同左。ノイズ帯=同作品の既存複数run(例: 開いた窓r2=199〜232語、`run_pntrial/sftrial/sf_prod`)の実測幅 |
| M3 essentials保持 | CPチェックリスト9行(従来8行+narration)を引用で記入し、欠落0 | 同左 |
| M4 構造整合 | `speaker_table`で自白台詞等の話者が全てnarratorへ帰属(決定論+LLM判定の既存plan stageの結果を読むだけ、Adv本文のplanは不要=テキスト評価のみなら省略) | 同左 |

人手評価(Fable、盲検の比較: 現行Adv=r2、r0、案A Adv/Stdを順不同で提示)。観点(各0/1/2):
1. 一人称の語りが維持されている(語り手の「I」)
2. 聞き手への呼びかけ("you")が働いている
3. 主人公の異常な心理・執着(過信、自己陶酔、恐怖を楽しむ心理、被害妄想)が表現されている
4. 緊張の積み重ね(音の増大、沈黙、1時間動かない場面)が損なわれていない
5. 心臓音・自白に至る展開と因果が保持されている
6. 英語レベル(B1-B2/Std A2)と聞きやすさ(平均文長、段落)が維持されている
7. 物語としての面白さ(通読の総合評価。現行r2より明確に良いか、r0に並ぶか)
合格: 1〜5各2点かつ6・7が現行r2以上。

### 5-2 Phase 2(既存Z作品への横展開、テキストのみ)
選定(人称・語り口・会話量の多様性): 
- **賢者の贈り物**(三人称・語り手が論評する語り=語り手の立場を欄に載せた場合の効果と、完成版[ユーザー承認済み]との差の確認。※完成版は変更しない)
- **開いた窓**(三人称・会話中心。人名維持・オチの語り手の総括が既にessentialsにある=重複/過剰化の副作用確認)
- **猿の手**(三人称・ホラー・長め。Prompt追加によるテンポ劣化の確認)
(『二十年後』『メロス』は後続の追加確認候補。一人称原作は現状『告げ口心臓』のみ=汎用性は「三人称作品で挙動不変・副作用なし」と「語り口の質の指定が働くか」で確認する。)
各作品のSeed(DEVコピー)に`narration_voice`1文を追記→全段チェーン1サンプル→既存完成版(基準)と比較。副作用指標: 語数(ノイズ帯内か)、平均文長、段落数、essentials保持、人称不変、重複・冗長(Fable読み)。
合格: 全作品で人称・語り口が不変、essentials欠落0、語数・テンポ指標がノイズ帯内、盲検でFableが完成版より劣ると判断しない。

## 6. 費用見積(単価出典: 各`run_sf_prod_01/writer/provenance.json`の`chain[].cost_jpy`=実績。モデルはProduction同一=gpt-6.1-sol effort=high。最新世代推奨モデル原則に該当[Production同一モデル]、開発評価用途の例外なし)
| 項目 | 単価根拠 | 見積 |
|---|---|---|
| 1a R1のみ×2条件 | 『告げ口心臓』r1=2.82円 | 5.6円 |
| 1b 全段チェーン×2サンプル | r0 2.63 + r1 2.82 + r2 3.81 + std 6.84 = 16.1円/本 | 32.2円 |
| 1c Advのみ音声(任意) | `e2e_stage_log.jsonl`: tts_b1b段のspent差≒6.7円+gate/ASR込み | ≤12円 |
| Phase 2 賢者 | r0 2.34+r1 2.10+r2 1.95+std 6.09 | 12.5円 |
| Phase 2 開いた窓 | 2.26+2.09+1.93+6.35 | 12.6円 |
| Phase 2 猿の手 | 2.48+4.37+4.38+8.14 | 19.4円 |
| 再Trial予備(Phase 1チェーン1本) | 16.1 | 16.1円 |
| 合計(上限見込み) | | **約110円**(Fable案件上限150円・300円以下の自律枠内。LLM judgeや追加検査は使わないため評価費用0) |
- 日付分割・案件分割で境界を回避しない。見積が150円を超える見込みになった時点でFableへ報告(Phase 2を2作品に縮小する等)。
- 量産単価への影響: 追加LLM呼出0、追加Prompt約40 token/段×4段≒<0.05円/記事。目標70円/記事セットへの寄与は事実上0(Z記事は約40円/作品の実績、`cost_log`)。

## 7. 撤退条件・STOP条件・Production不変の保証
- 撤退/設計見直し(同一方向の反復をしない): (1)1aで現行文言でも反転が再現しない→原因仮説を見直す(固定文言以外の要因)。 (2)案Aで2サンプル中1以上が人称反転または`you`ゼロ→文言反復でなく設計見直し(欄の位置/R1・R2の構造を再検討、Opus条件B相当を検討)。 (3)三人称作品で人称・essentials欠落・テンポ指標がノイズ帯を外れる→案Aの副作用として採用候補から外し報告。 (4)累計150円見込み超過・STOP通知・Gate抵触→即時停止してFableへ報告。
- STOP: 各有料起動前に`tools/stop_scope_check_01.py --managed-id FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 ...`(rc=3で新規API禁止)。自PID以外のprocess終了なし。再起動は委任文の許可回数のみ。
- Production不変の保証: (1)DEV runnerは`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/`配下に置き、`sftrial_dev_runner_01.py`と同型で**メモリ上でのみ**`build_r0_prompt`/`build_revise_prompt`/`_render_essentials_block`を差し替える(Production fileは書き換えない・Productionからのimport参照0)。 (2)出力は`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/out/<arm>/`のみ(`er026_output/`へ書かない・`user_test/`未使用・公開なし)。 (3)Seedは同ディレクトリ内コピー(Production `seed.json`と`er026_seeds/`は無変更)。 (4)`narration_voice`が無いSeed(=Production Seed)でDEV関数が元関数とbyte同一を返すことをDefaultOffIsolation型testで確認、`git diff --stat -- er062_family_z_writer_01.py er026_*`が0であることを各段の前後で確認。 (5)flagは新設しない(Productionに到達する新コード経路が存在しないため、11-7の限定例外も使わない)。

## 8. ユーザー判断候補(現時点)
- 現時点で新たな`判断候補`なし。語り口の例外(Voice構造上の制約等)は見つかっていない(ROOT_CAUSE_01.md§4)。Production採用はTrial結果後にFableが`USER_DECISION_REQUIRED`として別途提示(Trial成功時も自動配線しない)。
- 注意点(Opus確認事項): 案Aは既存`source_essentials`スキーマの拡張でありProduction Promptの直接編集を伴う(採用時)。

## 9. 懸念・リスク(自己評価)
- 欄を増やす=「作品ごとの記述の増加」に見えるが、全作品で1文を必須記入するだけで、作品別コード分岐は0。
- 一人称Advを生成した場合のKP選定は既存のcanonicalization(`myself→oneself`追加済み、`OPEN_KP_MYSELF_IMPACT_01.md`)で通過実績あり(Std)。Advで`my/me/I`を含むKPの人称一般化は`generalize_person_dependent_reference`が扱う(音声化に進んだ場合のみ確認)。
- 1文の指定でLLMがどこまで語りの質(自己陶酔・呼びかけ)を守れるかは未検証=Phase 1の主目的。
- サンプル数が少ない(Phase 1=2、Phase 2=各1)ため統計的な保証はなく、「反転がPrompt文言に由来する」ことは1aの対照で、「副作用がない」ことは既存runの変動幅との比較で判断する(限界を明記)。
