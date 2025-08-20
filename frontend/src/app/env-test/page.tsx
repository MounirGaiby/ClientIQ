'use client';

export default function EnvTest() {
  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h2>Environment Variables Test</h2>
      <div>
        <p><strong>NEXT_PUBLIC_API_URL:</strong> {process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}</p>
        <p><strong>NEXT_PUBLIC_API_BASE_URL:</strong> {process.env.NEXT_PUBLIC_API_BASE_URL || 'NOT SET'}</p>
        <p><strong>NEXT_PUBLIC_MAIN_DOMAIN:</strong> {process.env.NEXT_PUBLIC_MAIN_DOMAIN || 'NOT SET'}</p>
        <p><strong>NEXT_PUBLIC_IS_DEVELOPMENT:</strong> {process.env.NEXT_PUBLIC_IS_DEVELOPMENT || 'NOT SET'}</p>
        <p><strong>NODE_ENV:</strong> {process.env.NODE_ENV || 'NOT SET'}</p>
      </div>
    </div>
  );
}
