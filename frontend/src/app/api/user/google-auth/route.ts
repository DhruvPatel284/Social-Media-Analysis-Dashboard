import { NextResponse,NextRequest } from 'next/server';
import { sign } from 'jsonwebtoken';
import  prisma  from '@/lib/prisma';
import axios from "axios"
export async function POST(req: NextRequest, res: NextResponse) {
    const { token } = await req.json();
    
    if (!token) {
      return new NextResponse('Token is required',{ status:400 });
    }
    
    try {
      const googleResponse = await axios.get(`https://oauth2.googleapis.com/tokeninfo?id_token=${token}`);
      const { email, name } = googleResponse.data;
      
      if (!email) {
        return new NextResponse('Invalid Google token',{ status:400 })
      }
      
      let user = await prisma.user.findUnique({ where: { username: email } });
      
      if (!user) {
        user = await prisma.user.create({
          data: {
            username: email,
            name: name || 'Google User',
            password: 'xyz@kunj3740',
          },
        });
      }
      
      const jwt = sign({ id: user.id, name: user.name, username: user.username }, process.env.JWT_SECRET || "");
      return Response.json({ token: jwt },{status:200}); 
    } catch (error) {
      console.error('Google token validation error:', error);
      return new NextResponse('Internal server error', { status: 500 });
    }
  }