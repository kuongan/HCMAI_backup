import { updateImageGrid, get_url } from './utils.js';

export async function search() {
    const videoId = document.getElementById('search-video-Id').value.trim();
    const frameId = document.getElementById('search-frame-Id').value.trim();
    
    // Chuyển frameId thành số nguyên nếu có giá trị, hoặc giữ nguyên là null
    const payload = {
        video_id: videoId || null,
        frame_id: frameId ? parseInt(frameId) : null 
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            
            // Tạo các image URLs từ dữ liệu trả về
            const imageUrls = data.map(item => ({
                url: get_url(item.frame_id, item.video_id, item.position),
                frameId: item.frame_id,
                videoId: item.video_id
            }));
            
            // Cập nhật kết quả vào grid
            updateImageGrid(imageUrls);
        } else {
            console.error('Response not OK:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching search results:', error);
    }
}
