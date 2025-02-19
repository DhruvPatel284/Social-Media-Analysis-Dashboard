"use client"
import { ChangeEvent, useState } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"
import { SignupInput } from "@dhruv156328/medium-common"
import { Toaster, toast } from "react-hot-toast"
import { motion } from "framer-motion"
import { LockIcon, MailIcon, UserIcon } from 'lucide-react'
import { GoogleLogin } from '@react-oauth/google'
import Link from "next/link"

export const Auth = ({ type }: { type: "signup" | "signin" }) => {
  const navigate = useRouter()
  const [postInputs, setPostInputs] = useState<SignupInput>({
    name: "",
    username: "",
    password: "",
  })

  async function sendRequest() {
    try {
      toast.loading("Authentication in progress")
      const response = await axios.post(
        `/api/user/${type === "signup" ? "signup" : "signin"}`,
        postInputs
      )
      if (!response) {
        toast.error("Error while logging in!")
      }
      toast.dismiss()
      toast.success("Logged In!")
      const jwt = response.data
      localStorage.setItem("token", jwt)
      navigate.push("/dashboard")
    } catch (e) {
      toast.dismiss()
      toast.error("Error while logging in!")
    }
  }

  async function LoginAsGuest() {
    try {
      toast.loading("Authentication in progress")
      const response = await axios.post( `/api/user/signin`, {
          username: "dhruv@gmail.com",
          password: "123456",
        }
      );
      if (!response) {
        toast.error("Error while logging in!")
      }
      toast.dismiss()
      toast.success("Logged In!")
      const jwt = response.data
      localStorage.setItem("token", jwt)
      navigate.push("/dashboard")
    } catch (e) {
      toast.dismiss()
      toast.error("Error while logging in!")
    }
  }

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      toast.loading("Google Authentication in progress")
      // Send the Google token to your backend for verification and user creation/login
      const response = await axios.post(`/api/user/google-auth`, {
        token: credentialResponse.credential,
      })
      if (!response) {
        toast.error("Error while logging in with Google!")
      }
      toast.dismiss()
      toast.success("Logged In with Google!")
      const jwt = response.data.token;
      localStorage.setItem("token", jwt)
      navigate.push("/dashboard")
    } catch (e) {
      toast.dismiss()
      toast.error("Error while logging in with Google!")
    }
  }

  const handleGoogleError = () => {
    toast.error("Google sign-in was unsuccessful. Please try again.")
  }

  return (
    <div className="min-h-screen flex justify-center items-center bg-gradient-to-br from-purple-700 to-indigo-900">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full bg-white shadow-2xl rounded-2xl p-8 m-4"
      >
        <div className="text-center">
          <h1 className="text-4xl font-extrabold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 mb-2">
            {type === "signin" ? "Welcome Back" : "Join Us Today"}
          </h1>
          <p className="text-sm text-gray-600 mb-8">
            {type === "signin"
              ? "Don't have an account?"
              : "Already have an account?"}
            <Link
              className="ml-1 font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
              href={type === "signin" ? "/signup" : "/signin"}
            >
              {type === "signin" ? "Sign up" : "Sign in"}
            </Link>
          </p>
        </div>
        <div className="space-y-6">
          {type === "signup" && (
            <LabelledInput
              label="Name"
              placeholder="John Doe"
              icon={<UserIcon className="h-5 w-5 text-gray-400" />}
              onChange={(e) =>
                setPostInputs({
                  ...postInputs,
                  name: e.target.value,
                })
              }
            />
          )}
          <LabelledInput
            label="Email"
            placeholder="john@example.com"
            icon={<MailIcon className="h-5 w-5 text-gray-400" />}
            onChange={(e) =>
              setPostInputs({
                ...postInputs,
                username: e.target.value,
              })
            }
          />
          <LabelledInput
            label="Password"
            type="password"
            placeholder="••••••••"
            icon={<LockIcon className="h-5 w-5 text-gray-400" />}
            onChange={(e) =>
              setPostInputs({
                ...postInputs,
                password: e.target.value,
              })
            }
          />
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={sendRequest}
            className="w-full text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 focus:ring-4 focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-3 transition-all duration-300 ease-in-out"
          >
            {type === "signup" ? "Create Account" : "Sign In"}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={LoginAsGuest}
            className="w-full text-indigo-600 bg-white border-2 border-indigo-600 hover:bg-indigo-50 focus:ring-4 focus:ring-indigo-300 font-medium rounded-lg text-sm px-5 py-3 transition-all duration-300 ease-in-out mt-4"
          >
            Login as Guest
          </motion.button>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-800">Or continue with</span>
            </div>
          </div>
          <div className="mt-6 border-2 border-purple-600 rounded-md shadow-lg">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap
            />
          </div>
        </div>
      </motion.div>
    </div>
  )
}

interface LabelledInputType {
  label: string
  placeholder: string
  onChange: (e: ChangeEvent<HTMLInputElement>) => void
  type?: string
  icon?: React.ReactNode
}

function LabelledInput({ label, placeholder, onChange, type, icon }: LabelledInputType) {
  return (
    <div>
      <label className="block mb-2 text-sm font-medium text-gray-700">{label}</label>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {icon}
        </div>
        <input
          onChange={onChange}
          type={type || "text"}
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full pl-10 p-2.5 transition-all duration-300 ease-in-out"
          placeholder={placeholder}
          required
        />
      </div>
    </div>
  )
}