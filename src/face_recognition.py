from deepface import DeepFace

result = DeepFace.verify(
  img1_path = "Screenshot 2025-01-27 at 14.57.18.png",
  img2_path = "Screenshot 2025-01-27 at 14.57.42.png",
)

print(result)