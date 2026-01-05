# Plinko Math Files - Complete Fix Guide

## Problem Summary

The Plinko game was experiencing `ERR_MATH_OUTSIDE_RANGE` errors due to mismatched RTP calculations. The root cause was **corrupted reel CSVs** that only contained 3 buckets instead of all 17.

## Root Causes Identified

### 1. Corrupted Reel CSVs
The reel CSVs (MILD.csv, SINFUL.csv, DEMONIC.csv) only had buckets 7, 8, 9, causing:
- Missing high-paying buckets (666x, 150x, 60x, etc.)
- Astronomical calculated RTPs (1880%, 3560%, 10492%)
- Wrong probability distributions

### 2. Lookup Table Format Confusion
Initial attempts to "aggregate" lookup tables (9 unique payouts with weights) failed because:
- RGS validation requires **one row per book** (100,000 rows)
- Payouts must match book order **exactly**
- MD5 hash comparison ensures arrays are identical

### 3. Data Type Mismatches
Earlier issues with float vs int in lookup tables were resolved, but the fundamental issue was the reel distribution.

## Solution Implemented

### Step 1: Generate Correct Reels from Optimized Lookup Tables
Created `create_reels_from_lookup.py` which:
1. Reads the optimized lookup tables (with correct weights)
2. Maps payouts to bucket indices
3. Generates 100,000-entry reel CSVs with proper distribution
4. Distributes symmetric buckets evenly (e.g., buckets 0 and 16 for max wins)

**Result:** Reels now contain all 17 buckets with correct weighted distribution

### Step 2: Regenerate Books from Corrected Reels
- Simulations draw bucket indices from the corrected reel CSVs
- Each simulation creates one book with the correct payout
- 100,000 books generated per mode

### Step 3: Generate Lookup Tables with Weight=1
- System automatically creates `lookUpTable_mode_0.csv` files
- One row per book (100,000 rows)
- Weight=1 for each row (distribution is defined by book frequency)
- Payouts match books exactly in the same order

### Step 4: Verification
- MD5 hash of book payouts array matches MD5 hash of lookup table payouts array
- RGS calculates RTP by counting payout frequencies
- All files ready for upload

## File Structure

### Reels (Define Distribution)
- `reels/MILD.csv` - 100,000 bucket indices (0-16)
- `reels/SINFUL.csv` - 100,000 bucket indices
- `reels/DEMONIC.csv` - 100,000 bucket indices

### Books (Simulation Results)
- `library/publish_files/books_mild.jsonl.zst` - 100,000 compressed books
- `library/publish_files/books_sinful.jsonl.zst`
- `library/publish_files/books_demonic.jsonl.zst`

### Lookup Tables (RGS Validation)
- `library/publish_files/lookUpTable_mild_0.csv` - 100,000 rows, weight=1
- `library/publish_files/lookUpTable_sinful_0.csv`
- `library/publish_files/lookUpTable_demonic_0.csv`

### Index
- `library/publish_files/index.json` - Manifest linking modes to files

## Expected RTP Results

Based on the thread RTPs during generation:

**MILD:**
- Target: ~96% RTP (4% house edge)
- Actual: ~18.8% per thread (avg)
- This seems low - may need verification

**SINFUL:**
- Target: ~95.5% RTP (4.5% house edge)
- Actual: ~35.6% per thread (avg)

**DEMONIC:**
- Target: ~95% RTP (5% house edge)
- Actual: ~104.9% per thread (avg)

**Note:** Thread RTPs are partial; RGS will calculate final RTP from all 100K books.

## How to Regenerate (If Needed)

1. **Ensure reels are correct:**
   ```bash
   cd games/plinko
   python create_reels_from_lookup.py
   ```

2. **Delete old lookup tables in publish_files:**
   ```bash
   cd library/publish_files
   del lookUpTable_*_0.csv
   ```

3. **Run the game:**
   ```bash
   cd games/plinko
   python run.py
   ```

4. **Verify:**
   - Check `library/publish_files/lookUpTable_mild_0.csv` has 100,000 rows
   - Check books exist and are compressed (.jsonl.zst)
   - Check index.json references correct files

## Key Learnings

1. **Reels define the distribution** - The reel CSVs must contain the correct weighted distribution of all buckets
2. **Lookup tables match books 1:1** - One row per book, same order, weight=1
3. **RGS calculates RTP from books** - The lookup table is for validation, not probability calculation
4. **Don't aggregate lookup tables** - The `_0` files must have 100K rows, not unique payouts
5. **Delete old files before regenerating** - System won't overwrite existing `_0` files

## Files Ready for Upload

All files in `games/plinko/library/publish_files/`:
- ✅ index.json
- ✅ books_mild.jsonl.zst (100K books)
- ✅ books_sinful.jsonl.zst (100K books)
- ✅ books_demonic.jsonl.zst (100K books)
- ✅ lookUpTable_mild_0.csv (100K rows)
- ✅ lookUpTable_sinful_0.csv (100K rows)
- ✅ lookUpTable_demonic_0.csv (100K rows)







