export function handleSubmitButtonClick() {
    const submitButtons = document.querySelectorAll('.submit-button');
    const popupContainer = document.getElementById('popup-container');
    const popupOverlay = document.getElementById('popup-overlay');
    const cancel = document.getElementById('cancel');
    const Frame_id = document.getElementById('frame-id');
    const Video_id = document.getElementById('video-id');

    const randomButton = document.getElementById('random');
    const questionIdInput = document.getElementById('question-id');
    const qaTypeSelect = document.getElementById('QA');
    const minValueFrameInput = document.getElementById('min-value-frame');
    const maxValueFrameInput = document.getElementById('max-value-frame');
    const numberRandomInput = document.getElementById('Number-random');
    const minFrameDisplay = document.getElementById('min-frame-value-display');
    const maxFrameDisplay = document.getElementById('max-frame-value-display');
    const Quantity = document.getElementById('Quantity');
    submitButtons.forEach(button => {
        button.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            const frameId = this.getAttribute('data-frame-id');

            // Hiển thị popup và overlay
            popupContainer.style.display = 'block';
            popupOverlay.style.display = 'block';
            Frame_id.value = frameId;
            Video_id.value = videoId;
        });
    });

    // Event listener for the Random button
    randomButton.addEventListener('click', function () {
        const videoId = Video_id.value; 
        const frameId = Frame_id.value
        

        // Tạo payload
        let payload = {
            videoId: videoId,
            frameId: frameId,
            questionId: questionIdInput.value.trim(),
            qaType: qaTypeSelect.value,
            minFrameValue: minFrameDisplay.textContent,
            maxFrameValue: maxFrameDisplay.textContent,
            Quantity:Quantity.value,
            randomNumber: numberRandomInput.value,
        };

        // Gửi payload dạng JSON
        fetch('http://127.0.0.1:8000/save-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        }).then(response => {
            if (response.ok) {
                questionIdInput.value = ''; 
                minValueFrameInput.value = ''; 
                maxValueFrameInput.value = ''; 
                Quantity.value = '';
                numberRandomInput.value = ''; 
                popupContainer.style.display = 'none';
                popupOverlay.style.display = 'none';
            } else {
                alert('Error saving data!');
            }
        }).catch(err => {
            alert('Error sending CSV data: ' + err); 
            console.error('Error sending CSV data:', err);
        });

    });

    document.getElementById('insert').addEventListener('click', function() {
        // Hiển thị bảng nhỏ khi bấm Insert
        document.getElementById('small-popup-container').style.display = 'block';
    });

    document.getElementById('small-popup-close').addEventListener('click', function() {
        // Đóng bảng nhỏ khi bấm nút Close
        document.getElementById('small-popup-container').style.display = 'none';
    });

    const text_small = document.getElementById('small-text-input')

    document.getElementById('small-popup-save').addEventListener('click', function() {
        // Đóng bảng nhỏ khi bấm nút Close
        document.getElementById('small-popup-container').style.display = 'none';
        let payload = {
            questionId: questionIdInput.value.trim(),
            text: text_small.value,
            qaType: qaTypeSelect.value,
        };

        // Gửi payload dạng JSON
        fetch('http://127.0.0.1:8000/save-csv-small', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        }).then(response => {
            if (response.ok) {
                alert('success!');
            } else {
                alert('Error saving data!');
            }
        }).catch(err => {
            alert('Error sending CSV data: ' + err); 
            console.error('Error sending CSV data:', err);
        });
    });

    // Đóng popup khi nhấp ra ngoài
    popupOverlay.addEventListener('click', function() {
        popupContainer.style.display = 'none';
        popupOverlay.style.display = 'none';
    });
    cancel.addEventListener('click', function() {
        popupContainer.style.display = 'none';
        popupOverlay.style.display = 'none';
    });
}
