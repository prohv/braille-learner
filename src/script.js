const BRAILLE_MAP = {
    'a': [1, 0, 0, 0, 0, 0], 'b': [1, 1, 0, 0, 0, 0], 'c': [1, 0, 0, 1, 0, 0],
    'd': [1, 0, 0, 1, 1, 0], 'e': [1, 0, 0, 0, 1, 0], 'f': [1, 1, 0, 1, 0, 0],
    'g': [1, 1, 0, 1, 1, 0], 'h': [1, 1, 0, 0, 1, 0], 'i': [0, 1, 0, 1, 0, 0],
    'j': [0, 1, 0, 1, 1, 0], 'k': [1, 0, 1, 0, 0, 0], 'l': [1, 1, 1, 0, 0, 0],
    'm': [1, 0, 1, 1, 0, 0], 'n': [1, 0, 1, 1, 1, 0], 'o': [1, 0, 1, 0, 1, 0],
    'p': [1, 1, 1, 1, 0, 0], 'q': [1, 1, 1, 1, 1, 0], 'r': [1, 1, 1, 0, 1, 0],
    's': [0, 1, 1, 1, 0, 0], 't': [0, 1, 1, 1, 1, 0], 'u': [1, 0, 1, 0, 0, 1],
    'v': [1, 1, 1, 0, 0, 1], 'w': [0, 1, 0, 1, 1, 1], 'x': [1, 0, 1, 1, 0, 1],
    'y': [1, 0, 1, 1, 1, 1], 'z': [1, 0, 1, 0, 1, 1]
};

const dots = {
    1: document.getElementById('dot-1'),
    2: document.getElementById('dot-2'),
    3: document.getElementById('dot-3'),
    4: document.getElementById('dot-4'),
    5: document.getElementById('dot-5'),
    6: document.getElementById('dot-6')
};

const currentLetter = document.getElementById('current-letter');
const speechLog = document.getElementById('speech-log');
const historyList = document.getElementById('history-list');
const statusTag = document.getElementById('status-tag');
const testBtn = document.getElementById('test-btn');
const testInput = document.getElementById('test-letter');

testBtn.onclick = () => {
    const char = testInput.value.toLowerCase();
    if (BRAILLE_MAP[char]) {
        updateDisplay(char, BRAILLE_MAP[char]);
        addToHistory(char);
        testInput.value = '';

        // Auto reset after 3 seconds for manual input too
        setTimeout(resetDots, 3000);
    }
};

testInput.onkeyup = (e) => {
    if (e.key === 'Enter') testBtn.click();
};

function connect() {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        console.log('Connected to simulation backend');
        statusTag.textContent = 'SYSTEM ACTIVE';
        statusTag.className = 'status-tag active';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);

        switch (data.type) {
            case 'letter':
                updateDisplay(data.letter, data.pattern);
                addToHistory(data.letter);
                break;
            case 'recognition':
                speechLog.textContent = data.text;
                break;
            case 'status':
                updateStatus(data.value);
                break;
            case 'reset':
                resetDots();
                break;
        }
    };

    ws.onclose = () => {
        console.log('Disconnected. Retrying...');
        statusTag.textContent = 'DISCONNECTED';
        statusTag.className = 'status-tag';
        setTimeout(connect, 2000);
    };
}

function updateDisplay(letter, pattern) {
    currentLetter.textContent = letter.toUpperCase();

    pattern.forEach((isRaised, index) => {
        const dotNum = index + 1;
        if (isRaised) {
            dots[dotNum].classList.add('raised');
        } else {
            dots[dotNum].classList.remove('raised');
        }
    });

    speechLog.textContent = `Displaying Letter ${letter.toUpperCase()}...`;
}

function resetDots() {
    Object.values(dots).forEach(dot => dot.classList.remove('raised'));
    currentLetter.textContent = '-';
    speechLog.textContent = 'Ready to hear...';
}

function updateStatus(status) {
    if (status === 'LISTENING') {
        speechLog.textContent = 'Listening...';
        speechLog.style.color = 'black';
    } else if (status === 'THINKING') {
        speechLog.textContent = 'Processing...';
        speechLog.style.color = '#555';
    }
}

function addToHistory(letter) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.textContent = letter.toUpperCase();

    // Insert at beginning
    if (historyList.firstChild) {
        historyList.insertBefore(item, historyList.firstChild);
    } else {
        historyList.appendChild(item);
    }

    // Limit to 10 items
    if (historyList.children.length > 15) {
        historyList.removeChild(historyList.lastChild);
    }
}

// Initial connection
connect();
