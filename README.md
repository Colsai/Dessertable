# DessertAble 🍰

**Find the best dessert spots near you with ease.**

DessertAble is a simple, elegant web application that helps you discover top-rated dessert restaurants, bakeries, ice cream shops, and sweet treat locations in your area. Just enter your address, and we'll show you the top 3 dessert destinations nearby with ratings, reviews, and directions.

![GitHub repo size](https://img.shields.io/github/repo-size/Colsai/DessertAble)
![GitHub license](https://img.shields.io/github/license/Colsai/DessertAble)

---

## What Does It Do?

DessertAble takes the stress out of finding great desserts. Instead of scrolling through endless restaurant listings, you get:

- **Top 3 Results Only**: We show you the best 3 dessert spots based on ratings and reviews
- **Location-Based Search**: Enter any US address or zip code
- **Rich Details**: See ratings, addresses, hours, and popular menu items
- **Search History**: All your searches are saved locally for quick reference
- **One-Click Access**: Direct links to Google Maps and restaurant websites

Perfect for when you're craving something sweet and don't want to spend time researching!

---

## Quick Start

### Windows
1. Download or clone this repository
2. Double-click `START_APP.bat`
3. Follow the on-screen instructions to set up your API key
4. Click "Start Server" and search for desserts!

### Mac/Linux
1. Download or clone this repository
2. Open Terminal and run: `./START_APP.sh`
3. Follow the on-screen instructions to set up your API key
4. Click "Start Server" and search for desserts!

**That's it!** The application will open automatically in your browser.

---

## Features

### 🔍 Smart Search
- Enter any US address or zip code
- Automatically finds dessert-focused businesses nearby (bakeries, ice cream shops, dessert cafes, etc.)
- Shows only the **top 3** results to reduce decision fatigue

### 📊 Detailed Information
Each result includes:
- ⭐ Google ratings and review counts
- 📍 Full address with distance from your location
- 🚗 Estimated driving time
- 🕐 Operating hours and open/closed status
- 🍰 Popular menu items extracted from customer reviews
- 🔗 Direct links to Google Maps and restaurant websites

### 📚 Search History
- All searches automatically saved to a local database
- View past search results instantly without using the API again
- See statistics: total searches, restaurants found, and more
- Access your history anytime through the "History" tab

### 🖥️ Easy-to-Use Launcher
- Simple desktop application to start/stop the server
- No command line knowledge needed
- Visual API key setup
- Real-time server status and logs

---

## Screenshots

### Search Page
The main search interface where you enter your location:

![Search Interface](assets/screenshot-search.png)

### Results Page
Top 3 dessert spots with all the details you need:

![Results Display](assets/screenshot-results.png)

### History Page
Quickly access your previous searches:

![Search History](assets/screenshot-history.png)

---

## Requirements

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **Google Places API Key** (Free tier includes $200/month credit)
  - [Get your API key here](https://console.cloud.google.com/)
  - Enable: Geocoding API and Places API
  - See [setup guide](USER_GUIDE.md) for detailed instructions

---

## How to Get a Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable these APIs:
   - **Geocoding API**
   - **Places API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy your API key
6. When you first run the app, paste your API key into the launcher

**Note:** Google provides $200 in free monthly credits. For typical personal use, you won't exceed this limit.

---

## Installation (For Developers)

If you prefer to set things up manually:

```bash
# Clone the repository
git clone https://github.com/Colsai/DessertAble.git
cd DessertAble

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_PLACES_API_KEY

# Run the application
python run.py
```

Visit http://localhost:5000 in your browser.

---

## Usage Tips

1. **Be Specific**: Use full addresses for best results (e.g., "123 Main St, New York, NY" instead of just "New York")
2. **Try Nearby Areas**: If you don't find what you want, try a nearby zip code or neighborhood
3. **Check History**: Before searching again, check your history tab - you might have already searched that area!
4. **Popular Items**: The "Popular Menu Items" are extracted from real customer reviews, so they're great recommendations

---

## Technology Stack

Built with modern, reliable technologies:

- **Backend**: Python + Flask
- **Database**: SQLite (local, no setup needed)
- **API**: Google Places API
- **Frontend**: Bootstrap 5 (responsive design)
- **Launcher**: Tkinter (built-in with Python)

---

## Project Structure

```
DessertAble/
├── app/                    # Main application code
│   ├── routes.py          # Web routes and logic
│   ├── models/            # Database models
│   ├── services/          # API integration
│   └── templates/         # HTML pages
├── data/                  # SQLite database (auto-created)
├── launcher.py            # GUI launcher
├── START_APP.bat          # Windows startup script
├── START_APP.sh           # Mac/Linux startup script
└── requirements.txt       # Python dependencies
```

---

## Version History

### Version 1.1.0 (2026-01-05)
- Rebranded from "Restaurant Finder" to "DessertAble"
- Simplified to focus exclusively on dessert establishments
- Streamlined UI for faster, easier searches
- Added comprehensive search history feature
- Implemented Top 3 results display to reduce decision fatigue
- Updated all documentation and branding

### Version 1.0.0 (2025-12-29)
- Initial release as "Restaurant Finder"
- Core search functionality with Google Places API
- Basic filtering and sorting (backend implementation)
- Search history database
- GUI launcher for easy startup
- Bootstrap 5 responsive design

---

## Troubleshooting

### App won't start
- Make sure Python 3.8+ is installed: `python --version`
- Try running `TROUBLESHOOT.bat` (Windows) for automated diagnostics
- Check that your API key is correctly set in the `.env` file

### "API key not configured" error
1. Make sure you created a `.env` file (copy from `.env.example`)
2. Verify your API key is pasted correctly (no extra spaces)
3. Restart the launcher after adding the API key

### No results found
- Double-check your address is in the United States
- Try a more specific address (include street, city, state)
- Make sure your Google API key has the Geocoding and Places APIs enabled

### Port 5000 already in use
- Another application might be using port 5000
- Close any other Flask apps or web servers
- Or edit `run.py` to use a different port

For more help, see the [User Guide](USER_GUIDE.md) or open an issue on GitHub.

---

## FAQ

**Q: Is this free to use?**
A: Yes! The app is free and open source. Google Places API includes $200/month in free credits, which is plenty for personal use.

**Q: Does it work outside the US?**
A: Currently, the app is optimized for US addresses. International support may be added in future versions.

**Q: Why only 3 results?**
A: Research shows that too many choices can be overwhelming. We show you the top 3 to make decision-making easier and faster.

**Q: Can I change the search radius?**
A: Yes! Developers can edit `config.py` and change `DEFAULT_SEARCH_RADIUS` (default is 5000 meters / ~3 miles).

**Q: Is my search data private?**
A: Yes! All searches are stored locally on your computer in a SQLite database. Nothing is sent to external servers except the Google Places API queries.

---

## Contributing

We welcome contributions! If you'd like to improve DessertAble:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Powered by [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with [Bootstrap 5](https://getbootstrap.com/)
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/)

---

## Support

Having issues? Need help?

- 📖 Check the [User Guide](USER_GUIDE.md) for detailed instructions
- 🐛 [Open an issue](https://github.com/Colsai/DessertAble/issues) on GitHub
- 💡 Have a feature idea? Let us know in the issues!

---

**Happy dessert hunting!** 🍰🍦🧁

---

Made with ❤️ by the DessertAble team
