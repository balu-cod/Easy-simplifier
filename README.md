# AI Image Processor

A sophisticated web application that combines AI-powered image processing with interactive gaming elements. Upload images, extract text using OCR, analyze content with computer vision, and challenge yourself with brain-training games.

## 🚀 Features

### AI Image Processing
- **Advanced OCR**: Extract text from images with high accuracy
- **Object Detection**: Identify and locate objects in images
- **Scene Understanding**: Analyze image content and context
- **Content Simplification**: AI-powered explanations of complex content
- **Multi-format Support**: JPEG, PNG, PDF, TIFF

### Interactive Gaming
- **Pattern Recognition**: Visual pattern completion puzzles
- **Word Completion**: Language-based challenges from extracted text
- **Spatial Reasoning**: 3D puzzles and spatial challenges
- **Math Puzzles**: Mathematical problems from image content
- **Memory Games**: Match patterns and images from memory
- **Progressive Difficulty**: Easy to expert levels
- **Scoring System**: Points, levels, and achievements
- **Daily Challenges**: New challenges every day
- **Leaderboards**: Compete with other users

### Intelligent Chat
- **Context-Aware AI**: Discuss uploaded images with intelligent responses
- **Multi-turn Conversations**: Maintain conversation history
- **Sentiment Analysis**: Understand emotional context
- **Personalized Interactions**: Tailored responses based on user preferences

### User Experience
- **Modern UI**: Clean, responsive design with dark/light themes
- **Real-time Processing**: Instant image analysis and feedback
- **Progress Tracking**: Monitor your improvement over time
- **Achievement System**: Unlock badges and rewards
- **Social Features**: Share achievements and compete with friends

### Security & Privacy
- **Secure Authentication**: JWT tokens with refresh rotation
- **Social Login**: Google, Facebook, GitHub integration
- **Two-Factor Authentication**: Optional 2FA for enhanced security
- **Data Protection**: Enterprise-grade security measures
- **Privacy Controls**: Manage image visibility and data sharing

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: User data and relational information
- **MongoDB**: Image metadata and game sessions
- **Redis**: Caching and session management
- **OpenAI API**: Advanced AI capabilities
- **Google Vision API**: Enhanced image analysis
- **AWS S3**: Cloud file storage
- **Celery**: Background task processing

### Frontend
- **React 18**: Modern UI library with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **React Query**: Data fetching and caching
- **Zustand**: State management
- **React Hook Form**: Form handling
- **Canvas API**: Game rendering

### AI & ML
- **OpenCV**: Computer vision processing
- **Tesseract**: OCR text extraction
- **TensorFlow**: Machine learning models
- **Transformers**: Natural language processing
- **BLIP**: Image captioning
- **NLTK**: Text analysis and processing

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **PostgreSQL** 13+
- **MongoDB** 5.0+
- **Redis** 6.0+

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-image-processor
```

### 2. Install Dependencies

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && pip install -r requirements.txt && cd ..
```

### 3. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your configuration:

```env
# Database URLs
DATABASE_URL=postgresql://username:password@localhost:5432/ai_image_processor
MONGODB_URL=mongodb://localhost:27017/ai_image_processor

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services (Optional but recommended)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLOUD_VISION_CREDENTIALS=path/to/service-account.json

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name

# Social Authentication (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 4. Database Setup

**PostgreSQL:**
```bash
# Create database
createdb ai_image_processor

# Run migrations (you may need to create them first)
cd backend
alembic upgrade head
```

**MongoDB:**
MongoDB will create collections automatically when first used.

### 5. Start the Application

**Development Mode:**
```bash
# Start both frontend and backend
npm run dev

# Or start individually:
npm run dev:backend  # Backend on http://localhost:8000
npm run dev:frontend # Frontend on http://localhost:3000
```

**Production Mode:**
```bash
# Build frontend
npm run build

# Start backend
npm start
```

## 🎮 Gaming Features

### Available Games

1. **Pattern Recognition** (5-10 minutes)
   - Visual pattern completion
   - Progressive difficulty
   - Spatial awareness training

2. **Word Completion** (3-7 minutes)
   - Complete words from image text
   - Language comprehension
   - Vocabulary building

3. **Spatial Reasoning** (10-15 minutes)
   - 3D puzzle solving
   - Spatial visualization
   - Logic challenges

4. **Math Puzzles** (5-12 minutes)
   - Mathematical problem solving
   - Number pattern recognition
   - Arithmetic challenges

5. **Memory Match** (3-8 minutes)
   - Image and pattern matching
   - Memory enhancement
   - Attention training

### Scoring System
- **Base Points**: Earned for correct answers
- **Time Bonus**: Faster responses earn more points
- **Difficulty Multiplier**: Higher difficulty = more points
- **Streak Bonus**: Consecutive correct answers
- **Daily Challenge Bonus**: Extra points for daily participation

### Achievements
- 🎮 **First Steps**: Complete your first game
- 🏆 **High Scorer**: Score over 800 points
- ⚡ **Speed Demon**: Complete game under 3 minutes
- 💯 **Perfectionist**: 100% accuracy
- 📅 **Daily Champion**: 7-day streak
- 👑 **Master Player**: Reach level 10

## 🧠 AI Capabilities

### Image Analysis
- **Text Extraction**: OCR with 98%+ accuracy
- **Object Detection**: Identify and locate objects
- **Scene Analysis**: Understand image context
- **Content Summarization**: AI-generated summaries
- **Sentiment Analysis**: Emotional content detection

### Language Processing
- **Content Simplification**: Complex text made easy
- **Contextual Responses**: Intelligent chat interactions
- **Multi-language Support**: Process various languages
- **Grammar Correction**: Improve extracted text quality

## 📱 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

#### Images
- `POST /api/images/upload` - Upload and process image
- `GET /api/images/` - List user images
- `GET /api/images/{id}` - Get image details
- `POST /api/images/{id}/analyze` - Custom analysis

#### Games
- `GET /api/games/` - List available games
- `POST /api/games/{type}/start` - Start game session
- `POST /api/games/{type}/answer` - Submit answer
- `GET /api/games/{type}/leaderboard` - View leaderboard

#### Chat
- `POST /api/chat/` - Send message to AI
- `GET /api/chat/history` - Get conversation history
- `DELETE /api/chat/clear` - Clear chat history

## 🔧 Development

### Project Structure

```
ai-image-processor/
├── backend/
│   ├── config/          # Configuration settings
│   ├── database/        # Database connections
│   ├── middleware/      # Authentication middleware
│   ├── models/          # Database models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── contexts/    # React contexts
│   │   ├── hooks/       # Custom React hooks
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── utils/       # Utility functions
│   ├── public/          # Static assets
│   └── package.json     # Frontend dependencies
├── package.json         # Root package file
└── README.md           # This file
```

### Development Commands

```bash
# Install all dependencies
npm run install:all

# Development with hot reload
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### Adding New Features

1. **Backend**: Add routes in `backend/routers/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Database**: Create migrations for schema changes
4. **Tests**: Add tests for new functionality

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Manual Deployment

1. **Build Frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure Environment:**
   - Set production environment variables
   - Configure database connections
   - Set up SSL certificates

3. **Deploy Backend:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Serve Frontend:**
   - Use nginx or similar web server
   - Serve built files from `frontend/dist/`

### Environment Variables for Production

```env
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/ai_image_processor
MONGODB_URL=mongodb://prod-mongo:27017/ai_image_processor
REDIS_URL=redis://prod-redis:6379
CORS_ORIGINS=["https://yourdomain.com"]
SECRET_KEY=your-production-secret-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript/Python best practices
- Add tests for new features
- Update documentation
- Follow existing code style
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce

## 🙏 Acknowledgments

- OpenAI for GPT models
- Google for Vision API
- Tesseract OCR community
- React and FastAPI communities
- All contributors and users

## 🔮 Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Advanced game types
- [ ] Team competitions
- [ ] Video processing
- [ ] API rate limiting
- [ ] Advanced analytics
- [ ] Custom AI model training
- [ ] Marketplace for user-generated games

### Performance Improvements
- [ ] Image processing optimization
- [ ] Database query optimization
- [ ] CDN integration
- [ ] Caching improvements
- [ ] Background processing
- [ ] Load balancing

---

**Built with ❤️ by the AI Image Processor Team**
