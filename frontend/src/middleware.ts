import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hostname = request.headers.get('host') || '';
  
  // Skip middleware for API routes, static files, and special paths
  if (pathname.startsWith('/api') || 
      pathname.startsWith('/_next') || 
      pathname.startsWith('/favicon.ico') ||
      pathname.startsWith('/env-test')) {
    return NextResponse.next();
  }
  
  // Get the subdomain by removing the main domain
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
    const parts = hostname.split('.');
    if (parts.length > 2 && parts[0] !== 'www') {
      subdomain = parts[0];
    }
  }

  // If there's a subdomain, handle tenant routing
  if (subdomain) {
    // For now, we'll assume common tenant names are valid
    // In production, you might want to validate against a cached list
    const knownTenants = ['acme', 'testcorp', 'demo']; // Add your tenant names here
    
    if (!knownTenants.includes(subdomain.toLowerCase())) {
      // Unknown tenant - redirect to main landing page
      const isDevelopment = process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true';
      const mainDomain = isDevelopment 
        ? (process.env.NEXT_PUBLIC_MAIN_DOMAIN || 'localhost:3000')
        : (process.env.NEXT_PUBLIC_PRODUCTION_DOMAIN || 'clientiq.com');
      const protocol = isDevelopment ? 'http' : 'https';
      
      // Prevent redirect loops by checking if we're already on the main domain
      if (!hostname.includes(mainDomain)) {
        return NextResponse.redirect(new URL(`${protocol}://${mainDomain}`, request.url));
      }
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
  
  // If no subdomain, this is the main domain
  // Block tenant-only routes on main domain
  if (pathname === '/login' || 
      pathname === '/dashboard' || 
      pathname.match(/^\/(users|contacts|companies|leads|settings)$/)) {
    // Redirect to tenant selection or main page
    return NextResponse.redirect(new URL('/', request.url));
  }
  
  // For main domain, continue normally (landing page, demo form, etc.)
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
