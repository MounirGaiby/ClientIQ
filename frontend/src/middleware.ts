import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hostname = request.headers.get('host') || '';
  
  // Get the subdomain by removing the main domain
  // For development, we'll check for localhost patterns
  // For production, this would be your actual domain
  const isLocalhost = hostname.includes('localhost') || hostname.includes('127.0.0.1');
  
  let subdomain = '';
  
  if (isLocalhost) {
    // In development, check for patterns like "tenant.localhost:3000"
    const parts = hostname.split('.');
    if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
      subdomain = parts[0];
    }
  } else {
    // In production, extract subdomain from your actual domain
    // e.g., "tenant.clientiq.com" -> "tenant"
    const parts = hostname.split('.');
    if (parts.length > 2 && parts[0] !== 'www') {
      subdomain = parts[0];
    }
  }

  // If there's a subdomain, this is a tenant domain
  if (subdomain) {
    // For tenant domains, we serve the pages directly
    // The pages at /login and /dashboard are tenant-aware
    if (pathname === '/') {
      // Tenant root -> use tenant-root page to determine redirect
      return NextResponse.rewrite(new URL('/tenant-root', request.url));
    }
    
    // For /login and /dashboard, serve them directly
    // They are already tenant-aware through client-side subdomain detection
    return NextResponse.next();
  }
  
  // If no subdomain, this is the main domain - continue normally
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
