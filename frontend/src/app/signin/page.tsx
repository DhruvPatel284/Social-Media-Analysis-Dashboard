import { Auth } from "@/components/auth/Auth"
import { GoogleOAuthProvider } from "@react-oauth/google"

export default function Signin(){
  return <div>
        <div className="">
            <div>
            <GoogleOAuthProvider clientId={process.env.GOOGLE_CLIENT_ID || ""}>
                <Auth type="signin"/>
            </GoogleOAuthProvider>
            </div>
        </div>
  </div>
}