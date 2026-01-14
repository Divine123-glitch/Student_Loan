import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, BookOpen, GraduationCap, FileText, ArrowRight, ExternalLink } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);

  const features = [
    {
      icon: <GraduationCap className="w-8 h-8" />,
      title: "Eligibility Check",
      description: "Find out instantly if you qualify for NELFUND student loans"
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Application Guide",
      description: "Step-by-step guidance through the entire application process"
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Document Help",
      description: "Learn exactly what documents you need and how to prepare them"
    },
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: "AI-Powered Answers",
      description: "Get accurate answers backed by official NELFUND documents"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <GraduationCap className="w-8 h-8 text-green-600" />
              <span className="text-xl font-bold text-gray-900">NELFUND Navigator</span>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="https://nelf.gov.ng"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-gray-600 hover:text-green-600 transition-colors"
              >
                <span>Official NELFUND</span>
                <ExternalLink className="w-4 h-4" />
              </a>
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 text-green-600 hover:text-green-700 font-medium transition-colors"
              >
                Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all shadow-md hover:shadow-lg"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 bg-green-100 text-green-700 px-4 py-2 rounded-full mb-8 animate-pulse">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm font-medium">AI-Powered Student Loan Assistant</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Your Path to{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-green-600">
              Higher Education
            </span>
            {' '}Starts Here
          </h1>
          
          <p className="text-xl text-gray-600 mb-10 leading-relaxed">
            Navigate NELFUND with confidence. Get instant, accurate answers to all your student loan questions,
            backed by official documents and powered by advanced AI.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/register')}
              className="px-8 py-4 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center space-x-2 group"
            >
              <span className="font-semibold">Start Your Journey</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <a
              href="https://nelf.gov.ng"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-white text-green-600 rounded-xl hover:bg-gray-50 transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-2 border-2 border-green-200"
            >
              <span className="font-semibold">Visit NELFUND</span>
              <ExternalLink className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Everything You Need to Know About NELFUND
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              onMouseEnter={() => setHoveredCard(index)}
              onMouseLeave={() => setHoveredCard(null)}
              className={`bg-white p-6 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 cursor-pointer ${
                hoveredCard === index ? 'transform -translate-y-2' : ''
              }`}
            >
              <div className={`text-green-600 mb-4 transition-transform duration-300 ${
                hoveredCard === index ? 'scale-110' : ''
              }`}>
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-green-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center text-white">
            <div>
              <div className="text-4xl font-bold mb-2">10,000+</div>
              <div className="text-green-200">Questions Answered</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">500+</div>
              <div className="text-green-200">Students Helped</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-green-200">Always Available</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-green-600 to-green-600 rounded-3xl p-12 text-center text-white shadow-2xl">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 text-green-100">
            Join hundreds of students who are navigating NELFUND with confidence
          </p>
          <button
            onClick={() => navigate('/register')}
            className="px-8 py-4 bg-white text-green-600 rounded-xl hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl font-semibold"
          >
            Create Your Free Account
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-green-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <GraduationCap className="w-6 h-6 text-green-400" />
                <span className="text-white font-semibold">NELFUND Navigator</span>
              </div>
              <p className="text-sm">
                Empowering Nigerian students with accurate NELFUND information through AI technology.
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="https://nelf.gov.ng" target="_blank" rel="noopener noreferrer" className="hover:text-green-400 transition-colors">
                    Official NELFUND Website
                  </a>
                </li>
                <li>
                  <button onClick={() => navigate('/login')} className="hover:text-green-400 transition-colors">
                    Login
                  </button>
                </li>
                <li>
                  <button onClick={() => navigate('/register')} className="hover:text-green-400 transition-colors">
                    Register
                  </button>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Disclaimer</h3>
              <p className="text-sm">
                This is an AI-powered assistant. For more information, always visit the NELFUND official website .
              </p>
            </div>
          </div>
          <div className="border-t border-green-800 mt-8 pt-8 text-center text-sm">
            <p>© 2026 NELFUND Navigator. Built for Nigerian Students.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;