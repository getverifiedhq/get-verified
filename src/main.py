from get_verified import analyze, predict

filename = "test.png"

with open(filename, "rb") as f:
    bytes = f.read()

boxes = predict(bytes, None)

if boxes is None:
    raise ValueError

obj = analyze(boxes)

if obj is None:
    raise ValueError

print(obj)
