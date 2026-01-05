import zstandard as zstd
import json

f = open('library/publish_files/books_mild.jsonl.zst', 'rb')
data = zstd.ZstdDecompressor().decompress(f.read()).decode()
f.close()

book = json.loads(data.split('\n')[0])
print('First book:')
print(f'  payoutMultiplier: {book["payoutMultiplier"]}')
print(f'  events: {book["events"]}')







