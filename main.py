import PyPDF2

reader = PyPDF2.PdfReader('./assets/浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf')

def extract_text_from_pdf(pdf_reader: PyPDF2.PdfReader):
    page_to_text = []
    for page_index, page in enumerate(pdf_reader.pages):
        page_to_text.append({
            'page': page_index,
            'text': page.extract_text()
        })
    return page_to_text


print(extract_text_from_pdf(reader))