import collections

buckets = [int(line.strip()) for line in open('reels/MILD.csv')]
counts = collections.Counter(buckets)
total = len(buckets)

print(f'Total entries: {total}')
print()
print('Bucket  Count    Percentage')
print('------  ------  -----------')
for i in range(17):
    count = counts[i]
    pct = count/total*100
    bar = '#' * int(pct)
    print(f'{i:6d}  {count:6d}  {pct:5.2f}%  {bar}')

# Check if it's natural (center buckets should be most common)
center_pct = (counts[7] + counts[8] + counts[9]) / total * 100
print()
print(f'Center buckets (7,8,9): {center_pct:.2f}%')
if center_pct > 60:
    print('This looks like a NATURAL bell curve!')
else:
    print('This looks like OLD scripted distribution')











