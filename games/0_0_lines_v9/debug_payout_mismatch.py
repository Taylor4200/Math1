"""Debug script to find which mode has payout mismatch"""

import json
import os
import pickle
import hashlib
import zstandard as zst
from io import TextIOWrapper
from game_config import GameConfig

def get_lut_payouts(lut_file):
    """Extract payouts from lookup table"""
    payouts = []
    with open(lut_file, 'r', encoding='UTF-8') as f:
        for line in f:
            _, weight, payout = line.strip().split(',')
            payouts.append(int(float(payout)))
    return payouts

def get_book_payouts(book_file):
    """Extract payouts from book file"""
    payouts = []
    with open(book_file, 'rb') as f:
        decompressor = zst.ZstdDecompressor()
        with decompressor.stream_reader(f) as reader:
            txt_stream = TextIOWrapper(reader, encoding='UTF-8')
            for line in txt_stream:
                line = line.strip()
                if not line:
                    continue
                blob = json.loads(line)
                payouts.append(blob['payoutMultiplier'])
    return payouts

def compare_mode(config, mode_name):
    """Compare payouts for a specific mode"""
    book_name = f"books_{mode_name}.jsonl.zst"
    lookup_name = f"lookUpTable_{mode_name}_0.csv"
    book_file = os.path.join(config.publish_path, book_name)
    lut_file = os.path.join(config.publish_path, lookup_name)
    
    if not os.path.exists(book_file) or not os.path.exists(lut_file):
        print(f"  [X] Files missing for {mode_name}")
        return False
    
    lut_payouts = get_lut_payouts(lut_file)
    book_payouts = get_book_payouts(book_file)
    
    lut_md5 = hashlib.md5(pickle.dumps(lut_payouts)).hexdigest()
    book_md5 = hashlib.md5(pickle.dumps(book_payouts)).hexdigest()
    
    print(f"\n{mode_name}:")
    print(f"  LUT count:  {len(lut_payouts)}")
    print(f"  Book count: {len(book_payouts)}")
    print(f"  LUT MD5:    {lut_md5}")
    print(f"  Book MD5:   {book_md5}")
    
    if lut_md5 == book_md5:
        print(f"  [OK] Match!")
        return True
    else:
        print(f"  [FAIL] MISMATCH!")
        
        # Find first difference
        for i, (lut_val, book_val) in enumerate(zip(lut_payouts, book_payouts)):
            if lut_val != book_val:
                print(f"  First difference at index {i}:")
                print(f"    LUT:  {lut_val}")
                print(f"    Book: {book_val}")
                # Show context
                start = max(0, i-2)
                end = min(len(lut_payouts), i+3)
                print(f"  Context (indices {start}-{end-1}):")
                print(f"    LUT:  {lut_payouts[start:end]}")
                print(f"    Book: {book_payouts[start:end]}")
                break
        
        return False

if __name__ == "__main__":
    config = GameConfig()
    
    print("Checking all modes for payout mismatches...")
    print("=" * 60)
    
    all_match = True
    for bet_mode in config.bet_modes:
        mode_name = bet_mode.get_name()
        matches = compare_mode(config, mode_name)
        if not matches:
            all_match = False
    
    print("\n" + "=" * 60)
    if all_match:
        print("[OK] All modes match!")
    else:
        print("[FAIL] Some modes have mismatches!")

