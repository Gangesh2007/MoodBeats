import express from 'express';
import fetch from 'node-fetch';

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

// Route to render the homepage
app.get('/', (req, res) => {
  res.render('index');
});

// Function to generate unique user ID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Chatbot API route
app.post('/chat', async (req, res) => {
  const { query } = req.body;
  const apiKey = 'DGIbuc4ltiM7oFzRUu9q9eRKQv8HbaW6'; // Replace with your actual API key
  const externalUserId = generateUUID();

  console.log('Incoming query:', query);

  try {
    // Create chat session
    const sessionId = await createChatSession(apiKey, externalUserId);
    console.log('Created session ID:', sessionId);

    // Submit user query
    const chatbotResponse = await submitQuery(apiKey, sessionId, query);
    console.log('Full chatbot response:', JSON.stringify(chatbotResponse, null, 2));

    // Check if response structure is as expected
    if (chatbotResponse && chatbotResponse.data) {
      // Adjust this based on actual response structure
      const botMessage = chatbotResponse.data.answer || chatbotResponse.data.message || 'Sorry, I didn’t get that.';
      console.log('Bot message:', botMessage);

      // Fetch playlist based on chatbot's mood detection
      const playlist = await getMoodBasedPlaylist(botMessage);
      res.json({ botMessage, playlist });
    } else {
      console.error('Unexpected response structure:', chatbotResponse);
      res.json({ botMessage: 'Unexpected response from chatbot.', playlist: [] });
    }
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

// Function to create a chat session
async function createChatSession(apiKey, externalUserId) {
  try {
    const response = await fetch('https://api.on-demand.io/chat/v1/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': apiKey,
      },
      body: JSON.stringify({
        pluginIds: [], // Add your plugins here if needed
        externalUserId: externalUserId,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error creating chat session:', errorText);
      throw new Error('Failed to create chat session: ' + response.statusText);
    }

    const data = await response.json();
    return data.data.id; // Extract session ID
  } catch (error) {
    console.error('Error in createChatSession:', error);
    throw error;
  }
}

// Function to submit a query using the session ID
async function submitQuery(apiKey, sessionId, query) {
  try {
    const response = await fetch(`https://api.on-demand.io/chat/v1/sessions/${sessionId}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': apiKey,
      },
      body: JSON.stringify({
        endpointId: 'predefined-openai-gpt4o', // Replace with the actual endpoint ID
        query: query,
        pluginIds: ['plugin-1712327325', 'plugin-1713962163'], // Ensure these are valid
        responseMode: 'sync',
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error submitting query:', errorText);
      throw new Error('Failed to submit query: ' + response.statusText);
    }

    const data = await response.json();
    return data; // Return the full response data for debugging
  } catch (error) {
    console.error('Error in submitQuery:', error);
    throw error;
  }
}

// Start server
app.listen(PORT, () => {
  console.log(`MoodBeats running on http://localhost:${PORT}`);
});
