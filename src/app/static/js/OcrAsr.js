// Get the elements
import { get_url, updateImageGrid } from './utils.js';
// Function to handle the OCR search
export async function searchOCR(ocrText, topK) {
    const ocrValue = ocrText.value; // Get the value from the OCR text field
    const payload = { ocr: ocrValue, topk: parseInt(topK) };
    console.log(ocrValue)
    try {
        // Make a fetch request to the /ocr route
        const response = await fetch('http://127.0.0.1:8000/ocr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload) // Send OCR text as JSON
        });

        if (response.ok) {
            const data = await response.json();
            // Map the data to create image URLs
            const imageUrls = data.data.map(item => ({
                url: get_url(item.frame_id, item.video_id, item.position),
                frameId: item.frame_id,
                videoId: item.video_id
            }));

            // Update the image grid with URLs
            updateImageGrid(imageUrls);
        } else {
            console.error('Response not OK:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Function to handle the ASR search
export async function searchASR(asrText, topK) {
    const asrValue = asrText.value; // Get the value from the ASR text field
    const payload = { asr: asrValue, topk: parseInt(topK)};
    console.log(asrValue)
    try {
        // Make a fetch request to the /ocr route
        const response = await fetch('http://127.0.0.1:8000/asr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload) // Send OCR text as JSON
        });

        if (response.ok) {
            const data = await response.json();
            // Map the data to create image URLs
            const imageUrls = data.data.map(item => ({
                url: get_url(item.frame_id, item.video_id, item.position),
                frameId: item.frame_id,
                videoId: item.video_id
            }));

            // Update the image grid with URLs
            updateImageGrid(imageUrls);
        } else {
            console.error('Response not OK:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
