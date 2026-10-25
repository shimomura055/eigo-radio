管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01。Opus必須レビュー(PM_GOVERNANCE 11-3 条件A: 新しいProduction経路の設計、実装前)。読み取り専用。日本語で報告。

## 背景(ユーザー正式決定 2026-10-25)
Family Yを正式Productionとして立ち上げる(APPROVED_FOR_PRODUCTION→PRODUCTION_WIRED目標)。Y基本構成=リード/Voice1/Voice2/Voice3/Tension+Closing、3人3立場・人物像から一人称で主観的に語る(既存承認設計維持)。Closing一般化方式=Prompt 02(sha 4713ceff…)・gpt-6.1-sol・effort high を今後のY記事に正式採用(意味変更・Prompt 03化禁止)。『宅配の再配達』のみ人手設計案B「料金は、誰の何を動かせるのか」を個別採用。最重要=他Family/共通仕様との乖離解消と将来の配線漏れ防止(過剰な新仕組みは作らず既存SSOT・Gate活用)。承認済み共通仕様はY立上げ時に組込み、未承認(JA ASR案A・Prompt 03・Tier内順位改善等)は先行採用禁止。Prompt 02・Gate基準の独断変更禁止。X正式Production基盤を最大限再利用。受入条件12項目(正式初回経路/Y固有構成維持/Prompt 02+sol highの実使用/model_id・routing・Prompt hash記録/HRあり・なし/適用対象共通仕様/retry・fallback・regeneration・resume/Regression・Validator・integration/正式E2E/SSOT・Git/OPEN追跡/承認内容と出力一致)。

Sonnet Phase 0成果物(C:\Users\tensh\eigo-radio\docs\research\FAMILY-Y-PRODUCTION-LAUNCH-01\): SPEC_LEDGER_01.md(+spec_ledger_01.json、55行)、EXISTING_SPEC_CHECK_01.md、PROMPT_GATE_ALIGNMENT_01.md、DESIGN_01.md、OPUS_REVIEW_REQUEST_01.md、BUDGET_PLAN_01.md、OPEN_TRACKING_01.md。
関連: `er110_family_y_closing_general_trial_01.py`(Prompt 02の組立・schema・決定論検査・Gate呼出)、`er110_family_y_persona_text_trial_01.py`、`er110_family_y_audio_trial_01.py`(production_reachable=False)、`er012_b_family_voices_a2_production_01.py:358`付近(Leakage Gate定義)、X基盤 `er019_family_x_audio_production_runner_01.py`、Z stage framework `er062_family_z_writer_01.py`(ensure_stage/DEPENDENTS)、`er006_model_routing_contract_01.py`、`er103_proper_noun_alarm_policy_01.py:42`/`er109_xz_scope_01.py:25`(scope X/Z)、KP HR `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_02.md`(er119)、Part 2 `docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md`(er120)、案B正本 `docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md`。

Sonnet設計の要点: 新規`er121_*` runner(Zのstage framework形式。X runner拡張はKP HR/Part 2統合と競合するため不採用、DEV昇格はpatched_*/alias ID/DEV予算skipを持ち込むため不採用)。新規file=text core/audio/runner/案B固定registry。共有file最小編集5群(routing `FAMILY_Y_*`、scope "Y"、Y segment ID、page注意書き+検査tool、CURRENT_SPEC)。案B固定注入=コード定数registry(slug・sha・承認ref)、env/CLIで有効化不可、Gate1判定のみ・局所書換え禁止・FAILはSTOP。Closingは既存`run_gate`(判定≤3・局所書換え・LEAKAGE_RESIDUAL_STOP)を使い、局所書換えpromptに選定済み切り口を付加(I-1)、gate_history全保存、残存FAIL時は未公開JA稿+FAIL記録。台帳: A共通24/B X基盤2/C Y固有12/D X・Z固有5/E旧B3/F進行中9。除外: Research/Ledger/B3/Fact Lock/RF(Yは入力が空)、中核数値v4/J2(承認原文がY/Z対象外)、Z固有、旧B経路。判断待ち: Voice生成方式の採用範囲、Chunk TTSのY適用、Gate文言、OPEN-469。費用: 宅配(案B・再利用)27〜35円、通常Y記事69〜93円(70円目標を約11円超過。主因Voice R0 20〜26円+Closing 17〜22円)、立上げ総額73〜113円。所要: 実装約2日+evidence約1日。

## レビューしてほしい論点(絞る。追加探索可)
1. runner方式の選択(新規er121 Z形式 vs X runner拡張 vs DEV昇格): 再利用率・Dangling Reference・将来の共通仕様配線漏れ防止(X/Z変更時にYへ自動的に効く部分と効かない部分)の観点で妥当か。X基盤のどの関数を直接importで共有し、どれを複製するかの線引きが「将来差分が再発しない」設計か。
2. 共通仕様の継承判定(台帳): 除外7件・判断待ち4件・適用26件の分類に誤りや漏れがないか。特にChunk TTS(承認原文X/Zのみ)、ASR cascade/同音・異表記救済/TTS再生成・HR Lock/KP vote/Redundancy QA/数字・固有名詞(中核数値v4/J2は対象外と明記)/Part 1(Adv限定、Yのレベル構成との関係)/KP HR・文法HR・Part 2(er119/er120接続点)のY適用。
3. Closing一般化のProduction移植: er110のDEV runner(`--paid`+BUDGET_APPROVED gate、DEV予算skip等)からProduction moduleへ切り出す際にPrompt 02の組立・入力構造(THEME/PERSONA/VOICE block、Research/Fact空)・schema・決定論検査(違反時最大1回再生成)・Leakage Gate呼出が逐語で保たれるか。I-1(局所書換えpromptに選定済み切り口を付加)はGate/Prompt 02の意味的変更に当たらないか(承認済み`run_gate`の範囲内か)。残存FAIL時のfail-closed。routing契約(Closing=gpt-6.1-sol high、判定=gpt-6-luna)の固定とactual model_id記録。
4. 案B固定注入: 当該記事のみ・監査可能・一般化方式迂回の例外として安全か(別記事へ誤適用されない、本文shaで固定、Gate 1判定でFAILならSTOP)。受入条件3「Prompt 02+sol highの実使用」を宅配で満たせないため別記事(SNS)でevidenceを取る計画の妥当性。
5. Prompt/Gate不整合の整理(PROMPT_GATE_ALIGNMENT_01): FAIL5件の分類(本文3/Gate過剰2/実装不具合0)、不整合の実体2点(肯定側が旧B骨格で狭い/判定器が「見えてくる」をdiscovery_syntaxとして拾う)の妥当性。自律実装可とした対処(I-1〜I-4)が承認済み基準内か。ユーザー判断に回す変更案(G-1〜G-3、P-1)の整理は適切か。
6. 将来の配線漏れ防止: 台帳(json)+既存Closeout Mandatory Checkへの1項目追加提案(共通仕様採用時にX/Y/Zの配線状況確認)で必要十分か。過剰でないか。
7. 費用・所要: 通常Y記事69〜93円(70円超過)の原価低減余地(品質維持の範囲で)。実装2日+evidence1日の短縮余地(並列レーン)。

## 出力形式
必須修正(M-n: 理由・具体案・該当箇所)/推奨(R-n)/問題なし確認(C-n)/ユーザー確認が必要と考える点(理由付き)/実装着手可否の総合所見。断定できない点は「未確認」。