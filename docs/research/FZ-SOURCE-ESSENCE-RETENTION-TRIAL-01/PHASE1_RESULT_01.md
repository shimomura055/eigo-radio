# PHASE1_RESULT_01: 『告げ口心臓』Advanced Phase 1(1a対照実験・1b全段・1c音声化)結果

作成: 2026-10-25 / 評価基準=`PREREGISTERED_CRITERIA_01.md`(生成前commit e7783bc73)。モデル=Production同一(gpt-6.1-sol effort=high、最新世代推奨モデル原則に該当)。評価LLMなし(決定論指標+Sonnet暫定読み。**最終判定はFable**)。
Status候補(Sonnet所見): Phase 1は決定論基準を概ね満たし(段落数のみ事前基準外)、案Aが語りの質で(ii)より優位。`VALIDATED`候補だが判定はFable。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。

## 1a. 対照実験(R1のみ、固定入力 Production r0.md、3アーム×2本=6 call、実費18.81円)
出力: `er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1a/<arm>_s<k>/`(r1.md・r1_prompt.txt・meta.json)、集計=`1a/metrics_1a.json`、盲検=`1a/BLIND_1A.md`+`BLIND_KEY_1A.json`、読み=`1a/READING_1A.md`。
| アーム | s | 語数 | 一人称語 | 三人称語 | you | 反転 | 人称合格P | 読み点(q1+q2+q3) |
|---|---|---|---|---|---|---|---|---|
| (i) 現行文言 | s1 | 428 | 0 | 54 | 0 | **反転** | × | 1 (C) |
| (i) 現行文言 | s2 | 408 | 0 | 46 | 0 | **反転** | × | 2 (D) |
| (ii) 汎用置換のみ | s1 | 422 | 41 | 27 | 2 | - | ○ | 4 (A) |
| (ii) 汎用置換のみ | s2 | 440 | 43 | 25 | 2 | - | ○ | 4 (F) |
| (iii) 案A | s1 | 435 | 44 | 23 | 5 | - | ○ | 6 (B) |
| (iii) 案A | s2 | 419 | 43 | 21 | 8 | - | ○ | 6 (E) |
基準本文: r0 = 一人称語44 / 三人称語23 / you4。
- **反転の再現(撤退条件1を否定)**: (i)現行文言は2/2サンプルで一人称が0語に反転(r0の一人称44語→0語、you4→0)。**R1の固定文言"in third person, "が人称反転の直接原因**であることを、同一入力・R1のみの対照で再現確認した(ROOT_CAUSE_01 §6の反証の実行)。
- **人称は汎用置換(ii)で足りる**: (ii)Seed欄なしでも一人称語41〜43を維持(P合格)。したがって人称維持だけなら**REVISE固定句の汎用置換だけで足りる**(欄は人称には不要)。
- **語りの質は(iii)が(ii)より明確に優位**(Sonnet暫定、盲検コード読み、平均 6.0 vs 4.0。READING_1A.md): (iii)は「Would a madman speak so calmly?」「Slowly, you understand」「I almost laughed at my own skill」「You see how careful I was?」など、自信満々の語り口と聞き手への呼びかけが機能。(ii)は一人称ではあるが呼びかけは冒頭のみ(you 2)で、自己陶酔の語りが薄い。**規則(PREREGISTERED §1-4)により(iii)=欄が要る**を採用。
- 限界: 各アーム2サンプル・Sonnet読み(完全盲検でなくyou密度からアームを推測できた)。差の大きさは示唆。Fable読みで再採点してください。懸念: (iii)s2はyou=8で上限(≤8)ちょうど。過剰忠実の兆し(「You see...?」「You can imagine...」)あり=1bで確認。

## 1b. 全段チェーン(R0→R1→R2→Std、案A、DEV Seed、2サンプル、実費30.56円)
出力: `.../the_tell_tale_heart/1b_s1/writer/`・`1b_s2/writer/`(r0〜std・各prompt・provenance・cp_checklist)。比較原稿=`COMPARISON_01.md`。
| 本文 | 語数 | 段落 | 平均文長 | 一人称語 | 三人称語 | you |
|---|---|---|---|---|---|---|
| 基準 現行r2(sf_prod) | 431 | 22 | 6.95 | 0 | 51 | 0 |
| 基準 現行std | 437 | 22 | 8.57 | 41 | 26 | 1 |
| 1b s1 Adv(r2) | 414 | 17 | 6.27 | 42 | 23 | 5 |
| 1b s1 Std | 443 | 17 | 9.04 | 48 | 29 | 7 |
| 1b s2 Adv(r2) | 409 | 17 | 6.01 | 43 | 24 | 4 |
| 1b s2 Std | 424 | 17 | 9.02 | 45 | 23 | 5 |
### 決定論基準(PREREGISTERED §2-1)
- Adv一人称維持(一人称語≥30かつ>三人称語): s1 42、s2 43 **○○**。 you 2〜8: 5、4 **○○**(過剰忠実上限 ≤8)。
- Std: Advと人称一致(一人称語>三人称語)かつ you 1〜8: s1 (48>29, 7)・s2 (45>23, 5) **○○**。`check_std_guardrails` failures 0(warningはSTD_AVG_SENT_LEN_NOT_SHORTER=soft gateのみ。s1 9.04 vs Adv 6.27、s2 9.02 vs 6.01。既存Productionと同種のWARN)。
- 語数330〜470: Adv 414/409、Std 443/424 **○○**。
- 平均文長: Adv 5.21〜8.69 → 6.27/6.01 **○○**。Std 6.43〜10.71 → 9.04/9.02 **○○**。Std段落=Adv段落(17=17、17=17) **○○**。
- **段落数 19〜25(基準22±3)→ 17 / 17 × ×(事前基準の未達)**。事前固定の副次指標で、Fableの委任文が列挙したゲート項目(Adv一人称維持・Std you≥1かつ人称一致・過剰忠実なし・語数と文長が既存幅内・心理/心臓音/自白/因果の保持)には含まれない。**基準は変更せず未達として報告**し、ゲート列挙に従い1c・Phase 2へ進んだ。解釈: 段落数は同じProduction chainのstage間でも揺れる(Phase 2猿の手の完成版でもr0 48→r1 38→r2 32)。1aでは同じ入力から23〜27段落が出ており、案Aに固有の短縮傾向は見られない(1bのr1/r2で17へ統合されたのは短行"Always closed."等の統合)。ノイズ帯の根拠は参照1点のみで確定できない=限界。
- 3点の幅(OPUS推奨): 語数 414/409/431、平均文長 6.27/6.01/6.95、段落 17/17/22、you 5/4/0(sf_prod現行)。既存sf_prodはPromptが異なる(固定文言)ため純粋なサンプリング揺れではなく、参照1点のみで幅は狭い/広いの双方の限界がある。

### essentials保持(CP、Sonnet記入・引用。Fable確認)
| 項目 | 1b s1 Adv | 1b s2 Adv | Std s1 / s2 |
|---|---|---|---|
| ending_reveal(自白+最終行) | “I did it!” I screamed. “Tear up the planks! Here, beneath my chair! It is the beating of his hideous heart!” | “Stop pretending!” I screamed. “I did it! Tear up the planks! Here, under my chair! It is the beating of his hideous heart!” | “I killed him!” ... “That is the sound of his horrible heart beating!” / “I killed him! Pull up the floorboards...That is his terrible heart beating!” |
| withhold(結末前の示唆・事後なし) | 付加文なし、自白で終わる | 同左 | 同左 |
| setup1(感覚が鋭い→最後に心臓音) | “I hear everything in heaven and earth. Listen, and judge how calmly I tell you what happened.” → “Beneath their voices came a low, quick beating.” | “I hear everything in heaven and earth. Notice how calmly I explain it all.” → “No—a low, quick beating.” | 保持 / 保持 |
| setup2(vulture eye、7夜閉じ→8夜目に開) | “A vulture’s eye.” / “Always, the eye was closed.” / “Wide open.” | “A vulture’s eye!” / “Always closed!” / “wide open.” | 保持 / 保持 |
| key_role 語り手(無名・一人称) | "I"、名前なし | 同左 | 同左 |
| key_role 老人・警官3人 | “The old man shared my house.” / “three police officers” | 同左 | 同左 |
| key_causality(7夜→8夜目→心臓音→恐れ→殺害→床下→警官→再び音→自白) | 全て順序どおり | 全て順序どおり | 同左 |
| narration(一人称+you) | “You call me mad?” “Imagine such control!” “You see how little I feared?” “How could you expect me to sit there and bear it?” | “Listen to me before you judge.” “Was that not clever?” “You would have admired my work.” “How could a madman be so confident?” | “You must admire how I stood still” ...(Std s1 you=7)/“You can see how clever I was, can’t you?” |
欠落0(Sonnet読み)。KP(音声化時): `sharpen someone's senses` / `bear it` / `hideous heart`(人称一般化済み、CANONICALIZATION_PASS)。

### Fable読み7観点(Sonnet暫定、各0/1/2。最終判定はFable)
| 観点 | Adv s1 | Adv s2 | 所見 |
|---|---|---|---|
| 1 一人称の語り維持 | 2 | 2 | I全編、名なし |
| 2 聞き手への呼びかけ | 2 | 2 | s1 「You understand?」「You see how little I feared?」/ s2 「You understand: only that eye had to go.」「Nothing to hide, you see.」 |
| 3 異常な心理・執着 | 2 | 2 | s1 「I smiled at my own patience」「Imagine such control!」「Would a madman have worked so neatly?」 / s2 「Was that not clever?」「I smiled at my own skill」 |
| 4 緊張の積み重ね | 2 | 2 | 光の筋・「Wide open.」・音が増す・椅子を擦る |
| 5 心臓音・自白・因果 | 2 | 2 | 保持 |
| 6 英語レベル・聞きやすさ | 2 | 2 | 平均文長6.0〜6.3(現行6.95)、語彙B1-B2 |
| 7 通読の総合(現行r2より良いか/r0に並ぶか) | 2 | 2 | 一人称・自己陶酔の声が戻り、r0に並ぶ。現行r2(三人称)は心理の内面描写が外面化していた(ROOT_CAUSE_01 §3(4))のに対し明確に良い |
過剰忠実の観点: youはAdv 5/4(r0は4、上限8)で単調ではない。ただしStd s1はyou=7で上限近く、「You must admire」「you see my courage?」「How could you expect me」が連続する箇所あり=Stdの呼びかけがやや多い(Fable確認点)。テンポ低下は見られない(語数409〜414は現行431より短い)。

## 1c. 音声化(Adv 1本=1b s1、既存Z正式TTS/Gate経路のDEV呼び出し、実費9.10円、JST 08:10:33-08:17)
- 呼び出し: `fz_essence_dev_audio_01.py`(Production runnerをファイル無変更のままimportし、メモリ上でのみ出力root/seed dir/pages dirをDEVへ差替え・LEVELSをb1bに限定)。stage = plan,support,kp,tts_b1b,provision_shell,gate,assemble。Production run dir・公開ページには書いていない。
- 結果: gate `shared_gate: PASS`(M2完了、`audio_text_deviation_clips=[]`、z_speed_v2全clip ok)。HR Lock・approve_regenerate: **なし**(`human_review_queue.jsonl`未生成)。通し音声 **273.8秒**(wav `.../1b_s1/b1b/assembly/Family_Z_the_tell_tale_heart_b1b.wav`、headroom補正なし)。
- 注: plan/support/kpは経路の仕様上Std(a2)も処理するため(kp a2を含む)、Adv音声化の費用(9.10円)にはStd分の少額LLM費が含まれる。TTSはtts_b1bのみ(Std音声は作らない)。
- 試聴ページ: `user_test/fz_essence_trial_01/index.html`(現行Adv[三人称]とTrial Adv[一人称]の比較。公開URLはpush後に確認)。公開版 `user_test/family_z_tell_tale_heart_01/` は不変。標準ページcheck(`er_user_listening_page_common_01`)は、StandardとAdvancedの2レベル+再生順script等を前提とする本番ページ用のため、比較用のこのTrialページには適用していない(N/A)。

## 結論(Sonnet所見)
1. 人称反転の原因はREVISE固定句(再現2/2)。2. 人称維持だけなら汎用置換で足りるが、**語りの質(自己陶酔の語り口・聞き手への呼びかけ)は欄(narration_voice)+Narration行が効いた**(1a平均 6.0 vs 4.0)。3. 1bは2/2サンプルで決定論基準(段落数を除く)を満たし、essentials欠落0、音声Gate PASS。4. 限界: サンプル少数・Sonnet読み・段落数が事前基準外・Std youがやや多い。
