import json

with open('vector_db_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("VECTOR DATABASE ANALYSIS")
print("=" * 60)

# 1. METADATA ANALYSIS
print("\n📋 METADATA ANALYSIS")
print("-" * 40)
sources = {}
pages_count = {'with_page': 0, 'without_page': 0}
has_start_index = 0

for item in data:
    source = item['metadata'].get('source', 'Unknown')
    sources[source] = sources.get(source, 0) + 1
    if item['metadata'].get('page'):
        pages_count['with_page'] += 1
    else:
        pages_count['without_page'] += 1
    if 'start_index' in item['metadata']:
        has_start_index += 1

print(f"Total chunks: {len(data)}")
print(f"\nChunks per source:")
for s, c in sorted(sources.items()):
    print(f"  - {s}: {c} chunks")
    
print(f"\nPage metadata coverage: {pages_count['with_page']}/{len(data)} ({100*pages_count['with_page']/len(data):.1f}%)")
print(f"Start index coverage: {has_start_index}/{len(data)} ({100*has_start_index/len(data):.1f}%)")

# 2. CHUNK LENGTH ANALYSIS
print("\n📏 CHUNK LENGTH ANALYSIS")
print("-" * 40)
lengths = [len(item['content']) for item in data]
print(f"Average: {sum(lengths)/len(lengths):.1f} chars")
print(f"Min: {min(lengths)} chars")
print(f"Max: {max(lengths)} chars")
print(f"Median: {sorted(lengths)[len(lengths)//2]} chars")

very_short = len([l for l in lengths if l < 100])
short = len([l for l in lengths if 100 <= l < 500])
medium = len([l for l in lengths if 500 <= l < 800])
long_ = len([l for l in lengths if l >= 800])
print(f"\nLength distribution:")
print(f"  Very short (<100):  {very_short} ({100*very_short/len(data):.1f}%)")
print(f"  Short (100-500):    {short} ({100*short/len(data):.1f}%)")
print(f"  Medium (500-800):   {medium} ({100*medium/len(data):.1f}%)")
print(f"  Long (>=800):       {long_} ({100*long_/len(data):.1f}%)")

# 3. QUALITY ISSUES
print("\n⚠️ POTENTIAL QUALITY ISSUES")
print("-" * 40)

# Find very short chunks
very_short_chunks = [item for item in data if len(item['content']) < 50]
print(f"Very short chunks (<50 chars): {len(very_short_chunks)}")
if very_short_chunks:
    print("  Examples:")
    for item in very_short_chunks[:3]:
        print(f"    - [{item['metadata']['source']}] \"{item['content'][:50]}...\"")

# Find chunks with garbled text (control chars)
garbled = []
for item in data:
    control_chars = sum(1 for c in item['content'] if ord(c) < 32 and c not in '\n\r\t')
    if control_chars > 5:
        garbled.append(item)
print(f"\nChunks with many control chars: {len(garbled)}")

# 4. SAMPLE THAI CONTENT
print("\n🇹🇭 SAMPLE THAI CONTENT")
print("-" * 40)
for item in data:
    if 'thailand' in item['metadata'].get('source', '').lower():
        thai_chars = sum(1 for c in item['content'] if '\u0e00' <= c <= '\u0e7f')
        if thai_chars > 20:
            print(f"Source: {item['metadata']['source']} (Page {item['metadata'].get('page', 'N/A')})")
            print(f"Thai chars: {thai_chars}")
            print(f"Content (first 300 chars):")
            print(f"  {item['content'][:300]}...")
            print()
            break

# 5. RECOMMENDATIONS
print("\n💡 RECOMMENDATIONS")
print("-" * 40)

if very_short > len(data) * 0.1:
    print("❌ Too many short chunks - consider increasing minimum chunk size")
else:
    print("✅ Chunk size distribution looks reasonable")

if pages_count['with_page'] == len(data):
    print("✅ All chunks have page metadata")
else:
    print(f"⚠️  {pages_count['without_page']} chunks missing page metadata")

if has_start_index == len(data):
    print("✅ All chunks have start_index for overlap tracking")
else:
    print(f"⚠️  {len(data) - has_start_index} chunks missing start_index")
