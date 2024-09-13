export function handleSubmitButtonClick() {
    const submitButtons = document.querySelectorAll('.submit-button');

    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const videoId = this.getAttribute('data-video-id');
            const frameId = this.getAttribute('data-frame-id');

            console.log("frameId", frameId);
            console.log("videoId", videoId);

            // Kiểm tra nếu videoId và frameId hợp lệ
            if (!videoId || !frameId) {
                console.error('Error: Missing videoId or frameId');
                return;
            }

            // Tạo payload với JSON
            const payload = {
                videoId: videoId,
                frameId: frameId
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
                    alert('Data added successfully!');
                } else {
                    alert('Error saving data!');
                }
            }).catch(err => console.error('Error sending CSV data:', err));
        });
    });
}
