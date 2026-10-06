#!/usr/bin/env python3
"""Compare ORIGINAL baseline against immutable user-approved binary union mask."""
import argparse,json,pathlib,math
from project_contract import file_hash
def main():
    p=argparse.ArgumentParser()
    for key in ['before','after','mask']:p.add_argument(key,type=pathlib.Path)
    p.add_argument('--authorized-mask-sha256',required=True,help='Previously recorded approval hash; not an unreviewed replacement mask')
    p.add_argument('--channel-tolerance',type=int,default=2);p.add_argument('--max-changed-ratio',type=float,default=.001);a=p.parse_args()
    if not 0<=a.channel_tolerance<=255 or not math.isfinite(a.max_changed_ratio) or not 0<=a.max_changed_ratio<=1:p.error('tolerance 0..255; finite ratio 0..1')
    if file_hash(a.mask)!=a.authorized_mask_sha256:p.error('mask changed since authorization')
    from PIL import Image,ImageChops
    with Image.open(a.before) as x,Image.open(a.after) as y,Image.open(a.mask) as m:
        if x.size!=y.size or x.size!=m.size:p.error('before/after/mask sizes must match')
        before=x.convert('RGB');after=y.convert('RGB');mask=m.convert('L')
    pixels=mask.tobytes()
    if any(v not in (0,255) for v in pixels):p.error('mask must be approved binary union; feathering belongs INSIDE it')
    diff=ImageChops.difference(before,after).tobytes();locked=changed=0
    for i,v in enumerate(pixels):
        if v==0:locked+=1;changed+=max(diff[i*3:i*3+3])>a.channel_tolerance
    ratio=changed/locked if locked else None;passed=locked>0 and ratio<=a.max_changed_ratio
    result={'status':'verified' if locked else 'not-applicable','locked_pixels':locked,'changed_locked_pixels':changed,'changed_ratio':ratio,'pass':passed,
      'before_sha256':file_hash(a.before),'after_sha256':file_hash(a.after),'mask_sha256':file_hash(a.mask),'authorized_mask_sha256':a.authorized_mask_sha256,
      'channel_tolerance':a.channel_tolerance,'max_changed_ratio':a.max_changed_ratio}
    print(json.dumps(result,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
