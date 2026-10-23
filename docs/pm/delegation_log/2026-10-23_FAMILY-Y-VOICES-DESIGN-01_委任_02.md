FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_02-SYNTHESIS-20261023

# 委任_02: Family Y(Voices型)基本設計案の統合作成(DESIGN/RESEARCH ONLY・API費用0・Production/Prompt変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_02.md`(N≈324〜334、先頭行MARKER一致確認)。
2. ACTIVE_TASK.md: 別agent(ASR-HOMOPHONE 委任_05、速度Trial 委任_03)が並行中。編集直前に再読込し、FAMILY-Y行だけ更新。

## 1. 入力(すべて読む。SSOTは節単位Grepのみ)
- ユーザー指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`(§2の確定済み基本設計は再承認不要。§5「ユーザー判断を最小化」、§6品質リスク(1)〜(6)、§8成果物①〜⑦、§9 DESIGN/RESEARCH ONLY)。
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/INVENTORY_X_Z_SPEC_01.md`(X/Z最新仕様、§10接続点T1〜T17、§11衝突・注意点1〜16、§13取り違え点)。
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/INVENTORY_OLD_B_VOICES_01.md`(旧B仕様、§8品質NG F1〜F12と承認済み対策、§10 C不継承候補C1〜C12、§11 D候補8件、§12未確認)。
- 関連OPEN: 217/218/219/415(Y過去Trial記録)、167(nuance境界)、461/462(Z速度Trial進行中)。

## 2. Fableの設計方針(分類の指針。これに沿って判断事項を絞る)
- **Family Xの正式経路を基盤**にし、Yは「構造差分(5パート・3 Voices・Tension+Closing)+Voice編集思想」だけを追加する。旧BのProductionコード・registry・B専用入口・命名(C9)は転用しない。
- 分類A(X/Z承認済み共通仕様→継承)に含めるもの: Research/Ledger/B3の枠組み(Voices向けの選定単位調整は設計で吸収)、Writer三段(日本語→忠実英訳→A2簡易化)、KPFT/KP3V/CMU gate、PNAP、er109(X/Zリテラルscopeへ"Y"を加えるのは技術対応=PM_GOVERNANCE 28-1運用7の範囲として扱い、ユーザー判断にしない。ただし開示する)、AUW(原文に「Yは開発時に正式配線」既決)、多語同音救済、TTS backend/style profile/ASR 3層/値ガード/HR Lock、retry/fallback/Store/resume、QA gates、試聴ページ標準、Std 6%減速(Z速度Trialの結果が出れば追従)。**「承認原文がXのみ」の項目(丸め判断・Risk Flagger)は、当時Xが唯一のニュース系Familyだったことによる限定であり、Voicesの性質と衝突しなければA(継承・開示)として扱い、Dにしない。**
- 分類B(旧B承認済みVoices固有→継承設計): 01B §4の「B継承候補」全件(Voice Card起点、一人称"I"、語り手の外側要約禁止、具体状況から書き始め、同じ意味の反復禁止、解決策提案禁止、陣営機械割当の禁止、候補A/E/F、候補C[数字は本人経験のみ最大1つ]、体験claim根拠付け、Leakage項目の考え方、Acceptance Gate、Tension「共通前提→分岐点→非対称性」)。
- 分類C(不継承): 01B C1〜C12+TTS声割当の旧B方式。
- 分類D(ユーザー判断)は**本当に新しい編集仕様・承認済み仕様との実質衝突・重要トレードオフ・設計思想の変更**に限る。候補ごとに「既存仕組みで解決できないか」「過去に解決済みでないか」を確認し、Fable推奨案と短い理由を付ける。目標は**D 6件以内**。D候補として検討するもの(各々、推奨案を用意): (D1)Tension+Closingの中身(再定義要素の有無・尺配分、Comment4の廃止/移動を含めて1件に統合)、(D2)Voice Cardの作成方式(人手/Storyline+B3割当からの半自動。推奨は「X基盤のResearch→B3で3視点のStakeholder候補を決定論的に出し、Voice CardはWriter前段のLLM1回で生成、Leakage Checkで検査」のような費用最小案を具体化)、(D3)3 VoicesのTTS Voice(Std=Aoede単独のX方針のままか、Z承認済み登場人物Voice表[男女各5・登場順循環]を再利用して人物別にするか。推奨と費用差)、(D4)OPEN-167 nuance許容境界(推奨: 旧B承認済み候補A/E/Fを維持し、Leakage Checkの`leak_position_blur`は現状のまま、Trialで実測してから判断=今回は判断不要にできるか検討)、(D5)Tension非対称性文×Ledger Deviationの構造衝突(推奨: Tensionは新事実を導入しない規則+Ledger照合をTensionに適用しない等、既存規則内で解ける案があればAに落とす)、(D6)Yの総尺・語数の目標(X実測4.5〜5分/Std 385〜434語を基準に、3V+Tensionで何語配分か。推奨値を提示し、X基準踏襲ならDにしない)。
- 品質リスク§6(1)〜(6)は、承認済み対策(B継承)で何がカバーされ、何が残り、残りに対して**新Validatorを増やさず**設計で抑える方法(Voice Cardの独立性設計、Tensionの役割限定、Fact Lock規則2の運用、Acceptance Gateの流用、局所書き換え[X既存`--only-segments`相当のテキスト版があるか確認])を示す。新検査の追加は最小限とし、追加する場合は理由とQCDを明記(採用はユーザー判断=D)。
- QCD: 量産単価70円目標に対し、Yの構造差分で増える費用要因(Voice Card生成1回、Leakage Check LLM判定、3Vで本文が長くなる場合のTTS/ASR)と減る要因を、X実測(A 54.06/B 131.61、定常平均約75.3円)と旧B実測(2V 1セット99.01円[TTS除く]、3V Writer 1attempt約24〜28円)を出典にして見積(推定は推定と明記)。
- 次工程(⑦): 設計確定後の最小Trial計画(1テーマ・Std/Adv各1本、既存X経路+Y差分のDEV実装、費用見込み、評価項目=構造・尺・Voiceの人物性・重複・Tension・Fact Safety・音声QA、成功基準は既存承認基準のみ)。実施は別途承認。

## 3. 成果物
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/DESIGN_PROPOSAL_01.md`: ユーザー§8の順序で①結論 ②仕様継承マトリクス(A/B/C/D、各行に出典・Status・Y適用時の注意) ③Family Y構造案(5パート×役割×境界、Preview/Comment/KP/In One Line等の学習支援構造の配置、segment_id案、X接続点T1〜T17との対応) ④品質NG対応表(旧B F1〜F12×原因・承認済み対策・Y適用方針・残存リスク、§6(1)〜(6)との対応) ⑤QCD評価 ⑥ユーザー判断事項(D、推奨付き、6件以内) ⑦次工程(最小Trial計画案)。非エンジニア向けに、技術用語は初出で短い日本語説明。
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPUS_REVIEW_REQUEST_01.md`: Opus独立レビュー用の論点(旧B NG再発・継承漏れ・不要な複雑化・QCD)と、設計の要点サマリ。
- SSOT: OPEN_ITEMSに新item「FAMILY-Y-VOICES-DESIGN-01」(Status=`DESIGN_DRAFT_PENDING_OPUS_REVIEW`、確定済み基本方針[原文§2]と判断待ち候補[D]を分けて記載)、CURRENT_SPECは**変更しない**(未承認案を正式仕様として書かない。ただし01Aが指摘したCURRENT_SPEC:1677の古い記述「M2P0+A方式=PRODUCTION_WIRED」は、KPFT撤去済みの事実に合わせて「(撤去済み、OPEN-454参照)」と注記する最小修正のみ可)、DECISION_LOG 1件(設計調査実施・採用なし)、REPORT_LEDGER 1行。commitは明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- Trial、API費用、Production/Promptコード変更、未承認案の正式仕様化、A/B/Cコード変更、Dの水増し(自明な継承・内部実装・軽微不整合を判断事項にしない)。

## 5. 報告(docs/pm/RESULT_PACKET_FYD2.md、同内容を最終報告で)
(1)①結論の要旨 (2)マトリクス件数(A/B/C/D) (3)構造案の要点 (4)D一覧(推奨付き) (5)QCD要点 (6)最小Trial計画の要点・費用見込み (7)Opusレビュー論点 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。