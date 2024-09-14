export function handleSubmitButtonClick() {
    const submitButtons = document.querySelectorAll('.submit-button');
    const popupContainer = document.getElementById('popup-container');
    const popupOverlay = document.getElementById('popup-overlay');
    const confirmSubmitButton = popupContainer.querySelector('#confirm-submit');
    let isSubmitEventAttached = false;  // Biến cờ để theo dõi việc gắn sự kiện

    submitButtons.forEach(button => {
        button.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            const frameId = this.getAttribute('data-frame-id');

            // Hiển thị popup và overlay
            popupContainer.style.display = 'block';
            popupOverlay.style.display = 'block';

            // Lấy giá trị từ phần tử filename textarea
            const filenameInput = popupContainer.querySelector('#filename');
            const qaCheckbox = popupContainer.querySelector('#qa-checkbox');
            const qaTextInput = popupContainer.querySelector('#qa-text');
            const qaInputContainer = popupContainer.querySelector('#qa-input-container');

            // Đảm bảo trạng thái ban đầu của qaCheckbox và qaInputContainer
            qaCheckbox.checked = false;
            qaInputContainer.style.display = 'none';
            filenameInput.value = '';  // Reset filename input

            // Sự kiện thay đổi hiển thị QA Text nếu QA checkbox được chọn
            qaCheckbox.addEventListener('change', function () {
                if (this.checked) {
                    qaInputContainer.style.display = 'block';
                } else {
                    qaInputContainer.style.display = 'none';
                }
            });

            // Kiểm tra và chỉ thêm sự kiện submit một lần
            if (!isSubmitEventAttached) {
                confirmSubmitButton.addEventListener('click', handleSubmit);
                isSubmitEventAttached = true;  // Gắn cờ khi sự kiện đã được gắn
            }

            // Hàm xử lý submit
            function handleSubmit() {
                const filename = filenameInput.value.trim();  // Lấy giá trị từ textarea filename
                const isQAEnabled = qaCheckbox.checked;
                const qaText = qaTextInput.value.trim();

                // Kiểm tra điều kiện bắt buộc
                if (!videoId || !frameId || !filename) {
                    alert('Error: Missing required fields (videoId, frameId, filename)');
                    return;
                }

                // Tạo payload dựa trên QA checkbox
                let payload = {
                    videoId: videoId,
                    frameId: frameId,
                    filename: filename  // Đảm bảo filename được lấy từ textarea
                };

                if (isQAEnabled && qaText) {
                    payload.qa = qaText; // Nếu QA được bật, thêm trường QA vào payload
                }
                // Gửi payload dạng JSON
                fetch('http://127.0.0.1:8000/save-csv', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                }).then(response => {
                    if (response.ok) {
                        // Đặt lại form về trạng thái ban đầu
                        filenameInput.value = '';
                        qaCheckbox.checked = false;
                        qaInputContainer.style.display = 'none';  
                        qaTextInput.value = '';  
                        popupContainer.style.display = 'none';
                        popupOverlay.style.display = 'none';
                        
                    } else {
                        alert('Error saving data!');
                    }
                }).catch(err => {
                    alert('Error sending CSV data: ' + err); // Hiển thị alert khi có lỗi
                    console.error('Error sending CSV data:', err);
                });
            }

            // Đóng popup khi nhấp ra ngoài
            popupOverlay.addEventListener('click', function() {
                popupContainer.style.display = 'none';
                popupOverlay.style.display = 'none';
            });
        });
    });
}
