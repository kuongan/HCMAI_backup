import { updateImageGrid, get_url} from './utils.js'
export function getActiveTaskGridId() {
    const imageGrid = document.getElementById('image-grid');
    const imageGridCluster = document.getElementById('image-grid-cluster');

    if (window.getComputedStyle(imageGrid).display !== 'none') {
        return imageGrid.id;
    } else if (window.getComputedStyle(imageGridCluster).display !== 'none') {
        return imageGridCluster.id;
    }

    return null;
}
// Function to filter images based on start and end date
export function handleDateChange(startDayInput, endDayInput) {
    const startDate = new Date(startDayInput.value);
    const endDate = new Date(endDayInput.value);

    if (startDate && endDate) {
        console.log("Start day:", startDate);
        console.log("End day:", endDate);

        const activeGridId = getActiveTaskGridId();
        if (!activeGridId) {
            console.error("No active task grid found.");
            return;
        }

        // Collect all image elements in the grid
        const taskGrid = document.getElementById(activeGridId);
        if (!taskGrid) {
            console.error("Task grid not found.");
            return;
        }

        console.log("Task grid element:", taskGrid);
        const imageElements = taskGrid.querySelectorAll('.grid-item');
        console.log("Image elements:", imageElements);

        const imageUrls = [];
        // Collect image URLs
        imageElements.forEach(item => {
            const imgElement = item.querySelector('img');
            if (imgElement) {
                const imgUrl = imgElement.src;
                imageUrls.push(imgUrl);
            }
        });

        console.log("Collected image URLs:", imageUrls);

        // Ensure there are images to process
        if (imageUrls.length === 0) {
            console.error("No images found in the grid.");
            return;
        }

        // Call the backend to further process filtered images
        $.ajax({
            url: '/date',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                urls: imageUrls,  // Use 'urls' as expected by FastAPI
                startDate: startDate.toISOString(),
                endDate: endDate.toISOString()
            }),
            success: function (response) {
                console.log("Success:", response);
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
}