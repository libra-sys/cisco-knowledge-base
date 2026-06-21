import zipfile
import xml.etree.ElementTree as ET
import sys

docx_path = r"C:\Users\吴海睿\Downloads\超绝牛逼网络笔记.docx"
output_path = r"E:\ciscotop\network_notes.md"

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'

def get_text_from_docx(path):
    with zipfile.ZipFile(path, 'r') as z:
        xml_content = z.read('word/document.xml')
    
    tree = ET.fromstring(xml_content)
    body = tree.find(f'{{{W}}}body')
    
    paragraphs = []
    for p in body:
        tag = p.tag.split('}')[-1] if '}' in p.tag else p.tag
        if tag != 'p':
            continue
        
        texts = []
        for elem in p.iter():
            ttag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if ttag == 't' and elem.text:
                texts.append(elem.text)
        
        para_text = ''.join(texts)
        
        # Check for heading style
        pPr = p.find(f'{{{W}}}pPr')
        heading = False
        if pPr is not None:
            pStyle = pPr.find(f'{{{W}}}pStyle')
            if pStyle is not None:
                style_val = pStyle.get(f'{{{W}}}val', '')
                if 'eading' in style_val or 'eading' in style_val:
                    try:
                        level_str = ''.join(c for c in style_val if c.isdigit())
                        level = int(level_str) if level_str else 2
                        level = max(1, min(6, level))
                        para_text = '#' * level + ' ' + para_text
                        heading = True
                    except:
                        pass
        
        # Check for numbering (list item)
        if not heading and para_text.strip():
            numPr = pPr.find(f'{{{W}}}numPr') if pPr is not None else None
            if numPr is not None:
                para_text = '- ' + para_text
        
        if para_text.strip():
            paragraphs.append(para_text)
        else:
            paragraphs.append('')
    
    # Remove consecutive empty lines
    result = []
    prev_empty = False
    for p in paragraphs:
        if not p.strip():
            if not prev_empty:
                result.append('')
                prev_empty = True
        else:
            result.append(p)
            prev_empty = False
    
    # Remove leading/trailing empty
    while result and not result[0]:
        result.pop(0)
    while result and not result[-1]:
        result.pop()
    
    return '\n\n'.join(result)

try:
    text = get_text_from_docx(docx_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"OK: {len(text)} chars, ~{text.count(chr(10))} lines")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
