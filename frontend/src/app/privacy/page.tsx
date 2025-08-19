import { Layout } from '@/components/layout';
import LandingHeader from '@/components/layout/LandingHeader';
import LandingFooter from '@/components/layout/LandingFooter';

export default function PrivacyPage() {
  return (
    <Layout showSidebar={false}>
      <LandingHeader />
      
      <div className="min-h-screen bg-white">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-50 via-white to-blue-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                Privacy Policy
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
                Last updated: August 19, 2025
              </p>
            </div>
          </div>
        </div>

        {/* Privacy Policy Content */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="prose prose-lg prose-blue max-w-none">
            
            <h2>1. Introduction</h2>
            <p>
              ClientIQ (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our customer intelligence platform and related services.
            </p>

            <h2>2. Information We Collect</h2>
            
            <h3>2.1 Information You Provide</h3>
            <ul>
              <li><strong>Account Information:</strong> Name, email address, company name, job title</li>
              <li><strong>Contact Information:</strong> Phone number, mailing address</li>
              <li><strong>Demo Requests:</strong> Information submitted through our demo request forms</li>
              <li><strong>Customer Data:</strong> Data you upload or input into our platform</li>
            </ul>

            <h3>2.2 Information We Collect Automatically</h3>
            <ul>
              <li><strong>Usage Data:</strong> How you interact with our platform and services</li>
              <li><strong>Device Information:</strong> IP address, browser type, operating system</li>
              <li><strong>Cookies:</strong> Information stored through cookies and similar technologies</li>
              <li><strong>Log Data:</strong> Server logs, error reports, and performance metrics</li>
            </ul>

            <h2>3. How We Use Your Information</h2>
            <p>We use your information for the following purposes:</p>
            <ul>
              <li>Provide and maintain our services</li>
              <li>Process demo requests and respond to inquiries</li>
              <li>Send important updates about our services</li>
              <li>Improve our platform and develop new features</li>
              <li>Ensure security and prevent fraud</li>
              <li>Comply with legal obligations</li>
              <li>Analyze usage patterns and platform performance</li>
            </ul>

            <h2>4. Data Sharing and Disclosure</h2>
            <p>We may share your information in the following circumstances:</p>
            
            <h3>4.1 Service Providers</h3>
            <p>
              We may share information with trusted third-party service providers who assist us in operating our platform, conducting business, or serving our users.
            </p>

            <h3>4.2 Legal Requirements</h3>
            <p>
              We may disclose information if required by law, regulation, legal process, or governmental request.
            </p>

            <h3>4.3 Business Transfers</h3>
            <p>
              In the event of a merger, acquisition, or sale of assets, your information may be transferred as part of that transaction.
            </p>

            <h3>4.4 Consent</h3>
            <p>
              We may share information with your explicit consent or at your direction.
            </p>

            <h2>5. Data Security</h2>
            <p>
              We implement appropriate technical and organizational measures to protect your information against unauthorized access, alteration, disclosure, or destruction. These measures include:
            </p>
            <ul>
              <li>Encryption of data in transit and at rest</li>
              <li>Regular security assessments and audits</li>
              <li>Access controls and authentication measures</li>
              <li>Employee training on data protection</li>
              <li>Incident response procedures</li>
            </ul>

            <h2>6. Data Retention</h2>
            <p>
              We retain your information for as long as necessary to provide our services, comply with legal obligations, resolve disputes, and enforce our agreements. When we no longer need your information, we will securely delete or anonymize it.
            </p>

            <h2>7. Your Rights and Choices</h2>
            <p>Depending on your location, you may have the following rights:</p>
            <ul>
              <li><strong>Access:</strong> Request a copy of the personal information we hold about you</li>
              <li><strong>Rectification:</strong> Request correction of inaccurate or incomplete information</li>
              <li><strong>Erasure:</strong> Request deletion of your personal information</li>
              <li><strong>Portability:</strong> Request transfer of your data to another service</li>
              <li><strong>Objection:</strong> Object to certain types of processing</li>
              <li><strong>Restriction:</strong> Request limitation of processing in certain circumstances</li>
            </ul>

            <h2>8. Cookies and Tracking Technologies</h2>
            <p>
              We use cookies and similar technologies to enhance your experience, analyze usage, and improve our services. You can control cookie preferences through your browser settings.
            </p>

            <h3>8.1 Types of Cookies We Use</h3>
            <ul>
              <li><strong>Essential Cookies:</strong> Required for basic functionality</li>
              <li><strong>Analytics Cookies:</strong> Help us understand how you use our platform</li>
              <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
              <li><strong>Marketing Cookies:</strong> Used to deliver relevant advertisements</li>
            </ul>

            <h2>9. International Data Transfers</h2>
            <p>
              Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place to protect your information during such transfers.
            </p>

            <h2>10. Children&apos;s Privacy</h2>
            <p>
              Our services are not intended for individuals under the age of 16. We do not knowingly collect personal information from children under 16. If we become aware of such collection, we will take steps to delete the information.
            </p>

            <h2>11. Changes to This Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date.
            </p>

            <h2>12. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our privacy practices, please contact us at:
            </p>
            <div className="bg-gray-50 p-6 rounded-lg mt-6">
              <p><strong>ClientIQ Privacy Team</strong></p>
              <p>Email: privacy@clientiq.com</p>
              <p>Address: 123 Tech Street, San Francisco, CA 94105</p>
              <p>Phone: (555) 123-4567</p>
            </div>

            <h2>13. Specific Regional Provisions</h2>
            
            <h3>13.1 California Residents (CCPA)</h3>
            <p>
              California residents have additional rights under the California Consumer Privacy Act (CCPA), including the right to know what personal information is collected, sold, or disclosed.
            </p>

            <h3>13.2 European Users (GDPR)</h3>
            <p>
              European users have rights under the General Data Protection Regulation (GDPR), including the right to data portability and the right to lodge a complaint with a supervisory authority.
            </p>

            <div className="bg-blue-50 border-l-4 border-blue-400 p-6 mt-8">
              <p className="text-blue-800">
                <strong>Note:</strong> This privacy policy is a template for demonstration purposes. 
                In a real application, you should have this reviewed by legal counsel to ensure 
                compliance with applicable laws and regulations.
              </p>
            </div>

          </div>
        </div>
      </div>
      
      <LandingFooter />
    </Layout>
  );
}
