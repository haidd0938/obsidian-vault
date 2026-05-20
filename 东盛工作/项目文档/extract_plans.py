import fitz
import os

pdf_path = "/Users/mac/Desktop/成县民宿全套图纸.pdf"
doc = fitz.open(pdf_path)
print(f"Total pages: {doc.page_count}")

# Page 21 (0-indexed=20) - 一楼平面图
page = doc[20]
pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
pix.save("/Users/mac/Desktop/first_floor_layout.png")
print(f"Page 21 saved: {pix.width}x{pix.height}")

# Page 37 (0-indexed=36) - 二楼平面图
page = doc[36]
pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
pix.save("/Users/mac/Desktop/second_floor_layout.png")
print(f"Page 37 saved: {pix.width}x{pix.height}")

doc.close()
print("Done!")
