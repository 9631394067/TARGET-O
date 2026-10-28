# ============================================
# tests/conftest.py - Shared Test Fixtures
# ============================================
import pytest


SAMPLE_INDIAN_JOURNAL_TEXT = """
International Journal of Computer Applications (0975 – 8887)
Volume 183 – No.22, September 2021

Deep Learning Based Plant Disease Detection Using Convolutional Neural Networks

Dr. Ramesh Sharma1, Priya Gupta2, Anil Kumar Singh3
1Department of CSE, IIT Delhi, New Delhi - 110016
2School of Computing, Amity University, Noida
3NIT Allahabad, Prayagraj, UP

Abstract: This paper proposes a robust deep learning model for plant disease
detection using convolutional neural networks (CNN). The model is trained on
the PlantVillage dataset containing 54,306 images. Our approach achieves
97.8% classification accuracy across 38 disease categories. The model is
optimized for deployment on low-cost edge devices used by Indian farmers.

Keywords: Deep Learning, Convolutional Neural Network, Plant Disease Detection,
Image Classification, Precision Agriculture, Indian Agriculture

1. Introduction
Agriculture is the backbone of the Indian economy...

DOI: 10.5120/ijca2021921534
ISSN: 0975-8887
Pages: 12-19
"""

SAMPLE_CONFERENCE_TEXT = """
2023 International Conference on Intelligent Computing and Data Science (ICICDS 2023)
IEEE Xplore Digital Library
ISBN: 978-1-6654-9876-5

Federated Learning for Privacy-Preserving Healthcare Data Analysis in India

Neha Agarwal, Suresh Patel, Vikram Bhatia
Indian Institute of Technology Bombay, Mumbai, India

Abstract: Healthcare data privacy is a critical concern in the Indian medical ecosystem.
This paper presents a federated learning framework that enables collaborative model
training without sharing sensitive patient data across hospitals.

Keywords: Federated Learning, Healthcare AI, Privacy, India

pp. 145-152
DOI: 10.1109/ICICDS2023.456789
"""


@pytest.fixture
def indian_journal_text():
    return SAMPLE_INDIAN_JOURNAL_TEXT


@pytest.fixture
def conference_text():
    return SAMPLE_CONFERENCE_TEXT
