Fableからの委任_02(FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01: 3 Lane統合+◎源の人物具体性の限定精読+レジストリ/SSOT反映。API(LLM)0、Production変更なし)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_委任_02.md` に逐語保存してから開始。`tools/stop_scope_check_01.py --managed-id FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/stop_check_02.json`(rc=3で停止)。
正本: ユーザー原文 `docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`(§3〜§9を全文)。入力: `docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/{LANE_A_OVERSEAS_EN_01.md, LANE_B_EUROPE_ASIA_CIVIC_01.md, LANE_C_DOMESTIC_01.md}`、既存 `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/{SOURCE_REGISTRY_01.md, TERMS_REVIEW_01.md, THEME_FINAL_01.md}`。並行Worker(I)がJA-ASR配線中(コード・SSOTの日本語ASR節を編集)。ACTIVE_TASKは(M)行のみ(編集直前Re-Read)、SSOT編集は自分の節だけ最小Edit、index.lock衝突は数秒待って再試行。

## Fable受入所見(Lane a/b/c受領。統合時に反映すること)
1. The Conversation(CC BY-ND 4.0)は○でなく**未確認(ND=翻案配布禁止。想定用途が翻案に当たらないと断定できない)**として推奨一覧から外す。
2. Hacker Newsは前回「未確認」→今回「除外」(YC規約逐語)。レジストリを更新。
3. 商用○の「何も禁じない型」(Tildes/Lemmy.world)は○のまま、注意事項に「AI利用の明示許諾なし・投稿者著作権は個別」を必ず残す。
4. 取得手順の逸脱(自己申告)をFINAL_REPORTとレジストリ注記に正直に記録: Lane a=Kialo(robots `Disallow: /`配下の規約ページ3件を単発取得。討論ページ未取得)、Lemmy.world(`Crawl-delay: 60`に対し公開API 20回を60秒未満間隔で実行→以後停止)。今後の収集規則として「robots/Crawl-delay遵守・手動相当の単発取得のみ」をレジストリ冒頭の運用注記に追記(新Gateではなく既存の取得規則の明記)。
5. Family Y適性◎は3 Laneとも0。◎ライセンス源(Polis/Grand Débat/Hansard/国会/審議会)は論点は豊富だが人物像が薄い=Debate系+体験談系の組合せが前提、という共通所見。

## やること
A. **限定精読(時間上限45分、◎ライセンス源の人物具体性を実測)**: 仏 Grand Débat National(data.gouv.fr、Licence Ouverte 2.0)の自由記述データのうち、「家族・働き方・車/移動」に関わる回答を**手動相当の単発取得**で読み(一括DLは公開データセットとして許容されるライセンスだが、取得量はテーマ1〜2件分に限定)、一人称の生活背景・職業・家族・感情が実際にどの程度書かれているかを、実例3〜5件(仏語原文+日本語要旨、回答ID/URL)で示す。Polis(CC BY 4.0)の公開コメントも同様に1テーマで実測。結論を「Personaの作りやすさ」の再評価に反映(上げる/据え置きの根拠を実例で)。
B. **FINAL_REPORT_01.md**(ユーザー原文§7の構成厳守):
   §A 推奨情報源一覧(国内/海外別、原文8列+規約URL・該当条項・確認日列。◎/○のみ。評価理由を各行に)。
   §B テーマ候補一覧(国内/海外別、原文9項目を各テーマに。3軸確認済みは実発言3系統が確認できたもののみ。AI構成案は明示分離)。Lane a/b/cの候補+精読結果を統合し、品質で選抜(数合わせ禁止)。
   §C PM評価用の事実整理(判断はFableが書くので、事実・数値・リスクだけ: 継続利用候補/Y向きテーマ/国内・海外の特徴/Debate系+体験談系の組合せ案と各組合せの商用Status/量産時の収集負荷・費用見積/規約残存リスク一覧/Production採用前に必要なユーザー判断の候補[挙証付き])。
   §D 探索範囲と偏り(評価サイト総数、規約本文を読んだ数、除外・未確認の内訳、取得逸脱の開示、未調査候補[Participedia/idebate/EU PETI/Surfvote再確認/Ask a Manager照会等])。
C. **SOURCE_REGISTRY_01.md更新**(既存形式・「登録≠継続利用承認」の冒頭原則維持): 新規候補(◎/○)を各10項目で追加、HN除外更新、The Conversation未確認、取得運用注記。既登録行の判定は変えない(新コンテンツ種別の追記は可)。
D. **SSOT**: `CURRENT_SPEC.md`のFamily Y情報源節(3249付近、Grepで特定)に「Debate/Discussion拡張調査(2026-10-29)結果: 候補登録のみ・Production採用はユーザー判断」の1〜2行追記。`OPEN_ITEMS.md`新規OPEN 1件(FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01、Status=USER_DECISION_REQUIRED、要点・参照)。`docs/pm/USER_DECISION_REGISTER_01.md`に新規UDR(分類D、挙証付き): (1)オープンライセンス系Debate源(Polis/Grand Débat/Hansard・英国請願/国会会議録/審議会)のProduction採用可否とCC BY出典表示の方式、(2)Debate系+体験談系(条件付き登録源)の組合せ方式の採用可否、(3)任意: Ask a Manager運営照会・Surfvoteメンテ明け再確認の実施可否。`DECISION_LOG.md` 1エントリ。ACTIVE_TASK(M)行更新。
E. commit(編集ファイルのみ明示`git add`)→`git push origin HEAD:main`(FF)。

## 範囲(11-8)
範囲内=統合・限定精読・記録。範囲外=本文生成/英訳/TTS/公開、新収集方式のProduction採用、禁止サイトの再調査、アクセス制限回避、レジストリ既登録判定の変更。

## 報告
`docs/pm/RESULT_PACKET_FYD2.md`: 整合/未承認機能/成果物と目的適合(◎/○件数、3軸確認済みテーマ数、精読結果)/撤去・残置/判断候補/費用0/commit。`判定整合:`行。最終回答は短く(件数・精読の結論1〜2行・新OPEN/UDR番号・commit)。
