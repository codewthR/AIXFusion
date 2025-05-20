import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import DocUploadForm
from docx import Document
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from django.contrib import messages




def presenting(response):
    return render(response,'product.html')




import os
import tempfile
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline


# Initialize NLP summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def ho(request):
    return render(request, 'writetext.html')

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_pdf(path):
    pdf_doc = fitz.open(path)
    return "\n".join([page.get_text() for page in pdf_doc])

def split_text_into_chunks(text, max_tokens=500):
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def summarize_text(text):
    chunks = split_text_into_chunks(text)
    summary = []
    for chunk in chunks:
        try:
            result = summarizer(chunk, max_length=80, min_length=30, do_sample=False)
            summary.append(result[0]['summary_text'])
        except:
            summary.append(chunk)  # fallback
    return summary

@csrf_exempt
def convert_text_to_ppt(request):
    if request.method == 'POST':
        title = request.POST.get("title", "Untitled Presentation")
        author = request.POST.get("author", "Anonymous")
        raw_text = request.POST.get("text", "")

        if not raw_text.strip():
            return HttpResponse("No text provided.")

        # Summarize
        summarized_sections = summarize_text(raw_text)

        # Create PowerPoint
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # Title Slide
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = title
        slide.placeholders[1].text = author

        # Content Slides
        for i, section in enumerate(summarized_sections, start=1):
            slide = prs.slides.add_slide(content_slide_layout)
            slide.shapes.title.text = f"Slide {i}"
            body_shape = slide.shapes.placeholders[1]
            tf = body_shape.text_frame
            for line in section.split(". "):
                if line.strip():
                    tf.add_paragraph().text = "• " + line.strip()

        # Output PPT
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























import os
import tempfile
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from django.http import HttpResponse
from django.shortcuts import render
from docx import Document
from transformers import pipeline


# Initialize NLP pipelines
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")



def home(request):
    return render(request, 'upload.html')

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_pdf(path):
    pdf_doc = fitz.open(path)
    return "\n".join([page.get_text() for page in pdf_doc])

def split_text_into_chunks(text, max_tokens=500):
    # Rough chunking
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def summarize_text(text):
    chunks = split_text_into_chunks(text)
    summary = []
    for chunk in chunks:
        try:
            result = summarizer(chunk, max_length=80, min_length=30, do_sample=False)
            summary.append(result[0]['summary_text'])
        except:
            summary.append(chunk)  # fallback
    return summary

def convert_to_ppt(request):
    if request.method == 'POST' and request.FILES.get('input_file'):
        Title = request.POST.get("Title")
        author = request.POST.get("author")
        input_file = request.FILES['input_file']
        file_ext = os.path.splitext(input_file.name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            for chunk in input_file.chunks():
                temp.write(chunk)
            temp_path = temp.name

        # Extract text based on file type
        if file_ext in ['.doc', '.docx']:
            raw_text = extract_text_from_docx(temp_path)
        elif file_ext == '.pdf':
            raw_text = extract_text_from_pdf(temp_path)
        else:
            return HttpResponse("Unsupported file format.")

        # NLP Summary
        summarized_sections = summarize_text(raw_text)

        # PowerPoint Generation
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # Title Slide
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = Title
        slide.placeholders[1].text = author

        # Content Slides
        for i, section in enumerate(summarized_sections, start=1):
            slide = prs.slides.add_slide(content_slide_layout)
            slide.shapes.title.text = f"Slide {i}"
            body_shape = slide.shapes.placeholders[1]
            tf = body_shape.text_frame
            for line in section.split(". "):
                if line.strip():
                    tf.add_paragraph().text = "• " + line.strip()

        # Return PPTX as response
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
        prs.save(output_path)
        with open(output_path, 'rb') as ppt_file:
            response = HttpResponse(
                ppt_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            response['Content-Disposition'] = 'attachment; filename="converted.pptx"'
            return response

    return HttpResponse("Invalid request")
