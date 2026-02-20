import os
import gc
from multiprocessing import Pool, cpu_count
from collections import Counter
from PIL import Image
from tqdm import tqdm

# -----------------------------------------
# CONFIG
# -----------------------------------------
ROOT = r"C:\Users\stebe\Downloads\organized\person"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
PROBLEM_FILE_LOG = os.path.join(ROOT, "problem_files.txt")


# -----------------------------------------
# Worker function
# -----------------------------------------
def analyze_one(path):
    try:
        img = Image.open(path)
        img.load()

        mode = img.mode
        has_icc = "icc_profile" in img.info

        img.close()
        del img
        gc.collect()

        return (True, mode, has_icc, path)

    except Exception as e:
        return (False, None, None, (path, str(e)))


# -----------------------------------------
# Collect all image paths
# -----------------------------------------
def iter_images(root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXTS:
                yield os.path.join(dirpath, f)


# -----------------------------------------
# Main
# -----------------------------------------
def main():
    paths = list(iter_images(ROOT))
    total = len(paths)

    print(f"Scanning {total} images...\n")

    mode_counter = Counter()
    icc_counter = Counter()
    ext_counter = Counter()
    problem_files = []

    with Pool(processes=max(cpu_count() - 1, 1)) as pool:
        for ok, mode, has_icc, data in tqdm(
            pool.imap_unordered(analyze_one, paths, chunksize=64),
            total=total,
            desc="Analyzing",
            ncols=80
        ):
            if ok:
                mode_counter[mode] += 1
                icc_counter["has_icc" if has_icc else "no_icc"] += 1
                ext = os.path.splitext(data)[1].lower()
                ext_counter[ext] += 1
            else:
                problem_files.append(data)

    # Write problem files
    if problem_files:
        with open(PROBLEM_FILE_LOG, "w", encoding="utf-8") as f:
            for path, err in problem_files:
                f.write(f"{path} :: {err}\n")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Total images: {total}")
    print(f"With ICC: {icc_counter['has_icc']}")
    print(f"Without ICC: {icc_counter['no_icc']}\n")

    print("Modes:")
    for mode, count in mode_counter.most_common():
        print(f"  {mode}: {count}")

    print("\nExtensions:")
    for ext, count in ext_counter.most_common():
        print(f"  {ext}: {count}")

    if problem_files:
        print(f"\nProblem files logged to: {PROBLEM_FILE_LOG}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()
