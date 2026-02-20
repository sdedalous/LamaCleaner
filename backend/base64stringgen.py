import base64

mask_path = r"C:\Users\stebe\PycharmProjects\deep_edit\test_lama\mask.png"

with open(mask_path, "rb") as f:
    b64_bytes = base64.b64encode(f.read())

b64_str = b64_bytes.decode("utf-8")
data_url = f"data:image/png;base64,{b64_str}"

print(data_url)  # This is the string you will send to the /inpaint endpoint
