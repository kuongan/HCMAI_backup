// Sidebar.js
import {handleDateChange} from './date.js';
import {updateImageOverlay, updateImageGrid, get_url} from './utils.js';
import {handleKeyUp} from './object.js';
import { sendAllBoxesToBackend, initializeCanvas , drawGrid} from './color.js';
import {searchOCR, searchASR} from './OcrAsr.js'
import { handleRerankButtonClick} from './rerank.js';
import { search } from './searchtop.js'
import { handleUpload } from './image-query.js';

document.addEventListener("DOMContentLoaded", function() {
    const enterButton = document.getElementById('enter-btn');
    const uploadButton = document.getElementById('upload-btn');
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
    const rerankButtons = document.querySelectorAll('.rerank-btn');
    const topK = document.getElementById('input-topk')
    // Sự kiện khi checkbox được thay đổi (tạo hoặc xóa Text Query 2)
    document.getElementById("query-checkbox").addEventListener("change", function() {
        const isChecked = this.checked;

        // Kiểm tra nếu checkbox được bật, thì tạo query 2
        if (isChecked) {
            // Kiểm tra nếu đã tồn tại một phần tử text-query nào đó thì không tạo thêm
            if (document.getElementById('query-container-1')) {
                return; // Nếu đã tồn tại, không tạo thêm
            }

            // Create a new div to contain the label and textarea
            const newContainer = document.createElement('div');
            newContainer.id = 'query-container-1'; // Chỉ có một container với id cố định

            // Create a sub-container to hold the label
            const labelRemoveContainer = document.createElement('div');
            labelRemoveContainer.style.display = 'flex'; // Use flexbox to align label and button
            labelRemoveContainer.style.alignItems = 'center'; // Align items vertically in the center

            // Create the label for new text query
            const newLabel = document.createElement('label');
            newLabel.setAttribute('for', 'text-query-1');
            newLabel.textContent = 'Text Query 2'; // Chỉ tạo text query 2

            // Create the textarea for new text query with unique id
            const newTextArea = document.createElement('textarea');
            newTextArea.id = 'text-query-1'; // Assign fixed unique id
            newTextArea.rows = '4';
            newTextArea.cols = '50';
            newTextArea.placeholder = 'Enter your text query';

            // Append label to the labelRemoveContainer
            labelRemoveContainer.appendChild(newLabel);

            // Append the labelRemoveContainer and textarea to the newContainer
            newContainer.appendChild(labelRemoveContainer);
            newContainer.appendChild(newTextArea);

            // Append the newContainer to the additional-queries div
            document.getElementById('additional-queries').appendChild(newContainer);
        } else {
            // Nếu checkbox không được bật, ẩn và xóa Text Query 2 nếu tồn tại
            const queryContainer = document.getElementById('query-container-1');
            if (queryContainer) {
                queryContainer.remove();
            }
        }
    });

    // Sự kiện khi nhấn "Enter"
    // Sự kiện khi nhấn "Enter"
    enterButton.addEventListener('click', async function() {
        const model = document.getElementById('model-select').value;
        const topK = document.getElementById('input-topk').value;
        const mainTextQuery = document.getElementById('text-query').value;
        
        // Kiểm tra trạng thái của prompt-checkbox (Gemini)
        const gemini = document.getElementById('prompt-checkbox').checked;

        // Initialize queries object and add the main query first
        const textQuery = {};
        textQuery[0] = { id: 0, query: mainTextQuery };

        // Kiểm tra sự tồn tại của Text Query 2 (nếu checkbox đã bật)
        const textArea2 = document.getElementById('text-query-1');
        if (textArea2 && textArea2.value.trim() !== '') {
            textQuery[1] = { id: 1, query: textArea2.value };
        }

        // Log the number of text queries and their values
        console.log("Number of Text Queries:", Object.keys(textQuery).length);
        console.log("Text Queries:", textQuery);

        // Tạo payload và thêm gemini vào payload
        const payload = {
            model: model.toString(),
            textQuery: textQuery,  // textQuery là object chứa các {id, query}
            topK: topK.toString(),
            gemini: gemini  // Thêm giá trị gemini bool để kiểm tra trạng thái checkbox
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
                console.log("Response data:", data);
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


    let currentChain = "";  // Store the selected hierarchical path
    initializeCanvas();
    // Attach event listener for hierarchical search
    objectClassInput.addEventListener('keyup', handleKeyUp);
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
            max: parseInt(max),
            topk: parseInt(topK.value)
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

    enterocr.addEventListener('click', function() {
        searchOCR(ocrText, topK.value);
    });
    
    enterasr.addEventListener('click', function() {
        searchASR(asrText, topK.value);
    });
    
    // Add event listeners to the date inputs
    startDayInput.addEventListener('change', () => handleDateChange(startDayInput, endDayInput, topK.value));
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
                sendAllBoxesToBackend(topK.value);
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

    uploadButton.addEventListener('click', handleUpload)
    // Lắng nghe sự kiện click của nút Search
    document.getElementById('enter-search-btn').addEventListener('click', search);
    // Initial call to update overlay based on initial checkbox states
    updateImageOverlay(frameIdCheckbox, videoIdCheckbox, clusterCheckbox);
});
