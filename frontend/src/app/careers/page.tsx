import { Layout } from '@/components/layout';
import LandingHeader from '@/components/layout/LandingHeader';
import LandingFooter from '@/components/layout/LandingFooter';

export default function CareersPage() {
  const jobs = [
    {
      id: 1,
      title: 'Senior Frontend Developer',
      department: 'Engineering',
      location: 'San Francisco, CA / Remote',
      type: 'Full-time',
      description: 'Join our engineering team to build cutting-edge user interfaces for our customer intelligence platform.',
      requirements: [
        '5+ years of experience with React/Next.js',
        'Strong TypeScript skills',
        'Experience with modern CSS frameworks',
        'Knowledge of responsive design principles'
      ]
    },
    {
      id: 2,
      title: 'Backend Engineer',
      department: 'Engineering',
      location: 'San Francisco, CA / Remote',
      type: 'Full-time',
      description: 'Help us scale our multi-tenant Django backend to serve millions of users with robust APIs.',
      requirements: [
        '4+ years of Python/Django experience',
        'Experience with PostgreSQL and Redis',
        'Knowledge of RESTful API design',
        'Familiarity with Docker and cloud platforms'
      ]
    },
    {
      id: 3,
      title: 'Product Manager',
      department: 'Product',
      location: 'San Francisco, CA',
      type: 'Full-time',
      description: 'Drive product strategy and roadmap for our customer intelligence platform.',
      requirements: [
        '3+ years of product management experience',
        'Experience with B2B SaaS products',
        'Strong analytical and communication skills',
        'Understanding of customer analytics space'
      ]
    },
    {
      id: 4,
      title: 'Customer Success Manager',
      department: 'Customer Success',
      location: 'Remote',
      type: 'Full-time',
      description: 'Help our customers achieve success with ClientIQ and drive retention and growth.',
      requirements: [
        '2+ years in customer success or account management',
        'Experience with SaaS platforms',
        'Excellent communication skills',
        'Problem-solving mindset'
      ]
    },
    {
      id: 5,
      title: 'Data Scientist',
      department: 'Data Science',
      location: 'San Francisco, CA / Remote',
      type: 'Full-time',
      description: 'Develop machine learning models and advanced analytics to enhance our customer intelligence capabilities.',
      requirements: [
        'PhD or Masters in Data Science, Statistics, or related field',
        'Experience with Python, R, or similar',
        'Knowledge of machine learning algorithms',
        'Experience with large-scale data processing'
      ]
    },
    {
      id: 6,
      title: 'DevOps Engineer',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time',
      description: 'Build and maintain our cloud infrastructure to ensure scalability, reliability, and security.',
      requirements: [
        '3+ years of DevOps/SRE experience',
        'Experience with AWS, Kubernetes, Docker',
        'Knowledge of CI/CD pipelines',
        'Understanding of monitoring and alerting systems'
      ]
    }
  ];

  return (
    <Layout showSidebar={false}>
      <LandingHeader />
      
      <div className="min-h-screen bg-white">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-50 via-white to-blue-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                Join Our Team
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
                Help us build the future of customer intelligence. We&apos;re looking for passionate, 
                talented individuals who want to make a real impact.
              </p>
            </div>
          </div>
        </div>

        {/* Why Work Here Section */}
        <div className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center mb-12">
              <h2 className="text-3xl font-extrabold text-gray-900">Why Work at ClientIQ?</h2>
            </div>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
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
                  Work on cutting-edge technology and solve complex problems.
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
                <h3 className="mt-4 text-lg font-medium text-gray-900">Great Team</h3>
                <p className="mt-2 text-base text-gray-500">
                  Collaborate with talented, passionate teammates who care about their work.
                </p>
              </div>
              <div className="text-center">
                <div className="flex justify-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Global Impact</h3>
                <p className="mt-2 text-base text-gray-500">
                  Help businesses worldwide understand their customers better.
                </p>
              </div>
              <div className="text-center">
                <div className="flex justify-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Competitive Benefits</h3>
                <p className="mt-2 text-base text-gray-500">
                  Excellent compensation, health benefits, and equity packages.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Open Positions */}
        <div className="bg-gray-50 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center mb-12">
              <h2 className="text-3xl font-extrabold text-gray-900">Open Positions</h2>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                We&apos;re always looking for talented individuals to join our growing team.
              </p>
            </div>
            <div className="space-y-6">
              {jobs.map((job) => (
                <div key={job.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="lg:flex lg:items-center lg:justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-medium text-gray-900">{job.title}</h3>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {job.department}
                        </span>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 space-x-4">
                        <span>📍 {job.location}</span>
                        <span>⏰ {job.type}</span>
                      </div>
                      <p className="mt-3 text-gray-600">{job.description}</p>
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Requirements:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {job.requirements.map((req, index) => (
                            <li key={index} className="flex items-start">
                              <span className="mr-2">•</span>
                              <span>{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="mt-4 lg:mt-0 lg:ml-6 lg:flex-shrink-0">
                      <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                        Apply Now
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Benefits Section */}
        <div className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center mb-12">
              <h2 className="text-3xl font-extrabold text-gray-900">Benefits & Perks</h2>
            </div>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">🏥 Health & Wellness</h3>
                <p className="mt-2 text-base text-gray-500">
                  Comprehensive health, dental, and vision insurance for you and your family.
                </p>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">🏖️ Time Off</h3>
                <p className="mt-2 text-base text-gray-500">
                  Generous PTO policy and flexible work arrangements to maintain work-life balance.
                </p>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">💰 Equity</h3>
                <p className="mt-2 text-base text-gray-500">
                  Competitive salary plus equity package so you can share in our success.
                </p>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">📚 Learning</h3>
                <p className="mt-2 text-base text-gray-500">
                  Annual learning budget for conferences, courses, and professional development.
                </p>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">🏠 Remote Friendly</h3>
                <p className="mt-2 text-base text-gray-500">
                  Work from anywhere with a flexible remote-first culture and home office stipend.
                </p>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">🎉 Team Events</h3>
                <p className="mt-2 text-base text-gray-500">
                  Regular team building events, company retreats, and social activities.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-blue-600">
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              <span className="block">Don&apos;t see the right fit?</span>
              <span className="block text-blue-200">We&apos;d still love to hear from you.</span>
            </h2>
            <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
              <div className="inline-flex rounded-md shadow">
                <button className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50">
                  Send us your resume
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <LandingFooter />
    </Layout>
  );
}
