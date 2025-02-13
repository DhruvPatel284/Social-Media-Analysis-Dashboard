import { NextResponse,NextRequest } from 'next/server';
import { sign } from 'jsonwebtoken';
import { signupInput } from '@dhruv156328/medium-common';
import  prisma  from '@/lib/prisma';

export  async function POST(req: NextRequest) {
    const body = await req.json();
    console.log(body)
    const { success } = signupInput.safeParse(body);
    if (!success) {
      return new NextResponse('Inputs not correct',{ status:411 })
    }
    
    try {
      const user = await prisma.user.create({
        data: {
          username: body.username,
          password: body.password,
          name: body.name,
        },
      });
      
      const jwt = sign({ id: user.id, name: user.name, username: user.username }, process.env.JWT_SECRET || "");  
      return Response.json({ token: jwt },{status:200}); 
    } catch (e) {
      console.error(e);
      return new NextResponse('Internal server error', { status: 500 });
    }
  }
  