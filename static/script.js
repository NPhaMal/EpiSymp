document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element Selections ---
    const popupOverlay = document.getElementById('popup');
    const wardForm = document.getElementById('ward-data-form');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const searchForm = document.getElementById('search-form');
    const searchResultsContainer = document.getElementById('search-results');
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- State ---
    const API_ENDPOINTS = {
        saveWard: '/save_data',
        getResponse: '/get_response',
        search: '/search'
    };

    // --- Helper Functions ---
    /**
     * Performs an asynchronous POST request.
     * @param {string} url - The URL to send the request to.
     * @param {object} data - The data to send in the request body.
     * @returns {Promise<object>} - The JSON response from the server.
     */
    async function postData(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error in postData to ${url}:`, error);
        }
    }

    /**
     * Performs an asynchronous GET request.
     * @param {string} url - The URL to send the request to.
     * @returns {Promise<object>} - The JSON response from the server.
     */
    async function getData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error in getData from ${url}:`, error);
        }
    }

    /**
     * Appends a message to the chat interface with a typing effect.
     * @param {string} text - The message text.
     * @param {string} type - The message type ('sent' or 'received').
     */
    function appendMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                contentDiv.textContent += text.charAt(i);
                i++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                clearInterval(interval);
            }
        }, 25);
    }

    // --- Event Handlers ---
    /**
     * Handles the submission of the suburb selection form.
     */
    async function handleWardFormSubmit(event) {
        event.preventDefault();
        const ward = document.getElementById('suburb-dropdown').value;
        
        if (ward) {
            const response = await postData(API_ENDPOINTS.saveWard, { ward });
            if (response && response.message) {
                alert(response.message);
            }
            popupOverlay.style.display = 'none';
            appendMessage("Hi, how are you feeling today?", 'received');
        }
    }

    /**
     * Handles sending a user message in the chat.
     */
    async function handleSendMessage() {
        const messageText = userInput.value.trim();
        if (messageText) {
            appendMessage(messageText, 'sent');
            userInput.value = '';
            
            const response = await postData(API_ENDPOINTS.getResponse, { message: messageText });
            if (response && response.message) {
                appendMessage(response.message, 'received');
            }
        }
    }

    /**
     * Handles the disease search form submission.
     */
    async function handleSearchSubmit(event) {
        event.preventDefault();
        const query = document.getElementById('search-input').value;
        if (!query) return;

        const results = await getData(`${API_ENDPOINTS.search}?q=${encodeURIComponent(query)}`);
        displaySearchResults(results);
    }

    /**
     * Displays search results in the Education tab.
     * @param {Array} results - An array of search result objects.
     */
    function displaySearchResults(results) {
        searchResultsContainer.innerHTML = "";
        if (!results || results.length === 0 || results.Severity === 0) {
            searchResultsContainer.innerHTML = "<p>No results found for your search.</p>";
            return;
        }

        results.forEach(result => {
            const resultItem = document.createElement("div");
            resultItem.innerHTML = `
                <h2>${result.Disease}</h2>
                <p>${result.Information}</p>
                <h3>Precautions</h3>
                <p>${result.Precaution}</p>
            `;
            searchResultsContainer.appendChild(resultItem);
        });
    }

    /**
     * Handles tab switching in the navigation.
     */
    function handleTabSwitch(event) {
        event.preventDefault();
        const clickedTab = event.currentTarget;
        
        navLinks.forEach(link => link.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        clickedTab.classList.add('active');
        const tabId = clickedTab.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    }

    // --- Event Listeners ---
    wardForm.addEventListener('submit', handleWardFormSubmit);
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
    searchForm.addEventListener('submit', handleSearchSubmit);
    navLinks.forEach(link => link.addEventListener('click', handleTabSwitch));

    // --- Initializations ---
    // On page load, show the popup.
    popupOverlay.style.display = 'flex';
});