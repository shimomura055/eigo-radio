# TRIAL_RESULT_02 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_03、Family X 0.2秒版 B0.2。TTS 0・API 0・Production変更0)

原文: `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md` §2。状態: Trial継続(APPROVED_FOR_PRODUCTIONではない)。

## 1. 作成方法(再組立のみ)
- 既存のB_r1/B_r2 chunk wav(`er113_output/fx_paragraph_chunk_trial_01/gen/B_r{1,2}_p*/…`、委任_02で生成済み)を再利用。**TTS呼出0・ASR API呼出0**(ASRはローカルfaster-whisper `small`のみ)。
- 組立は委任_02と同一関数 `compute_b_artifacts(pause_seconds=0.2)`(chunkごと同target_rms[0.09149]のRMS gain + np.concatenate + 段落間追加無音 0.2秒 + 既存ヘッドルーム弁)。新しい音声加工なし。
- 実行: `er113_fx_paragraph_chunk_trial_02.py`(新規、`.venv/Scripts/python.exe`)。出力 `measure_02.json`。再組立の健全性: pause=0.5で再組立した本文長がmeasure_01と完全一致(part1 57.29 / part2 49.79 / part3 42.90秒)。
- 追加無音は10 chunk間のうち同一part内の7境界に各0.2秒(計1.4秒)。B0(追加なし)→B0.2の全長差=+1.40秒(実測 146.48→147.88)=指定どおり。段落構造(10 chunk)維持。

## 2. 速度(本文3パート合計、428語、同一計測法)
| 方式 | 全長s | 全体WPM | 実発話WPM(art300) | art500 |
|---|---|---|---|---|
| A 現行(承認済みtake) | 139.92 | 183.53 | 211.48 | 197.72 |
| A_r2(現行方式の別take) | 135.76 | 189.16 | 215.29 | 202.81 |
| B0(追加なし) | 146.48 | 175.31 | 201.68 | 190.19 |
| **B0.2(新、+0.2秒)** | **147.88** | **173.65** | **201.68** | 190.89 |
| 旧B(0.5秒) | 149.98 | 171.22 | 201.68 | 190.89 |
| B0.2_r2(別take) | 149.62 | 171.63 | 197.44 | 187.73 |

- B0/B0.2/旧Bは**同一の音声**(同じchunk wav)で、差は追加無音だけ。よって実発話WPM(art300)は同一(201.68)、全体WPMのみが追加無音の分だけ変わる。
- A→B0.2: 全長+7.96秒(+5.7%)。M4分解(`measure_02.json` decomposition `A->B02_r1`): Δ発話区間+7.90秒、Δ段落境界gap+0.04秒、Δ両端+0.02秒。**増加の大半は発話そのものの遅さで、追加無音ではない**(委任_02の結論と同じ)。10段落中10段落でB側の発話区間が長い(段落span比 平均1.084)。
- 実発話WPM差(art300): B0.2 − A = −9.8 WPM(−4.6%)、−A_r2 = −13.6(−6.3%)、B0.2_r2 − A = −14.0 / − A_r2 = −17.9。take間ばらつき(A vs A_r2=+3.8 WPM、B_r1 vs B_r2=−4.7 WPM)より、A→Bの差(−10〜−18)の方が大きく、**Bは実発話が約5〜7%遅い**(委任_02の結論を再確認)。
- 注意: ASRタイムスタンプの揺らぎにより、同一音声のB0とB0.2でも段落span差が最大約1.2秒出る(`B0_r1->B02_r1` Δ発話+1.16秒)。実際の音声の発話区間は同一であり、断定には`art300`と全長(決定的)を使う。

## 3. ポーズ・接続品質
- 段落境界gap(ASR実測、7境界平均): A 0.53 / A_r2 0.45 / **B0.2 0.54(r2 0.57)** / B0 0.50 / 旧B 0.90。B0.2の段落間の間はAの自然な間とほぼ同じ(旧B 0.5秒は約0.35〜0.4秒長かった)。個別値には0.00(ASR時刻の接触)が含まれるため参考値(平均で見る)。
- 500ms以上の中間ポーズ: B0.2 20個/13.35秒(A 17個/10.04秒、旧B 20個/15.45秒)。
- 境界音量差(前chunk末尾1秒RMS vs 次chunk先頭1秒RMS、gain適用後): 9境界 [2.2, −0.89, 3.26, 3.64, 5.81, 3.3, 3.04, 3.77, 1.83] dB(最大5.81)。Aの既存part境界は2.83 / 7.8 dB(A_r2 8.28 / 6.45)。追加無音の長さは境界音量差に影響しない(0.5秒版と同値)。
- 欠落・二重: 整列(ローカルASR)で全パート全段落整列True、ASR語数/台本語数 = part1 1.007 / part2 1.020 / part3 1.000(旧Bのpart1/2は1.06=ASR側の余分語認識があったが、B0.2は1.00〜1.02でAと同水準)。**欠落・二重再生なし**。
- ヘッドルーム: 通し(Advanced通し)の peak 0.925、ヘッドルーム弁 applied=False(`full_episode_b02_r1`)。通しの長さ B0.2 288.80秒 / B0 287.40秒。
- 声質・抑揚の一貫性、段落間の自然さ、速さの体感は**機械指標で代替せず、ユーザー試聴で判断**(過去P6B不合格の論点)。

## 4. 保護対象・Production
- PROTECTED_STORES(10 store)・PROTECTED_TREES(承認済みrun dir、公開版`user_test/uk_train_speaker_playback_e2e_02`、local_rewrite_recovery)のbefore/after sha: **変化0**(`measure_02.json` `protected_changed=[]`)。
- Production code/Prompt/flag変更0、TTS呼出0、費用0円(追加なし)。

## 5. 試聴ページ
- `user_test/fx_paragraph_chunk_trial_01/index.html`(主表示=A現行/B0(追加なし)/**B0.2(新)**、本文1〜3・本文全体・Advanced通し。旧B(0.5秒)・A_r2・旧B_r2・B0.2_r2は折りたたみ参考)。追加mp3=`audio/B02_*.mp3`、`B0_full.mp3`、`B02r2_part*.mp3`。
- URL: https://shimomura055.github.io/eigo-radio/user_test/fx_paragraph_chunk_trial_01/index.html
