FABLE-DELEGATION-MARKER: FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01-委任_01-20261023

# 委任_01: Family Z Standard 会話部分の6%減速撤去版(B)の制作とA/B比較試聴ページ(Trial、Production採用未決定・Production変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_委任_01.md`(N≈318〜328、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_USER.md` に逐語保存。
3. `docs/pm/ACTIVE_TASK.md`: 別agent(ASR-HOMOPHONE 委任_04)が並行中の可能性。編集直前に再読込し、OPEN-461の並行タスク1行を本管理IDの状態へ更新(他行は触らない)。有料呼出を行う場合は直前に同行へ「有料run進行中(時刻)」、終了後「有料run終了(時刻)」。

## 1. ユーザー指示原文(逐語)
```
# Claude Codeへの指示:Family Z Standard会話速度比較Trial

## 1. 目的

Family Z『走れメロス』『開いた窓』について、Standardの会話がやや遅く感じられるため、**会話部分のみ生成後6%減速を撤去したVersion**を制作し、ユーザーが速度感・自然さを比較試聴できるようにしてください。

**Status:Trial(Production採用未決定)**

現行Production仕様は変更しません。

## 2. Trial条件

対象作品:
- 『走れメロス』Standard
- 『開いた窓』Standard

比較条件:

| 項目 | A:現行版 | B:今回Trial版 |
|---|---|---|
| Narrator | 6%減速あり | 6%減速あり |
| 登場人物の会話 | 6%減速あり | **6%減速なし** |
| Voice | 現行のまま | 同一Voice |
| TTS生成Prompt | 現行のまま | 同一Prompt |
| 本文・台詞 | 現行のまま | 同一内容 |
| その他の音声・効果音 | 現行のまま | 変更なし |

Advancedは変更・再生成しません。

『走れメロス』の既存Voice割当も変更しないでください。

## 3. 実施方法・費用

- 既存のTTS原音が残っている場合、再生成せずに利用する。
- 会話clipのみ6%減速処理を外す。
- Narratorなどその他の音声は既存成果物を再利用する。
- 必要な再組立・音声QAを実施する。
- 原音が不足する場合は、対象と追加費用を確認し、必要最小限の方法で対応する。
- 独立した2作品の処理は可能な範囲で並列化する。

Trialの比較に不要なTTS再生成・本文再生成・追加検査は行わないでください。

## 4. 比較試聴ページ

**両作品について、現行版AとTrial版Bを切り替えて比較できる試聴ページ**を作成してください。

最低限必要な機能:

1. Standard A/Bの通し再生。
2. 会話部分のA/B個別再生(同じ台詞を直接比較できること)。
3. A/B間でVoice・本文・台詞が同一であることの確認。
4. 会話部分の実測速度(WPM)と変更前後の差の表示。

試聴ページは既存のシンプルな構成を再利用し、余計なUI開発は不要です。

## 5. 検証・受入条件

- 会話clipのみ6%減速が撤去されている。
- Narratorの6%減速は維持。
- Voice・本文・台詞・音声順序は不変。
- A/Bの通し音声が正常に再生できる。
- 公開試聴ページの音声リンク・再生を検証。
- 既存Production成果物を上書き・破損していない。
- 必要なGit反映・Trial証跡を記録。

Fableによる独立確認を行ってください。

## 6. Trial終了時の報告

以下を簡潔に報告してください。

- 『走れメロス』『開いた窓』それぞれのA/B試聴URL
- 会話速度の実測比較
- 音声QA結果
- 再生成の有無・実費
- 現行Productionへの影響がないこと
- Trial終了Status

**Trial版を正式Productionへ反映することは禁止します。**

Trial終了後は、ユーザーの比較試聴結果を待ち、`USER_DECISION_REQUIRED`として報告してください。

Production採用・既存完成音声の差し替えは、ユーザーが明示的に承認した場合のみ実施します。
```

## 2. 前提(Fable)
- 背景調査: OPEN-461 / `docs/pm/RESULT_PACKET_FZSPD.md`(Standardは後処理で全clip6%減速[実測1.050〜1.059]、会話の生成時減速指示は撤去済み、WPM表あり)。
- 『開いた窓』A=`er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/a2`(公開 `user_test/family_z_open_window_01/`)。
- 『走れメロス』A=**受入済み公開ページ `user_test/family_z_melos_02/` の元run**(provenance/index.htmlの記載・ファイルshaから元runを特定し報告する。`run_jre_01`は別の証拠runなので、公開版の元runを優先。特定できなければ理由を書いてSTOP報告)。
- 6%減速の実装箇所(er063の後処理、`_original.wav`等の原音保存の有無)はコードで確認。原音が残っていれば再生成なし。原音が無い会話clipは、**同一Voice・同一Prompt・同一設定**で該当clipのみ再生成(Production runには書き込まず、Trial dirに生成。Store登録もTrial用keyで分離するか登録しない)。再生成見込みが60円を超える場合はTTS開始前にSTOP報告。別agentの有料runが走行中なら終了まで待機(5分間隔・最大30分)。
- **Production成果物(両runのa2/b1b、公開ページ`family_z_melos_02`・`family_z_open_window_01`・`family_z_melos_jre_01`、Master Audio Store manifest)への書き込み・上書きは禁止**。Trialの作業は `er0XX_output/family_z_std_dialogue_speed_ab_01/<story>/` などTrial専用dirにコピーして行う。
- 本日の開発費累計は約54円+er109分。本Trialは300円自律枠内。

## 3. 作業
1. A版: 既存成果物(a2のassembled wav、timeline、clip wav)をTrial dirへコピー(読み取り元は無変更)。
2. B版: 会話clip(dialogue kind)のみ「減速前の原音」を使用(原音が無ければ上記条件で再生成→既存のASR QA[Production既定、Family Z判定器]を通す)。Narrator・その他clipはA版と同一ファイル(sha一致)。既存のassemble経路(er063/er026の組立関数)をTrial dirに対して実行して通し音声を再構築。無音間隔・順序はAと同一。
3. 検証: (i)会話clipの長さ比がA/B≈1.05〜1.06、Narrator clipはsha一致、(ii)順序・本文・台詞・Voiceの同一性(timeline/plan/speaker_tableの照合表)、(iii)B版の会話clipごとWPMとA版との差、作品全体の会話WPM中央値・平均、(iv)通し音声の再生可否。
4. 比較試聴ページ: `user_test/family_z_std_dialogue_speed_ab_01/index.html`(作品2つ、各: A/B通し再生、会話ごとのA/B並列再生[同じ台詞を隣接表示、話者・Voice名・テキスト・A秒/B秒/WPM A→B・差]、同一性確認の表[Narrator clip sha一致数、台詞テキスト一致、Voice一致]、全体WPM表)。既存ページscript(`er026_fz_*page*`等)を再利用し、mp3化(lameenc 128kbps)。commit/push後にHTTP 200+Playwright実再生(全audio)。
5. 証跡: `docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/TRIAL_RESULT_01.md`(条件表、元run特定、原音の有無・再生成数・費用出典、QA結果、WPM表、同一性証拠、Production無変更の証拠[対象runディレクトリ・公開ページのsha/`git status`差分0])。
6. SSOT: OPEN_ITEMSに新item(Status=`TRIAL_COMPLETE_USER_DECISION_REQUIRED`、OPEN-461を参照)、DECISION_LOG(Trial実施・Production未変更)、USER_DECISION_REGISTER(比較試聴の判断項目1件:『走れメロス』『開いた窓』それぞれA/Bどちらを採用するか+採用時の反映費用見込み)、REPORT_LEDGER。commitは明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。wavはpushしない(mp3のみ)。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- Production仕様・コード・既存成果物・公開ページの変更、Advancedの変更、メロスVoice割当の変更、比較に不要な再生成・本文再生成・追加検査、新Gate、Trial版のProduction反映。

## 5. 報告(docs/pm/RESULT_PACKET_FZSPAB.md、同内容を最終報告で)
(1)A/B試聴URL(作品別) (2)会話速度の実測比較(表) (3)音声QA結果 (4)再生成の有無・clip数・実費(出典) (5)現行Productionへの影響なしの証拠 (6)Trial Status (7)採用した場合の反映手順と費用見込み(参考) (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。