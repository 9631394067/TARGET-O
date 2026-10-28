"""Test the PDF parse API with the sample PDF"""
import urllib.request, json

pdf_path = 'sample_pdfs/indian_journal_sample.pdf'
boundary = 'CitationParserBoundary12345'
disp = 'Content-Disposition: form-data; name="file"; filename="indian_journal_sample.pdf"'

with open(pdf_path, 'rb') as f:
    pdf_data = f.read()

body  = ('--' + boundary + '\r\n').encode()
body += (disp + '\r\n').encode()
body += b'Content-Type: application/pdf\r\n\r\n'
body += pdf_data
body += ('\r\n--' + boundary + '--\r\n').encode()

req = urllib.request.Request(
    'http://localhost:8000/api/v1/parse/pdf?use_ai=false&lookup_crossref=true',
    data=body, method='POST',
    headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    m = data.get('metadata', {})
    print('SUCCESS   :', data.get('success'))
    print('Message   :', data.get('message'))
    print('Title     :', m.get('title'))
    print('Authors   :', m.get('authors'))
    print('Year      :', m.get('year'))
    print('DOI       :', m.get('doi'))
    print('Journal   :', m.get('journal'))
    print('Volume    :', m.get('volume'))
    print('Issue     :', m.get('issue'))
    print('Pages     :', m.get('pages'))
    print('ISSN      :', m.get('issn'))
    print('Keywords  :', m.get('keywords'))
    print('Source    :', m.get('source'))
    print('Confidence:', m.get('confidence_score'))
    print()
    print('=== BibTeX Output ===')
    print(data.get('bibtex'))
