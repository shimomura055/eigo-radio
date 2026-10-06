# P0a 追加3記事の選定(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02、JPY0、read-only)
## 1. 固定台帳の棚卸し(テーマ別、代表run。txt必須/JSON・B3は可能なら。txtのみも候補可=notes追記はtxtへ決定論追記)
| テーマ | txt | draft | verif | B3 brief | JA original | EN記事 | 代表run dir |
|---|---|---|---|---|---|---|---|
| meta | Y | Y | Y | Y | Y(wiring run_01 ja_writer) | Y | er019_output/meta/run_03 |
| hormuz | Y | N | N | Y | Y | Y | er019_output/family_x_refresh_e2e_01/hormuz/run_03 |
| small_bag(tiny_bags) | Y | Y(er014のみ) | Y(er014のみ) | Y(er019 diversity run_01/02) | Y(run_01 ja_writer) | Y | er019_output/family_x_b3_diversity_trial_01/small_bag/run_01 |
| space_weapons | Y | Y | Y | N | N | Y(a2/b1b article.md) | er014_output/user_test_news_2ep_01/space_weapons |
| ai_control | Y | Y | Y | N | N | Y(a2/b1b) | er014_output/user_test_news_2ep_01/ai_control |
| sewer(下水道) | Y | Y | Y | N | N | N(rejected_advanced_attempt2.mdのみ) | er012_output/e_family_two_level_wiring_01/sewer |
| UK SNS夜間制限(A02) | Y | Y | Y | N | N | Y(run1/run2_article.md) | er003_output/en_direct_vfl_01/A02 |
| convenience_ai / news_stage3(CAR-T) / four_type(news,trend,discovery,voices) / towels / wake_before_alarm / family_c_future / b1_rebuild / entertainment_line(Muse) / world_cup A01 / IMO ADD03 | Y | 大半Y | 大半Y | N | N | 一部Y | er014/er011/er013/er012/er017/er003各dir(Globで確認) |
| er006 pool_pilot 約12テーマ/er005/er003 n3,novel等 | Y | N | N | N | N | 一部 | 同上(固定台帳として使えるが形式が旧) |
固定台帳(txt)が揃う既存テーマ: 約45テーマ(txtのみ約20含む)。B3 briefが既存なのはmeta/hormuz/small_bagの3つのみ。注: 他テーマでTrialを行うにはB3 brief生成が必要(=Trial側で有料call。Fable判断)。
## 2. 候補テーマの高確度表現(A3確度高=取り違えで逆転/重大変質。難語・分母曖昧・仮定試算は除外)
| テーマ | fact_id | 表現(逐語) | タイプ | 逆転時の意味 | 根拠 |
|---|---|---|---|---|---|
| space_weapons | F-009 | 核兵器を搭載する新しい衛星をASAT能力として開発していると評価 | 完了/予定 | 「核搭載衛星を宇宙へ配備した」 | notesが「開発中と配備」を厳密に分けると指示=誤読リスク自明 |
| space_weapons | F-001 | 配備していると述べた/初めて認めた発言 | 時系列・主体 | 「米国が初めて配備した」(認めたのが初) | 公式記事「初めて認めた発言」 |
| space_weapons | F-002/F-007 | counter-space weaponと評価/ペレット兵器を開発しているとの非公開情報 | 主体・完了 | 「実際に攻撃した/配備済み」 | notes: 評価と実施を区別 |
| sewer | F-011 | 未整備区域を推進区域へ転換した/残る未整備区域全てを方針案(意見募集) | 対象・完了/予定 | 「整備済み下水道を浄化槽へ切替・決定した」 | 実記録あり: b1b/audit/deviation_check.json(MAJOR, changed_fact+scope)、記事"changing aging sewer systems to septic tanks" |
| sewer | F-010/F-016 | 市街化区域=公共下水道・調整区域=浄化槽(原則)/漁業集落排水廃止→浄化槽 | 対象・方向 | 区域取違え・既設下水管切替と読む | F-016 notesが公共下水道切替と区別せよ |
| ai_control | EVID-006 | 模擬シナリオでblackmail試行84%(実在人物なし) | 対象(模擬/実) | 実在の技師を恐喝した | notes明記:real engineerと書くな |
| ai_control | EVID-004 | 誘導されればsandbagする/誘導なしのsandbagは未検出 | 原因・主体 | 自発的に手を抜く、と逆に言う | notes: 両方述べよ |
| ai_control | CONTROL-001/003 | 当時は人間の制御を損なう能力なし/最新モデルは標的が実在と認識し停止 | 時系列・因果 | 現在も不可能/停止は一般保証 | notesが一般化禁止 |
| UK SNS A02 | POL-01/06 | 計画で未施行/default-onだが利用者が変更可 | 完了/予定・状態 | 施行済み・強制 | notes明記。ただしspace_weaponsと完了/予定が重なる |
| small_bag | F002/F009/F016 | being displaced/autumn's return/carried by | 方向・時系列・主体 | 中確度止まり(A3: 確度高0件、いずれも「消滅/流行終了」への強化=変質) | 逆転でない |
## 3. 選定3テーマ(Trial 5テーマ=meta,hormuz+3)
1. **space_weapons**: 「開発中・評価・発言」と「配備・実施」の完了/予定差で記事の核(宇宙兵器配備)が逆転するFactが複数(F-009,F-001,F-002,F-007)。タイプ=完了/予定・主体。
2. **sewer**: 台帳F-011/F-010/F-016の「方式転換(未整備区域・方針案)」を既存下水管の浄化槽切替と誤読した実記録があり(deviation_check.json MAJOR)、タイプ=対象・方向。
3. **ai_control**: 模擬/実在・誘導/自発・当時/現在・停止の一般保証化で意味が逆転するFactが複数(EVID-006/004,CONTROL-001/003)、タイプ=原因/結果・時系列。
## 4. 非選定理由(各1行)
- small_bag: A3で確度高0件(displaced/autumn's return/carried byは強化=変質止まりで逆転でない)。B3既存の利点があるが、「高確度のみ」条件を満たさない。補欠扱い。
- UK SNS(A02): 高確度(POL-01/06)はあるが完了/予定がspace_weaponsと重複、多様性が劣る。補欠(第1補欠)。
- convenience_ai/news_stage3/four_type等: 逆転型の高確度表現は未確認(今回は全factを精読していない、残課題)。
- er006 pool_pilot等: 旧形式でnotes_for_writerの粒度が不明、新規読込コスト大。
## 5. 選定3テーマの固定台帳パス・Before・既存記事
| slug | txt | draft | verification | Before run dir | 既存記事 |
|---|---|---|---|---|---|
| space_weapons | er014_output/user_test_news_2ep_01/space_weapons/research/verified_fact_ledger.txt | 同research/fact_ledger_draft.json | 同research/fact_ledger_verification.json | er014_output/user_test_news_2ep_01/space_weapons | a2/article.md, b1b/article.md(JA original・B3 briefは無し) |
| sewer | er012_output/e_family_two_level_wiring_01/sewer/ledger/verified_fact_ledger.txt | 同ledger/fact_ledger_draft.json | 同ledger/fact_ledger_verification.json | er012_output/e_family_two_level_wiring_01/sewer | b1b/audit/rejected_advanced_attempt2.md(却下版のみ。誤読実記録=audit/deviation_check.json) |
| ai_control | er014_output/user_test_news_2ep_01/ai_control/research/verified_fact_ledger.txt | 同research/fact_ledger_draft.json | 同research/fact_ledger_verification.json | er014_output/user_test_news_2ep_01/ai_control | a2/article.md, b1b/article.md |
注意: 3テーマとも既存B3 briefなし。Trial(B3→JA)にはBefore/After両方のB3生成が必要。台帳は日本語(space,sewer)/英語(ai_control)。ai_control台帳の英語はsmall_bagと同様JA Writerで扱う前提。
## 6. 5テーマ最終一覧
| テーマ | slug | 台帳パス(txt) | 対象fact_id | 表現 | タイプ |
|---|---|---|---|---|---|
| Meta | meta_run03 | er019_output/meta/run_03/ledger/verified_fact_ledger.txt | MUSE-HC-012(+HC-014) | ロールバックした/商業者との改善 | 撤回/復元・対象 |
| ホルムズ | hormuz_run03 | er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt | HF-009(+HF-007) | 上げ幅縮小→高水準へ戻った | 方向・途中/最終・状態変化 |
| 宇宙兵器 | space_weapons | 上記5節 | F-009,F-001,F-002,F-007 | 開発している/初めて認めた/評価 | 完了/予定・主体 |
| 下水道 | sewer | 上記5節 | F-011,F-010,F-016 | 未整備区域を転換/方針案 | 対象・方向 |
| AI制御 | ai_control | 上記5節 | EVID-006,EVID-004,CONTROL-001 | 模擬/誘導/当時 | 原因/結果・時系列 |
タイプ分布: 撤回/復元1・方向2(hormuz,sewer)・状態/途中最終1・完了/予定1・主体2(meta対象含む)・対象2・時系列/原因結果1。6類型のうち状態変化/方向/主体対象/時系列/完了予定/原因結果が全て最低1回カバー。
STOP該当: なし(候補3確保)。留意: 3テーマにB3 brief無し、誤読実記録はsewerのみ(他は台帳notesの警告からの推定)。
