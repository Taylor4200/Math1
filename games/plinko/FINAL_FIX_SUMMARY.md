# Plinko Math Files - Final Fix Summary

## Issue Identified

The `ERR_MATH_OUTSIDE_RANGE` error was caused by a mismatch in how the RGS validates lookup tables against book files.

### Root Cause

The RGS validation (`utils/rgs_verification.py`) compares the **MD5 hash** of the payout arrays from:
1. **Lookup table CSV** - all payout values from the third column
2. **Books file** - all `payoutMultiplier` values from every book

For the hashes to match, the arrays must be:
- **Same length** (number of rows in CSV = number of books in .jsonl.zst)
- **Same order** (payout values must appear in identical sequence)
- **Same values** (exact integer matches)

### Previous State (BROKEN)

- **Lookup tables:** 17 rows (one per unique bucket payout)
- **Books:** 100,000 books (one per simulation)
- **Result:** Arrays had different lengths → MD5 hashes didn't match → validation failed

### Fixed State (WORKING)

- **Lookup tables:** 100,000 rows (one per book)
- **Books:** 100,000 books
- **Result:** Arrays are identical → MD5 hashes match → validation passes

## Files Fixed

All three lookup tables have been expanded:

1. `library/publish_files/lookUpTable_mild_0.csv` - 100,000 rows
2. `library/publish_files/lookUpTable_sinful_0.csv` - 100,000 rows
3. `library/publish_files/lookUpTable_demonic_0.csv` - 100,000 rows

## Validation Results

All modes now pass RGS validation:

### MILD
- ✅ Array lengths match: True
- ✅ MD5 hashes match: `5b2737233c5e6afd862ef2f94133698a`
- ✅ VALIDATION PASSED

### SINFUL
- ✅ Array lengths match: True
- ✅ MD5 hashes match: `27ad5ca50235d147bafea48d883a9371`
- ✅ VALIDATION PASSED

### DEMONIC
- ✅ Array lengths match: True
- ✅ MD5 hashes match: `deabce7c9e623a07504f076a6342ef53`
- ✅ VALIDATION PASSED

## Ready for Upload

All files in `library/publish_files/` are now production-ready:
- ✅ `index.json` - Correctly references all modes
- ✅ `lookUpTable_mild_0.csv` - 100,000 rows, matches books exactly
- ✅ `lookUpTable_sinful_0.csv` - 100,000 rows, matches books exactly
- ✅ `lookUpTable_demonic_0.csv` - 100,000 rows, matches books exactly
- ✅ `books_mild.jsonl.zst` - 100,000 books, compressed
- ✅ `books_sinful.jsonl.zst` - 100,000 books, compressed
- ✅ `books_demonic.jsonl.zst` - 100,000 books, compressed

## Math Specifications

### MILD Mode
- RTP: ~95.93% (House Edge: ~4.07%)
- Prob Less Bet: ~0.789 (78.9%)
- Max Win: 666x (66,600 cents)

### SINFUL Mode
- RTP: ~95.42% (House Edge: ~4.58%)
- Prob Less Bet: ~0.789 (78.9%)
- Max Win: 1,666x (166,600 cents)

### DEMONIC Mode
- RTP: ~94.87% (House Edge: ~5.13%)
- Prob Less Bet: ~0.809 (80.9%)
- Max Win: 16,666x (1,666,600 cents)

### House Edge Margins
- MILD → SINFUL: +0.51% ✅
- SINFUL → DEMONIC: +0.55% ✅
- All within acceptable range

## Upload Command

The files are ready to be uploaded to the RGS. The `ERR_MATH_OUTSIDE_RANGE` error should now be resolved.







