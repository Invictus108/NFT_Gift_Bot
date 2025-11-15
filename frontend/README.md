# NFT Gift Box - Frontend

A stunning, modern frontend interface for the NFT Gift Box platform. This interface allows users to create personalized NFT gift subscriptions with AI-powered curation.

## Features

- **Dark, Modern Design**: Inspired by premium digital asset platforms with a sleek dark theme
- **Animated Background**: Dynamic gradient spheres that create an immersive experience
- **Comprehensive Form**: Collects user preferences including:
  - Personal information
  - Wallet details
  - Budget and timing preferences
  - Art style and theme preferences
  - Investment goals and risk tolerance
- **Real-time Validation**: Instant feedback on wallet addresses, email, and budget constraints
- **Responsive Design**: Fully optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Scroll animations, hover effects, and transitions
- **Interactive Elements**: Custom checkboxes, radio buttons, and form controls

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # All styling and animations
├── js/
│   └── script.js       # Form validation and interactivity
├── assets/             # Place images and other assets here
└── README.md           # This file
```

## Getting Started

### Option 1: Open Directly
Simply open `index.html` in your web browser to view the page.

### Option 2: Local Server
For the best experience, serve the files using a local server:

```bash
# Using Python 3
cd frontend
python3 -m http.server 8000

# Using Node.js (http-server)
npx http-server frontend -p 8000

# Using PHP
cd frontend
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

## Form Data Structure

When submitted, the form collects data in the following format:

```javascript
{
  personalInfo: {
    fullName: "string",
    email: "string"
  },
  walletInfo: {
    walletAddress: "0x..."
  },
  budget: {
    totalBudget: number,
    maxPricePerNFT: number,
    frequency: "daily|weekly|biweekly|monthly",
    duration: number (months)
  },
  preferences: {
    styles: ["abstract", "pixel", "3d", ...],
    themes: ["nature", "scifi", "fantasy", ...],
    additionalPreferences: "string",
    favoriteArtists: "string"
  },
  investmentGoals: {
    primaryGoal: "collection|investment|both",
    riskTolerance: "conservative|moderate|aggressive"
  },
  specialInstructions: "string",
  timestamp: "ISO string"
}
```

## Backend Integration

To connect this frontend to your backend:

1. Open `js/script.js`
2. Find the `submitFormData()` function
3. Update the `API_ENDPOINT` constant with your backend URL
4. Uncomment the actual fetch implementation

Example:
```javascript
const API_ENDPOINT = 'https://your-backend.com/api/submit-gift-box';
```

## Customization

### Colors
Edit the CSS variables in `css/styles.css`:
```css
:root {
    --primary-bg: #000000;
    --accent-blue: #00d4ff;
    --accent-purple: #b429f9;
    --accent-pink: #ff006e;
    /* ... more variables */
}
```

### Form Fields
Add or remove form fields in `index.html` and update the `collectFormData()` function in `js/script.js`.

### Animations
Modify animation speeds and effects in the CSS file under the animations section.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Design Philosophy

The design follows these principles:
- **Premium Feel**: Dark theme with gradient accents
- **User-Friendly**: Clear labels, helpful hints, and real-time validation
- **Engaging**: Animations and interactions that delight users
- **Trust-Building**: Professional appearance to instill confidence

## Technologies Used

- Pure HTML5, CSS3, and Vanilla JavaScript
- Google Fonts (Inter)
- CSS Grid and Flexbox for layouts
- CSS Custom Properties for theming
- Intersection Observer API for scroll animations

## Future Enhancements

- [ ] Add wallet connection (MetaMask integration)
- [ ] Real-time NFT previews based on preferences
- [ ] Multi-step form wizard
- [ ] Save draft functionality
- [ ] Social media integration
- [ ] Payment integration
- [ ] User dashboard

## License

This frontend is part of the NFT Gift Bot project.

---

**Enjoy building amazing NFT experiences!** 🎁✨
