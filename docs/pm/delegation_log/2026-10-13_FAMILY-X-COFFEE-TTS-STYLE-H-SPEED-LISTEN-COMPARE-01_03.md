# FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_03 (2026-10-13)
- 依頼: N01 Std Take3破綻の原因(Prompt仕様か確率的TTS失敗か)判断のための既存ログ事実集計(JPY0、API呼出なし、生成なし、SSOT編集なし)。
- 結果: 全128 call(主集計TRIAL-03/04/05=92、TRIAL-02参考=36)中、生成破綻2件(J11 Adv Take1=原稿外文挿入、N01 Std Take3=原稿全文の2周読み上げ)。主集計の発生率2.2%(2/92)。N01 Std Take3は他take比音声長1.92倍、tokenは線形で費用は音声長に比例(約25 token/s)。
- 詳細: er057_output/coffee_tts_style_h_speed_05_listen/collapse_rate_03.md / collapse_rate_03.json
- 追加確認案(未実行): N01 Std Take4〜6(3call、約JPY3.9)ほか。結論・採用判断はFable/ユーザー。
- STOP確認: Coffee用STOP/STOP_ALL不在(Melos用STOP_NOTICEは対象外)。
