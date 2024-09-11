let currentChain = "";  // This tracks the full chain of selected categories
let currentFocus = -1;  // This keeps track of the keyboard navigation index

// Function to handle keyup events (typing and arrow key navigation)
function handleKeyUp(event) {
    const input = event.target.value;
    const suggestionsDiv = document.getElementById('suggestions');

    // Handle arrow key navigation
    if (event.key === "ArrowDown") {
        currentFocus++;
        addActive(suggestionsDiv);
        return;
    } else if (event.key === "ArrowUp") {
        currentFocus--;
        addActive(suggestionsDiv);
        return;
    } else if (event.key === "Enter") {
        event.preventDefault();
        if (currentFocus > -1) {
            suggestionsDiv.children[currentFocus].click();
        }
        return;
    }

    // Handle deleting parts of the chain
    const chainParts = input.split(">").map(part => part.trim()).filter(Boolean);
    if (chainParts.length < currentChain.split(">").length) {
        // User has deleted part of the chain, update currentChain
        currentChain = chainParts.join(" > ");
    }

    // Show suggestions based on current input
    showSuggestions(chainParts.pop() || "");
}

// Function to fetch and display suggestions dynamically based on input
function showSuggestions(query) {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';  // Clear previous suggestions

    // Don't show suggestions if the query is empty
    if (query.length === 0) {
        suggestionsDiv.style.display = 'none';
        return;
    }

    // Fetch suggestions from FastAPI server based on current input and chain
    fetch(`http://127.0.0.1:8000/suggest?query=${query}&chain=${currentChain}`)
        .then(response => response.json())
        .then(data => {
            // Clear existing suggestions
            suggestionsDiv.innerHTML = '';

            // If no suggestions, hide the dropdown
            if (data.length === 0) {
                suggestionsDiv.style.display = 'none';
                return;
            }

            // Add each suggestion to the dropdown
            data.forEach(result => {
                const suggestion = document.createElement('a');
                suggestion.href = '#';
                suggestion.innerHTML = `${result.DisplayName} (path: ${result.path.trim()})`; // Fix display of the path
                suggestion.onclick = function() {
                    selectCategory(result.DisplayName, result.path);
                    return false;
                };
                suggestionsDiv.appendChild(suggestion);
            });

            // Show the dropdown if suggestions are available
            suggestionsDiv.style.display = 'block';
            currentFocus = -1;  // Reset focus for new suggestions
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
            suggestionsDiv.style.display = 'none';  // Hide on error
        });
}

// Function to add highlight to the currently focused suggestion
function addActive(suggestionsDiv) {
    const items = suggestionsDiv.getElementsByTagName("a");
    if (!items) return false;

    // Remove the "active" class from all items
    removeActive(items);

    // Loop back if out of bounds
    if (currentFocus >= items.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = items.length - 1;

    // Add the "active" class to the current item
    items[currentFocus].classList.add("highlight");
}

// Remove the active class from all suggestion items
function removeActive(items) {
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove("highlight");
    }
}

// Function to handle category selection and automatically fetch subcategories
function selectCategory(suggestion, path) {
    const inputField = document.getElementById("object-class");

    // Update the current chain of selected categories
    currentChain = path.trim() ? path + " > " + suggestion : suggestion;
    inputField.value = currentChain;

    // Automatically fetch subcategories for the new selection
    fetchNextSubcategories();

    inputField.focus();  // Refocus on the input field for the next input

    // Clear suggestions
    document.getElementById("suggestions").innerHTML = "";
}

// Function to automatically fetch the next set of subcategories based on the current chain
async function fetchNextSubcategories() {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';  // Clear previous suggestions

    // Fetch subcategories from the backend for the current chain
    const response = await fetch(`http://127.0.0.1:8000/suggest?query=&chain=${currentChain}`);
    const data = await response.json();

    // Clear existing suggestions
    suggestionsDiv.innerHTML = '';

    // If no suggestions (no further subcategories), hide the dropdown
    if (data.length === 0) {
        suggestionsDiv.style.display = 'none';
        return;  // No more subcategories
    }

    // Display the next set of subcategories in the dropdown
    data.forEach(result => {
        const suggestion = document.createElement('a');
        suggestion.href = '#';
        suggestion.innerHTML = result.DisplayName;
        suggestion.onclick = function() {
            selectCategory(result.DisplayName, currentChain);
            return false;
        };
        suggestionsDiv.appendChild(suggestion);
    });

    // Show the dropdown with the subcategories
    suggestionsDiv.style.display = 'block';
}

// Initialize by showing suggestions for the top-level categories
showSuggestions("");