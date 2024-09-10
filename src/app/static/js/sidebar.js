// Sidebar.js
import {handleDateChange} from './date.js'
import {updateImageOverlay, updateImageGrid, get_url} from './utils.js'
document.addEventListener("DOMContentLoaded", function() {
    const enterButton = document.getElementById('enter-btn');
    const frameIdCheckbox = document.getElementById('frame_id');
    const videoIdCheckbox = document.getElementById('video_id');
    const clusterCheckbox = document.getElementById('cluster');
    const startDayInput = document.getElementById('min');
    const endDayInput = document.getElementById('max');
    // Get the initial states of the checkboxes
    const frameIdChecked = frameIdCheckbox.checked;
    const videoIdChecked = videoIdCheckbox.checked;
    const clusterChecked = clusterCheckbox.checked;
    enterButton.addEventListener('click', async function() {
        const model = document.getElementById('model-select').value;
        const textQuery = document.getElementById('text-query').value;

        const payload = {
            model: model.toString(),
            textQuery: textQuery.toString(),
        };

        try {
            const response = await fetch('/side-bar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                const imageUrls = data.data.map(item => ({
                    url: get_url(item.frame_id, item.video_id, item.position),
                    frameId: item.frame_id,
                    videoId: item.video_id
                }));
                updateImageGrid(imageUrls);
            } else {
                console.error('Response not OK:', response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Add event listeners to the date inputs
    startDayInput.addEventListener('change', () => handleDateChange(startDayInput, endDayInput));
    endDayInput.addEventListener('change', () => handleDateChange(startDayInput, endDayInput));

    // Attach event listeners to the checkboxes to trigger updateImageOverlay when they change
    frameIdCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });
    videoIdCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });
    clusterCheckbox.addEventListener('change', () => {
        updateImageOverlay(
            frameIdCheckbox.checked,
            videoIdCheckbox.checked,
            clusterCheckbox.checked
        );
    });

    //color.js
    $(function() {
        
        let zIndexCounter = 1;

        // Draw the grid on canvas
        function drawGrid(gridWidth, gridHeight) {
            const canvasWidth = $('#canvasContainer').width();
            const canvasHeight = $('#canvasContainer').height();
            console.log("Drawing grid...");

            for (let x = gridWidth; x < canvasWidth; x += gridWidth) {
                const verticalLine = $('<div class="grid-line vertical-line"></div>').css({
                    height: canvasHeight + 'px',
                    left: x + 'px'
                });
                $('#canvasContainer').append(verticalLine);
            }

            for (let y = gridHeight; y < canvasHeight; y += gridHeight) {
                const horizontalLine = $('<div class="grid-line horizontal-line"></div>').css({
                    width: canvasWidth + 'px',
                    top: y + 'px'
                });
                $('#canvasContainer').append(horizontalLine);
            }
        }

        // Draw grid on load
        drawGrid(252 / 7, 154 / 7);  // Draw a 7x7 grid

        // Make palette items draggable
        $(".palette div").draggable({
            helper: "clone",
            containment: "body",
        });

        // Allow canvas container to accept droppable items
        $("#canvasContainer").droppable({
            accept: ".palette div",
            drop: function(event, ui) {
                console.log("Box dropped");
                const color = $(ui.helper).data("color");

                const canvasOffset = $(this).offset();
                const dropX = ui.offset.left - canvasOffset.left;
                const dropY = ui.offset.top - canvasOffset.top;

                const newBox = $('<div class="draggable-box"></div>').css({
                    width: "50px",
                    height: "50px",
                    backgroundColor: color,
                    top: Math.max(0, Math.min(dropY, $(this).height() - 60)),
                    left: Math.max(0, Math.min(dropX, $(this).width() - 60)),
                    zIndex: zIndexCounter++
                }).text(color.toUpperCase());

                newBox.draggable({
                    containment: "#canvasContainer",
                    start: function() {
                        $(this).css("z-index", zIndexCounter++);
                    }
                }).resizable({
                    containment: "#canvasContainer",
                    minWidth: 10,
                    minHeight: 10,
                    maxWidth: $("#canvasContainer").width(),
                    maxHeight: $("#canvasContainer").height()
                });

                $(this).append(newBox);
                console.log(`Box created with color: ${color}`);
            }
        });
        // Function to send all box details to the backend for encoding
        function sendAllBoxesToBackend() {
            const boxDetails = [];
            $(".draggable-box").each(function() {
                const box = $(this);
                const x = parseInt(box.css('left'), 10);
                const y = parseInt(box.css('top'), 10);
                const width = box.width();
                const height = box.height();
                const color = box.css('backgroundColor');

                console.log(`Collecting box data: Color: ${color}, X: ${x}, Y: ${y}, Width: ${width}, Height: ${height}`);

                const gridHeight = 154 / 7;
                const gridWidth = 252 / 7;

                const rowsCovered = Math.ceil(height / gridHeight);
                const colsCovered = Math.ceil(width / gridWidth);

                const startRow = Math.max(0, Math.floor(y / gridHeight));
                const startCol = String.fromCharCode(97 + Math.max(0, Math.floor(x / gridWidth)));

                boxDetails.push({
                    row: startRow,
                    col: startCol,
                    rows_covered: rowsCovered,
                    cols_covered: colsCovered,
                    color: color
                });
            });

            // Send box details to backend
            console.log("Sending box details to backend:", boxDetails);
            $.ajax({
                url: 'http://127.0.0.1:8000/encode_box/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(boxDetails),
                success: function(response) {
                    console.log("Search Results:", response.data);

                    // Assuming response.data contains the image information
                    const imageUrls = response.data.map(item => ({
                        url: get_url(item.frame_id, item.video_id, item.position),
                        frameId: item.frame_id,
                        videoId: item.video_id
                    }));
                    
                    // Call updateImageGrid function from sidebar.js
                    updateImageGrid(imageUrls);
                },
                error: function(err) {
                    console.error("Error:", err);
                }
            });
        }
        // Send boxes to backend when Enter is pressed
        $(document).keypress(function(e) {
            if (e.which === 13) {  // Enter key code
                console.log("Enter pressed");
        
                // Check if there are any draggable boxes on the canvas
                if ($(".draggable-box").length > 0) {
                    console.log("Boxes found, sending box details to backend");
                    sendAllBoxesToBackend();
                } else {
                    console.log("No boxes found on the canvas");
                }
            }
        });
        // Clear the canvas
        $("#trashIcon").click(function() {
            console.log("Clearing the canvas");
            $("#canvasContainer").empty();
            drawGrid(252 / 7, 154 / 7);
        });
    });
    // Initial call to update overlay based on initial checkbox states
    updateImageOverlay(frameIdChecked, videoIdChecked, clusterChecked);
});

