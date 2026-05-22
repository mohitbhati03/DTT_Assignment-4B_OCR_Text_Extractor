# ============================================
# OCR Text Extractor
# Assignment 4 - Computer Vision Project
# Technologies: Python, OpenCV, pytesseract
# ============================================

import cv2
import pytesseract
from PIL import Image
import os
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ============================================
# FUNCTION: Preprocess Image
# ============================================
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    denoised = cv2.GaussianBlur(thresh, (3, 3), 0)
    return denoised

# ============================================
# FUNCTION: Clean Extracted Text
# ============================================
def clean_text(text):
    # Step 1: Fix hyphenated words at line breaks → "non-\nessential" → "non-essential"
    text = re.sub(r'-\n(\S)', r'-\1', text)

    # Step 2: Add blank line before bullet points (* - • –)
    text = re.sub(r'\n([*\-•–])', r'\n\n\1', text)

    # Step 3: Join wrapped lines that are continuation of same sentence
    # Only join if: line doesn't end with . ! ? :  AND next line is NOT a bullet
    lines = text.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Empty line — keep as is
        if not line.strip():
            result.append('')
            i += 1
            continue

        # Try to join with next line if sentence continues
        while (i + 1 < len(lines) and
               not re.search(r'[.!?:]$', line.strip()) and
               lines[i + 1].strip() and
               not re.match(r'^[*\-•–]', lines[i + 1].strip())):
            i += 1
            line = line.strip() + ' ' + lines[i].strip()

        result.append(line.strip())
        i += 1

    # Step 4: Remove duplicate blank lines
    final = []
    for line in result:
        if line == '' and final and final[-1] == '':
            continue
        final.append(line)

    return '\n'.join(final).strip()

# ============================================
# FUNCTION: Extract Text from Image
# ============================================
def extract_text(image_path):
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at '{image_path}'")
        return None

    image = cv2.imread(image_path)
    if image is None:
        print("ERROR: Could not read image.")
        return None

    print(f"Image loaded: {image_path}")
    processed = preprocess_image(image)
    print("Image preprocessed (grayscale + threshold + denoise)")

    pil_image = Image.fromarray(processed)
    extracted_text = pytesseract.image_to_string(pil_image, lang='eng', config='--psm 3')

    extracted_text = clean_text(extracted_text)
    print("Text cleaned (broken lines joined)")

    return extracted_text

# ============================================
# FUNCTION: Display Extracted Text
# ============================================
def display_text(text):
    print("\n" + "-" * 40)
    print("         EXTRACTED TEXT")
    print("-" * 40)
    if text.strip():
        print(text.strip())
    else:
        print("(No text detected in image)")
    print("-" * 40 + "\n")

# ============================================
# FUNCTION: Save Text to File
# ============================================
def save_text(text, output_path="output/extracted_text.txt"):
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("=" * 40 + "\n")
        file.write("       OCR EXTRACTED TEXT\n")
        file.write("=" * 40 + "\n\n")
        file.write(text.strip())
        file.write("\n\n" + "=" * 40 + "\n")
    print(f"Text saved to: {output_path}")

# ============================================
# MAIN PROGRAM
# ============================================
if __name__ == "__main__":
    print("=" * 40)
    print("   OCR Text Extractor - Assignment 4")
    print("=" * 40)

    supported = ('.jpg', '.jpeg', '.png', '.bmp')
    os.makedirs("images", exist_ok=True)

    files = [f for f in os.listdir("images") if f.lower().endswith(supported)]

    if not files:
        print("ERROR: No image found in images/ folder!")
        exit()

    print(f"Found {len(files)} image(s): {files}\n")

    for filename in files:
        IMAGE_PATH = f"images/{filename}"
        print(f"Processing: {filename}")

        text = extract_text(IMAGE_PATH)

        if text is not None:
            display_text(text)
            output_name = filename.rsplit('.', 1)[0]
            save_text(text, f"output/{output_name}_extracted.txt")
        else:
            print(f"OCR failed for: {filename}")

        print("-" * 40)

    print(f"\nDone! {len(files)} image(s) processed.")
    print("Check output/ folder for extracted text files.")