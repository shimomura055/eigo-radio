# BUDGET_LOG_01
- 呼出: gpt-6-luna(Production A2_SUPPORT設定。routing=`er006_model_routing_contract_01.SUPPORT_MODEL`)x 4回(Comment1〜4各1回、再生成なし、attempt全て1回目OK)
- tokens: after_generation_log_01.json参照(in/out合計はログの`in_tokens`/`out_tokens`)。実費(概算) = 0.1724円(pricing_snapshot gpt-6-luna in0.10/out0.50 USD/M x160円)。上限100円に対し0.17%。TTS/ASR/他API 0円。
- モデル: Production現行設定を使用(追加モデル比較なし)。最新世代系として設定済みのProductionモデルで、旧/下位モデル利用なし。
- 量産単価影響: 方式をProduction採用した場合の追加呼出は、Z方式でComment3のcontext(Part3先頭1段落)が増える程度。Comment数・呼出回数は不変(X: 5呼出[C1-4+Preview]→同数)。1記事あたり増分は入力数十〜百数十token程度=0.01円未満/記事セットで、70円/記事セット目標への影響は無視可能。lint+retry(D4)を採用した場合のみ最大+1呼出/Commentの上振れ余地あり(それでも1円未満)。
