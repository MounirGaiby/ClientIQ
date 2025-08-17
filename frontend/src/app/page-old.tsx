import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            Welcome to{" "}
            <span className="text-blue-600">ClientIQ</span>
          </h1>
          <p className="mt-6 text-xl leading-8 text-gray-600 max-w-3xl mx-auto">
            The intelligent multi-tenant SaaS platform that empowers businesses to manage their operations with unprecedented efficiency and insight.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Button size="lg" className="px-8 py-3">
              Request Demo
            </Button>
            <Button variant="outline" size="lg" className="px-8 py-3">
              Get Started
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Why Choose ClientIQ?
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Powerful features designed for modern businesses
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                </div>
                Multi-Tenant Architecture
              </CardTitle>
              <CardDescription>
                Secure, isolated environments for each client with complete data separation and customization capabilities.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                User Management
              </CardTitle>
              <CardDescription>
                Comprehensive user management with role-based permissions, authentication, and profile customization.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                Real-time Analytics
              </CardTitle>
              <CardDescription>
                Powerful dashboards and analytics to track performance, user engagement, and business metrics in real-time.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join hundreds of companies already using ClientIQ to streamline their operations and drive growth.
          </p>
          <Button size="lg" variant="secondary" className="px-8 py-3">
            Start Your Free Trial
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="text-gray-600">
            <p>&copy; 2025 ClientIQ. All rights reserved.</p>
            <p className="mt-2">Built with Django and Next.js</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
