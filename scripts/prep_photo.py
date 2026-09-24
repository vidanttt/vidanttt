from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    output_path = input_path.parent / "source-prepped.png"

    print("1/3 Removing background...")

    with open(input_path, "rb") as f:
        original = f.read()

    result = remove(original)

    temp_path = input_path.parent / "_temp-no-bg.png"

    with open(temp_path, "wb") as f:
        f.write(result)

    print("2/3 Improving contrast...")

    image = cv2.imread(str(temp_path), cv2.IMREAD_UNCHANGED)

    if image is None:
        print("❌ Could not read processed image.")
        sys.exit(1)

    # Separate RGB/BGR and alpha
    if image.shape[2] == 4:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
    else:
        bgr = image
        alpha = np.full(
            (image.shape[0], image.shape[1]),
            255,
            dtype=np.uint8,
        )

    # Convert to grayscale
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8),
    )

    gray = clahe.apply(gray)

    # Put the subject on a pure white background.
    white = np.full_like(gray, 255)

    alpha_float = alpha.astype(np.float32) / 255.0

    final = (
        gray.astype(np.float32) * alpha_float
        + white.astype(np.float32) * (1 - alpha_float)
    ).astype(np.uint8)

    print("3/3 Saving...")

    Image.fromarray(final).save(output_path)

    temp_path.unlink(missing_ok=True)

    print()
    print("✅ Done!")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()