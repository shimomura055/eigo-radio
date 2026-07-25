# ER-003-B1-P3W Step 1/2: MFA環境構築・スモークテストレポート

## Step 1: MFA環境確認・構築

事前確認の結果、`mfa`コマンド・conda・micromamba のいずれもこの環境には存在しなかったため、
アプリ本体(`.venv/`、production依存関係)とは完全に分離した専用環境を新規構築した。

| 項目 | 値 |
|---|---|
| 構築方法 | micromamba(公式バイナリ、win-64、直接ダウンロード) |
| micromamba version | 2.8.1 |
| micromamba配置先 | `mfa_tool/Library/bin/micromamba.exe` |
| 隔離env配置先(root prefix) | `mfa_tool/root`(micromamba用)/ `mfa_tool/envs/mfa`(実際のMFA環境) |
| MFAモデル配置先(MFA_ROOT_DIR) | `mfa_tool/mfa_root`(デフォルトの`~/Documents/MFA`から分離) |
| インストール元channel | conda-forge |
| montreal-forced-aligner version | 3.4.1(`pyhd8ed1ab_0`) |
| MFA依存の主要ネイティブパッケージ | kaldi 5.5.1172(win-64ビルド)、kalpy 0.10.4、pynini 2.1.7 |
| 追加インストール | spacy・sudachipy・sudachidict-core(日本語tokenizerに必須。`montreal-forced-aligner`本体のconda-forgeパッケージには含まれておらず、初回`mfa align`実行時に`ImportError`で判明したため追加) |

### 日本語モデル

| 種別 | モデル名 | version |
|---|---|---|
| acoustic model | japanese_mfa | 3.0(train date 2024-02-08) |
| dictionary | japanese_mfa | 3.0.0 |
| tokenizer | japanese_mfa | 2.2.1 |

いずれも`mfa model download <type> japanese_mfa`で取得(取得元: MFA公式モデルリポジトリ)。
モデル本体は`mfa_tool/mfa_root/pretrained_models/`配下に配置され、`.gitignore`により
Git管理対象外(`mfa_tool/`を一括除外)。名称・versionは本ファイルおよび
`audio_metadata.json`の`env_check`へ記録済み。

ネットワーク・権限・容量の問題はなく、構築は正常に完了した。Whisper等の他alignerへの
切り替えは行っていない。

## Step 2: MFAスモークテスト

新規TTS生成前に、既存の日本語音声(ER-003-B1-P3Tの成果物)でalignmentが正常に機能するかを確認した。

| 項目 | 値 |
|---|---|
| 対象音声 | `er003_output/b1_p3t/A01/raw/ja_full_sentence.wav`(既存、新規生成なし) |
| sha256 | `a239ef34a7623be6c82d9d7994647f18df0423d684e13c3e990ebe8d559b19bd` |
| 対応原稿 | 「前半は激しい接触と緊張が続き、両チームとも枠内シュートを記録できないまま、静かな均衡が保たれます。」 |
| ビーム幅 | デフォルト(beam=10, retry_beam=40) |
| 結果 | 成功。TextGrid正常生成 |
| 語順一致 | 一致(22語、原稿の語順と完全に一致することを機械的に確認) |
| 出力TextGrid | `mfa_tool/smoke_test_output/ja_full_sentence.TextGrid`(参考コピー: `environment/smoke_test_ja_full_sentence.TextGrid`) |

スモークテストは正常に成功したため、Step 3(マーカー入り音声のTTS生成)へ進んだ。

## 補足: Step 4で判明したビーム幅の問題

Step 4(マーカー入り音声のalignment)では、デフォルトビーム幅で`NoAlignmentsError`
(1発話全体で整列パスが1つも見つからない)が発生した。診断の結果、これは日本語tokenizer
自体の不具合ではなく(トークン化・OOV検出は正常に機能しており、辞書内に存在しない語は
「保たれます」1語のみで、スモークテストの音声でも同じ語が同様にOOV扱いされていたにも
関わらずスモークテストは成功していた)、Kaldiデコーダの探索幅(ビーム幅)がこの発話(24語、
マーカー語を含む)に対して不足していたことが原因と特定した。MFA公式のエラーメッセージが
提示する標準的な対処(`--beam 100 --retry_beam 400`)を適用したところ、alignmentは成功した。
これはMFA自体が提供する標準的なチューニングパラメータであり、無音長・ASR・GPT推測等の
代替手段への切り替えではない。
