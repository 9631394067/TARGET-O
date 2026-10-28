"""
generate_sample_pdf.py
Generates a realistic Indian journal research paper PDF for testing.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
import os

OUTPUT_PATH = os.path.join("sample_pdfs", "indian_journal_sample.pdf")

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # ── Color scheme (IJCA style) ──────────────────────────
    HEADER_BG   = HexColor("#1a3c6e")
    ACCENT      = HexColor("#2563eb")
    LIGHT_GRAY  = HexColor("#f3f4f6")
    DARK_TEXT   = HexColor("#111827")
    MID_TEXT    = HexColor("#374151")

    styles = getSampleStyleSheet()
    story  = []

    # ══════════════════════════════════════════════════════
    # JOURNAL HEADER
    # ══════════════════════════════════════════════════════
    header_style = ParagraphStyle(
        "header", fontSize=9, textColor=white,
        alignment=TA_CENTER, leading=14, fontName="Helvetica-Bold"
    )
    sub_header_style = ParagraphStyle(
        "sub_header", fontSize=7.5, textColor=white,
        alignment=TA_CENTER, leading=11, fontName="Helvetica"
    )

    header_data = [[
        Paragraph("International Journal of Computer Applications (IJCA)", header_style),
    ],[
        Paragraph("ISSN: 0975-8887  |  Volume 185, No. 12, March 2024  |  www.ijcaonline.org", sub_header_style),
    ]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HEADER_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ══════════════════════════════════════════════════════
    # PAPER TITLE
    # ══════════════════════════════════════════════════════
    title_style = ParagraphStyle(
        "title", fontSize=15, textColor=HEADER_BG,
        alignment=TA_CENTER, leading=20,
        fontName="Helvetica-Bold", spaceAfter=8
    )
    story.append(Paragraph(
        "Deep Learning Based Crop Disease Detection Using<br/>"
        "Convolutional Neural Networks: A Study on Indian Agricultural Data",
        title_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT))
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════
    # AUTHORS
    # ══════════════════════════════════════════════════════
    author_style = ParagraphStyle(
        "authors", fontSize=10.5, textColor=DARK_TEXT,
        alignment=TA_CENTER, leading=16, fontName="Helvetica-Bold"
    )
    affil_style = ParagraphStyle(
        "affil", fontSize=8.5, textColor=MID_TEXT,
        alignment=TA_CENTER, leading=13, fontName="Helvetica"
    )
    story.append(Paragraph(
        "Dr. Ramesh Kumar Sharma<sup>1</sup>, "
        "Priya Gupta<sup>2</sup>, "
        "Anil Kumar Singh<sup>3</sup>, "
        "Sunita Verma<sup>1</sup>",
        author_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<sup>1</sup>Department of Computer Science &amp; Engineering, "
        "Indian Institute of Technology Delhi, New Delhi – 110016, India<br/>"
        "<sup>2</sup>School of Computing, Amity University, Noida, Uttar Pradesh – 201313, India<br/>"
        "<sup>3</sup>National Institute of Technology, Allahabad, Prayagraj – 211004, India",
        affil_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#d1d5db")))
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════
    # ABSTRACT
    # ══════════════════════════════════════════════════════
    section_label = ParagraphStyle(
        "section_label", fontSize=9.5, textColor=white,
        fontName="Helvetica-Bold", leading=14,
        leftIndent=5, spaceBefore=4, spaceAfter=4
    )
    body_style = ParagraphStyle(
        "body", fontSize=9, textColor=DARK_TEXT,
        alignment=TA_JUSTIFY, leading=14, fontName="Helvetica",
        leftIndent=5, rightIndent=5
    )
    bold_label = ParagraphStyle(
        "bold_label", fontSize=9.5, textColor=ACCENT,
        fontName="Helvetica-Bold", leading=14, spaceBefore=6
    )

    # Abstract label box
    abs_label = Table([[Paragraph("ABSTRACT", section_label)]], colWidths=[17*cm])
    abs_label.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), ACCENT),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(abs_label)
    story.append(Spacer(1, 0.2*cm))

    abstract_text = (
        "Agriculture is the backbone of the Indian economy, contributing approximately 17% to the "
        "national GDP and providing livelihood to over 58% of the population. Crop diseases are a "
        "major threat to agricultural productivity, causing losses estimated at 20–40% of global "
        "food production annually. Early and accurate identification of plant diseases is crucial "
        "for effective crop management and minimizing yield losses. This paper presents a robust "
        "deep learning framework using Convolutional Neural Networks (CNN) for automated detection "
        "and classification of crop diseases from leaf images. The proposed VGG-16 based transfer "
        "learning model is trained on the PlantVillage dataset augmented with field images collected "
        "from farms across Uttar Pradesh, Madhya Pradesh, and Maharashtra. The system achieves a "
        "classification accuracy of <b>97.83%</b> across 38 disease categories covering tomato, "
        "potato, corn, rice, and wheat — crops central to Indian agriculture. The model is "
        "optimized for edge deployment on low-cost Raspberry Pi devices used by farmers. "
        "Experimental results demonstrate significant improvement over existing approaches, "
        "with a 4.2% accuracy gain over ResNet-50 baseline on the Indian field dataset."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════
    # KEYWORDS
    # ══════════════════════════════════════════════════════
    kw_style = ParagraphStyle(
        "kw", fontSize=9, textColor=MID_TEXT,
        fontName="Helvetica", leading=14,
        leftIndent=5, rightIndent=5
    )
    story.append(Paragraph(
        "<b>Keywords:</b> Deep Learning, Convolutional Neural Networks, Crop Disease Detection, "
        "Transfer Learning, VGG-16, PlantVillage Dataset, Indian Agriculture, Edge Computing, "
        "Raspberry Pi, Image Classification",
        kw_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#d1d5db")))
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ══════════════════════════════════════════════════════
    story.append(Paragraph("1. INTRODUCTION", bold_label))
    story.append(Paragraph(
        "India is predominantly an agrarian economy where crop health directly impacts national "
        "food security and farmer livelihoods. Traditional disease diagnosis relies on visual "
        "inspection by agricultural experts, which is slow, expensive, and requires domain "
        "expertise often unavailable in rural regions. The advent of affordable smartphones "
        "and machine learning technologies presents an unprecedented opportunity to democratize "
        "crop disease diagnosis in India [1].",
        body_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Convolutional Neural Networks (CNN) have demonstrated remarkable success in computer "
        "vision tasks. Several studies have applied CNNs to plant disease detection with "
        "promising results [2, 3]. However, most existing models are trained on laboratory "
        "conditions that poorly represent real-world Indian field conditions characterized by "
        "variable lighting, soil backgrounds, and camera quality [4].",
        body_style
    ))

    # ══════════════════════════════════════════════════════
    # 2. METHODOLOGY
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("2. METHODOLOGY", bold_label))
    story.append(Paragraph(
        "The proposed system pipeline consists of four stages: (i) data collection and "
        "augmentation, (ii) preprocessing and segmentation, (iii) CNN feature extraction "
        "using VGG-16 with fine-tuned fully connected layers, and (iv) softmax classification. "
        "Field images were collected across 12 districts in three Indian states during the "
        "Kharif season 2023.",
        body_style
    ))

    # Results table
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Table 1: Performance Comparison on Indian Field Dataset", ParagraphStyle(
        "table_cap", fontSize=8.5, textColor=MID_TEXT,
        alignment=TA_CENTER, fontName="Helvetica-Bold", leading=12
    )))
    story.append(Spacer(1, 0.15*cm))

    table_data = [
        ["Model", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"],
        ["AlexNet",      "89.12", "87.45", "88.23", "87.84"],
        ["ResNet-50",    "93.61", "92.18", "93.04", "92.61"],
        ["InceptionV3",  "94.87", "93.92", "94.31", "94.11"],
        ["MobileNetV2",  "95.34", "94.87", "95.12", "94.99"],
        ["VGG-16 (Ours)","97.83", "97.41", "97.65", "97.53"],
    ]
    t = Table(table_data, colWidths=[4.5*cm, 3*cm, 3*cm, 3*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  HEADER_BG),
        ("TEXTCOLOR",    (0,0), (-1,0),  white),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT_GRAY, white]),
        ("BACKGROUND",   (0,-1),(-1,-1), HexColor("#dcfce7")),
        ("FONTNAME",     (0,-1),(-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",    (0,-1),(-1,-1), HexColor("#166534")),
        ("GRID",         (0,0), (-1,-1), 0.5, HexColor("#e5e7eb")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ]))
    story.append(t)

    # ══════════════════════════════════════════════════════
    # 3. CONCLUSION
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("3. CONCLUSION", bold_label))
    story.append(Paragraph(
        "This paper presented a VGG-16 based deep learning model for crop disease detection "
        "tailored to Indian agricultural conditions. The model achieves 97.83% accuracy and "
        "is deployable on edge devices, making it suitable for rural Indian farmers with limited "
        "connectivity. Future work includes expansion to 50+ disease categories and integration "
        "with the PM-KISAN farmer portal for real-time advisory services.",
        body_style
    ))

    # ══════════════════════════════════════════════════════
    # REFERENCES
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#d1d5db")))
    story.append(Paragraph("REFERENCES", bold_label))
    ref_style = ParagraphStyle(
        "ref", fontSize=8, textColor=MID_TEXT,
        fontName="Helvetica", leading=12, leftIndent=15,
        firstLineIndent=-15, spaceAfter=3
    )
    refs = [
        "[1] Prajapati, H. B., Shah, J. P., and Dabhi, V. K. (2017). Detection and classification of rice plant diseases. Intelligent Decision Technologies, 11(3), 357-373.",
        "[2] Mohanty, S. P., Hughes, D. P., and Salathé, M. (2016). Using deep learning for image-based plant disease detection. Frontiers in Plant Science, 7, 1419.",
        "[3] Ferentinos, K. P. (2018). Deep learning models for plant disease detection and diagnosis. Computers and Electronics in Agriculture, 145, 311-318.",
        "[4] Ramesh, S., Hebbar, R., Niveditha, M., Pooja, R., Shashank, N., and Vinod, P. V. (2018). Plant disease detection using machine learning. IEEE ICDCS, 1-5.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, ref_style))

    # ══════════════════════════════════════════════════════
    # FOOTER with DOI & publication info
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    footer_style = ParagraphStyle(
        "footer", fontSize=7.5, textColor=MID_TEXT,
        alignment=TA_CENTER, leading=11, fontName="Helvetica"
    )
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "DOI: 10.5120/ijca2024923456  |  Pages: 14–22  |  Volume 185, Issue 12  |  "
        "Published: March 2024  |  ISSN: 0975-8887<br/>"
        "© 2024 Foundation of Computer Science (FCS), NY, USA. All rights reserved.",
        footer_style
    ))

    doc.build(story)
    print(f"\n✅ PDF generated: {OUTPUT_PATH}")
    print(f"   Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

if __name__ == "__main__":
    os.makedirs("sample_pdfs", exist_ok=True)
    build_pdf()
