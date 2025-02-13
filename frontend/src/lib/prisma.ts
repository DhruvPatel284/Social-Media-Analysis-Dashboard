import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
    datasources: {
      db: {
        url: process.env.DATABASE_URL, // Assuming you have this environment variable set
      },
    },
});

export default prisma;