import { NextRequest, NextResponse } from 'next/server';

// Function to validate if subdomain is a valid tenant
async function isValidTenant(subdomain: string): Promise<boolean> {
  try {
    // Check with the backend API to see if this tenant exists
    const response = await fetch(`http://localhost:8000/api/v1/tenants/validate/${subdomain}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    console.error('Error validating tenant:', error);
    return false;
  }
}

export async function middleware(request: NextRequest) {
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

  // If there's a subdomain, validate it's a real tenant
  if (subdomain) {
    const isValid = await isValidTenant(subdomain);
    
    if (!isValid) {
      // Invalid tenant - redirect to main landing page
      const mainDomain = isLocalhost ? 'localhost:3000' : 'clientiq.com';
      return NextResponse.redirect(new URL(`http://${mainDomain}`, request.url));
    }

    
    if (pathname === '/') {
      // Tenant root -> use tenant-root page to determine redirect
      return NextResponse.rewrite(new URL('/tenant-root', request.url));
    }
    
    // Rewrite /login to tenant-specific login page
    if (pathname === '/login') {
      return NextResponse.rewrite(new URL(`/tenant/${subdomain}/login`, request.url));
    }
    
    // Rewrite /dashboard to tenant-specific dashboard page
    if (pathname === '/dashboard') {
      return NextResponse.rewrite(new URL(`/tenant/${subdomain}/dashboard`, request.url));
    }
    
    // Rewrite other tenant paths like /users, /contacts, etc.
    if (pathname.match(/^\/(users|contacts|companies|leads|settings)$/)) {
      return NextResponse.rewrite(new URL(`/tenant/${subdomain}${pathname}`, request.url));
    }
    
    // For other paths, continue normally
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
