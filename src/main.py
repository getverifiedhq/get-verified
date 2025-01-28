from document_feature_detection import document_feature_detection, verify_identity_document
import sys

filename = sys.argv[1]

with open(filename, "rb") as f:
    bytes = f.read()

boxes = document_feature_detection(bytes)

print(boxes)

obj = verify_identity_document(bytes, boxes) if boxes is not None else None

print(obj)
