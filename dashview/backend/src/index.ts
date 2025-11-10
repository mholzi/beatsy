import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes placeholder
app.get('/api/rooms', (req: Request, res: Response) => {
  res.json({ message: 'Rooms endpoint - to be implemented' });
});

app.listen(PORT, () => {
  console.log(`DashView backend running on port ${PORT}`);
});
