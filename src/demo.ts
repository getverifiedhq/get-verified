const tesseract = require("tesseract.js");
const path = require("path");

// Function to perform OCR on an image
async function performOCR(imagePath: any) {
    try {
        console.log("Starting OCR...");
        const result = await tesseract.recognize(imagePath, 'eng', {
            logger: (info: any) => console.log(info) // Logs progress information
        });

        console.log("OCR Completed");
        console.log("Extracted Text:");
        console.log(result.data.text);

        return result.data.text;
    } catch (error) {
        console.error("Error during OCR:", error);
        throw error;
    }
}

// Example usage
(async () => {
    const imagePath = path.join(__dirname, "../abc.png"); // Replace with your image path
    const extractedText = await performOCR(imagePath);
    console.log("Extracted Text from Image:", extractedText);
})();
