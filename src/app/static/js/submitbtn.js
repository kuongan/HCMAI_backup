export function handleSubmitButtonClick() {
    const submitButtons = document.querySelectorAll('.submit-button');
    const popupContainer = document.getElementById('popup-container');
    const popupOverlay = document.getElementById('popup-overlay');
    const confirmSubmitButton = popupContainer.querySelector('#confirm-submit');

    submitButtons.forEach(button => {
        button.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            const frameId = this.getAttribute('data-frame-id');

            // Hiển thị popup và overlay
            popupContainer.style.display = 'block';
            popupOverlay.style.display = 'block';
            document.getElementById('videoId-Submit').textContent = `VideoId: ${videoId}`;
            document.getElementById('frameId-Submit').textContent = `FrameId: ${frameId}`;

            // Lấy giá trị từ phần tử filename textarea
            const qaCheckbox = popupContainer.querySelector('#qa-checkbox');
            const qaTextInput = popupContainer.querySelector('#qa-text');
            const qaInputContainer = popupContainer.querySelector('#qa-input-container');

            // Đảm bảo trạng thái ban đầu của qaCheckbox và qaInputContainer
            qaCheckbox.checked = false;
            qaInputContainer.style.display = 'none';
            
            // Sự kiện thay đổi hiển thị QA Text nếu QA checkbox được chọn
            qaCheckbox.addEventListener('change', function () {
                if (this.checked) {
                    qaInputContainer.style.display = 'block';
                } else {
                    qaInputContainer.style.display = 'none';
                }
                console.log("QA changed!")
            });
            console.log("submit clicked");
            confirmSubmitButton.removeEventListener('click', handleSubmit);

            // Hàm xử lý submit
            function handleSubmit() {
                console.log("handleSubmit")
                const isQAEnabled = qaCheckbox.checked;
                const qaText = qaTextInput.value.trim();

                // Kiểm tra điều kiện bắt buộc
                if (!videoId || !frameId) {
                    alert('Error: Missing required fields (videoId, frameId)');
                    return;
                }

                // Tạo payload dựa trên QA checkbox
                let payload = {
                    videoId: videoId,
                    frameId: frameId,
                    qa: "No-data",
                };

                if (isQAEnabled && qaText) {
                    payload.qa = qaText; // Nếu QA được bật, thêm trường QA vào payload
                }
                // Gửi payload dạng JSON
                fetch('http://127.0.0.1:8000/submit-answer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                }).then(response => {
                    if (response.ok) {
                        console.log("Submission OK!")
                        console.log(response)
                    } else {
                        alert('Error saving data!');
                    }
                }).catch(err => {
                    alert('Error sending CSV data: ' + err); // Hiển thị alert khi có lỗi
                    console.error('Error sending CSV data:', err);
                });
            }
            
            confirmSubmitButton.addEventListener('click', handleSubmit, { once: true });
            // Đóng popup khi nhấp ra ngoài
            popupOverlay.addEventListener('click', function() {
                popupContainer.style.display = 'none';
                popupOverlay.style.display = 'none';
            });
        });
    });
}
