# Phase B 予算逸脱記録(NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01)

作成: fix01（2026-09-25）。事実記録のみ。Production仕様変更なし。

## 1. 実行コマンド

Phase B本体（別worker実行）は以下の形の呼び出し（`entry_point.json`の
`ja_article_path`/`slug`/`out_dir`から復元。`--stage tts`部分の完全な
生コマンド文字列自体はACTIVE_TASK.mdの要約以上には別途保存されていない）:

```
.venv/Scripts/python.exe er012_e_family_entertainment_two_level_runner_01.py \
  --ja-article docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md \
  --slug meta \
  --out-dir er012_output/e_family_two_level_wiring_01/meta \
  --stage tts
```

## 2. 期待していたこと vs 実際に起きたこと

- **期待**（Phase A reconの推測、未実行の見込みに基づく）: B1は
  `full_story_part2`のみ、A2は`full_story_part2` + `comment_1`/`comment_2`/
  `comment_3`のみが再生成される（text未変更のsegmentはスキップされる）。
- **実際**: `--stage tts`は`run_tts_stage()` → `tts_gen.run_theme(theme)`
  → `generate_b1_segments(theme)` / `generate_a2_segments(theme)`
  （`er003_v1_n3_01_tts_generate.py` L923-926）を呼び、これらは
  b1b・a2それぞれの**全segment**（本記事構成で13segment×2level）を
  無条件でループ処理する。加えてKey Phrase側（英語5件＋日本語5件、
  `sc.run_key_phrases`/関連経路）も同一run内で再生成された。

## 3. 原因（コード引用）

### 3-1. Human Review Lockの`check_before_generation()`はRESOLVEDを
ブロックしない

`er011_human_review_lock_01.py` L226-253:

```python
    if entry is None:
        return {"proceed": True, "theme_id": theme_id, "level": level, "segment_id": segment_id}

    text_matches = entry.get("canonical_text_sha256") == _text_hash(text)
    if not text_matches:
        # 台本が変わった -> 新しいsegmentのバージョンとして扱う(過去のlockは無効)。
        return {"proceed": True, "note": "canonical_text changed since last lock; treated as new version",
                "theme_id": theme_id, "level": level, "segment_id": segment_id}

    state = entry.get("state")
    if state == "REGENERATE_APPROVED":
        return {"proceed": True, "consuming_regenerate_approval": True,
                "theme_id": theme_id, "level": level, "segment_id": segment_id}
    if state == "HUMAN_REVIEW_REQUIRED":
        return {"proceed": False, "status": state, "reason": entry.get("reason"),
                "locked_entry": entry, "theme_id": theme_id, "level": level, "segment_id": segment_id}
    # RESOLVED(status=OKで確定済み)は監査用の記録に留め、ブロックはしない。
    # 理由: A2 6% slowdown retry(...)は、内側のgenerate_english_
    # segment_with_fallback()がstatus=OKを返した直後に、post-process後の
    # ASR再検証が別途不一致となり、同じ内側関数を最大3回まで正当に取り
    # 直す既存の設計を持つ。ここでRESOLVEDをブロック対象にすると、この
    # 既存の正当なretryまで機械的に止めてしまう(実害のある誤検知)。
    # 本Guardが実際に防ぐべきなのは「Human Review/繰り返し失敗への機械的
    # 再挑戦」であり、「一度成功したsegmentへの正当な再挑戦」ではない。
    # AUTO_PROCESSING等、その他の状態も安全側でproceedを許可する。
    return {"proceed": True, "theme_id": theme_id, "level": level, "segment_id": segment_id}
```

つまり、text hashが一致していてもstate=`RESOLVED`（既にstatus=OKで
確定済み）の場合は`proceed=True`を返す設計であり、「既存音声をそのまま
再利用してAPI呼び出し自体をスキップする」経路はそもそも存在しない。
これは意図的な設計（コメントにある通り、A2 slowdown retryの正当な
再試行を機械的に止めないための判断）であり、バグではない。ただし
「text未変更ならAPI呼び出し自体を省略する」というPhase Aの期待とは
別物である。

### 3-2. `run_tts_stage()`/`tts_gen.run_theme()`は全segment無条件ループ

`er012_e_family_entertainment_two_level_runner_01.py` L373-380:

```python
def run_tts_stage(theme: dict, japanese_title: str) -> dict:
    tts_gen.JAPANESE_TITLES[theme["theme_id"]] = japanese_title
    return tts_gen.run_theme(theme)
```

`er003_v1_n3_01_tts_generate.py` L923-926:

```python
def run_theme(theme: dict) -> dict:
    b1_result = generate_b1_segments(theme)
    a2_result = generate_a2_segments(theme)
    return {"b1b": b1_result, "a2": a2_result}
```

`generate_b1_segments`/`generate_a2_segments`は、変更されたsegmentを
選別する引数を持たず、テーマ内の全segmentを毎回ループする実装。
「差分segmentのみ指定して再生成する」ための`--only-segments`等の
CLI引数は現状存在しない。

### 3-3. 既存の「audio再利用キャッシュ」機構は存在しない

3-1で示した通り、Human Review Lockは「呼び出し前にblockするかどうか」の
Gateであり、「テキストhash一致時に既存wavファイルをそのまま再利用して
TTS API呼び出し自体を省略する」キャッシュ層ではない。そのようなキャッシュ
機構はコード内に見当たらなかった（`er011_human_review_lock_01.py`
全体・`er003_v1_n3_01_tts_generate.py`のsegment生成経路を確認した範囲）。

## 4. 実測費用: ¥54.66（このrun分、実行前累計¥17.96 → 実行後累計¥72.62の差分）

`raw_usage_log.jsonl`の`compute_cost_jpy_so_far()`（本コード、
`er012_e_family_entertainment_two_level_runner_01.py` L114-140）で
プロバイダ別に算出した累計費用（このタスクで再計算し確認、本fix01時点
=実行後と同値、TTS再実行以降このrunでは追加費用なし):

```
累計(実行後) jpy= 72.62  by_provider={'openai': 13.92, 'gemini_batch': 0.0,
  'openai_asr': 7.38, 'gemini': 51.31, 'azure': 0.0}
```

ACTIVE_TASK.mdの記録による実行前累計は¥17.96のため、`--stage tts`実行
1回分の差分は¥54.66（内訳の大半はTTS本体`gemini`プロバイダの¥51.31、
ASR確認`openai_asr`の一部を含む。b1b・a2両level・13segment×2 +
Key Phrase英語5件・日本語5件の再生成に相当）。

## 5. runner内部guard（既定¥300）が効かなかった理由

`assert_budget_ok()`（`er012_e_family_entertainment_two_level_runner_01.py`
L143-149）:

```python
def assert_budget_ok(out_dir: str, budget_jpy: float, note: str = "") -> float:
    cost_log_path = f"{out_dir}/raw_usage_log.jsonl"
    jpy, by_provider = compute_cost_jpy_so_far(cost_log_path)
    print(f"[E-FAMILY-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > budget_jpy:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {budget_jpy} JPY. Stopping ({note}).")
    return jpy
```

`main()`側の呼び出し（L697-699）:

```python
    if args.stage in ("tts", "all"):
        run_tts_stage(theme, japanese_title)
        assert_budget_ok(args.out_dir, args.budget_jpy, "after tts")
```

このguardは(a)**stage全体が完了した後にのみ**評価される事後チェックで
あり、segment単位で費用を積算しながら上限到達時点で処理を中断する
仕組みではない。(b)`--budget-jpy`はCLI引数で既定値¥300
（`build_arg_parser()` L628 `default=300.0`）であり、今回のrun後累計
¥72.62は既定¥300を明確に下回るため、`assert_budget_ok`は正常終了と
判定した。今回のPhase B委任時の個別予算上限¥10は、Fable/PM運用層が
このタスクに対して設定した外部的な承認上限であり、`--budget-jpy`引数
（コード側の一般的な安全装置）とは別物で、コードには一切伝わっていない。
つまり「コード側guardが機能しなかった」のではなく、「コード側guardは
既定¥300しか知らず、今回のタスク固有の¥10という上限はコードへ渡されて
いなかった」ことが実態である。

## 6. Phase A reconの推測が誤っていた旨

`docs/pm/recon_news_e2e_pre_keyphrase_closeout_01.md`（Phase A、未実行の
コードreadingに基づく推測）のA-2節が述べていた「text変更時のみ
再生成される見込み」は、本fix01で確認した`check_before_generation()`
のRESOLVED分岐（3-1参照）とは整合しない誤った推測だった。RESOLVED状態
はtext hashが一致していてもblockされず、`generate_b1_segments`/
`generate_a2_segments`自体もtext差分に基づくフィルタリング機構を
持たないため、「一部segmentのみ再生成される」という前提は成立しない。

## 7. 再発防止策（提案のみ、本タスクでは未実装）

- `run_tts_stage()`に`--only-segments`のようなCLI引数を追加し、
  再生成対象segment IDを明示的に絞り込めるようにする。
- `--budget-jpy`とは別に、stage開始前に想定コストを見積もり、
  Fable/PM運用層が設定したタスク固有の上限（今回の¥10等）とCLI引数を
  一致させる運用ルール（コード変更ではなく運用手順の徹底）を検討する。
