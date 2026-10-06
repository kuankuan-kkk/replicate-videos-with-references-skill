#!/usr/bin/env python3
"""Validate v3.1 structure, evidence and version-bound workflow gates."""
import argparse,pathlib,sys
from project_contract import load,validate
def main():
    p=argparse.ArgumentParser();p.add_argument('manifest',type=pathlib.Path);a=p.parse_args()
    try:errors=validate(load(a.manifest),a.manifest.resolve().parent)
    except (OSError,ValueError,TypeError,KeyError) as exc:errors=[str(exc)]
    for e in errors:print('ERROR: '+e)
    if not errors:print('manifest structure, evidence and workflow invariants: PASS')
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
