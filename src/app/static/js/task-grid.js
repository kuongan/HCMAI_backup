let videoUrlMap = new Map();

// Tải dữ liệu từ file JSON
async function loadVideoUrls() {
    try {
        const response = await fetch("static/data/url.json");
        if (response.ok) {
            const data = await response.json();
            // Chuyển đổi đối tượng JSON thành đối tượng Map
            videoUrlMap = new Map(Object.entries(data));
        } else {
            console.error('Failed to load video URLs:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching video URLs:', error);
    }
}

// Gọi hàm loadVideoUrls khi trang được tải
document.addEventListener("DOMContentLoaded", loadVideoUrls);

function attachImageGridButtonEvents(imageData) {
    console.log(imageData)
    const blueButtons = document.querySelectorAll('.color-button.blue');
    const yellowButtons = document.querySelectorAll('.color-button.yellow');
    const redButtons = document.querySelectorAll('.color-button.red');
    console.log(blueButtons)
    blueButtons.forEach(function(btn) {
        btn.onclick = function() {
            // Tìm phần tử grid-item chứa nút màu xanh được nhấp
            const gridItem = event.target.closest('.grid-item');
            const frameId = gridItem.getAttribute('data-frame-id');
            const videoId = gridItem.getAttribute('data-video-id');

            // URL của video YouTube bạn muốn mở
            const videoUrl = videoUrlMap.get(videoId);
            const URL = `${videoUrl}&t=${frameId/25}s`

            // Mở cửa sổ mới với kích thước 800x600 và không có thanh công cụ, thanh cuộn
            window.open(URL, "_blank", "width=800,height=600,toolbar=no,scrollbars=no");
        }
    });

    yellowButtons.forEach(function(btn) {
        btn.onclick = function() {
            console.log("Clicked on a yellow button!");
        };
    });

    redButtons.forEach(function(btn) {
        btn.onclick = function() {
            console.log("Clicked on a redButtons button!");
        };
    });
}