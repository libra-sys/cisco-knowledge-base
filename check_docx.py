import zipfile
import xml.etree.ElementTree as ET

docx_path = r"C:\Users\吴海睿\Downloads\超绝牛逼网络笔记.docx"

with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read('word/document.xml')
    # Print first 3000 chars to understand the structure
    print(xml_content[:3000].decode('utf-8'))
