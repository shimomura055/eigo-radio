import json,sys
sys.path.insert(0,'.')
import er007_ja_asr_validator_01 as v
canon="長い間、あの夜のことを誰にも話さなかったミノキチが、今、妻にある女性のことを話します。妻はまず、何を尋ねるのでしょうか。"
for asr in ["長い間、あの夜のことを誰にも話さなかった実基が、今、妻にある女性のことを話します。妻はまず、何を尋ねるのでしょうか。","長い間、あの夜のことを誰にも話さなかった美濃吉が、今、妻にある女性のことを話します。妻はまず、何を尋ねるのでしょうか。"]:
  for er in (None,{"ミノキチ":"ミノキチ"}):
    r=v.classify_ja_asr_match(canon,asr,expected_readings=er)
    print(er,r.classification,r.protected.content_diffs if r.protected else None)
