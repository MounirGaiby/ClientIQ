import { Layout } from '@/components/layout';
import LandingHeader from '@/components/layout/LandingHeader';
import LandingFooter from '@/components/layout/LandingFooter';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <Layout showSidebar={false}>
      <LandingHeader />
      
      <div className="min-h-screen bg-white">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-50 via-white to-blue-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                About ClientIQ
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
                We&apos;re revolutionizing customer intelligence with powerful multi-tenant analytics 
                that help businesses understand their customers better than ever before.
              </p>
            </div>
          </div>
        </div>

        {/* Mission Section */}
        <div className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">Our Mission</h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                Empowering businesses through intelligent customer insights
              </p>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                At ClientIQ, we believe that understanding your customers is the key to business success. 
                Our platform provides the tools and insights you need to make data-driven decisions that drive growth.
              </p>
            </div>
          </div>
        </div>

        {/* Values Section */}
        <div className="bg-gray-50 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center mb-12">
              <h2 className="text-3xl font-extrabold text-gray-900">Our Values</h2>
            </div>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <div className="text-center">
                <div className="flex justify-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Innovation</h3>
                <p className="mt-2 text-base text-gray-500">
                  We continuously push the boundaries of what&apos;s possible in customer intelligence and analytics.
                </p>
              </div>
              <div className="text-center">
                <div className="flex justify-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Security</h3>
                <p className="mt-2 text-base text-gray-500">
                  Your data security is our top priority. We implement enterprise-grade security measures.
                </p>
              </div>
              <div className="text-center">
                <div className="flex justify-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Customer Success</h3>
                <p className="mt-2 text-base text-gray-500">
                  Your success is our success. We&apos;re committed to helping you achieve your business goals.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center mb-12">
              <h2 className="text-3xl font-extrabold text-gray-900">Meet Our Team</h2>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                Our diverse team of experts is passionate about helping businesses succeed through better customer insights.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <div className="text-center">
                <div className="mx-auto h-40 w-40 rounded-full bg-gray-300 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-600">JS</span>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">John Smith</h3>
                <p className="text-blue-600">CEO & Founder</p>
                <p className="mt-2 text-base text-gray-500">
                  Former VP of Analytics at Fortune 500 companies with 15+ years of experience in customer intelligence.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto h-40 w-40 rounded-full bg-gray-300 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-600">SK</span>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Sarah Kim</h3>
                <p className="text-blue-600">CTO</p>
                <p className="mt-2 text-base text-gray-500">
                  Expert in scalable architecture and data engineering with a passion for building robust platforms.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto h-40 w-40 rounded-full bg-gray-300 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-600">MD</span>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Mike Davis</h3>
                <p className="text-blue-600">Head of Product</p>
                <p className="mt-2 text-base text-gray-500">
                  Product visionary focused on creating intuitive user experiences that drive business value.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-blue-600">
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              <span className="block">Ready to get started?</span>
              <span className="block text-blue-200">Request a demo today.</span>
            </h2>
            <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
              <div className="inline-flex rounded-md shadow">
                <Link
                  href="/#demo"
                  className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50"
                >
                  Request Demo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <LandingFooter />
    </Layout>
  );
}
