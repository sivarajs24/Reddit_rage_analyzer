document.addEventListener('DOMContentLoaded', () => {
    triggerEntranceAnimations();

    const analysisForm = document.getElementById('analysis-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const analyzeBtn = document.getElementById('analyze-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');

    let currentProduct = "";

    // ───────────────────────────────────
    // Focus Mode Logic
    // ───────────────────────────────────
    const focusMode = document.getElementById('focus-mode');
    const customFocusGroup = document.getElementById('custom-focus-group');
    
    focusMode.addEventListener('change', (e) => {
        if (e.target.value === 'custom') {
            customFocusGroup.classList.remove('hidden');
        } else {
            customFocusGroup.classList.add('hidden');
        }
    });

    // ───────────────────────────────────
    // Analysis Form
    // ───────────────────────────────────
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const product = document.getElementById('product').value.trim();
        const subreddits = document.getElementById('subreddits').value.trim();
        
        let focus = '';
        if (focusMode.value === 'negative') {
            focus = 'major issues bugs hate worst features';
        } else if (focusMode.value === 'positive') {
            focus = 'positive feedback praise love best features';
        } else if (focusMode.value === 'general') {
            focus = 'opinions feedback review good bad';
        } else if (focusMode.value === 'custom') {
            focus = document.getElementById('focus').value.trim();
        }
        
        if (!product) return;
        currentProduct = product;

        // UI State: Loading
        analyzeBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    product_name: product, 
                    custom_subreddits: subreddits,
                    focus: focus
                })
            });
            if (!res.ok) throw new Error("Analysis failed.");
            const data = await res.json();

            setTimeout(() => {
                loadingIndicator.classList.add('hidden');
                analyzeBtn.disabled = false;
                renderResults(data);
            }, 500);
        } catch (error) {
            console.error(error);
            alert("Error running analysis. Check console.");
            loadingIndicator.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    // ───────────────────────────────────
    // Render Results
    // ───────────────────────────────────
    function renderResults(data) {
        const analysis = data.analysis_result;
        const docs = data.retrieved_docs;

        // Metrics
        document.getElementById('metric-sentiment').innerText = analysis.overall_sentiment || "N/A";
        document.getElementById('metric-intensity').innerText = analysis.emotional_intensity || "N/A";
        animateValue("metric-count", 0, docs.length, 1200);

        // Summary (Typewriter)
        const summaryText = analysis.summary_paragraph || "No summary available.";
        typeWriter("ai-summary", summaryText, 15);

        // Keywords
        const keywordsList = document.getElementById('keywords-list');
        keywordsList.innerHTML = '';
        if (analysis.top_keywords && analysis.top_keywords.length > 0) {
            analysis.top_keywords.forEach((kw, i) => {
                const span = document.createElement('span');
                span.className = 'tag';
                span.innerText = kw;
                span.style.opacity = '0';
                span.style.transform = 'translateY(8px)';
                span.style.transition = `all 0.4s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.06}s`;
                keywordsList.appendChild(span);
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        span.style.opacity = '1';
                        span.style.transform = 'translateY(0)';
                    });
                });
            });
        } else {
            keywordsList.innerHTML = '<p class="placeholder-text">No keywords found.</p>';
        }

        // Hated Features
        const hatedList = document.getElementById('hated-features');
        hatedList.innerHTML = '';
        if (analysis.most_hated_features && analysis.most_hated_features.length > 0) {
            analysis.most_hated_features.forEach(f => {
                const li = document.createElement('li');
                li.innerText = f;
                hatedList.appendChild(li);
            });
        } else {
            hatedList.innerHTML = '<li class="placeholder-text">Nothing found</li>';
        }

        // Common Bugs
        const bugsList = document.getElementById('common-bugs');
        bugsList.innerHTML = '';
        if (analysis.common_bug_patterns && analysis.common_bug_patterns.length > 0) {
            analysis.common_bug_patterns.forEach(b => {
                const li = document.createElement('li');
                li.innerText = b;
                bugsList.appendChild(li);
            });
        } else {
            bugsList.innerHTML = '<li class="placeholder-text">Nothing found</li>';
        }

        // Reset chat
        chatHistory.innerHTML = `<div class="sys-msg">Analysis complete for ${currentProduct}. Ask me anything about the results!</div>`;
    }

    // ───────────────────────────────────
    // Chat
    // ───────────────────────────────────
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg || !currentProduct) return;
        chatInput.value = '';

        const userDiv = document.createElement('div');
        userDiv.className = 'msg-user';
        userDiv.innerText = msg;
        chatHistory.appendChild(userDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_name: currentProduct, prompt: msg })
            });
            if (!res.ok) throw new Error("Chat failed.");
            const data = await res.json();

            const aiDiv = document.createElement('div');
            aiDiv.className = 'msg-ai';
            chatHistory.appendChild(aiDiv);

            // Typewriter for chat response
            let i = 0;
            const chatText = data.response;
            function typeChat() {
                if (i < chatText.length) {
                    aiDiv.innerHTML += chatText.charAt(i);
                    i++;
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                    setTimeout(typeChat, 8);
                }
            }
            typeChat();
        } catch (error) {
            const errDiv = document.createElement('div');
            errDiv.className = 'sys-msg';
            errDiv.innerText = 'Something went wrong. Please try again.';
            chatHistory.appendChild(errDiv);
        }
    });

    // ───────────────────────────────────
    // Animations
    // ───────────────────────────────────
    function triggerEntranceAnimations() {
        const cards = document.querySelectorAll('.glass-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animate-in');
            }, 150 + index * 120);
        });
    }

    function animateValue(id, start, end, duration) {
        if (start === end) return;
        const obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function typeWriter(id, text, speed) {
        const el = document.getElementById(id);
        el.innerHTML = '<p></p>';
        const p = el.querySelector('p');
        p.className = 'summary-text';
        let i = 0;
        function type() {
            if (i < text.length) {
                p.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                // Add blinking cursor at end
                p.innerHTML += '<span class="footer-blink" style="color: var(--neon-cyan);">_</span>';
            }
        }
        type();
    }
});
