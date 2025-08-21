import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Users, BarChart3, Shield, Zap, ChevronRight, TrendingUp, Star } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-400 via-orange-500 to-pink-500">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Navigation */}
        <nav className="relative z-10 flex items-center justify-between p-6 lg:px-8">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white">ClientIQ</h1>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-white/90 hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-white/90 hover:text-white transition-colors">Pricing</a>
            <a href="#contact" className="text-white/90 hover:text-white transition-colors">Contact</a>
            <a href="/demo" className="btn-secondary">Try Demo</a>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 pt-20 pb-32">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Beautiful CRM
              <span className="block bg-gradient-to-r from-yellow-200 to-pink-200 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
              Transform your customer relationships with our intuitive, multi-tenant CRM platform. 
              Built for modern teams who value simplicity and results.
            </p>
            <div className="flex flex-col md:flex-row gap-4 justify-center">
              <a href="/demo" className="btn-primary text-lg px-8 py-4 flex gap-2">
                Start Free Trial
                <ChevronRight className="ml-2 h-5 w-5" />
              </a>
              <a href="#features" className="btn-secondary text-lg px-8 py-4">
                See Features
              </a>
            </div>
          </div>
        </div>

        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-white/10 blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-white/10 blur-3xl"></div>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white/5 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Why Choose ClientIQ?</h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">
              Everything you need to manage customer relationships effectively
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Users className="h-8 w-8" />,
                title: "Multi-Tenant Architecture",
                description: "Perfect isolation for multiple organizations with custom domains"
              },
              {
                icon: <Zap className="h-8 w-8" />,
                title: "Lightning Fast",
                description: "Built with modern React and optimized for speed and performance"
              },
              {
                icon: <Shield className="h-8 w-8" />,
                title: "Secure & Compliant",
                description: "Enterprise-grade security with role-based permissions"
              },
              {
                icon: <TrendingUp className="h-8 w-8" />,
                title: "Analytics & Insights",
                description: "Powerful reporting tools to track your business growth"
              },
              {
                icon: <Star className="h-8 w-8" />,
                title: "Beautiful Design",
                description: "Intuitive interface that your team will love to use"
              },
              {
                icon: <Zap className="h-8 w-8" />,
                title: "Easy Integration",
                description: "Connect with your favorite tools and workflows"
              }
            ].map((feature, index) => (
              <div key={index} className="card p-6 text-center group hover:scale-105 transition-transform">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-pink-500 text-white mb-4 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of companies already using ClientIQ to grow their business
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <a href="/demo" className="btn-primary text-lg px-8 py-4">
              Start Your Free Trial
            </a>
            <button className="btn-secondary text-lg px-8 py-4">
              Schedule a Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm py-12">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">ClientIQ</h3>
            <p className="text-white/80 mb-6">Beautiful CRM for modern teams</p>
            <div className="flex justify-center space-x-6">
              <a href="#" className="text-white/60 hover:text-white transition-colors">Privacy</a>
              <a href="#" className="text-white/60 hover:text-white transition-colors">Terms</a>
              <a href="#" className="text-white/60 hover:text-white transition-colors">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
