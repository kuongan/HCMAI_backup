export function handleExpandClick() {
    const redButtons = document.querySelectorAll('.color-button.red');
    redButtons.forEach(function(btn) {
        btn.onclick = function () {
            // Lấy phần tử cha gần nhất của nút này là '.grid-item' hoặc '.cluster-item'
            const item = btn.closest('.grid-item') || btn.closest('.cluster-item');
            // Tìm uri của ảnh trong item
            const imgURI = item.querySelector('img').src;
            console.log(imgURI)

            // gọi BE để tìm videoURL và frameID từ imageURI
            $.ajax({
                url: 'http://127.0.0.1:8000/expandBtn/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    url: imgURI, 
                }),
                success: function (response) {
                    console.log("Success:", response);
                    if (response.frameId) {
                        // Kết hợp videoURL với frameId để đến đúng frame hiện tại trong video
                        const URL = `${response.videoURL}&t=${response.frameId / 25}s`
                        // Mở cửa sổ mới với kích thước 800x600 và không có thanh công cụ, thanh cuộn
                        window.open(URL, "_blank", "width=800,height=600,toolbar=no,scrollbars=no");

                        document.getElementById('popup').style.display = 'flex';
                        document.getElementById('videoId').textContent = `VideoId: ${response.videoId}`;

                    } else {
                        console.error("No data received from the server.");
                    }
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error('Error:', textStatus, errorThrown);
                }
            });
        }

        
    });
}