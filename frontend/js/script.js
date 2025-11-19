import { BrowserProvider, parseEther } from "https://cdnjs.cloudflare.com/ajax/libs/ethers/6.7.1/ethers.min.js";


// ===== SMOOTH SCROLLING =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== NAVBAR SCROLL EFFECT =====
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.style.boxShadow = 'none';
    } else {
        navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
    }

    lastScroll = currentScroll;
});

// ===== FORM VALIDATION AND SUBMISSION =====
const form = document.getElementById('nftGiftForm');

// Real-time validation for wallet address
const walletInput = document.getElementById('walletAddress');
walletInput.addEventListener('input', function() {
    const value = this.value;
    const walletPattern = /^0x[a-fA-F0-9]{40}$/;

    if (value && !walletPattern.test(value)) {
        this.style.borderColor = '#ff006e';
    } else {
        this.style.borderColor = 'var(--border-color)';
    }
});

// Real-time validation for email
const emailInput = document.getElementById('email');
emailInput.addEventListener('input', function() {
    const value = this.value;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (value && !emailPattern.test(value)) {
        this.style.borderColor = '#ff006e';
    } else {
        this.style.borderColor = 'var(--border-color)';
    }
});

// Budget validation - price cap should not exceed budget
const budgetInput = document.getElementById('budget');
const priceCapInput = document.getElementById('priceCap');

function validateBudget() {
    const budget = parseFloat(budgetInput.value);
    const priceCap = parseFloat(priceCapInput.value);

    if (budget && priceCap && priceCap > budget) {
        priceCapInput.style.borderColor = '#ff006e';
        showTooltip(priceCapInput, 'Price cap cannot exceed total budget');
    } else {
        priceCapInput.style.borderColor = 'var(--border-color)';
        hideTooltip(priceCapInput);
    }
}

budgetInput.addEventListener('input', validateBudget);
priceCapInput.addEventListener('input', validateBudget);

// Tooltip functions
function showTooltip(element, message) {
    let tooltip = element.parentElement.querySelector('.validation-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('span');
        tooltip.className = 'validation-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            bottom: -25px;
            left: 0;
            color: #ff006e;
            font-size: 0.85rem;
            font-weight: 500;
        `;
        element.parentElement.style.position = 'relative';
        element.parentElement.appendChild(tooltip);
    }
    tooltip.textContent = message;
}

function hideTooltip(element) {
    const tooltip = element.parentElement.querySelector('.validation-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Form submission handler
form.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Validate wallet address
    const walletPattern = /^0x[a-fA-F0-9]{40}$/;
    if (!walletPattern.test(walletInput.value)) {
        alert('Please enter a valid Ethereum wallet address (0x...)');
        walletInput.focus();
        return;
    }

    // Validate budget
    const budget = parseFloat(budgetInput.value);
    const priceCap = parseFloat(priceCapInput.value);

    if (priceCap > budget) {
        alert('Price cap per NFT cannot exceed total budget');
        priceCapInput.focus();
        return;
    }

    // Collect form data
    const formData = collectFormData();

    // Show loading state
    const submitButton = form.querySelector('.submit-button');
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="button-text">Processing...</span> <span class="button-icon">⏳</span>';
    submitButton.disabled = true;

    const ethAmount = Number(formData.budget.totalBudget);
    const recipient = "0xfe1d04eab4c872ead7d778cf7c22ef09fb23f7c6"; // THIS IS MY WALLET. THIS IS NOT FOR PROD THIS IS TEST
    const status = document.getElementById('status');


    // Payment stuff
    // GPTed so hope it works
    if (!window.ethereum) {
        status.innerText = "MetaMask not detected.";
        console.error("MetaMask not detected.");
        return;
    }
    if (!ethAmount || Number(ethAmount) <= 0) {
        status.innerText = "Invalid ETH amount.";
        console.error("Invalid ETH amount.", ethAmount);
        return;
    }

    // covert to string
    const string_ethAmount = String(ethAmount);

    try {
        console.log("2")
        // ⭐ Step 1: Trigger MetaMask payment
        status.innerText = "Waiting for MetaMask…";

        const provider = new BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();

        console.log("About to open MetaMask…");
        const tx = await signer.sendTransaction({
            to: recipient,
            value: parseEther(string_ethAmount)
        });

        status.innerText = "Transaction pending…";

        await tx.wait();  // ⭐ Wait for blockchain confirmation

        status.innerText = "Payment confirmed.";

        // ⭐ Step 2: Now submit form to your backend
        const fullFormData = Object.fromEntries(new FormData(form));

        // Optionally attach TX hash for backend validation
        fullFormData.txHash = tx.hash;

        try {
            // Simulate API call (replace with actual backend endpoint)
            await submitFormData(fullFormData);

            // Show success message
            showSuccessMessage();

            // Reset form
            form.reset();

        } catch (error) {
            // Show error message
            alert('An error occurred while submitting your form. Please try again.');
            console.error('Form submission error:', error);
        } finally {
            // Restore button state
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        }

    } catch (error) {
        // Show error message
        alert('An error occurred while submitting your form. Please try again.');
        console.error('Form submission error:', error);
        // Restore button state
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
    }



});

// Collect all form data
function collectFormData() {
    const formData = {
        personalInfo: {
            fullName: document.getElementById('fullName').value,
            email: document.getElementById('email').value
        },
        walletInfo: {
            walletAddress: document.getElementById('walletAddress').value
        },
        budget: {
            totalBudget: parseFloat(document.getElementById('budget').value),
            maxPricePerNFT: parseFloat(document.getElementById('priceCap').value),
            frequency: document.getElementById('frequency').value,
        },
        preferences: {
            styles: Array.from(document.querySelectorAll('input[name="styles"]:checked')).map(cb => cb.value),
            themes: Array.from(document.querySelectorAll('input[name="themes"]:checked')).map(cb => cb.value),
            additionalPreferences: document.getElementById('preferences').value,
            favoriteArtists: document.getElementById('favoriteArtists').value
        },
        investmentGoals: {
            primaryGoal: document.querySelector('input[name="goal"]:checked')?.value,
            riskTolerance: document.querySelector('input[name="risk"]:checked')?.value
        },
        specialInstructions: document.getElementById('specialInstructions').value,
        timestamp: new Date().toISOString()
    };

    return formData;
}

// Submit form data to backend (placeholder function)
async function submitFormData(data) {
    // Replace this URL with your actual backend endpoint
    const API_ENDPOINT = 'http://localhost:5000/api/form';

    // For demonstration, we'll just log the data and simulate a delay
    console.log('Form Data to Submit:', data);

    // send data to backend
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error('Failed to submit form');
    }

    return await response.json();
    
}

// Show success message
function showSuccessMessage() {
    // Create success modal
    const modal = document.createElement('div');
    modal.className = 'success-modal';
    modal.innerHTML = `
        <div class="success-modal-content">
            <div class="success-icon">✅</div>
            <h2>Gift Box Created Successfully!</h2>
            <p>Thank you for choosing NFT Gift Box. We've received your preferences and our AI is already curating the perfect NFTs for you.</p>
            <p>You'll receive a confirmation email shortly with next steps.</p>
            <button class="close-modal-btn">Continue Exploring</button>
        </div>
    `;

    // Add styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;

    const content = modal.querySelector('.success-modal-content');
    content.style.cssText = `
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 30px;
        padding: 3rem;
        max-width: 500px;
        text-align: center;
        animation: slideUp 0.4s ease;
    `;

    const icon = modal.querySelector('.success-icon');
    icon.style.cssText = `
        font-size: 5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 0 20px var(--accent-blue));
    `;

    const closeBtn = modal.querySelector('.close-modal-btn');
    closeBtn.style.cssText = `
        margin-top: 2rem;
        padding: 1rem 2rem;
        background: var(--gradient-1);
        color: var(--text-primary);
        border: none;
        border-radius: 50px;
        font-family: var(--font-family);
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
    `;

    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    document.body.appendChild(modal);
}

// ===== SCROLL ANIMATIONS =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for scroll animations
document.querySelectorAll('.step, .feature-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ===== FORM PROGRESS INDICATOR =====
const formSections = document.querySelectorAll('.form-section');
let completedSections = 0;

function updateProgress() {
    const requiredInputs = form.querySelectorAll('[required]');
    const filledInputs = Array.from(requiredInputs).filter(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            return document.querySelector(`[name="${input.name}"]:checked`) !== null;
        }
        return input.value.trim() !== '';
    });

    const progress = (filledInputs.length / requiredInputs.length) * 100;
    console.log(`Form Progress: ${Math.round(progress)}%`);
}

// Listen to all form inputs for progress tracking
form.addEventListener('input', updateProgress);
form.addEventListener('change', updateProgress);

// ===== ANALYTICS (PLACEHOLDER) =====
function trackEvent(eventName, data) {
    console.log('Analytics Event:', eventName, data);
    // Integrate with your analytics service (Google Analytics, Mixpanel, etc.)
}

// Track form start
form.addEventListener('focusin', function() {
    trackEvent('form_started', { timestamp: new Date() });
}, { once: true });

// Track section completion
formSections.forEach((section, index) => {
    const inputs = section.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            trackEvent('section_interaction', {
                section: index + 1,
                field: input.name
            });
        });
    });
});

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (document.activeElement.closest('form') === form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
});

// ===== INITIALIZE =====
console.log('🎁 NFT Gift Box initialized');
console.log('Form ready for submissions');

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
