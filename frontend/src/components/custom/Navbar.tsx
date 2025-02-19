"use client";

import React, { useState, useEffect } from "react";
import {
  Home,
  Bell,
  Search,
  Menu,
  X,
} from "lucide-react";
import Link from "next/link";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { title: "Dashboard", icon: <Home size={20} />, navigateTo: "/dashboard" },
  ];

  return (
    <>
      {/* Navbar */}
      <nav
        className={`w-full py-4 transition-all duration-300 bg-[#0a1630] ${
          isScrolled ? "shadow-lg shadow-indigo-900/20" : ""
        }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <div className="flex items-center">
              <span className="text-2xl font-light tracking-tight text-indigo-300">
                Social<span className="font-bold text-indigo-100">Dash</span>
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.title}
                  href={item.navigateTo}
                  className="flex items-center space-x-2 text-indigo-200 hover:text-indigo-50 transition-colors duration-200 group"
                >
                  <span className="group-hover:text-purple-300 transition-colors duration-200">
                    {item.icon}
                  </span>
                  <span className="font-medium text-sm tracking-wide">
                    {item.title}
                  </span>
                </Link>
              ))}
            </div>

            {/* Right Section */}
            <div className="hidden md:flex items-center space-x-6">
              <button className="text-indigo-300 hover:text-indigo-100 transition-colors duration-200">
                <Bell size={20} />
              </button>
              <button className="text-indigo-300 hover:text-indigo-100 transition-colors duration-200">
                <Search size={20} />
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-indigo-700/60 flex items-center justify-center text-indigo-100 font-medium text-sm ring-2 ring-indigo-500/30">
                  JD
                </div>
              </div>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="text-indigo-300 hover:text-indigo-100 transition-colors duration-200"
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-[#122252] shadow-xl shadow-indigo-900/30 rounded-b-lg mx-2 mt-1 border border-indigo-700/20">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.title}
                href={item.navigateTo}
                className="flex items-center space-x-3 px-4 py-3 text-indigo-200 hover:bg-indigo-800/30 hover:text-indigo-50 rounded-md transition-colors duration-200"
              >
                <span>{item.icon}</span>
                <span className="font-medium text-sm">{item.title}</span>
              </Link>
            ))}
            <div className="border-t border-indigo-700/30 my-2"></div>
            <div className="flex justify-between items-center px-4 py-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-indigo-700/60 flex items-center justify-center text-indigo-100 font-medium text-sm ring-2 ring-indigo-500/30">
                  JD
                </div>
                <span className="text-sm font-medium text-indigo-200">
                  John Doe
                </span>
              </div>
              <div className="flex space-x-4">
                <Bell size={20} className="text-indigo-300" />
                <Search size={20} className="text-indigo-300" />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;