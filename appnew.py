import express from 'express';
import fetch from 'node-fetch';
import SpotifyWebApi from 'spotify-web-api-node';

const app = express();
const PORT = 3000;

// Initialize the Spotify API with your credentials
const spotifyApi = new SpotifyWebApi({
  clientId: 'b0485bcee07141aea74cdc08a38cf568',
  clientSecret: '3a5cfe6c45064f8b9e48d908644a9ce8',
  redirectUri: 'http://localhost:3000/callback' // Ensure this matches with your Spotify Dashboard
});

app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

// Route to render the homepage
app.get('/', (req, res) => {
  res.render('index');
});

// Spotify login route
app.get('/login', (req, res) => {
  const scopes = ['user-read-private', 'user-read-email']; // Define the scopes needed
  const authorizeURL = spotifyApi.createAuthorizeURL(scopes);
  res.redirect(authorizeURL);
});

// Spotify callback route
app.get('/callback', async (req, res) => {
  const code = req.query.code || null; // Get the authorization code from the query parameters

  try {
    const data = await spotifyApi.authorizationCodeGrant(code);
    const { access_token, refresh_token } = data.body;

    // Set the access token and refresh token on the API object
    spotifyApi.setAccessToken(access_token);
    spotifyApi.setRefreshToken(refresh_token);

    res.send('Successfully authenticated! Tokens have been set.');
  } catch (err) {
    console.error('Error during Spotify callback:', err);
    res.send('Something went wrong during the authentication process.');
  }
});

// Function to generate unique user ID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Chatbot API route (Now calling Flask API)
app.post('/chat', async (req, res) => {
  const { query } = req.body;
  const externalUserId = generateUUID();

  console.log('Incoming query:', query);

  try {
    // Call Flask API for chatbot response
    const flaskResponse = await fetch('http://localhost:5000/chat', {  // Change to your Flask API's URL if deployed
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input: query })
    });

    if (!flaskResponse.ok) {
      throw new Error('Error fetching response from Flask API');
    }

    const data = await flaskResponse.json();
    const botMessage = data.reply;

    // Fetch playlist based on chatbot's mood detection
    const playlist = await getMoodBasedPlaylist(botMessage);
    res.json({ botMessage, playlist });
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ botMessage: 'Error with the chatbot', error: error.message });
  }
});

// Function to fetch playlists based on the mood
async function getMoodBasedPlaylist(mood) {
  const playlists = {
    happy: ['Song 1 - Happy', 'Song 2 - Happy'],
    sad: ['Song 1 - Sad', 'Song 2 - Sad'],
    excited: ['Song 1 - Excited', 'Song 2 - Excited'],
    default: ['Song 1 - Default', 'Song 2 - Default'],
  };

  if (mood.includes('happy')) return playlists.happy;
  if (mood.includes('sad')) return playlists.sad;
  if (mood.includes('excited')) return playlists.excited;
  return playlists.default;
}

// Start server
app.listen(PORT, () => {
  console.log(`MoodBeats running on http://localhost:${PORT}`);
});
