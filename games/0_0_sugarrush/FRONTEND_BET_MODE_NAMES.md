# Frontend Bet Mode Names - Sugar Rush

## Overview
The frontend only needs to send the **correct bet mode name** in API requests. The backend RGS handles all book mapping and configuration.

## Bet Mode Names (Use Exactly As Shown)

When making buy bonus or bet mode requests to the backend, use these exact names:

1. **`"base"`** - Base game (regular spins)
2. **`"bonus"`** - Regular Bonus Buy (100x bet)
3. **`"super_bonus"`** - Super Bonus Buy (500x bet)
4. **`"bonus_booster"`** - Bonus Booster (2x bet multiplier)

## Important Notes

- **Case-sensitive**: Use lowercase with underscores exactly as shown
- **Backend handles everything**: The backend RGS maps these names to the correct books (`books_base.jsonl.zst`, `books_super_bonus.jsonl.zst`, etc.)
- **No frontend config needed**: You don't need to configure book paths or file names - just send the mode name
- **If backend rejects**: The backend RGS doesn't have that mode configured yet (backend issue, not frontend)

## Example API Request

```json
{
  "betMode": "super_bonus",
  "costMultiplier": 500
}
```

The backend will:
- Look up `"super_bonus"` in its configuration
- Load the correct book file (`books_super_bonus.jsonl.zst`)
- Return the appropriate game outcome

## Summary

**Frontend responsibility**: Send the correct bet mode name string  
**Backend responsibility**: Map name → book file → game outcome

If you get a "bad request" error, it means the backend doesn't have that bet mode configured yet (backend team needs to add it).



