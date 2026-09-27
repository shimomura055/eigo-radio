# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT

## Stage 3a(2026-09-27): Meta記事(Entertainment News)のruntime実行

Stage 1(commit `32430691`、runner/plan実装+dry-run、¥0)の続き。実TTS/ASR/
Assembly APIを実行し、runtime evidenceを取得した。入力はユーザー確認済みの
Meta run_01(`er019_output/family_x_b3_production_wiring_01/run_01`)。

### 1. 実行前に判明したbug(所有ファイル内、最小修正)
Stage 1では`--stage scaffold/tts/assemble`が未実行だったため顕在化しな
かった、`er019_family_x_audio_production_runner_01.py`内の2件の実装bugを
本Stageで修正した(既存Production module=`er003_*`/`er006_*`/`er020_*`等は
無編集):
1. `main()`のA2 `japanese_title`受け渡しが、`a2/article.md`の英語title
   をそのまま渡すStage 1時点のplaceholderのままだった。正式path
   (NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01)が生成した
   `ja_writer/runtime_evidence.json["title"]`から日本語titleを取得する
   `derive_japanese_title()`を追加し、これを使うよう修正。
2. `run_plan_stage()`の`article_sha256`が常に`None`固定だった。実際の
   sha256を計算するよう修正(`sha256_text()`追加)。

あわせて、要求されていた成果物(player.html、cost budget guard、cost
logger install)を本ファイル内に追加実装した(`build_player_html`/
`assert_budget_ok`/`compute_cost_jpy_so_far`/`cl.install()`呼び出し)。
Unit test 25/25 PASSを維持(dry-runの¥0・副作用ゼロ契約も回帰確認済み)。

### 2. 入力article.mdの不変性
- `a2/article.md` sha256(raw bytes、`sha256sum`): 
  `5fed4170a97251f1e679bb179139177da4ca32e41b2b127f20117facdd8806a2`
- `b1b/article.md` sha256(raw bytes、`sha256sum`):
  `d60ec9241e9b83974e5bc9e9da5d5a341438abd7e85e25fccb0645bbd4a8f50a`
- 実行前後で再計算し、完全一致(不変)を確認済み。

### 3. 実行結果サマリ
- scaffold(Comment1-4+Preview+Key Phrase選定、A2/B1B): 完了。両levelとも
  Key Phrase `canonicalization status=CANONICALIZATION_PASS`。
- tts(全segment、A2/B1B): ほぼ全segment`status=OK`。**例外2件が
  既存Placeholder Notation Gate(`er003_v1_n3_01_tts_generate.py`、
  ER-006-KP5-CANONICAL-BUG-01由来、Key Phrase以外の日本語TTS経路にも
  適用済み)によりSTOPPED**:
  - A2 `japanese_title`: canonical text中の"…"(三点リーダー)を
    未発話placeholder記号と判定しTTS呼び出し自体を実行せずSTOP。
  - B1B `key_phrases`の`kp1`(rank1)日本語gloss: canonical text中の
    "〜"を同様に検出しSTOP。
- assemble(A2/B1B): **両levelとも既存Audio Validation Gate
  (`asm.verify_episode_audio_validation_gate`)が正しく発火し、
  `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`でepisode assemblyを中止**
  (A2: `japanese_title=STOPPED`起因、B1B: `kp1_japanese=STOPPED`起因)。
  Gateを回避・無効化する変更は一切行っていない。

### 4. STOP(回避せず報告)
上記2件は、いずれもcanonical text(A2日本語titleはja_writer正式path由来、
B1B KP1 glossはscaffold LLM生成物)に、既存Gateが「読み上げ不可な記法」と
判定する記号("…"/"〜")が含まれていたために生じた。本委任範囲では
Production module編集・記事本文/Key Phrase内容の書き換えは行っていない。
Fable/ユーザー判断が必要な選択肢(実装はしていない):
  (a) 該当箇所を含むgloss/titleをKey Phrase再選定・ja_writer再生成
      経路で作り直す(既存retry/regeneration機構の範囲内)。
  (b) "…"/"〜"を読み上げ可能な形へ機械的に正規化するルールをGate側へ
      追加する(既存Production module=`er003_v1_n3_01_tts_generate.py`/
      `er009_ja_foreign_token_gate_01.py`系の変更が必要、ユーザー承認要)。
  (c) 当該2箇所のみ人手でテキストを差し替える。
どちらも本Sonnet単独では選択・実装しない。

### 5. 詳細
runtime evidence全文・segment表・cost・regression結果は
`docs/pm/RESULT_PACKET_FXA2.md`参照。
