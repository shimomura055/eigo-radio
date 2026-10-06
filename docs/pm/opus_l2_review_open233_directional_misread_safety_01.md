# Opus独立技術レビュー(条件A): OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01

日付2026-10-06、opus-consultant、read-only、¥0、Part 1=事前スキャン(信号喪失箇所・同型誤読)、Part 2=設計doc評価。Fable照合結果は設計doc §14

## Part 2(逐語)

### 総合判定: 条件付きで進める(限定Trial提案へは、下の必須修正3点を反映してから)
1. 案E(LLMが枠を抽出し、Python側で比較する)という方向性は妥当です。ただし、Ledger側と記事側の抽出を別々に、記事側はLedgerを見せずに(blind)行わないと、相関は断てません。
2. 【確# Opus Part 2レビュー 抜粋(U1〜U3、逐語)

### U1. 同一モデルの相関誤りを減らせるか
- 結論: 「1回のcallで両側を抽出」する方式なら、旧verifyとほぼ同じで相関は断てません。2つの条件をそろえて初めて、実質的に断てる見込みです【推測】。条件はLedger側を記事から独立して事前抽出すること、記事側をLedgerを見せずに抽出すること。
- 根拠: 【確認】HC-012のLedger原文は「機能を当面ロールバックした」です(`er019_output/meta/run_03/storyline_b3/full_ledger.json` L3)。記事の「restored the human concierge feature to the way it had been before」は、「roll back=以前の状態へ戻す」の直訳的な言い換えになっています。誤読の正体は、多義語「ロールバック」(状態を戻す/機能を撤回する)の解釈です。そのため、枠「向き・結果状態」を自由記述で抽出すると、両側とも「以前の状態へ」となり、Pythonで比較しても一致します。抽出タスク自体が同じ読み癖に汚染される経路は具体的に存在します【推測、根拠はLedger原文と記事文】。§7改訂がbaseにしている「1 schemaで両側」方式では、モデルが両側を見て辻褄を合わせるバイアスが残ります。
- 推奨: (1)枠の値を動詞でなく「対象Xの事象後の状態」の固定値(enum)にする。例: 利用可能/停止/一時停止/増加/減少/不変/未言及/不明。(2)Ledger側はfactごとに1回、記事文脈なしで抽出してキャッシュする(F1のT-D'と同じ成果物)。(3)記事側には「対象X」だけを渡し、Ledgerの値は渡さない。(4)別モデルの必要度は、Ledger側=高(factごとで安価なので2モデル一致を推奨)、記事側=中(blindなら同じモデルでも可【推測】、Trialで検証)。

### U2. T1〜T6の線引き
- 結論: 判定(BLOCKING)の対象を第1段=T1+T2に絞るのは妥当です。ただし、T3/T4も同じcallで「観察欄として抽出するだけ(判定しない)」を推奨します。
- 根拠: T1/T2は固定値の比較に落とせます。T3/T4は主体名の言い換え(contract workers / human staff / people)をPythonで文字列比較することになり、照合が誤爆の主因になります【推測】。T4(未指定の役割の充填)は「Ledgerに書いていない」ことを示す必要があり、さらに難しい作業です。
- 推奨: 同じcallで主体/相手の値を記録だけしておき、第2段の判断材料(誤爆率)をタダで集めます。T5/T6を対象外とすることには同意します。

### U3. 過剰Safetyへ逆戻りしないか
- 結論: 判定が「固定値の不一致」かつ「両側の逐語引用あり」に限られるなら、一律厳格化には当たりません。ただし、母集団が全文に広がるため、誤逆転率が小さくても件数が効いてきます。抽出失敗=BLOCKINGは過剰Safetyの再来になります。
- 根拠: §8改訂 L289「抽出失敗・引用なしはBLOCKING→Rewrite」は、§5 L193「判定不能として未解消のまま記録」およびL201「引用がなければ逆転を採用しない」と矛盾します。誤爆の経路は4つあります。(a)対象Xの取り違え(同じfact内の別の事象。HC-012は「ミスを認めた」と「ロールバック」の2事象を持つ)(b)一時性の差(停止と一時停止を逆転扱いしてしまう)(c)文が対象Xに触れていない(未言及を不一致扱いしてしまう)(d)比較の基準のずれ(T2)
- 推奨: Ledgerの枠を事象のリストにし、記事側に「どの事象か」を引用付きで選ばせる。未言及は通過、一時性の差は逆転にしない。抽出・API失敗は1回retryし、なお失敗なら未解消記録+QUALITY(BLOCKINGにしない)。§5のルールは「明確な逆転=BLOCKING/一致=通過/曖昧=別モデル→QUALITY」なら妥当です。
### U4. 既存Checker信号を捨てている他の箇所
- 結論: §13に3点漏れがあり、いずれも案Eの結果が無視される経路です。
- (新1)SUPPORTED判定の文が後段へ行かない【確認】: checker L636-645。決定論検査に理由がなければSUPPORTEDで終わり、Stage 2へ行きません。→案Eの適用点は、Stage 2の記録ではなくStage 1の全単位(`support_fact_ids`付き)にする必要があります。
- (新2)逆転判定をStage 2候補として流すと、Stage 2/S1が同じ読みで再降格する【推測、HC-012の実績から】。→precheck_floor経路(runner L8784-8789、Stage 2を通らず直接BLOCKING)と同じ迂回が必要です。S1/2-of-2の対象条件(L4141-4148/L4086-4093)から外れることも確認すること。
- (新3)Rewrite後に逆転が残ったときの出口【確認】: Stage 4の許可理由はL8307-8311で、BLOCKING由来の理由は「Stage 2(+S1)でBLOCKING確定」を条件にしています。Stage 2を迂回した案E BLOCKINGは`not_funnelled`で差し戻され、宙に浮き
### F1. T-D / T-E / T-C のどれを第1案にするか
- 結論: 第1案はT-D'(T-Dの修正版)です。factごとにLedger側の枠を1回抽出し、それを分類も兼ねさせます。そのうえで、状態変化・比較を含むfactに紐づくStage 1の全単位(SUPPORTED含む)へ、記事側をblindで抽出します。T-Eはfalse negative監査用(Trial時だけ全件)、T-Cは不採用(補助としても不要)とします。
- 根拠: T-Dの分類は記事文脈を見ないため、Writerの誤読は伝播しにくいです。Ledger側の抽出と同じ成果物なので、追加費用もほぼゼロです。汚染リスクは「分類」より「向きの値の解釈」にあるため、2モデル一致で抑えます。2モデルが割れたfactは、そのfactだけ全単位を対象にしてQUALITYへ倒します。件数の見込み(§4/§7の13.7件/run)は、母集団の誤りにより再集計が必要です。全単位はその数倍と見込みます【推測】。¥0で数えられます。
### F2. 数字floor穴と`apply_stage2_two_of_two`(逐語未保存)
- 逐語転記はSonnet API中断(3回)により未保存。要旨: 両者とも別管理IDを推奨。数字floor穴=承認済み構成(FLOOR_MODE=number_only)の意図どおりの配線是正、新floorではない、ユーザー一言確認+¥0 replayで足りる、新9 run実害0。`apply_stage2_two_of_two`(runner L4106-4122)は`claim_identity`=`fact:<id>`(L1424-1429)で兄弟文を上書き、現在OFFのため再有効化前提条件として記録。S1(L4176-4201)はindex対応で問題なし。
- 出典: 設計doc §12(6)・§13、OPUS_FINDINGS_LEDGER OF-057。

### F3. §9改訂の限定Trial案は十分か
- 結論: このままでは不十分です。陽性(真の逆転)サンプルが少なすぎ、「忠実文を一致と返す」側の対象も正しい母集団になっていません。
- 追加すべきもの: (1)HC-012に紐づく実文32文の全件(合成4文ではなく)。A4-1と「rolled back」系の忠実文を含めます。(2)状態変化factごとの、Stage 1でSUPPORTEDになった実文(実際の運用で案Eがかかる母集団)。(3)Fableが事前に作る、合成の反転文10〜20件。複数fact分を、LLMを使わず決定論で作ります。gold非変更・Trial専用です。(4)比較条件: 1 callに両側 vs 2 call blind、同モデル vs 別モデル(Ledger側)。相関を断てるかという仮説そのものの検証です。(5)HC-012とA5-0は各3回以上繰り返す(ばらつきの分離)。(6)Ledger側の正解の枠を実行前に固定する(事前登録)。
- STOP条件の書き方: 絶対件数ではなく、「誤逆転率×全単位数=1 runあたりの不要Rewrite見込み」で事前登録すべきです。比較対象は現行のRewrite約0.67件/runです。費用は増やしても約¥15以内の見込みです【推測】。

### F4. 設計docの誤り・矛盾・Dangling Reference
- §4 L177・§7改訂: 「T-E 123=fact紐付き全件と同数」は誤りです(上のU4 新1)。
- §8改訂 L289 と §5 L193/L201 が矛盾しています(上のU3)。
- 名前の衝突: §3 L123「代替E(語彙トリガ)」と、§8旧 L282「採用しない案: E/T-C主導」が、新しい「案E(枠抽出)」と同名です。旧Eは改名が必要です。
- §1表「S1 … runner L4055」: L4055はrun_stage2の結果組み立て部分で、S1本体はL4160-4203です。
- §12 L396のユーザー判断事項(1)「案D」は撤回候補のまま残っており、整理が必要です。
- 【未確認】§3 L116「runner L2760(旧verify)」は今回照合していません。
- 参考【確認】: HC-012の記録には`dev.severity_final=BLOCKING`(rule `existing_major_v2`)が付いていますが、`materiality`はACCEPTABLEです(meta_run03_advanced.json L366-376)。これは全候補共通のMAJOR写像で、方向の信号ではありません。

### Fableがユーザーへ提示すべき判断事項(推奨案付き)
1. センサーの差し替え: 決定論検査をT-D'(Ledger側の枠を事前抽出+状態変化fact紐付きの全単位へ記事側blind抽出)に置き換えるか。推奨=採用。ユーザー仮説の「センサー→専用確認」の構造は維持しつつ、センサーの実体を差し替えることになる点を明示します。
2. 別モデルの使用: 推奨=Ledger側は2モデル一致、記事側はTrialで同モデルと別モデルを比較して決める。
3. 抽出失敗時の扱い: 推奨=1回retry→未解消記録+QUALITY。BLOCKINGにしない(§8改訂を修正)。
4. 逆転BLOCKINGの経路: 推奨=Stage 2/S1を迂回する(precheck_floor型)。解消はPython再比較で判定する。Rewrite上限到達時はHuman Reviewへ振らず、「STOP」か「QUALITY記録で通過」のどちらにするかをユーザーが選ぶ。
5. T3/T4: 推奨=観察欄として記録のみ、判定には使わない。
6. 数字floor穴・#8: 推奨=別管理ID。数字floor穴は「承認済み構成の意図どおりにする配線是正」として¥0 replay付きで確認します。
7. 限定Trial(有料、約¥15以内見込み)の承認: 上のF3の対象追加と、STOP条件(1 runあたり不要Rewrite見込み)を事前登録したうえで依頼します。¥0のT-D'母集団再集計を先に行うことを推奨します。

主な参照: `er052_open233_stage1_coverage_checker_01.py`(L496-561, L612-648)、`er052_open233_self_recovery_flow_runner_01.py`(L1424-1429, L4086-4203, L8307-8323, L8763-8789)、`er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json`(L330-406)、`er019_output/meta/run_03/storyline_b3/full_ledger.json`(L3)。

## Part 1要約(Fable作成。逐語ではない。詳細は設計doc §13)
- Checkerの`issue`/`flags`/`sub_reasons`はStage 2 promptへ渡っていない(calib L652-662)。S1は同入力。DV/Tier0はissueを見るが承認構成でOFF。Recheck `prior_issues`はBLOCKINGのみ。S-4非BLOCKING再利用(runner L8765-8775)のキーにsub_reasonsなし。出口検査はRewriteがあった記事のみ。再分類filterはmodel由来候補のみ。Rewrite hintに決定論理由名がそのまま入る。
- HC-012の否定センサー反応はLedger行「開示なし」への偶発反応の可能性→委任_02dで確認済み(真)。
- 系統的誤読の型: T1状態変化の向き反転(A5-0/HC-012)、T2推移・比較の向き反転(委任_61/HF-009)、T3当事者取り違え(A4-0)、T4未指定役割の充填(A2A3-0/HF-003)、T5因果・条件の捏造(B3/B4-a)、T6可能性の既成事実化(軽微)。共通核=語彙はLedgerと重なるが事象の枠が1つ入れ替わる。
- 代替案: 判定役でなく抽出役(枠を別々に抽出、Python比較)。最単純案: Stage 2へissue渡し(priming前例=委任_16)。
- 潜在不具合: `apply_stage2_two_of_two`(L4106-4122)が`fact:<id>`キーで兄弟文を上書き(現在OFF)。数字floor穴: `number_not_in_fact`が`changed_number`へ未変換。
- 入力限定に使えるデータ: claim_text/local_context/related_fact_id/unit_ids、`floor_verify_fact_block`、`ledger_block_fields`、DV骨組み(L3584-3628)。取れない: r3の`ledger_quotes`、`support_fact_ids`2件目以降。
