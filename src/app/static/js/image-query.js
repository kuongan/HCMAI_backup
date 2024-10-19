import { updateImageGrid, get_url } from './utils.js';

export function handleUpload() {
    const imageUpload = document.getElementById('image-upload'); 
    console.log("Image button clicked")
    imageUpload.addEventListener('change', handleImageUpload)
    imageUpload.click(); // Kích hoạt trình chọn file khi nhấn nút Upload
}

function handleImageUpload(event) {
    const file = event.target.files[0]; // Lấy file đầu tiên
    if (!file) {
        console.error("No file selected."); // Kiểm tra xem có file đã chọn không
        return;
    }

    const model = document.getElementById('model-select').value; //Thêm model
    console.log(file.name, model); // Hiển thị tên file đã chọn trong console
    
    // Tạo FormData để gửi file và model
    const formData = new FormData();
    formData.append('file', file);  // Thêm file vào FormData
    formData.append('model', model);  // Thêm model vào FormData

    // Gọi backend để upload file
    $.ajax({
        url: '/image', // URL của endpoint trên server
        type: 'POST',
        processData: false, // Ngăn jQuery tự động xử lý dữ liệu
        contentType: false, // Đặt content type cho FormData
        data: formData,
        success: function (response) {
            console.log("Image Query:", response);
            if (response.data) {
                const imageUrls = response.data.map(item => ({
                    url: get_url(item.frame_id, item.video_id, item.position),
                    frameId: item.frame_id,
                    videoId: item.video_id,
                }));
                updateImageGrid(imageUrls);
            } else {
                console.error("No data received from the server.");
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Error:', textStatus, errorThrown);
        }
    });
}