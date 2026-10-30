# TRIAL_DESIGN_02: KP選定品質の追加Trial 設計(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02 委任_01、2026-10-30、API 0)

原文=`docs/pm/delegation_log/2026-10-30_KP-DIFFICULTY-4LEVEL-DISPLAY-01_USER.md` §2・§3・§6(照合済み)。前回=`../KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/{RESULT_01,RESULT_02,TRIAL_DESIGN_01}.md`。
Trial専用。Production code/Prompt/Validator/閾値の変更0(Productionは保存済み候補docの読取のみ)。実装=`kpg03_*.py`(本ディレクトリ)。正本のPrompt文言は`kpg03_methods.py`(本書は要点)。

## 1. 目的・制約(ユーザー原文との対応)
| 項目 | 内容 | 原文 |
|---|---|---|
| 改善対象 | ①自由な単語の組合せの混入(deep image/point-like object) ②一般化の失敗(take points away from→take something away from、make life work→make something work) | §2.1 |
| 対象外 | 易しい表現の排除(rely on等は残す。難しい表現優先の方針は維持=difficultyは**並び順にだけ**使い、除外理由にしない) / 3件以上の割合(副次記録) | §2.2 |
| G1型 | 一般化後に独立した学習価値があれば認める方向。条件=自然な英語/原文の意味・用法と整合/自由な組合せでない/不適切な語の追加・削除なし。**表示形と本文の根拠表現を分けて管理** | §3.2 |
| 比較基準 | 方式D(TRIAL-01)。D'(ガード追加)の反復は不可。Promptを1種に固定して細部調整しない=方式(順序・役割分担・モデル)を変える | §3.1 |
| 評価 | 主=自由な組合せ混入率/一般化成功率/一般化後の意味・用法の正確性/修正せず選べる率/良質候補の脱落。参考=3件以上/提示数/難易度分布/ばらつき。別系列独立評価。母集団差を明示 | §3.3 |
| 予算 | 個別Cap **¥120**(Fable設定、無断引上げ禁止)。到達見込み時は事前報告 | §6 |
| 終了 | 実質改善なし→Dを最終採用候補として提示。改善あり→改善版。どちらもProduction配線はユーザー採用判断後 | §3.4 |

## 2. 前回からの原因整理(方式を変える根拠)
- 前回D'(ガード追加)は率が低下(64%)。RESULT_02 5節: 残NGの主因は**塊判定器(luna)のF/C境界の甘さ**(deep image・need an instruction manual・early step towardをCと判定)と、**一般化を『本文の語句』単位で先に塊判定する順序**(G1/G2は『本文の語句』が自由な組合せに見える→選定で落ちる)。
- 同一系列(luna)で生成・判定・一般化するため、判定が自己整合しやすい(別系列gemini判定は不可12件のうちSonnet OKは1件=ゲートとして精度が高い)。
- 一般化の失敗は、(a)人称の取違え(hear something out)、(b)修飾語の保持/除去の基準が曖昧(set a lower limit/took an unexpected turn)、(c)受動形・時制の残りに分かれる。D'は(b)を『語彙的ガード』(決定論)で処理して逆に副作用が出た→**今回はガードではなくPromptの判断基準(除去テスト)で扱う**(ガードはコードに残すが既定OFF)。

## 3. 比較方式(アプローチ(1)〜(4)と対応)
```
D (基準)      : 候補源(P7+過剰生成) → 塊判定(luna) → 一般化v3 → 別系列検証(gemini) → 決定論検査
E1L (対照)    : 候補源 → 塊判定v3[luna] → 一般化v4 → 別系列検証                     ※Prompt強化の純効果
E1S (1)       : 候補源 → 塊判定v3[gpt-6.1-sol low] → 一般化v4 → 別系列検証           ※上位モデルの純効果(E1Lとの差)
E2  (2)(3)    : 候補源 → 一般化v4(全候補) → 塊判定v3[luna](一般化後の見出し形を判定) → 別系列検証   ※順序変更+G1型を構造的に解決
E3  (3)(4)    : E2 + 別系列(gemini)検証に選定ゲート(FREE_COMBINATION/WORD_ONLYのみ除外)を併合(同一call)
E4  (1)(3)(4) : E2の塊判定をsol + 別系列ゲート                                     ※合理的な組合せ(最大構成)
(E5 予備)     : 塊判定にgemini-3.1-pro-preview(別系列の上位、thinking最小・出力上限明示)。E1S/E4で上位モデルの効果が見えた場合のみ、費用が許せば追加
```
共通: 候補源=現行P7保存doc(または簡易再現)+luna過剰生成(TRIAL-01と同一prompt=cache hitで費用0)。span包含/同一display_formの重複除去。冒頭の節断片(whose…/which…)は決定論除外(継承)。WordNet lock・複数形lemma補正を継承(kpg02_methodsのpatch)。
- **E2 vs E1L** = 判定順序(一般化→塊判定)の効果(G1型を『一般化後の見出し形』で判定できる)。**E1S vs E1L** = 上位モデルの効果。**E3 vs E2** = 別系列ゲートの効果。**E4** = 組合せ。1要因ずつ差を取れるよう設計(同一入力・同一上流はcache共有で厳密に同じ)。
- 実行順序の注意: E3/E4はE2とGEN_ALL(+E4以外はSEL)が同一promptなのでcache hit(費用0・厳密に同じ上流)。**E2を先に完了してからE3/E4を起動**(並列起動するとcache未成立で二重課金)。

## 4. 塊判定の定義強化(`CHUNK_DEFS_V3`・`EXTRA_RULES_V3`)
- **W/F/C**の定義は前回を継承し、Fの例を具体化: 形容詞/副詞/名詞+名詞の**描写的組合せ**・**専門分野の記述的名詞句(deep image、point-like object型)**・字面どおりの動詞+目的語・**辞書に定着していない一回限りの比喩(need an instruction manual型)**・修飾語を同類語に替えても成り立つ型。
- **専門名詞句の扱い**: 分野内の記述的な名詞句=F。ただし学習者用英英辞書に一般語として見出しがあり他の文脈でも使える定着した複合名詞(pain point/glass ceiling/sales pitch型)はC。
- **判定テスト4つ**(1つでも当てはまればF): T1辞書テスト(見出し・派生項目・句動詞項目・連語欄に載るか) / T2置換テスト(同類語に替えても同じ型で成り立つか) / T3予測テスト(全語を知る学習者が意味と語の組合せを自力で再現できるか) / T4理由テスト(なぜひと塊か40字で言えるか)。
- **難易度は区分と独立**: Cならrely on等の基本語の句動詞もCのまま(ユーザー方針)。difficultyは並び順(advanced→upper→easy)のみ。前回D'の『C判定でeasyなら不可』veto**は廃止**(ユーザー§2.2)。
- **G1型**: 本文の語句が個別名詞を含み自由な組合せに見えても、可変部をsomething/someoneにした見出し形が辞書見出しとして成立すればC。逆に一般化で字面どおりの易しい組合せ(set a limit等)に落ちて学習価値が消える場合はF。E1は『見出し形で成立するか』を考慮させ、E2は**実際に一般化した形を判定対象**にする(`mode='form'`)。
- 受動断片・節断片はkeep=false、同一意味・用法の重複は代表1件のみkeep(品質を下げて埋めない、継承)。

## 5. 一般化規則(v4、`GEN4_EXTRA`。トークン分類CORE/SLOT/DROPは継承し`display_form`は決定論組立)
- **核/可変部/除去**: 入替テスト(無関係な別名詞に替えても同構文・同語義ならSLOT)を継承。目的語を省いても成立する句動詞はDROP、途中に挟む場合のみSLOT、前置詞で終わる見出しの後続名詞句はDROP(継承)。
- **人称**: 目的語の位置の語が本文で人を指すならSLOT_PERSON(someone)、物・事ならSLOT_THING。代名詞itでも文脈で人なら人。
- **意味を担う修飾語の判定(除去テスト)**: (1)除いた形が同じ辞書見出し・同語義で成立→DROP / (2)除くと別表現・別語義・意味喪失、または修飾語自体が見出しの一部(否定語等)→CORE / (3)SLOT名詞の修飾語は常にDROP / (4)**迷えばDROPせずCOREのまま**(誤った見出し形を作るより、残して選定段でFとして落とす方が安全)。語彙の決定論ガードは使わない(D'の副作用)。
- 受動・過去分詞は核に残さない(能動にできなければ無理に一般化せず元の形のまま)。固定句中の動詞も原形(or so it seemed→or so it seems)。
- **表示形と本文根拠の分離管理**: `display_form`(見出し形、例 `take something away from`)と`source_span`(本文の根拠、例 `take points away from`)は別フィールド。出力JSONと比較ページに両方を保持(根拠は変更しない)。一般化後に動詞+前置詞/粒子の組合せ自体が見出しなら、本文の個別名詞は積極的にSLOT化する。
- 検証(別系列gemini・非thinking・出力上限4500): 意味保持/gloss整合/見出しの自然さ。FIXは決定論検査(`display_check`)を再通過した場合のみ採用。`meaning_preserved=false`は元のspan形へ戻す(D'から継承、安全側)。
- 別系列ゲート(E3/E4): 上記検証と同一callで`gate_cls`(W/F/C)・`gate_code`を返し、**FREE_COMBINATION/WORD_ONLYのみ除外**(TOO_EASY/OVER_GENERALIZEDは除外理由にしない=易しい表現を排除しない、G1型を落とさない)。除外はlogに全件記録。

## 6. 評価手順(`kpg03_stats.py`/`kpg03_judge.py`/`kpg03_manual.py`)
1. **対象**: 前回と同じ14ケース(必須8=untidi/ai_cha/jwst_m/meta_w×a2・b1b、汎化3=aiisland_b1b/surname_b1b/melos_a2、未使用3=ignobel_a2/b1b・tesla_b1b)。可能なら追加3(moon_a2/b1b、melos_b1b)。Beforeは**D**(TRIAL-01 `kpg01_work/results/*__D_luna.json`)を読込。
2. **一次判定=Sonnet実読**(`kpg03_manual.MAN[arm][case][表示形]=(コード,理由)`、記載なし=OK、`JUDGED`に実読済みを登録)。コード=FREE(自由な組合せ)/GEN(一般化失敗)/MEAN(意味・用法不正確)/NAT(不自然)/OTHER。**D自身の判定も新基準へ再分類**(`D_OVERRIDE`。rely onは易しいだけ=OK扱いに変更。この結果Dは62/71=87%、TRIAL-01の61/71と1件差。比較は同一基準で行うため新基準Dを使う)。最終の独立受入はFable。
3. **別系列独立評価**(生成・判定に使っていない系列、非thinking・出力上限明示): `deepseek-flash`(全arm、1 callに40件までバッチ)+finalistに`deepseek-v4-pro`(非thinking、max_tokens明示。前回のthinking既定事故は再発防止)。`gemini-3.8-flash`による独立判定は**ゲートを使わないarm(E1L/E1S/E2)のみ**(E3/E4はgeminiがゲートに入るため循環。実施しない)。完全な独立でなく、最終は人(Sonnet/Fable)の実読。
4. **指標**(`kpg03_stats.py`の定義): 自由な組合せ混入率=FREE/提示数 / 一般化成功率=一般化を適用した候補(display≠本文核)のうちGEN NGでない割合 / 意味・用法の正確性=1−MEAN/提示数 / 修正せず選べる率=OK/提示数 / **良質候補の脱落**=Dで修正せず選べた候補のうちarmに残らなかった割合(span核またはdisplay一致) / 参考=3件以上ケース率・平均提示数・difficulty分布 / **run間ばらつき**=同一入力・`KPG_SALT`違い(`--suffix _r2`)の提示形の一致/和集合。
5. **必須例の達成表**(G1〜G5・V1〜V4+deep image/point-like object)。**母集団差**=各armが実行済みのケース集合を表示し、全arm共通ケースのみの再集計も併記(armごとにケースを絞った場合の影響を分離)。未実読の候補が残る場合は出力冒頭に「暫定値」警告。
6. **比較ページ**(`kpg03_page.py`): 記事×レベル別にD vs E各方式を並べ、各候補にOK/NGコード・本文根拠表示、冒頭に主評価表。既定は非公開preview、`--publish`で`user_test/kp_generalization_trial_02/`(委任_02でFable確認後)。

## 7. 費用見積(円、実績単価に基づく。Cap ¥120)
単価の根拠=TRIAL-01/02ledger実測: luna SEL 0.28/call・GEN 0.17・B1 0.17(cache hitで0)・gemini VER 0.39・sol B2相当(約2.1k in/0.8k out)1.9〜3.2。dry-run(mock、入力token実測推定+出力経験値)でも同水準。**費用の不確実性が最も大きいのはsol呼出(約2.6/call、レンジ2〜3.5)**。
| arm | 1レベルの費用(単独) | cache共有後の増分 | 14ケース合計(増分ベース) |
|---|---|---|---|
| E1L | 0.84(SEL0.28+GEN0.17+VER0.39) | 0.84 | 11.8 |
| E2 | 1.02(GEN_ALL0.35+SEL0.28+VER0.39) | 1.02 | 14.3 |
| E3 | 1.13 | **0.5**(GATEのみ新規。GEN_ALL/SELはE2とcache共有) | 7.0 |
| E1S | 3.16(SEL sol 2.6+GEN0.17+VER0.39) | 3.16 | (4ケース12.6/14ケース44) |
| E4 | 3.45 | **3.1**(SEL sol 2.6+GATE0.5。GEN_ALLはE2と共有) | (6ケース18.6/14ケース43) |
| 独立評価 | ds-flash 約1.0/arm(14ケースを3 call) | dspro約3.8/arm | 5arm分約5+finalist1〜2arm分4〜8 |
**フェーズ構成(Cap内に収まる構成)**
| Phase | 内容 | 見込み | 累計 | 停止点(`--phase-cap`) |
|---|---|---|---|---|
| P1 | E1L+E2+E3 ×14ケース(E2→E3の順) | 33 | 33 | 38 |
| P2 | E4 ×難所6ケース(untidi_a2/b1b・ai_cha_b1b・jwst_m_a2/b1b・meta_w_b1b)+E1S ×4ケース | 31 | 64 | 34 |
| P3 | P1/P2で最良のsol arm(E4またはE1S)を残り8ケースへ拡張(最良がsolでなければ省略) | 0〜25 | 64〜89 | 28 |
| P4 | 独立評価(ds-flash 全arm+dspro finalist) | 9〜13 | 73〜102 | 15 |
| P5 | run間ばらつき(最良armを2〜3ケース、SALT違い) | 3〜10 | 76〜112 | 11 |
| P6 | 追加ケースmoon_a2/b1b・melos_b1b(D相当のbaseline run含む) | 約14 | 90〜126 | **累計≤¥95の場合のみ実施** |
- **Cap整合**: 必須構成(P1+P2+P4+P5軽量)は約¥82、P3拡張込みで最大約¥107。P6は任意で最優先で削る。累計¥96(Capの80%)到達で新規フェーズに入らず、完了済みデータで集計・報告へ(`kpg03_llm`が警告し、`CAP=120`超で新規callを拒否=ラッパが物理的に停止)。
- **削減案(優先順)**: ①P6省略 ②P5を2ケースに ③E1Sを3ケースに(E4とE1Lの差で上位モデル効果を代替推定) ④P3をE4でなくE3(安価)に ⑤dsproを省略。いずれも品質評価の主指標(混入率・一般化成功率・脱落)は維持。
- **量産単価への換算**(参考): E2/E3は1レベル約¥1.0〜1.1(既存P7の置換相殺は未確認)、1記事セット(Std+Adv)約¥2.0〜2.3=70円の約3%。sol系は約¥6.3〜6.9/セット(約9〜10%)。Dは0.98/レベル。**sol系は量産単価に見合う品質差があるかが採用判断の焦点**。

## 8. 実装準備の状態(API 0、すべて完了)
| ファイル | 役割 | 検証 |
|---|---|---|
| `kpg03_llm.py` | 専用台帳・Cap(120)/フェーズCap強制・max_out/think_budget必須・mock・deepseek非thinking+max_tokens | `kpg03_test.py` 9件PASS(Cap超過/phase停止点超過でAPI前に拒否、max_out未指定拒否、gemini think_budget未指定拒否) |
| `kpg03_methods.py` | E1L/E1S/E2/E3/E4、Prompt v3/v4、ゲート、pick(easy非除外)、WordNet lock継承 | mock dry-run 14ケース×5方式=全70run完走(エラー0) |
| `kpg03_run.py` | 実行(`--arms --cases A/B/C/ALL14 --phase-cap --suffix --mock`)。CapReachedでrc=3停止、自動再試行なし | mock実行OK |
| `kpg03_judge.py` | 独立評価(ds/dspro/gem、バッチ40件) | mock実行OK |
| `kpg03_stats.py` / `kpg03_manual.py` / `kpg03_page.py` | 集計・実読記入先・比較ページ | mock集計/ページ生成OK(内容は無意味) |
- 実API呼出0(`kpg03_work/cost_ledger.jsonl`は未生成=実費0。mock台帳・mock結果は削除済み)。Production module(er*)非import(testで確認)。前回cache(`kpg01_work/llm_cache`)を読むため、**委任_02はこのworking treeで実行**(gitにcacheは無い)。
- 未確認(実走で確認): solの実出力token/費用レンジ、E2のGEN_ALL(全候補一括)の一般化品質、E3の gate_cls 精度、cache共有の成立(E3/E4上流がE2と一致すること=ledgerのcached=true)。

## 9. 委任_02の実行計画(順序・停止点)
1. 開始時に`tools/stop_scope_check_01.py`確認。P1: `E1L,E2`を実行 → 完了後`E3` → Sonnet実読(14ケース×3方式)で暫定集計。
2. P2: 難所6ケースにE4、4ケースにE1S。実読。ここで上位モデル効果(E1S−E1L)とゲート効果(E3−E2)・順序効果(E2−E1L)を主評価で判定。
3. 判断: 最良armが「Dから実質改善」(混入率↓かつ修正せず選べる率↑かつ脱落が小さい)ならP3(必要時)→P4→P5。改善なしならP3/P5を省き、**Dを最終採用候補**としてClose(ユーザー原文§3.4)。
4. 停止点: 累計¥96到達/CapReached/原因不明のrc≠0×2は停止してFableへ。独立評価は`deepseek-flash`を全arm、`dspro`はfinalistのみ。比較ページ公開と判定整合のFable確認後に報告。
5. Closeout案: VALIDATED(改善あり・採用はユーザー判断)/REJECTED/USER_DECISION_REQUIRED(採用に新ルール=display_form許容・G1型・費用が必要な場合は常にユーザー判断)。Production配線は一切行わない。

## 10. リスク・限界
- Sonnet実読と別系列判定の一致率は前回89%(gemini)/約8割(deepseek-flash)。差が小さい改善は判定ばらつきの範囲に埋もれうる→run間ばらつき(P5)と共通ケース集計で補う。
- 評価母集団が小さい(約70〜90件)。率の差は数件の入れ替わりで動く。
- E2は全候補を一般化するため一般化callの入力が約1.5倍。品質が出ない場合はE1L/E3比で費用対効果を判断する。
- 前回D'と同様に、設計途中の調整は同一ループ内のパラメータ調整に限り、方式追加は記録する(Fable報告)。
