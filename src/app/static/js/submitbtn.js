import { getActiveTaskGridId } from './date.js';
export function handleSubmitButtonClick() {
    const submitButtons = document.querySelectorAll('.submit-button');
    const popupContainer = document.getElementById('popup-container');
    const popupOverlay = document.getElementById('popup-overlay');
    const confirmSubmitButton = document.getElementById('add-btn');
    const viewPopup = document.getElementById('view-popup');
    let isSubmitEventAttached = false;

    submitButtons.forEach(button => {
        button.addEventListener('click', function () {
            const activeGridId = getActiveTaskGridId();
            if (!activeGridId) {
                console.error("No active task grid found.");
                return;
            }
            const taskGrid = document.getElementById(activeGridId);
            if (!taskGrid) {
                console.error("Task grid not found.");
                return;
            }
            const imageElements = taskGrid.querySelectorAll('.grid-item');
            const imageUrls = [];
            let count = 0;

            // Collect image URLs (only first 100)
            imageElements.forEach(item => {
                if (count >= 100) return;
                const imgElement = item.querySelector('img');
                if (imgElement) {
                    const imgUrl = imgElement.src;
                    imageUrls.push(imgUrl);
                    count++;
                }
            });

            console.log("Collected image URLs:", imageUrls);
            const qaCheckbox = popupContainer.querySelector('#question-check');
            const qaInputContainer = popupContainer.querySelector('.answer-group');

            // Show popup and overlay
            popupContainer.style.display = 'block';
            qaCheckbox.checked = false;
            qaInputContainer.style.display = 'none';
            popupOverlay.style.display = 'block';

            // Set frame_id and video_id from button's data attributes
            const frame_id = document.getElementById('frame-id');
            const video_id = document.getElementById('video-id');

            frame_id.value = this.getAttribute('data-frame-id');
            video_id.value = this.getAttribute('data-video-id');
            frame_id.readOnly = true;
            video_id.readOnly = true;

            // Toggle the visibility of the answer fields when the checkbox is checked or unchecked
            qaCheckbox.addEventListener('change', function () {
                if (this.checked) {
                    qaInputContainer.style.display = 'flex';
                } else {
                    qaInputContainer.style.display = 'none';
                }
            });

            const queryInput = document.getElementById('query-id');
            queryInput.addEventListener('input', function () {
                queryID = this.value;
            });

            // Attach the submit event handler only once
            if (!isSubmitEventAttached) {
                confirmSubmitButton.addEventListener('click', async function () {
                    const rank = parseInt(document.getElementById('rank').value);
                    const answer = document.getElementById('answer').value || null;
                    const min = document.getElementById('min-submit').value ? parseInt(document.getElementById('min-submit').value) : null;
                    const max = document.getElementById('max-submit').value ? parseInt(document.getElementById('max-submit').value) : null;

                    // Dynamically update the queryID and isQuestion just before submission
                    const queryID = queryInput.value;
                    const isQuestion = qaCheckbox.checked;

                    // Build payload
                    const payload = {
                        imageUrls: imageUrls,
                        frame_id: frame_id.value,
                        video_id: video_id.value,
                        query_id: queryID,
                        rank: rank,
                        answer: answer,
                        min: min,
                        max: max,
                        isQuestion: isQuestion
                    };

                    try {
                        // Send data to FastAPI backend
                        const response = await fetch('http://127.0.0.1:8000/submit', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload),
                        });

                        if (response.ok) {
                            console.log('Data successfully sent to FastAPI');
                        } else {
                            console.error('Error sending data to FastAPI', response);
                        }
                    } catch (error) {
                        console.error('Error:', error);
                    }
                });

                isSubmitEventAttached = true;
            }

            const viewButton = document.getElementById('view-file-btn');
            const closePopupBtn = document.getElementById('close-popup-btn');
            const savePopupBtn = document.getElementById('save-popup-btn');

            viewButton.addEventListener('click', async function () {
                // Dynamically update the queryID and isQuestion just before loading the file
                const queryID = queryInput.value;
                const isQuestion = qaCheckbox.checked;
                const filename = `query-p3-${queryID}-${isQuestion ? 'qa' : 'kis'}.csv`;

                try {
                    // Fetch the file content from the server
                    const response = await fetch(`http://127.0.0.1:8000/load?filename=${filename}`);
                    if (response.ok) {
                        const data = await response.json();
                        document.getElementById('query-id-header').innerText = queryID;
                        document.getElementById('view-file-textarea').value = data.content;
                        viewPopup.style.display = 'block';
                        popupOverlay.style.display = 'block';
                    } else {
                        console.error(`Error loading file: ${filename}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });

            savePopupBtn.addEventListener('click', async function () {
                const textareaContent = document.getElementById('view-file-textarea').value;
                const filename = `query-p3-${queryInput.value}-${qaCheckbox.checked ? 'qa' : 'kis'}.csv`;

                const payload = {
                    filename: filename,
                    content: textareaContent
                };

                try {
                    const response = await fetch('http://127.0.0.1:8000/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    });

                    if (response.ok) {
                        console.log('File successfully updated');
                    } else {
                        console.error('Error saving file:', response);
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });

            // Close Popup
            closePopupBtn.addEventListener('click', function () {
                viewPopup.style.display = 'none';
            });

            // Close popup when clicking outside of it (on the overlay)
            popupOverlay.addEventListener('click', function () {
                popupContainer.style.display = 'none';
                viewPopup.style.display = 'none';
                popupOverlay.style.display = 'none';
            });
        });
    });
}
