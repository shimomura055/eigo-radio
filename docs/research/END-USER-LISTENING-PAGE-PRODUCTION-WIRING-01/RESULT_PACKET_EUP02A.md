# RESULT_PACKET_EUP02A(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02A: WP-C 音声同期、2026-10-29)

## 成果物(新規ファイルのみ、既存・runner・DEV・正式run未編集)
- `er135_enduser_sync_01.py`(`sync_level(level_dir, rows, *, cache_dir, model="medium", thresholds=None, align_mode="auto")`、`EnduserSyncError`(`ENDUSER_SYNC_*`)、CLI `--level-dir --rows-json --out --cache-dir --model`)
- `er135_enduser_sync_test_01.py`(32 test: 構造不変条件・短行閾値・二段/直接・キャッシュ(生出力のみ・整列再実行・変更segmentのみ再ASR)・失敗時例外とfallback不在(CLI失敗でoutput無し)・lock・KP(4/5/3ブロック・不一致・組立記録優先)・単調スナップ回帰・実音声1本)
- Phase-0: `docs/research/END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01/PHASE0_SYNC_01.md`+`phase0/`(生結果・summary・e2e)+`phase0_sync_01.py`/`phase0_report_01.py`(再現用)
- API費用 **0円**(faster-whisperローカルのみ、API呼出0、音声生成0)。stop_scope_check rc=0(非停止)。

## Phase-0結論
1. **主案**: 二段整列と**表示文直接整列は同等(X/Y/Z×Std/Adv 694境界で差 最大0.00s)**。DEV最終sync(月Adv 98境界)との差は中央値0/p95 0/最大1.133s(差>0.1sは2境界のみ=DEVの二段目`split`比例按分の境界で、本実装は実測無音に吸着=改善)。Fable条件(同等以上と実測)を満たすため**直接整列を推奨既定**(02Bは`tts_text`を渡さない)。二段整列もコード・test済みで`rows[*].tts_text`を渡すだけで有効(最終選択はFable)。
2. **閾値(確定案)**: 行=`一致率>=0.90`、または短行(en<=20/ja<=30トークン)で`不一致<=2(ja3)かつ>=0.75`。+全補間文(>=2トークンで一致0)は1件でもSTOP。KP=英語窓ASRで`max(トークン,連結文字被覆)>=0.80`、ブロック>=4。実測: 0.90未満はen 15/17と6/7の2行のみ(内容は正常)、全6 level×2方式=12実行PASS。
3. **所要時間**(他Worker並行負荷下): medium 約6.5分/セット(RTF0.66)、small 約2.5分/セット(RTF0.26)。境界差は最大0.04sだが、**smallはZ Adv KP2「Current」のKP照合に失敗**→品質優先でmedium維持。再実行はキャッシュで約1秒。

## Phase-0で見つけ修正した不具合(委任範囲内で修正・test済み)
- 境界スナップの逆転(Z Adv Part1「Go.」で`end<start`): 前境界の無音を再選択していた → 後続候補のみに制限(旧実装でtest FAIL・新実装でPASS確認)。
- KP英語区間のASR: 全体clip言語自動判定だと英語がカタカナ化(Z Std KP5)→ 英語窓のみ`language=en`でASR。
- Yのdevページはdivのscriptにclassなしinlineのspan(`&#9208;0.76s@0:04.6`)を含む → **02B/アダプタで除去必須**(WIRING_DESIGN §4の除去対象に追加提案)。

## 02B(Fable)への申し送り
- 出力`kp_en`は`{start,end,source,blocks,token_match}`(rowsスキーマへの追加キー。KP行のみ。02Bの`er135_enduser_page_01.py`は既にこの形を想定)。`source=assembly_record`のときblocksは実測ブロック数(3以下の場合02B側の`blocks>=4`検査と衝突しうる)。
- 時刻は行のsegment mp3先頭からの秒。ゲート(4)episode_offset_check・(5)全編音声長差は本moduleに含めていない(02B/次委任)。
- 判断候補: なし(閾値・主案は工学基準で既存設計内。緩和・fallback追加はしていない)。

## RESULT_PACKET 4行
1. 既存仕様整合: WIRING_DESIGN_01.md:52-62(§6-1方式・キャッシュ)・:63-73(§6-2失敗時=例外のみ、縮退実装なし)、T/sync_build_01.py:60-196(align/fill_gaps/snap移植)、T/tools/build_sync_index_02.py:19-83(二段目移植)、T/asr_raw_01.py:22-25(ASR設定同一)、decision: Fable M2/M3/M8。差異=単調スナップ制約追加・KP英語窓ASR(上記)。
2. 未承認機能の既定値: 本moduleは新規file・単独呼出でProduction経路に未接続(runner hookは02B/次委任)。flagなし。既存runner(er019/er121/er026)からの参照0(02Bのer135_enduser_page_01.pyは本moduleをコメントで参照のみ、importなし)\|sync_level` で既存runner/Production fileからの参照0。
3. 失敗終了時の最終成果物: 失敗は`EnduserSyncError`のみ(CLIはrc=3でoutput file未生成=testで確認)。部分JSON・縮退(ハイライトなし/比例按分)は生成しない。目的適合(ユーザー原文「エンドユーザーページ1文単位ハイライト」)=同期不能なら公開しない(WIRING_DESIGN 判断候補1 B案)。聴感は未確認。
4. 撤去・残置: 旧規則の撤去なし(新規)。DEVの`==4`ブロック規則は不採用(`kp_min_blocks`以上)。残存Grep: `proportional|dummy|equal_split|highlight_off`=er135_enduser_sync_01.pyで0件(testで検査)。
判定整合: 重大NG=なし
