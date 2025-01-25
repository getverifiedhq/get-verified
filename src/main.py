from get_verified import analyze, predict
import sys

filename = sys.argv[1]

with open(filename, "rb") as f:
    bytes = f.read()

boxes = predict(bytes, None)

print(boxes)

obj = analyze(boxes) if boxes is not None else None

print(obj)
