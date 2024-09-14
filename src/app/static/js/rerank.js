import { get_url, updateImageGrid } from './utils.js'

export function handleRerankButtonClick() {
    // Lấy tất cả các nút màu vàng đã được check
    const likeButtons = document.querySelectorAll('.color-button.yellow:checked');
    const model = document.getElementById('model-select').value;

    // Tạo mảng chứa URL của các grid-item có nút màu vàng được check
    const checkedImageUrls = [];

    // Duyệt qua tất cả các nút màu vàng đã check
    likeButtons.forEach(function (button) {
        // Lấy phần tử cha gần nhất chứa class 'grid-item' của nút này
        const gridItem = button.closest('.grid-item');

        // Nếu tìm thấy grid-item, lấy URL từ thẻ <img> bên trong
        if (gridItem) {
            const imgElement = gridItem.querySelector('img');
            if (imgElement) {
                checkedImageUrls.push(imgElement.src); // Lấy URL và thêm vào mảng
            }
        }
    });

    // Call the backend to further process filtered images
    $.ajax({
        url: '/rerank',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            urls: checkedImageUrls,  // Use 'urls' as expected by FastAPI
            model: model
        }),
        success: function (response) {
            console.log("Rerank Success:", response);
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