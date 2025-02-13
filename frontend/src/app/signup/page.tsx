// import React from 'react';
import { Auth } from "@/components/auth/Auth";
import { GoogleOAuthProvider } from "@react-oauth/google"


export default function Signup(){
  return <div>
        <div className="">
            <div>
            <GoogleOAuthProvider clientId={process.env.GOOGLE_CLIENT_ID || ""}>
                <Auth type="signup"/>
            </GoogleOAuthProvider>
            </div>
        </div>
  </div>
}