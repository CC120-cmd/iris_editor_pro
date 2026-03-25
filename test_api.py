import requests

url = "https://iris-editor-pro-6-3ghb.onrender.com/swap"

files = {
    "source": open("image1.jpg", "rb"),
    "target": open("image2.jpg", "rb"),
}

print("Sending request...")

res = requests.post(url, files=files)

with open("result.jpg", "wb") as f:
    f.write(res.content)

print("Done! Check result.jpg")