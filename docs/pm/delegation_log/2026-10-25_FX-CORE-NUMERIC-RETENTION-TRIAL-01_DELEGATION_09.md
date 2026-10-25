FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_09(月の記事run_ms_03 Std `japanese_title`のHuman Review Lock: 人間判断用の試聴clipを限定公開。API 0、Lock解除・回避・再生成は行わない)。あなたはsonnet-worker。Fable(PM)からの委任。

## 背景
委任_08報告: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/`の`japanese_title`(「月のしわ、8,900本超！…」)が3回ともSTOPPED(1回目: OpenAI ASRが「8000・800本」と転写しp1_value_diff NG/2回目: Azure副ASRは「8900本」と正しいが`secondary_not_accepted`で主ASRに別の誤り/3回目: minimal_fallbackでもNG)→HUMAN_REVIEW_LOCKED。証跡`a2/audit/review_lock_state.json`。Advは全48 segment OK・組立済み。

## 作業
1. 3 attemptの題wav(存在するもの全て。attempt別のpath・ASR転写・判定理由を`review_lock_state.json`/results/auditから特定)をmp3化し、`user_test/family_x_moon_shrinking_02/hr_title/`へ置く。簡易ページ`index.html`(noindex、一覧非掲載、「Human Review用・完成候補ではない」注記): 各attemptの再生ボタン、台本テキスト(題の全文)、主ASR転写・副ASR転写・判定理由、聴くポイント(「8,900本超」が「はっせんきゅうひゃっぽんちょう」等と正しく読まれているか、他の語の読み誤りがないか)。Advの組立済みwav(`b1b/assembled/Family_X_Audio_B1_MOON_SHRINKING.wav`)も参考として同ページ内に「Advanced完成候補(参考)」としてmp3で置く(公開差替えではない)。
2. push後、HTTP 200を確認(デプロイ待ちは再試行)。
3. HR承認後の再開手順(Fable権限の`approve_regenerate`相当のコマンド全文と、`--stages provision_shell,gate,assemble,pages,page_verify`での再開コマンド、想定費用≈0円〜数円)を`docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/HR_TITLE_NOTE_01.md`に記載。あわせて事実の整理: 「8,900本超」は欄(E)外の中核数値で、規則5で許可・O-2'は同単位系(m)のみ対象のため題に使われた(検証済み設計どおり)、を1段落で。
4. OPEN-507に「Std japanese_title HR Lock、人間試聴待ち、試聴URL」を1行追記。`docs/pm/RESULT_PACKET_FXNR9.md`、ACTIVE_TASK自行。委任文逐語保存(抽出tool、冒頭「FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_09」で照合)。
5. Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`→`git push origin HEAD:main`。wav不追跡(mp3は`user_test/`配下のみ)。secret grep 0件。Production file変更0。

## 報告
(1)試聴URL (2)attempt別の転写・判定理由の表 (3)再開手順と費用 (4)commit。「判定整合」1行。
