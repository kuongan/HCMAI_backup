// Hàm mở popup
function openPopup() {
    document.getElementById('popup').style.display = 'flex';
}

// Hàm đóng popup và xóa input
function closePopup() {
    document.getElementById('popup').style.display = 'none';

    // Clear các giá trị trong input khi popup đóng
    document.getElementById('minutes').value = '';
    document.getElementById('seconds').value = '';
    document.getElementById('videoId').textContent = '';
    document.getElementById('frameId').textContent = '';
}

// Đóng popup khi bấm vào nút close
document.querySelector('.close').onclick = function() {
    closePopup();
};

// Đóng popup khi bấm ra ngoài popup
window.onclick = function(event) {
    if (event.target === document.getElementById('popup')) {
        closePopup();
    }
};

// Convert time to frame ID
document.getElementById('convertBtn').onclick = function() {
    const minutes = parseInt(document.getElementById('minutes').value) || 0;
    const seconds = parseInt(document.getElementById('seconds').value) || 0;

    // Tính tổng thời gian bằng cách chuyển phút sang giây và cộng với số giây nhập vào
    const totalTimeInSeconds = (minutes * 60) + seconds;

    // Giả sử tốc độ khung hình là 25 khung hình trên giây
    const frameId = Math.floor(totalTimeInSeconds * 25);

    // Hiển thị kết quả
    document.getElementById('frameId').textContent = `FrameId: ${frameId}`;
};
