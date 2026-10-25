Fable転記、2026-10-25、条件A[Production配線]

## Opus独立技術レビュー(条件A): FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 案A Production配線設計 + 『告げ口心臓』再生成計画

**判定: 必須修正あり。設計の見直しは不要。** 下の修正5点を反映すれば実装へ進めてよい。Writer側の配線(W1〜W5)、Seed補完、runnerのコード変更0という判断は妥当と確認した。
- 確認した事実:
  - Prompt組立は`run_writer_chain`(730〜768行)が毎回Seedから作り直す純関数。初回・`--regenerate-stage`・resume・部分run・LLM技術retryのどれでも同じbuilderを通る。
  - resumeで再利用するかの判定には`ess.sha256`(narration_voiceを含む)が入る(781行)。
  - plan/support/kp/TTSは物語本文のPromptを組まない。
  - 『告げ口心臓』の話者設定(structure 304〜321行)は既に一人称前提。
  - Std側の共有ブロック(`er003_v1_n3_01_standard_a2_generate.py`)に人称の指定はない。
  - 本番コードからDEV runnerへの参照は0件。
  - Prompt本文に入る人称関連の指示は`REVISE_USER_TMPL`の141行と`_CONVERSION_SUBSTITUTIONS`の131行だけ。131行は、Grepした範囲で5作品の`er026_seeds`の`conversion_plan`に一致文言がなく発火しない。

### 必須修正
1. **【最重要】再生成計画③「tts_b1bとtts_a2を並列2process」はそのままでは動かない。**
   - 同じrun dirでは2本目が`FamilyZRunLockHeld`で起動を拒否される。`er062_family_z_structure_01.py:558-587`の`acquire_run_lock`が、run dir単位で`RUN_LOCK.json`を排他作成するため。
   - 加えて、5分間に3回以上起動すると`RESTART_STORM`でrun dirに`STOP`が自動作成される(607-636行。解除は`--clear-stop`のみ)。
   - 修正案: ③と④をまとめ、`--stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`の1起動にする(OPEN-480も満たす)。各起動の間は5分以上空ける。
   - 「並列2process」の記述は撤回する。直列化の理由は「同じrun dirの排他lock」。
2. **公開差替えの確認範囲にStandardを加える。** 旧Standardも旧三人称Advから作られているため、同じ問題を持つ。
   - (ii)の確認対象に`standard.html`と`audio_standard`(sha差分、全ファイルがrun_sf_prod_02由来であること)を追加する。
   - 「housemate」が無いことの確認(否定条件)だけでは弱い。両レベルの本文に一人称の`I`と、聞き手への`you`があることも、Fableが目視で引用確認する(自動判定は作らない)。
3. **runtime evidenceで「dumpされたPrompt=実際に送ったPrompt」を結びつける手順を明記する。**
   - `{stage}_prompt.txt`は、ensure_stageで本文を再利用した場合でも書き直される(768行)。dumpの存在だけでは送信の証拠にならない。
   - 受入時の手順:
     - (a) run_sf_prod_02でr0/r1/r2/std_adjustの4段すべてのstatusがgeneratedであること。
     - (b) 各dumpから`sha((dev or "") + "\n\n---\n\n" + user)`を再計算し、provenanceの`prompt_sha256`と一致すること。r1/r2のdumpはdevも区切りも含まないので、再計算式を合わせる。
     - (c) git HEADと`er062_family_z_writer_01.py`のfile shaを`RUNTIME_EVIDENCE_02.md`に記録する。これが「Trial専用経路ではない」証拠になる。
   - 新しいログ機構は不要。narration_voice自体はessentials_sha256とdumpで追跡できる。
   - PM Gateの「各工程」はR0/R1/R2/Std調整を指すと明記する(ユーザー原文§1の範囲。plan/support/kpは本文Promptを作らない)。
4. **W6(CPチェックリストのnarration行を「重大」にする)と、既存の`CP_TREATMENT_RULE`(803-808行、2026-10-23ユーザー承認)の文言を整合させる。**
   - 現在の(A)重大の列挙にnarrationが無い。このままだと「重大なのに処置規則の対象外」という矛盾が出る。
   - 推奨: (A)の列挙にnarrationを加える。根拠として10-25承認の§1(語り口維持)と§6(PRODUCTION_WIRED条件)を併記し、DECISION_LOGに記録する。
   - 処置は既存の明示`--regenerate-stage`と決定論パッチのみで、新retryや自動判定は入らない。承認範囲内と判断する。
5. **DEV runnerを昇格後に動かすと壊れることへの対処。**
   - `fz_essence_dev_runner_01.py`のarm iiiを昇格後に動かすと、Narration行が二重に入る。さらに`revise_dev`がテンプレートを先に置換するため、W3の`assert _REVISE_THIRD in tmpl`が失敗する。
   - 対処(どちらか):
     - (a) DEV runnerの先頭に、本番writerが`_NARR_LINE`を持っていれば停止するfail-fast guardを入れ、「歴史的」と注記する。
     - (b) 同runnerのtestは移植済みであることを確認し、全回帰の対象外として理由を記録する。
   - これを実装commitの前に決める。

### 推奨(任意)
- `ESSENTIALS_EXEMPT_STORIES == ("melos",)`を固定するtestを追加する。`in third person`の残置がMelos以外へ広がらないようにするため。
- 『賢者の贈り物』の`free_to_cut`に"the narrator's jokes and asides"があり、記入規則(c)と緊張関係にある。Trialとのbyte同一性を守るため、今回は変更しない。次回この作品を再生成するときに見直す、と記録する。
- R0の共通ブロック94行の例示(her mother/his father)は三人称の所有格になっている。Trialとbyte一致している範囲なので、今回は変更しない。

### 論点別の所見
- **(a) 配線の網羅**: 漏れは見つからなかった。retry(`llm.call`)はPrompt固定。`_bak_*`と`STALE_*`はplan以降の段なので、本文Promptには関与しない。
- **(b) Seed必須化**: W4(`Essentials.__init__`)とW5の2か所で必須化し、置換条件を`essentials is not None`に揃える。この設計で第3状態(essentialsはあるのに語り口欄が無い)には到達しない。妥当。
  - **Melos**: 残置を「受容して記録」で可とする。理由: 原作が三人称で、承認と矛盾しない。汎用句に置き換えるとMelosのbyte同一性が崩れる。完了報告の§2に「Melos専用経路に原作どおりの三人称指定を残置」と明記する。
  - **『二十年後』**: 「受容して記録」。既存Seedの`conversion_plan`はBobを主役に置いており、"close on Bob"はこれと一致する。視点がBobに寄ることで、結末前に警官の正体を伏せる働きとも矛盾しない。有料の追加確認は不要。API 0の構造test+次回再生成時の初回CPで足りる。
- **(c) 「役割で呼ぶ」指示との整合**: Narration行は「人称・視点・語り手の立場を保つ」という汎用1句だけ。新たな文学基準や作品別の禁止ルールは含まれていない。
- **(d) 既存作品の副作用確認**: Prompt byte一致16/16+Trial結果の再利用で、必要十分と判断する。猿の手の段落数+8は限界として記録すれば足りる。告げ口心臓の`free_to_cut`差替えは承認範囲内と判断する。Trialで検証した条件そのものである。現行の「the narrator's repeated arguments that he is wise and cunning」はユーザー原文§4-3(自己正当化)と矛盾する。DECISION_LOGに、案AのSeed補完の一部として根拠付きで記録する。
- **(f) S-1(既存run dirでSeed sha不一致STOP)**: M3(受容して記録)で可。影響はplan/support/kpのみ(`_prov`を呼ぶのは1421/1440/1697行だけ)。注意: 試聴待ちの既存Z作品で、KPやsupportをその場で直す必要が出た場合はSTOPする。そのときはM4(provenanceの付替え手順)を別委任で作るか、新runで作り直す。
- **(g) 撤退とX/Yへの波及**: 単一commitのrevert+STALE退避+公開物の差替えを別commitにする、で十分。X/Yとの共有は無く、波及は無い(er111はnarration_voiceを参照しない)。
- **(h) 再生成計画**: 段階分割と、CP確認をstd_adjustの後・planの前に置く点は妥当。予算70円は前例と同じだが余裕が少ない。TTSの段別見積は各40円で、着手時の累計約22〜29円に足すと62〜69円になる。LR等で費用が増えると、guardでSTOPしうる。STOPしても安全側の停止であり、300円以下の範囲で上限を上げるのはAI自律で可。事前に80円程度へ上げておく選択肢もある。

### リスクと対処
- 並列TTSで二重起動を拒否される、またはRESTART_STORMでSTOPする → 必須修正1。
- 旧Standardが残る → 必須修正2。
- 本文を再利用したdumpを証拠と誤認する → 必須修正3。
- DEV runnerを誤って再利用し、二重注入になる → 必須修正5。

### ユーザー判断が必要になりうる論点
現時点ではUDRは不要と判断する。Melosの残置と、CP処置規則へのnarration追加は承認範囲内の整合作業として扱う。どちらも完了報告とDECISION_LOGに明記して、透明性を確保すること。
