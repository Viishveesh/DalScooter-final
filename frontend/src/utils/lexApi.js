// Lex API integration for DALScooter frontend

const LEX_API_URL = process.env.REACT_APP_LEX_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod/lex';

class LexAPI {
    constructor() {
        this.sessionId = null;
        this.userId = null;
    }

    // Initialize the Lex session
    initializeSession(userId) {
        this.userId = userId;
        this.sessionId = `session_${userId}_${Date.now()}`;
    }

    // Send message to Lex bot
    async sendMessage(message) {
        try {
            const response = await fetch(LEX_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    message: message,
                    userId: this.userId,
                    sessionId: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                message: data.message,
                intent: data.intent,
                slots: data.slots
            };
        } catch (error) {
            console.error('Error sending message to Lex:', error);
            return {
                success: false,
                message: 'Sorry, I\'m having trouble connecting right now. Please try again.',
                error: error.message
            };
        }
    }

    // Get bot capabilities
    async getBotCapabilities() {
        try {
            const response = await fetch(`${LEX_API_URL}/capabilities`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                capabilities: data.capabilities
            };
        } catch (error) {
            console.error('Error getting bot capabilities:', error);
            return {
                success: false,
                capabilities: []
            };
        }
    }

    // Book a scooter through Lex
    async bookScooter(location, duration) {
        const message = `I want to book a scooter at ${location} for ${duration}`;
        return await this.sendMessage(message);
    }

    // Check bookings through Lex
    async checkBookings() {
        const message = 'Check my booking status';
        return await this.sendMessage(message);
    }

    // Cancel booking through Lex
    async cancelBooking(bookingId) {
        const message = `Cancel my booking ${bookingId}`;
        return await this.sendMessage(message);
    }

    // Get help through Lex
    async getHelp() {
        const message = 'I need help';
        return await this.sendMessage(message);
    }

    // Process natural language input
    async processNaturalLanguage(input) {
        return await this.sendMessage(input);
    }
}

// Create a singleton instance
const lexAPI = new LexAPI();

export default lexAPI; 