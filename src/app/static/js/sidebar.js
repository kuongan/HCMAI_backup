// Sidebar.js
import {handleDateChange} from './date.js';
import {updateImageOverlay, updateImageGrid, get_url} from './utils.js';
import {handleKeyUp} from './object.js';
import { sendAllBoxesToBackend, initializeCanvas , drawGrid} from './color.js';
import {searchOCR, searchASR} from './OcrAsr.js'
import { handleRerankButtonClick} from './rerank.js';

document.addEventListener("DOMContentLoaded", function() {
    const enterButton = document.getElementById('enter-btn');
    const frameIdCheckbox = document.getElementById('frame_id');
    const videoIdCheckbox = document.getElementById('video_id');
    const clusterCheckbox = document.getElementById('cluster');
    const startDayInput = document.getElementById('min');
    const endDayInput = document.getElementById('max');
    const enterod = document.getElementById('enter-od-btn');
    const objectClassInput = document.getElementById('object-class');
    const minInput = document.getElementById('object-class-min');
    const maxInput = document.getElementById('object-class-max');
    const ocrText = document.getElementById('ocr')
    const asrText = document.getElementById("asr")
    const enterocr = document.getElementById('enter-ocr')
    const enterasr = document.getElementById('enter-asr')
    console.log("ocrText",ocrText, "asrText", asrText, "enterocr", enterocr)
    const rerankButtons = document.querySelectorAll('.rerank-btn');
    let currentChain = "";  // Store the selected hierarchical path
    initializeCanvas();
    // Attach event listener for hierarchical search
    objectClassInput.addEventListener('keyup', handleKeyUp);
    // Handle search action when "enter" button is clicked
    enterod.addEventListener('click', async function() {
        const min = minInput.value;
        const max = maxInput.value;
        const objectClass = objectClassInput.value;

        // Validation: Ensure all fields are filled
        if (!objectClass || !min || !max) {
            alert('Please fill in all fields (Object Class, Min, and Max)');
            return;
        }

        // Split the object class chain by '>' and get the deepest subclass
        const chainParts = objectClass.split(">").map(part => part.trim()).filter(Boolean);
        const deepestClass = chainParts[chainParts.length - 1];
        console.log("deepestClass", deepestClass)
        // Create the payload for Elasticsearch search
        const payload = {
            objectClass: deepestClass,  // Use the deepest class for search
            min: parseInt(min),
            max: parseInt(max)
        };
        
        try {
            // Send the payload to the backend for Elasticsearch search
            const response = await fetch('/object', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                const imageUrls = data.data.map(item => ({
                    url: get_url(item.frame_id, item.video_id, item.position),
                    frameId: item.frame_id,
                    videoId: item.video_id
                }));
                updateImageGrid(imageUrls);
            } else {
                console.error('Response not OK:', response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
    enterButton.addEventListener('click', async function() {
        const model = document.getElementById('model-select').value;
        const textQuery = document.getElementById('text-query').value;

        const payload = {
            model: model.toString(),
            textQuery: textQuery.toString(),
        };

        try {
            const response = await fetch('/side-bar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                const imageUrls = data.data.map(item => ({
                    url: get_url(item.frame_id, item.video_id, item.position),
                    frameId: item.frame_id,
                    videoId: item.video_id
                }));
                updateImageGrid(imageUrls);
            } else {
                console.error('Response not OK:', response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    enterocr.addEventListener('click', function() {
        searchOCR(ocrText);
    });
    
    enterasr.addEventListener('click', function() {
        searchASR(asrText);
    });
    
    // Add event listeners to the date inputs
    startDayInput.addEventListener('change', () => handleDateChange(startDayInput, endDayInput));
    endDayInput.addEventListener('change', () => handleDateChange(startDayInput, endDayInput));

    // Attach event listeners to the checkboxes to trigger updateImageOverlay when they change
    frameIdCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });
    videoIdCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });
    clusterCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });

    //color.js
        // Send boxes to backend when Enter is pressed
    $(document).keypress(function(e) {
        if (e.which === 13) {  // Enter key code
            console.log("Enter pressed");
    
            // Check if there are any draggable boxes on the canvas
            if ($(".draggable-box").length > 0) {
                console.log("Boxes found, sending box details to backend");
                sendAllBoxesToBackend();
            } else {
                console.log("No boxes found on the canvas");
            }
        }
    });
    // Clear the canvas
    $("#trashIcon").click(function() {
        console.log("Clearing the canvas");
        $("#canvasContainer").empty();
        drawGrid(252 / 7, 154 / 7);
    });

    // Gán sự kiện click cho tất cả các nút rerank
    rerankButtons.forEach(function(button) {
        button.addEventListener('click', handleRerankButtonClick);
    });
    // Initial call to update overlay based on initial checkbox states
    updateImageOverlay(frameIdCheckbox, videoIdCheckbox, clusterCheckbox);

});

