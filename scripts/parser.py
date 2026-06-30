import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
import re


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEBATES_DIR = REPO_ROOT / "data" / "debates"
OUTPUT_PATH = REPO_ROOT / "data" / "debates.parquet"


files = sorted(DEBATES_DIR.glob("*.xml"))
print(f"Number of files: {len(files)}")


STRIP_TAGS = {'div', 'table', 'tr', 'td', 'th', 'tbody', 'caption', 'a', 'img', 'col'}

def extract_text(elem):
    parts = []
    if elem.tag in STRIP_TAGS:
        return parts
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.extend(extract_text(child))
        if child.tail:
            parts.append(child.tail)
    return parts

def get_speech_text(speech_elem):
    parts = extract_text(speech_elem)
    return ' '.join(p.strip() for p in parts if p.strip())

def clean_time(val):
    if not val:
        return None
    match = re.match(r'^0*(\d+):(\d{2}):(\d{2})$', val.strip())
    if match:
        h, m, s = match.groups()
        return f"{int(h):02d}:{m}:{s}"
    return None

def clean_oral_qnum(val):
    if not val:
        return None
    return val.strip().rstrip('.')

rows = []
chunk_size = 2000
chunk_num = 0

for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f"{i}/{len(files)} — {len(rows)} rows so far")

    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
    if not date_match:
        continue
    date = date_match.group(1)

    try:
        root = ET.parse(f).getroot()
    except ET.ParseError as e:
        print(f"skip {f.name}: {e}")
        continue

    for speech in root.findall('speech'):
        a = speech.attrib
        rows.append({
            'source_id':          a.get('id'),
            'date':        date,
            'url':         a.get('url'),
            'time':        clean_time(a.get('time')),
            'person_id':   a.get('person_id'),
            'speakerid':   a.get('speakerid'),
            'speakername': a.get('speakername'),
            'nospeaker':   a.get('nospeaker'),
            'type':        a.get('type'),
            'oral_qnum':   clean_oral_qnum(a.get('oral-qnum')),
            'text':        get_speech_text(speech),
        })

    if (i + 1) % chunk_size == 0:
        pd.DataFrame(rows).to_parquet(OUTPUT_PATH.parent / f'debates_chunk_{chunk_num}.parquet', index=False)
        print(f"  wrote chunk {chunk_num}")
        rows = []
        chunk_num += 1

# write remaining rows
if rows:
    pd.DataFrame(rows).to_parquet(OUTPUT_PATH.parent / f'debates_chunk_{chunk_num}.parquet', index=False)

# concatenate chunks
chunks = sorted(OUTPUT_PATH.parent.glob('debates_chunk_*.parquet'))
df = pd.concat([pd.read_parquet(c) for c in chunks])

df['date'] = pd.to_datetime(df['date'])
df['speech_id'] = df.index

df.to_parquet(OUTPUT_PATH, index=False)
print(f"saved {len(df):,} rows")

for c in chunks:
    Path(c).unlink()