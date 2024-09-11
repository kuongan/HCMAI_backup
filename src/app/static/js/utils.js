import {handleExpandClick} from './expand_btn.js'

export function get_url(frame_id, video_id, position) {
    const name = frame_id + "_" + video_id + "_" + position + ".jpg";
    const video = video_id.split("_")[0];
    const url = "static/image/" + "Videos_" + video + "/" + video_id + "/" + name;
    return url;
}
    
export function updateImageGrid(imageData) {
    const grid = document.getElementById('image-grid');
    const frameIdCheckbox = document.getElementById('frame_id');
    const videoIdCheckbox = document.getElementById('video_id');
    const clusterCheckbox = document.getElementById('cluster');
    grid.innerHTML = ''; 

    imageData.forEach(data => {
        const gridItem = document.createElement('div');
        console.log(data.url);
        gridItem.className = 'grid-item';
        gridItem.innerHTML = `
            <img src="${data.url }" alt="Image" width="100%" height="auto">
            <button class="submit-button">Submit</button>
            <div class="image-overlay">
                <span class="frame-id-label">${data.frameId}</span>
                <span class="video-id-label">${data.videoId}</span>
            </div>
            <div class="color-buttons">
                <input type='checkbox' class="color-button yellow">
                <button class="color-button red"></button>
                <button class="color-button blue"></button>
            </div>
        `;
        grid.appendChild(gridItem);
    });

    const groupedByVideoId = imageData.reduce((acc, item) => {
        if (!acc[item.videoId]) {
            acc[item.videoId] = [];
        }
        acc[item.videoId].push(item);
        return acc;
    }, {});

    const cluster = document.getElementById("image-grid-cluster");
    cluster.innerHTML = ''; 

    // Cập nhật phần tử image-grid-cluster với các nhóm hình ảnh

    for (const videoId in groupedByVideoId) {
        const clusterItems = groupedByVideoId[videoId];
        const clusterGroup = document.createElement('div');
        clusterGroup.className = 'cluster-group';

        clusterItems.forEach(data => {
            const clusterItem = document.createElement('div');
            clusterItem.className = 'cluster-item';
            clusterItem.innerHTML = `
                <img src="${data.url }" alt="Image">
                <button class="submit-button">Submit</button>
                <div class="image-overlay">
                    <span class="frame-id-label">${data.frameId}</span>
                    <span class="video-id-label">${data.videoId}</span>
                </div>
                <div class="color-buttons">
                    <input type='checkbox' class="color-button yellow">
                    <button class="color-button red"></button>
                    <button class="color-button blue"></button>
                </div>
            `;
            clusterGroup.appendChild(clusterItem);
        });

        const groupLabel = document.createElement('h4');
        groupLabel.className = 'video_group';
        groupLabel.textContent = `Video ID: ${videoId}`;
        groupLabel.appendChild(clusterGroup)
        cluster.appendChild(groupLabel);
    }
    updateImageOverlay(frameIdCheckbox.checked, videoIdCheckbox.checked, clusterCheckbox.checked)
    handleExpandClick();
}

export function updateImageOverlay(frameIdChecked, videoIdChecked, clusterChecked) {
    const grid = document.getElementById('image-grid');
    const cluster = document.getElementById('image-grid-cluster');
    
    const gridItems = document.querySelectorAll('.grid-item');
    const clusterItems = document.querySelectorAll('.cluster-item');

    // Update grid item overlays
    gridItems.forEach(gridItem => {
        const frameIdLabel = gridItem.querySelector('.frame-id-label');
        const videoIdLabel = gridItem.querySelector('.video-id-label');
        
        frameIdLabel.style.display = frameIdChecked ? 'block' : 'none';
        videoIdLabel.style.display = videoIdChecked ? 'block' : 'none';
    });

    clusterItems.forEach(gridItem => {
        const frameIdLabel = gridItem.querySelector('.frame-id-label');
        const videoIdLabel = gridItem.querySelector('.video-id-label');
        
        frameIdLabel.style.display = frameIdChecked ? 'block' : 'none';
        videoIdLabel.style.display = videoIdChecked ? 'block' : 'none';
    });

    // Show/hide grid and cluster items
    if (clusterChecked) {
        grid.style.display = 'none';
        cluster.style.display = 'grid'; // Ensure the cluster is displayed as grid
    } else {
        grid.style.display = 'grid'; // Ensure the grid is displayed as grid
        cluster.style.display = 'none';
    }
}
