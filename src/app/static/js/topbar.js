function search(ele) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission
        const text = ele.value; 

        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }) // Wrap text in an object with a key
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Assuming 'data.url' contains the URL to the image
            updateImageGrid([data.url]); // Update the image grid with the URL
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

function updateImageGrid(imageUrls) {
    const grid = document.getElementById('image-grid');
    grid.innerHTML = ''; // Clear previous content

    imageUrls.forEach(url => {
        const gridItem = document.createElement('div');
        gridItem.className = 'grid-item';
        gridItem.innerHTML = `
            <img src="${url}" alt="Image" width="256" height="144">
            <button class="submit-button">Submit</button>
            <div class="color-buttons">
                <button class="color-button yellow"></button>
                <button class="color-button red"></button>
                <button class="color-button blue"></button>
            </div>
        `;
        grid.appendChild(gridItem);
    });
}