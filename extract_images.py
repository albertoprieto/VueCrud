from docx import Document
import os

docx_path = 'Reporte Programa GPSubicacion 25-sep.docx'
output_dir = 'docx_images'
os.makedirs(output_dir, exist_ok=True)

doc = Document(docx_path)
img_count = 0
for rel in doc.part.rels.values():
    if 'image' in rel.target_ref:
        img_count += 1
        ext = rel.target_ref.split('.')[-1]
        img_path = os.path.join(output_dir, f'image_{img_count}.{ext}')
        with open(img_path, 'wb') as f:
            f.write(rel.target_part.blob)
print(f'Extracted {img_count} images to {output_dir}/')
