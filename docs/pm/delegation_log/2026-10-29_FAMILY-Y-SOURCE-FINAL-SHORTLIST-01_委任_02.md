Fableからの委任_02(FAMILY-Y-SOURCE-FINAL-SHORTLIST-01: 3 Lane統合→最大20件の比較一覧(ユーザー向け)+内部証跡+レジストリ/SSOT反映。API 0、Production変更なし)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Y-SOURCE-FINAL-SHORTLIST-01_委任_02.md` に逐語保存してから開始。`tools/stop_scope_check_01.py --managed-id FAMILY-Y-SOURCE-FINAL-SHORTLIST-01 --run-dir docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01 --out docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01/stop_check_02.json`(rc=3で停止)。
正本: ユーザー原文 `docs/pm/delegation_log/2026-10-29_FAMILY-Y-SOURCE-FINAL-SHORTLIST-01_USER.md`(§3基準・§5成果物・§7完了条件を全文)。入力: `docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01/{LANE_A_INTEGRATED_EVAL_01.md, LANE_B_DOMESTIC_NEW_01.md, LANE_C_OVERSEAS_NEW_01.md}`、`docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/SOURCE_REGISTRY_01.md`。並行Worker: (I)JA-ASR配線・(O)ニュアンス配線がコード・SSOTを編集中、(Q)視聴ページ試作がuser_test/dev配下。本委任のSSOT編集は自分の節・行の最小Editのみ(編集直前Re-Read)、index.lock衝突は数秒待って再試行。Lane cのcommit 27dea4a95はwork branchのみ=本委任のpush(`git push origin HEAD:main`)で一緒にmainへ入ることを確認。

## Fable裁定(統合時に必ず反映)
1. robotsがAI bot/AI利用を名指しで拒否するサイト(はてな匿名ダイアリー・Yahoo!知恵袋・弁護士ドットコムQ&A・PTT `ai-train=no` 等)は、規約が○でも**推奨一覧に載せない**(運営の意思表示を尊重=取得制限。内部記録に「○(規約)だがrobotsでAI拒否→非掲載」と残す)。
2. Grand Débat=◎維持、注記「取得は手動DL限定(robotsが/resourcesの自動取得を拒否)」、量産適性△。
3. Stack Exchange・The Conversation=未確認のまま非掲載。Hacker News・価格.com・Yahoo!ニュースコメント・MSE Forum(T&C非商用)=除外。MSE Forumの運営照会は任意UDR候補。
4. Harvard Dataverse(CC0逐語録)=◎だが固定データで継続性なし→量産適性△、「参加者同意の範囲と倫理」を注記。掲載可否は総合適性で判定。
5. 内閣府(www8.cao.go.jp)作文: `https://www.cao.go.jp/notice/rule.html`(PDL1.0)の適用範囲がwww8ドメインを含むかを規約文言で確認し、含むなら◎、不明なら○のまま。法務省人権作文(著作権主催者帰属)=○でも「翻案権が主催者に帰属=利用範囲に重大制約」注記、総合適性は低く扱う。
6. 掲示板型・生活密着型(ガルちゃん○/ママスタ○/note○)は維持して掲載(前回の誤り=Debate偏重の是正)。◎/○の意味は原文§3の定義どおりで、○を「AI利用が許可」と書かない。
7. 一覧は**合計20件以下**、国内/海外別、各サイト名に公式URLリンク。20件を埋めるために適性の低いものを入れない(B-5/B-8/B-9/Hashnode/Pantip根拠弱 等は原則非掲載)。選抜基準=商用◎/○(必須)→テーマ選定性×ペルソナ性×量産適性の総合。評価は各Laneの**実コンテンツ確認に基づく値**を使い、組合せ前提で単独評価を上げない。
8. 取得手順の逸脱(Lane a: Grand Débat Range取得1回・Stack Exchange API 1回、Debate調査: Kialo・Lemmy)を内部証跡に正直に記録し、レジストリ冒頭の取得運用注記に「取得前にrobots/Content-Signalを機械確認する共通fetcher経由のみ(直接urllib禁止)」を追記(既存規則の明文化、新Gateではない)。

## 成果物
A. `docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01/SHORTLIST_01.md`(ユーザー向け): 記号の意味(3行)→国内表→海外表(列=原文§5の5列: サイト名[リンク]|商用AI利用(◎/○+短い注記)|テーマ選定性|ペルソナ性|概要・特徴[得意テーマ・意見の特徴・人物像、2行以内])→短い総括(5行以内: 種別の内訳、国内/海外件数、◎×ペルソナ◎が存在しないこと等)→残る利用上の制約(箇条書き5件以内)→必要なユーザー判断(Production採用=UDR、任意照会)。長大な経緯・技術ログは書かない。
B. `EVIDENCE_01.md`(内部証跡): 掲載各サイトの規約URL・該当条項逐語・確認日/◎○の判断根拠/確認した実際の題材・発言(URL・要旨)/テーマ・ペルソナ評価根拠/取得制約・量産注意/除外サイトと理由(全件)/未確認(全件)/前回候補からの変更点(前回判定→今回)/取得逸脱の開示/探索の限界(検索エンジン不可等)。
C. `SOURCE_REGISTRY_01.md`: §6「2026-10-29 最終一覧(FINAL-SHORTLIST-01)」として掲載20件以下を10項目形式で追加・既存行は判定変更分のみ追記(価格.com除外/Yahoo!ニュース除外/Stack Exchange未確認/Grand Débat robots注記/Netmums・Participedia除外/内閣府PDL確認/MSE除外)。冒頭原則「登録≠継続利用承認」維持+取得運用注記追記。
D. SSOT: OPEN-587へ本調査の結論を追記しStatus=USER_DECISION_REQUIRED維持(新OPENは作らない)、`docs/pm/USER_DECISION_REGISTER_01.md`の#212(オープンライセンス系採用)を「最終一覧からの採用選択」へ追記更新+新規UDR(任意: MSE Forum運営照会)、`DECISION_LOG.md` 1件、`CURRENT_SPEC.md` Y情報源節に1行(最終一覧の参照)、ACTIVE_TASK(P)行更新。
E. commit(編集ファイル明示`git add`)→`git push origin HEAD:main`(FF)。
F. `docs/pm/RESULT_PACKET_FYS2.md`(整合/未承認機能/成果物と目的適合[原文§7の1〜9ごとに達成/未達]/判断候補/費用0/commit、`判定整合:`行)。最終回答は短く(掲載件数 国内/海外・◎/○内訳・種別内訳・commit)。

## 範囲(11-8)
範囲内=統合・選抜・記録・レジストリ/SSOT。範囲外=新規サイトの追加調査(必要なら「未調査」として記録)、Production採用、収集方式変更、Family Y生成仕様変更。
