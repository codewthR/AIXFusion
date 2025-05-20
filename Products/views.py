
from django.shortcuts import render
from docx import Document
import PyPDF2  # lighter than fitz
from pptx import Presentation
from pptx.util import Inches
import nltk


def presenting(response):
    return render(response,'product.html')



import os
import tempfile
from pptx import Presentation
from pptx.util import Inches
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


def ho(request):
    return render(request, 'writetext.html')


def summarize_text(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return [str(sentence) for sentence in summary]


@csrf_exempt
def convert_text_to_ppt(request):
    if request.method == 'POST':
        title = request.POST.get("title", "Untitled Presentation")
        author = request.POST.get("author", "Anonymous")
        raw_text = request.POST.get("text", "")

        if not raw_text.strip():
            return HttpResponse("No text provided.")

        summarized_sections = summarize_text(raw_text)

        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # Title Slide
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = title
        slide.placeholders[1].text = author

        # Content Slide
        slide = prs.slides.add_slide(content_slide_layout)
        slide.shapes.title.text = "Summary"
        body_shape = slide.shapes.placeholders[1]
        tf = body_shape.text_frame
        for line in summarized_sections:
            tf.add_paragraph().text = "• " + line.strip()

        # Save and return as HTTP response
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_ppt:
            prs.save(tmp_ppt.name)
            tmp_ppt.seek(0)
            response = HttpResponse(
                tmp_ppt.read(),
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            response['Content-Disposition'] = 'attachment; filename="text_to_ppt.pptx"'
            return response

    return HttpResponse("Invalid request method.")








import nltk
nltk.download('punkt_tab')
# Ensure NLTK punkt tokenizer is available
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize


def home(request):
    return render(request, 'upload.html')


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_text_from_pdf(path):
    text = ""
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def split_text_into_chunks(text, max_chars=800):
    sentences = sent_tokenize(text)
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) <= max_chars:
            current += sent + " "
        else:
            chunks.append(current.strip())
            current = sent + " "
    if current:
        chunks.append(current.strip())
    return chunks


def basic_summarize(text):
    chunks = split_text_into_chunks(text)
    summary = []
    for chunk in chunks:
        lines = sent_tokenize(chunk)
        if len(lines) > 2:
            summary.append(lines[0] + " " + lines[1])
        else:
            summary.append(chunk)
    return summary


def convert_to_ppt(request):
    if request.method == 'POST' and request.FILES.get('input_file'):
        title = request.POST.get("Title", "Presentation Title")
        author = request.POST.get("author", "Author")
        input_file = request.FILES['input_file']
        ext = os.path.splitext(input_file.name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
            for chunk in input_file.chunks():
                temp.write(chunk)
            temp_path = temp.name

        # Extract text
        if ext in ['.doc', '.docx']:
            raw_text = extract_text_from_docx(temp_path)
        elif ext == '.pdf':
            raw_text = extract_text_from_pdf(temp_path)
        else:
            return HttpResponse("Unsupported file format.")

        # Summarize
        summaries = basic_summarize(raw_text)

        # PPT creation
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # Title Slide
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = title
        slide.placeholders[1].text = author

        # Content Slides
        for i, section in enumerate(summaries, 1):
            slide = prs.slides.add_slide(content_slide_layout)
            slide.shapes.title.text = f"Slide {i}"
            tf = slide.placeholders[1].text_frame
            for sent in sent_tokenize(section):
                if sent.strip():
                    tf.add_paragraph().text = "• " + sent.strip()

        # Serve PPT
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
        prs.save(output_path)
        with open(output_path, 'rb') as ppt_file:
            response = HttpResponse(
                ppt_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            response['Content-Disposition'] = 'attachment; filename="converted.pptx"'
            return response

    return HttpResponse("Invalid request.")
