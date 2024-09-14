let currentChain = "";  // Tracks the full chain of selected categories
let currentFocus = -1;  // Tracks the keyboard navigation index

// Handle keyup events (typing and arrow key navigation)
export function handleKeyUp(event) {
    const input = event.target.value;
    const suggestionsDiv = document.getElementById('suggestions');
    // Handle arrow key navigation
    if (event.key === "ArrowDown") {
        currentFocus++;
        addActive(suggestionsDiv);
    } else if (event.key === "ArrowUp") {
        currentFocus--;
        addActive(suggestionsDiv);
    } else if (event.key === "Enter") {
        event.preventDefault();
        if (currentFocus > -1) {
            suggestionsDiv.children[currentFocus].click();
        }
    } else {
        // Handle input change and update currentChain
        const chainParts = input.split(">").map(part => part.trim()).filter(Boolean);
        if (chainParts.length < currentChain.split(">").length) {
            // User has deleted part of the chain
            currentChain = chainParts.join(" > ");
        }

        // Show suggestions based on current input
        showSuggestions(chainParts.pop() || "");
    }
}

// Fetch and display suggestions dynamically based on input
export function showSuggestions(query) {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';  // Clear previous suggestions

    if (query.length === 0) {
        suggestionsDiv.style.display = 'none';
        return;
    }

    fetch(`http://127.0.0.1:8000/suggest?query=${query}&chain=${currentChain}`)
        .then(response => response.json())
        .then(data => {
            suggestionsDiv.innerHTML = '';

            if (data.length === 0) {
                suggestionsDiv.style.display = 'none';
                return;
            }

            data.forEach(result => {
                const suggestion = document.createElement('a');
                suggestion.href = '#';
                suggestion.innerHTML = `${result.DisplayName} (path: ${result.path.trim()})`;
                suggestion.onclick = function() {
                    selectCategory(result.DisplayName, result.path);
                    return false;
                };
                suggestionsDiv.appendChild(suggestion);
            });

            suggestionsDiv.style.display = 'block';
            currentFocus = -1;  // Reset focus for new suggestions
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
            suggestionsDiv.style.display = 'none';
        });
}

// Highlight the currently focused suggestion
function addActive(suggestionsDiv) {
    const items = suggestionsDiv.getElementsByTagName("a");
    if (!items.length) return;

    removeActive(items);

    if (currentFocus >= items.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = items.length - 1;

    items[currentFocus].classList.add("highlight");
}

// Remove the "highlight" class from all items
function removeActive(items) {
    Array.from(items).forEach(item => item.classList.remove("highlight"));
}

// Handle category selection and automatically fetch subcategories
function selectCategory(suggestion, path) {
    const inputField = document.getElementById("object-class");
    currentChain = path.trim() ? path + " > " + suggestion : suggestion;
    inputField.value = currentChain;
    fetchNextSubcategories();
    inputField.focus();
    document.getElementById("suggestions").innerHTML = "";
}

// Fetch the next set of subcategories based on the current chain
async function fetchNextSubcategories() {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';  // Clear previous suggestions

    try {
        const response = await fetch(`http://127.0.0.1:8000/suggest?query=&chain=${currentChain}`);
        const data = await response.json();

        if (data.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }

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

        suggestionsDiv.style.display = 'block';
    } catch (error) {
        console.error('Error fetching subcategories:', error);
        suggestionsDiv.style.display = 'none';
    }
}


// Initialize by showing suggestions for the top-level categories
showSuggestions("");