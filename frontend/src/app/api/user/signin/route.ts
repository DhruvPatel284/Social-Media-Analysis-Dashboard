import { NextResponse,NextRequest } from 'next/server';
import { sign } from 'jsonwebtoken';
import { signinInput } from '@dhruv156328/medium-common';
import  prisma  from '@/lib/prisma';

export async function POST(req: NextRequest) {
    const body = await req.json();
    const { success } = signinInput.safeParse(body);
    if (!success) {
        return new NextResponse('Inputs not correct',{ status:411 })
    }
    
    try {
      const user = await prisma.user.findFirst({
        where: {
          username: body.username,
          password: body.password,
        },
      });
      
      if (!user) {
        return new NextResponse('Invalid',{ status:403 }) 
      }
      
      const jwt = sign({ id: user.id, name: user.name, username: user.username }, process.env.JWT_SECRET || "");
      return Response.json({ token: jwt },{status:200}); 
    } catch (e) {
      console.error(e);
      return new NextResponse('Internal server error', { status: 500 });
    }
  }