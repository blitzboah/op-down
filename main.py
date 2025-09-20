import sys
import os
import requests
import img2pdf
import subprocess
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

path = 'out/'

def download_file(filename, url):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def main():
    os.makedirs(path, exist_ok=True)

    url = sys.argv[1]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pictures = soup.find_all('picture')

    img_urls = [pic.img['src'] for pic in pictures]

    # yeah very retarded shi
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for i, url in enumerate(img_urls):
            ext = os.path.splitext(url)[-1] or ".png"
            filename = os.path.join(path, f"image_{i}{ext}")
            futures.append(executor.submit(download_file, filename, url))
            print(f"queued page {i}")

        for i, future in enumerate(as_completed(futures)):
            future.result()
            print(f"downloaded page {i}")

    image_files = sorted(
    [os.path.join(path, i) for i in os.listdir(path) if i.endswith(".png")],
    key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("_")[1])
    )

    print("converting to pdf")
    pdf_data = img2pdf.convert(image_files)
    with open(os.path.join(path, 'output.pdf'), 'wb') as f:
        f.write(pdf_data)

    subprocess.run("rm -f out/*.png", shell=True, check=True)

if __name__ == "__main__":
    main()
