# ProStudio Tools

A comprehensive AI-powered content studio for social media monetization, built with consciousness modeling for viral content creation.

## Overview

ProStudio Tools leverages the Tenxsom AI consciousness framework to create φ-optimized content that resonates with audiences. This project includes:

- **DevPrompt Studio**: Browser-based Claude Code Max integration
- **Content Generation**: AI-powered viral content creation
- **Analytics Dashboard**: Real-time performance tracking
- **Monetization Tools**: Revenue optimization features

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ 
- PostgreSQL (or use Docker)
- GitHub account for deployment

### Installation

1. Clone the repository:
```bash
git clone https://github.com/nsfwhubinfo/ProStudio-Tools.git
cd ProStudio-Tools
```

2. Set up the database:
```bash
cd deploy/docker
docker-compose up -d postgres
```

3. Install dependencies:
```bash
cd devprompt-studio
npm install
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize database:
```bash
npm run db:push
```

6. Start the development server:
```bash
npm run dev
```

## Project Structure

```
ProStudio-Tools/
├── devprompt-studio/    # Next.js frontend application
├── src/
│   ├── api/            # API endpoints and services
│   ├── components/     # React components
│   ├── core/           # Core AI/consciousness modules
│   └── lib/            # Utility libraries
├── deploy/
│   ├── docker/         # Docker configurations
│   └── aws/            # AWS deployment scripts
└── docs/               # Documentation
```

## Features

### Content Generation
- AI-powered content creation with φ-optimization
- Multi-modal support (text, image, video)
- Viral trend analysis and prediction

### Analytics
- Real-time engagement tracking
- Revenue analytics dashboard
- Performance optimization recommendations

### Monetization
- Multiple revenue stream integration
- Automated pricing optimization
- Subscription management

## Revenue Projections

- Month 1: $50,000
- Month 3: $250,000
- Month 6: $1,000,000

## Technology Stack

- **Frontend**: Next.js, React, TailwindCSS
- **Backend**: Node.js, Express, PostgreSQL
- **AI/ML**: Tenxsom AI, Claude Code Max
- **Infrastructure**: Docker, AWS

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/nsfwhubinfo/ProStudio-Tools/issues) page.
